.. Comoros hands-on exercise 3 solution, English. Adapted from the Guatemala
.. guide at ../Guatemala/exercise_3_en.rst. What differs is explained where it
.. comes up: a fifth control picks the commune, because every Comoros product is
.. per commune; the Severe gate needs no special case here; and the plugins are
.. the francophone `_comoros` family, so their labels read in French. Every
.. plugin reads the TITO sample cycle of 27 April 2024 (``cycle`` = ``sample``).
.. The built dashboard is dashboards/Comoros/Comoros_Hands_On_3.json.

==============================================================
Exercise 3: Hazard classification with adjustable thresholds
==============================================================

Building **Comores Exercice 3** step by step.

**Start here:** This exercise reuses the four probability layers from
`Exercise 1 <exercise_1.rst>`_, so building that one first will save you time.

.. contents:: On this page
   :depth: 2
   :local:
   :backlinks: none


What you are building
=====================

A full-window map carrying the four probability rasters from exercise 1 plus two
computed layers: a hazard classification and the buildings and roads that fall
inside it. Four number inputs across the top set the probability threshold for
each hazard level, a commune dropdown picks where, and an impact table sits under
the thresholds. Change a threshold and the classification, the affected features
and the table all recompute.

.. figure:: images/ex3-finished.png
   :alt: The finished exercise 3 dashboard
   :width: 100%

   **Screenshot:** the finished dashboard: full-window map, four threshold
   inputs along the top, commune selector top-left, impact table on the right.

**Tip:** ``notebooks/Comoros/03_hazard_classification.ipynb`` derives this
classification as plain Python, including the percent-scale trap and the commune
filter that the plugins now handle for you. Worth running first if you want to
understand the analysis before assembling the interface. The notebook still reads
the earlier training files rather than the sample cycle, so its numbers may
differ from the dashboard's.


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
   * - Faible (Low)
     - P(≥ 10 cm)
     - green
     - 0.8
   * - Moyen (Medium)
     - P(≥ 30 cm)
     - yellow
     - 0.8
   * - Élevé (High)
     - P(≥ 70 cm)
     - red
     - 0.8
   * - Sévère (Severe)
     - P(≥ 100 cm)
     - purple
     - 0.8

A cell takes the level of the **deepest** threshold whose gate it clears.

**Note:** **All four gates can sit at 0.8 here, and that is worth saying out
loud** if you have taught the Guatemala version. There the 76 cm raster only ever
holds 0 or 0.2, so its Severe gate has to be dropped to 0.2 or the class can
never appear at all. In Moroni every layer of the sample cycle reaches 1.0, and
cells clear 0.8 at every depth (861 cells at 10 cm, 82 at 30 cm, 8 at 70 cm and
2 at 100 cm), so nothing has to be weakened to make the top level mean
something. The lesson survives the
difference: check what range a layer can actually reach before you expose a
control for it.


Step 1: Create the dashboard
============================

#. Create a new dashboard (see
   `Creating a dashboard <getting_started.rst#creating-a-dashboard>`_) with:

   * **Name**: ``Comores Exercice 3``
   * **Description**: ``Solution pour l'exercice pratique OMM Comores n°3``

#. Find your dashboard on the landing page and double-click it to open.

#. Open **Dashboard Settings** in the top-right corner, and turn on
   **Unrestricted Grid Item Movement**. Save the settings.

#. Exit **Dashboard Settings** and click **Edit Dashboard** to enter edit mode.


Step 2: Add the base map and commune selectors
==============================================

Both are exactly as in exercise 1, so if you built that dashboard the quickest
route is **Export** on each item's 3-dot menu and **Import Dashboard Item** here.

Building them fresh:

#. Click the existing item's 3-dot menu, select **Edit**, and set the
   **Visualization Type** to **Variable Input**.

#. Fill in ``variable_name`` ``Fond de Carte``, ``show_label`` ``True``,
   ``variable_options_source`` ``Base Map Layers``. Set **Background Color** to
   ``#ffffff``, pick **World Imagery**, save, and drag it to the top-left.

#. Add another item, set it to **Variable Input**, and fill in ``variable_name``
   ``Commune``, ``show_label`` ``True``, ``variable_options_source``
   ``dropdown``.

#. Fill the **choices** editor with the communes, label and value as in
   exercise 1: ``Moroni`` / ``Comoros_Moroni`` and so on. The value is TITO's
   site folder, because the four raster URLs splice it into their path; the
   plugins in steps 5, 6 and 8 accept that form too (as well as the pcode form,
   ``KM274_Moroni``), so one ``${Commune}`` feeds both.

   **Note:** The shipped solution carries only **22 communes**, everything from
   ``Comoros_Ngouengoe`` onward, a list inherited from an earlier version of
   exercise 2. This exercise reads only the probability rasters and the receptor
   geopackage, and the sample cycle publishes **both for all 55**, so the list can
   safely be widened here. Exercise 1 already offers all 55 if you would rather
   import that item instead.

#. Set **Background Color** to ``#ffffff``, set the initial value to ``Moroni``,
   save, and drag it beside the base map selector.


Step 3: Add the four threshold inputs
=====================================

Build all four before the layers that consume them. Each is a **Variable Input**
with ``variable_options_source`` set to ``number``:

.. list-table::
   :header-rows: 1
   :widths: 100

   * - ``variable_name``
   * - ``Seuil Faible (P(≥10 cm))``
   * - ``Seuil Moyen (P(≥30 cm))``
   * - ``Seuil Élevé (P(≥70 cm))``
   * - ``Seuil Sévère (P(≥100 cm))``

For **each** of the four:

#. Add a dashboard item, open its 3-dot menu and select **Edit**, and set the
   **Visualization Type** to **Variable Input**.

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

#. On the **Settings** tab, set **Background Color** to ``#ffffff`` and add a
   top border, changing its style to ``solid`` so it shows. Give the leftmost
   input a left border and the rightmost a right border as well, so the four read
   as one strip.

#. Set the initial value to ``0.8``.

#. Save the item and drag it into place along the top of the dashboard, to the
   right of the commune selector.

The names carry the depth they gate, ``(P(≥10 cm))`` and so on, because the
plugin argument they bind to is called only ``seuil_faible``. Without the depth
in the variable name, nothing on the dashboard says which threshold does what.

.. figure:: images/ex3-threshold-inputs.png
   :alt: The four threshold variable inputs across the top of the dashboard
   :width: 100%

   **Screenshot:** the four threshold inputs side by side, each showing its
   label and value.


Step 4: Add the map and the four probability rasters
====================================================

If you have exercise 1, reuse its map:

#. Open the exercise 1 dashboard, click the map item's 3-dot menu, choose
   **Export**.

#. Back in this dashboard, click **Import Dashboard Item** and import it.

#. Edit the map item. For each of the four rasters, open the layer and turn off
   **Default Visibility** on the **Layer** tab, so the classification is what
   shows on load and the rasters are there to switch on for comparison. Save each
   layer.

#. On each raster's **Source** tab, set ``mask_below`` back to ``0``. Exercise 1
   bound it to a ``Masque de Probabilité`` input that does not exist here (the
   thresholds do that filtering now), and an unresolved variable leaves the
   field empty.

If you do not have exercise 1, build the map and the four rasters from scratch as
described there, then carry on. Either way the four URLs point at the sample
cycle, ``https://tito.uffis.org/sample/comoros/20240427.000000/``, which is the
same cycle the plugins below read.

#. If the map is covering the inputs, click its 3-dot menu, hover over **Order**,
   and select **Send to Back**.

#. Save the dashboard.


Step 5: Add the hazard classification layer
===========================================

#. Set the dashboard in edit mode, then click the map item's 3-dot menu and
   select **Edit**. You may need to move a threshold input out of the way to
   reach the map's menu.

#. Next to **Layers**, click **Add Layer**.

#. Go straight to the **Source** tab and set **Source Type** to
   **Comores: Couche d'Aléa** (listed under the **UFFIS: Comores** group).

#. The plugin's arguments appear. Fill in:

   .. list-table::
      :header-rows: 1
      :widths: 30 70

      * - Argument
        - Value
      * - ``seuil_faible``
        - ``${Seuil Faible (P(≥10 cm))}``
      * - ``seuil_moyen``
        - ``${Seuil Moyen (P(≥30 cm))}``
      * - ``seuil_eleve``
        - ``${Seuil Élevé (P(≥70 cm))}``
      * - ``seuil_severe``
        - ``${Seuil Sévère (P(≥100 cm))}``
      * - ``commune``
        - ``${Commune}``
      * - ``cycle``
        - ``sample`` (shown as **Événement d'exemple** in the dropdown)

   Six arguments, not four. Every Comoros product is written per commune, so the
   plugin cannot know which rasters to classify until the commune reaches it:
   the same reason exercises 1 and 2 each carry a commune selector. ``cycle``
   says which TITO cycle to read, and ``sample`` means the country's published
   sample cycle, the same 27 April 2024 data the four raster layers draw. Left
   unset it would read the latest live cycle instead.

   Leave ``source_inondation`` unset. It defaults to **Pluviale (débordement)**,
   the same ``pluvial_overbank`` variant as the four raster layers.

#. Click **Fetch plugin defaults**. The layer is named **Classification de
   l'aléa**, styled with four rules on the ``alea`` attribute, and given a
   four-item **Aléa** legend.

#. Save the layer by clicking **Create**.

.. figure:: images/ex3-hazard-layer-source.png
   :alt: The hazard layer source configuration with its gates, commune and cycle
   :width: 100%

   **Screenshot:** the **Source** tab for the hazard layer, four gates and the
   commune bound to variables and ``cycle`` set to the sample.


Step 6: Add the affected-features layer
=======================================

#. Next to **Layers**, click **Add Layer** again.

#. Go straight to the **Source** tab and set **Source Type** to
   **Comores: Couche d'Impact**.

#. Fill in the same arguments as in the previous step: the four gates and the
   commune bound to the same five variables, and ``cycle`` set to ``sample``.
   This plugin has no ``source_inondation``: it reads the probabilities already
   stored on each building and road.

#. Click **Fetch plugin defaults**. The layer arrives as **Bâtiments et routes en
   danger** with eight rules (polygon and linestring per level) and an **Aléa**
   legend.

#. Save the layer by clicking **Create**.

The two layers answer different questions from the same thresholds: the hazard
layer classifies *ground*, this one classifies *assets*. Keeping them separate
lets a viewer turn off the ground shading and look only at what is affected.


Step 7: Finish the map
======================

#. In the **Map Extent** argument, choose **Use a Custom Extent** and enter:

   .. code-block:: text

      4814984.15,-1312113.30,13.83

#. On the **Settings** tab, turn on **Fill Viewport** so the map occupies the
   whole window.

#. Save the item, resize the map to fill the window, and move any threshold input
   you displaced back into place.

#. Save the dashboard.

**Warning:** As in exercises 1 and 2, **the extent does not follow the
commune**. Switch to a commune on another island and the layers reload correctly
but the view stays over Moroni until you pan.


Step 8: Add the impact summary table
====================================

#. Set the dashboard in edit mode, add another item, open its 3-dot menu and
   select **Edit**.

#. Set the **Visualization Type** to **Comores: Résumé d'Impact** (in the
   **UFFIS: Comores** group).

#. Fill in the same arguments as in step 6: the four gates and the commune bound
   to their variables, and ``cycle`` set to ``sample``.

#. On the **Settings** tab, set **Background Color** to ``#ffffff`` and add
   borders on the left, right and bottom, so it joins the strip of threshold
   inputs above it.

#. Save the item and drag it directly below the threshold inputs on the right.

#. Save the dashboard.

The share in the last column is of the people living in the **commune's**
buildings, as counted in its receptor file, not the island's or the country's
population. That is the other reason the commune has to reach the plugin as an
argument rather than being baked in. The table's title ends with the cycle,
**(2024-04-27 00:00 UTC, ÉCHANTILLON)**, so nobody mistakes the sample for a
live forecast.

.. figure:: images/ex3-impact-summary.png
   :alt: The impact summary table bound to the four thresholds and the commune
   :width: 100%

   **Screenshot:** the impact summary table arguments bound to the four threshold
   variables and the commune, with ``cycle`` set to the sample.


Step 9: Test the wiring
=======================

At the default gates (0.8 for all four) in Moroni you should see 145 hazard
polygons, a progress message reporting 1,339 buildings and roads at risk, and
this table:

.. list-table::
   :header-rows: 1
   :widths: 40 30 30

   * - Level
     - Buildings
     - People
   * - Sévère
     - 29
     - 29
   * - Élevé
     - 19
     - 57
   * - Moyen
     - 241
     - 828
   * - Faible
     - 961
     - 3,468
   * - TOTAL en danger
     - 1,250
     - 4,383

The total row also reports 14.1 km of roads and 6.29 % of the population.

Change a threshold. The hazard shading, the affected features and the table
should all recompute together, with progress messages while the layers rebuild.

Lowering the **Seuil Faible** from 0.8 is the clearest demonstration: the green
class spreads across the low ground as cells that only a minority of members
flood start to qualify.

Then change the **Commune**. All three plugin-backed items reload against a
different commune's rasters and receptors, and the table's percentage is
measured against a different population.

.. figure:: images/ex3-thresholds-before.png
   :alt: The dashboard before lowering a threshold
   :width: 100%

   **Screenshot:** the view before lowering the Faible threshold.

.. figure:: images/ex3-thresholds-after.png
   :alt: The dashboard after lowering a threshold
   :width: 100%

   **Screenshot:** the same view after lowering it.


Item positions
==============

The shipped solution, for reference.

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
     - 99
     - 41
   * - Base Map (variable input)
     - 0
     - 0
     - 17
     - 6
   * - Commune (variable input)
     - 18
     - 0
     - 16
     - 6
   * - Seuil Faible (variable input)
     - 56
     - 0
     - 11
     - 7
   * - Seuil Moyen (variable input)
     - 67
     - 0
     - 12
     - 7
   * - Seuil Élevé (variable input)
     - 79
     - 0
     - 11
     - 7
   * - Seuil Sévère (variable input)
     - 90
     - 0
     - 10
     - 7
   * - Résumé d'Impact (table)
     - 56
     - 7
     - 44
     - 21


Checkpoint
==========

You should now have:

* A map filling the window, with seven layers in the layer control (four
  rasters, two computed layers, and the base map).
* The four probability rasters switched off on load, there to compare against.
* Four labelled threshold inputs across the top, and a commune selector
  top-left.
* Moving any threshold updating the hazard layer, the impact layer and the
  table.
* Changing the commune reloading all three against different data.
* Progress messages while the layers recompute.


Talking points
==============

* **Four gates on four different questions.** "Sévère" means P(≥100 cm) ≥ 0.8
  while "Élevé" means P(≥70 cm) ≥ 0.8. Those are different questions at the same
  cutoff, so the level names are not comparable to each other and "sévère"
  carries no meaning on its own. Setting all four gates equal, as the default
  does, is the easiest version to explain: the levels then differ only by depth.
* **An unreachable class is an interface problem.** Not here, but it is worth
  telling the Guatemala story: there the Severe gate can be set where nothing can
  qualify and the interface gives no hint. Ask attendees how they would prevent
  it: cap the input? show the value range? annotate the legend?
* **What the gate actually filters.** A threshold of 0.8 keeps cells where at
  least 40 of the forecast's 50 members reached that depth. Every probability is
  a count out of 50, a multiple of 0.02, so it is coarse and the classification
  changes in visible jumps rather than smoothly.
* **Vectorising a classification.** A map layer can only point at a URL, and
  nothing serves a computed raster, so the plugin vectorises the classified grid:
  adjacent cells of equal class merge into one polygon, about 145 of them for
  Moroni at the default gates. Normal and NoData are dropped (most of the grid)
  because a basemap shows unaffected ground better than a coloured layer does.
* **The commune is an argument, not a constant.** Guatemala and Antigua and
  Barbuda each have one domain, so their plugins hardcode it. Comoros has 55, so
  the commune travels with the gates into every one of the three plugins. That
  also decides the denominator in the table's last column.
* **The cycle is an argument too.** Here it is fixed to ``sample`` so the
  exercise always has a flood to show. Bind it to ``${Date}`` from exercise 2's
  cycle list instead and the three plugins follow live data; for a live cycle
  the four raster layers would then need their URLs pointed at
  ``https://tito.uffis.org/outputs/comoros/${Date}/...`` to stay in step.


Next
====

The three exercises together cover the raster products, the likely depth on
buildings and roads, and the classification. The companion notebooks in
``notebooks/Comoros/`` derive the same analysis as plain Python, and section 6 of
the exercise 3 notebook walks through how these plugins are put together. The
notebooks still use the earlier training files, so their numbers may differ from
the dashboards'.
