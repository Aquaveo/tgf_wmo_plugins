"""Every dashboard in dashboards/ still binds to the installed plugins.

A renamed plugin, a removed argument or a changed label leaves a dashboard that
imports fine and then silently shows nothing, so the bindings are checked here.
"""

import json
import re
from importlib.metadata import entry_points
from pathlib import Path

import pytest

DASHBOARDS = sorted((Path(__file__).parent.parent / "dashboards").glob("*/*.json"))
PLUGINS = {
    ep.name: ep.load() for ep in entry_points(group="intake.drivers")
    if ep.value.startswith("tgf_wmo_plugins.")
}
VARIABLE = re.compile(r"\$\{([^}]+)\}")
# Option sources the frontend provides itself rather than a plugin argument.
BUILT_IN_SOURCES = {"Base Map Layers", "dropdown", "number", "text", "checkbox", "date"}


def space_and_capitalize(arg):
    """The frontend's spaceAndCapitalize, which names an argument in an option source."""
    return " ".join(word[:1].upper() + word[1:] for word in arg.replace("_", " ").split(" "))


def option_sources():
    return {
        f"{cls.group}: {cls.label} - {space_and_capitalize(arg)}"
        for cls in PLUGINS.values() for arg in cls.args
    }


def plugin_uses(dashboard):
    """(source, args) for every plugin a dashboard calls, map layers included."""
    for tab in dashboard["tabs"]:
        for item in tab["gridItems"]:
            if item["source"] == "Map":
                for layer in item["args_string"].get("layers", []):
                    plugin = layer["configuration"]["props"].get("pluginSource")
                    if plugin:
                        yield plugin["source"], plugin["args"]
            elif item["source"] != "Variable Input":
                yield item["source"], item["args_string"]


def defined_variables(dashboard):
    names = set()
    for tab in dashboard["tabs"]:
        for item in tab["gridItems"]:
            if item["source"] == "Variable Input":
                names.add(item["args_string"]["variable_name"])
            elif PLUGINS.get(item["source"]) and PLUGINS[item["source"]].type == "variable_input":
                cls = PLUGINS[item["source"]]
                published = getattr(cls, "variable_name", None)
                names.add(published(item["args_string"]) if published else cls.publishes)
    return names


@pytest.mark.parametrize("path", DASHBOARDS, ids=lambda p: f"{p.parent.name}/{p.stem}")
def test_dashboard_binds(path):
    dashboard = json.loads(path.read_text())
    problems = []
    for source, args in plugin_uses(dashboard):
        if not source.startswith("uffis_"):
            continue
        cls = PLUGINS.get(source)
        if cls is None:
            problems.append(f"{source} is not installed")
            continue
        unknown = set(args) - set(cls.args)
        if unknown:
            problems.append(f"{source} has no args {sorted(unknown)}")

    sources = option_sources()
    for tab in dashboard["tabs"]:
        for item in tab["gridItems"]:
            src = item["args_string"].get("variable_options_source")
            if item["source"] == "Variable Input" and src not in BUILT_IN_SOURCES and src not in sources:
                problems.append(f"option source {src!r} matches no plugin argument")

    used = set(VARIABLE.findall(json.dumps(dashboard, ensure_ascii=False)))
    missing = used - defined_variables(dashboard)
    if missing:
        problems.append(f"variables used but never defined: {sorted(missing)}")
    assert not problems, problems
