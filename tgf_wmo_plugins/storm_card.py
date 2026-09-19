"""Magnitude, flooded area and depth for one storm of the ensemble."""

from tethysapp.tethysdash.plugin_helpers import TethysDashPlugin

from tgf_wmo_plugins.common import (
    COMOROS_STORM_OPTIONS,
    COMOROS_UNIT_OPTIONS,
    COMOROS_UNITS,
    DEFAULT_STORE,
    FIRST_WET_STORM,
    STORM_OPTIONS,
    coerce_index,
    load_stats,
    storm_row,
)
from tgf_wmo_plugins.storm_impact import COMOROS_DEFAULT_STORM, comoros_storm_stats
from tgf_wmo_plugins.strings import STRINGS


class BaseStormCard(TethysDashPlugin):
    LANG = None
    type = "card"
    args = {"index": STORM_OPTIONS}

    def run(self):
        s = STRINGS[self.LANG]
        index = coerce_index(self.get_arg("index", FIRST_WET_STORM), FIRST_WET_STORM)
        stats = load_stats(DEFAULT_STORE)
        row = storm_row(stats, index)

        if row is None:
            return {
                "data": [
                    {
                        "color": "#888888",
                        "label": s["out_of_range"],
                        "value": f"0-{int(stats.storm_index.max())}",
                        "icon": "BiError",
                    }
                ]
            }

        magnitude = {
            "color": "#4c78a8",
            "label": s["card_magnitude"],
            "value": f"{row.magnitude_mm:g} mm",
            "icon": "BiCloudRain",
        }

        # Two storms in this ensemble flood nowhere at all, so their chunks were
        # never written. Say so rather than showing a row of zeros that reads
        # like a loading failure.
        if row.flooded_px == 0:
            return {
                "data": [
                    magnitude,
                    {
                        "color": "#888888",
                        "label": s["card_flooding"],
                        "value": s["card_no_flooding"],
                        "icon": "BiCheckCircle",
                    },
                ]
            }

        return {
            "data": [
                magnitude,
                {
                    "color": "#e45756",
                    "label": s["card_flooded_area"],
                    "value": f"{row.area_km2:.2f} km² ({row.pct_domain:.1f}%)",
                    "icon": "BiWater",
                },
                {
                    "color": "#54a24b",
                    "label": s["card_max_depth"],
                    "value": f"{row.max_depth_m:.2f} m",
                    "icon": "BiRuler",
                },
                {
                    "color": "#b279a2",
                    "label": s["card_mean_depth"],
                    "value": f"{row.mean_wet_depth_m:.2f} m",
                    "icon": "BiStats",
                },
            ]
        }


class StormCardEN(BaseStormCard):
    LANG = "en"
    name = "wmo_storm_card_en"
    label = f"{STRINGS['en']['storm_card_label']} ({STRINGS['en']['language']})"
    group = STRINGS["en"]["group"]
    tags = ["flood", "zarr", "storm", "card", "english"]
    description = STRINGS["en"]["storm_card_desc"]


class StormCardES(BaseStormCard):
    LANG = "es"
    name = "wmo_storm_card_es"
    label = f"{STRINGS['es']['storm_card_label']} ({STRINGS['es']['language']})"
    group = STRINGS["es"]["group"]
    tags = ["inundación", "zarr", "tormenta", "tarjeta", "español"]
    description = STRINGS["es"]["storm_card_desc"]


class BaseStormCardComoros(TethysDashPlugin):
    """The same four figures as BaseStormCard, for one commune's library.

    Kept separate rather than folded into that class because the two read their
    numbers from different places: Guatemala has one national store with an
    `ensemble_stats.csv` precomputed beside it, while a Comoros commune store
    ships no summary, so the figures are computed from the storm's own chunk.
    """

    LANG = None
    type = "card"
    args = {"commune": COMOROS_UNIT_OPTIONS, "index": COMOROS_STORM_OPTIONS}

    def run(self):
        s = STRINGS[self.LANG]
        unit = self.get_arg("commune", COMOROS_UNITS[0][0])
        index = coerce_index(self.get_arg("index", COMOROS_DEFAULT_STORM),
                             COMOROS_DEFAULT_STORM)
        stats = comoros_storm_stats(unit, index)

        if stats is None:
            return {"data": [{"color": "#888888", "label": s["out_of_range"],
                              "value": "0-199", "icon": "BiError"}]}

        magnitude = {
            "color": "#4c78a8",
            "label": s["card_magnitude"],
            "value": f"{stats['magnitude_mm']:g} mm",
            "icon": "BiCloudRain",
        }
        if stats["flooded_cells"] == 0:
            return {"data": [magnitude,
                             {"color": "#888888", "label": s["card_flooding"],
                              "value": s["card_no_flooding"], "icon": "BiCheckCircle"}]}

        return {
            "data": [
                magnitude,
                {"color": "#e45756", "label": s["card_flooded_area"],
                 "value": f"{stats['area_km2']:.2f} km² ({stats['pct_domain']:.1f}%)",
                 "icon": "BiWater"},
                {"color": "#54a24b", "label": s["card_max_depth"],
                 "value": f"{stats['max_depth_m']:.2f} m", "icon": "BiRuler"},
                {"color": "#b279a2", "label": s["card_mean_depth"],
                 "value": f"{stats['mean_wet_depth_m']:.2f} m", "icon": "BiStats"},
            ]
        }


class StormCardComoros(BaseStormCardComoros):
    LANG = "fr"
    name = "uffis_storm_card_comoros"
    label = f"{STRINGS['fr']['storm_card_label']} (Comores)"
    group = STRINGS["fr"]["group"]
    tags = ["inondation", "zarr", "tempête", "carte", "français"]
    description = STRINGS["fr"]["storm_card_desc"]
