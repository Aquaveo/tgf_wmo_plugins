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
    FEATURES_URL,
    HAITI_FEATURES_CSV_URL,
    HAITI_LAYERS,
    PROB_FIELDS,
    cached_download,
)
from tgf_wmo_plugins.strings import STRINGS, threshold_args

# The frontend does not bundle proj4, so OpenLayers only resolves EPSG:4326 and
# EPSG:3857. Anything else -- the source data is UTM 15N -- would be read as raw
# map units and land nowhere near Guatemala.
OUTPUT_CRS = "EPSG:4326"
# ~0.1 m at this latitude. Enough to trim digits off metre-scale footprints
# without visibly moving them.
PRECISION_DEG = 1e-6

# Geometry source per country. Guatemala ships one GeoJSON; Haiti ships a
# geopackage whose buildings and roads are separate layers.
FEATURES_URLS = {
    "guatemala": FEATURES_URL,
    "haiti": HAITI_FEATURES_CSV_URL,
}

# Attributes carried through to the GeoJSON, per country. `peligro` drives the
# styling rules and `nivel` is its translated label, so both are always present.
FEATURE_COLUMNS = {
    "guatemala": ["tipo", "nivel", "peligro", "poblacion", "area_m2", "longitud_m"],
    "haiti": ["type", "nivel", "peligro", "population", "surface_m2", "longueur_m"],
}

# Measures each Haiti layer does not carry -- a road has no population, a
# building no length -- filled so the styling and the popup can read every row.
HAITI_MEASURES = ["population", "surface_m2", "longueur_m"]


def _read_haiti(url):
    """Both geopackage layers, stacked, with the probability fields aligned.

    The buildings layer stores its severe extraction under `probability_30cm`,
    misnamed upstream, so the renames put it back before the gates are applied.
    """
    path = cached_download(url)
    parts = []
    for type_, (layer, renames) in HAITI_LAYERS.items():
        # Fields already carrying their final name, plus the ones to rename.
        columns = [f for f in PROB_FIELDS["haiti"] if f not in renames.values()]
        part = pyogrio.read_dataframe(
            path,
            layer=layer,
            columns=columns + list(renames),
            read_geometry=True,
            use_arrow=True,
        )
        part = part.rename(columns=renames)
        part["type"] = type_
        parts.append(part)

    stacked = gpd.GeoDataFrame(pd.concat(parts, ignore_index=True), crs=parts[0].crs)
    for col in HAITI_MEASURES:
        stacked[col] = stacked[col].fillna(0.0) if col in stacked else 0.0
    return stacked


@lru_cache(maxsize=4)
def _load(country):
    """Source features for `country`, already in the output CRS.

    Cached: only the gates change between requests, and both the download and
    the reprojection are wasted work to repeat.
    """
    url = FEATURES_URLS[country]
    gdf = _read_haiti(url) if country == "haiti" else gpd.read_file(url)
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
    name = "UFFIS_impact_layer_guatemala"
    label = f"{STRINGS[LANG]['impact_layer_label']} (Guatemala)"
    group = STRINGS[LANG]["group"]
    tags = ["inundación", "impacto", "IBF", "map_layer", "dinámico", "español"]
    description = STRINGS[LANG]["impact_layer_desc"]


class ImpactLayerHaiti(BaseImpactLayer):
    LANG = "fr"
    country = "haiti"
    args = threshold_args(LANG)
    name = "UFFIS_impact_layer_haiti"
    label = f"{STRINGS[LANG]['impact_layer_label']} (Haiti)"
    group = STRINGS[LANG]["group"]
    tags = ["inondation", "impact", "IBF", "map_layer", "dynamique", "français"]
    description = STRINGS[LANG]["impact_layer_desc"]
