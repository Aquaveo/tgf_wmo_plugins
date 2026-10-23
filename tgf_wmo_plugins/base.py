"""The base every country plugin derives from."""

from tethysapp.tethysdash.plugin_helpers import TethysDashPlugin

from tgf_wmo_plugins.receptors import load_receptors
from tgf_wmo_plugins.strings import LIVE_ARGS, STRINGS
from tgf_wmo_plugins.tito import LATEST, TRAINING, cycle_label, resolve_cycle


class CountryPlugin(TethysDashPlugin):
    """A plugin family's computation, with the country left as a parameter.

    A concrete plugin only sets `country`. TethysDash reads `name`, `label`,
    `args` and the rest off the class at discovery time, so `__init_subclass__`
    derives them from the country the moment the subclass is defined. The
    labels and args are a published interface -- dashboards store them -- and
    tests/plugin_metadata.json pins them.
    """

    family = None  # the entry-point infix, e.g. "hazard_layer"
    strings_key = None  # prefix of the family's label/desc/tags in strings.py
    country = None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        country = cls.__dict__.get("country")
        if country is None:
            return
        s = STRINGS[country.lang]
        cls.name = f"uffis_{cls.family}_{country.key}"
        cls.label = f"{s[f'{cls.strings_key}_label']} ({country.label_name})"
        cls.group = s["group"]
        cls.tags = list(s[f"{cls.strings_key}_tags"])
        cls.description = s[f"{cls.strings_key}_desc"]
        cls.args = cls.country_args(country)

    @classmethod
    def country_args(cls, country):
        """The family's `args` schema for `country`."""
        raise NotImplementedError

    @staticmethod
    def unit_args(country):
        """The admin-unit dropdown, for a country published per unit."""
        units = country.units
        return {units.arg: units.options} if units else {}

    @property
    def strings(self):
        return STRINGS[self.country.lang]

    def unit(self):
        """The admin unit asked for, or the default when unset or unresolved."""
        units = self.country.units
        if units is None:
            return None
        value = self.get_arg(units.arg)
        return value if value in units.by_code else units.default


class LiveData:
    """The cycle and site arguments of a plugin that can read live TITO cycles.

    Mixed in beside CountryPlugin. A country without live data keeps only its
    training data and gets none of these arguments.
    """

    # Whether the plugin reads the probability rasters, and so offers a choice
    # of raster variant.
    uses_rasters = False

    @classmethod
    def has_training(cls, country):
        return True

    @classmethod
    def live_args(cls, country):
        live = country.live
        if live is None:
            return {}
        s, names = STRINGS[country.lang], LIVE_ARGS[country.lang]
        cycles = [{"value": LATEST, "label": s["cycle_latest"]}]
        if cls.has_training(country):
            cycles.append({"value": TRAINING, "label": s["cycle_training"]})
        args = {names["cycle"]: cycles}
        if live.site_arg:
            args[live.site_arg] = [
                {"value": code, "label": label} for code, label in live.site_choices
            ]
        if cls.uses_rasters:
            args[names["variant"]] = [
                {"value": v, "label": s["variants"][v]} for v in live.variants
            ]
        return args

    def selected_cycle(self):
        """The cycle stamp to read, or TRAINING. Unset means the latest cycle."""
        live = self.country.live
        if live is None:
            return TRAINING
        cycle = resolve_cycle(self.get_arg(LIVE_ARGS[self.country.lang]["cycle"]), live.slug)
        if cycle == TRAINING and not self.has_training(self.country):
            raise ValueError(self.strings["msg_no_training"])
        return cycle

    def scope(self):
        """The admin unit, or the live site where the sites are not units."""
        if self.country.units is not None:
            return self.unit()
        live = self.country.live
        if live is not None and live.site_arg:
            codes = [code for code, _label in live.site_choices]
            value = self.get_arg(live.site_arg)
            return value if value in codes else codes[0]
        return None

    def scope_label(self):
        """The scope as a reader would name it, for messages."""
        scope, country = self.scope(), self.country
        if country.units is not None:
            return country.units.by_code[scope].name
        if country.live is not None and country.live.site_arg:
            return dict(country.live.site_choices)[scope]
        return country.label_name

    def variant(self):
        variants = self.country.live.variants
        value = self.get_arg(LIVE_ARGS[self.country.lang]["variant"])
        return value if value in variants else variants[0]

    def receptors(self, cycle, geometry=False):
        """The scope's receptors (None if the cycle published none), the
        `Receptors` config describing them, and the population share's
        denominator.

        Live files carry no census figure, so a live share is of the people in
        the file -- the site's whole building stock.
        """
        country, scope = self.country, self.scope()
        df = load_receptors(country.key, scope, geometry, cycle)
        if cycle == TRAINING:
            return df, country.receptors, country.unit_population(scope)
        rec = country.live.receptors
        population = 0.0 if df is None else df[rec.columns.population].sum()
        return df, rec, population

    @staticmethod
    def title_suffix(cycle):
        return "" if cycle == TRAINING else f" — {cycle_label(cycle)}"
