"""People, buildings and roads by flood depth for one storm of the ensemble."""

from tethysapp.tethysdash.plugin_helpers import TethysDashPlugin

from tgf_wmo_plugins.common import (
    FIRST_WET_STORM,
    STORM_OPTIONS,
    TOTAL_POPULATION,
    coerce_index,
)
from tgf_wmo_plugins.common import (
    BARBADOS_PARISH_OPTIONS,
    COMOROS_UNIT_OPTIONS,
    COMOROS_UNITS,
    UNIT_STORM_OPTIONS,
)
from tgf_wmo_plugins.storm_impact import (
    DEPTH_BANDS,
    UNIT_BUILDING,
    UNIT_DEFAULT_STORM,
    banded_features,
    unit_banded_features,
    unit_population,
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


class StormImpactSummaryGuatemala(BaseStormImpactSummary):
    LANG = "es"
    name = "uffis_storm_impact_summary_guatemala"
    label = f"{STRINGS['es']['storm_summary_label']} (Guatemala)"
    group = STRINGS["es"]["group"]
    tags = ["inundación", "impacto", "zarr", "tormenta", "tabla", "español"]
    description = STRINGS["es"]["storm_summary_desc"]


class BaseStormImpactSummaryUnit(TethysDashPlugin):
    """Exposure by depth band for one storm of one unit's library."""

    LANG = None
    country = None
    unit_arg = "unit"
    default_unit = None
    type = "table"

    def run(self):
        s = STRINGS[self.LANG]
        unit = self.get_arg(self.unit_arg, self.default_unit)
        index = coerce_index(
            self.get_arg("index", UNIT_DEFAULT_STORM), UNIT_DEFAULT_STORM
        )
        gdf = unit_banded_features(self.country, unit, index)
        total = unit_population(self.country, unit)

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
        buildings = group[group["type"] == UNIT_BUILDING]
        population = group.population_per_building.sum()
        return {
            s["col_depth"]: name,
            s["col_buildings"]: f"{len(buildings):,}",
            s["col_population"]: f"{population:,.0f}",
            s["col_area"]: f"{group.building_area_m2.sum():,.0f}",
            s["col_roads_km"]: f"{group.road_length_m.sum() / 1000:,.1f}",
            s["col_pop_share"]: f"{100 * population / total_population:.2f}%",
        }


class StormImpactSummaryComoros(BaseStormImpactSummaryUnit):
    LANG = "fr"
    country = "comoros"
    unit_arg = "commune"
    default_unit = COMOROS_UNITS[0][0]
    args = {"commune": COMOROS_UNIT_OPTIONS, "index": UNIT_STORM_OPTIONS}
    name = "uffis_storm_impact_summary_comoros"
    label = f"{STRINGS['fr']['storm_summary_label']} (Comores)"
    group = STRINGS["fr"]["group"]
    tags = ["inondation", "impact", "zarr", "tempête", "tableau", "français"]
    description = STRINGS["fr"]["storm_summary_desc"]


class StormImpactSummaryBarbados(BaseStormImpactSummaryUnit):
    LANG = "en"
    country = "barbados"
    unit_arg = "parish"
    default_unit = "BB08_SaintMichael"
    args = {"parish": BARBADOS_PARISH_OPTIONS, "index": UNIT_STORM_OPTIONS}
    name = "uffis_storm_impact_summary_barbados"
    label = f"{STRINGS['en']['storm_summary_label']} (Barbados)"
    group = STRINGS["en"]["group"]
    tags = ["flood", "impact", "zarr", "storm", "table", "english"]
    description = STRINGS["en"]["storm_summary_desc"]
