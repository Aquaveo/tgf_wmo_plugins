"""Rainfall accumulation from the live TITO workflow, as a map layer.

The ensemble summary rasters sit at
<grid>/summary/qpeaccum_<period>_<statistic>.<cycle>.tif; see tito.py for how
cycles are published and how long they are kept.
"""

from tethysapp.tethysdash.plugin_helpers import (
    LayerConfigurationBuilder,
    TethysDashPlugin,
    geotiff_source,
)

from tgf_wmo_plugins.tito import (
    LATEST,
    TRAINING,
    cycle_files,
    file_url,
    latest_cycle,
    resolve_cycle,
)

from tgf_wmo_plugins.countries import ANTIGUA_BARBUDA, COMOROS, GUATEMALA, HAITI

STATISTICS = [
    {"value": "median", "label": "Median"},
    {"value": "min", "label": "Minimum"},
    {"value": "max", "label": "Maximum"},
]
PERIODS = [
    {"value": "forecast", "label": "Forecast"},
    {"value": "nowcast", "label": "Nowcast"},
]

# The tito.uffis.org legend for rainfall: class i covers breaks[i] to
# breaks[i + 1] mm, and the last runs open-ended.
BREAKS_MM = [1, 5, 10, 25, 50, 75, 100, 150, 250]
COLORS = [
    "#d9f0a3",
    "#addd8e",
    "#41ab5d",
    "#ffffb2",
    "#fdae61",
    "#f46d43",
    "#d73027",
    "#a50026",
    "#6a3d9a",
]


def _choice(value, options):
    """`value` when it is one of `options`, else the first option.

    An unset arg arrives as None, and an unbound variable as its literal
    "${...}" text, so neither can be trusted to be a valid choice.
    """
    values = [o["value"] for o in options]
    return value if value in values else values[0]


class BasePrecipLayer(TethysDashPlugin):
    """Set `country`; its `live.rain_grids` name the grids to offer.

    The labels are English in every country, like the cycle inputs, as they
    were when only the Guatemala layer existed.
    """

    country = None
    group = "UFFIS Live"
    type = "map_layer"

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        country = cls.__dict__.get("country")
        if country is None:
            return
        cls.name = f"uffis_precip_layer_{country.key}"
        cls.label = f"Rainfall Accumulation ({country.label_name})"
        cls.tags = ["uffis", "tito", "rainfall", country.key]
        cls.description = (
            f"Ensemble rainfall accumulation from one hourly TITO cycle for "
            f"{country.label_name}. Bind the cycle to an Available Cycles input, "
            "or leave it at 'latest'."
        )
        # `cycle` takes the stamp an Available Cycles input carries; it is not
        # a "date" arg, which would parse the stamp as a datetime.
        cls.args = {
            "cycle": [{"value": LATEST, "label": "Latest cycle"}],
            "grid": cls.grids(),
            "statistic": STATISTICS,
            "period": PERIODS,
        }

    @classmethod
    def grids(cls):
        return [{"value": g, "label": label} for g, label in cls.country.live.rain_grids]

    dynamic_map_layer = True
    dynamic_map_layer_source = "GeoTIFF"

    def run(self):
        """Configure-time scaffold: the binding, the class colours and legend."""
        builder = LayerConfigurationBuilder("Rainfall accumulation", "GeoTIFF")
        builder.set_plugin_source(self.name, self.received_args)
        builder.set_raster_classes(
            "ranges",
            [
                {"value": upper, "color": color, "label": label}
                for upper, color, label in zip(BREAKS_MM[1:], COLORS, self._labels())
            ],
            fallback_color=COLORS[-1],
        )
        builder.set_legend(
            {
                "title": "Rainfall accumulation (mm)",
                "items": [
                    {"label": label, "color": color, "symbol": "square"}
                    for label, color in zip(self._labels(), COLORS)
                ],
            }
        )
        return builder.build()

    def fetch_source(self):
        """Runtime source: the cycle's raster, re-fetched when a binding changes."""
        slug = self.country.live.slug
        grid = _choice(self.get_arg("grid"), self.grids())
        statistic = _choice(self.get_arg("statistic"), STATISTICS)
        period = _choice(self.get_arg("period"), PERIODS)
        cycle = resolve_cycle(self.get_arg("cycle"), slug)
        if cycle == TRAINING:
            cycle = latest_cycle(slug)

        path = f"{grid}/summary/qpeaccum_{period}_{statistic}.{cycle}.tif"
        if path not in cycle_files(slug, cycle):
            raise ValueError(f"cycle {cycle} published no {period} {statistic} rainfall on {grid}")
        # Under 1 mm, the -9999 nodata included, is left transparent.
        return geotiff_source(file_url(slug, cycle, path), mask_below=BREAKS_MM[0])

    @staticmethod
    def _labels():
        pairs = zip(BREAKS_MM, BREAKS_MM[1:])
        return [f"{lo} - {hi}" for lo, hi in pairs] + [f"{BREAKS_MM[-1]} or more"]


class PrecipLayerGuatemala(BasePrecipLayer):
    country = GUATEMALA


class PrecipLayerHaiti(BasePrecipLayer):
    country = HAITI


class PrecipLayerAntiguaBarbuda(BasePrecipLayer):
    country = ANTIGUA_BARBUDA


class PrecipLayerComoros(BasePrecipLayer):
    country = COMOROS
