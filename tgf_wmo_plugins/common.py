"""Shared helpers for the flood-map visualizations.

The ensemble summary (one row per storm) is precomputed and stored beside the Zarr
store, because computing it live means reading every storm's depth array -- about
108 MB. Only the per-storm depth histogram touches the arrays themselves, and it
reads a single chunk.
"""

import os
import tempfile
import time
import urllib.request
from functools import lru_cache
from pathlib import Path

import pandas as pd

BUCKET = "https://cog-s3-test-401506828094-us-east-1-an.s3.us-east-1.amazonaws.com"
DEFAULT_STORE = f"{BUCKET}/floodmaps_test"
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


class ZarrStoreError(Exception):
    """A Zarr store could not be opened."""


def _retry(fn, attempts=3, base_delay=0.25):
    """Call `fn`, retrying on any exception with linear backoff.

    A store is read live over HTTPS, so a single range read fails transiently now
    and then -- a dropped connection, a 5xx from the bucket. Re-issuing it beats
    failing the whole request.
    """
    for attempt in range(attempts):
        try:
            return fn()
        except Exception:
            if attempt == attempts - 1:
                raise
            time.sleep(base_delay * (attempt + 1))


@lru_cache(maxsize=64)
def open_zarr_store(store_url):
    """Open the Zarr group at `store_url` (a public https URL) read-only.

    This used to delegate to `tethysapp.tethysdash.zarr_utils.open_store`. That
    module was a server-side Zarr-to-COG converter and was removed once the
    frontend began rendering Zarr directly, so the opener lives here now.

    fsspec rather than s3fs on purpose: the stores are public, and s3fs would
    drag in an AWS stack and expect credentials that are not needed to read them.

    zarr is imported inside the function because most of this package's plugins
    never touch a store -- only the storm family does -- and importing it at
    module scope would cost every one of them the load.
    """
    import zarr
    from zarr.storage import FsspecStore

    try:
        return _retry(
            lambda: zarr.open_group(FsspecStore.from_url(store_url), mode="r")
        )
    except Exception as exc:  # noqa: BLE001 - surfaced to the dashboard as-is
        raise ZarrStoreError(
            f"could not open zarr store {store_url}: {exc}"
        ) from exc


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

# Barbados ships one forecast cycle -- Hurricane Tomas, 30 October 2010 -- with
# the eleven parish products mosaicked onto a single island grid, so the
# threshold plugins need no parish argument the way Comoros needs a commune. The
# Zarr flood-map libraries are still per parish, which is why BARBADOS_PARISHES
# exists below.
BARBADOS_CYCLE = "20101030.000000"
BARBADOS_ROOT = (
    f"{BUCKET}/Barbados_training/Barbados_Tomas_2010_flood_maps_for_IBF"
)
# Buildings and roads with each receptor counted once, island wide -- the full
# stock, as polygon footprints, not the yellow-or-worse subset published beside
# it. Regenerated by re-running the IBF pipeline over all eleven parishes and
# deduplicating on each parish's own ADM1_PCODE, which reproduces the published
# per-parish counts exactly and restores the 176,984 VERY LOW buildings that
# the severity filter dropped: 204,727 buildings and 22,509 road segments.
BARBADOS_FEATURES_URL = (
    f"{BARBADOS_ROOT}/04_ibf_island_deduplicated/"
    f"barbados_ibf_receptors_full.{BARBADOS_CYCLE}.gpkg"
)

# (path segment, display name, population), in pcode order. Population is the
# parish figure from ibf_island_by_parish.csv; they sum to the island's 269,090.
BARBADOS_PARISHES = [
    ("BB01_ChristChurch", "Christ Church", 51184),
    ("BB02_SaintAndrew", "Saint Andrew", 5677),
    ("BB03_SaintGeorge", "Saint George", 21940),
    ("BB04_SaintJames", "Saint James", 24819),
    ("BB05_SaintJohn", "Saint John", 10417),
    ("BB06_SaintJoseph", "Saint Joseph", 6698),
    ("BB07_SaintLucy", "Saint Lucy", 11136),
    ("BB08_SaintMichael", "Saint Michael", 77395),
    ("BB09_SaintPeter", "Saint Peter", 13565),
    ("BB10_SaintPhilip", "Saint Philip", 32129),
    ("BB11_SaintThomas", "Saint Thomas", 14130),
]
BARBADOS_PARISH_OPTIONS = [
    {"value": seg, "label": name} for seg, name, _pop in BARBADOS_PARISHES
]
BARBADOS_PARISH_POPULATION = {seg: pop for seg, _name, pop in BARBADOS_PARISHES}
# Saint Michael whenever a dashboard leaves the parish unset: it holds Bridgetown
# and a third of the island's exposure, so it is the one parish where an unset
# argument still shows something worth looking at.
BARBADOS_PARISH = "BB08_SaintMichael"


def barbados_store_url(parish):
    """The Zarr flood-map library for one parish. All eleven are published."""
    return f"{BUCKET}/Barbados_IBF/Barbados/fim_store_{parish}_v1.zarr"


# Comoros writes one product set per ADM3 commune rather than one national grid,
# so a unit has to be pinned before any path resolves. That is the same shape as
# Guatemala (one municipality) and Haiti (one commune), not Antigua and Barbuda
# (the whole country). Moroni is the capital, and its pcode prefix also decides
# which island file carries its receptors.
COMOROS_CYCLE = "20240427.000000"
COMOROS_UNIT = "KM274_Moroni"
COMOROS_PCODE = COMOROS_UNIT.split("_")[0]
COMOROS_ISLAND = "grande"
COMOROS_ROOT = (
    f"{BUCKET}/Comoros_training/Comoros_cycle_20240427_0000UTC"
    "/Comoros_cycle_20240427_0000UTC"
)
# One geopackage per island: it carries all 29 communes of Grande Comore, and the
# Moroni rows are a subset selected by GPKG_WHERE below.
COMOROS_FEATURES_URL = (
    f"{COMOROS_ROOT}/ibf/receptors_{COMOROS_ISLAND}_{COMOROS_CYCLE}.gpkg"
)

# Every ADM3 commune the cycle publishes, as (path segment, display name, island,
# population). The segment is what appears in a product URL; the island decides
# which receptor geopackage carries the commune; the population is the
# denominator for that commune's exposure share.
#
# Static rather than read from communes_<cycle>.csv, so building a dropdown costs
# no network round-trip at import -- the same reason STORM_MAGNITUDES_MM above is
# a literal. Regenerate from that CSV if the cycle changes.
COMOROS_UNITS = [
    ("KM111_BambaoMtsanga", "Bambao Mtsanga", "anjouan", 13970),
    ("KM112_Domoni", "Domoni", "anjouan", 25005),
    ("KM113_Jimlime", "Jimlimé", "anjouan", 13433),
    ("KM114_Koni", "Koni", "anjouan", 14203),
    ("KM115_Ngandzale", "Ngandzalé", "anjouan", 9288),
    ("KM121_Adda", "Adda", "anjouan", 14029),
    ("KM122_Chaweni", "Chaweni", "anjouan", 6138),
    ("KM123_Mramani", "Mramani", "anjouan", 10212),
    ("KM124_Mremani", "Mrémani", "anjouan", 12160),
    ("KM125_Ongojou", "Ongojou", "anjouan", 9739),
    ("KM131_BandraniYaChironkamba", "Bandrani Ya Chironkamba", "anjouan", 12837),
    ("KM132_BandraniYaMtsangani", "Bandrani Ya Mtsangani", "anjouan", 8403),
    ("KM133_Mirontsi", "Mirontsi", "anjouan", 20874),
    ("KM134_Mutsamudu", "Mutsamudu", "anjouan", 37426),
    ("KM141_BambaoMtrouni", "Bambao Mtrouni", "anjouan", 23179),
    ("KM142_Bazimini", "Bazimini", "anjouan", 17846),
    ("KM143_Ouani", "Ouani", "anjouan", 28723),
    ("KM151_Moya", "Moya", "anjouan", 15199),
    ("KM152_Sima", "Sima", "anjouan", 22258),
    ("KM153_Vouani", "Vouani", "anjouan", 12460),
    ("KM211_Mboinkou", "Mboinkou", "grande", 7281),
    ("KM212_NyumaMro", "Nyuma Mro", "grande", 8265),
    ("KM213_NyumaMsiru", "Nyuma Msiru", "grande", 12244),
    ("KM221_Djoumoipangua", "Djoumoipangua", "grande", 7229),
    ("KM222_Tsinimoipangua", "Tsinimoipangua", "grande", 14492),
    ("KM231_Bangaani", "Bangaani", "grande", 16801),
    ("KM232_Djoumoichongo", "Djoumoichongo", "grande", 6777),
    ("KM233_Hamanvou", "Hamanvou", "grande", 16237),
    ("KM234_Isahari", "Isahari", "grande", 9848),
    ("KM235_Mbadani", "Mbadani", "grande", 11953),
    ("KM241_Domba", "Domba", "grande", 5933),
    ("KM242_Itsahidi", "Itsahidi", "grande", 19281),
    ("KM243_Pimba", "Pimba", "grande", 8604),
    ("KM251_Ngouengoe", "Ngouengoe", "grande", 9684),
    ("KM252_Nioumagama", "Nioumagama", "grande", 7748),
    ("KM261_CembenoiLacSale", "Cembenoi Lac Salé", "grande", 6816),
    ("KM262_CembenoiSadaDjoulamlima", "Cembenoi Sada Djoulamlima", "grande", 5465),
    ("KM263_Mitsamiouli", "Mitsamiouli", "grande", 12361),
    ("KM264_NyumaKomo", "Nyuma Komo", "grande", 5971),
    ("KM265_NyumamroKiblani", "Nyumamro Kiblani", "grande", 11984),
    ("KM266_NyumamroSouheili", "Nyumamro Souheili", "grande", 14465),
    ("KM271_BambaoYaHari", "Bambao Ya Hari", "grande", 23640),
    ("KM272_BambaoYaMboini", "Bambao Ya Mboini", "grande", 22089),
    ("KM273_BambaoYadjou", "Bambao Yadjou", "grande", 16781),
    ("KM274_Moroni", "Moroni", "grande", 69668),
    ("KM281_Dimani", "Dimani", "grande", 9864),
    ("KM282_OichiliYadjou", "Oichili Yadjou", "grande", 10138),
    ("KM283_OichiliYamboini", "Oichili Yamboini", "grande", 7745),
    ("KM291_CratereDuKarthala", "Cratère du Karthala", "grande", 0),
    ("KM311_Djando", "Djando", "moheli", 7276),
    ("KM321_Fomboni", "Fomboni", "moheli", 22727),
    ("KM322_MoiliMdjini", "Moili Mdjini", "moheli", 8716),
    ("KM323_Moimbassa", "Moimbassa", "moheli", 4750),
    ("KM331_Mledjele", "Mlédjélé", "moheli", 4891),
    ("KM332_Moimbao", "Moimbao", "moheli", 3205),
]

COMOROS_UNIT_NAME = {seg: name for seg, name, _isl, _pop in COMOROS_UNITS}
COMOROS_UNIT_ISLAND = {seg: isl for seg, _name, isl, _pop in COMOROS_UNITS}
COMOROS_UNIT_POPULATION = {seg: pop for seg, _name, _isl, pop in COMOROS_UNITS}

# Commune choices for a plugin `args` entry, in pcode order so the three islands
# group together.
COMOROS_UNIT_OPTIONS = [
    {"value": seg, "label": name} for seg, name, _isl, _pop in COMOROS_UNITS
]


# Every position in a unit's library, as a plugin `args` dropdown. Comoros and
# Barbados both hold 200 scenarios per unit, sorted by magnitude.
#
# The label is the position itself, not a rainfall total. Guatemala labels its
# storms in millimetres because one national store serves the whole dashboard,
# but a Comoros magnitude is the area-weighted mean rain over one commune, so the
# same position is 346 mm in Cembenoi Lac Salé and 462 mm in Moimbassa -- a third
# apart, and no single number is right for all 55. What is the same everywhere is
# the ordering: every store holds 200 scenarios sorted by magnitude, so a higher
# position is a wetter storm in every commune. The storm card reports the actual
# millimetres once a commune has been chosen.
#
# The driest few positions are a commune's permanent standing water rather than a
# storm, so they are offered but will look almost dry -- which is the honest thing
# for them to look like.
UNIT_STORM_COUNT = 200
UNIT_STORM_OPTIONS = [
    {"value": str(i), "label": str(i)} for i in range(UNIT_STORM_COUNT)
]


def comoros_store_url(unit):
    """The Zarr flood-map library for one commune.

    Not every commune has one yet: the stores were still uploading when these
    plugins were written, and only KM251 onward were in place. A missing store
    surfaces as a read error naming the URL, which is the actionable thing.
    """
    return f"{BUCKET}/Comoros_IBF/Comoros/fim_store_{unit}_v1.zarr"


def comoros_receptors_url(unit):
    """The receptor geopackage for the island `unit` sits on."""
    island = COMOROS_UNIT_ISLAND[unit]
    return f"{COMOROS_ROOT}/ibf/receptors_{island}_{COMOROS_CYCLE}.gpkg"

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
    "comoros": [
        "probability_low",
        "probability_med",
        "probability_high",
        "probability_severe",
    ],
    "barbados": [
        "probability_low",
        "probability_med",
        "probability_high",
        "probability_severe",
    ],
}
TYPE_FIELD = {
    "guatemala": "tipo",
    "haiti": "type",
    "antigua_barbuda": "type",
    "comoros": "type",
    "barbados": "type",
}

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

# Comoros names its four exceedance columns after the depth rather than the hazard
# level, and both layers spell them the same way, so one rename dict serves both.
# The measures already carry the names the plugins read, as for Antigua and
# Barbuda, so nothing else is renamed.
KM_PROB_RENAMES = {
    "p_ge_10cm_pct": "probability_low",
    "p_ge_30cm_pct": "probability_med",
    "p_ge_70cm_pct": "probability_high",
    "p_ge_100cm_pct": "probability_severe",
}
KM_LAYERS = {
    "building": ("buildings", KM_PROB_RENAMES),
    "road": ("roads", KM_PROB_RENAMES),
}

# Barbados names its exceedance columns after the depth, like Comoros, but
# stores them as fractions already -- so the renames are all that is needed, and
# PROB_SCALE has no Barbados entry.
BB_PROB_RENAMES = {
    "p_ge_10cm": "probability_low",
    "p_ge_30cm": "probability_med",
    "p_ge_70cm": "probability_high",
    "p_ge_100cm": "probability_severe",
}
BB_LAYERS = {
    "building": ("buildings_ibf", BB_PROB_RENAMES),
    "road": ("roads_ibf", BB_PROB_RENAMES),
}

# Geopackage layout per country, for the readers that stack buildings and
# roads into one frame. Guatemala is absent: it ships a flat GeoJSON/CSV.
GPKG_LAYERS = {
    "haiti": HAITI_LAYERS,
    "antigua_barbuda": AB_LAYERS,
    "comoros": KM_LAYERS,
    "barbados": BB_LAYERS,
}

# The countries whose products are published one set per admin unit rather than
# one per country, and the column each one's receptors carry the unit code in.
# Comoros is scoped because its geopackage is per island; Barbados because its
# file is the whole island and the exercises work a parish at a time.
UNIT_PCODE_FIELD = {"comoros": "ADM3_PCODE", "barbados": "ADM1_PCODE"}
UNIT_DEFAULT = {"comoros": COMOROS_UNIT, "barbados": BARBADOS_PARISH}
UNIT_POPULATION = {
    "comoros": COMOROS_UNIT_POPULATION,
    "barbados": BARBADOS_PARISH_POPULATION,
}


def gpkg_where(country, unit=None):
    """Row filter for a country's geopackage read, or None for no filter.

    Both scoped countries keep every unit in one file, so the unit is selected in
    the driver rather than afterwards -- that keeps the other 110,000 (Comoros)
    or 165,000 (Barbados) geometries from ever being built. The unit code is the
    segment before the underscore of the argument value, so `BB08_SaintMichael`
    filters on `BB08`.
    """
    field = UNIT_PCODE_FIELD.get(country)
    if field is None:
        return None
    pcode = (unit or UNIT_DEFAULT[country]).split("_")[0]
    return f"{field} = '{pcode}'"

# Factor that puts a country's probability columns on the 0-1 scale the gates
# assume. Only Comoros stores them as percent; left unscaled, a gate of 0.8 is
# cleared by anything above 0.8 PERCENT and roughly eight times too many features
# land in a hazard level. Normalising in the reader rather than in the classifier
# keeps the unit from reaching gates() and DEFAULT_GATES, which every country
# shares.
PROB_SCALE = {"comoros": 0.01}


def scale_probabilities(df, country):
    """Put `country`'s probability columns on the fraction scale, in place."""
    scale = PROB_SCALE.get(country)
    if scale is not None:
        df[PROB_FIELDS[country]] = df[PROB_FIELDS[country]] * scale
    return df

# Population across every building in the country's geopackage, so exposure can
# be given as a share. Guatemala from notebooks/precompute_impact_table.py;
# Haiti summed the same way over the `population_per_building` field.
# Comoros is Moroni's own population, matching the commune GPKG_WHERE selects.
# Grande Comore is 379,364 and the country 758,311; widening the filter without
# widening this measures the share against the wrong denominator.
TOTAL_POPULATION = {
    "guatemala": 290868,
    "haiti": 336473,
    "antigua_barbuda": 93839,
    "comoros": 69668,
    # The whole island, and the receptor file now covers it, so this also equals
    # the sum of its per-parish populations.
    "barbados": 269090,
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
