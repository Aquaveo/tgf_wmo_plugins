"""Classified buildings and roads as a dynamic map layer.

The feature counterpart to `hazard_layer`, which draws the raster classification.
Each building and road already carries the four exceedance probabilities -- taken
as the maximum over its own footprint -- so the escalating gates classify a
feature directly, no rasterising involved.

Only features that land in a hazard level are returned. Normal is the large
majority and adds nothing a basemap does not already show, and dropping it keeps
the payload to a few hundred KB rather than the ~2 MB source.
"""

import json
from functools import lru_cache

import geopandas as gpd
import pandas as pd
import pyogrio
from shapely import set_precision
from tethysapp.tethysdash.plugin_helpers import (
    LayerConfigurationBuilder,
    TethysDashPlugin,
)

from tgf_wmo_plugins.classification import LEVELS, ThresholdGates
from tgf_wmo_plugins.common import (
    ANTIGUA_BARBUDA_FEATURES_CSV_URL,
    COMOROS_FEATURES_URL,
    FEATURES_URL,
    GPKG_LAYERS,
    GPKG_WHERE,
    HAITI_FEATURES_CSV_URL,
    PROB_FIELDS,
    cached_download,
    scale_probabilities,
)
from tgf_wmo_plugins.strings import STRINGS, threshold_args

# The frontend does not bundle proj4, so OpenLayers only resolves EPSG:4326 and
# EPSG:3857. Anything else -- the source data is UTM 15N -- would be read as raw
# map units and land nowhere near Guatemala.
OUTPUT_CRS = "EPSG:4326"
# ~0.1 m at this latitude. Enough to trim digits off metre-scale footprints
# without visibly moving them.
PRECISION_DEG = 1e-6

# Geometry source per country. Guatemala ships one GeoJSON; Haiti and Antigua
# and Barbuda ship a geopackage whose buildings and roads are separate layers.
FEATURES_URLS = {
    "guatemala": FEATURES_URL,
    "haiti": HAITI_FEATURES_CSV_URL,
    "antigua_barbuda": ANTIGUA_BARBUDA_FEATURES_CSV_URL,
    "comoros": COMOROS_FEATURES_URL,
}

# Measures the popup shows, per country. A geopackage layer only carries the
# ones that apply to it -- a road has no population, a building no length -- so
# the reader fills the rest with zero and every row reads the same way.
MEASURES = {
    "guatemala": ["poblacion", "area_m2", "longitud_m"],
    "haiti": ["population", "surface_m2", "longueur_m"],
    "antigua_barbuda": [
        "population_per_building",
        "building_area_m2",
        "road_length_m",
    ],
    # The Comoros geopackage happens to spell these exactly as Antigua and
    # Barbuda's does, so the popup needs no renames on top of the probabilities.
    "comoros": [
        "population_per_building",
        "building_area_m2",
        "road_length_m",
    ],
}

# Attributes carried through to the GeoJSON, per country. `peligro` drives the
# styling rules and `nivel` is its translated label, so both are always present.
FEATURE_COLUMNS = {
    "guatemala": ["tipo", "nivel", "peligro", *MEASURES["guatemala"]],
    "haiti": ["type", "nivel", "peligro", *MEASURES["haiti"]],
    "antigua_barbuda": ["type", "nivel", "peligro", *MEASURES["antigua_barbuda"]],
    "comoros": ["type", "nivel", "peligro", *MEASURES["comoros"]],
}


def _read_geopackage(url, country):
    """Both geopackage layers, stacked, with the probability fields aligned.

    The buildings layers store their severe extraction under `probability_30cm`,
    misnamed upstream, so the renames put it back before the gates are applied.
    Only the fields the plugin uses are read; the rest of the layer stays on
    disk.
    """
    path = cached_download(url)
    parts = []
    for type_, (layer, renames) in GPKG_LAYERS[country].items():
        # Fields already carrying their final name, plus the ones to rename,
        # plus whichever measures this layer actually has.
        available = set(pyogrio.read_info(path, layer=layer)["fields"])
        wanted = [f for f in PROB_FIELDS[country] if f not in renames.values()]
        wanted += list(renames) + MEASURES[country]
        part = pyogrio.read_dataframe(
            path,
            layer=layer,
            columns=[f for f in wanted if f in available],
            # Only Comoros sets one: its file is per island, so the commune is
            # selected in the driver rather than after 130,000 geometries have
            # been built. `where` is evaluated on the layer, so the column it
            # names does not have to be among `columns`.
            where=GPKG_WHERE.get(country),
            read_geometry=True,
            use_arrow=True,
        )
        part = part.rename(columns=renames)
        part["type"] = type_
        parts.append(part)

    stacked = gpd.GeoDataFrame(pd.concat(parts, ignore_index=True), crs=parts[0].crs)
    for col in MEASURES[country]:
        stacked[col] = stacked[col].fillna(0.0) if col in stacked else 0.0
    return scale_probabilities(stacked, country)


@lru_cache(maxsize=4)
def _load(country):
    """Source features for `country`, already in the output CRS.

    Cached: only the gates change between requests, and both the download and
    the reprojection are wasted work to repeat.
    """
    url = FEATURES_URLS[country]
    if country in GPKG_LAYERS:
        gdf = _read_geopackage(url, country)
    else:
        gdf = gpd.read_file(url)
    gdf = gdf.to_crs(OUTPUT_CRS)
    gdf["geometry"] = set_precision(gdf.geometry.values, PRECISION_DEG)
    return gdf[~gdf.geometry.is_empty]


class BaseImpactLayer(ThresholdGates, TethysDashPlugin):
    LANG = None
    country = None
    type = "map_layer"
    dynamic_map_layer = True

    def run(self):
        s = STRINGS[self.LANG]
        builder = LayerConfigurationBuilder(s["impact_layer_name"], "GeoJSON")
        builder.set_plugin_source(self.name, self.received_args)
        builder.set_style(self._style(s))
        builder.set_legend(
            {
                "title": s["hazard_legend"],
                "items": [
                    {"label": s["levels"][value], "color": color, "symbol": "square"}
                    for value, color in LEVELS
                ],
            }
        )
        return builder.build()

    def fetch_features(self):
        s = STRINGS[self.LANG]
        country = self.country
        gates = self.gates()

        self.send_update(s["msg_loading_features"], percentage_complete=20)
        gdf = _load(country).copy()

        self.send_update(s["msg_classifying"], percentage_complete=60)
        gdf["peligro"] = 0
        for field, (value, _color) in zip(PROB_FIELDS[country], LEVELS):
            gdf.loc[gdf[field] >= gates[value], "peligro"] = value

        exposed = gdf[gdf.peligro > 0].copy()
        exposed["nivel"] = exposed.peligro.map(s["levels"])

        self.send_update(
            s["msg_at_risk"].format(count=len(exposed)), percentage_complete=100
        )
        columns = FEATURE_COLUMNS[country]
        collection = json.loads(exposed[columns + ["geometry"]].to_json())
        collection["crs"] = {"type": "name", "properties": {"name": OUTPUT_CRS}}
        return collection

    @staticmethod
    def _style(s):
        """Rule-based styling on `peligro`, for both polygons and lines.

        See hazard_layer._style for why the rule shape is what it is.
        """
        rules = []
        for value, color in LEVELS:
            condition = {
                "conditionField": "peligro",
                "conditionType": "=",
                "conditionValue": str(value),
            }
            rules.append(
                {
                    "name": f"{s['levels'][value]} ({s['buildings']})",
                    "geometryType": "polygon",
                    **condition,
                    "fill": color,
                    "stroke": color,
                    "strokeWidth": "1",
                }
            )
            rules.append(
                {
                    "name": f"{s['levels'][value]} ({s['roads']})",
                    "geometryType": "linestring",
                    **condition,
                    "stroke": color,
                    "strokeWidth": "3",
                }
            )
        return {
            "default": {
                "polygon": {"fill": "#9e9e9e", "stroke": "#9e9e9e", "strokeWidth": "0"},
                "linestring": {"stroke": "#9e9e9e", "strokeWidth": "1"},
            },
            "rules": rules,
        }


class ImpactLayerGuatemala(BaseImpactLayer):
    LANG = "es"
    country = "guatemala"
    args = threshold_args(LANG)
    name = "uffis_impact_layer_guatemala"
    label = f"{STRINGS[LANG]['impact_layer_label']} (Guatemala)"
    group = STRINGS[LANG]["group"]
    tags = ["inundación", "impacto", "IBF", "map_layer", "dinámico", "español"]
    description = STRINGS[LANG]["impact_layer_desc"]


class ImpactLayerHaiti(BaseImpactLayer):
    LANG = "fr"
    country = "haiti"
    args = threshold_args(LANG)
    name = "uffis_impact_layer_haiti"
    label = f"{STRINGS[LANG]['impact_layer_label']} (Haiti)"
    group = STRINGS[LANG]["group"]
    tags = ["inondation", "impact", "IBF", "map_layer", "dynamique", "français"]
    description = STRINGS[LANG]["impact_layer_desc"]


class ImpactLayerAntiguaBarbuda(BaseImpactLayer):
    LANG = "en"
    country = "antigua_barbuda"
    args = threshold_args(LANG)
    name = "uffis_impact_layer_antigua_barbuda"
    label = f"{STRINGS[LANG]['impact_layer_label']} (Antigua and Barbuda)"
    group = STRINGS[LANG]["group"]
    tags = ["flood", "impact", "IBF", "map_layer", "dynamic", "english"]
    description = STRINGS[LANG]["impact_layer_desc"]


class ImpactLayerComoros(BaseImpactLayer):
    LANG = "fr"
    country = "comoros"
    args = threshold_args(LANG)
    name = "uffis_impact_layer_comoros"
    label = f"{STRINGS[LANG]['impact_layer_label']} (Comores)"
    group = STRINGS[LANG]["group"]
    tags = ["inondation", "impact", "IBF", "map_layer", "dynamique", "français"]
    description = STRINGS[LANG]["impact_layer_desc"]
