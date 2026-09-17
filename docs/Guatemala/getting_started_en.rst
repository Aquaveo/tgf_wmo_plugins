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
   * - `Exercise 1 — A flood depth and probability map <exercise_1_en.rst>`_
     - Guatemala Hands On 1 (English)
     - A flood depth raster and four exceedance-probability rasters on one map,
       with a switchable base map.
   * - `Exercise 2 — Impact for a single storm <exercise_2_en.rst>`_
     - Guatemala Hands On 2 (English)
     - Depth for a single storm out of a 198-member ensemble, plus the buildings
       and roads that storm floods, a summary table and a headline card.
   * - `Exercise 3 — Hazard classification with adjustable thresholds <exercise_3_en.rst>`_
     - Guatemala Hands On 3 (English)
     - A hazard classification driven by four probability thresholds the viewer
       can move, with the affected buildings and roads and an impact table.

The exercises are cumulative in difficulty, not in content — each is a separate
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

Conventions
-----------

* **Bold** marks something you click or a field label exactly as it appears in
  the interface, e.g. **Add Layer**, **Source Type**.
* ``Monospace`` marks a value you type or paste.
* Steps are numbered. Where the order does not matter, that is said explicitly.
* Every exercise ends with a **Checkpoint** listing what you should be able to
  see, and **Talking points** worth raising if you are teaching from it.

**Note** — Screenshots in these guides are placeholders. Each ``figure`` block
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
   **Flood Maps (English)** group.
#. **Outbound HTTPS from the server.** Every plugin reads its data from a public
   S3 bucket at request time. Nothing is bundled with the package.
#. **Visualization permissions**, if your instance restricts plugin types. The
   exercises use the ``table``, ``card`` and ``map_layer`` types.

**Warning** — If the **Flood Maps (English)** group is missing from the
dropdown, the package is not installed in the environment the app is actually
running in. That is by far the most common setup problem. Installing into your
shell's Python is not enough when the app runs under a different interpreter or
container.

The data
--------

Everything comes from one public bucket. The root is the same throughout, and
the exercises refer to it as ``.../``:

.. code-block:: text

   https://cog-s3-test-401506828094-us-east-1-an.s3.us-east-1.amazonaws.com

Three prefixes matter:

.. list-table::
   :header-rows: 1
   :widths: 26 74

   * - Prefix
     - Contents
   * - ``PBI_Actividad_2/``
     - The rasters used by the map layers: one depth GeoTIFF, four
       exceedance-probability GeoTIFFs, and the ensemble Zarr store's companion
       files. All are EPSG:3857 copies on a single shared grid.
   * - ``Guatemala_IBF/``
     - The impact features (buildings and roads) and the original UTM rasters
       they were sampled from. The plugins read the slim CSV from here.
   * - ``floodmaps_test/``
     - The 198-member ensemble Zarr store used by exercise 2.

**Important** — The rasters the dashboards point at are the **EPSG:3857** copies
under ``PBI_Actividad_2/``, not the UTM originals under ``Guatemala_IBF/``. This
is not cosmetic. TethysDash ships no proj4, so OpenLayers can only resolve
EPSG:4326 and EPSG:3857 for layer data. Point a layer at a UTM raster and it
will appear to load and then vanish, or drag the whole map into UTM. If a layer
flashes on and disappears, check its projection first.


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

**Tip** — Save often. **Cancel** reverts to the last save, so a long unsaved
editing session is a single mistake away from being lost.

Adding and configuring a dashboard item
---------------------------------------

#. In edit mode, click **Add Dashboard Item**. An empty item appears.
#. Click the item's **3-dot menu** and select **Edit**. The data viewer
   modal opens.
#. On the **Visualization** tab, pick a **Visualization Type**. Arguments for
   that visualization appear underneath.
#. Fill the arguments in. The preview updates as you go.
#. Switch to the **Settings** tab for item-level options — borders, background,
   **Fill Viewport**. Settings only become available once a visualization is
   configured and previewing.
#. Click **Save** in the bottom-right corner of the item editor to apply,
   then **Save Changes** in the top-right corner of the dashboard editor to
   persist.

.. figure:: images/00-dataviewer.png
   :alt: The data viewer modal showing the Visualization Type dropdown
   :width: 100%

   **Screenshot:** the data viewer with the **Visualization Type** dropdown open,
   showing the **Flood Maps (English)** group.

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
sit anywhere and overlap — needed here so the controls and panels can float over
a full-bleed map.

Each exercise ends with an **Item positions** table giving the exact ``x``, ``y``,
``w`` and ``h`` of every item in that solution. You do not need to match them to
the pixel; drag to something close and adjust.

Referencing a variable input
----------------------------

All three exercises wire visualizations to variable inputs. There are two ways to
write the reference, depending on the argument:

* **Dropdown-type arguments** list the available variables in a
  **Variable Inputs** section at the bottom of the dropdown — pick from there.
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

   dashboards/Guatemala/Guatemala_Hands_On_1_English.json
   dashboards/Guatemala/Guatemala_Hands_On_2_English.json
   dashboards/Guatemala/Guatemala_Hands_On_3_English.json

Spanish versions sit alongside them with ``_Espanol`` in place of ``_English``.
The Spanish dashboards use the ``_es`` plugins throughout, so a dashboard is
internally consistent in one language — do not mix them.

These files are whole-dashboard exports. Individual items can also be moved
between dashboards through **Export** on an item's 3-dot menu and
**Import Dashboard Item** in the header, which is the quickest way to reuse
exercise 1's five raster layers in exercise 3.


Troubleshooting
===============

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Symptom
     - Cause and fix
   * - The **Flood Maps (English)** group is missing from
       **Visualization Type**.
     - ``tgf_wmo_plugins`` is not installed in the environment the app runs in,
       or the app was not restarted. Install it server-side and restart.
   * - A visualization says a variable is empty.
     - The ``${...}`` name does not match a ``variable_name`` exactly, or the
       variable input was added after the item that references it. Check
       spelling, spaces and punctuation, then re-select the variable.
   * - A layer flashes on and then disappears.
     - Almost always a projection problem. Confirm the layer points at the
       ``PBI_Actividad_2`` EPSG:3857 copy, not a ``Guatemala_IBF`` UTM original.
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
   * - Purple never appears in exercise 3.
     - Expected if the Severe threshold is above 0.2. The 76 cm raster only ever
       holds 0 or 0.2. Lower the threshold to 0.2 or below.
   * - The dashboard cannot be edited.
     - Only the owner can edit, and only in edit mode. Check the header for the
       **Edit Dashboard** button.
