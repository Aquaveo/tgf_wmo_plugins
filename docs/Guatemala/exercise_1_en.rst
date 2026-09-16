.. Guatemala hands-on exercise 1 solution, English. A Spanish translation lives
.. alongside this file as exercise_1_es.rst.

==============================================================
Exercise 1 — A flood depth and probability map
==============================================================

Building **Guatemala Hands On 1 (English)** step by step.

.. contents:: On this page
   :depth: 2
   :local:
   :backlinks: none


What you are building
=====================

One map filling the window, carrying five raster layers — flood depth plus four
exceedance probabilities — and a small dropdown in the top-left corner that
switches the base map underneath them.

.. figure:: images/ex1-finished.png
   :alt: The finished exercise 1 dashboard
   :width: 100%

   **Screenshot:** the finished dashboard, layer control open so all five layers
   are visible.

This exercise is about raster layers: where the URL goes, how a colour ramp is
chosen, and the difference between letting the app scale a layer and pinning the
scale yourself.


Step 1 — Create the dashboard
=============================

#. Create a new dashboard (see
   `Creating a dashboard <getting_started_en.rst#creating-a-dashboard>`_) with:

   * **Name**: ``Guatemala Hands On 1 (English)``
   * **Description**: ``Solution for WMO Guatemala Hands On Exercise #1``

#. Find your dashboard on the landing page and double-click it to open. The
   dashboard is empty, so the preview shows a blank canvas.

#. Open **Dashboard Settings** in the top-right corner, and turn on
   **Unrestricted Grid Item Movement**. Save the settings.

#. Exit **Dashboard Settings** and click **Edit Dashboard** in the top-right
   corner to enter edit mode.


Step 2 — Add the map
====================

#. You will see an existing item on the dashboard. Click on the item's 3-dot
   menu and select **Edit**.

#. Set the **Visualization Type** to **Map** (in the **Default** group).

#. Five arguments appear: **Base Map**, **Layer Control**, **Layers**,
   **Map Extent** and **Map Drawing**. Leave them for now — you will fill them
   over the next steps.

#. In the **Base Map** argument, choose ``World Light Gray Base`` for now. You
   will update this to be dynamic in a later step.

.. figure:: images/ex1-map-args.png
   :alt: The Map visualization's arguments in the data viewer
   :width: 100%

   **Screenshot:** the **Map** visualization's five arguments, with a default
   base map selected.


Step 3 — Add the depth layer
============================

#. Next to **Layers**, click **Add Layer**. The layer editor opens with tabs
   **Layer**, **Source**, **Style**, **Legend**, **Attributes/Table Popup** and
   **Custom Modal Popup**.

#. On the **Layer** tab, set the following properties:

   .. list-table::
      :header-rows: 1
      :widths: 24 76

      * - Field
        - Value
      * - ``name``
        - ``Depth (m)``
      * - ``opacity``
        - ``.5``

#. On the **Source** tab, set **Source Type** to **GeoTIFF** and fill in:

   .. list-table::
      :header-rows: 1
      :widths: 24 76

      * - Field
        - Value
      * - ``url``
        - ``https://cog-s3-test-401506828094-us-east-1-an.s3.us-east-1.amazonaws.com/PBI_Actividad_2/depth_m.tif``
      * - ``mask_below``
        - ``0.01``

   ``mask_below`` hides cells at or below the value given. Dry ground in this
   raster is 0, and without a mask the whole domain would be painted the
   ramp's low colour instead of showing the base map.

#. On the **Style** tab, leave the mode on **Continuous** and pick the
   **YlGnBu** ramp. Leave **Min** and **Max** empty.

   Leaving both bounds empty is a deliberate choice, not laziness. An empty
   bound means "resolve it from the file's statistics at render time", so the
   ramp stretches across whatever range this particular raster holds — 0 to
   about 4.76 m here. Set both and the raw values are styled directly
   instead.

#. On the **Legend** tab, select **Default Legend**. For a ramp-styled
   raster the app generates a colour bar automatically.

#. Save the layer by clicking **Create** at the bottom of the layer editor.

.. figure:: images/ex1-layer-source-geotiff.png
   :alt: The Source tab configured for the depth GeoTIFF
   :width: 100%

   **Screenshot:** the **Source** tab with **Source Type** GeoTIFF, the depth
   URL, and ``mask_below`` 0.01.

.. figure:: images/ex1-layer-style-ramp.png
   :alt: The Style tab with the YlGnBu ramp selected
   :width: 100%

   **Screenshot:** the **Style** tab, **Continuous** mode, **YlGnBu** selected,
   **Min** and **Max** empty.


Step 4 — Add the four probability layers
========================================

These four are identical except for the URL and the name, so build one and
repeat. Add them in this order, so the deepest threshold ends up lowest in the
stack and the shallowest — which covers the largest area — ends up on top:

.. list-table::
   :header-rows: 1
   :widths: 34 66

   * - Layer **Name**
     - ``url``
   * - ``Flood Probability at 76 cm``
     - ``https://cog-s3-test-401506828094-us-east-1-an.s3.us-east-1.amazonaws.com/PBI_Actividad_2/prob_76cm.tif``
   * - ``Flood Probability at 30 cm``
     - ``https://cog-s3-test-401506828094-us-east-1-an.s3.us-east-1.amazonaws.com/PBI_Actividad_2/prob_30cm.tif``
   * - ``Flood Probability at 10 cm``
     - ``https://cog-s3-test-401506828094-us-east-1-an.s3.us-east-1.amazonaws.com/PBI_Actividad_2/prob_10cm.tif``
   * - ``Flood Probability at 7.6 cm``
     - ``https://cog-s3-test-401506828094-us-east-1-an.s3.us-east-1.amazonaws.com/PBI_Actividad_2/prob_7p62.tif``

(More information about the data is in
`The data <getting_started_en.rst#the-data>`_.)

For **each** of the four:

#. On the **Layer** tab, set the following properties:

   .. list-table::
      :header-rows: 1
      :widths: 24 76

      * - Field
        - Value
      * - ``name``
        - *see the table above*

#. On the **Source** tab, set **Source Type** to **GeoTIFF** and fill in:

   .. list-table::
      :header-rows: 1
      :widths: 24 76

      * - Field
        - Value
      * - ``url``
        - *see the table above*
      * - ``mask_below``
        - ``0``

   Zero means "no chance of flooding here".

#. On the **Style** tab, leave the mode on **Continuous** and pick the
   **turbo** ramp. Set **Min** = ``0`` and **Max** = ``1``.

   Pinning Min and Max to 0–1 is the whole point of these four layers.
   Probability has a fixed, meaningful range, and all four layers must use the
   same one or they cannot be compared. Left to auto-scale, each layer would
   stretch its ramp over its own range and 0.2 would look like a different
   severity on each — the shallow layer's mid-tone and the deep layer's
   mid-tone would mean different numbers.

#. If setting up the first layer, on the **Legend** tab, select **Default
   Legend**. For a ramp-styled raster the app generates a colour bar
   automatically.

   Only the first probability layer needs its legend enabled; the four share a
   scale, so four identical colour bars would just take up room. In the shipped
   solution the 76 cm layer carries the legend and the other three have none.

#. Save the layer by clicking **Create** at the bottom of the layer editor.

#. Save the map item by clicking **Save** in the bottom-right corner of the map
   editor.

#. Resize the map item to fill the window by dragging the handle in its
   bottom-right corner.

#. Save the dashboard by clicking **Save Changes** in the top-right corner of
   the dashboard editor.

.. figure:: images/ex1-layer-list.png
   :alt: The Layers list showing all five raster layers
   :width: 100%

   **Screenshot:** the **Layers** list with all five layers in order.


Step 5 — Add the base map selector
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


Step 6 — Update the map's base map, extent and viewport
=======================================================

#. Set the dashboard in edit mode by clicking on the **Edit Dashboard** button
   in the top-right corner.

#. Click on the 3-dot menu of the map item and select **Edit**.

#. In the **Base Map** argument, choose ``Base Map`` from the **Variable
   Inputs** section at the bottom of the dropdown. The value becomes ``${Base
   Map}``.

   See `Referencing a variable input
   <getting_started_en.rst#referencing-a-variable-input>`_ for the two forms
   this reference can take.

#. In the **Map Extent** argument, choose **Use a Custom Extent** and enter:

   .. code-block:: text

      -10078437.52,1629645.07,15

   That is ``centre-x,centre-y,zoom`` in EPSG:3857 metres.

#. On the **Settings** tab, turn on **Fill Viewport** so the map occupies the
   whole window.

#. Save the item by clicking **Save** in the bottom-right corner of the map
   editor.

#. Save the dashboard by clicking **Save Changes** in the top-right corner of
   the dashboard editor.

.. figure:: images/ex1-settings-fill-viewport.png
   :alt: The Settings tab with Fill Viewport enabled
   :width: 100%

   **Screenshot:** the **Settings** tab with **Fill Viewport** on.


Checkpoint
==========

You should now have:

* A map filling the window, showing Guatemala City.
* A layer control listing six layers (including the base map); toggling each
  changes what is drawn.
* A legend control with a colour bar for depth, and one for probability.
* A base-map dropdown top-left that changes the imagery underneath.
* Depth visible through to the probability layers beneath it, thanks to the
  0.5 opacity.


Talking points
==============

* **Auto-scaled versus pinned ramps.** Depth auto-scales because its range is a
  property of this particular event. Probability is pinned to 0–1 because the
  range is fixed by definition and the four layers must be comparable. This is
  the single most transferable idea in the exercise.
* **What** ``mask_below`` **is for.** Rasters usually encode "nothing here" as a
  real number, and unless you mask it the ramp will faithfully colour the whole
  domain. Different layers need different thresholds: ``0.01`` for depth,
  ``0`` for probability.
* **Layer order is draw order.** The first layer in the list draws lowest, just
  above the base map, and each later one paints over it. Depth goes in first and
  so sits at the bottom; the four probability layers stack above it, deepest
  threshold lowest. Nothing is hidden in practice because every layer is masked
  where it has no data — the probabilities paint only where there is a non-zero
  chance, and depth only where there is water.
* **The projection constraint.** All five rasters are EPSG:3857 copies. See the
  warning in `The data <getting_started_en.rst#the-data>`_ — this comes up again
  in exercise 3, where getting it wrong makes layers appear and then vanish.


Next
====

`Exercise 2 — Impact for a single storm <exercise_2_en.rst>`_ adds a
plugin-backed vector layer and a data-driven selector to what you have just
built.
