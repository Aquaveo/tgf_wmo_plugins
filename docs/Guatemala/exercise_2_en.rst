.. Guatemala hands-on exercise 2 solution, English. A Spanish translation lives
.. alongside this file as exercise_2_es.rst.

==============================================================
Exercise 2 — Impact for a single storm
==============================================================

Building **Guatemala Hands On 2 (English)** step by step.

.. contents:: On this page
   :depth: 2
   :local:
   :backlinks: none


What you are building
=====================

A map on the left showing one storm's flood depth and the buildings and roads it
floods, and on the right a table and a card summarising that storm. A dropdown
selects the storm, and everything re-computes.

.. figure:: images/ex2-finished.png
   :alt: The finished exercise 2 dashboard
   :width: 100%

   **Screenshot:** the finished dashboard, with the storm dropdown, map, summary
   table and card.

New ideas here: reading a slice out of a Zarr store, a vector layer whose
features are produced by a plugin rather than fetched from a URL, and one
variable input driving four separate things at once.

**Tip** — ``notebooks/Guatemala/02_storm_impact.ipynb`` derives the numbers this dashboard
shows as plain Python — how depth is sampled onto each building and road, and
how the summary table is assembled. Worth running first if you want to
understand the analysis before assembling the interface.


Step 1 — Create the dashboard
=============================

#. Create a new dashboard (see
   `Creating a dashboard <getting_started_en.rst#creating-a-dashboard>`_) with:

   * **Name**: ``Guatemala Hands On 2 (English)``
   * **Description**: ``Solution for WMO Guatemala Hands On Exercise #2``

#. Find your dashboard on the landing page and double-click it to open. The
   dashboard is empty, so the preview shows a blank canvas.

#. Open **Dashboard Settings** in the top-right corner, and turn on
   **Unrestricted Grid Item Movement**. Save the settings.

#. Exit **Dashboard Settings** and click **Edit Dashboard** in the top-right
   corner to enter edit mode.


Step 2 — Add the storm selector
===============================

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
        - ``Storm``
      * - ``show_label``
        - ``True``
      * - ``variable_options_source``
        - ``Flood Maps (English): Storm Impact Summary (English) - Index``

   That options source is generated from an existing plugin argument, in the
   form ``<group>: <plugin label> - <Argument>``. Picking it means
   "offer the same choices the Storm Impact Summary plugin's ``index`` argument
   offers", so the dropdown is populated from the plugin and cannot drift out of
   sync with it.

#. On the **Settings** tab, set **Background Color** to ``#ffffff`` and add a
   border on the right side only.

#. Select an initial value for the dropdown from the preview on the right side
   of the editor. The shipped solution uses the first entry, but any storm is
   fine.

#. Save the item by clicking **Save** in the bottom-right corner of the item
   editor.

#. Drag the item to the top of the dashboard and resize it as needed. Leave room
   to its left for the base map selector.

#. Save the dashboard by clicking **Save Changes** in the top-right corner of
   the dashboard editor.

.. figure:: images/ex2-storm-input.png
   :alt: The storm selector variable input configuration
   :width: 100%

   **Screenshot:** the **Variable Input** arguments for the storm selector, with
   the plugin-derived options source selected.


Step 3 — Add the base map selector
==================================

The base map is a variable input so the viewer can switch it without editing
anything. Build the input first, then point the map at it.

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
        - ``Base Map``
      * - ``show_label``
        - ``True``
      * - ``variable_options_source``
        - ``Base Map Layers``

   ``Base Map Layers`` is a built-in options source — it fills the dropdown with
   the base maps the instance offers, so you do not enumerate them yourself.

#. On the **Settings** tab, set **Background Color** to ``#ffffff``. Without it
   the dropdown floats on the map with no backing and is hard to read.

#. Select an initial value for the dropdown from the preview on the right side
   of the editor. The shipped solution uses ``World Light Gray Base``, but any
   base map is fine.

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


Step 4 — Add the map with the Zarr depth layer
==============================================

#. Set the dashboard in edit mode by clicking on the **Edit Dashboard** button
   in the top-right corner.

#. Add another item by clicking **Add Dashboard Item** in the top-right corner.

#. Click on the 3-dot menu of the new item and select **Edit**.

#. Set the **Visualization Type** to **Map** (in the **Default** group).

#. In the **Base Map** argument, choose ``Base Map`` from the **Variable
   Inputs** section at the bottom of the dropdown. The value becomes
   ``${Base Map}``.

#. Next to **Layers**, click **Add Layer**.

#. On the **Layer** tab, set the following properties:

   .. list-table::
      :header-rows: 1
      :widths: 24 76

      * - Field
        - Value
      * - ``name``
        - ``Flood Depth (m)``

#. On the **Source** tab, set **Source Type** to **Zarr** and fill in:

   .. list-table::
      :header-rows: 1
      :widths: 24 76

      * - Field
        - Value
      * - ``url``
        - ``https://cog-s3-test-401506828094-us-east-1-an.s3.us-east-1.amazonaws.com/floodmaps_test``
      * - ``variable``
        - ``depth``
      * - ``index``
        - ``${Storm}``

   The ``index`` field is where this exercise becomes interactive. The Zarr
   store holds all 198 storms in one array, and ``index`` selects the slice.
   Binding it to ``${Storm}`` means changing the dropdown re-reads a different
   slice — no duplicated layers, no separate files.

#. On the **Style** tab, leave the mode on **Continuous** and pick the **blue single hue**
   ramp. Leave **Min** and **Max** empty.

#. On the **Legend** tab, select **Default Legend**. For a ramp-styled raster
   the app generates a colour bar automatically.

#. Save the layer by clicking **Create** at the bottom of the layer editor.

.. figure:: images/ex2-zarr-source.png
   :alt: The Source tab configured for the Zarr store
   :width: 100%

   **Screenshot:** the **Source** tab with **Source Type** Zarr, the store URL,
   ``variable`` depth and ``index`` ``${Storm}``.


Step 5 — Add the plugin-backed impact layer
===========================================

This layer's features are computed per request by a plugin. There is no GeoJSON
URL — the plugin samples depth onto every building and road and returns the
result.

#. Next to **Layers**, click **Add Layer** again.

#. Go straight to the **Source** tab and set **Source Type** to **Storm Impact
   Layer (English)**. Dynamic map-layer plugins appear in the same **Source
   Type** dropdown as GeoTIFF and Zarr, listed under their plugin group.

#. The plugin's arguments appear. Fill in:

   .. list-table::
      :header-rows: 1
      :widths: 24 76

      * - Argument
        - Value
      * - ``index``
        - ``${Storm}``

#. Click **Fetch plugin defaults**.

   This is the step that saves the most work. The plugin's ``run()`` returns a
   ready-made scaffold — the layer name, the source binding, a rule-based style
   keyed on the ``banda`` (depth band) attribute, and a matching legend. After
   fetching you should see the layer named **Flooded buildings and roads**,
   eight style rules, and a four-item **Depth** legend, none of which you had to
   author. Authoring vector style rules by hand is error-prone: a rule in the
   wrong shape silently never matches and leaves every feature grey.

#. Check the **Style** and **Legend** tabs to see what arrived. Colours run
   green → yellow → red → purple across four depth bands, with separate rules
   for polygons (buildings) and linestrings (roads) so roads get a stroke wide
   enough to see.

#. Save the layer by clicking **Create** at the bottom of the layer editor.

#. In the **Map Extent** argument, choose **Use a Custom Extent** and enter:

   .. code-block:: text

      -10078413.13,1629754.90,14.83

#. On the **Settings** tab, set **Background Color** to ``#ffffff`` and add a
   border on all four sides.

   This map does *not* fill the viewport — it shares the window with the table
   and the card, so leave **Fill Viewport** off.

#. Save the item by clicking **Save** in the bottom-right corner of the map
   editor.

#. Resize the map item to fill the left half of the window by dragging the
   handle in its bottom-right corner.

#. If the map is covering the storm selector and base map selector, click on
   the 3-dot menu, hover over **Order**, and select **Send to Back**. The
   selectors should now be visible on top of the map.

#. Save the dashboard by clicking **Save Changes** in the top-right corner of
   the dashboard editor.

.. figure:: images/ex2-dynamic-layer-source.png
   :alt: The Source tab with a dynamic map-layer plugin selected
   :width: 100%

   **Screenshot:** the **Source** tab with **Storm Impact Layer (English)**
   selected, ``index`` bound to ``${Storm}``, and the **Fetch plugin defaults**
   button.

.. figure:: images/ex2-dynamic-layer-style.png
   :alt: The Style tab showing the fetched rule-based style
   :width: 100%

   **Screenshot:** the **Style** tab after fetching, showing the eight rules on
   the ``banda`` attribute.


Step 6 — Add the summary table
==============================

#. Set the dashboard in edit mode by clicking on the **Edit Dashboard** button
   in the top-right corner.

#. Add another item by clicking **Add Dashboard Item** in the top-right corner.

#. Click on the 3-dot menu of the new item and select **Edit**.

#. Set the **Visualization Type** to **Storm Impact Summary (English)** (in the
   **Flood Maps (English)** group).

#. Fill in:

   .. list-table::
      :header-rows: 1
      :widths: 24 76

      * - Argument
        - Value
      * - ``index``
        - ``${Storm}``

   The table breaks the storm's flooded features into depth bands, deepest
   first, with counts of buildings, population, area, road length and the share
   of the municipality's population affected.

#. Save the item by clicking **Save** in the bottom-right corner of the item
   editor.

#. Drag the item to the right of the map and resize it as needed.

#. Save the dashboard by clicking **Save Changes** in the top-right corner of
   the dashboard editor.


Step 7 — Add the storm card
===========================

#. Set the dashboard in edit mode, add another item, and open its 3-dot menu and
   select **Edit**, as in the previous step.

#. Set the **Visualization Type** to **Storm Summary (English)** (in the **Flood
   Maps (English)** group).

#. Fill in:

   .. list-table::
      :header-rows: 1
      :widths: 24 76

      * - Argument
        - Value
      * - ``index``
        - ``${Storm}``

   The card gives the headline figures — the storm, its magnitude, the flooded
   area and the population affected — for someone who will not read a table.

#. Save the item by clicking **Save** in the bottom-right corner of the item
   editor.

#. Drag the item below the summary table and resize it as needed.

#. Save the dashboard by clicking **Save Changes** in the top-right corner of
   the dashboard editor.

.. figure:: images/ex2-table-card.png
   :alt: The summary table and storm card
   :width: 100%

   **Screenshot:** the summary table and card for one storm.


Step 8 — Test the wiring
========================

Change the storm dropdown. All four items should update: the
Zarr layer re-reads its slice, the impact layer re-runs, and the table and card
re-fetch. Progress messages appear while the impact layer recomputes.


Checkpoint
==========

You should now have:

* A storm dropdown labelled with magnitudes in millimetres, not indices.
* Changing it updates the depth raster, the coloured buildings and roads, the
  table and the card — all four.
* A layer control listing three layers (including the base map).
* The impact layer coloured by depth band with a **Depth** legend, and roads
  visible as coloured lines rather than hairlines.


Talking points
==============

* **One variable, four consumers.** ``${Storm}`` appears in a Zarr source index,
  a plugin layer argument, and two visualization arguments. Nothing in the four
  items knows about the others; they all just declare a dependency on a name.
* **Dynamic layers re-run; static layers re-fetch.** The Zarr layer re-reads a
  slice of an existing array. The impact layer re-executes Python that samples a
  raster onto 5,000-odd geometries. Same trigger, very different cost — which is
  why the plugin reports progress while it works.
* **Labels versus values.** The dropdown shows magnitude, the plugin receives an
  index. Presenting a meaningful label over an opaque key is nearly always worth
  the indirection.
* **The magnitudes are placeholders.** They are illustrative, not measured. They
  are unique and monotonic, so they identify a storm reliably and sort sensibly,
  but do not present them as physical rainfall totals.
* **Why the plugin ships a style.** The alternative — hand-authoring eight rules
  in the GUI — fails silently when a rule is malformed. Shipping the style from
  ``run()`` means the layer is correct the first time and stays correct if the
  bands change.


Next
====

`Exercise 3 — Hazard classification with adjustable thresholds <exercise_3_en.rst>`_
turns the thresholds themselves over to the viewer.
