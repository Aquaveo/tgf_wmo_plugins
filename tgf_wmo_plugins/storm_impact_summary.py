"""People, buildings and roads by flood depth for one storm of the ensemble."""

from tethysapp.tethysdash.plugin_helpers import TethysDashPlugin

from tgf_wmo_plugins.common import (
    FIRST_WET_STORM,
    STORM_OPTIONS,
    TOTAL_POPULATION,
    coerce_index,
)
from tgf_wmo_plugins.storm_impact import DEPTH_BANDS, banded_features
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
