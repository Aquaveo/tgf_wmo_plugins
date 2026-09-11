"""Shared helpers for the flood-map visualizations.

The ensemble summary (one row per storm) is precomputed and stored beside the Zarr
store, because computing it live means reading every storm's depth array -- about
108 MB. Only the per-storm depth histogram touches the arrays themselves, and it
reads a single chunk.
"""

import os
import tempfile
import urllib.request
from pathlib import Path

import pandas as pd

DEFAULT_STORE = (
    "https://cog-s3-test-401506828094-us-east-1-an.s3.us-east-1.amazonaws.com/"
    "floodmaps_test"
)
STATS_FILE = "ensemble_stats.csv"

# Storms 0 and 1 are dry -- Zarr never wrote their chunks, since it omits
# fill-value chunks -- so offering them would only produce empty panels. Listing
# the rest as explicit choices makes the arg a dropdown, which still carries a
# "Variable Inputs" group at the bottom for binding to a slider.
FIRST_WET_STORM = 2
STORM_COUNT = 200
STORM_INDICES = [str(i) for i in range(FIRST_WET_STORM, STORM_COUNT)]

# Magnitude of each wet storm, in the same order, copied from ensemble_stats.csv
# so building the dropdown costs no network round-trip at import. Values are
# unique and monotonic, so a magnitude identifies a storm on its own.
#
# These are PLACEHOLDERS: the ensemble was sorted by flooded area and magnitudes
# assigned to the ranks, so they are not measured rainfall. The store says as
# much, and floodmaps_store_info surfaces the caveat on the dashboard. If real
# RainyDay 24-hour totals ever land, regenerate this list from the summary.
STORM_MAGNITUDES_MM = [
    27.76,
    29.15,
    30.53,
    31.91,
    33.29,
    34.67,
    36.06,
    37.44,
    38.82,
    40.2,
    41.58,
    42.96,
    44.35,
    45.73,
    47.11,
    48.49,
    49.87,
    51.26,
    52.64,
    54.02,
    55.4,
    56.78,
    58.17,
    59.55,
    60.93,
    62.31,
    63.69,
    65.08,
    66.46,
    67.84,
    69.22,
    70.6,
    71.98,
    73.37,
    74.75,
    76.13,
    77.51,
    78.89,
    80.28,
    81.66,
    83.04,
    84.42,
    85.8,
    87.19,
    88.57,
    89.95,
    91.33,
    92.71,
    94.1,
    95.48,
    96.86,
    98.24,
    99.62,
    101.01,
    102.39,
    103.77,
    105.15,
    106.53,
    107.91,
    109.3,
    110.68,
    112.06,
    113.44,
    114.82,
    116.21,
    117.59,
    118.97,
    120.35,
    121.73,
    123.12,
    124.5,
    125.88,
    127.26,
    128.64,
    130.03,
    131.41,
    132.79,
    134.17,
    135.55,
    136.93,
    138.32,
    139.7,
    141.08,
    142.46,
    143.84,
    145.23,
    146.61,
    147.99,
    149.37,
    150.75,
    152.14,
    153.52,
    154.9,
    156.28,
    157.66,
    159.05,
    160.43,
    161.81,
    163.19,
    164.57,
    165.95,
    167.34,
    168.72,
    170.1,
    171.48,
    172.86,
    174.25,
    175.63,
    177.01,
    178.39,
    179.77,
    181.16,
    182.54,
    183.92,
    185.3,
    186.68,
    188.07,
    189.45,
    190.83,
    192.21,
    193.59,
    194.97,
    196.36,
    197.74,
    199.12,
    200.5,
    201.88,
    203.27,
    204.65,
    206.03,
    207.41,
    208.79,
    210.18,
    211.56,
    212.94,
    214.32,
    215.7,
    217.09,
    218.47,
    219.85,
    221.23,
    222.61,
    223.99,
    225.38,
    226.76,
    228.14,
    229.52,
    230.9,
    232.29,
    233.67,
    235.05,
    236.43,
    237.81,
    239.2,
    240.58,
    241.96,
    243.34,
    244.72,
    246.11,
    247.49,
    248.87,
    250.25,
    251.63,
    253.02,
    254.4,
    255.78,
    257.16,
    258.54,
    259.92,
    261.31,
    262.69,
    264.07,
    265.45,
    266.83,
    268.22,
    269.6,
    270.98,
    272.36,
    273.74,
    275.13,
    276.51,
    277.89,
    279.27,
    280.65,
    282.04,
    283.42,
    284.8,
    286.18,
    287.56,
    288.94,
    290.33,
    291.71,
    293.09,
    294.47,
    295.85,
    297.24,
    298.62,
    300,
]
assert len(STORM_MAGNITUDES_MM) == len(STORM_INDICES)

# The `index` arg's choices: index as the stored value, magnitude as the label.
STORM_OPTIONS = [
    {"value": index, "label": f"{magnitude:g} mm"}
    for index, magnitude in zip(STORM_INDICES, STORM_MAGNITUDES_MM)
]


def stats_url(store_url):
    """URL of the precomputed summary that sits beside the store."""
    return f"{store_url.rstrip('/')}/{STATS_FILE}"


def load_stats(store_url):
    """The precomputed per-storm summary as a DataFrame, indexed by storm_index.

    Raises a plain ValueError with an actionable message when the file is absent,
    since that means the precompute step has not been run for this store.
    """
    url = stats_url(store_url)
    try:
        return pd.read_csv(url).set_index("storm_index", drop=False)
    except Exception as exc:  # noqa: BLE001 - surfaced to the dashboard as-is
        raise ValueError(
            f"could not read {url} -- run the ensemble precompute for this store "
            f"and upload {STATS_FILE} beside it ({exc})"
        ) from exc


def open_zarr_store(store_url):
    """Open the Zarr group read-only.

    Reuses the app's own opener, which retries transient range-read failures and
    normalizes errors. It is deliberately Django-free, so importing it here does
    not drag in app state.
    """
    from tethysapp.tethysdash.zarr_utils import open_store

    return open_store(store_url)


def coerce_index(value, default=0):
    """Slider values arrive as strings; treat anything unusable as the default."""
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def storm_row(stats, index):
    """The summary row for one storm, or None when the index is out of range."""
    if index in stats.index:
        return stats.loc[index]
    return None


# Buildings and roads with their sampled flood probabilities. The GeoJSON keeps
# geometry for map layers; the CSV is the same rows without it, for tables.
FEATURES_URL = (
    "https://cog-s3-test-401506828094-us-east-1-an.s3.us-east-1.amazonaws.com/"
    "Guatemala_IBF/impact_features.geojson"
)

GUATEMALA_FEATURES_CSV_URL = (
    "https://cog-s3-test-401506828094-us-east-1-an.s3.us-east-1.amazonaws.com/"
    "Guatemala_IBF/impact_features.csv"
)

HAITI_FEATURES_CSV_URL = (
    "https://cog-s3-test-401506828094-us-east-1-an.s3.us-east-1.amazonaws.com/"
    "Haiti%20training/outputs/impact_features.gpkg"
)

ANTIGUA_BARBUDA_FEATURES_CSV_URL = (
    "https://cog-s3-test-401506828094-us-east-1-an.s3.us-east-1.amazonaws.com/"
    "antigua_barbuda_IBF/AntiguaBarbuda_Jerry_cycle_10151010_IBF_outputs.gpkg"
)

# Layer feeding each hazard level, shallowest first -- the pairing the notebook
# uses, and the order the escalation depends on.
PROB_FIELDS = {
    "guatemala": [
        "probability_7p62cm",
        "probability_10cm",
        "probability_30cm",
        "probability_76cm",
    ],
    "haiti": [
        "probability_low",
        "probability_med",
        "probability_high",
        "probability_severe",
    ],
    "antigua_barbuda": [
        "probability_low",
        "probability_med",
        "probability_high",
        "probability_severe",
    ],
}
TYPE_FIELD = {"guatemala": "tipo", "haiti": "type", "antigua_barbuda": "type"}

HAITI_LAYERS = {
    "batiment": (
        "Haiti_LaQuinte_cycle_20230602_bldgs",
        {
            "probability_30cm": "probability_severe",
            "building_area_m2": "surface_m2",
            "population_per_building": "population",
        },
    ),
    "route": (
        "Haiti_LaQuinte_cycle_20230602_roads",
        {
            "road_length_m": "longueur_m",
        },
    ),
}

# The type keys must match what the readers compare against ("building" for
# the summary's building count), and the buildings layer misnames its severe
# probability `probability_30cm`, like Haiti's. The measures already carry the
# names the plugins read (`population_per_building`, `building_area_m2`,
# `road_length_m`), so nothing else is renamed.
AB_LAYERS = {
    "building": (
        "AntiguaBarbuda_Jerry_cycle_10151010_bldgs",
        {
            "probability_30cm": "probability_severe",
        },
    ),
    "road": ("AntiguaBarbuda_Jerry_cycle_10151010_roads", {}),
}

# Geopackage layout per country, for the readers that stack buildings and
# roads into one frame. Guatemala is absent: it ships a flat GeoJSON/CSV.
GPKG_LAYERS = {"haiti": HAITI_LAYERS, "antigua_barbuda": AB_LAYERS}

# Population across every building in the country's geopackage, so exposure can
# be given as a share. Guatemala from notebooks/precompute_impact_table.py;
# Haiti summed the same way over the `population_per_building` field.
TOTAL_POPULATION = {
    "guatemala": 290868,
    "haiti": 336473,
    "antigua_barbuda": 93839,
}


def cached_download(url):
    """Fetch `url` into the temp dir once and return the local path.

    Reading a geopackage straight off https goes through GDAL's /vsicurl, which
    range-requests the whole 56 MB file once per layer: minutes against about
    12 s for a single download.

    The transfer lands on a staging name and is moved into place only once it is
    complete. Downloading onto `path` directly publishes the name the moment the
    transfer starts, and the plugins sharing a dashboard read concurrently: the
    second one opens a half-written geopackage and GDAL reports "database disk
    image is malformed". A transfer that died midway left that truncated file
    cached for good, so every later request failed the same way.
    """
    path = Path(tempfile.gettempdir()) / url.rsplit("/", 1)[-1]
    if not path.exists():
        fd, staged = tempfile.mkstemp(
            dir=path.parent, prefix=f"{path.name}.", suffix=".part"
        )
        os.close(fd)
        try:
            urllib.request.urlretrieve(url, staged)
            os.replace(staged, path)
        finally:
            Path(staged).unlink(missing_ok=True)
    return path
