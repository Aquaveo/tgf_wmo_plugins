"""The storm family on live TITO cycles: flood depth by probability.

TITO's live flood-map libraries are not published, so the depth of the storm a
forecast member matched cannot be read. What a cycle does publish, for every
building and road, is the probability of the water reaching 10, 30, 70 and
100 cm. A feature's likely depth is the deepest of those it reaches with at
least the chosen probability, and the expected count of features reaching a
depth is the sum of their probabilities.
"""

import json
import statistics
from csv import DictReader
from io import StringIO

import numpy as np
from rasterio.crs import CRS

from tgf_wmo_plugins.base import LiveData
from tgf_wmo_plugins.strings import LIVE_ARGS
from tgf_wmo_plugins.tito import _get, cycle_files, file_url

DEFAULT_LIKELIHOOD = 0.5
# Class value and colour per depth band, shallow to deep, matching the order of
# a country's four probability columns.
LIKELY_BANDS = [(1, "green"), (2, "yellow"), (3, "red"), (4, "purple")]


def likely_band(df, probabilities, likelihood):
    """Band value per row: the deepest threshold reached with P >= likelihood."""
    band = np.zeros(len(df), dtype=np.uint8)
    for column, (value, _color) in zip(probabilities, LIKELY_BANDS):
        band[(df[column] >= likelihood).to_numpy()] = value
    return band


def cell_area_km2(transform, crs, rows):
    """One cell's true area, in a projected, Web Mercator or geographic grid."""
    crs = CRS.from_user_input(crs)
    dx, dy = abs(transform.a), abs(transform.e)
    lat_deg = transform.f + transform.e * rows / 2
    if crs.is_geographic:
        metres = 111_320.0
        return dx * metres * dy * metres * np.cos(np.radians(lat_deg)) / 1e6
    if crs.to_epsg() == 3857:
        # Web Mercator stretches lengths by 1/cos(latitude).
        lat = np.degrees(2 * np.arctan(np.exp(lat_deg / 6378137.0)) - np.pi / 2)
        return dx * dy * np.cos(np.radians(lat)) ** 2 / 1e6
    return dx * dy / 1e6


class LikelyDepth(LiveData):
    """Arguments and data shared by the live storm family."""

    @classmethod
    def has_training(cls, country):
        return False

    @classmethod
    def country_args(cls, country):
        return {
            **cls.unit_args(country),
            **cls.live_args(country),
            LIVE_ARGS[country.lang]["likelihood"]: "number",
        }

    def likelihood(self):
        """Arrives from the GUI as a string; anything unusable is the default."""
        try:
            value = float(self.get_arg(LIVE_ARGS[self.country.lang]["likelihood"]))
        except (TypeError, ValueError):
            return DEFAULT_LIKELIHOOD
        return value if 0 < value <= 1 else DEFAULT_LIKELIHOOD

    def site_file(self, cycle, name):
        """A file in the scope's TITO site folder, or None if not published."""
        live = self.country.live
        path = f"{live.grid}/fim/stream_sat_stormlab/{live.ibf_site(self.scope())}/{name}"
        if path not in cycle_files(live.slug, cycle):
            return None
        return _get(file_url(live.slug, cycle, path)).decode()

    def trigger(self, cycle):
        """The site's pf_summary trigger block, or None when there is none."""
        text = self.site_file(cycle, "pf_summary.json")
        return None if text is None else json.loads(text).get("trigger")

    def rainfall(self, cycle):
        """Median and maximum member rainfall in mm, or None when not triggered."""
        text = self.site_file(cycle, "member_decisions.csv")
        if text is None:
            return None
        totals = [float(r["total_mm"]) for r in DictReader(StringIO(text)) if r["total_mm"]]
        return (statistics.median(totals), max(totals)) if totals else None
