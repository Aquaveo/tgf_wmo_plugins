"""Impact-based forecasting with the SFFS/FGS flood risk matrix, from live cycles.

Speight et al. (2018): a feature's likelihood band (from its exceedance
probability) and impact severity (from the depth) are combined through the
matrix into a warning level. Severity is taken at each depth TITO thresholds --
0.1 m Minor, 0.3 m Significant, 0.7 m Severe -- and the feature takes the
highest warning any of them gives, ignoring probabilities under the reporting
threshold. This reproduces the `risk_class` TITO writes on every feature.
Districts use TITO's own warning, since its rule counts properties per district.
"""

from functools import lru_cache
from html import escape

import numpy as np
import pyogrio
from tethysapp.tethysdash.plugin_helpers import LayerConfigurationBuilder

from tgf_wmo_plugins.base import CountryChoiceInput, CountryPlugin, LiveData
from tgf_wmo_plugins.countries import ANTIGUA_BARBUDA, COMOROS, COUNTRIES, GUATEMALA, HAITI
from tgf_wmo_plugins.impact_layer import _load, feature_collection, feature_style
from tgf_wmo_plugins.strings import LIVE_ARGS, STRINGS
from tgf_wmo_plugins.tito import cycle_files, cycle_label, file_url, live_download

# [likelihood][severity] -> warning level, both indexed very low/minimal first.
MATRIX = np.array([[0, 0, 1, 1], [0, 1, 1, 2], [0, 1, 2, 2], [0, 1, 2, 3]])
LIKELIHOOD_EDGES = [0.2, 0.4, 0.6]  # Very Low < 0.2 <= Low < 0.4 <= Medium < 0.6 <= High
REPORTING_THRESHOLD = 0.05
RISK_COLORS = ["#63BE5F", "#FFD500", "#F58220", "#DA291C"]
TEXT_ON_COLOR = "#1d1d1b"
DEFAULT_MIN_RISK = 0


def risk_class(df, probabilities):
    """Warning level per row, from the P(>=0.1 m), P(>=0.3 m), P(>=0.7 m) columns."""
    p = df[list(probabilities[:3])].to_numpy(dtype=float)
    likelihood = np.digitize(np.nan_to_num(p), LIKELIHOOD_EDGES)
    per_severity = np.where(p >= REPORTING_THRESHOLD, MATRIX[likelihood, np.arange(1, 4)], 0)
    return per_severity.max(axis=1) if len(df) else np.zeros(0, dtype=int)


@lru_cache(maxsize=16)
def district_risk(key, scope, cycle):
    """TITO's warning level per district, or None when the cycle has none."""
    live = COUNTRIES[key].live
    path = live.receptor_path(scope, cycle)
    if path not in cycle_files(live.slug, cycle):
        return None
    local = live_download(file_url(live.slug, cycle, path))
    if "admin_ibf" not in {name for name, _ in pyogrio.list_layers(local)}:
        return None
    admin = pyogrio.read_dataframe(local, layer="admin_ibf", columns=["risk_class"],
                                   read_geometry=False)
    return admin["risk_class"].astype(int).to_numpy()


class LiveOnly(LiveData):
    @classmethod
    def has_training(cls, country):
        return False

    @classmethod
    def country_args(cls, country):
        return {**cls.unit_args(country), **cls.live_args(country)}


def _chip(label, color):
    return (f'<span style="display:inline-block;min-width:22%;margin:2px 1%;padding:4px 0;'
            f'border-radius:4px;background:{color};color:{TEXT_ON_COLOR};font-weight:700;'
            f'text-align:center;font-size:12px">{escape(label)}</span>')


class BaseRiskMatrix(LiveOnly, CountryPlugin):
    family = "risk_matrix"
    strings_key = "risk_matrix"
    type = "text"

    def run(self):
        s = self.strings
        cell = "border:2px solid #fff;height:30px"
        head = "font-size:12px;color:#555;font-weight:600;background:#f3f6f8;" + cell
        rows = []
        for li in reversed(range(4)):  # High at the top
            cells = "".join(
                f'<td style="background:{RISK_COLORS[MATRIX[li][sv]]};{cell}"></td>' for sv in range(4)
            )
            rows.append(f'<tr><th style="{head}">{escape(s["likelihood_levels"][li])}</th>{cells}</tr>')
        header = "".join(f'<th style="{head}">{escape(s["severity_levels"][sv])}</th>' for sv in range(4))
        axis = "font-size:11px;color:#555;font-weight:700;text-transform:uppercase"
        table = (
            '<table style="width:100%;border-collapse:collapse;table-layout:fixed;text-align:center">'
            f'<tr><th></th><th colspan="4" style="{axis}">{escape(s["axis_severity"])}</th></tr>'
            f'<tr><th style="{axis}">{escape(s["axis_likelihood"])}</th>{header}</tr>'
            f'{"".join(rows)}</table>'
        )
        chips = "".join(_chip(s["risk_levels"][r], RISK_COLORS[r]) for r in range(4))

        cycle = self.selected_cycle()
        districts = district_risk(self.country.key, self.scope(), cycle)
        if districts is not None and len(districts):
            worst = int(districts.max())
            chip = _chip(s["risk_levels"][worst], RISK_COLORS[worst])
            overall = (f'<p style="margin:8px 0 0">{escape(s["overall_warning"])} '
                       f'({escape(cycle_label(cycle, s["sample_tag"]))}): {chip}</p>')
        else:
            overall = (f'<p style="margin:8px 0 0;color:#555">{escape(s["overall_warning"])} '
                       f'({escape(cycle_label(cycle, s["sample_tag"]))}): {escape(s["status_quiet"])}</p>')
        return {"text": f'<h4 style="margin:0 0 6px">{escape(s["risk_matrix_title"])}</h4>'
                        f'{table}<div style="margin-top:6px">{chips}</div>{overall}'}


class BaseRiskFilter(CountryChoiceInput):
    """The warning-level choice the risk layer is filtered by."""

    family = "risk_filter"
    strings_key = "risk_filter"

    def choices(self, s):
        return [(str(level), label) for level, label in s["risk_filter_choices"].items()]

    def initial(self):
        return str(DEFAULT_MIN_RISK)


class BaseRiskLayer(LiveOnly, CountryPlugin):
    family = "risk_layer"
    strings_key = "risk_layer"
    type = "map_layer"
    dynamic_map_layer = True

    @classmethod
    def country_args(cls, country):
        s = STRINGS[country.lang]
        return {
            **super().country_args(country),
            LIVE_ARGS[country.lang]["min_risk"]: [
                {"value": str(level), "label": label}
                for level, label in s["risk_filter_choices"].items()
            ],
        }

    def min_risk(self):
        try:
            value = int(self.get_arg(LIVE_ARGS[self.country.lang]["min_risk"], DEFAULT_MIN_RISK))
        except (TypeError, ValueError):
            return DEFAULT_MIN_RISK
        return value if 0 <= value <= 3 else DEFAULT_MIN_RISK

    def run(self):
        s = self.strings
        builder = LayerConfigurationBuilder(s["risk_layer_name"], "GeoJSON")
        builder.set_plugin_source(self.name, self.received_args)
        colors = list(enumerate(RISK_COLORS))
        builder.set_style(feature_style(s, "attr_risk", s["risk_levels"], colors))
        builder.set_legend({
            "title": s["risk_legend"],
            "items": [{"label": s["risk_levels"][r], "color": c, "symbol": "square"} for r, c in colors],
        })
        return builder.build()

    def fetch_features(self):
        s = self.strings
        cycle = self.selected_cycle()
        rec = self.country.live.receptors

        self.send_update(s["msg_loading_features"], percentage_complete=20)
        gdf = _load(self.country.key, self.scope(), cycle)
        if gdf is None:
            self.send_update(s["msg_no_receptors"].format(site=self.scope_label(), cycle=cycle),
                             percentage_complete=100)
            return feature_collection(None, [])

        risk = risk_class(gdf, rec.probabilities)
        keep = risk >= self.min_risk()
        # "All" stops at the reporting threshold: the rest of a site's stock never
        # gets wet, and drawing it is a third of a million features in Gris.
        keep &= (risk > 0) | (gdf[rec.probabilities[0]] >= REPORTING_THRESHOLD).to_numpy()
        shown = gdf[keep].copy()
        shown[s["attr_risk"]] = risk[keep]
        shown[s["attr_risk_level"]] = shown[s["attr_risk"]].map(s["risk_levels"])
        shown[list(rec.probabilities)] = shown[list(rec.probabilities)].round(2)

        self.send_update(s["msg_at_risk"].format(count=len(shown)), percentage_complete=100)
        cols = rec.columns
        return feature_collection(
            shown, [cols.type, s["attr_risk_level"], s["attr_risk"], *rec.probabilities, *cols.measures]
        )


class BaseEventSummary(LiveOnly, CountryPlugin):
    family = "event_summary"
    strings_key = "event_summary"
    type = "text"

    def run(self):
        s = self.strings
        cycle = self.selected_cycle()
        df, rec, _population = self.receptors(cycle)
        cols = rec.columns
        title = (f'<h4 style="margin:0 0 6px">{escape(s["event_summary_title"])} '
                 f'({escape(cycle_label(cycle, s["sample_tag"]))})</h4>')
        if df is None:
            note = s["msg_no_receptors"].format(site=self.scope_label(), cycle=cycle)
            return {"text": f'{title}<p style="color:#555">{escape(note)}</p>'}

        risk = risk_class(df, rec.probabilities)
        buildings = (df[cols.type] == cols.building).to_numpy()
        districts = district_risk(self.country.key, self.scope(), cycle)

        td = "padding:4px 6px;border-bottom:1px solid #e6e5e0;text-align:right"
        rows = []
        for r in range(4):
            mask = risk == r
            dot = (f'<span style="display:inline-block;width:10px;height:10px;border-radius:2px;'
                   f'background:{RISK_COLORS[r]};margin-right:6px"></span>')
            n_districts = int((districts == r).sum()) if districts is not None else 0
            rows.append(
                f'<tr><td style="{td};text-align:left">{dot}{escape(s["risk_levels"][r])}</td>'
                f'<td style="{td}">{int((mask & buildings).sum()):,}</td>'
                f'<td style="{td}">{df.loc[mask, cols.length].sum() / 1000:,.1f}</td>'
                f'<td style="{td}">{n_districts:,}</td></tr>'
            )
        th = "padding:4px 6px;border-bottom:2px solid #ccc;text-align:right;font-weight:600"
        header = (f'<tr><th style="{th};text-align:left">{escape(s["col_warning"])}</th>'
                  f'<th style="{th}">{escape(s["col_buildings"])}</th>'
                  f'<th style="{th}">{escape(s["col_road_km"])}</th>'
                  f'<th style="{th}">{escape(s["col_districts"])}</th></tr>')
        people = df.loc[(risk >= 1) & buildings, cols.population].sum()
        footer = (f'<p style="margin:6px 0 0;font-size:12px;color:#555">'
                  f'{escape(s["population_yellow"])}: <b>{people:,.0f}</b></p>')
        return {"text": f'{title}<table style="width:100%;border-collapse:collapse;font-size:13px">'
                        f'{header}{"".join(rows)}</table>{footer}'}


class RiskMatrixGuatemala(BaseRiskMatrix):
    country = GUATEMALA


class RiskMatrixHaiti(BaseRiskMatrix):
    country = HAITI


class RiskMatrixAntiguaBarbuda(BaseRiskMatrix):
    country = ANTIGUA_BARBUDA


class RiskMatrixComoros(BaseRiskMatrix):
    country = COMOROS


class RiskFilterGuatemala(BaseRiskFilter):
    country = GUATEMALA


class RiskFilterHaiti(BaseRiskFilter):
    country = HAITI


class RiskFilterAntiguaBarbuda(BaseRiskFilter):
    country = ANTIGUA_BARBUDA


class RiskFilterComoros(BaseRiskFilter):
    country = COMOROS


class RiskLayerGuatemala(BaseRiskLayer):
    country = GUATEMALA


class RiskLayerHaiti(BaseRiskLayer):
    country = HAITI


class RiskLayerAntiguaBarbuda(BaseRiskLayer):
    country = ANTIGUA_BARBUDA


class RiskLayerComoros(BaseRiskLayer):
    country = COMOROS


class EventSummaryGuatemala(BaseEventSummary):
    country = GUATEMALA


class EventSummaryHaiti(BaseEventSummary):
    country = HAITI


class EventSummaryAntiguaBarbuda(BaseEventSummary):
    country = ANTIGUA_BARBUDA


class EventSummaryComoros(BaseEventSummary):
    country = COMOROS
