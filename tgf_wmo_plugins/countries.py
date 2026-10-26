"""Everything that differs between countries, one `Country` record each.

The plugins are generic: they read where a country's files are, what its columns
are called, which admin unit it is cut by and where its live TITO cycles are
from here, and never branch on the country. Adding a country means adding a
record below, one subclass per plugin family it supports, and the matching entry
points in pyproject.toml.
"""

from dataclasses import dataclass
from functools import cached_property
from typing import Callable, NamedTuple

BUCKET = "https://cog-s3-test-401506828094-us-east-1-an.s3.us-east-1.amazonaws.com"

# Every country's thresholds, shallowest first -- the order the hazard levels
# escalate through. Guatemala's are named in its own record.
DEPTHS = ("10cm", "30cm", "70cm", "100cm")


class Unit(NamedTuple):
    """One admin unit. `code` is the path segment the product URLs use."""

    code: str
    name: str
    population: int
    island: str | None = None

    @property
    def pcode(self):
        return self.code.split("_")[0]


@dataclass(frozen=True)
class Units:
    """A country whose products are published one set per admin unit."""

    arg: str  # the plugin argument, in the country's language
    pcode_field: str  # the receptor column holding the unit's pcode
    default: str  # used whenever a dashboard leaves the argument unset
    table: tuple[Unit, ...]

    def __post_init__(self):
        if self.default not in self.by_code:
            raise ValueError(f"default unit {self.default} is not in the table")

    @cached_property
    def by_code(self):
        return {u.code: u for u in self.table}

    @property
    def options(self):
        """The argument's choices, in table order."""
        return [{"value": u.code, "label": u.name} for u in self.table]


@dataclass(frozen=True)
class Columns:
    """What a country's receptor file calls the fields the plugins read."""

    type: str = "type"
    building: str = "building"  # the `type` value marking a building
    population: str = "population_per_building"
    area: str = "building_area_m2"
    length: str = "road_length_m"

    @property
    def measures(self):
        return [self.population, self.area, self.length]


@dataclass(frozen=True)
class Receptors:
    """Buildings and roads carrying their sampled exceedance probabilities.

    `layers` is None for a flat file (GeoJSON, with `table_url` the same rows as
    CSV), or maps each `type` value to its geopackage layer and the column
    renames that layer needs.
    """

    url: Callable[[str | None], str] | None  # None when found per cycle (live)
    probabilities: tuple[str, str, str, str]  # shallowest threshold first
    columns: Columns = Columns()
    layers: dict[str, tuple[str, dict[str, str]]] | None = None
    table_url: str | None = None
    prob_scale: float = 1.0  # puts the probabilities on the 0-1 scale


@dataclass(frozen=True)
class Storms:
    """A flood-map library of storms, one Zarr store per unit or per country."""

    store_url: Callable[[str | None], str]
    options: list[dict]
    default_index: int
    # True when per-storm figures come from an ensemble_stats.csv beside the
    # store rather than from the storm's own chunk.
    precomputed_stats: bool = False


# Every TITO receptor geopackage shares one layout.
LIVE_RECEPTORS = Receptors(
    url=None,
    layers={"building": ("buildings_ibf", {}), "road": ("roads_ibf", {})},
    probabilities=tuple(f"p_ge_{depth}" for depth in DEPTHS),
)

# The probability raster variants TITO can publish. The receptors' own
# probabilities are sampled from the first one a country publishes, so that is
# the default.
ALL_VARIANTS = (
    "combined_overbank",
    "combined",
    "pluvial_overbank",
    "pluvial",
    "fluvial_overbank",
    "fluvial",
)
PLUVIAL_VARIANTS = ("pluvial_overbank", "pluvial")


@dataclass(frozen=True)
class Live:
    """Where a country's hourly TITO cycles are, under tito.uffis.org/outputs.

    A site is TITO's modelling domain. `raster_site` and `ibf_site` map the
    plugin's scope -- the admin unit, or the `site_choices` entry when the sites
    are not admin units -- onto the site whose products to read; a None raster
    site reads the national mosaic instead.
    """

    slug: str
    grid: str
    variants: tuple[str, ...]
    raster_site: Callable[[str | None], str | None]
    ibf_site: Callable[[str | None], str]
    site_arg: str | None = None
    site_choices: tuple[tuple[str, str], ...] = ()
    receptors: Receptors = LIVE_RECEPTORS
    # River gauges with forecast hydrographs, as (TITO id, label), and the grid
    # whose members to plot.
    gauges: tuple[tuple[str, str], ...] = ()
    gauge_grid: str | None = None
    # Grids with ensemble rainfall summaries, as (TITO grid, label).
    rain_grids: tuple[tuple[str, str], ...] = ()

    def __post_init__(self):
        if bool(self.site_arg) != bool(self.site_choices):
            raise ValueError(f"{self.slug}: site_arg and site_choices go together")

    def prob_paths(self, scope, variant, cycle):
        """The four exceedance rasters, relative to the cycle."""
        site = self.raster_site(scope)
        base = f"{self.grid}/fim/stream_sat_stormlab"
        if site is not None:
            base = f"{base}/{site}"
        suffix = "_overbank" if variant.endswith("_overbank") else ""
        return [
            f"{base}/{variant}/prob_depth_ge_{depth}{suffix}.{cycle}.tif"
            for depth in DEPTHS
        ]

    def receptor_path(self, scope, cycle):
        return f"{self.grid}/ibf/{self.ibf_site(scope)}/ibf_receptors.{cycle}.gpkg"


@dataclass(frozen=True)
class Country:
    key: str  # entry-point suffix, e.g. "comoros"
    lang: str
    label_name: str  # shown in plugin labels, e.g. "Comores"
    receptors: Receptors
    population: int | None = None  # the whole domain, for a country without units
    prob_urls: Callable[[str | None], list[str]] | None = None
    storms: Storms | None = None
    units: Units | None = None
    live: Live | None = None

    def __post_init__(self):
        if (self.population is None) == (self.units is None):
            raise ValueError(f"{self.key}: give a population or units, not both")

    def unit_population(self, unit):
        if self.units is not None:
            return self.units.by_code[unit].population
        return self.population

    def gpkg_where(self, unit):
        """Row filter selecting `unit` in the driver, or None when unscoped."""
        if self.units is None:
            return None
        return f"{self.units.pcode_field} = '{unit.split('_')[0]}'"


# ---------------------------------------------------------------------------
# Guatemala: Santa Inés Petapa, one model domain.
# ---------------------------------------------------------------------------

GUATEMALA_STORE = f"{BUCKET}/floodmaps_test"

# Storms 0 and 1 are dry -- Zarr never wrote their chunks -- so they are not
# offered.
FIRST_WET_STORM = 2

# Placeholder magnitudes for storms 2-199, copied from ensemble_stats.csv so the
# dropdown costs no network round-trip at import. They were assigned to ranks by
# flooded area and are not measured rainfall.
GUATEMALA_MAGNITUDES_MM = [
    27.76, 29.15, 30.53, 31.91, 33.29, 34.67, 36.06, 37.44, 38.82, 40.2,
    41.58, 42.96, 44.35, 45.73, 47.11, 48.49, 49.87, 51.26, 52.64, 54.02,
    55.4, 56.78, 58.17, 59.55, 60.93, 62.31, 63.69, 65.08, 66.46, 67.84,
    69.22, 70.6, 71.98, 73.37, 74.75, 76.13, 77.51, 78.89, 80.28, 81.66,
    83.04, 84.42, 85.8, 87.19, 88.57, 89.95, 91.33, 92.71, 94.1, 95.48,
    96.86, 98.24, 99.62, 101.01, 102.39, 103.77, 105.15, 106.53, 107.91, 109.3,
    110.68, 112.06, 113.44, 114.82, 116.21, 117.59, 118.97, 120.35, 121.73, 123.12,
    124.5, 125.88, 127.26, 128.64, 130.03, 131.41, 132.79, 134.17, 135.55, 136.93,
    138.32, 139.7, 141.08, 142.46, 143.84, 145.23, 146.61, 147.99, 149.37, 150.75,
    152.14, 153.52, 154.9, 156.28, 157.66, 159.05, 160.43, 161.81, 163.19, 164.57,
    165.95, 167.34, 168.72, 170.1, 171.48, 172.86, 174.25, 175.63, 177.01, 178.39,
    179.77, 181.16, 182.54, 183.92, 185.3, 186.68, 188.07, 189.45, 190.83, 192.21,
    193.59, 194.97, 196.36, 197.74, 199.12, 200.5, 201.88, 203.27, 204.65, 206.03,
    207.41, 208.79, 210.18, 211.56, 212.94, 214.32, 215.7, 217.09, 218.47, 219.85,
    221.23, 222.61, 223.99, 225.38, 226.76, 228.14, 229.52, 230.9, 232.29, 233.67,
    235.05, 236.43, 237.81, 239.2, 240.58, 241.96, 243.34, 244.72, 246.11, 247.49,
    248.87, 250.25, 251.63, 253.02, 254.4, 255.78, 257.16, 258.54, 259.92, 261.31,
    262.69, 264.07, 265.45, 266.83, 268.22, 269.6, 270.98, 272.36, 273.74, 275.13,
    276.51, 277.89, 279.27, 280.65, 282.04, 283.42, 284.8, 286.18, 287.56, 288.94,
    290.33, 291.71, 293.09, 294.47, 295.85, 297.24, 298.62, 300,
]

GUATEMALA = Country(
    key="guatemala",
    lang="es",
    label_name="Guatemala",
    receptors=Receptors(
        url=lambda _unit: f"{BUCKET}/Guatemala_IBF/impact_features.geojson",
        table_url=f"{BUCKET}/Guatemala_IBF/impact_features.csv",
        # Named after the source files; three of the four are really
        # 15.24 / 30.48 / 60.96 cm. The ordering is right either way.
        probabilities=(
            "probability_7p62cm",
            "probability_10cm",
            "probability_30cm",
            "probability_76cm",
        ),
        columns=Columns(
            type="tipo",
            building="edificio",
            population="poblacion",
            area="area_m2",
            length="longitud_m",
        ),
    ),
    population=290868,
    # The EPSG:3857 copies rather than the UTM originals, so the map is not
    # reprojected on every tile.
    prob_urls=lambda _unit: [
        f"{BUCKET}/PBI_Actividad_2/prob_{depth}.tif"
        for depth in ("7p62", "10cm", "30cm", "76cm")
    ],
    storms=Storms(
        store_url=lambda _unit: GUATEMALA_STORE,
        options=[
            {"value": str(i), "label": f"{mm:g} mm"}
            for i, mm in enumerate(GUATEMALA_MAGNITUDES_MM, start=FIRST_WET_STORM)
        ],
        default_index=FIRST_WET_STORM,
        precomputed_stats=True,
    ),
    live=Live(
        slug="guatemala",
        grid="guatemala_90m",
        variants=ALL_VARIANTS,
        raster_site=lambda _scope: "Guatemala_SantaInesPetapa",
        ibf_site=lambda _scope: "Guatemala_SantaInesPetapa",
        # The 90 m members, which also drive the flood maps.
        rain_grids=(("guatemala_900m", "900 m (national)"), ("guatemala_90m", "90 m (flood sites)")),
        gauge_grid="guatemala_90m",
        gauges=(
            ("cuenca_villalobos_out", "Cuenca Villalobos (salida)"),
            ("cuenca_villalobos_1", "Cuenca Villalobos 1"),
            ("cuenca_villalobos_2", "Cuenca Villalobos 2"),
        ),
    ),
)

# ---------------------------------------------------------------------------
# Haiti: La Quinte. The training data is receptors only; live cycles add the
# rasters, and a second site, Gris.
# ---------------------------------------------------------------------------

HAITI = Country(
    key="haiti",
    lang="fr",
    label_name="Haiti",
    receptors=Receptors(
        url=lambda _unit: f"{BUCKET}/Haiti%20training/outputs/impact_features.gpkg",
        layers={
            "batiment": (
                "Haiti_LaQuinte_cycle_20230602_bldgs",
                {
                    # misnamed upstream
                    "probability_30cm": "probability_severe",
                    "building_area_m2": "surface_m2",
                    "population_per_building": "population",
                },
            ),
            "route": (
                "Haiti_LaQuinte_cycle_20230602_roads",
                {"road_length_m": "longueur_m"},
            ),
        },
        probabilities=(
            "probability_low",
            "probability_med",
            "probability_high",
            "probability_severe",
        ),
        columns=Columns(
            building="batiment",
            population="population",
            area="surface_m2",
            length="longueur_m",
        ),
    ),
    population=336473,
    live=Live(
        slug="haiti",
        grid="haiti_90m",
        variants=ALL_VARIANTS,
        raster_site=lambda site: site,
        ibf_site=lambda site: site,
        site_arg="site",
        site_choices=(("Haiti_LaQuinte", "La Quinte"), ("Haiti_Gris", "Gris")),
        rain_grids=(("haiti_900m", "900 m (national)"), ("haiti_90m", "90 m (flood sites)")),
        gauge_grid="haiti_90m",
        gauges=(
            ("cuenca_laquinta_1", "Cuenca Laquinta 1"),
            ("cuenca_laquinta_2", "Cuenca Laquinta 2"),
            ("cuenca_griss", "Cuenca Griss"),
        ),
    ),
)

# ---------------------------------------------------------------------------
# Antigua and Barbuda: Tropical Storm Jerry, both islands on one grid.
# ---------------------------------------------------------------------------

AB_CYCLE = "AntiguaBarbuda_Jerry_cycle_10151010"

ANTIGUA_BARBUDA = Country(
    key="antigua_barbuda",
    lang="en",
    label_name="Antigua and Barbuda",
    receptors=Receptors(
        url=lambda _unit: f"{BUCKET}/antigua_barbuda_IBF/{AB_CYCLE}_IBF_outputs.gpkg",
        layers={
            # misnamed upstream, as in Haiti
            "building": (f"{AB_CYCLE}_bldgs", {"probability_30cm": "probability_severe"}),
            "road": (f"{AB_CYCLE}_roads", {}),
        },
        probabilities=(
            "probability_low",
            "probability_med",
            "probability_high",
            "probability_severe",
        ),
    ),
    population=93839,
    # EPSG:4326, which OpenLayers resolves natively.
    prob_urls=lambda _unit: [
        f"{BUCKET}/antigua_barbuda_IBF/depth_prob/"
        f"antiguabarbuda_prob_depth_ge_{depth}_overbank.tif"
        for depth in DEPTHS
    ],
    # Rasters are published per parish only where the forecast triggered, so
    # the national mosaic is read; the receptors come as one national file.
    live=Live(
        slug="antigua",
        grid="antigua_30m",
        variants=PLUVIAL_VARIANTS,
        raster_site=lambda _scope: None,
        ibf_site=lambda _scope: "Antigua_Barbuda",
        rain_grids=(("antigua_30m", "30 m"),),
    ),
)

# ---------------------------------------------------------------------------
# Barbados: the Hurricane Tomas hindcast, worked one parish at a time.
# ---------------------------------------------------------------------------

BARBADOS_CYCLE = "20101030.000000"
BARBADOS_ROOT = f"{BUCKET}/Barbados_training/Barbados_Tomas_2010_flood_maps_for_IBF"

# Populations from ibf_island_by_parish.csv; they sum to the island's 269,090.
BARBADOS_PARISHES = (
    Unit("BB01_ChristChurch", "Christ Church", 51184),
    Unit("BB02_SaintAndrew", "Saint Andrew", 5677),
    Unit("BB03_SaintGeorge", "Saint George", 21940),
    Unit("BB04_SaintJames", "Saint James", 24819),
    Unit("BB05_SaintJohn", "Saint John", 10417),
    Unit("BB06_SaintJoseph", "Saint Joseph", 6698),
    Unit("BB07_SaintLucy", "Saint Lucy", 11136),
    Unit("BB08_SaintMichael", "Saint Michael", 77395),
    Unit("BB09_SaintPeter", "Saint Peter", 13565),
    Unit("BB10_SaintPhilip", "Saint Philip", 32129),
    Unit("BB11_SaintThomas", "Saint Thomas", 14130),
)


def _barbados_prob_urls(parish):
    """The parish's own window rather than the island mosaic: it is the rainfall
    that window was matched on. It runs past the parish edge; the receptors do
    not, since they are filtered on ADM1_PCODE."""
    name = parish.split("_", 1)[1]
    return [
        f"{BARBADOS_ROOT}/03_fim_parishes/Barbados_{name}/pluvial/"
        f"prob_depth_ge_{depth}.{BARBADOS_CYCLE}.tif"
        for depth in DEPTHS
    ]


BARBADOS = Country(
    key="barbados",
    lang="en",
    label_name="Barbados",
    receptors=Receptors(
        # The full island stock, each receptor counted once.
        url=lambda _unit: (
            f"{BARBADOS_ROOT}/04_ibf_island_deduplicated/"
            f"barbados_ibf_receptors_full.{BARBADOS_CYCLE}.gpkg"
        ),
        layers={"building": ("buildings_ibf", {}), "road": ("roads_ibf", {})},
        probabilities=tuple(f"p_ge_{depth}" for depth in DEPTHS),
    ),
    prob_urls=_barbados_prob_urls,
    storms=Storms(
        store_url=lambda parish: f"{BUCKET}/Barbados_IBF/Barbados/fim_store_{parish}_v1.zarr",
        options=[{"value": str(i), "label": str(i)} for i in range(200)],
        default_index=150,
    ),
    units=Units(
        arg="parish",
        pcode_field="ADM1_PCODE",
        # Bridgetown, and a third of the island's exposure
        default="BB08_SaintMichael",
        table=BARBADOS_PARISHES,
    ),
)

# ---------------------------------------------------------------------------
# Comoros: the 27 April 2024 cycle, one product set per ADM3 commune.
# ---------------------------------------------------------------------------

COMOROS_CYCLE = "20240427.000000"
COMOROS_ROOT = (
    f"{BUCKET}/Comoros_training/Comoros_cycle_20240427_0000UTC"
    "/Comoros_cycle_20240427_0000UTC"
)

# Static rather than read from communes_<cycle>.csv, so building the dropdown
# costs no network round-trip. Regenerate from that CSV if the cycle changes.
COMOROS_COMMUNES = (
    Unit("KM111_BambaoMtsanga", "Bambao Mtsanga", 13970, "anjouan"),
    Unit("KM112_Domoni", "Domoni", 25005, "anjouan"),
    Unit("KM113_Jimlime", "Jimlimé", 13433, "anjouan"),
    Unit("KM114_Koni", "Koni", 14203, "anjouan"),
    Unit("KM115_Ngandzale", "Ngandzalé", 9288, "anjouan"),
    Unit("KM121_Adda", "Adda", 14029, "anjouan"),
    Unit("KM122_Chaweni", "Chaweni", 6138, "anjouan"),
    Unit("KM123_Mramani", "Mramani", 10212, "anjouan"),
    Unit("KM124_Mremani", "Mrémani", 12160, "anjouan"),
    Unit("KM125_Ongojou", "Ongojou", 9739, "anjouan"),
    Unit("KM131_BandraniYaChironkamba", "Bandrani Ya Chironkamba", 12837, "anjouan"),
    Unit("KM132_BandraniYaMtsangani", "Bandrani Ya Mtsangani", 8403, "anjouan"),
    Unit("KM133_Mirontsi", "Mirontsi", 20874, "anjouan"),
    Unit("KM134_Mutsamudu", "Mutsamudu", 37426, "anjouan"),
    Unit("KM141_BambaoMtrouni", "Bambao Mtrouni", 23179, "anjouan"),
    Unit("KM142_Bazimini", "Bazimini", 17846, "anjouan"),
    Unit("KM143_Ouani", "Ouani", 28723, "anjouan"),
    Unit("KM151_Moya", "Moya", 15199, "anjouan"),
    Unit("KM152_Sima", "Sima", 22258, "anjouan"),
    Unit("KM153_Vouani", "Vouani", 12460, "anjouan"),
    Unit("KM211_Mboinkou", "Mboinkou", 7281, "grande"),
    Unit("KM212_NyumaMro", "Nyuma Mro", 8265, "grande"),
    Unit("KM213_NyumaMsiru", "Nyuma Msiru", 12244, "grande"),
    Unit("KM221_Djoumoipangua", "Djoumoipangua", 7229, "grande"),
    Unit("KM222_Tsinimoipangua", "Tsinimoipangua", 14492, "grande"),
    Unit("KM231_Bangaani", "Bangaani", 16801, "grande"),
    Unit("KM232_Djoumoichongo", "Djoumoichongo", 6777, "grande"),
    Unit("KM233_Hamanvou", "Hamanvou", 16237, "grande"),
    Unit("KM234_Isahari", "Isahari", 9848, "grande"),
    Unit("KM235_Mbadani", "Mbadani", 11953, "grande"),
    Unit("KM241_Domba", "Domba", 5933, "grande"),
    Unit("KM242_Itsahidi", "Itsahidi", 19281, "grande"),
    Unit("KM243_Pimba", "Pimba", 8604, "grande"),
    Unit("KM251_Ngouengoe", "Ngouengoe", 9684, "grande"),
    Unit("KM252_Nioumagama", "Nioumagama", 7748, "grande"),
    Unit("KM261_CembenoiLacSale", "Cembenoi Lac Salé", 6816, "grande"),
    Unit("KM262_CembenoiSadaDjoulamlima", "Cembenoi Sada Djoulamlima", 5465, "grande"),
    Unit("KM263_Mitsamiouli", "Mitsamiouli", 12361, "grande"),
    Unit("KM264_NyumaKomo", "Nyuma Komo", 5971, "grande"),
    Unit("KM265_NyumamroKiblani", "Nyumamro Kiblani", 11984, "grande"),
    Unit("KM266_NyumamroSouheili", "Nyumamro Souheili", 14465, "grande"),
    Unit("KM271_BambaoYaHari", "Bambao Ya Hari", 23640, "grande"),
    Unit("KM272_BambaoYaMboini", "Bambao Ya Mboini", 22089, "grande"),
    Unit("KM273_BambaoYadjou", "Bambao Yadjou", 16781, "grande"),
    Unit("KM274_Moroni", "Moroni", 69668, "grande"),
    Unit("KM281_Dimani", "Dimani", 9864, "grande"),
    Unit("KM282_OichiliYadjou", "Oichili Yadjou", 10138, "grande"),
    Unit("KM283_OichiliYamboini", "Oichili Yamboini", 7745, "grande"),
    Unit("KM291_CratereDuKarthala", "Cratère du Karthala", 0, "grande"),
    Unit("KM311_Djando", "Djando", 7276, "moheli"),
    Unit("KM321_Fomboni", "Fomboni", 22727, "moheli"),
    Unit("KM322_MoiliMdjini", "Moili Mdjini", 8716, "moheli"),
    Unit("KM323_Moimbassa", "Moimbassa", 4750, "moheli"),
    Unit("KM331_Mledjele", "Mlédjélé", 4891, "moheli"),
    Unit("KM332_Moimbao", "Moimbao", 3205, "moheli"),
)
_COMOROS_ISLAND = {u.code: u.island for u in COMOROS_COMMUNES}


def _comoros_prob_urls(commune):
    """EPSG:5629 at 30.57 m, windowed on the commune."""
    base = f"{COMOROS_ROOT}/fim/{commune}/stream_sat_stormlab/pluvial_overbank"
    return [
        f"{base}/prob_depth_ge_{depth}_overbank.{COMOROS_CYCLE}.tif"
        for depth in DEPTHS
    ]


COMOROS = Country(
    key="comoros",
    lang="fr",
    label_name="Comores",
    receptors=Receptors(
        # One geopackage per island; the commune is selected out of it.
        url=lambda commune: (
            f"{COMOROS_ROOT}/ibf/receptors_{_COMOROS_ISLAND[commune]}_{COMOROS_CYCLE}.gpkg"
        ),
        layers={"building": ("buildings", {}), "road": ("roads", {})},
        probabilities=tuple(f"p_ge_{depth}_pct" for depth in DEPTHS),
        prob_scale=0.01,  # stored as percent
    ),
    prob_urls=_comoros_prob_urls,
    storms=Storms(
        store_url=lambda commune: f"{BUCKET}/Comoros_IBF/Comoros/fim_store_{commune}_v1.zarr",
        options=[{"value": str(i), "label": str(i)} for i in range(200)],
        default_index=150,
    ),
    units=Units(
        arg="commune",
        pcode_field="ADM3_PCODE",
        default="KM274_Moroni",  # the capital
        table=COMOROS_COMMUNES,
    ),
    # TITO names a commune's site after it without the pcode: Comoros_Moroni.
    live=Live(
        slug="comoros",
        grid="comoros_30m",
        variants=PLUVIAL_VARIANTS,
        raster_site=lambda commune: f"Comoros_{commune.split('_', 1)[1]}",
        ibf_site=lambda commune: f"Comoros_{commune.split('_', 1)[1]}",
        rain_grids=(("comoros_30m", "30 m"),),
    ),
)

COUNTRIES = {c.key: c for c in (GUATEMALA, HAITI, ANTIGUA_BARBUDA, BARBADOS, COMOROS)}
