"""Flood hazard classification from four EF5 exceedance probabilities.

Port of `clasificar_peligro` from the UFFIS PBI Actividad 2 notebook. Each input
holds P(flood depth >= threshold) for one depth, and each hazard level has a
probability gate. A cell or feature takes the level of the DEEPEST threshold
whose gate it clears, which falls out of assigning the levels in ascending order
and letting later assignments win.
"""

import numpy as np

from tgf_wmo_plugins.strings import THRESHOLD_ARGS, threshold_args

# Class value and colour, shallow to deep. Display names are in strings.py.
LEVELS = [
    (1, "green"),
    (2, "yellow"),
    (3, "red"),
    (4, "purple"),
]
NODATA = 255

# The notebook's defaults, keyed by class value, for any gate left unset.
DEFAULT_GATES = {1: 0.3, 2: 0.2, 3: 0.1, 4: 0.15}


class ThresholdGates:
    """The four probability gates, read from the country's language's arg names."""

    @classmethod
    def country_args(cls, country):
        return {
            **threshold_args(country.lang),
            **cls.unit_args(country),
            **cls.live_args(country),
        }

    def gates(self):
        """The four gates, keyed by hazard class value."""
        names = THRESHOLD_ARGS[self.country.lang]
        return {value: self._gate(names[value], default)
                for value, default in DEFAULT_GATES.items()}

    def _gate(self, arg, default):
        """Gates arrive from the GUI as strings."""
        try:
            return float(self.get_arg(arg, default))
        except (TypeError, ValueError):
            return default


def clasificar_peligro(prob7p62, prob10cm, prob30cm, prob76cm, umbrales_peligro):
    """Classify flood hazard from the four probability rasters.

    4 = Severo, 3 = Alto, 2 = Medio, 1 = Bajo, 0 = Normal, 255 = NoData.
    """
    layers = (prob7p62, prob10cm, prob30cm, prob76cm)
    # A pixel missing from any layer cannot be classified.
    invalid = np.logical_or.reduce([np.ma.getmaskarray(layer) for layer in layers])

    peligro = np.zeros(prob7p62.shape, dtype=np.uint8)
    for layer, (value, _color) in zip(layers, LEVELS):
        peligro[layer.filled(-np.inf) >= umbrales_peligro[value]] = value

    peligro[invalid] = NODATA
    return peligro


def classify_receptors(df, probabilities, gates):
    """Hazard class per row of `df`, from its four probability columns."""
    hazard = np.zeros(len(df), dtype=np.uint8)
    for column, (value, _color) in zip(probabilities, LEVELS):
        hazard[(df[column] >= gates[value]).to_numpy()] = value
    return hazard
