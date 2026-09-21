"""Buildings and roads coloured by flood depth for one storm, as a map layer."""

import json

from tethysapp.tethysdash.plugin_helpers import (
    LayerConfigurationBuilder,
    TethysDashPlugin,
)

from tgf_wmo_plugins.common import (
    BARBADOS_PARISH_OPTIONS,
    COMOROS_UNIT_OPTIONS,
    COMOROS_UNITS,
    UNIT_STORM_OPTIONS,
    FIRST_WET_STORM,
    STORM_OPTIONS,
    as_representative_points,
    coerce_index,
)
from tgf_wmo_plugins.storm_impact import (
    DEPTH_BANDS,
    UNIT_DEFAULT_STORM,
    UNIT_MEASURES,
    banded_features,
    store_grid,
    unit_banded_features,
)
from tgf_wmo_plugins.strings import STRINGS


class BaseStormImpactLayer(TethysDashPlugin):
    LANG = None
    type = "map_layer"
    dynamic_map_layer = True
    args = {"index": STORM_OPTIONS}
    # See BaseImpactLayer.buildings_as_points: one flag for the geometry that
    # goes over the wire and the rules that colour it.
    buildings_as_points = False

    def run(self):
        s = STRINGS[self.LANG]
        builder = LayerConfigurationBuilder(s["storm_layer_name"], "GeoJSON")
        builder.set_plugin_source(self.name, self.received_args)
        builder.set_style(self._style(s))
        builder.set_legend(
            {
                "title": s["depth_legend"],
                "items": [
                    {"label": s["bands"][value], "color": color, "symbol": "square"}
                    for value, color, _floor in DEPTH_BANDS
                ],
            }
        )
        return builder.build()

    def fetch_features(self):
        s = STRINGS[self.LANG]
        index = coerce_index(self.get_arg("index", FIRST_WET_STORM), FIRST_WET_STORM)

        self.send_update(s["msg_sampling"], percentage_complete=40)
        flooded = banded_features(index).copy()
        flooded = flooded.rename(columns={"banda": s["attr_band"],
                                          "profundidad_m": s["attr_depth"]})
        flooded[s["attr_level"]] = flooded[s["attr_band"]].map(s["bands"])

        self.send_update(
            s["msg_flooded"].format(count=len(flooded)), percentage_complete=100
        )
        columns = [
            "tipo",
            s["attr_level"],
            s["attr_band"],
            s["attr_depth"],
            "poblacion",
            "area_m2",
            "longitud_m",
        ]
        collection = json.loads(flooded[columns + ["geometry"]].to_json())
        # The store's grid is already EPSG:3857, which OpenLayers resolves
        # natively -- no proj4 needed and no reprojection on the way out.
        _transform, _shape, crs = store_grid()
        collection["crs"] = {"type": "name", "properties": {"name": crs}}
        return collection

    @classmethod
    def _style(cls, s):
        """Rule-based styling on the depth-band attribute. See hazard_layer._style.

        The building rules follow `buildings_as_points`, exactly as the hazard
        impact layer's do.
        """
        rules = []
        for value, color, _floor in DEPTH_BANDS:
            condition = {
                "conditionField": s["attr_band"],
                "conditionType": "=",
                "conditionValue": str(value),
            }
            rules.append(
                {
                    "name": f"{s['bands'][value]} ({s['buildings']})",
                    **cls._building_rule(),
                    **condition,
                    "fill": color,
                    "stroke": color,
                }
            )
            rules.append(
                {
                    "name": f"{s['bands'][value]} ({s['roads']})",
                    "geometryType": "linestring",
                    **condition,
                    "stroke": color,
                    "strokeWidth": "3",
                }
            )
        return {"default": cls._default_style(), "rules": rules}

    @classmethod
    def _building_rule(cls):
        """The geometry-dependent half of a building rule."""
        if cls.buildings_as_points:
            return {"geometryType": "point", "strokeWidth": "1",
                    "size": "4", "shape": "circle"}
        return {"geometryType": "polygon", "strokeWidth": "1"}

    @classmethod
    def _default_style(cls):
        """What an unmatched feature falls back to, keyed by geometry bucket."""
        buildings = (
            {"point": {"fill": "#9e9e9e", "stroke": "#9e9e9e",
                       "strokeWidth": "1", "size": "3", "shape": "circle"}}
            if cls.buildings_as_points
            else {"polygon": {"fill": "#9e9e9e", "stroke": "#9e9e9e",
                              "strokeWidth": "0"}}
        )
        return {**buildings, "linestring": {"stroke": "#9e9e9e", "strokeWidth": "1"}}


class StormImpactLayerGuatemala(BaseStormImpactLayer):
    LANG = "es"
    name = "uffis_storm_impact_layer_guatemala"
    label = f"{STRINGS['es']['storm_layer_label']} (Guatemala)"
    group = STRINGS["es"]["group"]
    tags = ["inundación", "impacto", "zarr", "tormenta", "map_layer", "español"]
    description = STRINGS["es"]["storm_layer_desc"]


# Vector output is EPSG:4326 for every country. The raster loaders resolve a
# published CRS on demand from the generated EPSG table, but `loadGeoJSON` hands
# `crs.properties.name` straight to OpenLayers without that lookup, so a
# plugin-returned collection has to name a projection the map already holds.
# This is the same OUTPUT_CRS impact_layer settles on, for the same reason.
OUTPUT_CRS = "EPSG:4326"


class BaseStormImpactLayerUnit(BaseStormImpactLayer):
    """One unit's flooded buildings and roads, for one storm of its library.

    Only the two ends differ from the Guatemala layer: which features are
    sampled, and that the result is reprojected into a CRS the frontend resolves.
    The legend and the run() scaffold are inherited; every country here draws
    polygon buildings and linestring roads, so the shared style covers them all.
    """

    country = None
    unit_arg = "unit"
    default_unit = None

    def fetch_features(self):
        s = STRINGS[self.LANG]
        unit = self.get_arg(self.unit_arg, self.default_unit)
        index = coerce_index(
            self.get_arg("index", UNIT_DEFAULT_STORM), UNIT_DEFAULT_STORM
        )

        self.send_update(s["msg_sampling"], percentage_complete=40)
        flooded = unit_banded_features(self.country, unit, index).copy()
        flooded = flooded.rename(columns={"banda": s["attr_band"],
                                          "profundidad_m": s["attr_depth"]})
        flooded[s["attr_level"]] = flooded[s["attr_band"]].map(s["bands"])
        flooded = flooded.to_crs(OUTPUT_CRS)
        if self.buildings_as_points:
            flooded = as_representative_points(flooded)

        self.send_update(
            s["msg_flooded"].format(count=len(flooded)), percentage_complete=100
        )
        columns = ["type", s["attr_level"], s["attr_band"], s["attr_depth"],
                   *UNIT_MEASURES]
        collection = json.loads(flooded[columns + ["geometry"]].to_json())
        collection["crs"] = {"type": "name", "properties": {"name": OUTPUT_CRS}}
        return collection


class StormImpactLayerComoros(BaseStormImpactLayerUnit):
    LANG = "fr"
    country = "comoros"
    unit_arg = "commune"
    default_unit = COMOROS_UNITS[0][0]
    args = {"commune": COMOROS_UNIT_OPTIONS, "index": UNIT_STORM_OPTIONS}
    name = "uffis_storm_impact_layer_comoros"
    label = f"{STRINGS['fr']['storm_layer_label']} (Comores)"
    group = STRINGS["fr"]["group"]
    tags = ["inondation", "impact", "zarr", "tempête", "map_layer", "français"]
    description = STRINGS["fr"]["storm_layer_desc"]


class StormImpactLayerBarbados(BaseStormImpactLayerUnit):
    LANG = "en"
    country = "barbados"
    unit_arg = "parish"
    default_unit = "BB08_SaintMichael"
    args = {"parish": BARBADOS_PARISH_OPTIONS, "index": UNIT_STORM_OPTIONS}
    buildings_as_points = True
    name = "uffis_storm_impact_layer_barbados"
    label = f"{STRINGS['en']['storm_layer_label']} (Barbados)"
    group = STRINGS["en"]["group"]
    tags = ["flood", "impact", "zarr", "storm", "map_layer", "dynamic", "english"]
    description = STRINGS["en"]["storm_layer_desc"]
