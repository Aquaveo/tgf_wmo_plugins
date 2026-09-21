"""Shared core for per-storm impact on buildings and roads.

The RainyDay ensemble and the IBF buildings/roads turn out to sit on exactly the
same grid -- EPSG:3857, 424x319, 5 m cells, identical origin -- so a storm's depth
raster can be sampled onto the features with no reprojection or resampling at all.

This answers a different question from `impact_summary`. That one reports exposure
against exceedance probabilities ("what are the odds of 30 cm here"); this reports
depth in one specific storm ("in storm 150, how deep at each building"). Depth is a
physical quantity, so a band needs no explanation the way a probability gate does.
"""

from functools import lru_cache

import geopandas as gpd
import numpy as np
import pandas as pd
import pyogrio
import rasterio
import shapely
from rasterio.features import rasterize
from shapely import set_precision

from tgf_wmo_plugins.common import (
    BARBADOS_FEATURES_URL,
    BARBADOS_PARISH_POPULATION,
    COMOROS_UNIT_POPULATION,
    DEFAULT_STORE,
    FEATURES_URL,
    GPKG_LAYERS,
    barbados_store_url,
    cached_download,
    comoros_receptors_url,
    comoros_store_url,
    open_zarr_store,
)

# Ascending, so assigning in order lets the deepest band a feature reaches win --
# the same escalation clasificar_peligro uses for probabilities.
#
# The 0.05 m floor is the store's own `extent_threshold_m`: below it the model
# does not consider a cell wet. The rest are round depths chosen to be read
# without a legend -- ankle, knee/vehicle, storey.
DEPTH_BANDS = [
    (1, "green", 0.05),
    (2, "yellow", 0.30),
    (3, "red", 1.00),
    (4, "purple", 2.00),
]

# Coordinate snapping for the returned geometry, in the store's 5 m grid units.
PRECISION_M = 0.5


@lru_cache(maxsize=2)
def store_grid(store_url=DEFAULT_STORE):
    """The store's affine transform, shape and CRS."""
    group = open_zarr_store(store_url)
    attrs = dict(group.attrs)
    transform = rasterio.Affine(*attrs["transform"])
    rows, cols = attrs["grid_shape"]
    return transform, (rows, cols), attrs["crs"]


@lru_cache(maxsize=2)
def load_features(url=FEATURES_URL, store_url=DEFAULT_STORE):
    """Buildings and roads in the store's CRS, ready to rasterise against it."""
    _transform, _shape, crs = store_grid(store_url)
    gdf = gpd.read_file(url).to_crs(crs)
    # to_crs hands back full float precision, undoing the snapping the
    # precomputed source was written with and tripling the GeoJSON payload.
    # 0.5 m is a tenth of a cell, so it cannot move a feature into another band.
    gdf["geometry"] = set_precision(gdf.geometry.values, PRECISION_M)
    return gdf[~gdf.geometry.is_empty]


@lru_cache(maxsize=2)
def feature_id_grid(url=FEATURES_URL, store_url=DEFAULT_STORE):
    """A grid of 1-based feature ids, and the count of features that reach it.

    This is the expensive step and it does not depend on the storm, so it is paid
    once and reused for every index. all_touched matches how the IBF
    probabilities were sampled onto these same features.

    Features outside the 3.38 km2 model domain get no cells. They are counted
    here so percentages can be reported against what the model actually covers
    rather than against the whole geopackage.
    """
    transform, shape, _crs = store_grid(store_url)
    gdf = load_features(url, store_url)
    ids = rasterize(
        ((geom, i + 1) for i, geom in enumerate(gdf.geometry)),
        out_shape=shape,
        transform=transform,
        fill=0,
        all_touched=True,
        dtype="int32",
    )
    in_domain = np.unique(ids)
    return ids, int((in_domain > 0).sum())


def feature_max_depth(index, url=FEATURES_URL, store_url=DEFAULT_STORE):
    """Deepest water over each feature's own footprint, in metres.

    Reads one storm's chunk (~540 KB) rather than the whole 108 MB array.
    Features outside the domain, and dry ones, come back as 0.
    """
    group = open_zarr_store(store_url)
    depth = np.asarray(group["depth"][index], dtype="float32")
    # The store's nodata is a large negative float; anything non-finite or below
    # zero is "no water", not a depth.
    depth = np.where(np.isfinite(depth) & (depth > 0), depth, 0.0)

    ids, _in_domain = feature_id_grid(url, store_url)
    gdf = load_features(url, store_url)
    per_feature = np.zeros(len(gdf) + 1, dtype="float32")
    np.maximum.at(per_feature, ids.ravel(), depth.ravel())
    # Drop index 0, which accumulates every cell not covered by a feature.
    return per_feature[1:]


def classify_depth(depths):
    """Band value per feature: 0 for dry, then 1..4 by increasing depth."""
    banda = np.zeros(len(depths), dtype="uint8")
    for value, _color, floor in DEPTH_BANDS:
        banda[depths >= floor] = value
    return banda


def banded_features(index, url=FEATURES_URL, store_url=DEFAULT_STORE):
    """Features with a depth band attached, dry ones dropped.

    Returns a copy, so callers may modify it without disturbing the cache.
    """
    gdf = load_features(url, store_url).copy()
    depths = feature_max_depth(index, url, store_url)
    # Classify on the raw depth, round only for display. Rounding first promoted
    # 14 features sitting just under 0.05 m into the wet band -- a display
    # concern silently changing the answer.
    gdf["banda"] = classify_depth(depths)
    gdf["profundidad_m"] = depths.round(2)
    return gdf[gdf.banda > 0]


# ---------------------------------------------------------------------------
# Comoros
#
# Everything above assumes what Guatemala happens to provide: one national store,
# features on the store's own grid, and 5 m cells small enough that burning
# feature ids into a raster keeps every feature. None of that holds here.
#
#   * Products are per ADM3 commune, so a unit has to be named before any URL
#     resolves, and the receptor geopackage is per island rather than per commune.
#   * Cells are 30.57 m and most buildings in Moroni are smaller than one, so
#     many share a cell. `rasterize` writes one id per cell and silently drops
#     the rest -- about 61% of features vanish. The sampling therefore has to
#     allow MANY FEATURES PER CELL, which is what the (feature, cell) pair list
#     below does.
#   * The grid is EPSG:5629, which the frontend cannot resolve, so the layer
#     reprojects on the way out.
# ---------------------------------------------------------------------------

# Buildings and roads carry these under the same names Antigua and Barbuda uses,
# in every country whose receptors come from a geopackage.
UNIT_MEASURES = ["population_per_building", "building_area_m2", "road_length_m"]

# What differs between a Comorian commune and a Barbadian parish is only where
# the files are and what the admin column is called, so the sampling below is
# written once and keyed by country.
UNIT_SOURCES = {
    "comoros": {
        "store": comoros_store_url,
        # one geopackage per island, so the commune is selected out of it
        "receptors": comoros_receptors_url,
        "pcode_field": "ADM3_PCODE",
        "population": lambda unit: COMOROS_UNIT_POPULATION[unit],
    },
    "barbados": {
        "store": barbados_store_url,
        # one geopackage for the whole island, so the parish is selected out of it
        "receptors": lambda _unit: BARBADOS_FEATURES_URL,
        "pcode_field": "ADM1_PCODE",
        "population": lambda unit: BARBADOS_PARISH_POPULATION[unit],
    },
}

# The `type` column and GeoDataFrame.type collide: the attribute is GeoPandas'
# geometry-type property ("Point"/"LineString"/"Polygon"), not this column.
# Always subscript -- `gdf["type"] == "building"` -- or the comparison matches
# nothing and every building count silently reads 0.
UNIT_BUILDING = "building"

# A mid-library scenario, wet enough to put water in several depth bands without
# being the extreme at the top of the library.
UNIT_DEFAULT_STORM = 150


@lru_cache(maxsize=8)
def unit_features(country, unit):
    """One unit's buildings and roads, in the receptor file's own CRS.

    Read with the unit selected in the driver, so the rest of the island's
    geometries are never built.
    """
    cfg = UNIT_SOURCES[country]
    path = cached_download(cfg["receptors"](unit))
    pcode = unit.split("_")[0]
    parts = []
    for type_, (layer, _renames) in GPKG_LAYERS[country].items():
        available = set(pyogrio.read_info(path, layer=layer)["fields"])
        columns = [c for c in UNIT_MEASURES if c in available]
        part = pyogrio.read_dataframe(
            path,
            layer=layer,
            columns=columns,
            where=f"{cfg['pcode_field']} = '{pcode}'",
            use_arrow=True,
        )
        part["type"] = type_
        parts.append(part)
    gdf = gpd.GeoDataFrame(pd.concat(parts, ignore_index=True), crs=parts[0].crs)
    for col in UNIT_MEASURES:
        gdf[col] = gdf[col].fillna(0.0) if col in gdf else 0.0
    return gdf[~gdf.geometry.is_empty].reset_index(drop=True)


@lru_cache(maxsize=8)
def unit_store_grid(country, unit):
    """The unit store's affine transform, shape and CRS."""
    attrs = dict(open_zarr_store(UNIT_SOURCES[country]["store"](unit)).attrs)
    rows, cols = attrs["grid_shape"]
    return rasterio.Affine(*attrs["transform"]), (rows, cols), attrs["crs"]


@lru_cache(maxsize=8)
def unit_pairs(country, unit):
    """Every (feature, cell) pair the unit's features touch.

    The storm-independent half of the sampling, so it is paid once per unit and
    reused for all 200 scenarios. Built from bounding boxes and then filtered by
    a real intersection test, which is one vectorised call rather than one per
    feature.

    This is what `rasterize` cannot do. At 30 m a cell is bigger than most
    buildings and many share one, so burning feature ids keeps the last and
    silently drops the rest -- about 61% of them in Moroni. A pair list allows
    many features per cell, and a building spanning several is sampled in each.
    """
    transform, (rows, cols), _crs = unit_store_grid(country, unit)
    gdf = unit_features(country, unit).to_crs(_crs)

    a, _, x0, _, e, y0 = transform[:6]
    minx, miny, maxx, maxy = gdf.geometry.bounds.to_numpy().T
    # Row 0 is the top edge and the cell height `e` is negative, so the first row
    # comes from the maximum y.
    c0 = np.clip(np.floor((minx - x0) / a).astype(int), 0, cols - 1)
    c1 = np.clip(np.floor((maxx - x0) / a).astype(int), 0, cols - 1)
    r0 = np.clip(np.floor((maxy - y0) / e).astype(int), 0, rows - 1)
    r1 = np.clip(np.floor((miny - y0) / e).astype(int), 0, rows - 1)

    n_cells = (r1 - r0 + 1) * (c1 - c0 + 1)
    feature_idx = np.repeat(np.arange(len(gdf)), n_cells)
    within = np.arange(n_cells.sum()) - np.repeat(np.cumsum(n_cells) - n_cells, n_cells)
    width = np.repeat(c1 - c0 + 1, n_cells)
    row = np.repeat(r0, n_cells) + within // width
    col = np.repeat(c0, n_cells) + within % width

    boxes = shapely.box(
        x0 + col * a, y0 + (row + 1) * e, x0 + (col + 1) * a, y0 + row * e
    )
    touches = shapely.intersects(gdf.geometry.to_numpy()[feature_idx], boxes)
    return feature_idx[touches], (row * cols + col)[touches]


def unit_feature_max_depth(country, unit, index):
    """Deepest water over each feature's own footprint, in metres."""
    group = open_zarr_store(UNIT_SOURCES[country]["store"](unit))
    depth = np.asarray(group["depth"][index], dtype="float32").ravel()
    depth = np.where(np.isfinite(depth) & (depth > 0), depth, 0.0)

    feature_idx, cell_idx = unit_pairs(country, unit)
    per_feature = np.zeros(len(unit_features(country, unit)), dtype="float32")
    np.maximum.at(per_feature, feature_idx, depth[cell_idx])
    return per_feature


def unit_banded_features(country, unit, index):
    """One unit's features with a depth band attached, dry ones dropped."""
    gdf = unit_features(country, unit).copy()
    depths = unit_feature_max_depth(country, unit, index)
    # Classify on the raw depth and round only for display, or a feature at
    # 0.0455 m is promoted into the wet band by the rounding alone.
    gdf["banda"] = classify_depth(depths)
    # float64 before rounding: rounding a float32 leaves the nearest representable
    # value, so 0.07 serialises into the popup as 0.07000000029802322.
    gdf["profundidad_m"] = depths.astype("float64").round(2)
    return gdf[gdf.banda > 0]


def unit_population(country, unit):
    """The unit's own population, for the exposure share."""
    return UNIT_SOURCES[country]["population"](unit)


def unit_cell_area_m2(attrs):
    """Area of one cell in square metres, for either grid kind.

    A projected store gives it directly from the pixel size. A geographic one --
    Barbados is EPSG:4326 at one arc-second -- has to be converted, and the
    east-west side shrinks with latitude.
    """
    pixel = abs(attrs["transform"][0])
    if pixel > 0.01:                      # metres, not degrees
        return pixel ** 2
    lat = attrs["transform"][5] - 0.5 * attrs["grid_shape"][0] * pixel
    metres_ns = pixel * 111_320.0
    return metres_ns * metres_ns * np.cos(np.radians(lat))


def unit_storm_stats(country, unit, index):
    """Magnitude, flooded area and depth for one storm, straight from the store.

    Guatemala reads these from an `ensemble_stats.csv` precomputed beside its
    store. The Comoros and Barbados stores ship no such file, but the numbers are
    one chunk read away, so they are computed here instead of requiring a
    precompute step per unit. Returns None when the index is out of range.
    """
    group = open_zarr_store(UNIT_SOURCES[country]["store"](unit))
    depth_array = group["depth"]
    n_storms = depth_array.shape[0]
    if not 0 <= index < n_storms:
        return None

    attrs = dict(group.attrs)
    wet_floor = attrs["extent_threshold_m"]
    cell_m2 = unit_cell_area_m2(attrs)

    depth = np.asarray(depth_array[index], dtype="float32")
    depth = np.where(np.isfinite(depth) & (depth > 0), depth, 0.0)
    wet = depth >= wet_floor

    return {
        "n_storms": n_storms,
        "magnitude_mm": float(np.asarray(group["magnitude_mm"][index])),
        "flooded_cells": int(wet.sum()),
        "area_km2": float(wet.sum() * cell_m2 / 1e6),
        "pct_domain": float(100 * wet.sum() / depth.size),
        "max_depth_m": float(depth.max()),
        "mean_wet_depth_m": float(depth[wet].mean()) if wet.any() else 0.0,
    }
