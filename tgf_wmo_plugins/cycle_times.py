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

from tgf_wmo_plugins.base import country_group, country_label
from tgf_wmo_plugins.countries import ANTIGUA_BARBUDA, COMOROS, GUATEMALA, HAITI
from tgf_wmo_plugins.strings import LIVE_ARGS, STRINGS
from tgf_wmo_plugins.tito import LATEST, SAMPLE, available_cycles, cycle_label


class BaseCycleTimes(TethysDashPlugin):
    """Set `country`; everything else follows from it, in the country's language.

    The published variable stays `Date` in every language: every dashboard
    binds ${Date}.
    """

    country = None
    type = "variable_input"
    publishes = "Date"

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        country = cls.__dict__.get("country")
        if country is None:
            return
        s = STRINGS[country.lang]
        cls.name = f"uffis_cycle_times_{country.key}"
        cls.label = country_label(country, s["cycle_times_label"])
        cls.group = country_group(country)
        cls.tags = list(s["cycle_times_tags"])
        cls.description = s["cycle_times_desc"]
        # Where a sample exists, a demo dashboard can open on it instead.
        if country.live.sample:
            cls.args = {LIVE_ARGS[country.lang]["start"]: [
                {"value": LATEST, "label": s["start_latest"]},
                {"value": SAMPLE, "label": s["start_sample"]},
            ]}

    def run(self):
        live, s = self.country.live, STRINGS[self.country.lang]
        cycles = available_cycles(live.slug)
        # The sample cycles go after every live one.
        samples = available_cycles(live.slug, sample=True) if live.sample else []
        start_on_sample = samples and self.get_arg(LIVE_ARGS[self.country.lang]["start"]) == SAMPLE
        return {
            "variable_name": self.publishes,
            "initial_value": samples[0] if start_on_sample else cycles[0],
            "variable_options_source": "dropdown",
            "metadata": {
                "choices": [{"label": cycle_label(c, s["sample_tag"]), "value": c}
                            for c in cycles + samples]
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
