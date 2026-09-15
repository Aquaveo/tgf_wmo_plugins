# Workshop notebooks

Walkthroughs of the analysis behind the hands-on dashboards, one folder per
country. They derive the same numbers the dashboard plugins produce, but as plain
code you can read and re-run, so the logic is visible rather than hidden behind a
plugin class.

| notebook | question it answers |
|---|---|
| `Guatemala/02_storm_impact[_es].ipynb` | How deep did the water get on each building and road, in one storm of the RainyDay ensemble? |
| `Guatemala/03_hazard_classification[_es].ipynb` | What are the odds of at least 30 cm here, and what does that classify as? |
| `Haiti/02_storm_impact.ipynb`, `Haiti/03_hazard_classification[_fr].ipynb` | The same two questions on the La Quinte data |
| `Antigua_Barbuda/02_storm_impact.ipynb` | In one storm of the Saint John's flood-map library, how deep is the water on each building and road — and how does a forecast turn that library into probabilities? |
| `Antigua_Barbuda/03_hazard_classification.ipynb` | What are the odds of at least 30 cm here in the Tropical Storm Jerry forecast, and which buildings, roads and parishes does that put at risk? |

`01_plugin_example[_es|_fr].ipynb`, at the top level, builds the simplest plugin
from scratch and is country-independent.

Each country notebook ends with the real plugin source and notes on how the
notebook logic maps onto it.

## Running them

All data is read over HTTPS from a public S3 bucket — nothing to download first,
but you do need a network connection, and a few cells take 10–30 seconds while
they pull rasters or a geopackage.

```bash
pip install jupyter matplotlib "zarr>=3.0" fsspec aiohttp \
            rasterio geopandas pyogrio shapely numpy pandas
jupyter lab
```

If you have already installed this package (`pip install -e .`), only `jupyter`
and `matplotlib` are missing.

The Antigua and Barbuda notebooks also run on Google Colab: their first cell
installs the packages Colab lacks (`zarr>=3`, `rasterio`, `pyogrio`) and does
nothing anywhere else.

## A note on the exercises

The notebooks are written to be re-run with different values — change the storm
index, move the thresholds — and several sections ask you to do exactly that.
The final section of each lists suggested experiments.

Things the notebooks deliberately flag rather than paper over:

- **Guatemala: the ensemble magnitudes are placeholders.** The mm labels on the
  storm picker are illustrative, not measured. `02` explains where they come from.
  The Antigua and Barbuda libraries carry real RainyDay storm totals, and their
  `02` says why that changes what you may plot against.
- **Guatemala: three of the four depth labels are wrong upstream.** The filenames
  say 7.62 / 10 / 30 / 76 cm; three are actually 15.24 / 30.48 / 60.96 cm. The
  ordering is right, so the classification is unaffected, but do not quote the
  centimetre figures. `03` covers this.
- **Antigua and Barbuda: depth saturates at 2.55 m.** The flood-map libraries
  stored depth as whole centimetres in a byte, so no band above about 2 m is
  distinct. `02` sets its top band accordingly.
- **Antigua and Barbuda: the geopackage misnames and mislabels two fields.** The
  buildings layer stores P(≥ 100 cm) as `probability_30cm`, and `wrldpp_sum`
  repeats the parish population total on every building. `03` handles the first,
  and both warn about the second. `03` also recovers the single gate behind
  the geopackage's own `hazard_flag` rather than taking the documentation's word
  for it.
- **Antigua and Barbuda: no storm plugin yet.** Section 10 of `02` explains what
  the Guatemala-bound `wmo_storm_*` family would need to serve a parish library.

Section 5 of the Guatemala `03` also works through recovering an undocumented
sampling method from the data itself, and stops at "~98% plus an open question"
rather than claiming a match it cannot support. That pattern — verify, then
report the residual honestly — is worth more than any notebook's specific numbers.
