"""Shared flood hazard classification from four EF5 exceedance-probability rasters.

Port of `clasificar_peligro` from the UFFIS PBI Actividad 2 notebook. Each input
raster holds P(flood depth >= threshold) for one depth, and each hazard level has
a probability gate. A pixel takes the level of the DEEPEST threshold whose gate it
clears, which falls out of assigning the levels in ascending order and letting
later assignments win -- exactly as the notebook does it.

Note on the inputs: the layer names below follow the notebook (7.62 / 10 / 30 /
76 cm), but three of the source files are actually 15.24 / 30.48 / 60.96 cm
(6/12/24 inch) thresholds. The naming was inherited from upstream; the ordering
is correct either way, so the classification is unaffected.

This module holds no plugin of its own. The hazard classification is surfaced
as a map layer (`hazard_layer`) and as an exposure table (`impact_summary`);
a heatmap of the classified grid used to live here too, but it duplicated the
map layer's computation without adding anything the map does not show better.
"""

from functools import lru_cache

import numpy as np
import rasterio

from tgf_wmo_plugins.common import COMOROS_CYCLE, COMOROS_ROOT, COMOROS_UNIT
from tgf_wmo_plugins.strings import THRESHOLD_ARGS

BUCKET = "https://cog-s3-test-401506828094-us-east-1-an.s3.us-east-1.amazonaws.com"

# The four rasters the classification is defined over, per country, shallowest
# threshold first -- the order LEVELS escalates through. Fixed rather than
# exposed as args: the gates are the only thing worth varying, and four URL
# boxes in the editor invite mismatched or misordered grids.
#
# Guatemala's depth labels come from the source filenames and are wrong -- three
# of the four are 15.24/30.48/60.96 cm, not 7.62/10/30 cm. Kept as-is so the
# names still match the data everyone else refers to.
#
# Antigua and Barbuda's rasters are EPSG:4326 (unlike Guatemala's EPSG:3857
# copies), which OpenLayers also resolves without proj4, so they are read as-is.
PROB_URLS = {
    "guatemala": [
        f"{BUCKET}/PBI_Actividad_2/prob_{depth}.tif"
        for depth in ("7p62", "10cm", "30cm", "76cm")
    ],
    "antigua_barbuda": [
        f"{BUCKET}/antigua_barbuda_IBF/depth_prob/"
        f"antiguabarbuda_prob_depth_ge_{depth}_overbank.tif"
        for depth in ("10cm", "30cm", "70cm", "100cm")
    ],
}


def comoros_prob_urls(unit=COMOROS_UNIT):
    """The four exceedance rasters for one Comorian commune.

    Comoros cannot join PROB_URLS above: its products are written one set per
    ADM3 commune, so there is no single list of four to name. The plugins pick a
    commune at request time and call this instead.

    EPSG:5629 (Moznet / UTM zone 38S) at 30.57 m -- the island model's own grid
    rather than a reprojected copy -- and windowed on the commune, so 169 x 198
    cells for Moroni rather than a national extent.
    """
    base = f"{COMOROS_ROOT}/fim/{unit}/stream_sat_stormlab/pluvial_overbank"
    return [
        f"{base}/prob_depth_ge_{depth}_overbank.{COMOROS_CYCLE}.tif"
        for depth in ("10cm", "30cm", "70cm", "100cm")
    ]


class ComorosUnit:
    """Reads the commune argument the per-commune Comoros products need.

    Mixed into every Comoros plugin that reads a commune-scoped product, beside
    ThresholdGates, so the argument name is declared in exactly one place. Like
    the gates, it is read at request time rather than baked into the class.
    """

    def unit(self):
        return self.get_arg("commune", COMOROS_UNIT)

# Level -> (class value, display label, colour). Ordered shallow to deep, which
# is also the order the notebook assigns them in.
# Value and colour only; the display name is per language, in strings.py.
LEVELS = [
    (1, "green"),
    (2, "yellow"),
    (3, "red"),
    (4, "purple"),
]
NODATA = 255

# The notebook's defaults, one gate per hazard level, keyed by class value. Used
# whenever a dashboard leaves a threshold unset.
DEFAULT_GATES = {1: 0.3, 2: 0.2, 3: 0.1, 4: 0.15}


class ThresholdGates:
    """Reads the four probability gates from a plugin's own argument names.

    The English and Spanish variants of a plugin take differently named
    arguments (`low_threshold` vs `umbral_bajo`), so the names cannot be
    hard-coded by the plugin that reads them -- they are looked up from
    THRESHOLD_ARGS by the subclass's LANG. Mixed in by every plugin that gates
    on probability, which is how those three stay in step with each other.
    """

    def gates(self):
        """The four gates, keyed by hazard class value."""
        names = THRESHOLD_ARGS[self.LANG]
        return {
            value: self._gate(names[value], DEFAULT_GATES[value])
            for value in sorted(DEFAULT_GATES)
        }

    def _gate(self, arg, default):
        """Gates arrive from the GUI as strings."""
        try:
            return float(self.get_arg(arg, default))
        except (TypeError, ValueError):
            return default


@lru_cache(maxsize=16)
def _read_masked(url):
    """First band of a raster as a masked array. Cached: the four inputs do not
    change between requests, only the thresholds do."""
    with rasterio.open(url) as ds:
        return ds.read(1, masked=True)


def clasificar_peligro(prob7p62, prob10cm, prob30cm, prob76cm, umbrales_peligro):
    """Classify flood hazard from the four probability layers.

    4 = Severo, 3 = Alto, 2 = Medio, 1 = Bajo, 0 = Normal, 255 = NoData.
    """
    # A pixel missing from any layer cannot be classified.
    invalid = (
        np.ma.getmaskarray(prob7p62)
        | np.ma.getmaskarray(prob10cm)
        | np.ma.getmaskarray(prob30cm)
        | np.ma.getmaskarray(prob76cm)
    )

    peligro = np.zeros(prob7p62.shape, dtype=np.uint8)

    # Ascending order: each assignment overwrites the last, so the deepest
    # threshold that clears its gate is the one that sticks.
    layers = (prob7p62, prob10cm, prob30cm, prob76cm)
    # Gates arrive keyed by level value, not by name, so the classification is
    # identical in both languages.
    for layer, (value, _color) in zip(layers, LEVELS):
        peligro[layer.filled(-np.inf) >= umbrales_peligro[value]] = value

    peligro[invalid] = NODATA
    return peligro
