"""Every country exposes exactly the plugin families its data supports."""

from importlib.metadata import entry_points

import pytest

from tgf_wmo_plugins.countries import COUNTRIES
from tgf_wmo_plugins.strings import STRINGS

HAZARD_FAMILIES = {"hazard_layer"}
RECEPTOR_FAMILIES = {"impact_summary", "impact_layer"}
STORM_FAMILIES = {"storm_card", "storm_impact_layer", "storm_impact_summary"}
LIVE_FAMILIES = {"cycle_times", "precip_layer", "soil_moisture_layer", "unit_streamflow_layer",
                 "flood_map_layer", "depth_filter", "risk_matrix", "risk_filter", "risk_layer",
                 "event_summary"}

REGISTERED = {
    ep.name for ep in entry_points(group="intake.drivers")
    if ep.value.startswith("tgf_wmo_plugins.")
}


def expected_families(country):
    families = set(RECEPTOR_FAMILIES)
    # Live cycles publish the rasters even where the training data has none.
    if country.prob_urls is not None or country.live is not None:
        families |= HAZARD_FAMILIES
    # Live cycles stand in for a storm library: depth by probability.
    if country.storms is not None or country.live is not None:
        families |= STORM_FAMILIES
    if country.live is not None:
        families |= LIVE_FAMILIES
        if country.live.gauges:
            families |= {"discharge"}
    return families


@pytest.mark.parametrize("key", sorted(COUNTRIES))
def test_entry_points_match_capabilities(key):
    country = COUNTRIES[key]
    every = HAZARD_FAMILIES | RECEPTOR_FAMILIES | STORM_FAMILIES | LIVE_FAMILIES | {"discharge"}
    registered = {f for f in every if f"uffis_{f}_{key}" in REGISTERED}
    assert registered == expected_families(country)


@pytest.mark.parametrize("key", sorted(COUNTRIES))
def test_country_is_consistent(key):
    country = COUNTRIES[key]
    assert country.lang in STRINGS
    assert len(country.receptors.probabilities) == 4
    if country.prob_urls is not None:
        unit = country.units.default if country.units else None
        assert len(country.prob_urls(unit)) == 4
    if country.storms is not None:
        values = [o["value"] for o in country.storms.options]
        assert str(country.storms.default_index) in values
    if country.units is not None:
        codes = [u.code for u in country.units.table]
        assert len(codes) == len(set(codes))
        if country.receptors.layers is None:
            pytest.fail("unit filtering needs a geopackage")


@pytest.mark.parametrize("value, expected", [
    ("KM111_BambaoMtsanga", "KM111_BambaoMtsanga"),
    ("Comoros_BambaoMtsanga", "KM111_BambaoMtsanga"),  # the sample's site folder name
    ("Nowhere", "KM274_Moroni"),
])
def test_unit_accepts_code_or_site(value, expected):
    from tgf_wmo_plugins.hazard_layer import HazardLayerComoros

    plugin = HazardLayerComoros.__new__(HazardLayerComoros)
    plugin.get_arg = lambda name, default=None: value
    assert plugin.unit() == expected
