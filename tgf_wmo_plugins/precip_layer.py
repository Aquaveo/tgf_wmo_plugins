"""TITO's ensemble summary rasters -- rainfall, soil saturation and unit
streamflow -- as dynamic map layers.

Each sits at <grid>/summary/<product>_<period>_<statistic>.<cycle>.tif; see
tito.py for how cycles are published and how long they are kept. The colour
classes are the tito.uffis.org viewer's.
"""

from dataclasses import dataclass

from tethysapp.tethysdash.plugin_helpers import LayerConfigurationBuilder, geotiff_source

from tgf_wmo_plugins.base import CountryPlugin, LiveData
from tgf_wmo_plugins.countries import ANTIGUA_BARBUDA, COMOROS, GUATEMALA, HAITI
from tgf_wmo_plugins.strings import LIVE_ARGS, STRINGS
from tgf_wmo_plugins.tito import cycle_files, cycle_label, file_url, stamp

STATISTICS = ["median", "min", "max"]
PERIODS = ["forecast", "nowcast"]


@dataclass(frozen=True)
class Legend:
    """Class i covers breaks[i] to breaks[i + 1]; the last runs open-ended, and
    values under breaks[0] -- the -9999 nodata included -- are not drawn."""

    breaks: tuple
    colors: tuple
    open_ended: bool  # label the last class "<break> or more"


RAINFALL = Legend(
    breaks=(1, 5, 10, 25, 50, 75, 100, 150, 250),
    colors=("#d9f0a3", "#addd8e", "#41ab5d", "#ffffb2", "#fdae61",
            "#f46d43", "#d73027", "#a50026", "#6a3d9a"),
    open_ended=True,
)
SOIL_SATURATION = Legend(
    breaks=(10, 30, 50, 70, 85, 95, 100),
    colors=("#f6e8c3", "#dfc27d", "#80cdc1", "#35978f", "#01665e", "#003c30"),
    open_ended=False,
)
UNIT_STREAMFLOW = Legend(
    breaks=(0.1, 1, 2, 4, 6, 10, 20),
    colors=("#bdbdbd", "#d9ef8b", "#fdae61", "#d73027", "#c51b7d", "#2c7bb6", "#08306b"),
    open_ended=True,
)


def _choice(value, values):
    """`value` when it is one of `values`, else the first.

    An unset arg arrives as None, and an unbound variable as its literal
    "${...}" text, so neither can be trusted to be a valid choice.
    """
    return value if value in values else values[0]


class BaseSummaryLayer(LiveData, CountryPlugin):
    """Set `product`, `legend`, `family`, `strings_key` and `legend_key`; a
    country subclass then sets only `country`."""

    product = None
    legend = None
    legend_key = None
    type = "map_layer"
    dynamic_map_layer = True
    dynamic_map_layer_source = "GeoTIFF"

    @classmethod
    def has_training(cls, country):
        return False

    @classmethod
    def country_args(cls, country):
        s, names = STRINGS[country.lang], LIVE_ARGS[country.lang]
        # `cycle` takes the stamp an Available Cycles input carries; it is not a
        # "date" arg, which would parse the stamp as a datetime.
        return {
            names["cycle"]: cls.live_args(country)[names["cycle"]],
            names["grid"]: [
                {"value": grid, "label": f"{res} ({s['rain_grid_kinds'][kind]})" if kind else res}
                for grid, res, kind in country.live.rain_grids
            ],
            names["statistic"]: [{"value": v, "label": s["rain_statistics"][v]} for v in STATISTICS],
            names["period"]: [{"value": v, "label": s["rain_periods"][v]} for v in PERIODS],
        }

    def run(self):
        """Configure-time scaffold: the binding, the class colours and legend."""
        s, legend = self.strings, self.legend
        labels = self._labels()
        builder = LayerConfigurationBuilder(s[f"{self.strings_key}_name"], "GeoTIFF")
        builder.set_plugin_source(self.name, self.received_args)
        builder.set_raster_classes(
            "ranges",
            [
                {"value": upper, "color": color, "label": label}
                for upper, color, label in zip(legend.breaks[1:], legend.colors, labels)
            ],
            fallback_color=legend.colors[-1],
        )
        builder.set_legend(
            {
                "title": s[self.legend_key],
                "items": [
                    {"label": label, "color": color, "symbol": "square"}
                    for label, color in zip(labels, legend.colors)
                ],
            }
        )
        return builder.build()

    def fetch_source(self):
        """Runtime source: the cycle's raster, re-fetched when a binding changes."""
        s, names, live = self.strings, LIVE_ARGS[self.country.lang], self.country.live
        grid = _choice(self.get_arg(names["grid"]), [g for g, _res, _kind in live.rain_grids])
        statistic = _choice(self.get_arg(names["statistic"]), STATISTICS)
        period = _choice(self.get_arg(names["period"]), PERIODS)
        cycle = self.selected_cycle()

        path = f"{grid}/summary/{self.product}_{period}_{statistic}.{stamp(cycle)}.tif"
        if path not in cycle_files(live.slug, cycle):
            raise ValueError(s["msg_no_summary"].format(
                cycle=cycle_label(cycle, s["sample_tag"]), period=s["rain_periods"][period],
                statistic=s["rain_statistics"][statistic],
                product=s["summary_products"][self.product], grid=grid))
        return geotiff_source(file_url(live.slug, cycle, path), mask_below=self.legend.breaks[0])

    def _labels(self):
        breaks = self.legend.breaks
        labels = [f"{lo:g} - {hi:g}" for lo, hi in zip(breaks, breaks[1:])]
        if self.legend.open_ended:
            labels.append(self.strings["or_more"].format(value=f"{breaks[-1]:g}"))
        return labels


class BasePrecipLayer(BaseSummaryLayer):
    family = "precip_layer"
    strings_key = "precip_layer"
    legend_key = "precip_legend"
    product = "qpeaccum"
    legend = RAINFALL


class BaseSoilMoistureLayer(BaseSummaryLayer):
    family = "soil_moisture_layer"
    strings_key = "soil_layer"
    legend_key = "soil_legend"
    product = "maxsm"
    legend = SOIL_SATURATION


class BaseUnitStreamflowLayer(BaseSummaryLayer):
    family = "unit_streamflow_layer"
    strings_key = "unitq_layer"
    legend_key = "unitq_legend"
    product = "maxunitq"
    legend = UNIT_STREAMFLOW


class PrecipLayerGuatemala(BasePrecipLayer):
    country = GUATEMALA


class PrecipLayerHaiti(BasePrecipLayer):
    country = HAITI


class PrecipLayerAntiguaBarbuda(BasePrecipLayer):
    country = ANTIGUA_BARBUDA


class PrecipLayerComoros(BasePrecipLayer):
    country = COMOROS


class SoilMoistureLayerGuatemala(BaseSoilMoistureLayer):
    country = GUATEMALA


class SoilMoistureLayerHaiti(BaseSoilMoistureLayer):
    country = HAITI


class SoilMoistureLayerAntiguaBarbuda(BaseSoilMoistureLayer):
    country = ANTIGUA_BARBUDA


class SoilMoistureLayerComoros(BaseSoilMoistureLayer):
    country = COMOROS


class UnitStreamflowLayerGuatemala(BaseUnitStreamflowLayer):
    country = GUATEMALA


class UnitStreamflowLayerHaiti(BaseUnitStreamflowLayer):
    country = HAITI


class UnitStreamflowLayerAntiguaBarbuda(BaseUnitStreamflowLayer):
    country = ANTIGUA_BARBUDA


class UnitStreamflowLayerComoros(BaseUnitStreamflowLayer):
    country = COMOROS
