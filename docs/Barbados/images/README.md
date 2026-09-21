# Screenshots for the Barbados exercise guides

Every `figure` block in the guides points at a file in this folder. None exist
yet — drop a PNG at the given name and it renders with no other change. The
caption under each `figure` in the `.rst` says what the image should show; this
table is the checklist.

## Generic dialogs (`00-*`)

The same in every country. Copy them from `../../Guatemala/images/` — nothing in
them is country-specific.

| file | shows |
|---|---|
| `00-landing-page.png` | the landing page, with the **Create a New Dashboard** card |
| `00-new-dashboard-modal.png` | the new-dashboard modal, Name and Description filled in |
| `00-edit-mode-toolbar.png` | the header toolbar in edit mode |
| `00-dataviewer.png` | the data viewer with the **Visualization Type** dropdown open |
| `00-griditem-menu.png` | an item's 3-dot menu: Edit, Copy, Order, Export, Delete |

## Exercise 1

| file | shows |
|---|---|
| `ex1-finished.png` | the finished dashboard, layer control open, both controls along the top |
| `ex1-variable-input-basemap.png` | the **Variable Input** arguments for the base map selector |
| `ex1-variable-input-mask.png` | the **Variable Input** arguments for the probability mask |
| `ex1-map-args.png` | the **Map** arguments, **Base Map** bound and **Layer Control** on |
| `ex1-layer-source-geotiff.png` | the **Source** tab: **GeoTIFF**, one probability URL, `mask_below` bound to `${Probability Mask}` |
| `ex1-layer-style-turbo.png` | the **Style** tab: **turbo**, **Min** 0, **Max** 1 |
| `ex1-layer-list.png` | the **Layers** list with all four layers, deepest first |
| `ex1-settings-fill-viewport.png` | the **Settings** tab with **Fill Viewport** on |

## Exercise 2

| file | shows |
|---|---|
| `ex2-finished.png` | the finished dashboard, depth for storm 150 in Saint Michael |
| `ex2-parish-input.png` | the **Variable Input** arguments for the parish selector, choices editor open |
| `ex2-storm-input.png` | the **Variable Input** arguments for the storm selector |
| `ex2-zarr-source.png` | the **Source** tab: **Zarr**, store URL carrying `${Parish}`, `variable` depth, `index` `${Storm}`, `mask_below` 0.05 |
| `ex2-dynamic-layer-source.png` | the **Source** tab with **Storm Impact Layer (Barbados)** selected, `parish` and `index` bound, and **Fetch plugin defaults** |
| `ex2-table-card.png` | the summary table and card for one scenario |

## Exercise 3

| file | shows |
|---|---|
| `ex3-finished.png` | the finished dashboard: full-window map, four threshold inputs, impact table right |
| `ex3-threshold-inputs.png` | the four threshold inputs side by side |
| `ex3-hazard-layer-source.png` | the **Source** tab for the hazard layer, four gates bound |
| `ex3-impact-summary.png` | the impact summary table arguments bound to the four thresholds |
| `ex3-thresholds-before.png` | the view before lowering the Low threshold |
| `ex3-thresholds-after.png` | the same view after lowering it |

Barbados is EPSG:4326 throughout, so unlike the Comoros guides there is no
projection caveat blocking any of these captures.
