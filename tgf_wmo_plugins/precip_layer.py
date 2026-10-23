"""Rainfall accumulation for Guatemala from the live TITO workflow, as a map layer.

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

SLUG = "guatemala"

GRIDS = [
    {"value": "guatemala_900m", "label": "900 m (national)"},
    {"value": "guatemala_90m", "label": "90 m (flood sites)"},
]
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


class PrecipLayerGuatemala(TethysDashPlugin):
    name = "uffis_precip_layer_guatemala"
    group = "UFFIS Live"
    label = "Rainfall Accumulation (Guatemala)"
    type = "map_layer"
    tags = ["uffis", "tito", "rainfall", "guatemala"]
    description = (
        "Ensemble rainfall accumulation from one hourly TITO cycle for "
        "Guatemala. Bind the cycle to an Available Cycles input, or leave it "
        "at 'latest'."
    )
    # `cycle` takes the stamp an Available Cycles input carries; it is not a
    # "date" arg, which would parse the stamp as a datetime.
    args = {
        "cycle": [{"value": LATEST, "label": "Latest cycle"}],
        "grid": GRIDS,
        "statistic": STATISTICS,
        "period": PERIODS,
    }
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
        grid = _choice(self.get_arg("grid"), GRIDS)
        statistic = _choice(self.get_arg("statistic"), STATISTICS)
        period = _choice(self.get_arg("period"), PERIODS)
        cycle = resolve_cycle(self.get_arg("cycle"), SLUG)
        if cycle == TRAINING:
            cycle = latest_cycle(SLUG)

        path = f"{grid}/summary/qpeaccum_{period}_{statistic}.{cycle}.tif"
        if path not in cycle_files(SLUG, cycle):
            raise ValueError(f"cycle {cycle} published no {period} {statistic} rainfall on {grid}")
        # Under 1 mm, the -9999 nodata included, is left transparent.
        return geotiff_source(file_url(SLUG, cycle, path), mask_below=BREAKS_MM[0])

    @staticmethod
    def _labels():
        pairs = zip(BREAKS_MM, BREAKS_MM[1:])
        return [f"{lo} - {hi}" for lo, hi in pairs] + [f"{BREAKS_MM[-1]} or more"]
