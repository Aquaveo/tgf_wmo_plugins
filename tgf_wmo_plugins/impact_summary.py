"""Exposure by hazard class: people, buildings and roads in each level.

Each building and road in the IBF geopackage already carries the four exceedance
probabilities, sampled as the maximum over its own footprint, so the same
escalating gates classify a feature directly.
"""

from functools import lru_cache
import tempfile
import urllib
from pathlib import Path

import pandas as pd
import pyogrio
from tethysapp.tethysdash.plugin_helpers import TethysDashPlugin

from tgf_wmo_plugins.classification import LEVELS, ThresholdGates
from tgf_wmo_plugins.common import (
    GUATEMALA_FEATURES_CSV_URL,
    HAITI_FEATURES_CSV_URL,
    PROB_FIELDS,
    TOTAL_POPULATION,
    HAITI_LAYERS,
)
from tgf_wmo_plugins.strings import STRINGS, threshold_args


@lru_cache(maxsize=4)
def _load(url, country):
    if country == "guatemala":
        return pd.read_csv(url)
    elif country == "haiti":
        path = Path(tempfile.gettempdir()) / url.rsplit("/", 1)[-1]
        if not path.exists():
            urllib.request.urlretrieve(url, path)

        parts = []
        for type_, (layer, renames) in HAITI_LAYERS.items():
            # Fields already carrying their final name, plus the ones to rename.
            columns = [f for f in PROB_FIELDS["haiti"] if f not in renames.values()]
            part = pyogrio.read_dataframe(
                path,
                layer=layer,
                columns=columns + list(renames),
                read_geometry=False,
                use_arrow=True,
            )
            part = part.rename(columns=renames)
            part["type"] = type_
            parts.append(part)
        return pd.concat(parts, ignore_index=True)


class BaseImpactSummary(ThresholdGates, TethysDashPlugin):
    """Language-independent computation; subclasses only choose the strings."""

    LANG = None
    type = "table"

    def run(self):
        country = self.country
        s = STRINGS[self.LANG]
        gates = self.gates()

        if country == "guatemala":
            df = _load(GUATEMALA_FEATURES_CSV_URL, self.country).copy()
        elif country == "haiti":
            df = _load(HAITI_FEATURES_CSV_URL, self.country).copy()

            for col in ["population", "surface_m2", "longueur_m"]:
                df[col] = df[col].fillna(0.0) if col in df else 0.0
                
        # Escalating assignment: the deepest threshold a feature clears wins,
        # exactly as clasificar_peligro does for pixels.
        df["danger"] = 0
        for field, (value, _color) in zip(PROB_FIELDS[country], LEVELS):
            df.loc[df[field] >= gates[value], "danger"] = value

        # Deepest level first. Normal is left out: it is everything the gates did
        # not catch, so it carries no exposure and only pads the table.
        rows = [
            self._row(s, s["levels"][value], df[df.danger == value])
            for value, _color in reversed(LEVELS)
        ]
        rows.append(self._row(s, s["row_total_hazard"], df[df.danger > 0]))
        return {"title": s["hazard_summary_title"], "data": rows}

    def _row(self, s, name, group):
        if self.country == "guatemala":
            buildings = group[group.tipo == "edificio"]

            return {
                s["col_level"]: name,
                s["col_buildings"]: f"{len(buildings):,}",
                s["col_population"]: f"{group.poblacion.sum():,.0f}",
                s["col_area"]: f"{group.area_m2.sum():,.0f}",
                s["col_roads_km"]: f"{group.longitud_m.sum() / 1000:,.1f}",
                s["col_pop_share"]: (
                    f"{100 * group.poblacion.sum() / TOTAL_POPULATION['guatemala']:.2f}%"
                ),
            }
        elif self.country == "haiti":
            buildings = group[group.type == "batiment"]
            return {
                s["col_level"]: name,
                s["col_buildings"]: f"{len(buildings):,}",
                s["col_population"]: f"{group.population.sum():,.0f}",
                s["col_area"]: f"{group.surface_m2.sum():,.0f}",
                s["col_roads_km"]: f"{group.longueur_m.sum() / 1000:,.1f}",
                s["col_pop_share"]: (
                    f"{100 * group.population.sum() / TOTAL_POPULATION['haiti']:.2f}%"
                ),
            }


class ImpactSummaryBarbados(BaseImpactSummary):
    LANG = "en"
    country = "barbados"
    args = threshold_args(LANG)
    name = "UFFIS_impact_summary_barbados"
    label = f"{STRINGS['en']['hazard_summary_label']} (Barbados)"
    group = STRINGS["en"]["group"]
    tags = ["flood", "impact", "IBF", "exposure", "table", "english"]
    description = STRINGS["en"]["hazard_summary_desc"]


class ImpactSummaryGuatemala(BaseImpactSummary):
    LANG = "es"
    country = "guatemala"
    args = threshold_args(LANG)
    name = "UFFIS_impact_summary_guatemala"
    label = f"{STRINGS['es']['hazard_summary_label']} (Guatemala)"
    group = STRINGS["es"]["group"]
    tags = ["inundación", "impacto", "IBF", "exposición", "tabla", "español"]
    description = STRINGS["es"]["hazard_summary_desc"]


class ImpactSummaryHaiti(BaseImpactSummary):
    LANG = "fr"
    country = "haiti"
    args = threshold_args(LANG)
    name = "UFFIS_impact_summary_haiti"
    label = f"{STRINGS[LANG]['hazard_summary_label']} (Haiti)"
    group = STRINGS[LANG]["group"]
    tags = ["inondation", "impact", "IBF", "exposition", "tableau", "français"]
    description = STRINGS[LANG]["hazard_summary_desc"]
