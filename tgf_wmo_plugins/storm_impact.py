"""Shared core for per-storm impact on buildings and roads.

This answers a different question from `impact_summary`. That one reports
exposure against exceedance probabilities ("what are the odds of 30 cm here");
this reports depth in one specific storm ("in storm 150, how deep at each
building"). Depth is a physical quantity, so a band needs no explanation the way
a probability gate does.
"""

from functools import lru_cache

import numpy as np
import pandas as pd
import rasterio
import shapely

from tgf_wmo_plugins.common import open_zarr_store
from tgf_wmo_plugins.countries import COUNTRIES
from tgf_wmo_plugins.receptors import load_receptors

# Ascending, so assigning in order lets the deepest band a feature reaches win.
# The 0.05 m floor is the stores' own `extent_threshold_m`; the rest are round
# depths that read without a legend -- ankle, knee/vehicle, storey.
DEPTH_BANDS = [
    (1, "green", 0.05),
    (2, "yellow", 0.30),
    (3, "red", 1.00),
    (4, "purple", 2.00),
]

STATS_FILE = "ensemble_stats.csv"


def _store(key, unit):
    return open_zarr_store(COUNTRIES[key].storms.store_url(unit))


def _depth(group, index):
    """One storm's depth grid; non-finite or negative cells are dry."""
    depth = np.asarray(group["depth"][index], dtype="float32")
    return np.where(np.isfinite(depth) & (depth > 0), depth, 0.0)


@lru_cache(maxsize=8)
def store_grid(key, unit):
    """The store's affine transform, shape and CRS."""
    attrs = dict(_store(key, unit).attrs)
    rows, cols = attrs["grid_shape"]
    return rasterio.Affine(*attrs["transform"]), (rows, cols), attrs["crs"]


@lru_cache(maxsize=8)
def receptor_cells(key, unit):
    """Every (feature, cell) pair the receptors touch, as two index arrays.

    Storm-independent, so it is paid once and reused for every storm. A pair
    list rather than a rasterised id grid because a cell can hold many features:
    at 30 m most buildings are smaller than a cell, and burning ids would keep
    one per cell and drop the rest.
    """
    transform, (rows, cols), crs = store_grid(key, unit)
    geoms = load_receptors(key, unit, geometry=True).geometry.to_crs(crs)

    a, _, x0, _, e, y0 = transform[:6]
    minx, miny, maxx, maxy = geoms.bounds.to_numpy().T
    # The cell height `e` is negative, so the top row comes from the maximum y.
    c0 = np.clip(np.floor((minx - x0) / a).astype(int), 0, cols - 1)
    c1 = np.clip(np.floor((maxx - x0) / a).astype(int), 0, cols - 1)
    r0 = np.clip(np.floor((maxy - y0) / e).astype(int), 0, rows - 1)
    r1 = np.clip(np.floor((miny - y0) / e).astype(int), 0, rows - 1)

    # Every cell in each feature's bounding box, then only those it intersects.
    n_cells = (r1 - r0 + 1) * (c1 - c0 + 1)
    feature_idx = np.repeat(np.arange(len(geoms)), n_cells)
    within = np.arange(n_cells.sum()) - np.repeat(np.cumsum(n_cells) - n_cells, n_cells)
    width = np.repeat(c1 - c0 + 1, n_cells)
    row = np.repeat(r0, n_cells) + within // width
    col = np.repeat(c0, n_cells) + within % width

    boxes = shapely.box(
        x0 + col * a, y0 + (row + 1) * e, x0 + (col + 1) * a, y0 + row * e
    )
    touches = shapely.intersects(geoms.to_numpy()[feature_idx], boxes)
    return feature_idx[touches], (row * cols + col)[touches]


def classify_depth(depths):
    """Band value per feature: 0 for dry, then 1..4 by increasing depth."""
    band = np.zeros(len(depths), dtype="uint8")
    for value, _color, floor in DEPTH_BANDS:
        band[depths >= floor] = value
    return band


def banded_features(key, unit, index):
    """Receptors with `band` and `depth_m` attached, dry ones dropped.

    Returns a new frame, so callers may modify it.
    """
    gdf = load_receptors(key, unit, geometry=True)
    depth = _depth(_store(key, unit), index).ravel()
    feature_idx, cell_idx = receptor_cells(key, unit)
    depths = np.zeros(len(gdf), dtype="float32")
    np.maximum.at(depths, feature_idx, depth[cell_idx])

    gdf = gdf.copy()
    # Classify on the raw depth and round only for display, or a feature just
    # under 0.05 m is promoted into the wet band by the rounding. float64 first,
    # so 0.07 does not serialise as 0.07000000029802322.
    gdf["band"] = classify_depth(depths)
    gdf["depth_m"] = depths.astype("float64").round(2)
    return gdf[gdf["band"] > 0]


@lru_cache(maxsize=2)
def _precomputed_stats(store_url):
    url = f"{store_url.rstrip('/')}/{STATS_FILE}"
    try:
        return pd.read_csv(url).set_index("storm_index", drop=False)
    except Exception as exc:  # noqa: BLE001 - surfaced to the dashboard as-is
        raise ValueError(f"could not read {url}: {exc}") from exc


def _cell_area_m2(attrs):
    """Area of one cell, for a projected grid or a geographic one (Barbados is
    EPSG:4326, where the east-west side shrinks with latitude)."""
    pixel = abs(attrs["transform"][0])
    if pixel > 0.01:  # metres, not degrees
        return pixel**2
    lat = attrs["transform"][5] - 0.5 * attrs["grid_shape"][0] * pixel
    metres = pixel * 111_320.0
    return metres * metres * np.cos(np.radians(lat))


def storm_stats(key, unit, index):
    """Magnitude, flooded area and depth for one storm, or None out of range."""
    storms = COUNTRIES[key].storms
    if storms.precomputed_stats:
        stats = _precomputed_stats(storms.store_url(unit))
        if index not in stats.index:
            return None
        row = stats.loc[index]
        return {
            "n_storms": len(stats),
            "magnitude_mm": float(row.magnitude_mm),
            "flooded_cells": int(row.flooded_px),
            "area_km2": float(row.area_km2),
            "pct_domain": float(row.pct_domain),
            "max_depth_m": float(row.max_depth_m),
            "mean_wet_depth_m": float(row.mean_wet_depth_m),
        }

    group = _store(key, unit)
    n_storms = group["depth"].shape[0]
    if not 0 <= index < n_storms:
        return None
    attrs = dict(group.attrs)
    depth = _depth(group, index)
    wet = depth >= attrs["extent_threshold_m"]
    return {
        "n_storms": n_storms,
        "magnitude_mm": float(np.asarray(group["magnitude_mm"][index])),
        "flooded_cells": int(wet.sum()),
        "area_km2": float(wet.sum() * _cell_area_m2(attrs) / 1e6),
        "pct_domain": float(100 * wet.sum() / depth.size),
        "max_depth_m": float(depth.max()),
        "mean_wet_depth_m": float(depth[wet].mean()) if wet.any() else 0.0,
    }


class StormIndex:
    """The unit and storm arguments shared by the storm plugin family."""

    @classmethod
    def country_args(cls, country):
        return {**cls.unit_args(country), "index": country.storms.options}

    def storm_index(self):
        """Slider values arrive as strings; anything unusable is the default."""
        default = self.country.storms.default_index
        try:
            return int(float(self.get_arg("index", default)))
        except (TypeError, ValueError):
            return default
