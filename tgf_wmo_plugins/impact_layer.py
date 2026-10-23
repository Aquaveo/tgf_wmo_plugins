"""Classified buildings and roads as a dynamic map layer.

The feature counterpart to `hazard_layer`. Only features that land in a hazard
level are returned: Normal is the large majority and adds nothing a basemap does
not show, and dropping it is what keeps the payload tractable.
"""

import json
from functools import lru_cache

from tethysapp.tethysdash.plugin_helpers import LayerConfigurationBuilder

from tgf_wmo_plugins.base import CountryPlugin, LiveData
from tgf_wmo_plugins.classification import LEVELS, ThresholdGates, classify_receptors
from tgf_wmo_plugins.countries import (
    ANTIGUA_BARBUDA,
    BARBADOS,
    COMOROS,
    GUATEMALA,
    HAITI,
)
from tgf_wmo_plugins.receptors import OUTPUT_CRS, for_display, load_receptors
from tgf_wmo_plugins.tito import TRAINING


@lru_cache(maxsize=8)
def _load(key, scope, cycle):
    """Receptors in the output CRS, or None. Cached: only the gates change
    between requests, and the reprojection is wasted work to repeat."""
    gdf = load_receptors(key, scope, True, cycle)
    return None if gdf is None else for_display(gdf)


def feature_style(s, attr, labels, colors):
    """Rule-based styling on a class attribute, for polygon buildings and
    linestring roads. See hazard_layer._style for why the rules look like this."""
    rules = []
    for value, color in colors:
        condition = {
            "conditionField": s[attr],
            "conditionType": "=",
            "conditionValue": str(value),
        }
        rules.append(
            {
                "name": f"{labels[value]} ({s['buildings']})",
                "geometryType": "polygon",
                "strokeWidth": "1",
                **condition,
                "fill": color,
                "stroke": color,
            }
        )
        rules.append(
            {
                "name": f"{labels[value]} ({s['roads']})",
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


def feature_collection(gdf, columns):
    if gdf is None:
        collection = {"type": "FeatureCollection", "features": []}
    else:
        collection = json.loads(gdf[columns + ["geometry"]].to_json())
    collection["crs"] = {"type": "name", "properties": {"name": OUTPUT_CRS}}
    return collection


class BaseImpactLayer(ThresholdGates, LiveData, CountryPlugin):
    family = "impact_layer"
    strings_key = "impact_layer"
    type = "map_layer"
    dynamic_map_layer = True

    def run(self):
        s = self.strings
        builder = LayerConfigurationBuilder(s["impact_layer_name"], "GeoJSON")
        builder.set_plugin_source(self.name, self.received_args)
        builder.set_style(feature_style(s, "attr_hazard", s["levels"], LEVELS))
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
        s = self.strings
        cycle = self.selected_cycle()
        rec = self.country.receptors if cycle == TRAINING else self.country.live.receptors

        self.send_update(s["msg_loading_features"], percentage_complete=20)
        gdf = _load(self.country.key, self.scope(), cycle)
        if gdf is None:
            message = s["msg_no_receptors"].format(site=self.scope_label(), cycle=cycle)
            self.send_update(message, percentage_complete=100)
            return feature_collection(None, [])

        self.send_update(s["msg_classifying"], percentage_complete=60)
        hazard = classify_receptors(gdf, rec.probabilities, self.gates())
        exposed = gdf[hazard > 0].copy()
        exposed[s["attr_hazard"]] = hazard[hazard > 0]
        exposed[s["attr_level"]] = exposed[s["attr_hazard"]].map(s["levels"])

        self.send_update(
            s["msg_at_risk"].format(count=len(exposed)), percentage_complete=100
        )
        cols = rec.columns
        return feature_collection(
            exposed, [cols.type, s["attr_level"], s["attr_hazard"], *cols.measures]
        )


class ImpactLayerGuatemala(BaseImpactLayer):
    country = GUATEMALA


class ImpactLayerHaiti(BaseImpactLayer):
    country = HAITI


class ImpactLayerAntiguaBarbuda(BaseImpactLayer):
    country = ANTIGUA_BARBUDA


class ImpactLayerBarbados(BaseImpactLayer):
    country = BARBADOS


class ImpactLayerComoros(BaseImpactLayer):
    country = COMOROS
