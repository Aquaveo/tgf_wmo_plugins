# Hands-on exercise guides

Step-by-step guides for building the training dashboards in TethysDash, one
folder per country. Each folder has a getting-started page (setup, data, the
motions every exercise repeats) and one guide per exercise. The finished
dashboards each guide builds are in `dashboards/<country>/`, and the notebooks
that derive the numbers behind them are in `notebooks/<country>/`.

| country | language | start here | exercises |
|---|---|---|---|
| Guatemala | English | [getting_started_en.rst](Guatemala/getting_started_en.rst) | [1](Guatemala/exercise_1_en.rst) · [2](Guatemala/exercise_2_en.rst) · [3](Guatemala/exercise_3_en.rst) |
| Guatemala | Español | [getting_started_es.rst](Guatemala/getting_started_es.rst) | [1](Guatemala/exercise_1_es.rst) · [2](Guatemala/exercise_2_es.rst) · [3](Guatemala/exercise_3_es.rst) |
| Antigua and Barbuda | English | [getting_started.rst](Antigua_Barbuda/getting_started.rst) | [1](Antigua_Barbuda/exercise_1.rst) · [2](Antigua_Barbuda/exercise_2.rst) · [3](Antigua_Barbuda/exercise_3.rst) |

The three exercises follow the same arc in every country: a map of raster
layers, one storm sliced out of a Zarr store by a variable input, and a hazard
classification driven by four adjustable probability thresholds through the
`uffis_*` plugins. What changes is the data and what it can show.

| | Guatemala | Antigua and Barbuda |
|---|---|---|
| site | Santa Inés Petapa, one 3.4 km² model domain | both islands, warnings issued by parish |
| event | a RainyDay ensemble with placeholder magnitudes | the Tropical Storm Jerry forecast of October 2025, 50 members |
| rasters | EPSG:3857 copies of UTM originals, 5 m cells | EPSG:4326 at 1 arc-second, no reprojection needed |
| depth thresholds | 7.6 / 10 / 30 / 76 cm (three mislabelled upstream) | 10 / 30 / 70 / 100 cm |
| exercise 1 | one depth GeoTIFF plus the probabilities | one storm of the Saint John's flood-map library plus the probabilities |
| exercise 2 | depth, impact layer, table and card for one storm | depth for one storm of the Saint John's flood-map library, chosen by number; no storm plugin yet |
| exercise 3 | Severe level unreachable above a gate of 0.2 | every level reachable; probabilities step by 0.02 |

Screenshots live in each country's `images/` folder. The Guatemala guides have
theirs; the Antigua and Barbuda `figure` blocks name what each capture should
show and render once a PNG is dropped at the given path.
