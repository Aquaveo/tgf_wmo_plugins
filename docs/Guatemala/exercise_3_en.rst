.. Guatemala hands-on exercise 3 solution, English. A Spanish translation lives
.. alongside this file as exercise_3_es.rst.

==============================================================
Exercise 3: Hazard classification with adjustable thresholds
==============================================================

Building **Guatemala Hands On 3 (English)** step by step.

**Start here:** This exercise reuses the four raster layers from
`Exercise 1 <exercise_1_en.rst>`_, so building that one first will save you time.

.. contents:: On this page
   :depth: 2
   :local:
   :backlinks: none


What you are building
=====================

A full-window map carrying the four rasters from exercise 1 plus two computed
layers: a hazard classification and the buildings and roads that fall inside it.
Four number inputs across the top set the probability threshold for each hazard
level, and an impact table sits under them. Change a threshold and the
classification, the affected features and the table all recompute.

.. figure:: images/ex3-finished.png
   :alt: The finished exercise 3 dashboard
   :width: 100%

   **Screenshot:** the finished dashboard: full-window map, four threshold
   inputs along the top, impact table on the right.

**Tip:** ``notebooks/Guatemala/03_hazard_classification.ipynb`` derives this
classification as plain Python, including the gate sweep that shows what each
threshold controls. Worth running first if you want to understand the analysis
before assembling the interface. The notebook still uses the earlier training
files, so its numbers differ from this dashboard's.


Understanding the four thresholds
=================================

Each hazard level is tied to **one** depth threshold and has its **own**
probability gate:

.. list-table::
   :header-rows: 1
   :widths: 18 32 25 25

   * - Level
     - Driven by
     - Colour
     - Default gate
   * - Low
     - P(≥ 10 cm)
     - green
     - 0.8
   * - Medium
     - P(≥ 30 cm)
     - yellow
     - 0.8
   * - High
     - P(≥ 70 cm)
     - red
     - 0.8
   * - Severe
     - P(≥ 100 cm)
     - purple
     - 0.8

A cell takes the level of the **deepest** threshold whose gate it clears.

**Every level is reachable on the sample.** The probabilities are fractions of
50 ensemble members, so every value is a multiple of 0.02, and each of the four
rasters reaches 1.0 somewhere. At the default gates of 0.8, the number of cells
that clear their gate is:

.. list-table::
   :header-rows: 1
   :widths: 25 25 25 25

   * - P(≥ 10 cm)
     - P(≥ 30 cm)
     - P(≥ 70 cm)
     - P(≥ 100 cm)
   * - 3,900
     - 3,155
     - 2,880
     - 2,646

So all four colours appear at the defaults. Lowering a gate only lets more cells
clear it: at the four depths, 15,877, 12,269, 10,219 and 9,315 cells
respectively have any chance at all. A cell that clears several gates is shown
at the deepest, so these counts overlap rather than add up.


Step 1: Create the dashboard
============================

#. Create a new dashboard (see
   `Creating a dashboard <getting_started_en.rst#creating-a-dashboard>`_) with:

   * **Name**: ``Guatemala Hands On 3 (English)``
   * **Description**: ``Solution for WMO Guatemala Hands On Exercise #3``

#. Find your dashboard on the landing page and double-click it to open. The
   dashboard is empty, so the preview shows a blank canvas.

#. Open **Dashboard Settings** in the top-right corner, and turn on
   **Unrestricted Grid Item Movement**. Save the settings.

#. Exit **Dashboard Settings** and click **Edit Dashboard** in the top-right
   corner to enter edit mode.


Step 2: Add the base map selector
=================================

The base map is a variable input so the viewer can switch it without editing
anything. Build the input first, then point the map at it.

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
        - ``Base Map``
      * - ``show_label``
        - ``True``
      * - ``variable_options_source``
        - ``Base Map Layers``

   ``Base Map Layers`` is a built-in options source: it fills the dropdown with
   the base maps the instance offers, so you do not enumerate them yourself.

#. On the **Settings** tab, set **Background Color** to ``#ffffff``. Without it
   the dropdown floats on the map with no backing and is hard to read.

#. Select an initial value for the dropdown from the preview on the right side
   of the editor. The shipped solution uses ``World Imagery``, but any base
   map is fine.

#. Save the item by clicking **Save** in the bottom-right corner of the item
   editor.

#. Drag the item to the top-left corner over the map and resize it as needed.

#. Save the dashboard by clicking **Save Changes** in the top-right corner of
   the dashboard editor.

   You now have a base map selector on the dashboard, but it does not yet
   control the map.

.. figure:: images/ex1-variable-input-basemap.png
   :alt: The base map variable input configuration
   :width: 100%

   **Screenshot:** the **Variable Input** arguments for the base map selector.


Step 3: Add the four threshold inputs
=====================================

Build all four before the layers that consume them. Each is a **Variable Input**
with ``variable_options_source`` set to ``number``:

.. list-table::
   :header-rows: 1
   :widths: 100

   * - ``Variable Name``
   * - ``Low Threshold (P(≥10 cm))``
   * - ``Medium Threshold (P(≥30 cm))``
   * - ``High Threshold (P(≥70 cm))``
   * - ``Severe Threshold (P(≥100 cm))``

For **each** of the four:

#. Set the dashboard in edit mode by clicking on the **Edit Dashboard** button
   in the top-right corner.

#. Add another item by clicking **Add Dashboard Item** in the top-right corner.

#. Click on the 3-dot menu of the new item and select **Edit**.

#. Set the **Visualization Type** to **Variable Input** (in the **Default**
   group).

#. Fill in:

   .. list-table::
      :header-rows: 1
      :widths: 32 68

      * - Argument
        - Value
      * - ``variable_name``
        - *see the table above*
      * - ``show_label``
        - ``True``
      * - ``variable_options_source``
        - ``number``

#. On the **Settings** tab, set **Background Color** to ``#ffffff``.

#. On the **Settings** tab, add a top border by clicking the top border icon. A popup will appear. Change the style to ``solid`` to show the border.

   Give the leftmost input (``Low Threshold``) a left border and the rightmost (``Severe Threshold``) a right
   border as well, so the four read as one strip.

#. Set the initial value to ``0.8`` in the preview on the right side of the
   editor.

#. Save the item by clicking **Save** in the bottom-right corner of the item
   editor.

#. Drag the item into place along the top of the dashboard, to the right of the
   base map selector, and resize it as needed.

#. Save the dashboard by clicking **Save Changes** in the top-right corner of
   the dashboard editor.

.. figure:: images/ex3-threshold-inputs.png
   :alt: The four threshold variable inputs across the top of the dashboard
   :width: 100%

   **Screenshot:** the four threshold inputs side by side, each showing its
   label and value.


Step 4: Add the map and the four rasters
========================================

If you have exercise 1 then do the following. If you do not have exercise 1,
build the map and the four rasters from scratch as in `Exercise 1 <exercise_1_en.rst>`_.

#. Open the dashboard from exercise 1

#. Click on the map item's 3-dot menu and choose **Export**.

#. Open the new dashboard for this exercise.

#. Click **Edit Dashboard** in the top-right corner to enter edit mode.

#. Click the **Import Dashboard Item** in the top-right corner and import the
   dashboard item from exercise 1.

#. If the map is covering the base map selector and the threshold inputs, click
   on the 3-dot menu, hover over **Order**, and select **Send to Back**. The
   inputs should now be visible on top of the map.

#. Edit the map item. For each of the four rasters, edit the layer and turn off the
   **Default Visibility** in the **Layer** tab. This will hide the layers when the dashboard is first loaded.
   Make sure to save the layer after editing it.

#. Save the dashboard by clicking **Save Changes** in the top-right corner of
   the dashboard editor.


Step 5: Add the hazard classification layer
===========================================

#. Set the dashboard in edit mode by clicking on the **Edit Dashboard** button
   in the top-right corner.

#. Click on the map item's 3-dot menu and select **Edit**. You may need to move
   one of the threshold inputs out of the way to see the map menu.

#. Next to **Layers**, click **Add Layer**.

#. Go straight to the **Source** tab and set **Source Type** to
   **Guatemala: Capa de Peligro** (Flood Hazard Layer, in the
   **UFFIS: Guatemala** group).

#. The plugin's arguments appear, with Spanish names. Fill in:

   .. list-table::
      :header-rows: 1
      :widths: 26 74

      * - Argument
        - Value
      * - ``Umbral Bajo``
        - ``${Low Threshold (P(≥10 cm))}``
      * - ``Umbral Medio``
        - ``${Medium Threshold (P(≥30 cm))}``
      * - ``Umbral Alto``
        - ``${High Threshold (P(≥70 cm))}``
      * - ``Umbral Severo``
        - ``${Severe Threshold (P(≥100 cm))}``
      * - ``Ciclo``
        - **Evento de muestra** (``sample``)

   ``Ciclo`` picks the TITO cycle the plugin classifies. **Evento de muestra**
   is the country's published sample cycle, the same one the four raster layers
   come from. Left empty, the plugin reads the latest live cycle instead, and the
   hazard would no longer match the rasters underneath. Leave
   ``Fuente Inundacion`` empty; its default is the combined overbank source the
   rasters use.

#. Click **Fetch plugin defaults**. The layer is named **Clasificación de
   peligro** (hazard classification), styled with four rules on the ``peligro``
   attribute, and given a four-item **Peligro** legend (Bajo, Medio, Alto,
   Severo). Rename the layer on the **Layer** tab if you want an English name.

#. Save the layer by clicking **Create** at the bottom of the layer editor.

.. figure:: images/ex3-hazard-layer-source.png
   :alt: The hazard layer source configuration with four bound thresholds
   :width: 100%

   **Screenshot:** the **Source** tab for the hazard layer, four arguments bound
   to the four threshold variables and ``Ciclo`` set to **Evento de muestra**.


Step 6: Add the affected-features layer
=======================================

#. Next to **Layers**, click **Add Layer** again.

#. Go straight to the **Source** tab and set **Source Type** to
   **Guatemala: Capa de Impacto** (Flood Impact Layer).

#. Bind the same four arguments to the same four variables as in the previous
   step, and set ``Ciclo`` to **Evento de muestra** again.

#. Click **Fetch plugin defaults**. The layer arrives as **Edificios y
   carreteras en peligro** (buildings and roads at risk) with eight rules
   (polygon and linestring per level) and a **Peligro** legend.

#. Save the layer by clicking **Create** at the bottom of the layer editor.

The two layers answer different questions from the same thresholds: the hazard
layer classifies *ground*, this one classifies *assets*. Keeping them separate
lets a viewer turn off the ground shading and look only at what is affected.


Step 7: Finish the map
======================

#. In the **Map Extent** argument, choose **Use a Custom Extent** and enter:

   .. code-block:: text

      -10077781.20,1629865.34,15.13

#. On the **Settings** tab, turn on **Fill Viewport** so the map occupies the
   whole window.

#. Save the item by clicking **Save** in the bottom-right corner of the map
   editor.

#. Resize the map item to fill the window by dragging the handle in its
   bottom-right corner.

#. Make sure to move the threshold input back into place.

#. Save the dashboard by clicking **Save Changes** in the top-right corner of
   the dashboard editor.

**Important:** The rasters must be in EPSG:3857 (or EPSG:4326), as the sample
rasters are. If any layer points at a raster in another projection, such as UTM,
the map will auto-fit to that raster's projection, jump somewhere far from
Guatemala, and the vector layers will appear to load and then vanish. This exact
bug cost real debugging time on this dashboard.


Step 8: Add the impact summary table
====================================

#. Set the dashboard in edit mode by clicking on the **Edit Dashboard** button
   in the top-right corner.

#. Add another item by clicking **Add Dashboard Item** in the top-right corner.

#. Click on the 3-dot menu of the new item and select **Edit**.

#. Set the **Visualization Type** to **Guatemala: Resumen de Impacto** (Flood
   Impact Summary, in the **UFFIS: Guatemala** group).

#. Bind the same four arguments to the same four variables as in step 5, and set
   ``Ciclo`` to **Evento de muestra**.

   The table counts the people, buildings and roads in each hazard level, using
   the same gates as the map, and ends with a **TOTAL en peligro** row.

#. On the **Settings** tab, set **Background Color** to ``#ffffff`` and add
   borders on the left, right and bottom, so it joins the strip of threshold
   inputs above it.

#. Save the item by clicking **Save** in the bottom-right corner of the item
   editor.

#. Drag the item directly below the threshold inputs on the right and resize it
   as needed.

#. Save the dashboard by clicking **Save Changes** in the top-right corner of
   the dashboard editor.

.. figure:: images/ex3-impact-summary.png
   :alt: The impact summary table arguments bound to the four thresholds
   :width: 100%

   **Screenshot:** the impact summary table arguments bound to the four
   threshold variables, with ``Ciclo`` set to **Evento de muestra**.


Step 9: Test the wiring
=======================

Update a threshold. The hazard shading, the affected features
and the table should all recompute together, with progress messages while the
layers rebuild. As a demonstration, lower the Severe threshold to 0.2. The purple
Severe class spreads further along the stream, and the table shows more
buildings and roads in the Severe row.

.. figure:: images/ex3-thresholds-before.png
   :alt: The dashboard before lowering a threshold
   :width: 100%

   **Screenshot:** the same view before lowering the Severe threshold.

.. figure:: images/ex3-thresholds-after.png
   :alt: The dashboard after lowering a threshold
   :width: 100%

   **Screenshot:** the same view after lowering the Severe threshold.


Checkpoint
==========

You should now have:

* A map filling the window, with seven layers in the layer control (four
  rasters, the two computed layers and the base map).
* Four labelled threshold inputs across the top, each stepping by 0.05.
* At the default gates of 0.8: 1,127 hazard polygons showing all four colours,
  453 buildings and roads at risk, and an impact table whose
  **TOTAL en peligro** row shows 342 buildings and 886 people.
* Moving any threshold updates the hazard layer, the impact layer and the table.
* Progress messages while the layers recompute.


Talking points
==============

* **Four gates on four different questions.** With unequal gates, "Severe"
  might mean P(≥100 cm) ≥ 0.15 while "High" means P(≥70 cm) ≥ 0.1. Those are different questions with
  different cutoffs, so the level names are not comparable to each other and
  "severe" carries no meaning on its own. Setting all four gates equal is a good
  demonstration: the levels then differ only by depth, which is far easier to
  explain.
* **An empty class is an interface problem.** On the sample every level is
  reachable, but on a smaller event a deep threshold may never get near the
  gate, and then that colour simply never appears. A viewer moving that input
  gets no feedback distinguishing "nothing qualifies" from "the control is
  broken". Ask attendees how they would fix it: show the value range? annotate
  the legend? There is no single right answer, and the discussion is the point.
* **Probabilities come in steps of 0.02.** With 50 members, a probability can only
  be a multiple of 0.02, so a gate of 0.8 means "at least 40 of the 50 members".
  Framing a gate as a count of members is often easier to explain than a
  probability.
* **Vectorising a classification.** A map layer can only point at a URL, and
  nothing here serves a computed raster, so the plugin vectorises the classified
  grid into polygons (1,127 at the default gates). Adjacent cells of equal class
  merge, so this is exact rather than an approximation. Normal and NoData cells,
  most of the grid, are dropped, because a basemap shows unaffected ground better
  than a coloured layer does.


Item positions
==============

The shipped solution places its items as follows, on the 100-column grid:

.. list-table::
   :header-rows: 1
   :widths: 40 15 15 15 15

   * - Item
     - ``x``
     - ``y``
     - ``w``
     - ``h``
   * - Map
     - 0
     - 0
     - 99
     - 41
   * - Base Map input
     - 0
     - 0
     - 17
     - 6
   * - Low Threshold input
     - 56
     - 0
     - 11
     - 7
   * - Medium Threshold input
     - 67
     - 0
     - 11
     - 7
   * - High Threshold input
     - 78
     - 0
     - 11
     - 7
   * - Severe Threshold input
     - 89
     - 0
     - 11
     - 7
   * - Impact summary table
     - 56
     - 7
     - 44
     - 26
