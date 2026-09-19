"""People, buildings and roads by flood depth for one storm of the ensemble."""

from tethysapp.tethysdash.plugin_helpers import TethysDashPlugin

from tgf_wmo_plugins.common import (
    FIRST_WET_STORM,
    STORM_OPTIONS,
    TOTAL_POPULATION,
    coerce_index,
)
from tgf_wmo_plugins.common import (
    COMOROS_STORM_OPTIONS,
    COMOROS_UNIT_OPTIONS,
    COMOROS_UNITS,
)
from tgf_wmo_plugins.storm_impact import (
    COMOROS_BUILDING,
    COMOROS_DEFAULT_STORM,
    DEPTH_BANDS,
    banded_features,
    comoros_banded_features,
    comoros_population,
)
from tgf_wmo_plugins.strings import STRINGS


class BaseStormImpactSummary(TethysDashPlugin):
    LANG = None
    type = "table"
    args = {"index": STORM_OPTIONS}

    def run(self):
        s = STRINGS[self.LANG]
        index = coerce_index(self.get_arg("index", FIRST_WET_STORM), FIRST_WET_STORM)
        gdf = banded_features(index)

        # Deepest band first, so the worst case is the first thing read.
        rows = [
            self._row(s, s["bands"][value], gdf[gdf.banda == value])
            for value, _color, _floor in reversed(DEPTH_BANDS)
        ]
        rows.append(self._row(s, s["row_total_flooded"], gdf))
        return {
            "title": s["storm_summary_title"].format(index=index),
            "data": rows,
        }

    @staticmethod
    def _row(s, name, group):
        buildings = group[group.tipo == "edificio"]
        return {
            s["col_depth"]: name,
            s["col_buildings"]: f"{len(buildings):,}",
            s["col_population"]: f"{group.poblacion.sum():,.0f}",
            s["col_area"]: f"{group.area_m2.sum():,.0f}",
            s["col_roads_km"]: f"{group.longitud_m.sum() / 1000:,.1f}",
            s["col_pop_share"]: (
                f"{100 * group.poblacion.sum() / TOTAL_POPULATION['guatemala']:.2f}%"
            ),
        }


class StormImpactSummaryEN(BaseStormImpactSummary):
    LANG = "en"
    name = "wmo_storm_impact_summary_en"
    label = f"{STRINGS['en']['storm_summary_label']} ({STRINGS['en']['language']})"
    group = STRINGS["en"]["group"]
    tags = ["flood", "impact", "zarr", "storm", "table", "english"]
    description = STRINGS["en"]["storm_summary_desc"]


class StormImpactSummaryES(BaseStormImpactSummary):
    LANG = "es"
    name = "wmo_storm_impact_summary_es"
    label = f"{STRINGS['es']['storm_summary_label']} ({STRINGS['es']['language']})"
    group = STRINGS["es"]["group"]
    tags = ["inundación", "impacto", "zarr", "tormenta", "tabla", "español"]
    description = STRINGS["es"]["storm_summary_desc"]


class BaseStormImpactSummaryComoros(TethysDashPlugin):
    """Exposure by depth band for one storm of one commune's library."""

    LANG = None
    type = "table"
    args = {"commune": COMOROS_UNIT_OPTIONS, "index": COMOROS_STORM_OPTIONS}

    def run(self):
        s = STRINGS[self.LANG]
        unit = self.get_arg("commune", COMOROS_UNITS[0][0])
        index = coerce_index(
            self.get_arg("index", COMOROS_DEFAULT_STORM), COMOROS_DEFAULT_STORM
        )
        gdf = comoros_banded_features(unit, index)
        total = comoros_population(unit)

        rows = [
            self._row(s, s["bands"][value], gdf[gdf.banda == value], total)
            for value, _color, _floor in reversed(DEPTH_BANDS)
        ]
        rows.append(self._row(s, s["row_total_flooded"], gdf, total))
        return {"title": s["storm_summary_title"].format(index=index), "data": rows}

    @staticmethod
    def _row(s, name, group, total_population):
        # group["type"], never group.type: on a GeoDataFrame the attribute is the
        # geometry type, so the comparison would match nothing and every building
        # count would read 0.
        buildings = group[group["type"] == COMOROS_BUILDING]
        population = group.population_per_building.sum()
        return {
            s["col_depth"]: name,
            s["col_buildings"]: f"{len(buildings):,}",
            s["col_population"]: f"{population:,.0f}",
            s["col_area"]: f"{group.building_area_m2.sum():,.0f}",
            s["col_roads_km"]: f"{group.road_length_m.sum() / 1000:,.1f}",
            s["col_pop_share"]: f"{100 * population / total_population:.2f}%",
        }


class StormImpactSummaryComoros(BaseStormImpactSummaryComoros):
    LANG = "fr"
    name = "uffis_storm_impact_summary_comoros"
    label = f"{STRINGS['fr']['storm_summary_label']} (Comores)"
    group = STRINGS["fr"]["group"]
    tags = ["inondation", "impact", "zarr", "tempête", "tableau", "français"]
    description = STRINGS["fr"]["storm_summary_desc"]
