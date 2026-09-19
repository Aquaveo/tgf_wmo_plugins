"""Flood hazard classification as a dynamic map layer.

A map layer config can only point at a URL, and there is no endpoint that serves
a computed raster, so the classified grid is vectorized: each connected run of
equal class becomes one polygon carrying a `peligro` attribute. Guatemala comes
to roughly 600 polygons at the default gates, Antigua and Barbuda to about 3,400,
and Moroni -- one commune rather than a country -- to about 150.

Being a dynamic map_layer, `fetch_features` re-runs whenever a bound variable
input changes, so wiring the four gates to variable inputs makes the
classification interactive.
"""

from functools import lru_cache

import rasterio
from rasterio.features import shapes
from rasterio.warp import transform_geom
from tethysapp.tethysdash.plugin_helpers import (
    LayerConfigurationBuilder,
    TethysDashPlugin,
)

from tgf_wmo_plugins.classification import (
    LEVELS,
    NODATA,
    PROB_URLS,
    ThresholdGates,
    clasificar_peligro,
)
from tgf_wmo_plugins.strings import STRINGS, threshold_args

# Vectorizing a heavily fragmented classification could produce a huge payload.
# Warn loudly rather than silently shipping megabytes of geometry.
POLYGON_WARN_LIMIT = 20000

# Display name of each country, for the plugin label. Keys match PROB_URLS.
COUNTRY_NAMES = {
    "guatemala": "Guatemala",
    "antigua_barbuda": "Antigua and Barbuda",
    "comoros": "Comores",
}

# The frontend does not bundle proj4, so OpenLayers resolves only these two.
# Guatemala's rasters are already EPSG:3857 and Antigua and Barbuda's EPSG:4326,
# so their polygons go out in the grid's own CRS. The Comoros grid is EPSG:5629
# (Moznet / UTM zone 38S), which would be read as raw map units and land nowhere
# near the Indian Ocean, so those polygons are reprojected before they are sent.
RESOLVABLE_CRS = {"EPSG:4326", "EPSG:3857"}
OUTPUT_CRS = "EPSG:4326"


@lru_cache(maxsize=16)
def _read_raster(url):
    """First band as a masked array, with the grid it sits on.

    Cached: the rasters never change between requests, only the gates do, and
    re-fetching four multi-megabyte files on every slider move is what would
    make the layer feel slow.
    """
    with rasterio.open(url) as ds:
        return ds.read(1, masked=True), ds.transform, ds.crs


class BaseHazardLayer(ThresholdGates, TethysDashPlugin):
    """One hazard layer per (country, language); subclasses set only those.

    TethysDash reads `label`, `args`, `tags` and `description` off the class
    at discovery time, not off an instance, so they cannot be computed in
    `__init__`. `__init_subclass__` fills them in from LANG and country the
    moment a subclass is defined, which is what makes a new variant three
    lines and one entry point.
    """

    LANG = None
    country = None
    type = "map_layer"
    dynamic_map_layer = True

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        s = STRINGS[cls.LANG]
        cls.args = threshold_args(cls.LANG)
        cls.group = s["group"]
        cls.tags = list(s["hazard_layer_tags"])
        cls.description = s["hazard_layer_desc"]
        # A subclass may pin its own label -- the two legacy Guatemala plugins
        # keep the "(English)" / "(Español)" they were published with.
        if "label" not in cls.__dict__:
            cls.label = (
                f"{s['hazard_layer_label']} "
                f"({COUNTRY_NAMES[cls.country]}, {s['language']})"
            )

    def run(self):
        """Configure-time scaffold: source binding, style and legend."""
        s = STRINGS[self.LANG]
        builder = LayerConfigurationBuilder(s["hazard_layer_name"], "GeoJSON")
        # received_args, not args: `self.args` is the schema, while the runtime
        # re-invocation needs the configured values, including any "${Variable}"
        # bindings to resolve later.
        builder.set_plugin_source(self.name, self.received_args)
        builder.set_style(self._style(s))
        builder.set_legend(
            {
                "title": s["hazard_legend"],
                "items": [
                    {"label": s["levels"][value], "color": color, "symbol": "square"}
                    for value, color in LEVELS
                ],
            }
        )
        return builder.build()

    def fetch_features(self):
        """Runtime features: re-run on load and on variable-input change."""
        s = STRINGS[self.LANG]
        urls = PROB_URLS[self.country]
        gates = self.gates()

        self.send_update(s["msg_reading"], percentage_complete=10)
        layers, transform, crs = self._read(urls)

        self.send_update(s["msg_classifying"], percentage_complete=50)
        peligro = clasificar_peligro(*layers, gates)

        self.send_update(s["msg_polygons"], percentage_complete=75)
        features = self._vectorize(s, peligro, transform)
        features, crs = self._to_resolvable_crs(features, crs)

        self.send_update(s["msg_done"], percentage_complete=100)
        return {
            "type": "FeatureCollection",
            "features": features,
            "crs": {"type": "name", "properties": {"name": crs}},
        }

    @staticmethod
    def _to_resolvable_crs(features, crs):
        """Reproject the polygons when the grid's CRS is one the frontend cannot read.

        A no-op for Guatemala and Antigua and Barbuda. Done on the GeoJSON
        geometries rather than on the raster so the classification still happens
        cell for cell on the model's own grid -- warping the probabilities first
        would resample them and move the class boundaries.
        """
        name = str(crs)
        if name in RESOLVABLE_CRS:
            return features, name
        for feature in features:
            feature["geometry"] = transform_geom(crs, OUTPUT_CRS, feature["geometry"])
        return features, OUTPUT_CRS

    @staticmethod
    def _read(urls):
        layers, transform, crs = [], None, None
        for url in urls:
            layer, layer_transform, layer_crs = _read_raster(url)
            layers.append(layer)
            if transform is None:
                transform, crs = layer_transform, layer_crs
        shapes_seen = {layer.shape for layer in layers}
        if len(shapes_seen) != 1:
            raise ValueError(
                f"the four probability rasters must share a grid, got {shapes_seen}"
            )
        return layers, transform, crs

    @staticmethod
    def _vectorize(s, peligro, transform):
        """One polygon per connected run of equal class.

        Normal and NoData are left out: Normal is ~90% of the grid and would
        dominate the payload while adding nothing a basemap does not show.
        """
        mask = (peligro > 0) & (peligro != NODATA)
        features = [
            {
                "type": "Feature",
                "geometry": geometry,
                "properties": {
                    "peligro": int(value),
                    "nivel": s["levels"].get(int(value), ""),
                },
            }
            for geometry, value in shapes(peligro, mask=mask, transform=transform)
        ]
        if len(features) > POLYGON_WARN_LIMIT:
            print(
                f"hazard layer: {len(features):,} polygons exceeds "
                f"{POLYGON_WARN_LIMIT:,}; the classification is heavily "
                "fragmented and the payload will be large"
            )
        return features

    @staticmethod
    def _style(s):
        """Rule-based styling keyed on the `peligro` attribute.

        The shape matters: createJsonStyleFunction reads `geometryType` (not
        `geometry`), takes the condition from `conditionField`/`conditionType`
        on the rule itself, and merges the rule's own keys as the style -- there
        is no nested `style` object, and the operator is "=" not "==". A rule in
        any other shape silently never matches, leaving every feature grey.
        """
        return {
            "default": {
                "polygon": {"fill": "#9e9e9e", "stroke": "#9e9e9e", "strokeWidth": "0"}
            },
            "rules": [
                {
                    "name": s["levels"][value],
                    "geometryType": "polygon",
                    "conditionField": "peligro",
                    "conditionType": "=",
                    "conditionValue": str(value),
                    "fill": color,
                    "stroke": color,
                    "strokeWidth": "0",
                }
                for value, color in LEVELS
            ],
        }


class HazardLayerGuatemala(BaseHazardLayer):
    LANG = "es"
    country = "guatemala"
    name = "uffis_hazard_layer_guatemala"
    label = f"{STRINGS['es']['hazard_layer_label']} (Guatemala)"


class HazardLayerAntiguaBarbuda(BaseHazardLayer):
    LANG = "en"
    country = "antigua_barbuda"
    name = "uffis_hazard_layer_antigua_barbuda"
    label = f"{STRINGS['en']['hazard_layer_label']} (Antigua and Barbuda)"


class HazardLayerComoros(BaseHazardLayer):
    LANG = "fr"
    country = "comoros"
    name = "uffis_hazard_layer_comoros"
    label = f"{STRINGS['fr']['hazard_layer_label']} (Comores)"
