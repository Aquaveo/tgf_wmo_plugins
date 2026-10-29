"""Reading a country's buildings and roads, and summarising exposure over them."""

from functools import lru_cache

import geopandas as gpd
import pandas as pd
import pyogrio
from shapely import set_precision

from tgf_wmo_plugins.common import cached_download
from tgf_wmo_plugins.countries import COUNTRIES
from tgf_wmo_plugins.tito import TRAINING, cycle_files, file_url, live_download

# The frontend does not bundle proj4, so OpenLayers resolves only EPSG:4326 and
# EPSG:3857; vector output always goes out in 4326.
OUTPUT_CRS = "EPSG:4326"
# ~0.1 m. Trims digits off metre-scale footprints without visibly moving them.
PRECISION_DEG = 1e-6


def _read_layers(path, rec, where, geometry):
    """A geopackage's buildings and roads, stacked with a `type` column."""
    cols = rec.columns
    parts = []
    for type_, (layer, renames) in rec.layers.items():
        source_name = {new: old for old, new in renames.items()}
        wanted = [source_name.get(f, f) for f in (*rec.probabilities, *cols.measures)]
        available = set(pyogrio.read_info(path, layer=layer)["fields"])
        part = pyogrio.read_dataframe(
            path,
            layer=layer,
            columns=[f for f in wanted if f in available],
            where=where,
            read_geometry=geometry,
            use_arrow=True,
        ).rename(columns=renames)
        part[cols.type] = type_
        parts.append(part)
    df = pd.concat(parts, ignore_index=True)
    return gpd.GeoDataFrame(df, crs=parts[0].crs) if geometry else df


@lru_cache(maxsize=16)
def load_receptors(key, scope=None, geometry=False, cycle=TRAINING):
    """One country's buildings and roads, in the source CRS, or None when the
    cycle published none for `scope`.

    Every row carries the `type` column, the measures (zero where a layer lacks
    one -- a road has no population) and four probabilities on the 0-1 scale.
    Cached; callers must not modify the frame they get back.
    """
    country = COUNTRIES[key]
    if cycle == TRAINING:
        rec = country.receptors
        if rec.layers is None:
            df = gpd.read_file(rec.url(scope)) if geometry else pd.read_csv(rec.table_url)
        else:
            # A whole download beats GDAL range-reading the geopackage per layer.
            path = cached_download(rec.url(scope))
            df = _read_layers(path, rec, country.gpkg_where(scope), geometry)
    else:
        # A live file already covers just its site.
        live = country.live
        rec = live.receptors
        path = live.receptor_path(scope, cycle)
        if path not in cycle_files(live.slug, cycle):
            return None
        df = _read_layers(live_download(file_url(live.slug, cycle, path)), rec, None, geometry)

    for col in rec.columns.measures:
        df[col] = df[col].fillna(0.0) if col in df else 0.0
    if rec.prob_scale != 1.0:
        probs = list(rec.probabilities)
        df[probs] = df[probs] * rec.prob_scale
    if geometry:
        df = df[~df.geometry.is_empty].reset_index(drop=True)
    return df


def for_display(gdf):
    """`gdf` in the output CRS, with coordinates trimmed for a lighter payload."""
    gdf = gdf.to_crs(OUTPUT_CRS)
    gdf["geometry"] = set_precision(gdf.geometry.values, PRECISION_DEG)
    return gdf[~gdf.geometry.is_empty]


def exposure_row(s, first_col, name, group, columns, population):
    """One table row: buildings, people, area and road length in `group`.

    Always subscript `group[columns.type]`: on a GeoDataFrame `.type` is the
    geometry type, not the column.
    """
    people = group[columns.population].sum()
    share = 100 * people / population if population else 0.0
    return {
        s[first_col]: name,
        s["col_buildings"]: f"{(group[columns.type] == columns.building).sum():,}",
        s["col_population"]: f"{people:,.0f}",
        s["col_area"]: f"{group[columns.area].sum():,.0f}",
        s["col_roads_km"]: f"{group[columns.length].sum() / 1000:,.1f}",
        s["col_pop_share"]: f"{share:.2f}%",
    }
