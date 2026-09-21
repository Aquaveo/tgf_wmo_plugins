.. Comoros hands-on exercise 2 solution, English. Adapted from the Guatemala
.. guide at ../Guatemala/exercise_2_en.rst. What differs is explained where it
.. comes up: the depth library is per commune rather than national, so a second
.. selector drives it; and the plugins are the francophone `_comoros` family, so
.. their labels and output read in French inside an English-titled dashboard.
.. The built dashboard is dashboards/Comoros/Comoros_Hands_On_2.json.

==============================================================
Exercise 2 — Impact for a single storm
==============================================================

Building **Comores Exercice 2** step by step.

.. contents:: On this page
   :depth: 2
   :local:
   :backlinks: none


What you are building
=====================

A map on the left showing one storm's flood depth and the buildings and roads it
floods, and on the right a summary table and a headline card. Three controls
across the top pick the base map, the commune and the storm, and everything
re-computes.

.. figure:: images/ex2-finished.png
   :alt: The finished exercise 2 dashboard
   :width: 100%

   **Screenshot:** the finished dashboard, with the three selectors, map,
   summary table and card.

New ideas here: reading a slice out of a Zarr store, a vector layer whose
features are produced by a plugin rather than fetched from a URL, and two
variable inputs driving four separate things at once.

Exercise 1 drew **probabilities** across a whole forecast. This draws **depth**
in one specific scenario out of the commune's library — a physical quantity, so
it needs no threshold to interpret. Section 9 of the companion notebook shows
how the two connect.

**Tip** — ``notebooks/Comoros/02_storm_impact.ipynb`` derives the numbers this
dashboard shows as plain Python: how depth is sampled onto each building and
road, and how the summary table is assembled. It also rebuilds exercise 1's
probability raster from the 50 forecast members and checks it against the
published one. Worth running first if you want to understand the analysis before
assembling the interface.

**Note** — The plugins are the francophone ``_comoros`` family, so their group
reads **Cartes d'Inondation (Français)** in the dropdown and the table and card
come back in French, inside a dashboard whose own title is English. That is
deliberate — Comorian products are francophone — but it is the first thing
people ask about, so say it before they do.


Step 1 — Create the dashboard
=============================

#. Create a new dashboard (see
   `Creating a dashboard <getting_started.rst#creating-a-dashboard>`_) with:

   * **Name**: ``Comores Exercice 2``
   * **Description**: ``Solution pour l'exercice pratique OMM Comores n°2``

#. Find your dashboard on the landing page and double-click it to open. The
   dashboard is empty, so the preview shows a blank canvas.

#. Open **Dashboard Settings** in the top-right corner, and turn on
   **Unrestricted Grid Item Movement**. Save the settings.

#. Exit **Dashboard Settings** and click **Edit Dashboard** in the top-right
   corner to enter edit mode.


Step 2 — Add the three variable inputs
======================================

Build all three before anything that reads them. Every later item depends on at
least one.

**The base map selector**

#. You will see an existing item on the dashboard. Click on the item's 3-dot
   menu and select **Edit**.

#. Set the **Visualization Type** to **Variable Input** (in the **Default**
   group), and fill in:

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

#. On the **Settings** tab, set **Background Color** to ``#ffffff``.

#. Pick **World Imagery** as the initial value, save the item, and drag it to
   the top of the dashboard just right of where the map will sit.

**The commune selector**

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

#. In the **choices** editor, each entry has a **label** the viewer reads and a
   **value** that goes into the URL — the commune's name and its path segment,
   as in exercise 1:

   .. list-table::
      :header-rows: 1
      :widths: 40 60

      * - Label
        - Value
      * - ``Moroni``
        - ``KM274_Moroni``
      * - ``Fomboni``
        - ``KM321_Fomboni``
      * - …
        - …

   **Important** — This dropdown carries **22 communes, not the 55 of
   exercise 1.** Exercise 1 reads the probability rasters, which the cycle
   publishes for every commune. This one reads the Zarr flood-map libraries,
   and only 22 of those had finished uploading — everything from ``KM251``
   onward. Offering a commune whose library is absent produces a store-open
   error naming the URL, so the list is trimmed to what exists. Re-check the
   bucket before a workshop; if the rest have landed, widen it.

#. Set **Background Color** to ``#ffffff``, set the initial value to ``Moroni``,
   save, and drag it beside the base map selector.

**The storm selector**

#. Add a third item, open its 3-dot menu and select **Edit**, and set the
   **Visualization Type** to **Variable Input**.

#. Fill in:

   .. list-table::
      :header-rows: 1
      :widths: 32 68

      * - Argument
        - Value
      * - ``variable_name``
        - ``Tempête``
      * - ``show_label``
        - ``True``
      * - ``variable_options_source``
        - ``Cartes d'Inondation (Français): Résumé de Tempête (Comores) - Index``

   That options source is generated from an existing plugin argument, in the
   form ``<group>: <plugin label> - <Argument>``. Picking it means "offer the
   same choices the storm card's ``index`` argument offers", so the control is
   populated from the plugin and cannot drift out of sync with it.

   The choices are the 200 positions in a commune's library, labelled by
   position. They are **not** labelled in millimetres, and that is deliberate: a
   Comoros magnitude is the area-weighted mean rainfall over one commune, so the
   same position is 346 mm in one commune and 462 mm in another. What is the same
   everywhere is the ordering — every library holds 200 scenarios sorted by
   magnitude, so a higher position is a wetter storm wherever you are. The card
   in step 6 reports the actual millimetres once a commune is chosen.

#. On the **Settings** tab, set **Background Color** to ``#ffffff``.

#. Set the initial value, save the item, and drag it to the far right of the top
   row.

.. figure:: images/ex2-storm-input.png
   :alt: The storm selector variable input configuration
   :width: 100%

   **Screenshot:** the **Variable Input** arguments for the storm selector, with
   the plugin-derived options source selected.


Step 3 — Add the map with the Zarr depth layer
==============================================

#. Add another item, open its 3-dot menu and select **Edit**, and set the
   **Visualization Type** to **Map** (in the **Default** group).

#. In the **Base Map** argument, choose ``Base Map`` from the **Variable
   Inputs** section at the bottom of the dropdown. The value becomes
   ``${Fond de Carte}``.

#. Turn **Layer Control** on.

#. Next to **Layers**, click **Add Layer**.

#. On the **Layer** tab, set:

   .. list-table::
      :header-rows: 1
      :widths: 24 76

      * - Field
        - Value
      * - ``name``
        - ``Profondeur d'inondation (m), bibliothèque communale``

#. On the **Source** tab, set **Source Type** to **Zarr** and fill in:

   .. list-table::
      :header-rows: 1
      :widths: 24 76

      * - Field
        - Value
      * - ``url``
        - ``https://cog-s3-test-401506828094-us-east-1-an.s3.us-east-1.amazonaws.com/Comoros_IBF/Comoros/fim_store_${Commune}_v1.zarr``
      * - ``variable``
        - ``depth``
      * - ``index``
        - ``${Tempête}``
      * - ``mask_below``
        - ``0.05``

   Two variables in one source, doing different jobs. ``${Commune}`` is spliced
   into the URL, so changing it opens a **different store**. ``${Tempête}`` is the
   whole ``index`` field, so changing it reads a **different slice** of the store
   already open. The store holds all 200 scenarios in one array and ``index``
   selects one — no duplicated layers, no separate files, and only one
   scenario's worth of data crosses the wire.

   ``mask_below`` is ``0.05`` because that is the store's own
   ``extent_threshold_m``: the model does not consider a cell flooded below 5 cm.
   Reusing the number the data was built with beats inventing one.

#. On the **Style** tab, leave the mode on **Continuous** and pick the **Blues**
   ramp (under **Single hue**). Leave **Min** and **Max** empty.

   Leaving both bounds empty means "resolve them from the data at render time",
   so the ramp re-stretches for each scenario as the storm changes. Depth is a
   property of the particular scenario, so auto-scaling is right here — the
   opposite of exercise 1's probability layers, which had to be pinned to 0–1 so
   they could be compared with each other. With nothing else on this map, a
   single-hue blue reads as water without a legend.

#. On the **Legend** tab, select **Default Legend**.

#. Save the layer by clicking **Create** at the bottom of the layer editor.

.. figure:: images/ex2-zarr-source.png
   :alt: The Source tab configured for the Zarr store
   :width: 100%

   **Screenshot:** the **Source** tab with **Source Type** Zarr, the store URL
   carrying ``${Commune}``, ``variable`` depth, ``index`` ``${Tempête}`` and
   ``mask_below`` 0.05.


Step 4 — Add the plugin-backed impact layer
===========================================

This layer's features are computed per request by a plugin. There is no GeoJSON
URL — the plugin samples depth onto every building and road in the commune and
returns the result.

#. Next to **Layers**, click **Add Layer** again.

#. Go straight to the **Source** tab and set **Source Type** to **Couche
   d'Impact par Tempête (Comores)**. Dynamic map-layer plugins appear in the same
   **Source Type** dropdown as GeoTIFF and Zarr, listed under their plugin group.

#. The plugin's arguments appear. Fill in:

   .. list-table::
      :header-rows: 1
      :widths: 24 76

      * - Argument
        - Value
      * - ``commune``
        - ``${Commune}``
      * - ``index``
        - ``${Tempête}``

#. Click **Fetch plugin defaults**.

   This is the step that saves the most work. The plugin's ``run()`` returns a
   ready-made scaffold — the layer name, the source binding, a rule-based style
   keyed on the ``bande`` (depth band) attribute, and a matching legend. After
   fetching you should see eight style rules and a four-item **Profondeur**
   legend, none of which you had to author. Authoring vector style rules by hand
   is error-prone: a rule in the wrong shape silently never matches and leaves
   every feature grey.

#. Rename the layer to ``Bâtiments et routes inondés`` on the **Layer** tab if you want it to
   match the shipped solution.

#. Check the **Style** and **Legend** tabs to see what arrived. Colours run
   green → yellow → red → purple across four depth bands, with separate rules for
   polygons (buildings) and linestrings (roads) so roads get a stroke wide enough
   to see.

#. Save the layer by clicking **Create** at the bottom of the layer editor.

#. In the **Map Extent** argument, choose **Use a Custom Extent** and enter:

   .. code-block:: text

      4814984.15,-1312113.30,13.83

   That is ``centre-x,centre-y,zoom`` in EPSG:3857 metres, centred on Moroni.

   **Warning** — As in exercise 1, **the extent does not follow the commune**.
   Switch to a commune on another island and the view stays over Moroni until you
   pan. The layers reload correctly; only the camera is fixed.

#. Save the item, then resize the map to fill roughly the left 60% of the window,
   leaving the right-hand strip for the table and the card.

#. Save the dashboard by clicking **Save Changes** in the top-right corner.

.. figure:: images/ex2-dynamic-layer-source.png
   :alt: The Source tab with a dynamic map-layer plugin selected
   :width: 100%

   **Screenshot:** the **Source** tab with the storm impact layer selected,
   ``commune`` and ``index`` bound, and the **Fetch plugin defaults** button.

.. figure:: images/ex2-dynamic-layer-style.png
   :alt: The Style tab showing the fetched rule-based style
   :width: 100%

   **Screenshot:** the **Style** tab after fetching, showing the eight rules on
   the ``bande`` attribute.


Step 5 — Add the summary table
==============================

#. Set the dashboard in edit mode, add another item, open its 3-dot menu and
   select **Edit**.

#. Set the **Visualization Type** to **Résumé d'Impact par Tempête (Comores)**
   (in the **Cartes d'Inondation (Français)** group).

#. Fill in:

   .. list-table::
      :header-rows: 1
      :widths: 24 76

      * - Argument
        - Value
      * - ``commune``
        - ``${Commune}``
      * - ``index``
        - ``${Tempête}``

   The table breaks the scenario's flooded features into depth bands, deepest
   first, with counts of buildings, population, area, road length and the share
   of the **commune's** population affected — not the island's or the country's,
   which is why the commune has to reach the plugin as an argument rather than
   being baked in.

#. Save the item and drag it to the upper right of the dashboard.


Step 6 — Add the storm card
===========================

#. Add another item, open its 3-dot menu and select **Edit**.

#. Set the **Visualization Type** to **Résumé de Tempête (Comores)** (in the same
   group), and bind the same two arguments:

   .. list-table::
      :header-rows: 1
      :widths: 24 76

      * - Argument
        - Value
      * - ``commune``
        - ``${Commune}``
      * - ``index``
        - ``${Tempête}``

   The card gives the headline figures — the scenario's rainfall total, the
   flooded area, the deepest water and the mean depth where wet — for someone who
   will not read a table. This is where the magnitude in millimetres finally
   appears, because only now are both the commune and the scenario known.

#. Save the item and drag it below the summary table.

#. Save the dashboard by clicking **Save Changes** in the top-right corner.

.. figure:: images/ex2-table-card.png
   :alt: The summary table and storm card
   :width: 100%

   **Screenshot:** the summary table and card for one scenario.


Step 7 — Test the wiring
========================

Change the **Storm** input. Four things should update: the Zarr layer re-reads
its slice, the impact layer re-runs, and the table and card re-fetch. Progress
messages appear while the impact layer recomputes.

Then change the **Commune**. The same four update again, but this time the Zarr
layer opens a different store entirely and the plugins read a different set of
buildings and roads. Only the camera stays put.

Worth trying at the two ends of the library:

.. list-table::
   :header-rows: 1
   :widths: 18 82

   * - Storm
     - What you should see
   * - ``0``
     - Almost nothing — this is the commune's permanent standing water, not a
       storm. The card reports a rainfall total near zero.
   * - ``150``
     - A substantial footprint. For Moroni the card reads about 423 mm and 12 km².
   * - ``199``
     - The wettest scenario in the library, and the only end where the ``2 m ou
       plus`` band has any chance of appearing.


Item positions
==============

The shipped solution, for reference. You do not need to match these to the
pixel — drag to something close and adjust.

.. list-table::
   :header-rows: 1
   :widths: 46 13 13 13 15

   * - Item
     - ``x``
     - ``y``
     - ``w``
     - ``h``
   * - Map
     - 0
     - 0
     - 60
     - 44
   * - Base Map (variable input)
     - 60
     - 0
     - 13
     - 6
   * - Commune (variable input)
     - 74
     - 0
     - 13
     - 6
   * - Storm (variable input)
     - 89
     - 0
     - 11
     - 6
   * - Résumé d'Impact par Tempête (table)
     - 60
     - 9
     - 40
     - 20
   * - Résumé de Tempête (card)
     - 62
     - 29
     - 37
     - 12

Unlike exercise 1, the map does **not** fill the viewport here — it shares the
window with the table and the card, so leave **Fill Viewport** off.


Checkpoint
==========

You should now have:

* Three selectors across the top: base map, commune and storm.
* A map on the left with two layers plus the base map in the layer control.
* Depth drawn in blue, re-scaling as the storm changes.
* Buildings and roads coloured by depth band over the top, with a
  **Profondeur** legend, and roads visible as coloured lines rather than
  hairlines.
* A summary table and a card on the right, both in French, both updating with
  either selector.
* Changing the commune swapping the whole dataset — store, features and
  denominators — while the view stays where it was.


Talking points
==============

* **Two variables, four consumers.** ``${Tempête}`` appears in a Zarr source index,
  a plugin layer argument and two visualization arguments; ``${Commune}`` appears
  in all the same places plus the store URL. Nothing in the six items knows about
  the others; they all just declare a dependency on a name.
* **Splicing versus substituting.** ``${Tempête}`` is a whole field, so it resolves
  to a value with its type intact. ``${Commune}`` sits inside a longer URL, so it
  is spliced into the surrounding text. Same syntax, different behaviour, and it
  is what lets one layer reach 22 different stores.
* **Dynamic layers re-run; static layers re-fetch.** The Zarr layer re-reads a
  slice of an array that is already open. The impact layer re-executes Python
  that samples a raster onto 25,000-odd geometries. Same trigger, very different
  cost — which is why the plugin reports progress while it works.
* **Why the sampling is not a rasterisation.** The Guatemala plugin burns feature
  ids into a grid and reads depths back by id, which works at its 5 m cells. Here
  cells are 30.57 m and most buildings are smaller than one, so many share a cell
  — burning ids keeps the last and silently drops the rest, losing about 61% of
  the features. The Comoros plugin builds a list of (feature, cell) pairs instead,
  which allows many features per cell. Same question, different grid, different
  method: worth checking coverage whenever a sampling method meets a new grid.
* **Depth versus probability.** Exercise 1 asked "what are the odds of 30 cm
  here" across a whole forecast. This asks "how deep in this one scenario". Both
  use the same buildings. Which would you put in front of a civil-protection
  officer, and what would you say about the other?
* **Why the plugin ships a style.** The alternative — hand-authoring eight rules
  in the GUI — fails silently when a rule is malformed. Shipping the style from
  ``run()`` means the layer is correct the first time and stays correct if the
  bands change.


Next
====

Exercise 3 turns the probability thresholds themselves over to the viewer, using
the hazard and impact layers that classify against the four exceedance rasters
of exercise 1.
