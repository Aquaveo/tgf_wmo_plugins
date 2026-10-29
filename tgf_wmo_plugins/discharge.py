"""Forecast discharge at a river gauge, every ensemble member, as a plot.

Each TITO cycle runs the hydrological model once per forecast member and writes
a time series per gauge: `<grid>/<forcing>/<member>/ts.<gauge>.crest.<cycle>.csv`.
The forcing is the rainfall source the member was driven by, so members are
shown as the range of its members with their median. The forcings cover
different windows -- stream_sat the hours before the cycle, stormlab the ~30 h
after it, scampr both -- so each is summarised on its own time axis, and the
cycle start is marked.
"""

import io
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from functools import lru_cache

import pandas as pd

from tgf_wmo_plugins.base import CountryPlugin, LiveData
from tgf_wmo_plugins.countries import GUATEMALA, HAITI
from tgf_wmo_plugins.strings import LIVE_ARGS, STRINGS
from tgf_wmo_plugins.tito import (
    LATEST,
    SAMPLE,
    _get,
    cycle_files,
    cycle_label,
    cycle_time,
    file_url,
    stamp,
)

TIME, DISCHARGE, OBSERVED = "Time", "Discharge(m^3 s^-1)", "Observed(m^3 s^-1)"

# Drawn in this order, which is also time order: the satellite run covers the
# hours before the cycle, the nowcast both sides of it, the forecast after it.
# The colours follow the tito.uffis.org viewer, so the two read alike.
FORCINGS = {
    "stream_sat": "#5b6470",
    "scampr": "#eb6834",
    "stormlab": "#2a78d6",
}
OTHER_COLOR = "#8a8a85"
INK = "#2b2b29"
BAND_OPACITY = 0.25


def _rgba(hex_color, alpha):
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    return f"rgba({r}, {g}, {b}, {alpha})"


@lru_cache(maxsize=32)
def gauge_members(slug, cycle, grid, gauge):
    """Every member's series for one gauge, as {(forcing, member): frame}.

    Cached per cycle, since a published cycle never changes; the members are
    fetched in parallel, as there are about seventy small files.
    """
    suffix = f"/ts.{gauge}.crest.{stamp(cycle)}.csv"
    paths = sorted(
        p for p in cycle_files(slug, cycle) if p.startswith(f"{grid}/") and p.endswith(suffix)
    )

    def read(path):
        frame = pd.read_csv(io.BytesIO(_get(file_url(slug, cycle, path))))
        return frame[[TIME, DISCHARGE, OBSERVED]]

    with ThreadPoolExecutor(max_workers=16) as pool:
        frames = list(pool.map(read, paths))
    return {tuple(p.split("/")[1:3]): f for p, f in zip(paths, frames)}


class BaseDischarge(LiveData, CountryPlugin):
    family = "discharge"
    strings_key = "discharge"
    type = "plotly"

    @classmethod
    def has_training(cls, country):
        return False

    @classmethod
    def country_args(cls, country):
        s, names = STRINGS[country.lang], LIVE_ARGS[country.lang]
        cycles = [{"value": LATEST, "label": s["cycle_latest"]}]
        if country.live.sample:
            cycles.append({"value": SAMPLE, "label": s["cycle_sample"]})
        return {
            names["cycle"]: cycles,
            names["gauge"]: [{"value": g, "label": label} for g, label in country.live.gauges],
        }

    def gauge(self):
        gauges = dict(self.country.live.gauges)
        value = self.get_arg(LIVE_ARGS[self.country.lang]["gauge"])
        return value if value in gauges else next(iter(gauges))

    def run(self):
        s, live = self.strings, self.country.live
        cycle, gauge = self.selected_cycle(), self.gauge()
        label = dict(live.gauges)[gauge]
        members = gauge_members(live.slug, cycle, live.gauge_grid, gauge)

        layout = {
            "title": {"text": f"{s['discharge_title'].format(gauge=label)} "
                              f"({cycle_label(cycle, s['sample_tag'])})"},
            "xaxis": {"title": {"text": s["axis_time"]}, "showgrid": False},
            "yaxis": {"title": {"text": s["axis_discharge"]}, "rangemode": "tozero",
                      "gridcolor": "#e6e5e0"},
            "hovermode": "x unified",
            "legend": {"orientation": "h", "x": 0, "y": -0.48, "yanchor": "top"},
            "margin": {"t": 50, "r": 20, "b": 170},
            "shapes": [{
                "type": "line", "xref": "x", "yref": "paper", "y0": 0, "y1": 1,
                "x0": f"{cycle_time(cycle):%Y-%m-%d %H:%M}",
                "x1": f"{cycle_time(cycle):%Y-%m-%d %H:%M}",
                "line": {"color": INK, "width": 1.5, "dash": "dash"},
            }],
        }
        if not members:
            layout["title"]["text"] = s["msg_no_gauge"].format(gauge=label, cycle=cycle)
            return {"data": [], "layout": layout}

        # One frame per forcing, a column per member: the members of a forcing
        # share a time axis, while the forcings do not.
        by_forcing = {}
        for (forcing, _member), frame in members.items():
            by_forcing.setdefault(forcing, []).append(frame.set_index(TIME)[DISCHARGE])
        order = [f for f in FORCINGS if f in by_forcing] + sorted(set(by_forcing) - set(FORCINGS))

        data, peaks = [], []
        for forcing in order:
            stacked = pd.concat(by_forcing[forcing], axis=1)
            low, high, median = stacked.min(axis=1), stacked.max(axis=1), stacked.median(axis=1)
            color = FORCINGS.get(forcing, OTHER_COLOR)
            name = s["forcings"].get(forcing, forcing)
            x = stacked.index.tolist()
            # The band is the lower edge, then the upper edge filled down to it.
            data.append({
                "type": "scatter", "mode": "lines", "x": x, "y": low.round(2).tolist(),
                "line": {"width": 0}, "legendgroup": forcing, "showlegend": False,
                "hoverinfo": "skip",
            })
            data.append({
                "type": "scatter", "mode": "lines", "x": x, "y": high.round(2).tolist(),
                "line": {"width": 0}, "fill": "tonexty",
                "fillcolor": _rgba(color, BAND_OPACITY),
                "legendgroup": forcing, "showlegend": False, "hoverinfo": "skip",
            })
            data.append({
                "type": "scatter", "mode": "lines", "x": x, "y": median.round(2).tolist(),
                "name": f"{name}, {s['members'].format(n=stacked.shape[1])}",
                "legendgroup": forcing, "line": {"color": color, "width": 2.5},
                "hovertemplate": "%{y:.1f} m³/s",
            })
            peak_time = datetime.strptime(median.idxmax(), "%Y-%m-%d %H:%M")
            peaks.append(f"{name} " + s["peak_at"].format(
                value=median.max(), time=f"{peak_time:%H:%M %d/%m}"
            ))

        observed = next(iter(members.values())).set_index(TIME)[OBSERVED].dropna()
        if not observed.empty:
            data.append({
                "type": "scatter", "mode": "markers",
                "x": observed.index.tolist(), "y": observed.tolist(),
                "name": s["observed"],
                "marker": {"color": INK, "size": 8, "symbol": "circle-open"},
            })

        # The peaks read as a caption under the plot, one forcing per line.
        layout["annotations"] = [{
            "xref": "paper", "yref": "paper", "x": 0, "y": -0.16,
            "xanchor": "left", "yanchor": "top", "align": "left", "showarrow": False,
            "text": f"<b>{s['median_peaks']}</b><br>" + "<br>".join(peaks),
        }]
        return {"data": data, "layout": layout}


class DischargeGuatemala(BaseDischarge):
    country = GUATEMALA


class DischargeHaiti(BaseDischarge):
    country = HAITI
