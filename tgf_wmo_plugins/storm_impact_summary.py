"""People, buildings and roads by flood depth for one storm of a library."""

from tgf_wmo_plugins.base import CountryPlugin
from tgf_wmo_plugins.countries import BARBADOS, COMOROS, GUATEMALA
from tgf_wmo_plugins.receptors import exposure_row
from tgf_wmo_plugins.storm_impact import DEPTH_BANDS, StormIndex, banded_features


class BaseStormImpactSummary(StormIndex, CountryPlugin):
    family = "storm_impact_summary"
    strings_key = "storm_summary"
    type = "table"

    def run(self):
        s = self.strings
        unit, index = self.unit(), self.storm_index()
        gdf = banded_features(self.country.key, unit, index)
        columns = self.country.receptors.columns
        population = self.country.unit_population(unit)

        def row(name, group):
            return exposure_row(s, "col_depth", name, group, columns, population)

        # Deepest band first, so the worst case is the first thing read.
        rows = [
            row(s["bands"][value], gdf[gdf["band"] == value])
            for value, _color, _floor in reversed(DEPTH_BANDS)
        ]
        rows.append(row(s["row_total_flooded"], gdf))
        return {"title": s["storm_summary_title"].format(index=index), "data": rows}


class StormImpactSummaryGuatemala(BaseStormImpactSummary):
    country = GUATEMALA


class StormImpactSummaryBarbados(BaseStormImpactSummary):
    country = BARBADOS


class StormImpactSummaryComoros(BaseStormImpactSummary):
    country = COMOROS
