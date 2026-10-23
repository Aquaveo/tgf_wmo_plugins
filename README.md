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
| Guatemala | es | ✓ | ✓ (one national library) | — | ✓ |
| Haiti | fr | ✓ (hazard layer live only) | — | — | ✓, `site` La Quinte or Gris |
| Antigua and Barbuda | en | ✓ | — | — | ✓ |
| Barbados | en | ✓ | ✓ (one library per parish) | `parish` | — |
| Comoros | fr | ✓ | ✓ (one library per commune) | `commune` | ✓ |

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

## Two products, two questions

- **Hazard** (`hazard_layer`, `impact_summary`, `impact_layer`) works from four
  EF5 **exceedance-probability** rasters. Each hazard level has its own
  probability gate, and a feature takes the level of the deepest flood threshold
  it clears. It answers *"what are the odds of at least 30 cm here"*.
- **Storm** (`storm_card`, `storm_impact_summary`, `storm_impact_layer`) samples
  **depth** from one storm of a 200-storm flood-map library. It answers
  *"in storm 150, how deep is the water on this building"*. Depth is a physical
  quantity, so the bands need no reference to a threshold.

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
