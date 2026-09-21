# Hands-on exercise guides

Step-by-step guides for building the training dashboards in TethysDash, one
folder per country. Each folder has a getting-started page (setup, data, the
motions every exercise repeats) and one guide per exercise. The finished
dashboards each guide builds are in `dashboards/<country>/`, and the notebooks
that derive the numbers behind them are in `notebooks/<country>/`.

Each country ships its dashboards in **one language only** — the language its
`uffis_*` plugins speak, since the plugin labels, table headers and feature
attributes all come from that. Guatemala is Spanish; Antigua and Barbuda,
Barbados English; Comoros French. The dashboard filenames carry no language suffix.

| country | language | start here | exercises |
|---|---|---|---|
| Guatemala | English | [getting_started_en.rst](Guatemala/getting_started_en.rst) | [1](Guatemala/exercise_1_en.rst) · [2](Guatemala/exercise_2_en.rst) · [3](Guatemala/exercise_3_en.rst) |
| Guatemala | Español | [getting_started_es.rst](Guatemala/getting_started_es.rst) | [1](Guatemala/exercise_1_es.rst) · [2](Guatemala/exercise_2_es.rst) · [3](Guatemala/exercise_3_es.rst) |
| Antigua and Barbuda | English | [getting_started.rst](Antigua_Barbuda/getting_started.rst) | [1](Antigua_Barbuda/exercise_1.rst) · [2](Antigua_Barbuda/exercise_2.rst) · [3](Antigua_Barbuda/exercise_3.rst) |
| Comoros | Français | _(to write)_ | [1](Comoros/exercise_1.rst) · [2](Comoros/exercise_2.rst) · [3](Comoros/exercise_3.rst) |
| Barbados | English | _(to write)_ | [1](Barbados/exercise_1.rst) · [2](Barbados/exercise_2.rst) · [3](Barbados/exercise_3.rst) |

The three exercises follow the same arc in every country: a map of raster
layers, one storm sliced out of a Zarr store by a variable input, and a hazard
classification driven by four adjustable probability thresholds through the
`uffis_*` plugins. What changes is the data and what it can show.

| | Guatemala | Antigua and Barbuda | Comoros | Barbados |
|---|---|---|---|---|
| language | Español | English | Français | English |
| site | Santa Inés Petapa, one 3.4 km² model domain | both islands, warnings issued by parish | 55 ADM3 communes, one product set each | the whole island, 11 parishes mosaicked onto one grid |
| event | a RainyDay ensemble with placeholder magnitudes | the Tropical Storm Jerry forecast of October 2025, 50 members | the cycle of 27 April 2024, 50 members | the Hurricane Tomas hindcast of 30 October 2010, 50 members |
| rasters | EPSG:3857 copies of UTM originals, 5 m cells | EPSG:4326 at 1 arc-second, no reprojection needed | EPSG:5629 at 30.57 m, the island model's own grid | EPSG:4326 at 1 arc-second, one island mosaic |
| depth thresholds | 7.6 / 10 / 30 / 76 cm (three mislabelled upstream) | 10 / 30 / 70 / 100 cm | 10 / 30 / 70 / 100 cm | 10 / 30 / 70 / 100 cm |
| exercise 1 | one depth GeoTIFF plus the probabilities | one storm of the Saint John's flood-map library plus the probabilities | the four probabilities, with a commune selector and a probability mask | the four probabilities with a probability mask; no selector, the grid is island-wide |
| exercise 2 | depth, impact layer, table and card for one storm | depth for one storm of the Saint John's flood-map library, chosen by number; no storm plugin yet | depth, impact layer, table and card for one storm of the commune's library | depth for one storm of a parish library, parish and storm both selectable; no storm plugin |
| exercise 3 | Severe level unreachable above a gate of 0.2 | every level reachable; probabilities step by 0.02 | every level reachable; the commune is a fifth plugin argument | every level reachable; the parish is a fifth plugin argument; buildings analysed as footprints, drawn as points |

Screenshots live in each country's `images/` folder. The five `00-*` captures
of the generic dialogs are the same in both.
