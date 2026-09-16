"""Every plugin must be reachable under the name it advertises.

TethysDash resolves a dashboard item's `source` -- and a dynamic layer's
`pluginSource.source`, which `run()` fills from `self.name` -- by exact lookup in
`intake.source.registry`, whose keys are the `intake.drivers` entry-point names.
A class whose `name` differs from its entry-point key installs fine and then
fails at import time with "Visualization (...) is not installed."
"""

from importlib.metadata import entry_points

import pytest

PLUGIN_ENTRY_POINTS = [
    ep for ep in entry_points(group="intake.drivers")
    if ep.value.startswith("tgf_wmo_plugins.")
]


def test_package_registers_plugins():
    assert PLUGIN_ENTRY_POINTS, "tgf_wmo_plugins must be installed (pip install -e .)"


@pytest.mark.parametrize("ep", PLUGIN_ENTRY_POINTS, ids=lambda ep: ep.name)
def test_plugin_name_matches_entry_point(ep):
    assert ep.load().name == ep.name
