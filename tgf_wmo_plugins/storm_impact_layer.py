"""Buildings and roads coloured by flood depth for one storm, as a map layer."""

import json

from tethysapp.tethysdash.plugin_helpers import (
    LayerConfigurationBuilder,
    TethysDashPlugin,
)

from tgf_wmo_plugins.common import (
    COMOROS_STORM_OPTIONS,
    COMOROS_UNIT_OPTIONS,
    COMOROS_UNITS,
    FIRST_WET_STORM,
    STORM_OPTIONS,
    coerce_index,
)
from tgf_wmo_plugins.storm_impact import (
    COMOROS_DEFAULT_STORM,
    COMOROS_MEASURES,
    DEPTH_BANDS,
    banded_features,
    comoros_banded_features,
    store_grid,
)
from tgf_wmo_plugins.strings import STRINGS


class BaseStormImpactLayer(TethysDashPlugin):
    LANG = None
    type = "map_layer"
    dynamic_map_layer = True
    args = {"index": STORM_OPTIONS}

    def run(self):
        s = STRINGS[self.LANG]
        builder = LayerConfigurationBuilder(s["storm_layer_name"], "GeoJSON")
        builder.set_plugin_source(self.name, self.received_args)
        builder.set_style(self._style(s))
        builder.set_legend(
            {
                "title": s["depth_legend"],
                "items": [
                    {"label": s["bands"][value], "color": color, "symbol": "square"}
                    for value, color, _floor in DEPTH_BANDS
                ],
            }
        )
        return builder.build()

    def fetch_features(self):
        s = STRINGS[self.LANG]
        index = coerce_index(self.get_arg("index", FIRST_WET_STORM), FIRST_WET_STORM)

        self.send_update(s["msg_sampling"], percentage_complete=40)
        flooded = banded_features(index).copy()
        flooded = flooded.rename(columns={"banda": s["attr_band"],
                                          "profundidad_m": s["attr_depth"]})
        flooded[s["attr_level"]] = flooded[s["attr_band"]].map(s["bands"])

        self.send_update(
            s["msg_flooded"].format(count=len(flooded)), percentage_complete=100
        )
        columns = [
            "tipo",
            s["attr_level"],
            s["attr_band"],
            s["attr_depth"],
            "poblacion",
            "area_m2",
            "longitud_m",
        ]
        collection = json.loads(flooded[columns + ["geometry"]].to_json())
        # The store's grid is already EPSG:3857, which OpenLayers resolves
        # natively -- no proj4 needed and no reprojection on the way out.
        _transform, _shape, crs = store_grid()
        collection["crs"] = {"type": "name", "properties": {"name": crs}}
        return collection

    @staticmethod
    def _style(s):
        """Rule-based styling on the depth-band attribute. See hazard_layer._style."""
        rules = []
        for value, color, _floor in DEPTH_BANDS:
            condition = {
                "conditionField": s["attr_band"],
                "conditionType": "=",
                "conditionValue": str(value),
            }
            rules.append(
                {
                    "name": f"{s['bands'][value]} ({s['buildings']})",
                    "geometryType": "polygon",
                    **condition,
                    "fill": color,
                    "stroke": color,
                    "strokeWidth": "1",
                }
            )
            rules.append(
                {
                    "name": f"{s['bands'][value]} ({s['roads']})",
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


class StormImpactLayerGuatemala(BaseStormImpactLayer):
    LANG = "es"
    name = "uffis_storm_impact_layer_guatemala"
    label = f"{STRINGS['es']['storm_layer_label']} (Guatemala)"
    group = STRINGS["es"]["group"]
    tags = ["inundación", "impacto", "zarr", "tormenta", "map_layer", "español"]
    description = STRINGS["es"]["storm_layer_desc"]


# Vector output is EPSG:4326 for every country. The raster loaders resolve a
# published CRS on demand from the generated EPSG table, but `loadGeoJSON` hands
# `crs.properties.name` straight to OpenLayers without that lookup, so a
# plugin-returned collection has to name a projection the map already holds.
# This is the same OUTPUT_CRS impact_layer settles on, for the same reason.
OUTPUT_CRS = "EPSG:4326"


class BaseStormImpactLayerComoros(BaseStormImpactLayer):
    """One commune's flooded buildings and roads, for one storm of its library.

    Only the two ends differ from the Guatemala layer: which features are
    sampled, and that the result is reprojected out of the island model's
    EPSG:5629 grid. The style, the legend and the run() scaffold are inherited.
    """

    args = {"commune": COMOROS_UNIT_OPTIONS, "index": COMOROS_STORM_OPTIONS}

    def fetch_features(self):
        s = STRINGS[self.LANG]
        unit = self.get_arg("commune", COMOROS_UNITS[0][0])
        index = coerce_index(
            self.get_arg("index", COMOROS_DEFAULT_STORM), COMOROS_DEFAULT_STORM
        )

        self.send_update(s["msg_sampling"], percentage_complete=40)
        flooded = comoros_banded_features(unit, index).copy()
        flooded = flooded.rename(columns={"banda": s["attr_band"],
                                          "profundidad_m": s["attr_depth"]})
        flooded[s["attr_level"]] = flooded[s["attr_band"]].map(s["bands"])
        flooded = flooded.to_crs(OUTPUT_CRS)

        self.send_update(
            s["msg_flooded"].format(count=len(flooded)), percentage_complete=100
        )
        columns = ["type", s["attr_level"], s["attr_band"], s["attr_depth"],
                   *COMOROS_MEASURES]
        collection = json.loads(flooded[columns + ["geometry"]].to_json())
        collection["crs"] = {"type": "name", "properties": {"name": OUTPUT_CRS}}
        return collection


class StormImpactLayerComoros(BaseStormImpactLayerComoros):
    LANG = "fr"
    name = "uffis_storm_impact_layer_comoros"
    label = f"{STRINGS['fr']['storm_layer_label']} (Comores)"
    group = STRINGS["fr"]["group"]
    tags = ["inondation", "impact", "zarr", "tempête", "map_layer", "français"]
    description = STRINGS["fr"]["storm_layer_desc"]
