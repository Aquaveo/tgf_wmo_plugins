# tgf_wmo_plugins

TethysDash visualizations for the WMO Guatemala impact-based forecasting
training, in English and Spanish.

Every plugin ships as a matched pair — `_en` and `_es`. The pair shares one
implementation and differs only in the strings it renders, so the two languages
cannot disagree about a number.

## Plugins

| entry point | type | what it shows |
|---|---|---|
| `wmo_impact_summary_en` / `_es` | table | People, buildings and roads in each hazard level |
| `wmo_hazard_layer_en` / `_es` | map_layer | Hazard classification as map polygons |
| `wmo_impact_layer_en` / `_es` | map_layer | Buildings and roads coloured by hazard level |
| `wmo_storm_card_en` / `_es` | card | Magnitude, flooded area and depth for one storm |
| `wmo_storm_impact_summary_en` / `_es` | table | People, buildings and roads by flood depth for one storm |
| `wmo_storm_impact_layer_en` / `_es` | map_layer | Buildings and roads coloured by flood depth for one storm |

The three map layers are `dynamic_map_layer`s: they re-fetch whenever a bound
variable input changes, which is what makes the thresholds and the storm slider
interactive.

### Country variants

The hazard family also ships per-country variants under the `uffis_` prefix.
Each one is a subclass that sets `LANG`, `country` and `name` and nothing
else; the country selects the data (`PROB_URLS`, `FEATURES_URLS`, `PROB_FIELDS`,
`GPKG_LAYERS`) and the language selects the strings.

| entry point | language | data |
|---|---|---|
| `uffis_impact_summary_guatemala` | es | `Guatemala_IBF/impact_features.csv` |
| `uffis_impact_layer_guatemala` | es | `Guatemala_IBF/impact_features.geojson` |
| `uffis_impact_summary_haiti` / `uffis_impact_layer_haiti` | fr | `Haiti training/outputs/impact_features.gpkg` |
| `uffis_impact_summary_antigua_barbuda` / `uffis_impact_layer_antigua_barbuda` | en | `antigua_barbuda_IBF/AntiguaBarbuda_Jerry_cycle_10151010_IBF_outputs.gpkg` |
| `uffis_hazard_layer_antigua_barbuda` | en | `antigua_barbuda_IBF/depth_prob/antiguabarbuda_prob_depth_ge_*_overbank.tif` |

Haiti and Antigua and Barbuda ship geopackages with buildings and roads as
separate layers, which are stacked into one frame with a `type` column; in
both, the buildings layer misnames its severe probability `probability_30cm`,
and `GPKG_LAYERS` renames it back before the gates apply. The Antigua and
Barbuda probability rasters are EPSG:4326 at 1 arc-second (2658×921), unlike
Guatemala's EPSG:3857 copies, and are served in that CRS since OpenLayers
resolves it natively.

## Two products, two questions

The plugins split into two families that answer different questions, and the
distinction is worth keeping straight when building a dashboard:

- **Hazard** (`impact_summary`, `hazard_layer`, `impact_layer`) works from four
  EF5 **exceedance-probability** rasters. Each hazard level has its own
  probability gate, and a feature takes the level of the deepest flood threshold
  it clears. It answers *"what are the odds of at least 30 cm here"*.
- **Storm** (`storm_card`, `storm_impact_summary`, `storm_impact_layer`) samples
  **depth** from one storm of a 200-member RainyDay ensemble. It answers
  *"in storm 150, how deep is the water on this building"*. Depth is a physical
  quantity, so the bands need no reference to a threshold.

The two datasets sit on exactly the same grid — EPSG:3857, 424×319, 5 m cells,
identical origin — so no reprojection or resampling happens anywhere.

## Dashboards

`dashboards/` holds the six ready-to-import dashboards for the training — three
exercises, each in both languages:

| file | dashboard |
|---|---|
| `Guatemala_Hands_On_1_English.json` | Guatemala Hands On 1 (English) |
| `Guatemala_Hands_On_1_Espanol.json` | Guatemala Práctica 1 (Español) |
| `Guatemala_Hands_On_2_English.json` | Guatemala Hands On 2 (English) |
| `Guatemala_Hands_On_2_Espanol.json` | Guatemala Práctica 2 (Español) |
| `Guatemala_Hands_On_3_English.json` | Guatemala Hands On 3 (English) |
| `Guatemala_Hands_On_3_Espanol.json` | Guatemala Práctica 3 (Español) |
| `Antigua_Barbuda_Hands_On_1_English.json` | Antigua and Barbuda Hands On 1 (English) |
| `Antigua_Barbuda_Hands_On_2_English.json` | Antigua and Barbuda Hands On 2 (English) |
| `Antigua_Barbuda_Hands_On_3_English.json` | Antigua and Barbuda Hands On 3 (English) |

Import them from the landing page once the plugins are installed and the server
has restarted. Exercise 1 uses no plugins at all; exercise 2 uses the storm
family; exercise 3 uses the hazard family.

The Antigua and Barbuda set follows the same three exercises on the Tropical
Storm Jerry data. Exercise 1 shows the four `depth_prob` rasters with the GADM
parish boundaries. Exercise 2 reads flood depth for one storm straight out of
the Saint John's flood-map library (`AnB_IBF/AG04_SaintJohnS_v1.zarr`, 200
storms) through a Zarr layer whose `index` is bound to a `Storm` number input;
no storm plugin exists for these libraries yet, so there is no table or card.
Exercise 3 binds the three `uffis_*_antigua_barbuda` plugins to four threshold
inputs, preset to the plugin defaults. The step-by-step guides in `docs/` are
written for Guatemala, but every step transfers with the layer names and URLs
swapped.

A dashboard is bound to the plugins of its own language, and not only through
the `source` names. A variable input that draws its options from a plugin
argument stores the string `"<group>: <label> - <Arg>"`, which embeds the
plugin's translated group and label — so the English and Spanish copies of
exercise 2 reference different option sources for the same Storm slider. Renaming
a plugin's `label` or `group` breaks that binding silently; regenerate the
dashboards rather than editing the strings by hand.

## Installing

```bash
pip install -e .
```

Then restart the Tethys server; TethysDash discovers plugins through the
`intake.drivers` entry-point group at startup.

## Adding or changing text

All user-facing text lives in `strings.py`, keyed by language. Hazard levels and
depth bands are keyed by their numeric class value — the value the raster and the
feature attributes actually carry — so a translation can never change a
classification.

`check_parity()` runs at import and raises if the two dictionaries have drifted,
so a missing translation fails at install time rather than in front of a room of
trainees.

## Data

Everything is read from a public S3 bucket; nothing is bundled.

| dataset | what it is |
|---|---|
| `floodmaps_test/` | Zarr store, 200-storm RainyDay ensemble, `depth` in metres |
| `floodmaps_test/ensemble_stats.csv` | Precomputed per-storm summary |
| `Guatemala_IBF/impact_features.geojson` | Buildings and roads with sampled probabilities |
| `Guatemala_IBF/impact_features.csv` | The same rows without geometry, for tables |
| `PBI_Actividad_2/prob_*.tif` | The four exceedance-probability rasters, EPSG:3857 |
| `PBI_Actividad_2/depth_m.tif` | Flood depth in metres, EPSG:3857, on the same grid |

Two caveats that matter when reading the output:

- **The probability layer depths are mislabelled upstream.** The filenames say
  7.62 / 10 / 30 / 76 cm, but three of the four are actually 15.24 / 30.48 /
  60.96 cm. The ordering is correct either way, so the classification is
  unaffected — but the labels are not what they claim.
- **The 76 cm layer only ever contains 0 or 0.2.** Any gate above 0.2 therefore
  makes the top hazard level unreachable, not merely rare.

The dashboards deliberately use the `PBI_Actividad_2/` copies rather than the
`Guatemala_IBF/` originals. The originals are EPSG:32615 (UTM 15N), and a UTM
raster makes the map adopt that projection through the GeoTIFF auto-fit, which
costs a reprojection on every tile. All five 3857 rasters share one grid exactly
— 424×319, 5 m cells, identical origin — which is also the grid the RainyDay
ensemble uses, so nothing is resampled at render time.

`depth_m.tif` was resampled from the UTM original with nearest neighbour rather
than bilinear: the layer is drawn with `mask_below: 0.01`, and averaging across
the dry/wet boundary inflated the flooded footprint by 16% and clipped the peak
depth. Nearest holds the footprint to 7,705 cells against the original's 7,710,
the mean to 0.9281 m against 0.9289, and the maximum exactly.

## Site

Santa Inés Petapa, Guatemala. The model domain is 3.38 km² and covers 5,029 of
the 5,147 features in the geopackage; the remaining 118 fall outside it and never
appear as affected, whatever the storm.
