"""Exposure by hazard class: people, buildings and roads in each level.

Each building and road in the IBF geopackage already carries the four exceedance
probabilities, sampled as the maximum over its own footprint, so the same
escalating gates classify a feature directly.
"""

from functools import lru_cache

import pandas as pd
import pyogrio
from tethysapp.tethysdash.plugin_helpers import TethysDashPlugin

from tgf_wmo_plugins.classification import LEVELS, ComorosUnit, ThresholdGates
from tgf_wmo_plugins.common import (
    cached_download,
    GUATEMALA_FEATURES_CSV_URL,
    HAITI_FEATURES_CSV_URL,
    ANTIGUA_BARBUDA_FEATURES_CSV_URL,
    COMOROS_FEATURES_URL,
    COMOROS_UNIT_OPTIONS,
    COMOROS_UNIT_POPULATION,
    GPKG_LAYERS,
    PROB_FIELDS,
    TOTAL_POPULATION,
    comoros_receptors_url,
    gpkg_where,
    scale_probabilities,
)
from tgf_wmo_plugins.strings import STRINGS, threshold_args


@lru_cache(maxsize=8)
def _load(url, country, unit=None):
    if country == "guatemala":
        return pd.read_csv(url)

    path = cached_download(url)
    parts = []
    for type_, (layer, renames) in GPKG_LAYERS[country].items():
        part = pyogrio.read_dataframe(
            path,
            layer=layer,
            # Only Comoros sets one: its geopackage covers a whole island, so the
            # commune is selected in the driver rather than afterwards.
            where=gpkg_where(country, unit),
            read_geometry=False,
            use_arrow=True,
        )
        part = part.rename(columns=renames)
        part["type"] = type_
        parts.append(part)
    # Comoros stores its probabilities as percent; the gates are fractions.
    return scale_probabilities(pd.concat(parts, ignore_index=True), country)


class BaseImpactSummary(ThresholdGates, TethysDashPlugin):
    """Language-independent computation; subclasses only choose the strings."""

    LANG = None
    type = "table"

    def run(self):
        country = self.country
        s = STRINGS[self.LANG]
        gates = self.gates()

        if country == "guatemala":
            csv_url = GUATEMALA_FEATURES_CSV_URL
        elif country == "haiti":
            csv_url = HAITI_FEATURES_CSV_URL
        elif country == "antigua_barbuda":
            csv_url = ANTIGUA_BARBUDA_FEATURES_CSV_URL
        elif country == "comoros":
            csv_url = COMOROS_FEATURES_URL

        unit = self.unit() if isinstance(self, ComorosUnit) else None
        if unit:
            # The commune decides both which island file to read and which rows
            # to keep out of it.
            csv_url = comoros_receptors_url(unit)
        df = _load(csv_url, self.country, unit).copy()

        if country == "haiti":
            for col in ["population", "surface_m2", "longueur_m"]:
                df[col] = df[col].fillna(0.0) if col in df else 0.0

        # Escalating assignment: the deepest threshold a feature clears wins,
        # exactly as classify_hazard does for pixels.
        df["hazard"] = 0
        for field, (value, _color) in zip(PROB_FIELDS[country], LEVELS):
            df.loc[df[field] >= gates[value], "hazard"] = value

        # Deepest level first. Normal is left out: it is everything the gates did
        # not catch, so it carries no exposure and only pads the table.
        rows = [
            self._row(s, s["levels"][value], df[df.hazard == value])
            for value, _color in reversed(LEVELS)
        ]
        rows.append(self._row(s, s["row_total_hazard"], df[df.hazard > 0]))
        return {"title": s["hazard_summary_title"], "data": rows}

    def _population(self):
        """The denominator for the exposure share.

        Comoros reports against the chosen commune; every other country has a
        single domain and so a single constant.
        """
        if isinstance(self, ComorosUnit):
            return COMOROS_UNIT_POPULATION[self.unit()]
        return TOTAL_POPULATION[self.country]

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
        elif self.country in ("antigua_barbuda", "comoros"):
            # Both geopackages spell the measures the same way, so one branch
            # serves them; only the denominator differs.
            buildings = group[group.type == "building"]
            return {
                s["col_level"]: name,
                s["col_buildings"]: f"{len(buildings):,}",
                s["col_population"]: f"{group.population_per_building.sum():,.0f}",
                s["col_area"]: f"{group.building_area_m2.sum():,.0f}",
                s["col_roads_km"]: f"{group.road_length_m.sum() / 1000:,.1f}",
                s["col_pop_share"]: (
                    f"{100 * group.population_per_building.sum() / self._population():.2f}%"
                ),
            }


class ImpactSummaryBarbados(BaseImpactSummary):
    LANG = "en"
    country = "barbados"
    args = threshold_args(LANG)
    name = "uffis_impact_summary_barbados"
    label = f"{STRINGS['en']['hazard_summary_label']} (Barbados)"
    group = STRINGS["en"]["group"]
    tags = ["flood", "impact", "IBF", "exposure", "table", "english"]
    description = STRINGS["en"]["hazard_summary_desc"]


class ImpactSummaryGuatemala(BaseImpactSummary):
    LANG = "es"
    country = "guatemala"
    args = threshold_args(LANG)
    name = "uffis_impact_summary_guatemala"
    label = f"{STRINGS['es']['hazard_summary_label']} (Guatemala)"
    group = STRINGS["es"]["group"]
    tags = ["inundación", "impacto", "IBF", "exposición", "tabla", "español"]
    description = STRINGS["es"]["hazard_summary_desc"]


class ImpactSummaryHaiti(BaseImpactSummary):
    LANG = "fr"
    country = "haiti"
    args = threshold_args(LANG)
    name = "uffis_impact_summary_haiti"
    label = f"{STRINGS[LANG]['hazard_summary_label']} (Haiti)"
    group = STRINGS[LANG]["group"]
    tags = ["inondation", "impact", "IBF", "exposition", "tableau", "français"]
    description = STRINGS[LANG]["hazard_summary_desc"]


class ImpactSummaryAntiguaBarbuda(BaseImpactSummary):
    LANG = "en"
    country = "antigua_barbuda"
    args = threshold_args(LANG)
    name = "uffis_impact_summary_antigua_barbuda"
    label = f"{STRINGS[LANG]['hazard_summary_label']} (Antigua and Barbuda)"
    group = STRINGS[LANG]["group"]
    tags = ["flood", "impact", "IBF", "exposure", "table", "english"]
    description = STRINGS[LANG]["hazard_summary_desc"]


class ImpactSummaryComoros(ComorosUnit, BaseImpactSummary):
    LANG = "fr"
    country = "comoros"
    # The four gates plus the commune, which also sets the population the share
    # is measured against.
    args = {**threshold_args(LANG), "commune": COMOROS_UNIT_OPTIONS}
    name = "uffis_impact_summary_comoros"
    label = f"{STRINGS[LANG]['hazard_summary_label']} (Comores)"
    group = STRINGS[LANG]["group"]
    tags = ["inondation", "impact", "IBF", "exposition", "tableau", "français"]
    description = STRINGS[LANG]["hazard_summary_desc"]
