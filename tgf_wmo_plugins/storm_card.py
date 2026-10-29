"""A storm's headline figures, as a card.

For a country with live TITO cycles the card summarises the cycle's forecast;
Barbados, which TITO does not run, keeps one storm of its training library.
"""

from tgf_wmo_plugins.base import CountryPlugin
from tgf_wmo_plugins.countries import (
    ANTIGUA_BARBUDA,
    BARBADOS,
    COMOROS,
    GUATEMALA,
    HAITI,
)
from tgf_wmo_plugins.hazard_layer import _read_raster
from tgf_wmo_plugins.likely_depth import LikelyDepth, cell_area_km2
from tgf_wmo_plugins.storm_impact import StormIndex, storm_stats
from tgf_wmo_plugins.strings import STRINGS
from tgf_wmo_plugins.tito import cycle_files, file_url


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


class LiveStormCard(LikelyDepth, CountryPlugin):
    family = "storm_card"
    strings_key = "storm_card"
    type = "card"

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if "country" in cls.__dict__:
            cls.description = STRINGS[cls.country.lang]["likely_card_desc"]

    def run(self):
        s, live = self.strings, self.country.live
        cycle, p = self.selected_cycle(), self.likelihood()

        trigger = self.trigger(cycle)
        if not (trigger and trigger.get("triggered")):
            # A quiet site has no forecast products, so this is all there is to say.
            return {"data": [{"color": "#888888", "label": s["card_status"],
                              "value": s["status_quiet"], "icon": "BiCheckCircle"}]}
        data = []

        rain = self.rainfall(cycle)
        if rain is not None:
            data.append({"color": "#4c78a8", "label": s["card_rain"],
                         "value": f"{rain[0]:.0f} / {rain[1]:.0f} mm", "icon": "BiCloudRain"})

        shallowest = live.prob_paths(self.scope(), live.variants[0], cycle)[0]
        if shallowest in cycle_files(live.slug, cycle):
            prob, transform, crs = _read_raster(file_url(live.slug, cycle, shallowest))
            km2 = int((prob.filled(0) >= p).sum()) * cell_area_km2(transform, crs, prob.shape[0])
            data.append({"color": "#e45756", "label": s["card_likely_area"].format(p=p),
                         "value": f"{km2:.2f} km²", "icon": "BiWater"})

        df, rec, _population = self.receptors(cycle)
        if df is not None:
            cols, p30 = rec.columns, rec.probabilities[1]
            # Expected counts: each feature contributes its probability.
            people = (df[cols.population] * df[p30]).sum()
            buildings = df.loc[df[cols.type] == cols.building, p30].sum()
            data.append({"color": "#b279a2", "label": s["card_expected_people"],
                         "value": f"{people:,.0f}", "icon": "BiGroup"})
            data.append({"color": "#54a24b", "label": s["card_expected_buildings"],
                         "value": f"{buildings:,.0f}", "icon": "BiBuildings"})
        if not data:
            data.append({"color": "#e45756", "label": s["card_status"],
                         "value": s["status_triggered"], "icon": "BiError"})
        return {"data": data}


class StormCardGuatemala(LiveStormCard):
    country = GUATEMALA


class StormCardHaiti(LiveStormCard):
    country = HAITI


class StormCardAntiguaBarbuda(LiveStormCard):
    country = ANTIGUA_BARBUDA


class StormCardBarbados(BaseStormCard):
    country = BARBADOS


class StormCardComoros(LiveStormCard):
    country = COMOROS
