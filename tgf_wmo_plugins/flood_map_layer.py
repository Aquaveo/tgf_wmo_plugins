"""TITO's flood probability rasters as a dynamic GeoTIFF map layer.

Each cycle publishes, per site and flood source, the probability of the water
reaching 10, 30, 70 and 100 cm. This layer draws one of them as the raster it
is -- the hazard layer classifies the same files into polygons instead -- and
follows the cycle binding into live and sample cycles alike.
"""

from tethysapp.tethysdash.plugin_helpers import (
    LayerConfigurationBuilder,
    geotiff_source,
)

from tgf_wmo_plugins.base import CountryChoiceInput, CountryPlugin, LiveData
from tgf_wmo_plugins.countries import ANTIGUA_BARBUDA, COMOROS, DEPTHS, GUATEMALA, HAITI
from tgf_wmo_plugins.strings import LIVE_ARGS, STRINGS
from tgf_wmo_plugins.tito import cycle_files, cycle_label, file_url

DEFAULT_MIN_PROBABILITY = 0.05  # the SFFS reporting threshold

# FGS likelihood bands, one blue from light to dark. A Ranges class takes the
# values up to and including its bound, so each bound sits just under 20/40/60%:
# FGS puts exactly 20% in Low, and TITO's 1/50-member probabilities hit it.
BANDS = [
    (0.1999, "#9ec5f4", "< 20 %"),
    (0.3999, "#5598e7", "20-40 %"),
    (0.5999, "#256abf", "40-60 %"),
    (1.0, "#104281", "≥ 60 %"),
]


class BaseFloodMapLayer(LiveData, CountryPlugin):
    family = "flood_map_layer"
    strings_key = "flood_map_layer"
    type = "map_layer"
    dynamic_map_layer = True
    dynamic_map_layer_source = "GeoTIFF"
    uses_rasters = True

    @classmethod
    def has_training(cls, country):
        return False

    @classmethod
    def country_args(cls, country):
        s, names = STRINGS[country.lang], LIVE_ARGS[country.lang]
        return {
            **cls.unit_args(country),
            **cls.live_args(country),
            names["depth"]: [{"value": d, "label": s["depth_choices"][d]} for d in DEPTHS],
            names["likelihood"]: "number",
        }

    def selected_depth(self):
        value = self.get_arg(LIVE_ARGS[self.country.lang]["depth"])
        return value if value in DEPTHS else DEPTHS[0]

    def probability_floor(self):
        """Arrives from the GUI as a string; anything unusable is the default."""
        try:
            value = float(self.get_arg(LIVE_ARGS[self.country.lang]["likelihood"]))
        except (TypeError, ValueError):
            return DEFAULT_MIN_PROBABILITY
        return value if 0 <= value < 1 else DEFAULT_MIN_PROBABILITY

    def run(self):
        """Configure-time scaffold: the binding, the class colours and legend."""
        s = self.strings
        labels = [f"{s['likelihood_levels'][i]} ({band[2]})" for i, band in enumerate(BANDS)]
        builder = LayerConfigurationBuilder(s["flood_map_layer_name"], "GeoTIFF")
        builder.set_plugin_source(self.name, self.received_args)
        builder.set_raster_classes(
            "ranges",
            [{"value": bound, "color": color, "label": label}
             for (bound, color, _), label in zip(BANDS, labels)],
        )
        builder.set_legend({
            "title": s["flood_map_legend"],
            "items": [{"label": label, "color": color, "symbol": "square"}
                      for (_, color, _), label in zip(BANDS, labels)],
        })
        return builder.build()

    def fetch_source(self):
        """Runtime source: the chosen raster of the bound cycle."""
        s, live = self.strings, self.country.live
        cycle = self.selected_cycle()
        paths = live.prob_paths(self.scope(), self.variant(), cycle)
        path = paths[DEPTHS.index(self.selected_depth())]
        if path not in cycle_files(live.slug, cycle):
            raise ValueError(s["msg_not_triggered"].format(
                site=self.scope_label(), cycle=cycle_label(cycle, s["sample_tag"])))
        return geotiff_source(file_url(live.slug, cycle, path), mask_below=self.probability_floor())


class BaseDepthFilter(CountryChoiceInput):
    """The flood depth whose probability the flood probability layer shows."""

    family = "depth_filter"
    strings_key = "depth_filter"

    def choices(self, s):
        return [(depth, s["depth_filter_choices"][depth]) for depth in DEPTHS]

    def initial(self):
        return DEPTHS[0]


class FloodMapLayerGuatemala(BaseFloodMapLayer):
    country = GUATEMALA


class FloodMapLayerHaiti(BaseFloodMapLayer):
    country = HAITI


class FloodMapLayerAntiguaBarbuda(BaseFloodMapLayer):
    country = ANTIGUA_BARBUDA


class FloodMapLayerComoros(BaseFloodMapLayer):
    country = COMOROS


class DepthFilterGuatemala(BaseDepthFilter):
    country = GUATEMALA


class DepthFilterHaiti(BaseDepthFilter):
    country = HAITI


class DepthFilterAntiguaBarbuda(BaseDepthFilter):
    country = ANTIGUA_BARBUDA


class DepthFilterComoros(BaseDepthFilter):
    country = COMOROS
