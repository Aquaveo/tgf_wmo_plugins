.. Shared front matter for the Guatemala hands-on exercise guides, English.
.. A Spanish translation lives alongside this file as getting_started_es.rst.

==========================================================
Guatemala Hands-On Exercises: Getting Started
==========================================================

Setup, background and the motions that repeat in every exercise. Read this once,
then work through whichever exercise you need.

.. contents:: On this page
   :depth: 2
   :local:
   :backlinks: none


The three exercises
===================

Each exercise builds one dashboard and lives in its own file:

.. list-table::
   :header-rows: 1
   :widths: 30 22 48

   * - Guide
     - Dashboard
     - What it shows
   * - `Exercise 1: A flood probability map <exercise_1_en.rst>`_
     - Guatemala Hands On 1 (English)
     - Four exceedance-probability rasters from the TITO sample cycle on one
       map, with a switchable base map.
   * - `Exercise 2: Likely impact for a forecast cycle <exercise_2_en.rst>`_
     - Guatemala Hands On 2 (English)
     - The likely flood depth on every building and road for a chosen TITO
       cycle and probability, with a summary table and a headline card.
   * - `Exercise 3: Hazard classification with adjustable thresholds <exercise_3_en.rst>`_
     - Guatemala Hands On 3 (English)
     - A hazard classification driven by four probability thresholds the viewer
       can move, with the affected buildings and roads and an impact table.

The exercises are cumulative in difficulty, not in content: each is a separate
dashboard, and each can be built on its own. Exercise 1 teaches raster layers,
2 adds a plugin-backed vector layer and a data-driven selector, 3 adds
interactivity through variable inputs.

Companion notebooks
-------------------

``notebooks/Guatemala/02_storm_impact.ipynb`` and ``notebooks/Guatemala/03_hazard_classification.ipynb``
derive the numbers behind exercises 2 and 3 as plain Python. These guides cover
*building the dashboard*; the notebooks cover *why the numbers are what they
are*. They pair well: run the notebook first if you want to understand the
analysis, follow the guide if you want to assemble the interface.

The notebooks still work from the earlier training files rather than the TITO
sample cycle the dashboards now read, so their numbers differ from what the
dashboards show.

Conventions
-----------

* **Bold** marks something you click or a field label exactly as it appears in
  the interface, e.g. **Add Layer**, **Source Type**.
* ``Monospace`` marks a value you type or paste.
* Steps are numbered. Where the order does not matter, that is said explicitly.
* Every exercise ends with a **Checkpoint** listing what you should be able to
  see, and **Talking points** worth raising if you are teaching from it.

**Note:** Screenshots in these guides are placeholders. Each ``figure`` block
names what the image should show; drop a PNG at the given path under
``docs/Guatemala/images/`` and it will render.


Before you begin
================

What you need
-------------

#. **A TethysDash instance you can create dashboards on.** You need to be able
   to reach the landing page and create a dashboard, which means an account with
   dashboard-creation rights.
#. **The** ``tgf_wmo_plugins`` **package installed on the server**, not just on
   your laptop. Visualization plugins are discovered on the backend through
   Intake's entry points, so the app process must be able to import them:

   .. code-block:: bash

      pip install git+https://github.com/Aquaveo/tgf_wmo_plugins.git

   Restart the Tethys app after installing. To confirm it worked, open any
   dashboard item's **Visualization Type** dropdown and look for the
   **UFFIS: Guatemala** group.
#. **Outbound HTTPS from the server.** Every plugin reads its data from the
   public TITO server at request time. Nothing is bundled with the package.
#. **Spanish plugin names.** Guatemala's plugins speak Spanish whatever the
   dashboard's language: their labels, argument names, layer names and
   attribute names are all in Spanish. The English guides use the same
   plugins and give an English gloss where it helps.
#. **Visualization permissions**, if your instance restricts plugin types. The
   exercises use the ``table``, ``card``, ``map_layer`` and
   ``variable_input`` types.

**Warning:** If the **UFFIS: Guatemala** group is missing from the
dropdown, the package is not installed in the environment the app is actually
running in. That is by far the most common setup problem. Installing into your
shell's Python is not enough when the app runs under a different interpreter or
container.

The data
--------

All three dashboards read one TITO **sample cycle**: the forecast published at
2026-10-16 22:00 UTC for the Santa Inés Petapa site, kept as a fixed example so
the exercises show the same event in every session. Its root is:

.. code-block:: text

   https://tito.uffis.org/sample/guatemala/20261016.220000/

A sample cycle has the same layout as the live TITO outputs, which are published
under ``https://tito.uffis.org/outputs/guatemala/<cycle>/``. Anything built on
the sample therefore works on a live cycle once you change the cycle.

.. list-table::
   :header-rows: 1
   :widths: 26 74

   * - Used by
     - Contents
   * - Map layers (exercises 1 and 3)
     - The four exceedance-probability GeoTIFFs, in
       ``guatemala_90m/fim/stream_sat_stormlab/Guatemala_SantaInesPetapa/combined_overbank/``
       under the root, named
       ``prob_depth_ge_<depth>_overbank.20261016.220000.tif`` for ``<depth>`` =
       ``10cm``, ``30cm``, ``70cm`` and ``100cm``. Each cell holds the
       probability that flood water reaches that depth.
   * - Plugins (exercises 2 and 3)
     - The same cycle's buildings, roads and probabilities. The plugins find
       these themselves; you only tell them which cycle to read.

The probabilities are fractions of 50 ensemble members, so every value is a
multiple of 0.02, and each of the four rasters reaches 1.0 somewhere. The
rasters are 424 x 319 cells of about 5 m.

Earlier versions of these exercises read training files from an S3 bucket
(``PBI_Actividad_2/``, ``Guatemala_IBF/`` and ``floodmaps_test/``). The exercise
dashboards no longer use them; the companion notebooks still do.

**Important:** The sample rasters are natively **EPSG:3857**, and that matters.
TethysDash ships no proj4, so OpenLayers can only resolve EPSG:4326 and EPSG:3857
for layer data. Point a layer at a raster in another projection (a UTM raster,
for example) and it will appear to load and then vanish, or drag the whole map
into the wrong coordinates. If a layer flashes on and disappears, check its
projection first.

Groundwork common to all three exercises
========================================

These motions repeat in every exercise. They are spelled out once here, and the
exercises refer back to them as "create the dashboard" and "add a dashboard
item".

Creating a dashboard
--------------------

#. From the landing page, click the **Create a New Dashboard** card.
#. Fill in **Name** and **Description**, then click **Create**.
#. The new dashboard opens empty.

.. figure:: images/00-landing-page.png
   :alt: The TethysDash landing page with the Create a New Dashboard card
   :width: 100%

   **Screenshot:** the landing page, with the **Create a New Dashboard** card
   visible.

.. figure:: images/00-new-dashboard-modal.png
   :alt: The new dashboard modal with Name and Description fields
   :width: 100%

   **Screenshot:** the new-dashboard modal, Name and Description filled in.

Entering edit mode
------------------

A dashboard can only be changed by its owner, and only in edit mode. Click the
**Edit Dashboard** button in the header. The header then offers:

.. list-table::
   :header-rows: 1
   :widths: 34 66

   * - Button
     - What it does
   * - **Add Dashboard Item**
     - Adds a new, unconfigured item to the layout.
   * - **Lock/Unlock Movement**
     - Freezes item positions so you can click without dragging.
   * - **Import Dashboard Item**
     - Loads an item from an exported configuration file.
   * - **Dashboard Settings**
     - Name, description, thumbnail, sharing, notes, and
       **Unrestricted Grid Item Movement**.
   * - **Save Changes**
     - Persists the layout.
   * - **Cancel**
     - Discards changes back to the last save.

.. figure:: images/00-edit-mode-toolbar.png
   :alt: The dashboard header toolbar in edit mode
   :width: 100%

   **Screenshot:** the header toolbar in edit mode, with the buttons above
   visible.

**Tip:** Save often. **Cancel** reverts to the last save, so a long unsaved
editing session is a single mistake away from being lost.

Adding and configuring a dashboard item
---------------------------------------

#. In edit mode, click **Add Dashboard Item**. An empty item appears.
#. Click the item's **3-dot menu** and select **Edit**. The data viewer
   modal opens.
#. On the **Visualization** tab, pick a **Visualization Type**. Arguments for
   that visualization appear underneath.
#. Fill the arguments in. The preview updates as you go.
#. Switch to the **Settings** tab for item-level options (borders, background,
   **Fill Viewport**). Settings only become available once a visualization is
   configured and previewing.
#. Click **Save** in the bottom-right corner of the item editor to apply,
   then **Save Changes** in the top-right corner of the dashboard editor to
   persist.

.. figure:: images/00-dataviewer.png
   :alt: The data viewer modal showing the Visualization Type dropdown
   :width: 100%

   **Screenshot:** the data viewer with the **Visualization Type** dropdown open,
   showing the **UFFIS: Guatemala** group.

.. figure:: images/00-griditem-menu.png
   :alt: A dashboard item's 3-dot menu open
   :width: 100%

   **Screenshot:** an item's 3-dot menu, showing Edit, Copy, Order, Export
   and Delete.

Sizing and placing items
------------------------

Drag an item by its body, resize it from the handle in its lower-right corner.
The grid is 100 columns wide. All three solutions turn on
**Unrestricted Grid Item Movement** (in **Dashboard Settings**), which lets items
sit anywhere and overlap. That is needed here so the controls and panels can float over
a full-bleed map.

Each exercise ends with an **Item positions** table giving the exact ``x``, ``y``,
``w`` and ``h`` of every item in that solution. You do not need to match them to
the pixel; drag to something close and adjust.

Referencing a variable input
----------------------------

All three exercises wire visualizations to variable inputs. There are two ways to
write the reference, depending on the argument:

* **Dropdown-type arguments** list the available variables in a
  **Variable Inputs** section at the bottom of the dropdown; pick from there.
* **Free-text arguments** take the template syntax ``${Variable Name}``, typed by
  hand.

The name inside the braces must match the input's ``variable_name`` exactly,
spaces and punctuation included. Build the variable input *before* the items that
reference it, or there will be nothing to select.


Importing a finished solution
=============================

To reset between sessions, or to check your work, the finished dashboards are in
this repository under ``dashboards/``:

.. code-block:: text

   dashboards/Guatemala/Guatemala_Hands_On_1.json
   dashboards/Guatemala/Guatemala_Hands_On_2.json
   dashboards/Guatemala/Guatemala_Hands_On_2_English.json
   dashboards/Guatemala/Guatemala_Hands_On_3.json

``Guatemala_Hands_On_1.json``, ``_2.json`` and ``_3.json`` are the Spanish
solutions, so their variable inputs carry Spanish names (``Mapa Base``,
``Probabilidad``, ``Umbral Bajo (P(≥10 cm))``). Swap in the English names used in
these guides after importing, or keep the Spanish ones throughout; what matters
is that every ``${...}`` reference matches its input exactly.

``Guatemala_Hands_On_2_English.json`` is a fuller English live-forecast
dashboard. Its first tab holds the exercise 2 items (cycle dropdown,
``Probability`` input, likely-depth layer, card and table) alongside hazard,
rainfall and river discharge items, and a second tab shows warnings.

These files are whole-dashboard exports. Individual items can also be moved
between dashboards through **Export** on an item's 3-dot menu and
**Import Dashboard Item** in the header, which is the quickest way to reuse
exercise 1's four raster layers in exercise 3.

Troubleshooting
===============

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Symptom
     - Cause and fix
   * - The **UFFIS: Guatemala** group is missing from
       **Visualization Type**.
     - ``tgf_wmo_plugins`` is not installed in the environment the app runs in,
       or the app was not restarted. Install it server-side and restart.
   * - A visualization says a variable is empty.
     - The ``${...}`` name does not match a ``variable_name`` exactly, or the
       variable input was added after the item that references it. Check
       spelling, spaces and punctuation, then re-select the variable.
   * - A layer flashes on and then disappears.
     - Almost always a projection problem. Confirm the raster is in EPSG:3857
       or EPSG:4326. The sample rasters are EPSG:3857; a UTM raster is not.
   * - The whole map jumps to somewhere in Africa.
     - Same cause. A GeoTIFF in an unresolvable projection makes the auto-fit
       adopt coordinates that land near 0°, 0°.
   * - Every vector feature is grey.
     - The style rules are not matching. Use **Fetch plugin defaults** rather
       than hand-authoring rules; a malformed rule never matches and fails
       silently.
   * - A raster is a single flat colour.
     - The ramp bounds do not suit the data, or ``mask_below`` is unset so dry
       ground is being coloured. Check both.
   * - A plugin layer or table is empty, or shows a different event from the
       raster layers.
     - The plugin's cycle is not the sample. In exercise 3 set ``ciclo`` to
       **Evento de muestra** (``sample``); in exercise 2 bind it to ``${Date}``
       and pick the sample cycle. Left unset, a plugin reads the latest live
       cycle, which may not have flooded at all.
   * - The **Date** dropdown in exercise 2 opens on a live cycle.
     - The cycle list's ``inicio`` argument is not set. Set it to
       **Ciclo de muestra más reciente** (``sample``).
   * - The dashboard cannot be edited.
     - Only the owner can edit, and only in edit mode. Check the header for the
       **Edit Dashboard** button.
