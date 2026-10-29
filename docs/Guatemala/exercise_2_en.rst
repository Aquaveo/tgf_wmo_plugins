.. Guatemala hands-on exercise 2 solution, English. A Spanish translation lives
.. alongside this file as exercise_2_es.rst.

==============================================================
Exercise 2: Likely impact for a forecast cycle
==============================================================

Building **Guatemala Hands On 2 (English)** step by step.

.. contents:: On this page
   :depth: 2
   :local:
   :backlinks: none


What you are building
=====================

A map on the left showing every building and road coloured by the flood depth it
is likely to reach, and on the right a table and a card summarising the same
forecast. Two inputs across the top drive everything: a **Date** dropdown that
picks the TITO cycle, opening on the sample cycle, and a **Probability** number
that sets how sure the forecast must be. Change either and the layer, the table
and the card all recompute.

.. figure:: images/ex2-finished.png
   :alt: The finished exercise 2 dashboard
   :width: 100%

   **Screenshot:** the finished dashboard, with the Date and Probability inputs,
   the map, the summary table and the card.

For every building and road, a TITO cycle publishes the probability that the
water reaches 10, 30, 70 and 100 cm. A feature's *likely depth* is the deepest of
those it reaches with at least the chosen probability. At a Probability of 0.5,
a building whose chance of 30 cm is 0.6 and whose chance of 70 cm is 0.4 is
coloured as 0.3 - 0.7 m.

New ideas here: a dropdown whose choices come from a plugin, a vector layer whose
features are produced by a plugin rather than fetched from a URL, and two
variable inputs driving three separate items at once.

**Tip:** ``notebooks/Guatemala/02_storm_impact.ipynb`` shows as plain Python how
depth is sampled onto each building and road and how a summary table is
assembled. The notebook still uses the earlier training files, so its numbers
differ from this dashboard's.


Step 1: Create the dashboard
============================

#. Create a new dashboard (see
   `Creating a dashboard <getting_started_en.rst#creating-a-dashboard>`_) with:

   * **Name**: ``Guatemala Hands On 2 (English)``
   * **Description**: ``Live TITO forecast for Santa Inés Petapa: likely flood depth on buildings and roads for the chosen cycle and probability``

#. Find your dashboard on the landing page and double-click it to open. The
   dashboard is empty, so the preview shows a blank canvas.

#. Open **Dashboard Settings** in the top-right corner, and turn on
   **Unrestricted Grid Item Movement**. Save the settings.

#. Exit **Dashboard Settings** and click **Edit Dashboard** in the top-right
   corner to enter edit mode.


Step 2: Add the cycle selector
==============================

#. You will see an existing item on the dashboard. Click on the item's 3-dot
   menu and select **Edit**.

#. Set the **Visualization Type** to **Guatemala: Ciclos Disponibles**
   (Available Cycles, in the **UFFIS: Guatemala** group).

#. Fill in:

   .. list-table::
      :header-rows: 1
      :widths: 32 68

      * - Argument
        - Value
      * - ``inicio``
        - **Ciclo de muestra más reciente** (``sample``)

   Leave ``mostrar_etiqueta`` and ``texto_etiqueta`` at their defaults.

   This item is a variable input built by a plugin. It publishes a variable
   named ``Date`` and fills its dropdown with every live TITO cycle still
   published, newest first, followed by the sample cycles, which are marked
   ``MUESTRA`` (for example ``2026-10-16 22:00 UTC, MUESTRA``). Each value is
   the cycle stamp the URLs use, such as ``20261016.220000``.

   ``inicio`` sets the entry the dropdown opens on. ``sample`` opens on the
   newest sample cycle, so the dashboard shows the same event in every session.
   **Último ciclo en vivo** (``latest``) opens on the newest live cycle instead;
   live cycles are only kept for a short time, and a cycle with no flood forecast
   has nothing to show.

#. Save the item by clicking **Save** in the bottom-right corner of the item
   editor.

#. Drag the item to the top of the dashboard and resize it as needed. Leave room
   to its left for the base map selector.

#. Save the dashboard by clicking **Save Changes** in the top-right corner of
   the dashboard editor.

.. figure:: images/ex2-storm-input.png
   :alt: The cycle selector configuration
   :width: 100%

   **Screenshot:** the **Guatemala: Ciclos Disponibles** arguments, with
   ``inicio`` set to **Ciclo de muestra más reciente**.


Step 3: Add the probability input
=================================

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
        - ``Probability``
      * - ``show_label``
        - ``True``
      * - ``variable_options_source``
        - ``number``

   The shipped solution limits the number to the range 0.05 to 1 in steps of
   0.05.

#. Set the initial value to ``0.5`` in the preview on the right side of the
   editor.

   A feature only counts as reaching a depth if at least this fraction of the 50
   ensemble members puts that much water on it. At 0.5 that means at least half
   of them. Lower it and more features appear, in deeper bands; raise it and
   only the surest remain.

#. Save the item by clicking **Save** in the bottom-right corner of the item
   editor.

#. Drag the item to the top of the dashboard, to the right of the cycle
   selector, and resize it as needed.

#. Save the dashboard by clicking **Save Changes** in the top-right corner of
   the dashboard editor.

.. figure:: images/ex2-zarr-source.png
   :alt: The probability variable input configuration
   :width: 100%

   **Screenshot:** the **Variable Input** arguments for the Probability input,
   with ``number`` as the options source and an initial value of 0.5.


Step 4: Add the base map selector
=================================

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

   ``Base Map Layers`` is a built-in options source: it fills the dropdown with
   the base maps the instance offers, so you do not enumerate them yourself.

#. On the **Settings** tab, set **Background Color** to ``#ffffff``. Without it
   the dropdown floats on the map with no backing and is hard to read.

#. Select an initial value for the dropdown from the preview on the right side
   of the editor. The shipped solution uses ``World Imagery``, but any base map
   is fine.

#. Save the item by clicking **Save** in the bottom-right corner of the item
   editor.

#. Drag the item to the top-left corner and resize it as needed.

#. Save the dashboard by clicking **Save Changes** in the top-right corner of
   the dashboard editor.

   You now have a base map selector on the dashboard, but nothing uses it yet.

.. figure:: images/ex1-variable-input-basemap.png
   :alt: The base map variable input configuration
   :width: 100%

   **Screenshot:** the **Variable Input** arguments for the base map selector.


Step 5: Add the map with the likely-depth layer
===============================================

This layer's features are computed per request by a plugin. There is no GeoJSON
URL: the plugin reads the chosen cycle's buildings and roads, works out each
one's likely depth and returns the result.

#. Set the dashboard in edit mode by clicking on the **Edit Dashboard** button
   in the top-right corner.

#. Add another item by clicking **Add Dashboard Item** in the top-right corner.

#. Click on the 3-dot menu of the new item and select **Edit**.

#. Set the **Visualization Type** to **Map** (in the **Default** group).

#. In the **Base Map** argument, choose ``Base Map`` from the **Variable
   Inputs** section at the bottom of the dropdown. The value becomes
   ``${Base Map}``.

#. Next to **Layers**, click **Add Layer**.

#. Go straight to the **Source** tab and set **Source Type** to
   **Guatemala: Capa de Impacto por Tormenta** (Storm Impact Layer). Dynamic
   map-layer plugins appear in the same **Source Type** dropdown as GeoTIFF,
   listed under their plugin group.

#. The plugin's arguments appear. Fill in:

   .. list-table::
      :header-rows: 1
      :widths: 30 70

      * - Argument
        - Value
      * - ``ciclo``
        - ``${Date}``
      * - ``probabilidad_minima``
        - ``${Probability}``

   ``ciclo`` is a dropdown, so pick ``Date`` from its **Variable Inputs**
   section; its own fixed choices (**Último ciclo**, **Evento de muestra**)
   would pin the layer to one cycle. ``probabilidad_minima`` is a number field,
   so type ``${Probability}``. See `Referencing a variable input
   <getting_started_en.rst#referencing-a-variable-input>`_.

#. Click **Fetch plugin defaults**.

   This is the step that saves the most work. The plugin's ``run()`` returns a
   ready-made scaffold: the layer name, the source binding, a rule-based style
   keyed on the ``banda`` (depth band) attribute, and a matching legend. After
   fetching you should see the layer named **Profundidad probable en edificios
   y carreteras** (likely flood depth on buildings and roads), eight style
   rules, and a four-item **Profundidad** legend, none of which you had to
   author. The names arrive in Spanish because Guatemala's plugins speak
   Spanish; rename the layer on the **Layer** tab if you like. Authoring vector
   style rules by hand is error-prone: a rule in the wrong shape silently never
   matches and leaves every feature grey.

#. Check the **Style** and **Legend** tabs to see what arrived. Colours run
   green, yellow, red and purple across four bands (0.1 - 0.3 m, 0.3 - 0.7 m,
   0.7 - 1 m and 1 m or more), with separate rules for polygons (buildings) and
   linestrings (roads) so roads get a stroke wide enough to see.

#. Save the layer by clicking **Create** at the bottom of the layer editor.

#. In the **Map Extent** argument, choose **Use a Custom Extent** and enter:

   .. code-block:: text

      -10078413.13,1629754.90,14.83

#. On the **Settings** tab, set **Background Color** to ``#ffffff`` and add a
   border on all four sides.

   This map does *not* fill the viewport: it shares the window with the table
   and the card, so leave **Fill Viewport** off.

#. Save the item by clicking **Save** in the bottom-right corner of the map
   editor.

#. Resize the map item to fill the left half of the window by dragging the
   handle in its bottom-right corner.

#. If the map is covering the three inputs, click on the 3-dot menu, hover over
   **Order**, and select **Send to Back**. The inputs should now be visible on
   top of the map.

#. Save the dashboard by clicking **Save Changes** in the top-right corner of
   the dashboard editor.

.. figure:: images/ex2-dynamic-layer-source.png
   :alt: The Source tab with a dynamic map-layer plugin selected
   :width: 100%

   **Screenshot:** the **Source** tab with **Guatemala: Capa de Impacto por
   Tormenta** selected, ``ciclo`` bound to ``${Date}``, ``probabilidad_minima``
   bound to ``${Probability}``, and the **Fetch plugin defaults** button.

.. figure:: images/ex2-dynamic-layer-style.png
   :alt: The Style tab showing the fetched rule-based style
   :width: 100%

   **Screenshot:** the **Style** tab after fetching, showing the eight rules on
   the ``banda`` attribute.


Step 6: Add the summary table
=============================

#. Set the dashboard in edit mode by clicking on the **Edit Dashboard** button
   in the top-right corner.

#. Add another item by clicking **Add Dashboard Item** in the top-right corner.

#. Click on the 3-dot menu of the new item and select **Edit**.

#. Set the **Visualization Type** to **Guatemala: Resumen de Impacto por
   Tormenta** (Storm Impact Summary, in the **UFFIS: Guatemala** group).

#. Fill in the same two arguments as the layer:

   .. list-table::
      :header-rows: 1
      :widths: 30 70

      * - Argument
        - Value
      * - ``ciclo``
        - ``${Date}``
      * - ``probabilidad_minima``
        - ``${Probability}``

   The table breaks the flooded features into the same four likely-depth bands,
   deepest first, then a **TOTAL afectado** row, with counts of buildings,
   population, area, road length and the share of the population affected. The
   title names the probability and the cycle, for example
   ``Profundidad probable, probabilidad ≥ 50% (2026-10-16 22:00 UTC, MUESTRA)``.
   A TITO cycle carries no census figure, so the share is of the people in the
   site's own building stock.

#. Save the item by clicking **Save** in the bottom-right corner of the item
   editor.

#. Drag the item to the right of the map and resize it as needed.

#. Save the dashboard by clicking **Save Changes** in the top-right corner of
   the dashboard editor.


Step 7: Add the forecast card
=============================

#. Set the dashboard in edit mode, add another item, and open its 3-dot menu and
   select **Edit**, as in the previous step.

#. Set the **Visualization Type** to **Guatemala: Resumen de Tormenta** (Storm
   Summary, in the **UFFIS: Guatemala** group).

#. Fill in the same two arguments again: ``ciclo`` = ``${Date}`` and
   ``probabilidad_minima`` = ``${Probability}``.

   The card gives the headline figures for someone who will not read a table:
   the forecast rainfall (median and wettest ensemble member), the area flooded
   to at least 0.1 m at the chosen probability, and the people and buildings
   expected to get at least 0.3 m of water. When a cycle did not trigger a
   flood forecast for the site, the card shows a single status line instead.

#. Save the item by clicking **Save** in the bottom-right corner of the item
   editor.

#. Drag the item below the summary table and resize it as needed.

#. Save the dashboard by clicking **Save Changes** in the top-right corner of
   the dashboard editor.

.. figure:: images/ex2-table-card.png
   :alt: The summary table and forecast card
   :width: 100%

   **Screenshot:** the summary table and card for the sample cycle at a
   Probability of 0.5.


Step 8: Test the wiring
=======================

Change the Probability. The layer, the table and the card should all update,
with progress messages while the layer recomputes. The rainfall on the card
stays put, because it does not depend on probability.

Then pick a live cycle from the Date dropdown. All three items re-read that
cycle. A cycle with no flood forecast for the site gives an empty layer and a
card with only a status line. Switch back to the sample cycle when you are done.


Checkpoint
==========

You should now have:

* A Date dropdown that opens on ``2026-10-16 22:00 UTC, MUESTRA``.
* At a Probability of 0.5 on the sample cycle: 704 coloured buildings and roads;
  a table whose **TOTAL afectado** row shows 543 buildings and 1,644 people; and
  a card showing 21 / 36 mm of rain, 0.13 km² flooded and 1,178 people expected
  with at least 0.3 m.
* Changing the Probability or the Date updates the layer, the table and the
  card: all three.
* A layer control listing two layers (including the base map).
* The layer coloured by likely depth with a **Profundidad** legend, and roads
  visible as coloured lines rather than hairlines.


Talking points
==============

* **Two variables, three consumers.** ``${Date}`` and ``${Probability}`` each
  appear in a plugin layer argument and two visualization arguments. Nothing in
  the three items knows about the others; they all just declare a dependency on
  a name.
* **Sample versus live.** The sample cycle has exactly the layout of a live one,
  so this dashboard is a live dashboard already: only the Date changes. The
  sample is there because live cycles come and go quickly and a quiet one has
  nothing to show, which makes a poor exercise.
* **Two ways to count people.** The table's 1,644 people are everyone in the
  buildings whose likely depth is at least 0.1 m at the chosen probability. The
  card's 1,178 are an *expected* number: each person counts by their own chance
  of 0.3 m, so the figure does not move with the Probability input. They answer
  different questions, and both are worth showing.
* **Dynamic layers re-run.** Every change re-executes Python that reads the
  cycle's files and classifies every building and road at the site, which is
  why the plugin reports progress while it works.
* **Why the plugin ships a style.** The alternative, hand-authoring eight rules
  in the GUI, fails silently when a rule is malformed. Shipping the style from
  ``run()`` means the layer is correct the first time and stays correct if the
  bands change.


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
     - 54
     - 38
   * - Base Map input
     - 0
     - 0
     - 15
     - 6
   * - Cycle selector (Date)
     - 15
     - 0
     - 20
     - 6
   * - Probability input
     - 42
     - 0
     - 12
     - 6
   * - Summary table
     - 54
     - 2
     - 45
     - 26
   * - Forecast card
     - 54
     - 23
     - 46
     - 13


Next
====

`Exercise 3: Hazard classification with adjustable thresholds <exercise_3_en.rst>`_
turns the thresholds themselves over to the viewer.
