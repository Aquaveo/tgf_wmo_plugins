"""Current conditions at V.C. Bird International Airport, Antigua.

Antigua and Barbuda Meteorological Services publishes its hourly SYNOP through
WMO's WIS2 as open "core" data, and the Caribbean WIS2 node serves the decoded
reports as GeoJSON over plain HTTP: one feature per variable per report, no
credentials. It is the only public rain gauge in the country, so these plugins
make the most of it: a card of the latest conditions, a plot and a table of the
recent hours, and a marker for the map.

Rainfall arrives as 6-hour totals at 00, 06, 12 and 18 UTC and a 24-hour total
at 12 UTC. The other variables are hourly. The feed keeps a long history, so
the request window is bounded by the `hours` argument and the result cached for
five minutes, which is more often than the station reports.
"""

import json
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

import pandas as pd
from tethysapp.tethysdash.plugin_helpers import (
    LayerConfigurationBuilder,
    TethysDashPlugin,
)

COLLECTION = "urn:wmo:md:ag-antiguamet:core.surface-based-observations.synop"
ITEMS_URL = f"https://wiscaribbeancmo.org/oapi/collections/{COLLECTION}/items"
PAGE_SIZE = 1000
TIMEOUT = 60
CACHE_SECONDS = 300

GROUP = "Observations (English)"
ATTRIBUTION = (
    "Antigua and Barbuda Meteorological Services, hourly SYNOP via WMO WIS2 "
    "(Caribbean Meteorological Organization node)"
)

STATION = {
    "wigos_id": "0-20000-0-78862",
    "wmo_id": "78862",
    "name": "V.C. Bird International Airport",
    "lon": -61.79279,
    "lat": 17.13996,
}

# WIS2 variable name -> column name in the hourly frame.
COLUMNS = {
    "air_temperature": "temperature",
    "dewpoint_temperature": "dewpoint",
    "relative_humidity": "humidity",
    "pressure_reduced_to_mean_sea_level": "pressure",
    "24hour_pressure_change": "pressure_change",
    "wind_speed": "wind_speed",
    "wind_direction": "wind_direction",
    "horizontal_visibility": "visibility",
    "cloud_cover_total": "cloud_cover",
}
PRECIPITATION = "total_precipitation_or_total_water_equivalent"

HOURS_CHOICES = (24, 48, 72, 168)
HOURS_OPTIONS = [{"value": h, "label": f"Last {h} hours"} for h in HOURS_CHOICES]

COMPASS = [
    "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
    "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW",
]
KNOTS_PER_MS = 1.943844

MISSING = "—"


def _get_json(url):  # pragma: no cover
    """One GET, parsed. Kept separate so tests can stand in for the network.

    Not covered: the body is the network call itself, and the tests replace
    the function rather than reach the Caribbean node.
    """
    with urllib.request.urlopen(url, timeout=TIMEOUT) as response:
        return json.load(response)


def _iso(when):
    return when.strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch_features(start, end):
    """Every feature reported between `start` and `end`, following the API's paging.

    pygeoapi hands back at most PAGE_SIZE features per page and a `next` link
    while more remain; a page with no features ends the walk regardless.
    """
    query = {"f": "json", "limit": PAGE_SIZE, "datetime": f"{_iso(start)}/{_iso(end)}"}
    url = f"{ITEMS_URL}?{urllib.parse.urlencode(query)}"
    features = []
    while url:
        page = _get_json(url)
        batch = page.get("features", [])
        if not batch:
            break
        features.extend(batch)
        url = next((link["href"] for link in page.get("links", []) if link.get("rel") == "next"), None)
    return features


def period(phenomenon_time, report_time):
    """Start and end of a measurement; instantaneous values get the report time twice."""
    if phenomenon_time and "/" in phenomenon_time:
        start, end = phenomenon_time.split("/")
        return pd.Timestamp(start), pd.Timestamp(end)
    stamp = pd.Timestamp(report_time)
    return stamp, stamp


def tidy(features):
    """Long frame: one row per (report time, variable)."""
    rows = []
    for feature in features:
        props = feature["properties"]
        start, end = period(props.get("phenomenonTime"), props["reportTime"])
        rows.append(
            {
                "time": pd.Timestamp(props["reportTime"]),
                "name": props["name"],
                "value": props["value"],
                "start": start,
                "end": end,
            }
        )
    frame = pd.DataFrame(rows, columns=["time", "name", "value", "start", "end"])
    return frame.sort_values(["time", "name"], kind="stable").reset_index(drop=True)


_cache = {}


def observations(hours, now=None):
    """The last `hours` of reports as a long frame, cached for CACHE_SECONDS.

    The station reports hourly and the feed is a public service, so four
    plugins on one dashboard share a single fetch instead of hitting it on
    every refresh.
    """
    now = now or datetime.now(timezone.utc)
    hit = _cache.get(hours)
    if hit and time.monotonic() - hit[0] < CACHE_SECONDS:
        return hit[1]
    frame = tidy(fetch_features(now - timedelta(hours=hours), now))
    _cache[hours] = (time.monotonic(), frame)
    return frame


def hourly(frame):
    """One row per report time, the COLUMNS as columns, in report order."""
    subset = frame[frame.name.isin(COLUMNS)]
    wide = subset.pivot_table(index="time", columns="name", values="value", aggfunc="last")
    return wide.rename(columns=COLUMNS).reindex(columns=list(COLUMNS.values())).sort_index()


def rainfall(frame):
    """Precipitation totals with the length of their accumulation in hours."""
    subset = frame[frame.name == PRECIPITATION].copy()
    subset["hours"] = ((subset.end - subset.start) / pd.Timedelta(hours=1)).round().astype(int)
    subset = subset.rename(columns={"value": "mm"})
    return subset[["time", "start", "end", "hours", "mm"]].reset_index(drop=True)


def rain_summary(rain, latest):
    """Latest 6-hour total, latest 24-hour total, and the 6-hour totals summed over the day to `latest`."""
    six = rain[rain.hours == 6]
    day = rain[rain.hours == 24]
    last_six = six.iloc[-1] if len(six) else None
    last_day = day.iloc[-1] if len(day) else None
    window = six[(six.end > latest - pd.Timedelta(hours=24)) & (six.end <= latest)]
    rolling = float(window.mm.sum()) if len(window) else None
    return last_six, last_day, rolling


def compass(degrees):
    return COMPASS[int((degrees % 360) / 22.5 + 0.5) % 16]


def wind_text(speed, direction):
    """'9 kt (4.6 m/s) from E (070°)'; calm and missing spelled out."""
    if pd.isna(speed):
        return MISSING
    if speed == 0:
        return "Calm"
    text = f"{speed * KNOTS_PER_MS:.0f} kt ({speed:.1f} m/s)"
    if pd.isna(direction):
        return text
    return f"{text} from {compass(direction)} ({direction:03.0f}°)"


def fmt(value, unit="", digits=1):
    """A number with its unit, or the missing mark."""
    if pd.isna(value):
        return MISSING
    return f"{value:.{digits}f}{unit}"


def age_text(latest, now):
    minutes = int((now - latest).total_seconds() // 60)
    if minutes < 60:
        return f"{minutes} min ago"
    hours, minutes = divmod(minutes, 60)
    return f"{hours} h {minutes:02d} min ago"


def _stamps(index):
    return [stamp.strftime("%Y-%m-%dT%H:%M:%SZ") for stamp in index]


def _values(series):
    return [None if pd.isna(v) else float(v) for v in series]


def rain_labels(rain):
    """Report time -> '7.0 / 6 h, 27.8 / 24 h' for the table."""
    labels = {}
    for row in rain.itertuples():
        part = f"{row.mm:.1f} / {row.hours} h"
        labels[row.time] = f"{labels[row.time]}, {part}" if row.time in labels else part
    return labels


class BaseObservations(TethysDashPlugin):
    """Shared identity; each subclass sets type, name, label, args and run()."""

    group = GROUP
    attribution = ATTRIBUTION
    tags = ["observations", "rain gauge", "SYNOP", "WIS2", "Antigua and Barbuda", "english"]

    def hours_arg(self, default):
        """The `hours` argument as one of HOURS_CHOICES, else `default`.

        Not named `hours`: Intake sets every argument as an attribute on the
        instance, so a method of that name would be replaced by the value.
        """
        try:
            hours = int(self.get_arg("hours", default))
        except (TypeError, ValueError):
            return default
        return hours if hours in HOURS_CHOICES else default


class CurrentConditionsCardAntiguaBarbuda(BaseObservations):
    name = "obs_card_antigua_barbuda"
    label = "Current Conditions (Antigua and Barbuda)"
    type = "card"
    args = {}
    description = (
        "The latest hourly SYNOP from V.C. Bird International Airport: temperature, "
        "humidity, pressure, wind and the recent rainfall totals."
    )

    def run(self):
        now = datetime.now(timezone.utc)
        frame = observations(48, now)
        if frame.empty:
            return {"data": [{"color": "#888888", "label": STATION["name"], "value": "No observations received", "icon": "BiError"}]}
        wide = hourly(frame)
        latest = wide.index[-1]
        row = wide.iloc[-1]
        last_six, last_day, rolling = rain_summary(rainfall(frame), latest)

        pressure = fmt(row.pressure, " hPa")
        if not pd.isna(row.pressure_change):
            pressure += f" ({row.pressure_change:+.1f} in 24 h)"
        six = f"{last_six.mm:.1f} mm to {last_six.end:%H:%M} UTC" if last_six is not None else MISSING
        if rolling is not None:
            six += f", {rolling:.1f} mm in the last 24 h of totals"
        day = f"{last_day.mm:.1f} mm to {last_day.end:%d %b %H:%M} UTC" if last_day is not None else MISSING

        return {
            "data": [
                {"color": "#4c78a8", "label": f"{STATION['name']}, observed", "value": f"{latest:%d %b %H:%M} UTC ({age_text(latest, now)})", "icon": "BiTime"},
                {"color": "#e45756", "label": "Temperature / dew point", "value": f"{fmt(row.temperature, ' °C')} / {fmt(row.dewpoint, ' °C')}", "icon": "BiThermometer"},
                {"color": "#72b7b2", "label": "Humidity", "value": fmt(row.humidity, " %", 0), "icon": "BiDroplet"},
                {"color": "#54a24b", "label": "Pressure (MSL)", "value": pressure, "icon": "BiTachometer"},
                {"color": "#b279a2", "label": "Wind", "value": wind_text(row.wind_speed, row.wind_direction), "icon": "BiWind"},
                {"color": "#1f77b4", "label": "Rain, last 6-hour total", "value": six, "icon": "BiCloudRain"},
                {"color": "#0b4f8a", "label": "Rain, last 24-hour total", "value": day, "icon": "BiCloudDrizzle"},
            ]
        }


class ObservationsPlotAntiguaBarbuda(BaseObservations):
    name = "obs_plot_antigua_barbuda"
    label = "Recent Observations Plot (Antigua and Barbuda)"
    type = "plotly"
    args = {"hours": HOURS_OPTIONS}
    description = (
        "Temperature and dew point, the 6-hour rainfall totals and sea-level pressure "
        "at V.C. Bird International Airport over the last one to seven days."
    )

    def run(self):
        hours = self.hours_arg(48)
        frame = observations(hours)
        title = f"{STATION['name']}, last {hours} hours"
        if frame.empty:
            return {
                "data": [],
                "layout": {"title": {"text": title}, "annotations": [{"text": "No observations received", "showarrow": False, "x": 0.5, "y": 0.5, "xref": "paper", "yref": "paper"}]},
                "config": {"responsive": True, "displaylogo": False},
            }
        wide = hourly(frame)
        six = rainfall(frame)
        six = six[six.hours == 6]
        stamps = _stamps(wide.index)
        return {
            "data": [
                {"type": "scatter", "mode": "lines", "name": "Temperature (°C)", "x": stamps, "y": _values(wide.temperature), "line": {"color": "#e45756", "width": 2}, "yaxis": "y"},
                {"type": "scatter", "mode": "lines", "name": "Dew point (°C)", "x": stamps, "y": _values(wide.dewpoint), "line": {"color": "#54a24b", "width": 2, "dash": "dot"}, "yaxis": "y"},
                {"type": "bar", "name": "Rain (mm / 6 h)", "x": _stamps(six.start + pd.Timedelta(hours=3)), "y": _values(six.mm), "width": 6 * 3600 * 1000, "marker": {"color": "#1f77b4"}, "yaxis": "y2", "hovertemplate": "%{y:.1f} mm to %{x}<extra></extra>"},
                {"type": "scatter", "mode": "lines", "name": "Pressure (hPa)", "x": stamps, "y": _values(wide.pressure), "line": {"color": "#7f7f7f", "width": 1.5}, "yaxis": "y3"},
            ],
            "layout": {
                "title": {"text": title, "x": 0.02},
                "xaxis": {"title": {"text": "UTC"}, "domain": [0, 1]},
                "yaxis": {"title": {"text": "°C"}, "domain": [0.56, 1]},
                "yaxis2": {"title": {"text": "mm / 6 h"}, "domain": [0, 0.44], "rangemode": "tozero"},
                "yaxis3": {"title": {"text": "hPa"}, "overlaying": "y2", "side": "right", "showgrid": False},
                "legend": {"orientation": "h", "y": 1.12, "x": 0},
                "margin": {"l": 60, "r": 60, "t": 70, "b": 50},
                "hovermode": "x unified",
            },
            "config": {"responsive": True, "displaylogo": False},
        }


class ObservationsTableAntiguaBarbuda(BaseObservations):
    name = "obs_table_antigua_barbuda"
    label = "Recent Observations Table (Antigua and Barbuda)"
    type = "table"
    args = {"hours": HOURS_OPTIONS}
    description = (
        "The hourly SYNOP reports from V.C. Bird International Airport, newest first, "
        "with the 6-hour and 24-hour rainfall totals on the hours they are reported."
    )

    def run(self):
        hours = self.hours_arg(24)
        frame = observations(hours)
        title = f"{STATION['name']}, hourly reports, last {hours} hours"
        if frame.empty:
            return {"title": title, "data": []}
        wide = hourly(frame)
        labels = rain_labels(rainfall(frame))
        rows = []
        for stamp, row in wide[::-1].iterrows():
            rows.append(
                {
                    "Time (UTC)": f"{stamp:%d %b %H:%M}",
                    "Temp (°C)": fmt(row.temperature),
                    "Dew pt (°C)": fmt(row.dewpoint),
                    "RH (%)": fmt(row.humidity, digits=0),
                    "Pressure (hPa)": fmt(row.pressure),
                    "Wind": wind_text(row.wind_speed, row.wind_direction),
                    "Rain (mm)": labels.get(stamp, ""),
                }
            )
        return {"title": title, "data": rows}


class ObservationsStationLayerAntiguaBarbuda(BaseObservations):
    name = "obs_station_layer_antigua_barbuda"
    label = "Observation Station (Antigua and Barbuda)"
    type = "map_layer"
    args = {}
    description = (
        "V.C. Bird International Airport as a map marker carrying its latest "
        "observation, for the popup."
    )
    LAYER_NAME = "V.C. Bird Airport observations"
    ALIASES = {
        "observed": "Observed (UTC)",
        "temperature": "Temperature (°C)",
        "dewpoint": "Dew point (°C)",
        "humidity": "Humidity (%)",
        "pressure": "Pressure (hPa)",
        "wind": "Wind",
        "rain_6h": "Rain, last 6-hour total",
        "rain_24h": "Rain, last 24-hour total",
    }

    def run(self):
        frame = observations(48)
        properties = {"station": STATION["name"], "wmo_id": STATION["wmo_id"]}
        if not frame.empty:
            wide = hourly(frame)
            latest = wide.index[-1]
            row = wide.iloc[-1]
            last_six, last_day, _ = rain_summary(rainfall(frame), latest)
            properties.update(
                observed=f"{latest:%Y-%m-%d %H:%M}",
                temperature=fmt(row.temperature),
                dewpoint=fmt(row.dewpoint),
                humidity=fmt(row.humidity, digits=0),
                pressure=fmt(row.pressure),
                wind=wind_text(row.wind_speed, row.wind_direction),
                rain_6h=f"{last_six.mm:.1f} mm to {last_six.end:%H:%M} UTC" if last_six is not None else MISSING,
                rain_24h=f"{last_day.mm:.1f} mm to {last_day.end:%d %b %H:%M} UTC" if last_day is not None else MISSING,
            )
        geojson = {
            "type": "FeatureCollection",
            "crs": {"type": "name", "properties": {"name": "EPSG:4326"}},
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [STATION["lon"], STATION["lat"]]},
                    "properties": properties,
                }
            ],
        }
        builder = LayerConfigurationBuilder(self.LAYER_NAME, "GeoJSON")
        builder.set_geojson(geojson)
        builder.set_style({"default": {"point": {"fill": "#1f77b4", "stroke": "#ffffff", "strokeWidth": "2", "size": 9, "shape": "circle"}}})
        builder.set_legend({"title": "Observations", "items": [{"label": "SYNOP station", "color": "#1f77b4", "symbol": "circle"}]})
        for key, alias in self.ALIASES.items():
            builder.add_attribute_alias(key, alias, self.LAYER_NAME)
        return builder.build()
