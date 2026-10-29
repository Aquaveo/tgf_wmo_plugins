.. Comoros hands-on exercise 2 solution, English. Built on the TITO cycle plugins:
.. a cycle list publishes ${Date}, and every plugin reads the commune, the cycle
.. and a probability. The cycle list opens on the sample cycle of 27 April 2024.
.. The plugins are the francophone `_comoros` family, so their labels and output
.. read in French.
.. The built dashboard is dashboards/Comoros/Comoros_Hands_On_2.json.

==============================================================
Exercise 2: Likely flood depth on buildings and roads
==============================================================

Building **Comores Exercice 2** step by step.

.. contents:: On this page
   :depth: 2
   :local:
   :backlinks: none


What you are building
=====================

A map on the left showing the hazard classification of a forecast cycle and the
buildings and roads it is likely to flood, coloured by depth, and on the right a
summary table and a headline card. Four controls across the top pick the base
map, the commune, the forecast cycle and the probability, and everything
re-computes.

.. figure:: images/ex2-finished.png
   :alt: The finished exercise 2 dashboard
   :width: 100%

   **Screenshot:** the finished dashboard, with the four controls, map, summary
   table and card.

New ideas here: a variable input built by a plugin (the list of forecast
cycles), a variable input whose choices are borrowed from a plugin argument (the
communes), vector layers whose features are produced by a plugin rather than
fetched from a URL, and three variables driving four separate items at once.

Exercise 1 drew **probabilities**, one raster per depth, cell by cell. This
exercise turns the same probabilities into a **depth** per building and road. A
feature's *likely depth* is the deepest of the four thresholds (10, 30, 70 and
100 cm) it reaches with at least the probability you choose. At ``0.5`` that
means "the deepest water at least half of the 50 forecast members put on this
building".

The dashboard opens on TITO's **sample cycle**, the forecast of 27 April 2024 at
00:00 UTC, so there is always a flood to look at. The same dropdown lists the
live cycles too: switch to one and every item follows.

**Tip:** ``notebooks/Comoros/02_storm_impact.ipynb`` works through flood depth on
buildings and roads as plain Python: how depth is sampled onto each feature, and
how the summary table is assembled. It still reads the earlier training files
(the storm library of the old version of this exercise) rather than the sample
cycle, so its numbers differ from the dashboard's. Worth running if you want to
understand the analysis before assembling the interface.

**Note:** The plugins are the francophone ``_comoros`` family, listed under the
**UFFIS: Comores** group with labels that start ``Comores:``, so the table and
card come back in French. That is deliberate (Comorian products are
francophone), but it is the first thing people ask about, so say it before they
do.


Step 1: Create the dashboard
============================

#. Create a new dashboard (see
   `Creating a dashboard <getting_started.rst#creating-a-dashboard>`_) with:

   * **Name**: ``Comores Exercice 2``
   * **Description**: ``Prévision TITO en direct par commune : profondeur
     probable d'inondation sur les bâtiments et routes pour le cycle et la
     probabilité choisis``

#. Find your dashboard on the landing page and double-click it to open. The
   dashboard is empty, so the preview shows a blank canvas.

#. Open **Dashboard Settings** in the top-right corner, and turn on
   **Unrestricted Grid Item Movement**. Save the settings.

#. Exit **Dashboard Settings** and click **Edit Dashboard** in the top-right
   corner to enter edit mode.


Step 2: Add the four controls
=============================

Build all four before anything that reads them. Every later item depends on at
least two. They sit in one row along the top right, each about 10 columns wide
and 6 rows tall.

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
        - ``UFFIS: Comores: Comores: Résumé d'Impact par Tempête - Commune``

   That options source is generated from an existing plugin argument, in the
   form ``<group>: <plugin label> - <Argument>``. Picking it means "offer the
   same choices the summary table's ``commune`` argument offers", so the control
   lists all **55** communes and cannot drift out of sync with the plugins.

   Its values are pcodes such as ``KM274_Moroni``, where exercise 1 stored TITO's
   site folders such as ``Comoros_Moroni``. Either works here: the plugins accept
   both forms, and nothing in this dashboard splices the commune into a URL.

#. Set **Background Color** to ``#ffffff``, set the initial value to ``Moroni``,
   save, and drag it beside the base map selector.

**The cycle list**

This control is not a **Variable Input** at all. It is a plugin that builds the
dropdown itself, from the cycles TITO currently publishes.

#. Add a third item, open its 3-dot menu and select **Edit**, and set the
   **Visualization Type** to **Comores: Cycles Disponibles** (in the
   **UFFIS: Comores** group).

#. Fill in:

   .. list-table::
      :header-rows: 1
      :widths: 32 68

      * - Argument
        - Value
      * - ``debut``
        - ``sample`` (shown as **Cycle d'exemple le plus récent**)
      * - ``texte_etiquette``
        - *leave empty*
      * - ``afficher_etiquette``
        - *leave as it is*

   The dropdown lists every hourly cycle TITO still publishes, newest first
   (about a day's worth), and then the sample cycles. A live cycle reads like
   ``2026-10-29 12:00 UTC``; the sample reads
   ``2024-04-27 00:00 UTC, ÉCHANTILLON``. ``debut`` picks where it starts:
   ``sample`` opens on the sample, ``latest`` on the newest live cycle. For a
   workshop the sample is the safe choice, because a quiet day has no flood to
   show.

   ``texte_etiquette`` is the label, and also the name of the variable the item
   publishes. Left empty, the variable is ``Date``, which is what the plugins
   below bind to.

#. Save the item and drag it to the right of the commune selector.

.. figure:: images/ex2-storm-input.png
   :alt: The cycle list plugin configuration
   :width: 100%

   **Screenshot:** the **Comores: Cycles Disponibles** arguments, with ``debut``
   set to the sample cycle.

**The probability input**

#. Add a fourth item, open its 3-dot menu and select **Edit**, and set the
   **Visualization Type** to **Variable Input**.

#. Fill in:

   .. list-table::
      :header-rows: 1
      :widths: 32 68

      * - Argument
        - Value
      * - ``variable_name``
        - ``Probabilité``
      * - ``show_label``
        - ``True``
      * - ``variable_options_source``
        - ``number``

#. Set the initial value to ``0.5``. The shipped item also limits the input to
   ``0.05``-``1`` in steps of ``0.05``.

#. Save the item and drag it to the far right of the top row.


Step 3: Add the map with the hazard layer
=========================================

#. Add another item, open its 3-dot menu and select **Edit**, and set the
   **Visualization Type** to **Map** (in the **Default** group).

#. In the **Base Map** argument, choose ``Base Map`` from the **Variable
   Inputs** section at the bottom of the dropdown. The value becomes
   ``${Fond de Carte}``.

#. Turn **Layer Control** on.

#. Next to **Layers**, click **Add Layer**.

#. Go straight to the **Source** tab and set **Source Type** to
   **Comores: Couche d'Aléa**. Dynamic map-layer plugins appear in the same
   **Source Type** dropdown as GeoTIFF, listed under their plugin group.

#. The plugin's arguments appear. Fill in:

   .. list-table::
      :header-rows: 1
      :widths: 24 76

      * - Argument
        - Value
      * - ``commune``
        - ``${Commune}``
      * - ``cycle``
        - ``${Date}``

   Leave the four gates (``seuil_faible`` and the rest) and
   ``source_inondation`` unset. The gates then take the plugin's defaults, 0.3,
   0.2, 0.1 and 0.15 from Faible to Sévère, and the rasters the
   ``pluvial_overbank`` variant of exercise 1. Exercise 3 puts the four gates on
   the dashboard; here the layer is context for the buildings drawn over it.

#. Click **Fetch plugin defaults**. The layer is named **Classification de
   l'aléa**, styled with four rules on the ``alea`` attribute, and given a
   four-item **Aléa** legend.

#. Save the layer by clicking **Create** at the bottom of the layer editor.

.. figure:: images/ex2-zarr-source.png
   :alt: The Source tab configured for the hazard layer plugin
   :width: 100%

   **Screenshot:** the **Source** tab with **Comores: Couche d'Aléa** selected,
   ``commune`` bound to ``${Commune}`` and ``cycle`` to ``${Date}``.


Step 4: Add the likely-depth layer
==================================

This layer's features are computed per request by a plugin. There is no GeoJSON
URL: the plugin reads the cycle's buildings and roads for the commune, each
carrying its four probabilities, works out each one's likely depth, and returns
the ones that reach at least 10 cm.

#. Next to **Layers**, click **Add Layer** again.

#. Go straight to the **Source** tab and set **Source Type** to **Comores:
   Couche d'Impact par Tempête**.

#. The plugin's arguments appear. Fill in:

   .. list-table::
      :header-rows: 1
      :widths: 30 70

      * - Argument
        - Value
      * - ``commune``
        - ``${Commune}``
      * - ``cycle``
        - ``${Date}``
      * - ``probabilite_minimale``
        - ``${Probabilité}``

#. Click **Fetch plugin defaults**.

   This is the step that saves the most work. The plugin's ``run()`` returns a
   ready-made scaffold: the layer name, the source binding, a rule-based style
   keyed on the ``bande`` (depth band) attribute, and a matching legend. After
   fetching you should see the layer named **Profondeur probable sur les
   bâtiments et routes**, eight style rules and a four-item **Profondeur**
   legend, none of which you had to author. Authoring vector style rules by hand
   is error-prone: a rule in the wrong shape silently never matches and leaves
   every feature grey.

#. Check the **Style** and **Legend** tabs to see what arrived. Colours run
   green, yellow, red, purple across the four bands (``0.1 - 0.3 m``,
   ``0.3 - 0.7 m``, ``0.7 - 1 m`` and ``1 m ou plus``), with separate rules for
   polygons (buildings) and linestrings (roads) so roads get a stroke wide
   enough to see.

#. Save the layer by clicking **Create** at the bottom of the layer editor.

#. In the **Map Extent** argument, choose **Use a Custom Extent** and enter:

   .. code-block:: text

      4814984.15,-1312113.30,13.83

   That is ``centre-x,centre-y,zoom`` in EPSG:3857 metres, centred on Moroni.

   **Warning:** As in exercise 1, **the extent does not follow the commune**.
   Switch to a commune on another island and the view stays over Moroni until you
   pan. The layers reload correctly; only the camera is fixed.

#. Save the item, then resize the map to fill roughly the left 60% of the window,
   leaving the right-hand strip for the controls, the table and the card.

#. Save the dashboard by clicking **Save Changes** in the top-right corner.

.. figure:: images/ex2-dynamic-layer-source.png
   :alt: The Source tab with a dynamic map-layer plugin selected
   :width: 100%

   **Screenshot:** the **Source** tab with the likely-depth layer selected,
   ``commune``, ``cycle`` and ``probabilite_minimale`` bound, and the **Fetch
   plugin defaults** button.

.. figure:: images/ex2-dynamic-layer-style.png
   :alt: The Style tab showing the fetched rule-based style
   :width: 100%

   **Screenshot:** the **Style** tab after fetching, showing the eight rules on
   the ``bande`` attribute.


Step 5: Add the summary table
=============================

#. Set the dashboard in edit mode, add another item, open its 3-dot menu and
   select **Edit**.

#. Set the **Visualization Type** to **Comores: Résumé d'Impact par Tempête**
   (in the **UFFIS: Comores** group).

#. Fill in:

   .. list-table::
      :header-rows: 1
      :widths: 30 70

      * - Argument
        - Value
      * - ``commune``
        - ``${Commune}``
      * - ``cycle``
        - ``${Date}``
      * - ``probabilite_minimale``
        - ``${Probabilité}``

   The table breaks the flooded features into the same four depth bands,
   deepest first, then a **TOTAL affecté** row, with counts of buildings,
   population, area, road length and the share of the population affected. The
   share is of the people living in the **commune's** buildings, as counted in its
   receptor file, not the island's or the country's, which is why the commune
   has to reach the plugin as an argument rather than being baked in.

   The title names the probability and the cycle, for example **Profondeur
   probable, probabilité ≥ 50% (2024-04-27 00:00 UTC, ÉCHANTILLON)**, so a
   screenshot of the table can never be mistaken for a live forecast.

#. Save the item and drag it below the controls, on the right.


Step 6: Add the storm card
==========================

#. Add another item, open its 3-dot menu and select **Edit**.

#. Set the **Visualization Type** to **Comores: Résumé de Tempête** (in the same
   group), and bind the same three arguments:

   .. list-table::
      :header-rows: 1
      :widths: 30 70

      * - Argument
        - Value
      * - ``commune``
        - ``${Commune}``
      * - ``cycle``
        - ``${Date}``
      * - ``probabilite_minimale``
        - ``${Probabilité}``

   The card gives the headline figures for someone who will not read a table:
   the forecast rainfall over the commune (median and wettest of the 50
   members), the area flooded to at least 0.1 m with the chosen probability, and
   the people and buildings **expected** to get at least 0.3 m. An expected count
   adds up each feature's probability, so it does not depend on the probability
   input. A commune the cycle did not trigger shows a single **Calme : non
   déclenchée** line instead.

#. Save the item and drag it below the summary table.

#. Save the dashboard by clicking **Save Changes** in the top-right corner.

.. figure:: images/ex2-table-card.png
   :alt: The summary table and storm card
   :width: 100%

   **Screenshot:** the summary table and card for Moroni on the sample cycle.


Step 7: Test the wiring
=======================

On the sample cycle, with **Moroni** and **Probabilité** at ``0.5``, you should
see:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Item
     - What it shows
   * - Card
     - Rainfall ``92 / 285 mm`` (median / wettest member); area flooded
       ≥ 0.1 m (P ≥ 50%) ``1.10 km²``; ``1,647`` people and ``500`` buildings
       expected with ≥ 0.3 m.
   * - Table
     - **TOTAL affecté**: 1,569 buildings, 5,805 people, 16.8 km of roads,
       8.33% of the population.
   * - Likely-depth layer
     - 1,677 buildings and roads, reported in the progress message as it loads.

Then try each control:

* **Probabilité.** The likely-depth layer, the table and the card's flooded area
  update; the hazard layer does not, because it does not take the probability.
  Lower it and features turn deeper and more numerous; raise it and only what
  most members agree on is left.
* **Commune.** All four plugin items reload against a different commune's
  buildings, roads and rasters. Only the camera stays put.
* **Date.** All four plugin items re-read a different cycle. On a live cycle
  many communes are quiet; the card then says so and the layers come back
  empty, which is an answer rather than a failure.


Item positions
==============

The shipped solution, for reference. You do not need to match these to the
pixel: drag to something close and adjust.

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
   * - Fond de Carte (variable input)
     - 60
     - 0
     - 10
     - 6
   * - Commune (variable input)
     - 70
     - 0
     - 10
     - 6
   * - Cycles Disponibles (cycle list)
     - 80
     - 0
     - 10
     - 6
   * - Probabilité (variable input)
     - 90
     - 0
     - 10
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

Unlike exercise 1, the map does **not** fill the viewport here: it shares the
window with the controls, the table and the card, so leave **Fill Viewport**
off.


Checkpoint
==========

You should now have:

* Four controls across the top right: base map, commune, cycle and probability.
* The cycle dropdown opening on ``2024-04-27 00:00 UTC, ÉCHANTILLON``, with the
  live cycles listed above it.
* A map on the left with two layers plus the base map in the layer control.
* The hazard classification shaded underneath, and buildings and roads coloured
  by likely depth over the top, with a **Profondeur** legend, and roads visible
  as coloured lines rather than hairlines.
* A summary table and a card on the right, both in French, both updating with
  every control except the base map.
* Changing the commune swapping the whole dataset (features, rasters and
  denominators) while the view stays where it was.


Talking points
==============

* **Three variables, four consumers.** ``${Commune}`` and ``${Date}`` reach all
  four plugin items; ``${Probabilité}`` reaches three of them. Nothing in the
  seven items knows about the others; they all just declare a dependency on a
  name.
* **A plugin can be a control.** The cycle list is built when the dashboard
  loads, from what TITO publishes at that moment, so nobody maintains a list of
  dates. Live cycles are kept for about a day; the sample cycle stays, which is
  why a training dashboard opens on it.
* **Borrowed choices.** The commune dropdown takes its choices from a plugin
  argument, so the dashboard and the plugin cannot disagree about which
  communes exist. Exercise 1 had to supply its own list, because its values had
  to match folder names in a URL.
* **Likely depth is a choice of confidence.** "Likely depth at 0.5" is the
  deepest threshold at least half the members reach on that feature. At 0.2 the
  map shows what a pessimist plans for; at 0.8 what nearly every member agrees
  on. Which would you put in front of a civil-protection officer, and what would
  you say about the other?
* **Likely counts versus expected counts.** The table counts the features whose
  likely depth clears a band at the chosen probability. The card's expected
  people and buildings add up probabilities instead, so they do not move with
  the input. Both are honest; they answer different questions, and the
  difference is worth showing on screen.
* **Dynamic layers re-run.** Every change re-executes Python that reads the
  cycle's receptor file and classifies every building and road in the commune.
  Same trigger as a static layer, very different cost, which is why the plugins
  report progress while they work.
* **Why the plugin ships a style.** The alternative, hand-authoring eight rules
  in the GUI, fails silently when a rule is malformed. Shipping the style from
  ``run()`` means the layer is correct the first time and stays correct if the
  bands change.


Next
====

Exercise 3 turns the probability thresholds of the hazard layer over to the
viewer, using the hazard and impact layers that classify against the four
exceedance rasters of exercise 1.
