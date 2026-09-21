.. Comoros hands-on exercise 1 solution, English. Adapted from the Guatemala
.. guide at ../Guatemala/exercise_1_en.rst. Two things differ from that original
.. and are explained where they come up: there is no depth layer, because the
.. cycle publishes no single depth raster and one arbitrary member would not pair
.. with the four ensemble probabilities; and the rasters are EPSG:5629, which the
.. map cannot resolve until the code is registered -- see the warning below.
.. The built dashboard is dashboards/Comoros/Comoros_Hands_On_1.json.

==============================================================
Exercise 1 — A flood depth and probability map
==============================================================

Building **Comoros Hands On 1** step by step.

.. contents:: On this page
   :depth: 2
   :local:
   :backlinks: none


What you are building
=====================

One map filling the window, carrying the four exceedance-probability rasters of
the forecast cycle, and three controls across the top: a dropdown that switches
the base map underneath them, a second that picks which of the country's 55
communes to draw, and a number that sets how much probability a cell needs
before it is drawn at all. It opens on **Moroni** (KM274), the capital, on
Grande Comore.

.. figure:: images/ex1-finished.png
   :alt: The finished exercise 1 dashboard
   :width: 100%

   **Screenshot:** the finished dashboard, layer control open so all four layers
   are visible, with the two controls top-left.

This exercise is about raster layers: where the URL goes, why a probability ramp
has to be pinned rather than auto-scaled, and how a variable input can drive the
same setting on four layers at once — including one that rewrites part of each
layer's URL.

There is deliberately **no depth layer**. The cycle publishes no single depth
raster — only one per forecast member — and dropping one arbitrary member next to
four ensemble-wide probabilities would invite the reader to compare quantities
that are not comparable. Exercise 2 opens the depth library properly.

**Warning** — **The Comoros rasters are EPSG:5629 (Moznet / UTM zone 38S), and
the map cannot resolve that code yet.** OpenLayers handles EPSG:4326, EPSG:3857
and the WGS84 UTM zones on its own; anything else has to be registered, and the
table in ``reactapp/components/map/projections.js`` currently holds only
EPSG:5041 and EPSG:5070. Until ``EPSG:5629`` is added there, every layer in this
exercise will fail to place: a GeoTIFF layer loads and lands nowhere near the
Indian Ocean.
Adding it is a table entry plus a control point, as that file's own comments
describe. Nothing else in this guide changes when it is done.

**Note** — Screenshots in this guide are placeholders. Each ``figure`` block
names what the image should show; drop a PNG at the given path under
``docs/Comoros/images/`` and it will render. ``images/README.md`` lists them all.


The data
========

Everything comes from one public bucket:

.. code-block:: text

   https://cog-s3-test-401506828094-us-east-1-an.s3.us-east-1.amazonaws.com

The Comoros forecast products are written **one set per ADM3 commune**, not one
national grid, so every path below names a commune. That name is a single path
segment combining the pcode and the commune — ``KM274_Moroni`` — and swapping it
is all that separates one commune's rasters from another's. Step 2 turns that
segment into a dropdown, so the dashboard can reach all 55 without editing a URL.

.. list-table::
   :header-rows: 1
   :widths: 26 74

   * - Prefix
     - Contents
   * - ``Comoros_training/Comoros_cycle_20240427_0000UTC/``
     - The forecast cycle of 27 April 2024, and everything this exercise draws.
       ``fim/<commune>/stream_sat_stormlab/`` holds the four
       exceedance-probability rasters this exercise draws, and
       ``fim/<commune>/member_depths/`` the 50 per-member depth rasters they are
       counted from. The receptor geopackages exercise 3 reads are in ``ibf/``.
   * - ``Comoros_IBF/Comoros/``
     - The scenario stores, one Zarr per commune
       (``fim_store_KM274_Moroni_v1.zarr``), each holding all 200 synthetic
       storms of maximum depth. Exercise 2 opens Moroni's.

Two properties of this data shape the exercise:

* **Pluvial only.** The island models were run with rainfall forcing and no
  upstream boundary discharge, so a hazard level here means rain that has not
  drained, never a river rising.
* **A projected grid.** EPSG:5629 at 30.57 m, the island model's own grid rather
  than a reprojected copy. That is what the warning above is about, and it is a
  real difference from Guatemala, whose rasters were copied into EPSG:3857
  precisely so the map could read them.


Step 1 — Create the dashboard
=============================

#. Create a new dashboard (see
   `Creating a dashboard <getting_started.rst#creating-a-dashboard>`_) with:

   * **Name**: ``Comores Exercice 1``
   * **Description**: ``Solution pour l'exercice pratique OMM Comores n°1``

#. Find your dashboard on the landing page and double-click it to open. The
   dashboard is empty, so the preview shows a blank canvas.

#. Open **Dashboard Settings** in the top-right corner, and turn on
   **Unrestricted Grid Item Movement**. Save the settings.

#. Exit **Dashboard Settings** and click **Edit Dashboard** in the top-right
   corner to enter edit mode.


Step 2 — Add the three variable inputs
======================================

All three controls are built first, because the layers in step 4 refer to two of
them by name and there has to be something to refer to. See
`Referencing a variable input <getting_started.rst#referencing-a-variable-input>`_.

**The base map selector**

#. You will see an existing item on the dashboard. Click on the item's 3-dot
   menu and select **Edit**.

#. Set the **Visualization Type** to **Variable Input** (in the **Default**
   group).

#. Fill in:

   .. list-table::
      :header-rows: 1
      :widths: 32 68

      * - Argument
        - Value
      * - ``variable_name``
        - ``Fond de Carte``
      * - ``show_label``
        - ``True``
      * - ``variable_options_source``
        - ``Base Map Layers``

   ``Base Map Layers`` is a built-in options source — it fills the dropdown with
   the base maps the instance offers, so you do not enumerate them yourself.

#. On the **Settings** tab, set **Background Color** to ``#FFFFFF``. Without it
   the dropdown floats on the map with no backing and is hard to read.

#. Select an initial value from the preview on the right of the editor. The
   shipped solution uses **World Imagery** — aerial imagery makes it easy to see
   which buildings sit under the flooded cells — but any base map is fine.

#. Save the item, drag it to the top-left corner, and resize it to about 14
   columns wide and 5 rows tall.

.. figure:: images/ex1-variable-input-basemap.png
   :alt: The base map variable input configuration
   :width: 100%

   **Screenshot:** the **Variable Input** arguments for the base map selector.

**The commune selector**

This one is different from the other two: its options are not built in and not a
plain number, they are a list you supply.

#. Add another item, open its 3-dot menu, select **Edit**, and set the
   **Visualization Type** to **Variable Input**.

#. Fill in:

   .. list-table::
      :header-rows: 1
      :widths: 32 68

      * - Argument
        - Value
      * - ``variable_name``
        - ``Commune``
      * - ``show_label``
        - ``True``
      * - ``variable_options_source``
        - ``dropdown``

#. Choosing ``dropdown`` reveals a **choices** editor. Each entry has a **label**
   — what the viewer reads — and a **value** — what gets substituted into the
   URL. For the Comoros those are the commune's name and its path segment:

   .. list-table::
      :header-rows: 1
      :widths: 40 60

      * - Label
        - Value
      * - ``Moroni``
        - ``KM274_Moroni``
      * - ``Mutsamudu``
        - ``KM134_Mutsamudu``
      * - ``Fomboni``
        - ``KM321_Fomboni``
      * - …
        - …

   The split between the two is the point. The viewer never sees a pcode, and the
   URL never sees a display name. All **55** communes are in the shipped
   dashboard, ordered by pcode so the three islands group together — Anjouan
   (``KM1xx``), Grande Comore (``KM2xx``), Mohéli (``KM3xx``). Rather than typing
   them by hand, import the shipped item or copy the list out of
   ``dashboards/Comoros/Comoros_Hands_On_1.json``.

#. On the **Settings** tab, set **Background Color** to ``#ffffff``.

#. Set the initial value to ``Moroni``.

#. Save the item and drag it along the top, to the right of the base map
   selector.

.. figure:: images/ex1-variable-input-commune.png
   :alt: The commune variable input with its choices list
   :width: 100%

   **Screenshot:** the **Variable Input** arguments for the commune selector,
   with ``variable_options_source`` ``dropdown`` and the choices editor open.

**The probability mask**

#. Add a third item, open its 3-dot menu and select **Edit**, and set the
   **Visualization Type** to **Variable Input** again.

#. Fill in:

   .. list-table::
      :header-rows: 1
      :widths: 32 68

      * - Argument
        - Value
      * - ``variable_name``
        - ``Masque de Probabilité``
      * - ``show_label``
        - ``True``
      * - ``variable_options_source``
        - ``number``

#. On the **Settings** tab, set **Background Color** to ``#FFFFFF``.

#. Set the initial value to ``0`` in the preview. Zero means "draw every cell
   with any chance at all", which is where the exercise starts.

#. Save the item and drag it to the far right of the top row.

#. Save the dashboard by clicking **Save Changes** in the top-right corner.

.. figure:: images/ex1-variable-input-mask.png
   :alt: The probability mask variable input configuration
   :width: 100%

   **Screenshot:** the **Variable Input** arguments for the probability mask,
   with ``variable_options_source`` ``number`` and an initial value of 0.


Step 3 — Add the map
====================

#. Set the dashboard in edit mode, add another item, then open its 3-dot menu
   and select **Edit**.

#. Set the **Visualization Type** to **Map** (in the **Default** group).

#. Five arguments appear: **Base Map**, **Layer Control**, **Layers**,
   **Map Extent** and **Map Drawing**.

#. In the **Base Map** argument, choose ``Base Map`` from the **Variable
   Inputs** section at the bottom of the dropdown. The value becomes
   ``${Fond de Carte}``.

#. Turn **Layer Control** on, so the four layers can be toggled individually.

Leave **Map Extent** for step 5 — it is easier to pick once there is something
on the map.

.. figure:: images/ex1-map-args.png
   :alt: The Map visualization's arguments in the data viewer
   :width: 100%

   **Screenshot:** the **Map** visualization's five arguments, with **Base Map**
   bound to ``${Fond de Carte}`` and **Layer Control** on.


Step 4 — Add the four probability layers
========================================

These four are identical except for the URL and the name, so build one and
repeat. Add them in this order, so the deepest threshold ends up lowest in the
stack and the shallowest — which covers the largest area — ends up on top.

All four paths share one prefix; only the depth in the filename changes. Note
the ``${Commune}`` in the middle — that is the commune segment from step 2, and
it is what lets one set of four layers serve all 55 communes:

.. code-block:: text

   https://cog-s3-test-401506828094-us-east-1-an.s3.us-east-1.amazonaws.com/
     Comoros_training/Comoros_cycle_20240427_0000UTC/Comoros_cycle_20240427_0000UTC/
     fim/${Commune}/stream_sat_stormlab/pluvial_overbank/

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Layer **Name**
     - filename, appended to the prefix above
   * - ``Probabilité d'inondation à 100 cm``
     - ``prob_depth_ge_100cm_overbank.20240427.000000.tif``
   * - ``Probabilité d'inondation à 70 cm``
     - ``prob_depth_ge_70cm_overbank.20240427.000000.tif``
   * - ``Probabilité d'inondation à 30 cm``
     - ``prob_depth_ge_30cm_overbank.20240427.000000.tif``
   * - ``Probabilité d'inondation à 10 cm``
     - ``prob_depth_ge_10cm_overbank.20240427.000000.tif``

These are the **overbank** variants, with Moroni's permanent standing water
removed — the ``pluvial/`` folder alongside holds the same four without that
subtraction. For this commune the two differ in exactly 47 cells, so the choice
barely shows here, but it is the right one: a product that drew permanent water
as flooding would cry wolf every cycle.

For **each** of the four:

#. Next to **Layers**, click **Add Layer**. The layer editor opens with tabs
   **Layer**, **Source**, **Style**, **Legend**, **Attributes/Table Popup** and
   **Custom Modal Popup**.

#. On the **Layer** tab, set:

   .. list-table::
      :header-rows: 1
      :widths: 24 76

      * - Field
        - Value
      * - ``name``
        - *see the table above*
      * - ``opacity``
        - ``.5``

   Half-transparency matters here because the four thresholds are **nested**:
   anywhere the 100 cm layer has a value, the 10 cm layer has one too. The 10 cm
   layer is added last and so draws on top, and at full opacity it would hide the
   other three completely. At ``.5`` they tint through one another and the
   nesting stays visible.

#. On the **Source** tab, set **Source Type** to **GeoTIFF** and fill in:

   .. list-table::
      :header-rows: 1
      :widths: 24 76

      * - Field
        - Value
      * - ``url``
        - *see the table above, including the* ``${Commune}`` *segment*
      * - ``mask_below``
        - ``${Masque de Probabilité}``

   Both fields are free text, so both take the ``${Variable Name}`` form typed by
   hand, and the names inside the braces must match ``Commune`` and
   ``Masque de Probabilité`` exactly. They are substituted differently, and the
   difference is worth noticing: ``mask_below`` is *only* a placeholder, so it
   resolves to the number itself, while ``url`` has the placeholder embedded in a
   longer string, so the commune segment is spliced into the text around it.

   ``mask_below`` hides cells at or below the value given. At ``0`` every cell
   with any chance at all is drawn. Raise it and the map keeps only the cells
   that clear that likelihood — the whole point of step 5.

#. On the **Style** tab, leave the mode on **Continuous** and pick the **turbo**
   ramp. Set **Min** = ``0`` and **Max** = ``1``.

   Pinning Min and Max to 0–1 is the whole point of these four layers.
   Probability has a fixed, meaningful range, and all four must use the same one
   or they cannot be compared. Left to auto-scale, each layer would stretch its
   ramp over its own range and 0.2 would look like a different severity on each.

   Pinning matters more here than it looks. All four layers reach 1.0 somewhere,
   but they cover wildly different areas: about 7,600 cells carry a non-zero
   chance at 10 cm against 59 at 100 cm. Auto-scaled, the 100 cm layer would look
   as widespread as the 10 cm one.

#. **On the 100 cm layer only**, go to the **Legend** tab and select **Default
   Legend**. The four share a scale, so four identical colour bars would just
   take up room; the deepest layer carries the one legend and the other three
   have none.

#. Save the layer by clicking **Create** at the bottom of the layer editor.

.. figure:: images/ex1-layer-source-geotiff.png
   :alt: The Source tab configured for a probability GeoTIFF
   :width: 100%

   **Screenshot:** the **Source** tab with **Source Type** GeoTIFF, one
   probability URL, and ``mask_below`` bound to ``${Masque de Probabilité}``.

.. figure:: images/ex1-layer-style-turbo.png
   :alt: The Style tab with the turbo ramp pinned to 0-1
   :width: 100%

   **Screenshot:** the **Style** tab, **Continuous** mode, **turbo** selected,
   **Min** 0 and **Max** 1.

.. figure:: images/ex1-layer-list.png
   :alt: The Layers list showing all four raster layers
   :width: 100%

   **Screenshot:** the **Layers** list with all four layers, deepest first.


Step 5 — Finish the map, then drive it
======================================

#. In the **Map Extent** argument, choose **Use a Custom Extent** and enter:

   .. code-block:: text

      4814984.15,-1312113.30,13.83

   That is ``centre-x,centre-y,zoom`` in EPSG:3857 metres, centred on Moroni.
   The commune window is only about 5 km across, so the zoom is tighter than the
   country-wide views the other guides open on.

#. On the **Settings** tab, turn on **Fill Viewport** so the map occupies the
   whole window.

#. Save the item by clicking **Save** in the bottom-right corner of the map
   editor.

#. If the map is covering the three inputs, open its 3-dot menu, hover over
   **Order**, and select **Send to Back**. The controls should reappear on top.

#. Save the dashboard by clicking **Save Changes** in the top-right corner.

.. figure:: images/ex1-settings-fill-viewport.png
   :alt: The Settings tab with Fill Viewport enabled
   :width: 100%

   **Screenshot:** the **Settings** tab with **Fill Viewport** on.

**Try the mask.** Raise **Masque de Probabilité** from ``0`` and watch all four layers
thin out together:

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Mask
     - What is left on the map
   * - ``0``
     - Every cell any member floods to that depth.
   * - ``0.2``
     - Only cells where more than 10 of the 50 members reached that depth.
   * - ``0.5``
     - Only cells more than half the members agree on.
   * - ``0.9``
     - The handful of cells almost every member floods.

**Try the commune.** Change **Commune** and all four layers re-fetch from a
different folder. Mutsamudu and Jimlimé on Anjouan, Fomboni on Mohéli, and
Moroni here are four quite different places.

**Warning** — **The map extent does not follow the commune.** It is a fixed
string centred on Moroni, so switching to a commune on another island leaves the
view over open sea until you pan. There is no variable holding per-commune
coordinates and a 55-entry lookup is not something a variable input can express,
so the choices are to pan by hand, clear the custom extent and let the map
auto-fit to the layer, or keep one commune per dashboard. The shipped solution
keeps the fixed extent and expects you to pan — worth raising as a design
question rather than treating as a defect.


Item positions
==============

The shipped solution, for reference. You do not need to match these to the
pixel — drag to something close and adjust.

.. list-table::
   :header-rows: 1
   :widths: 34 16 16 16 18

   * - Item
     - ``x``
     - ``y``
     - ``w``
     - ``h``
   * - Base Map (variable input)
     - 0
     - 0
     - 14
     - 5
   * - Commune (variable input)
     - 42
     - 0
     - 18
     - 5
   * - Probability Mask (variable input)
     - 86
     - 0
     - 14
     - 5
   * - Map
     - 8
     - 4
     - 20
     - 20

The three inputs sit in one row across the top — left, centre, right — over a map
that has **Fill Viewport** on, so the map's own width and height matter less than
its stacking order.


Checkpoint
==========

You should now have:

* A map filling the window, showing Moroni over your chosen base map.
* A layer control listing five layers (including the base map); toggling each
  changes what is drawn.
* A legend control with one colour bar, on the 100 cm layer.
* Three controls across the top: a base-map dropdown, a commune dropdown listing
  all 55, and a **Masque de Probabilité** number.
* Raising the mask thins all four layers at once; setting it back to 0 restores
  them.
* Changing the commune re-fetches all four layers — and leaves the view where it
  was, for the reason in the warning above.
* The 10 cm layer covering a visibly larger footprint than the 100 cm one — in
  Moroni, roughly 7,600 cells against 59.

If instead the layers fail to place, or the map jumps somewhere far from the
Comoros, re-read the warning at the top of this page: the rasters are EPSG:5629
and the code has to be registered before any of this renders.


Talking points
==============

* **Why probability ramps must be pinned.** All four layers are fixed to 0–1
  because the range is meaningful and identical for each; without that, the same
  colour would mean a different number on each layer and the stack could not be
  read. Contrast this with depth, which has no natural upper bound and is
  normally left to auto-scale — one reason the two do not belong on the same map
  without care.
* **Two variables, two kinds of substitution.** ``${Masque de Probabilité}`` is a
  whole field, so it resolves to a number with its type intact.
  ``${Commune}`` sits inside a longer URL, so it is spliced into the surrounding
  text. Same syntax, and the app picks the right behaviour — but it is why a
  variable can rewrite part of a path, which is what turns one map into 55.
* **Label versus value.** The commune dropdown shows ``Moroni`` and stores
  ``KM274_Moroni``. Presenting a readable label over an opaque key is nearly
  always worth the indirection, and it means the pcode scheme can change without
  the viewer ever noticing.
* **What the mask actually filters.** Raising it to 0.2 does not keep "cells with
  a 20% chance of flooding". It keeps cells where **more than 10 of the forecast's
  50 members** reached that depth. Those 50 members collapse to 16 distinct
  library scenarios, so the values are coarse — the 10 cm layer takes only 41
  distinct values across the whole commune — and the layer therefore thins in
  visible jumps rather than smoothly. Worth demonstrating: it is the clearest way
  to show an audience that the number is an ensemble share, not a calibrated
  probability.
* **Layer order is draw order, and the thresholds are nested.** The first layer
  in the list draws lowest and each later one paints over it, so the 10 cm layer —
  added last, largest footprint — sits on top. Anywhere the 100 cm layer has a
  value the 10 cm layer has one too, so at full opacity the three deeper layers
  would be invisible. The ``.5`` opacity is what keeps the nesting readable;
  the layer control is still the way to isolate one threshold.
* **Overbank versus pluvial.** The four layers here have the commune's permanent
  standing water subtracted. For Moroni that is only 47 cells, so swapping one for
  its ``pluvial/`` twin barely shows — but the principle is the point, and other
  communes carry a larger baseline.
* **The projection constraint.** Guatemala's rasters were copied into EPSG:3857
  so the map could read them. The Comoros products were not copied, so the
  constraint lands on the application instead of on the data. Both are valid
  answers; this guide's warning says which one is outstanding here.


Next
====

Exercise 2 opens the commune's Zarr flood-map library — all 200 scenarios, not
just the 16 this cycle matched — and puts the storm on a variable input, so the
depth this exercise deliberately left out arrives with the context to read it.
