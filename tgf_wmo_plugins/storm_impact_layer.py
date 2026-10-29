"""Buildings and roads coloured by flood depth, as a map layer.

For a country with live TITO cycles, by the depth each feature reaches with at
least the chosen probability; Barbados, which TITO does not run, by its depth in
one storm of the training library.
"""

from tethysapp.tethysdash.plugin_helpers import LayerConfigurationBuilder

from tgf_wmo_plugins.base import CountryPlugin
from tgf_wmo_plugins.countries import (
    ANTIGUA_BARBUDA,
    BARBADOS,
    COMOROS,
    GUATEMALA,
    HAITI,
)
from tgf_wmo_plugins.impact_layer import _load, feature_collection, feature_style
from tgf_wmo_plugins.likely_depth import LIKELY_BANDS, LikelyDepth, likely_band
from tgf_wmo_plugins.receptors import for_display
from tgf_wmo_plugins.storm_impact import DEPTH_BANDS, StormIndex, banded_features
from tgf_wmo_plugins.strings import STRINGS


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


class LiveStormImpactLayer(LikelyDepth, CountryPlugin):
    family = "storm_impact_layer"
    strings_key = "storm_layer"
    type = "map_layer"
    dynamic_map_layer = True

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if "country" in cls.__dict__:
            cls.description = STRINGS[cls.country.lang]["likely_layer_desc"]

    def run(self):
        s = self.strings
        builder = LayerConfigurationBuilder(s["likely_layer_name"], "GeoJSON")
        builder.set_plugin_source(self.name, self.received_args)
        builder.set_style(feature_style(s, "attr_band", s["likely_bands"], LIKELY_BANDS))
        builder.set_legend(
            {
                "title": s["depth_legend"],
                "items": [
                    {"label": s["likely_bands"][v], "color": color, "symbol": "square"}
                    for v, color in LIKELY_BANDS
                ],
            }
        )
        return builder.build()

    def fetch_features(self):
        s = self.strings
        cycle, p = self.selected_cycle(), self.likelihood()
        rec = self.country.live.receptors

        self.send_update(s["msg_loading_features"], percentage_complete=20)
        gdf = _load(self.country.key, self.scope(), cycle)
        if gdf is None:
            message = s["msg_no_receptors"].format(site=self.scope_label(), cycle=cycle)
            self.send_update(message, percentage_complete=100)
            return feature_collection(None, [])

        band = likely_band(gdf, rec.probabilities, p)
        flooded = gdf[band > 0].copy()
        flooded[s["attr_band"]] = band[band > 0]
        flooded[s["attr_level"]] = flooded[s["attr_band"]].map(s["likely_bands"])
        flooded[list(rec.probabilities)] = flooded[list(rec.probabilities)].round(2)

        self.send_update(s["msg_flooded"].format(count=len(flooded)), percentage_complete=100)
        cols = rec.columns
        return feature_collection(
            flooded,
            [cols.type, s["attr_level"], s["attr_band"], *rec.probabilities, *cols.measures],
        )


class StormImpactLayerGuatemala(LiveStormImpactLayer):
    country = GUATEMALA


class StormImpactLayerHaiti(LiveStormImpactLayer):
    country = HAITI


class StormImpactLayerAntiguaBarbuda(LiveStormImpactLayer):
    country = ANTIGUA_BARBUDA


class StormImpactLayerBarbados(BaseStormImpactLayer):
    country = BARBADOS


class StormImpactLayerComoros(LiveStormImpactLayer):
    country = COMOROS
