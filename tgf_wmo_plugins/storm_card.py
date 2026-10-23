"""Magnitude, flooded area and depth for one storm of a flood-map library."""

from tgf_wmo_plugins.base import CountryPlugin
from tgf_wmo_plugins.countries import BARBADOS, COMOROS, GUATEMALA
from tgf_wmo_plugins.storm_impact import StormIndex, storm_stats


class BaseStormCard(StormIndex, CountryPlugin):
    family = "storm_card"
    strings_key = "storm_card"
    type = "card"

    def run(self):
        s = self.strings
        stats = storm_stats(self.country.key, self.unit(), self.storm_index())

        if stats is None:
            last = self.country.storms.options[-1]["value"]
            return {"data": [{"color": "#888888", "label": s["out_of_range"],
                              "value": f"0-{last}", "icon": "BiError"}]}

        magnitude = {
            "color": "#4c78a8",
            "label": s["card_magnitude"],
            "value": f"{stats['magnitude_mm']:g} mm",
            "icon": "BiCloudRain",
        }
        # A storm that floods nowhere says so, rather than showing a row of
        # zeros that reads like a loading failure.
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


class StormCardGuatemala(BaseStormCard):
    country = GUATEMALA


class StormCardBarbados(BaseStormCard):
    country = BARBADOS


class StormCardComoros(BaseStormCard):
    country = COMOROS
