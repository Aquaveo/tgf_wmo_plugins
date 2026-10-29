"""People, buildings and roads by flood depth, as a table.

For a country with live TITO cycles, by the depth each feature reaches with at
least the chosen probability; Barbados, which TITO does not run, by its depth in
one storm of the training library.
"""

import numpy as np
import pandas as pd

from tgf_wmo_plugins.base import CountryPlugin
from tgf_wmo_plugins.countries import (
    ANTIGUA_BARBUDA,
    BARBADOS,
    COMOROS,
    GUATEMALA,
    HAITI,
)
from tgf_wmo_plugins.likely_depth import LIKELY_BANDS, LikelyDepth, likely_band
from tgf_wmo_plugins.receptors import exposure_row
from tgf_wmo_plugins.storm_impact import DEPTH_BANDS, StormIndex, banded_features
from tgf_wmo_plugins.strings import STRINGS


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


class LiveStormImpactSummary(LikelyDepth, CountryPlugin):
    family = "storm_impact_summary"
    strings_key = "storm_summary"
    type = "table"

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if "country" in cls.__dict__:
            cls.description = STRINGS[cls.country.lang]["likely_summary_desc"]

    def run(self):
        s = self.strings
        cycle, p = self.selected_cycle(), self.likelihood()
        df, rec, population = self.receptors(cycle)
        title = s["likely_summary_title"].format(p=p) + self.title_suffix(cycle)

        if df is None:
            title += ". " + s["msg_no_receptors"].format(site=self.scope_label(), cycle=cycle)
            cols = rec.columns
            df = pd.DataFrame(columns=[cols.type, *cols.measures, *rec.probabilities])
            band = np.zeros(0, dtype=np.uint8)
        else:
            band = likely_band(df, rec.probabilities, p)

        def row(name, mask):
            return exposure_row(s, "col_depth", name, df[mask], rec.columns, population)

        # Deepest band first, so the worst case is the first thing read.
        rows = [row(s["likely_bands"][v], band == v) for v, _ in reversed(LIKELY_BANDS)]
        rows.append(row(s["row_total_flooded"], band > 0))
        return {"title": title, "data": rows}


class StormImpactSummaryGuatemala(LiveStormImpactSummary):
    country = GUATEMALA


class StormImpactSummaryHaiti(LiveStormImpactSummary):
    country = HAITI


class StormImpactSummaryAntiguaBarbuda(LiveStormImpactSummary):
    country = ANTIGUA_BARBUDA


class StormImpactSummaryBarbados(BaseStormImpactSummary):
    country = BARBADOS


class StormImpactSummaryComoros(LiveStormImpactSummary):
    country = COMOROS
