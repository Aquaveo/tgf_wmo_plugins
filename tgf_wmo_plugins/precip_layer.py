"""Rainfall accumulation for Guatemala from the live TITO workflow, as a map layer.

TITO runs hourly and publishes each cycle under
https://tito.uffis.org/outputs/guatemala/<cycle>/, where <cycle> is the start time
as YYYYMMDD.HHMMSS in UTC. The ensemble summary rasters sit at
<grid>/summary/qpeaccum_<period>_<statistic>.<cycle>.tif. Only recent cycles are
kept -- the bucket expires them within two days -- so a date much older than
that has nothing to show.
"""

import json
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

from tethysapp.tethysdash.plugin_helpers import (
    LayerConfigurationBuilder,
    TethysDashPlugin,
)

OUTPUTS = "https://tito.uffis.org/outputs/guatemala"

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

# The tito.uffis.org legend for rainfall: class i covers breaks[i] <= mm <
# breaks[i + 1], the last runs open-ended, and anything under 1 mm -- the -9999
# nodata included -- is left transparent.
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


def _get(url):
    with urllib.request.urlopen(url, timeout=30) as response:
        return response.read()


def latest_cycle():
    """The newest published cycle, e.g. '20261001.190000'."""
    return json.loads(_get(f"{OUTPUTS}/latest.json"))["cycle"]


CYCLE_FORMAT = "%Y%m%d.%H%M%S"
# The bucket deletes a cycle about two days after it is written, so nothing
# older than this is worth asking for.
LOOKBACK_HOURS = 54


def available_cycles():
    """Every cycle still published, newest first.

    latest.json names only the newest cycle and the bucket cannot be listed, so
    each hour back from it is probed for its index.json. Cycles are hourly but
    an hour is sometimes skipped, which is why every hour is checked rather than
    counting back.
    """
    newest = datetime.strptime(latest_cycle(), CYCLE_FORMAT)
    candidates = [
        (newest - timedelta(hours=h)).strftime(CYCLE_FORMAT)
        for h in range(LOOKBACK_HOURS)
    ]
    with ThreadPoolExecutor(max_workers=16) as pool:
        found = pool.map(lambda c: exists(f"{OUTPUTS}/{c}/index.json"), candidates)
    return [cycle for cycle, ok in zip(candidates, found) if ok]


def exists(url):
    request = urllib.request.Request(url, method="HEAD")
    try:
        with urllib.request.urlopen(request, timeout=30):
            return True
    except urllib.error.HTTPError:
        return False


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
        "Guatemala. Set the date to 'latest' for the newest cycle."
    )
    args = {
        "date": "date",
        "grid": GRIDS,
        "statistic": STATISTICS,
        "period": PERIODS,
    }
    dynamic_map_layer = True

    def run(self):
        grid = _choice(self.get_arg("grid"), GRIDS)
        statistic = _choice(self.get_arg("statistic"), STATISTICS)
        period = _choice(self.get_arg("period"), PERIODS)
        cycle = self.cycle()

        url = (
            f"{OUTPUTS}/{cycle}/{grid}/summary/"
            f"qpeaccum_{period}_{statistic}.{cycle}.tif"
        )
        if not exists(url):
            raise ValueError(
                f"no rainfall raster for cycle {cycle} ({grid}, {period}, "
                f"{statistic}); the newest cycle is {latest_cycle()}, and "
                "cycles more than about two days old are deleted"
            )

        builder = LayerConfigurationBuilder(
            f"Rainfall {period} {statistic}, {cycle} UTC", "GeoTIFF"
        )
        # Raw millimetres rather than OpenLayers' normalised bytes, so the
        # breaks below compare against real values, and no interpolation,
        # which would blend colours across class edges.
        builder.set_source_properties(url=url, normalize=False, interpolate=False)
        builder.set_style({"color": self._color()})
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

    def cycle(self):
        """The cycle the date names: the newest one for "latest", otherwise
        the cycle that starts in the same UTC hour as the date."""
        date = self.get_arg("date")
        if date in (None, "", "latest"):
            return latest_cycle()
        return date.strftime("%Y%m%d.%H0000")

    @staticmethod
    def _color():
        expression = ["case", ["<", ["band", 1], BREAKS_MM[0]], [0, 0, 0, 0]]
        for upper, color in zip(BREAKS_MM[1:], COLORS):
            expression += [["<", ["band", 1], upper], color]
        return expression + [COLORS[-1]]

    @staticmethod
    def _labels():
        pairs = zip(BREAKS_MM, BREAKS_MM[1:])
        return [f"{lo} - {hi}" for lo, hi in pairs] + [f"{BREAKS_MM[-1]} or more"]


class CycleTimesGuatemala(TethysDashPlugin):
    """A dropdown of every Guatemala cycle still published, newest first.

    Each value is the cycle stamp exactly as the URLs spell it, e.g.
    '20261001.200000', so a layer can name its file with the variable alone:

        .../outputs/guatemala/${Date}/guatemala_900m/summary/
        qpeaccum_forecast_median.${Date}.tif

    Every product in a cycle -- the ensemble summaries, the flood maps, the
    impact files -- carries that same stamp, so one list serves them all. There
    is no "latest" entry because no URL can spell it; the newest cycle is the
    first choice and the initial value instead.
    """

    name = "uffis_cycle_times_guatemala"
    group = "UFFIS Live"
    label = "Available Cycles (Guatemala)"
    type = "variable_input"
    tags = ["uffis", "tito", "guatemala", "date"]
    description = (
        "Every hourly TITO cycle still published for Guatemala, newest first, "
        "valued as the cycle stamp the file URLs use."
    )

    def run(self):
        cycles = available_cycles()
        choices = [
            {
                "label": f"{datetime.strptime(c, CYCLE_FORMAT):%Y-%m-%d %H:%M} UTC",
                "value": c,
            }
            for c in cycles
        ]
        return {
            "variable_name": "Date",
            "initial_value": cycles[0],
            "variable_options_source": "dropdown",
            "metadata": {"choices": choices},
        }
