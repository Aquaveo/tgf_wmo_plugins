# Screenshots for the Comoros exercise guides

Every `figure` block in the guides points at a file in this folder. None of them
exist yet — drop a PNG at the given name and it renders with no other change.
The caption under each `figure` in the `.rst` says what the image should show;
this table is the checklist.

Capture at a window wide enough that the data viewer's right-hand preview is
visible, and crop to the dialog rather than the whole screen.

## Generic dialogs (`00-*`)

These five are the same in every country. The quickest way to fill them is to
copy the files of the same name from `../../Guatemala/images/` — nothing in them
is country-specific.

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
| `ex1-finished.png` | the finished dashboard, layer control open so all four layers are visible, with all three controls across the top |
| `ex1-variable-input-basemap.png` | the **Variable Input** arguments for the base map selector |
| `ex1-variable-input-commune.png` | the **Variable Input** arguments for the commune selector: `variable_options_source` `dropdown`, choices editor open |
| `ex1-variable-input-mask.png` | the **Variable Input** arguments for the probability mask: `variable_options_source` `number`, initial value 0 |
| `ex1-map-args.png` | the **Map** arguments, **Base Map** bound to `${Base Map}` and **Layer Control** on |
| `ex1-layer-source-geotiff.png` | the **Source** tab: **GeoTIFF**, one probability URL, `mask_below` bound to `${Probability Mask}` |
| `ex1-layer-style-turbo.png` | the **Style** tab: **Continuous**, **turbo**, **Min** 0, **Max** 1 |
| `ex1-layer-list.png` | the **Layers** list with all four layers, deepest first |
| `ex1-settings-fill-viewport.png` | the **Settings** tab with **Fill Viewport** on |

**Before capturing anything**, note the warning at the top of `exercise_1.rst`:
the Comoros rasters are EPSG:5629, and until that code is registered in
`reactapp/components/map/projections.js` the layers will not place. Screenshots
of the dialogs can be taken regardless; `ex1-finished.png` and
`ex1-layer-list.png` cannot, because they show the rendered map.
