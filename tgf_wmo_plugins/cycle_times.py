"""A dropdown of a country's live TITO cycles, newest first.

Each value is the cycle stamp exactly as the URLs spell it, e.g.
'20261001.200000', so the same variable can drive a plugin's `cycle` argument or
name a file in a layer URL:

    .../outputs/guatemala/${Date}/guatemala_900m/summary/
    qpeaccum_forecast_median.${Date}.tif

There is no "latest" entry because no URL can spell it; the newest cycle is the
first choice and the initial value instead.
"""

from tethysapp.tethysdash.plugin_helpers import TethysDashPlugin

from tgf_wmo_plugins.countries import ANTIGUA_BARBUDA, COMOROS, GUATEMALA, HAITI
from tgf_wmo_plugins.tito import available_cycles, cycle_label


class BaseCycleTimes(TethysDashPlugin):
    """Set `country`; everything else follows from it.

    The labels are English in every country, as they were when only the
    Guatemala input existed, since dashboards store them.
    """

    country = None
    group = "UFFIS Live"
    type = "variable_input"

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        country = cls.__dict__.get("country")
        if country is None:
            return
        cls.name = f"uffis_cycle_times_{country.key}"
        cls.label = f"Available Cycles ({country.label_name})"
        cls.tags = ["uffis", "tito", country.key, "date"]
        cls.description = (
            f"Every hourly TITO cycle still published for {country.label_name}, "
            "newest first, valued as the cycle stamp the file URLs use."
        )

    def run(self):
        cycles = available_cycles(self.country.live.slug)
        return {
            "variable_name": "Date",
            "initial_value": cycles[0],
            "variable_options_source": "dropdown",
            "metadata": {
                "choices": [{"label": cycle_label(c), "value": c} for c in cycles]
            },
        }


class CycleTimesGuatemala(BaseCycleTimes):
    country = GUATEMALA


class CycleTimesHaiti(BaseCycleTimes):
    country = HAITI


class CycleTimesAntiguaBarbuda(BaseCycleTimes):
    country = ANTIGUA_BARBUDA


class CycleTimesComoros(BaseCycleTimes):
    country = COMOROS
