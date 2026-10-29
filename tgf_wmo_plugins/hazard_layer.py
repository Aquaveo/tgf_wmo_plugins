"""Flood hazard classification as a dynamic map layer.

A map layer config can only point at a URL, and there is no endpoint that serves
a computed raster, so the classified grid is vectorized: each connected run of
equal class becomes one polygon carrying the hazard-class attribute. Being a
dynamic map_layer, `fetch_features` re-runs whenever a bound variable input
changes, which is what makes the gates interactive.
"""

from functools import lru_cache

import rasterio
from rasterio.features import shapes
from rasterio.warp import transform_geom
from tethysapp.tethysdash.plugin_helpers import LayerConfigurationBuilder

from tgf_wmo_plugins.base import CountryPlugin, LiveData
from tgf_wmo_plugins.classification import (
    LEVELS,
    NODATA,
    ThresholdGates,
    clasificar_peligro,
)
from tgf_wmo_plugins.countries import (
    ANTIGUA_BARBUDA,
    BARBADOS,
    COMOROS,
    GUATEMALA,
    HAITI,
)
from tgf_wmo_plugins.receptors import OUTPUT_CRS
from tgf_wmo_plugins.tito import TRAINING, cycle_files, file_url

# Warn rather than silently ship megabytes of geometry from a fragmented grid.
POLYGON_WARN_LIMIT = 20000

# CRSs OpenLayers resolves without proj4. A grid in any other (Comoros is
# EPSG:5629) has its polygons reprojected on the way out.
RESOLVABLE_CRS = {"EPSG:4326", "EPSG:3857"}


@lru_cache(maxsize=16)
def _read_raster(url):
    """First band as a masked array, with its grid. Cached: only the gates change
    between requests."""
    # Without these GDAL probes for .aux.xml/.ovr sidecars over HTTP, which
    # costs seconds per file.
    with rasterio.Env(
        GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR", CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif"
    ):
        with rasterio.open(url) as ds:
            return ds.read(1, masked=True), ds.transform, ds.crs


class BaseHazardLayer(ThresholdGates, LiveData, CountryPlugin):
    family = "hazard_layer"
    strings_key = "hazard_layer"
    type = "map_layer"
    dynamic_map_layer = True
    uses_rasters = True

    @classmethod
    def has_training(cls, country):
        return country.prob_urls is not None

    def prob_urls(self):
        """The four rasters to classify, or None when the cycle has none for
        this scope -- TITO maps floods only where the forecast triggers."""
        cycle, scope = self.selected_cycle(), self.scope()
        if cycle == TRAINING:
            return self.country.prob_urls(scope)
        live = self.country.live
        paths = live.prob_paths(scope, self.variant(), cycle)
        if not set(paths) <= cycle_files(live.slug, cycle):
            return None
        return [file_url(live.slug, cycle, path) for path in paths]

    def run(self):
        """Configure-time scaffold: source binding, style and legend."""
        s = self.strings
        builder = LayerConfigurationBuilder(s["hazard_layer_name"], "GeoJSON")
        # received_args, not args: the runtime re-invocation needs the configured
        # values, including any "${Variable}" bindings still to resolve.
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
        s = self.strings
        gates = self.gates()

        self.send_update(s["msg_reading"], percentage_complete=10)
        urls = self.prob_urls()
        if urls is None:
            message = s["msg_not_triggered"].format(site=self.scope_label(), cycle=self.selected_cycle())
            self.send_update(message, percentage_complete=100)
            return {
                "type": "FeatureCollection",
                "features": [],
                "crs": {"type": "name", "properties": {"name": OUTPUT_CRS}},
            }
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
        """Reproject the polygons, not the rasters, so the classification still
        happens cell for cell on the model's own grid."""
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

        Normal and NoData are left out: Normal is ~90% of the grid and adds
        nothing a basemap does not show.
        """
        mask = (peligro > 0) & (peligro != NODATA)
        features = [
            {
                "type": "Feature",
                "geometry": geometry,
                "properties": {
                    s["attr_hazard"]: int(value),
                    s["attr_level"]: s["levels"].get(int(value), ""),
                },
            }
            for geometry, value in shapes(peligro, mask=mask, transform=transform)
        ]
        if len(features) > POLYGON_WARN_LIMIT:
            print(
                f"hazard layer: {len(features):,} polygons exceeds "
                f"{POLYGON_WARN_LIMIT:,}; the payload will be large"
            )
        return features

    @staticmethod
    def _style(s):
        """Rule-based styling keyed on the hazard-class attribute.

        createJsonStyleFunction wants `geometryType`, the condition keys on the
        rule itself, the style keys merged in flat and "=" rather than "==". A
        rule in any other shape silently never matches.
        """
        return {
            "default": {
                "polygon": {"fill": "#9e9e9e", "stroke": "#9e9e9e", "strokeWidth": "0"}
            },
            "rules": [
                {
                    "name": s["levels"][value],
                    "geometryType": "polygon",
                    "conditionField": s["attr_hazard"],
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
    country = GUATEMALA


class HazardLayerHaiti(BaseHazardLayer):
    country = HAITI


class HazardLayerAntiguaBarbuda(BaseHazardLayer):
    country = ANTIGUA_BARBUDA


class HazardLayerBarbados(BaseHazardLayer):
    country = BARBADOS


class HazardLayerComoros(BaseHazardLayer):
    country = COMOROS
