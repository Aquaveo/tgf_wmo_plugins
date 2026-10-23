"""Buildings and roads coloured by flood depth for one storm, as a map layer."""

from tethysapp.tethysdash.plugin_helpers import LayerConfigurationBuilder

from tgf_wmo_plugins.base import CountryPlugin
from tgf_wmo_plugins.countries import BARBADOS, COMOROS, GUATEMALA
from tgf_wmo_plugins.impact_layer import feature_collection, feature_style
from tgf_wmo_plugins.receptors import for_display
from tgf_wmo_plugins.storm_impact import DEPTH_BANDS, StormIndex, banded_features


class BaseStormImpactLayer(StormIndex, CountryPlugin):
    family = "storm_impact_layer"
    strings_key = "storm_layer"
    type = "map_layer"
    dynamic_map_layer = True

    def run(self):
        s = self.strings
        builder = LayerConfigurationBuilder(s["storm_layer_name"], "GeoJSON")
        builder.set_plugin_source(self.name, self.received_args)
        colors = [(value, color) for value, color, _floor in DEPTH_BANDS]
        builder.set_style(feature_style(s, "attr_band", s["bands"], colors))
        builder.set_legend(
            {
                "title": s["depth_legend"],
                "items": [
                    {"label": s["bands"][value], "color": color, "symbol": "square"}
                    for value, color in colors
                ],
            }
        )
        return builder.build()

    def fetch_features(self):
        s = self.strings
        self.send_update(s["msg_sampling"], percentage_complete=40)
        flooded = banded_features(self.country.key, self.unit(), self.storm_index())
        flooded = flooded.rename(columns={"band": s["attr_band"],
                                          "depth_m": s["attr_depth"]})
        flooded[s["attr_level"]] = flooded[s["attr_band"]].map(s["bands"])
        flooded = for_display(flooded)

        self.send_update(
            s["msg_flooded"].format(count=len(flooded)), percentage_complete=100
        )
        cols = self.country.receptors.columns
        return feature_collection(
            flooded,
            [cols.type, s["attr_level"], s["attr_band"], s["attr_depth"], *cols.measures],
        )


class StormImpactLayerGuatemala(BaseStormImpactLayer):
    country = GUATEMALA


class StormImpactLayerBarbados(BaseStormImpactLayer):
    country = BARBADOS


class StormImpactLayerComoros(BaseStormImpactLayer):
    country = COMOROS
