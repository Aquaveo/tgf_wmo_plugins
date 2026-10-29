"""The base every country plugin derives from."""

from tethysapp.tethysdash.plugin_helpers import TethysDashPlugin

from tgf_wmo_plugins.receptors import load_receptors
from tgf_wmo_plugins.strings import LIVE_ARGS, STRINGS
from tgf_wmo_plugins.tito import LATEST, SAMPLE, TRAINING, cycle_label, resolve_cycle


def country_group(country):
    """One plugin group per country, so its plugins list together."""
    return f"UFFIS: {country.label_name}"


def country_label(country, name):
    """Country first, so a country's plugins read as a block."""
    return f"{country.label_name}: {name}"


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
        cls.label = country_label(country, s[f"{cls.strings_key}_label"])
        cls.group = country_group(country)
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
        """The admin unit asked for, or the default when unset or unresolved.

        A unit may also be named by its TITO site, so one dropdown can feed both
        the plugins and raster URLs built from the site folders.
        """
        units = self.country.units
        if units is None:
            return None
        value = self.get_arg(units.arg)
        if value in units.by_code:
            return value
        live = self.country.live
        if live is not None:
            by_site = {live.raster_site(code): code for code in units.by_code}
            return by_site.get(value, units.default)
        return units.default


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
        if live.sample:
            cycles.append({"value": SAMPLE, "label": s["cycle_sample"]})
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

    def title_suffix(self, cycle):
        if cycle == TRAINING:
            return ""
        return f" ({cycle_label(cycle, self.strings['sample_tag'])})"


class LabelledInput:
    """The label text and show-label settings of a country's variable input.

    TethysDash shows a variable input's name as its label, so the label text is
    also the variable other plugins bind; left empty, it is `publishes`.
    """

    publishes = None

    @staticmethod
    def label_args(country):
        names = LIVE_ARGS[country.lang]
        return {names["label_text"]: "text", names["show_label"]: "checkbox"}

    @classmethod
    def variable_name(cls, args):
        """The variable a dashboard item publishes, given its stored args."""
        value = args.get(LIVE_ARGS[cls.country.lang]["label_text"])
        if isinstance(value, str) and value.strip() and "${" not in value:
            return value.strip()
        return cls.publishes

    def label_shown(self):
        """Shown unless the checkbox is cleared; it may arrive as a bool or a string."""
        value = self.get_arg(LIVE_ARGS[self.country.lang]["show_label"], True)
        return str(value).strip().lower() not in ("false", "0", "no", "off")


class CountryChoiceInput(LabelledInput, TethysDashPlugin):
    """A dropdown variable input with a country's choices, in its language.

    A subclass sets `family` and `strings_key` (the label, description, tags
    and published variable come from `<strings_key>_*` in strings.py), and
    implements `choices` and `initial`; a country subclass then sets only
    `country`.
    """

    family = None
    strings_key = None
    country = None
    type = "variable_input"

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        country = cls.__dict__.get("country")
        if country is None:
            return
        s = STRINGS[country.lang]
        cls.name = f"uffis_{cls.family}_{country.key}"
        cls.label = country_label(country, s[f"{cls.strings_key}_label"])
        cls.group = country_group(country)
        cls.tags = list(s[f"{cls.strings_key}_tags"])
        cls.description = s[f"{cls.strings_key}_desc"]
        cls.publishes = s[f"{cls.strings_key}_variable"]
        cls.args = cls.label_args(country)

    def choices(self, s):
        """(value, label) pairs, in display order."""
        raise NotImplementedError

    def initial(self):
        raise NotImplementedError

    def run(self):
        s = STRINGS[self.country.lang]
        return {
            "variable_name": self.variable_name(self.received_args),
            "show_label": self.label_shown(),
            "initial_value": self.initial(),
            "variable_options_source": "dropdown",
            "metadata": {"choices": [{"label": label, "value": value}
                                     for value, label in self.choices(s)]},
        }
