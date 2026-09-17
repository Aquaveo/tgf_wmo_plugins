"""The V.C. Bird observation plugins, against a stand-in for the WIS2 feed."""

import json
from datetime import datetime, timezone

import pandas as pd
import pytest

from tgf_wmo_plugins import observations as obs

NOW = datetime(2026, 9, 17, 16, 55, tzinfo=timezone.utc)
STATION = "0-20000-0-78862"


def feature(report_time, name, value, phenomenon=None, units="x"):
    return {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [-61.79279, 17.13996]},
        "properties": {
            "name": name,
            "value": value,
            "units": units,
            "reportTime": report_time,
            "phenomenonTime": phenomenon,
            "wigos_station_identifier": STATION,
        },
    }


def hourly_report(stamp, **values):
    """One SYNOP hour with the usual instantaneous variables."""
    defaults = dict(
        air_temperature=30.0,
        dewpoint_temperature=24.0,
        relative_humidity=70.0,
        pressure_reduced_to_mean_sea_level=1015.0,
        wind_speed=5.0,
        wind_direction=90.0,
        horizontal_visibility=10000.0,
        cloud_cover_total=50.0,
    )
    defaults.update(values)
    return [feature(stamp, name, value) for name, value in defaults.items()]


# Two days of hourly reports, with 6-hour totals at the synoptic hours and a
# 24-hour total at 12 UTC, mirroring what the Caribbean node serves.
FEATURES = []
for hour in range(0, 48):
    stamp = pd.Timestamp("2026-09-15T17:00:00Z") + pd.Timedelta(hours=hour)
    iso = stamp.strftime("%Y-%m-%dT%H:%M:%SZ")
    FEATURES += hourly_report(iso, air_temperature=26.0 + hour % 10)
    FEATURES.append(feature(iso, "24hour_pressure_change", 1.1))
    if stamp.hour % 6 == 0:
        start = (stamp - pd.Timedelta(hours=6)).strftime("%Y-%m-%dT%H:%M:%SZ")
        FEATURES.append(feature(iso, obs.PRECIPITATION, 3.5 if stamp.hour == 0 else 0.0, f"{start}/{iso}", "kg m-2"))
    if stamp.hour == 12:
        start = (stamp - pd.Timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%SZ")
        FEATURES.append(feature(iso, obs.PRECIPITATION, 27.8, f"{start}/{iso}", "kg m-2"))
LATEST = pd.Timestamp("2026-09-17T16:00:00Z")


@pytest.fixture(autouse=True)
def feed(monkeypatch):
    """Serve FEATURES in two pages and keep the cache cold between tests."""
    calls = []

    def get_json(url):
        calls.append(url)
        if "page=2" in url:
            return {"features": FEATURES[600:], "links": []}
        return {"features": FEATURES[:600], "links": [{"rel": "next", "href": obs.ITEMS_URL + "?page=2"}]}

    monkeypatch.setattr(obs, "_get_json", get_json)
    monkeypatch.setattr(obs, "_cache", {})
    return calls


def test_fetch_features_follows_next_links_and_stops_on_empty_page(feed, monkeypatch):
    got = obs.fetch_features(NOW - pd.Timedelta(hours=48), NOW)
    assert len(got) == len(FEATURES)
    assert "datetime=2026-09-15T16%3A55%3A00Z%2F2026-09-17T16%3A55%3A00Z" in feed[0]
    monkeypatch.setattr(obs, "_get_json", lambda url: {"features": [], "links": [{"rel": "next", "href": "x"}]})
    assert obs.fetch_features(NOW, NOW) == []


def test_observations_caches_per_window(feed, monkeypatch):
    clock = iter([100.0, 100.0, 1000.0, 1000.0, 2000.0])
    monkeypatch.setattr(obs.time, "monotonic", lambda: next(clock))
    first = obs.observations(48, NOW)
    assert obs.observations(48, NOW) is first
    assert len(feed) == 2  # one fetch, two pages
    obs.observations(48, NOW)
    assert len(feed) == 4  # expired after CACHE_SECONDS
    monkeypatch.setattr(obs, "_get_json", lambda url: {"features": []})
    assert obs.observations(24).empty  # a different window is a different entry


def test_period_and_tidy_shapes():
    start, end = obs.period("2026-09-17T00:00:00Z/2026-09-17T06:00:00Z", "2026-09-17T06:00:00Z")
    assert (end - start) == pd.Timedelta(hours=6)
    stamp, same = obs.period(None, "2026-09-17T06:00:00Z")
    assert stamp == same == pd.Timestamp("2026-09-17T06:00:00Z")
    frame = obs.tidy(FEATURES)
    assert list(frame.columns) == ["time", "name", "value", "start", "end"]
    assert frame.time.is_monotonic_increasing
    assert obs.tidy([]).empty


def test_hourly_and_rainfall_tables():
    frame = obs.tidy(FEATURES)
    wide = obs.hourly(frame)
    assert list(wide.columns) == list(obs.COLUMNS.values())
    assert len(wide) == 48 and wide.index[-1] == LATEST
    assert wide.temperature.iloc[0] == 26.0
    rain = obs.rainfall(frame)
    assert sorted(rain.hours.unique()) == [6, 24]
    assert rain[rain.hours == 24].mm.tolist() == [27.8, 27.8]


def test_rain_summary_rolls_six_hour_totals_over_a_day():
    rain = obs.rainfall(obs.tidy(FEATURES))
    six, day, rolling = obs.rain_summary(rain, LATEST)
    assert six.end == pd.Timestamp("2026-09-17T12:00:00Z") and six.mm == 0.0
    assert day.mm == 27.8
    assert rolling == 3.5  # only the 00 UTC total is wet
    empty = obs.rainfall(obs.tidy([]))
    assert obs.rain_summary(empty, LATEST) == (None, None, None)


@pytest.mark.parametrize(
    "degrees, point",
    [(0, "N"), (11.24, "N"), (11.25, "NNE"), (90, "E"), (348.74, "NNW"), (348.75, "N"), (360, "N"), (-90, "W")],
)
def test_compass_points(degrees, point):
    assert obs.compass(degrees) == point


def test_wind_text_variants():
    assert obs.wind_text(float("nan"), 90) == obs.MISSING
    assert obs.wind_text(0, 90) == "Calm"
    assert obs.wind_text(5.0, float("nan")) == "10 kt (5.0 m/s)"
    assert obs.wind_text(5.1, 110) == "10 kt (5.1 m/s) from ESE (110°)"


def test_small_formatters():
    assert obs.fmt(float("nan")) == obs.MISSING
    assert obs.fmt(69.6, " %", 0) == "70 %"
    assert obs.age_text(LATEST, NOW) == "55 min ago"
    assert obs.age_text(LATEST, NOW + pd.Timedelta(hours=2)) == "2 h 55 min ago"
    labels = obs.rain_labels(obs.rainfall(obs.tidy(FEATURES)))
    assert labels[pd.Timestamp("2026-09-17T12:00:00Z")] == "0.0 / 6 h, 27.8 / 24 h"
    assert labels[pd.Timestamp("2026-09-17T06:00:00Z")] == "0.0 / 6 h"


def test_hours_argument_is_coerced_to_a_choice():
    assert obs.ObservationsPlotAntiguaBarbuda(hours="72").hours_arg(48) == 72
    assert obs.ObservationsPlotAntiguaBarbuda(hours="soon").hours_arg(48) == 48
    assert obs.ObservationsPlotAntiguaBarbuda(hours=13).hours_arg(48) == 48
    assert obs.ObservationsTableAntiguaBarbuda().hours_arg(24) == 24


def test_card_reports_the_latest_hour(monkeypatch):
    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            return NOW

    monkeypatch.setattr(obs, "datetime", Clock)
    card = obs.CurrentConditionsCardAntiguaBarbuda().run()
    values = {item["label"]: item["value"] for item in card["data"]}
    assert values["V.C. Bird International Airport, observed"] == "17 Sep 16:00 UTC (55 min ago)"
    assert values["Temperature / dew point"] == "33.0 °C / 24.0 °C"
    assert values["Pressure (MSL)"] == "1015.0 hPa (+1.1 in 24 h)"
    assert values["Wind"] == "10 kt (5.0 m/s) from E (090°)"
    assert values["Rain, last 6-hour total"] == "0.0 mm to 12:00 UTC, 3.5 mm in the last 24 h of totals"
    assert values["Rain, last 24-hour total"] == "27.8 mm to 17 Sep 12:00 UTC"
    json.dumps(card)


def test_card_without_pressure_change_or_rain(monkeypatch):
    bare = hourly_report("2026-09-17T16:00:00Z", pressure_reduced_to_mean_sea_level=None)
    monkeypatch.setattr(obs, "_get_json", lambda url: {"features": bare})
    values = {item["label"]: item["value"] for item in obs.CurrentConditionsCardAntiguaBarbuda().run()["data"]}
    assert values["Pressure (MSL)"] == obs.MISSING
    assert values["Rain, last 6-hour total"] == obs.MISSING
    assert values["Rain, last 24-hour total"] == obs.MISSING


def test_card_plot_table_and_layer_when_the_feed_is_empty(monkeypatch):
    monkeypatch.setattr(obs, "_get_json", lambda url: {"features": []})
    assert obs.CurrentConditionsCardAntiguaBarbuda().run()["data"][0]["value"] == "No observations received"
    plot = obs.ObservationsPlotAntiguaBarbuda().run()
    assert plot["data"] == [] and plot["layout"]["annotations"][0]["text"] == "No observations received"
    assert obs.ObservationsTableAntiguaBarbuda().run()["data"] == []
    layer = obs.ObservationsStationLayerAntiguaBarbuda().run()
    props = layer["configuration"]["props"]["source"]["geojson"]["features"][0]["properties"]
    assert props == {"station": "V.C. Bird International Airport", "wmo_id": "78862"}


def test_plot_traces_and_axes():
    plot = obs.ObservationsPlotAntiguaBarbuda(hours=72).run()
    names = [trace["name"] for trace in plot["data"]]
    assert names == ["Temperature (°C)", "Dew point (°C)", "Rain (mm / 6 h)", "Pressure (hPa)"]
    rain = plot["data"][2]
    assert len(rain["x"]) == 8 and rain["x"][0] == "2026-09-15T15:00:00Z"  # bars centred on their 6 hours
    assert plot["data"][3]["yaxis"] == "y3" and plot["layout"]["yaxis3"]["overlaying"] == "y2"
    assert plot["layout"]["title"]["text"].endswith("last 72 hours")
    json.dumps(plot)


def test_table_rows_newest_first_with_rain_labels():
    table = obs.ObservationsTableAntiguaBarbuda(hours=48).run()
    rows = table["data"]
    assert len(rows) == 48 and rows[0]["Time (UTC)"] == "17 Sep 16:00"
    assert rows[0]["Rain (mm)"] == "" and rows[4]["Rain (mm)"] == "0.0 / 6 h, 27.8 / 24 h"
    assert rows[0]["Wind"] == "10 kt (5.0 m/s) from E (090°)"
    assert list(rows[0]) == ["Time (UTC)", "Temp (°C)", "Dew pt (°C)", "RH (%)", "Pressure (hPa)", "Wind", "Rain (mm)"]


def test_station_layer_carries_the_latest_observation():
    layer = obs.ObservationsStationLayerAntiguaBarbuda().run()
    props = layer["configuration"]["props"]["source"]["geojson"]["features"][0]["properties"]
    assert props["observed"] == "2026-09-17 16:00" and props["temperature"] == "33.0"
    assert props["rain_6h"] == "0.0 mm to 12:00 UTC" and props["rain_24h"] == "27.8 mm to 17 Sep 12:00 UTC"
    assert layer["attributeAliases"]["V.C. Bird Airport observations"]["rain_24h"] == "Rain, last 24-hour total"
    assert layer["legend"]["items"][0]["symbol"] == "circle"
    json.dumps(layer)
