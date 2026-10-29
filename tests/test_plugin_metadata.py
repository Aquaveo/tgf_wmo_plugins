"""Plugin names, labels, groups and args are a published interface.

A dashboard stores a plugin's `source` name and, for a variable input fed from a
plugin argument, a string embedding its group and label. Changing any of them
breaks saved dashboards silently, so they are pinned here. If a change is
deliberate, regenerate tests/plugin_metadata.json and the affected dashboards.
"""

import json
from importlib.metadata import entry_points
from pathlib import Path

import pytest

SNAPSHOT = json.loads((Path(__file__).parent / "plugin_metadata.json").read_text())
FIELDS = ("name", "label", "group", "type", "args", "dynamic_map_layer")

PLUGINS = {
    ep.name: ep for ep in entry_points(group="intake.drivers")
    if ep.value.startswith("tgf_wmo_plugins.")
}


def test_snapshot_covers_every_plugin():
    assert set(PLUGINS) == set(SNAPSHOT)


@pytest.mark.parametrize("name", sorted(SNAPSHOT))
def test_metadata_unchanged(name):
    cls = PLUGINS[name].load()
    # JSON round trip so tuples and lists compare equal.
    actual = json.loads(json.dumps({f: getattr(cls, f) for f in FIELDS}))
    assert actual == SNAPSHOT[name]


@pytest.mark.parametrize("name", sorted(SNAPSHOT))
def test_args_do_not_shadow_attributes(name):
    # TethysDashPlugin.__init__ setattr()s every received arg onto the
    # instance, so an arg named like a method replaces that method.
    cls = PLUGINS[name].load()
    assert not [arg for arg in cls.args if hasattr(cls, arg)]
