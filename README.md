# tgf_wmo_plugins

TethysDash visualizations for the WMO impact-based flood forecasting trainings
in Guatemala, Haiti, Antigua and Barbuda, Barbados and Comoros.

The repository has three parts besides the plugins: `docs/` holds the
step-by-step guides for building the hands-on dashboards, `dashboards/` the
finished dashboards those guides build, and `notebooks/` the analysis behind
them as plain Python. All three are organised by country; start at
[`docs/README.md`](docs/README.md).

## Plugins

Each plugin family has one implementation. Each country gets a one-line
subclass per family its data supports, registered as `uffis_<family>_<country>`.

| family | type | what it shows |
|---|---|---|
| `hazard_layer` | map_layer | Hazard classification as map polygons |
| `impact_summary` | table | People, buildings and roads in each hazard level |
| `impact_layer` | map_layer | Buildings and roads coloured by hazard level |
| `storm_card` | card | Magnitude, flooded area and depth for one storm |
| `storm_impact_summary` | table | People, buildings and roads by flood depth for one storm |
| `storm_impact_layer` | map_layer | Buildings and roads coloured by flood depth for one storm |

| country | language | hazard family | storm family | unit argument | live TITO data |
|---|---|---|---|---|---|
| Guatemala | es | ✓ | ✓ live | — | ✓ |
| Haiti | fr | ✓ (hazard layer live only) | ✓ live | — | ✓, `site` La Quinte or Gris |
| Antigua and Barbuda | en | ✓ | ✓ live | — | ✓ |
| Barbados | en | ✓ | ✓ training library, per parish | `parish` | — |
| Comoros | fr | ✓ | ✓ live (no receptors published) | `commune` | ✓ |

The map layers are `dynamic_map_layer`s: they re-fetch whenever a bound
variable input changes, which is what makes the thresholds and the storm slider
interactive.

## Live data

The hazard family reads the hourly cycles TITO publishes at
`https://tito.uffis.org/outputs/<country>/<cycle>/`, for every country that has
a `live` entry in `countries.py`. Three arguments control it, named in the
country's language:

- `cycle` / `ciclo`: `latest` (also what an unset argument means), `training`
  for the static training data the exercises use, or a cycle stamp such as
  `20261023.170000`. Bind it to a `uffis_cycle_times_<country>` variable input
  to get a dropdown of every cycle still published, about a day's worth.
- `flood_source` / `fuente_inundacion` / `source_inondation` (hazard layer
  only): which probability rasters to classify -- pluvial, fluvial or combined,
  overbank or not. The default is the variant TITO samples the receptors from
  (`combined_overbank`, or `pluvial_overbank` where only pluvial is modelled),
  so the map and the impact figures agree unless another is chosen.
- `site` (Haiti only): La Quinte or Gris.

TITO only maps floods, and only assesses impact, where the forecast triggers.
A quiet site has no rasters or receptors in that cycle, and the plugins say so
-- an empty layer with a message, a table of zeros -- rather than failing.
Comoros publishes no receptors yet, so its impact plugins are always empty on
live cycles. A live population share is of the people in the site's receptor
file, which carries no separate census total.

Two more live plugins take the same `cycle` binding:

- `uffis_precip_layer_guatemala`: ensemble rainfall accumulation (forecast or
  nowcast; median, minimum or maximum) on the 900 m or 90 m grid, as a dynamic
  GeoTIFF layer coloured with the tito.uffis.org rainfall classes.
- `uffis_discharge_<country>` (Guatemala, Haiti): the forecast hydrograph at a
  river gauge in the style of the tito.uffis.org viewer -- for each rainfall
  forcing, the range of its members as a shaded band and their median as a
  line, with each median's peak listed underneath. The forcings cover
  different windows (satellite rainfall the hours before the cycle, the
  StormLab forecast the ~30 h after it, the SCaMPR nowcast both), and the
  cycle start is marked. Antigua's one gauge is a placeholder that never
  flows, and Comoros has none, so neither has the plot.

## Warnings (SFFS/FGS risk matrix)

Four live plugins per TITO country follow the Scottish Flood Forecasting
Service and Flood Guidance Statement standard (Speight et al., 2018), as the
[AHWA IBF viewer](https://ahwalab.github.io/ibf_viz/guatemala/) does:

- `uffis_risk_matrix_<country>`: the likelihood × severity matrix, the four
  warning colours and the cycle's overall warning (the highest district level).
- `uffis_risk_filter_<country>`: a dropdown -- All, Yellow and up, Amber and
  up, Red only -- for the layer below.
- `uffis_risk_layer_<country>`: buildings and roads coloured VERY LOW to HIGH.
  "All" means every feature with a reportable probability (P(≥ 0.1 m) ≥ 5%);
  the never-wet rest of the stock is left out, since it runs to a third of a
  million features in Haiti Gris.
- `uffis_event_summary_<country>`: buildings, road km and districts at each
  warning level, and the population in buildings at yellow or worse.

A feature's warning is the highest the matrix gives across its P(≥ 0.1 m),
P(≥ 0.3 m) and P(≥ 0.7 m) -- Minor, Significant and Severe -- with likelihood
bands at 20 / 40 / 60 % and probabilities under 5 % ignored. This reproduces
the `risk_class` TITO writes on every feature, and the counts match its
`ibf_summary.json`. District warnings are TITO's own, since its district rule
counts properties per district. These plugins sit beside the threshold-based
hazard and impact plugins, which are unchanged.

## Two products, two questions

- **Hazard** (`hazard_layer`, `impact_summary`, `impact_layer`) works from four
  EF5 **exceedance-probability** rasters. Each hazard level has its own
  probability gate, and a feature takes the level of the deepest flood threshold
  it clears. It answers *"what are the odds of at least 30 cm here"*.
- **Storm** (`storm_card`, `storm_impact_summary`, `storm_impact_layer`)
  answers *"how deep is the water likely to get on this building"*. For every
  country TITO runs, it reads the live cycle: a feature's likely depth is the
  deepest of 10 / 30 / 70 / 100 cm it reaches with at least the chosen
  probability (`min_probability` / `probabilidad_minima` /
  `probabilite_minimale`, default 0.5), and the card adds the trigger status,
  forecast rainfall, the area likely to flood and the *expected* people and
  buildings with at least 0.3 m (each feature counted by its probability).
  TITO's live flood-map libraries are not published -- the copies in the S3
  bucket do not reproduce its forecasts -- so the depth of the storm a member
  matched cannot be shown. Barbados, which TITO does not run, keeps the
  training version: depth sampled from one storm of a 200-storm library,
  chosen by `index`.

## Adding a country

Everything that differs between countries lives in
[`countries.py`](tgf_wmo_plugins/countries.py), one `Country` record each:

- `receptors`: where the buildings and roads are, what their probability and
  measure columns are called, and any per-layer renames;
- `prob_urls`: the four exceedance rasters, if the hazard family applies;
- `storms`: the Zarr flood-map library, if the storm family applies;
- `units`: the admin unit the products are published by, if any. This adds a
  dropdown argument to every plugin and scopes the receptors, rasters, store
  and population share to the chosen unit;
- `live`: the country's TITO slug, grid, raster variants and how its plugin
  scope maps onto TITO site names, if TITO runs there. This adds the live
  arguments above and a `uffis_cycle_times_<key>` input.

Then add a subclass per supported family, which only sets `country`:

```python
class HazardLayerNewCountry(BaseHazardLayer):
    country = NEW_COUNTRY
```

Finally, add the matching `uffis_<family>_<key>` entry points to
`pyproject.toml` and reinstall. `tests/test_countries.py` fails if an entry
point is missing for a family the data supports, or present for one it
doesn't. A new language also needs its strings in `strings.py`.

## Dashboards

`dashboards/<country>/` holds the ready-to-import solution to each of the three
hands-on exercises, whose guides live in `docs/<country>/`. Import them from the
landing page once the plugins are installed and the server has restarted.
Exercise 1 uses no plugins, exercise 2 uses the storm family and exercise 3 the
hazard family.

Each TITO country also has a live dashboard, with a cycle dropdown driving
every panel:

| file | language |
|---|---|
| `Guatemala/Guatemala_Hands_On_2_English.json` | English (plugin text in Spanish) |
| `Haiti/Haiti_Live.json` | French, with a La Quinte / Gris site selector |
| `Antigua_Barbuda/Antigua_Barbuda_Live.json` | English |
| `Comoros/Comoros_Live.json` | French, with a commune selector |

The first tab has rainfall, hazard and likely flood depth on the map, the
forecast card and the depth and hazard tables (and the discharge forecast
where there are gauges); the second has the SFFS/FGS warnings. Antigua's gauge
is a placeholder and Comoros has none, so neither shows discharge, and TITO
publishes no Comoros buildings, so its impact panels stay empty.

Antigua and Barbuda has no storm plugins, so its exercise 2 binds a `Storm`
number input straight to a Zarr layer on the Saint John's flood-map library.
`Antigua_Barbuda_Hands_On_3_Depth.json` is exercise 3 with that depth layer
added beneath the buildings and roads at risk.

A dashboard binds to its plugins by more than the `source` name. A variable
input that draws its options from a plugin argument stores the string
`"<group>: <label> - <Arg>"`, which embeds the plugin's translated group and
label. Renaming a plugin's `label`, `group` or arguments therefore breaks saved
dashboards silently; `tests/plugin_metadata.json` pins them all.

## Installing

```bash
pip install -e .
pytest
```

Then restart the Tethys server; TethysDash discovers plugins through the
`intake.drivers` entry-point group at startup.

## Adding or changing text

All user-facing text lives in `strings.py`, keyed by language. Hazard levels and
depth bands are keyed by their numeric class value, the value the raster and
the feature attributes actually carry, so a translation can never change a
classification. `check_parity()` runs at import and raises if the language
dictionaries have drifted.

## Data

Everything is read from a public S3 bucket; nothing is bundled. The URLs are in
`countries.py`.

Caveats worth knowing when reading the output:

- **Guatemala's probability layers are mislabelled upstream.** The filenames say
  7.62 / 10 / 30 / 76 cm, but three of the four are actually 15.24 / 30.48 /
  60.96 cm. The ordering is correct either way, so the classification is
  unaffected.
- **Guatemala's 76 cm layer only ever contains 0 or 0.2.** Any gate above 0.2
  makes the top hazard level unreachable, not merely rare.
- **Guatemala's storm magnitudes are placeholders**, assigned to the storms by
  rank of flooded area rather than measured.
- **Haiti and Antigua and Barbuda's building layers misname their severe
  probability `probability_30cm`**; their `Receptors.layers` renames it back.
- **Comoros stores probabilities as percent**; `prob_scale` converts them to
  fractions before the gates apply.
- **Not every Comoros commune has a Zarr store yet.** A missing store surfaces
  as an error naming its URL.
