"""Exposure by hazard level: people, buildings and roads in each level.

Each building and road already carries the four exceedance probabilities,
sampled as the maximum over its own footprint, so the same escalating gates
classify a feature directly.
"""

import numpy as np
import pandas as pd

from tgf_wmo_plugins.base import CountryPlugin, LiveData
from tgf_wmo_plugins.classification import LEVELS, ThresholdGates, classify_receptors
from tgf_wmo_plugins.countries import (
    ANTIGUA_BARBUDA,
    BARBADOS,
    COMOROS,
    GUATEMALA,
    HAITI,
)
from tgf_wmo_plugins.receptors import exposure_row


class BaseImpactSummary(ThresholdGates, LiveData, CountryPlugin):
    family = "impact_summary"
    strings_key = "hazard_summary"
    type = "table"

    def run(self):
        s = self.strings
        cycle = self.selected_cycle()
        df, rec, population = self.receptors(cycle)
        title = s["hazard_summary_title"] + self.title_suffix(cycle)

        if df is None:
            # Zeros rather than an error: nothing published is an answer too.
            title += ". " + s["msg_no_receptors"].format(
                site=self.scope_label(), cycle=cycle
            )
            cols = rec.columns
            df = pd.DataFrame(columns=[cols.type, *cols.measures, *rec.probabilities])
            hazard = np.zeros(0, dtype=np.uint8)
        else:
            hazard = classify_receptors(df, rec.probabilities, self.gates())

        def row(name, mask):
            return exposure_row(s, "col_level", name, df[mask], rec.columns, population)

        # Deepest level first. Normal carries no exposure and only pads the table.
        rows = [row(s["levels"][value], hazard == value) for value, _ in reversed(LEVELS)]
        rows.append(row(s["row_total_hazard"], hazard > 0))
        return {"title": title, "data": rows}


class ImpactSummaryGuatemala(BaseImpactSummary):
    country = GUATEMALA


class ImpactSummaryHaiti(BaseImpactSummary):
    country = HAITI


class ImpactSummaryAntiguaBarbuda(BaseImpactSummary):
    country = ANTIGUA_BARBUDA


class ImpactSummaryBarbados(BaseImpactSummary):
    country = BARBADOS


class ImpactSummaryComoros(BaseImpactSummary):
    country = COMOROS
