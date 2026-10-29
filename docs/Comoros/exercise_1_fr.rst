.. Solution de l'exercice pratique 1 des Comores, français. La version anglaise
.. se trouve à côté de ce fichier, sous le nom exercise_1.rst. Deux points
.. diffèrent du guide original du Guatemala et sont expliqués là où ils se
.. présentent : il n'y a pas de couche de profondeur, car le cycle ne publie
.. aucun raster de profondeur unique et un membre choisi arbitrairement ne se
.. marierait pas avec les quatre probabilités d'ensemble ; et les rasters sont en
.. EPSG:5629, que la carte ne sait pas résoudre tant que le code n'est pas
.. enregistré -- voir l'avertissement ci-dessous.
.. Le tableau de bord construit est dashboards/Comoros/Comoros_Hands_On_1.json.

=======================================================================
Exercice 1 — Une carte de profondeur et de probabilité d'inondation
=======================================================================

Construction de **Comores Exercice 1**, pas à pas.

Rappel : l'interface est en anglais, donc les noms de boutons et de champs sont
laissés en anglais et en gras.

.. contents:: Sur cette page
   :depth: 2
   :local:
   :backlinks: none


Ce que vous allez construire
============================

Une carte occupant toute la fenêtre, portant les quatre rasters de probabilité de
dépassement du cycle de prévision, et trois contrôles en haut : une liste
déroulante qui change le fond de carte situé en dessous, une deuxième qui choisit
laquelle des 55 communes du pays est dessinée, et un nombre qui fixe la
probabilité minimale qu'une cellule doit atteindre pour être dessinée. Le tableau
de bord s'ouvre sur **Moroni** (KM274), la capitale, sur la Grande Comore.

.. figure:: images/ex1-finished.png
   :alt: Le tableau de bord terminé de l'exercice 1
   :width: 100%

   **Capture :** le tableau de bord terminé, contrôle des couches ouvert pour que
   les quatre couches soient visibles, avec les deux contrôles en haut à gauche.

Cet exercice porte sur les couches raster : où va l'URL, pourquoi une rampe de
probabilité doit être fixée plutôt que mise à l'échelle automatiquement, et
comment une entrée variable peut piloter le même réglage sur quatre couches à la
fois — dont une qui réécrit une partie de l'URL de chaque couche.

Il n'y a délibérément **aucune couche de profondeur**. Le cycle ne publie pas de
raster de profondeur unique — seulement un par membre de la prévision — et poser
un membre arbitraire à côté de quatre probabilités calculées sur tout l'ensemble
inviterait le lecteur à comparer des grandeurs qui ne sont pas comparables.
L'exercice 2 ouvre correctement la bibliothèque de profondeurs.

**Avertissement** — **Les rasters des Comores sont en EPSG:5629 (Moznet / UTM
zone 38S), et la carte ne sait pas encore résoudre ce code.** OpenLayers gère
EPSG:4326, EPSG:3857 et les zones UTM WGS84 par lui-même ; tout le reste doit être
enregistré, et la table de ``reactapp/components/map/projections.js`` ne contient
actuellement que EPSG:5041 et EPSG:5070. Tant que ``EPSG:5629`` n'y est pas
ajouté, toutes les couches de cet exercice se placeront mal : une couche GeoTIFF
se charge et atterrit très loin de l'océan Indien.
L'ajout consiste en une entrée de table plus un point de contrôle, comme le
décrivent les commentaires de ce fichier. Rien d'autre dans ce guide ne change
une fois que c'est fait.

**Remarque** — Les captures d'écran de ce guide sont des images provisoires.
Chaque bloc ``figure`` indique ce que l'image doit montrer ; déposez un PNG au
chemin indiqué sous ``docs/Comoros/images/`` et il s'affichera.
``images/README.md`` les répertorie toutes.


Les données
===========

Tout provient d'un seul bucket public :

.. code-block:: text

   https://cog-s3-test-401506828094-us-east-1-an.s3.us-east-1.amazonaws.com

Les produits de prévision des Comores sont écrits **par commune ADM3**, et non
sur une seule grille nationale : chaque chemin ci-dessous nomme donc une commune.
Ce nom est un segment de chemin unique combinant le pcode et la commune —
``KM274_Moroni`` — et l'échanger est tout ce qui sépare les rasters d'une commune
de ceux d'une autre. L'étape 2 transforme ce segment en liste déroulante, pour que
le tableau de bord atteigne les 55 communes sans modifier une URL.

.. list-table::
   :header-rows: 1
   :widths: 26 74

   * - Préfixe
     - Contenu
   * - ``Comoros_training/Comoros_cycle_20240427_0000UTC/``
     - Le cycle de prévision du 27 avril 2024, et tout ce que dessine cet
       exercice. ``fim/<commune>/stream_sat_stormlab/`` contient les quatre
       rasters de probabilité de dépassement dessinés ici, et
       ``fim/<commune>/member_depths/`` les 50 rasters de profondeur par membre à
       partir desquels ils sont comptés. Les geopackages de récepteurs que lit
       l'exercice 3 sont dans ``ibf/``.
   * - ``Comoros_IBF/Comoros/``
     - Les magasins de scénarios, un Zarr par commune
       (``fim_store_KM274_Moroni_v1.zarr``), contenant chacun les 200 tempêtes
       synthétiques de profondeur maximale. L'exercice 2 ouvre celui de Moroni.

Deux propriétés de ces données déterminent la forme de l'exercice :

* **Pluvial uniquement.** Les modèles insulaires ont été exécutés avec un forçage
  pluviométrique et sans débit entrant en limite amont : un niveau d'aléa signifie
  donc ici de la pluie qui ne s'est pas écoulée, jamais une rivière en crue.
* **Une grille projetée.** EPSG:5629 à 30,57 m, la grille propre au modèle
  insulaire plutôt qu'une copie reprojetée. C'est l'objet de l'avertissement
  ci-dessus, et c'est une vraie différence avec le Guatemala, dont les rasters ont
  été copiés en EPSG:3857 précisément pour que la carte puisse les lire.


Étape 1 — Créer le tableau de bord
==================================

#. Créez un nouveau tableau de bord (voir
   `Créer un tableau de bord <getting_started.rst#creating-a-dashboard>`_) avec :

   * **Name** : ``Comores Exercice 1``
   * **Description** : ``Solution pour l'exercice pratique OMM Comores n°1``

#. Retrouvez votre tableau de bord sur la page d'accueil et double-cliquez dessus
   pour l'ouvrir. Il est vide, la prévisualisation affiche donc une zone blanche.

#. Ouvrez **Dashboard Settings** dans le coin supérieur droit et activez
   **Unrestricted Grid Item Movement**. Enregistrez les paramètres.

#. Quittez **Dashboard Settings** et cliquez sur **Edit Dashboard** dans le coin
   supérieur droit pour passer en mode édition.


Étape 2 — Ajouter les trois entrées variables
=============================================

Les trois contrôles se construisent en premier, car les couches de l'étape 4 en
référencent deux par leur nom et il faut bien qu'il y ait quelque chose à
référencer. Voir
`Référencer une entrée variable <getting_started.rst#referencing-a-variable-input>`_.

**Le sélecteur de fond de carte**

#. Vous verrez un élément déjà présent sur le tableau de bord. Cliquez sur son
   menu à 3 points et sélectionnez **Edit**.

#. Réglez **Visualization Type** sur **Variable Input** (dans le groupe
   **Default**).

#. Renseignez :

   .. list-table::
      :header-rows: 1
      :widths: 32 68

      * - Argument
        - Valeur
      * - ``variable_name``
        - ``Fond de Carte``
      * - ``show_label``
        - ``True``
      * - ``variable_options_source``
        - ``Base Map Layers``

   ``Base Map Layers`` est une source d'options intégrée — elle remplit la liste
   déroulante avec les fonds de carte proposés par l'instance, vous n'avez donc
   pas à les énumérer vous-même.

#. Sur l'onglet **Settings**, réglez **Background Color** sur ``#FFFFFF``. Sans
   cela, la liste déroulante flotte sur la carte sans arrière-plan et devient
   difficile à lire.

#. Choisissez une valeur initiale dans la prévisualisation, à droite de
   l'éditeur. La solution livrée utilise **World Imagery** — l'imagerie aérienne
   permet de voir facilement quels bâtiments se trouvent sous les cellules
   inondées — mais n'importe quel fond de carte convient.

#. Enregistrez l'élément, faites-le glisser dans le coin supérieur gauche et
   redimensionnez-le à environ 14 colonnes de large sur 5 lignes de haut.

.. figure:: images/ex1-variable-input-basemap.png
   :alt: La configuration de l'entrée variable du fond de carte
   :width: 100%

   **Capture :** les arguments **Variable Input** du sélecteur de fond de carte.

**Le sélecteur de commune**

Celui-ci diffère des deux autres : ses options ne sont ni intégrées ni un simple
nombre, c'est une liste que vous fournissez.

#. Ajoutez un autre élément, ouvrez son menu à 3 points, sélectionnez **Edit** et
   réglez **Visualization Type** sur **Variable Input**.

#. Renseignez :

   .. list-table::
      :header-rows: 1
      :widths: 32 68

      * - Argument
        - Valeur
      * - ``variable_name``
        - ``Commune``
      * - ``show_label``
        - ``True``
      * - ``variable_options_source``
        - ``dropdown``

#. Choisir ``dropdown`` fait apparaître un éditeur de **choices**. Chaque entrée
   comporte une **label** — ce que lit l'utilisateur — et une **value** — ce qui
   est substitué dans l'URL. Pour les Comores, ce sont le nom de la commune et son
   segment de chemin :

   .. list-table::
      :header-rows: 1
      :widths: 40 60

      * - Étiquette
        - Valeur
      * - ``Moroni``
        - ``KM274_Moroni``
      * - ``Mutsamudu``
        - ``KM134_Mutsamudu``
      * - ``Fomboni``
        - ``KM321_Fomboni``
      * - …
        - …

   La distinction entre les deux est tout l'intérêt. L'utilisateur ne voit jamais
   de pcode, et l'URL ne voit jamais de nom d'affichage. Les **55** communes
   figurent dans le tableau de bord livré, ordonnées par pcode pour que les trois
   îles se regroupent — Anjouan (``KM1xx``), Grande Comore (``KM2xx``), Mohéli
   (``KM3xx``). Plutôt que de les saisir à la main, importez l'élément livré ou
   copiez la liste depuis ``dashboards/Comoros/Comoros_Hands_On_1.json``.

#. Sur l'onglet **Settings**, réglez **Background Color** sur ``#ffffff``.

#. Définissez la valeur initiale sur ``Moroni``.

#. Enregistrez l'élément et faites-le glisser le long du haut, à droite du
   sélecteur de fond de carte.

.. figure:: images/ex1-variable-input-commune.png
   :alt: L'entrée variable de commune avec sa liste de choix
   :width: 100%

   **Capture :** les arguments **Variable Input** du sélecteur de commune, avec
   ``variable_options_source`` à ``dropdown`` et l'éditeur de choix ouvert.

**Le masque de probabilité**

#. Ajoutez un troisième élément, ouvrez son menu à 3 points, sélectionnez
   **Edit**, et réglez de nouveau **Visualization Type** sur **Variable Input**.

#. Renseignez :

   .. list-table::
      :header-rows: 1
      :widths: 32 68

      * - Argument
        - Valeur
      * - ``variable_name``
        - ``Masque de Probabilité``
      * - ``show_label``
        - ``True``
      * - ``variable_options_source``
        - ``number``

#. Sur l'onglet **Settings**, réglez **Background Color** sur ``#FFFFFF``.

#. Définissez la valeur initiale sur ``0`` dans la prévisualisation. Zéro signifie
   « dessiner toute cellule ayant la moindre chance », et c'est le point de départ
   de l'exercice.

#. Enregistrez l'élément et faites-le glisser à l'extrême droite de la rangée du
   haut.

#. Enregistrez le tableau de bord en cliquant sur **Save Changes** dans le coin
   supérieur droit.

.. figure:: images/ex1-variable-input-mask.png
   :alt: La configuration de l'entrée variable du masque de probabilité
   :width: 100%

   **Capture :** les arguments **Variable Input** du masque de probabilité, avec
   ``variable_options_source`` à ``number`` et une valeur initiale de 0.


Étape 3 — Ajouter la carte
==========================

#. Mettez le tableau de bord en mode édition, ajoutez un autre élément, puis
   ouvrez son menu à 3 points et sélectionnez **Edit**.

#. Réglez **Visualization Type** sur **Map** (dans le groupe **Default**).

#. Cinq arguments apparaissent : **Base Map**, **Layer Control**, **Layers**,
   **Map Extent** et **Map Drawing**.

#. Dans l'argument **Base Map**, choisissez ``Base Map`` dans la section
   **Variable Inputs**, en bas de la liste déroulante. La valeur devient
   ``${Fond de Carte}``.

#. Activez **Layer Control**, pour que les quatre couches puissent être basculées
   individuellement.

Laissez **Map Extent** pour l'étape 5 — il est plus facile de la choisir une fois
qu'il y a quelque chose sur la carte.

.. figure:: images/ex1-map-args.png
   :alt: Les arguments de la visualisation Map dans le visualiseur de données
   :width: 100%

   **Capture :** les cinq arguments de la visualisation **Map**, avec
   **Base Map** lié à ``${Fond de Carte}`` et **Layer Control** activé.


Étape 4 — Ajouter les quatre couches de probabilité
===================================================

Ces quatre couches sont identiques à l'URL et au nom près : construisez-en une et
répétez. Ajoutez-les dans cet ordre, pour que le seuil le plus profond se
retrouve au bas de la pile et le moins profond — qui couvre la plus grande
surface — au-dessus.

Les quatre chemins partagent un préfixe ; seule la profondeur dans le nom de
fichier change. Notez le ``${Commune}`` au milieu — c'est le segment de commune de
l'étape 2, et c'est ce qui permet à un seul jeu de quatre couches de servir les 55
communes :

.. code-block:: text

   https://cog-s3-test-401506828094-us-east-1-an.s3.us-east-1.amazonaws.com/
     Comoros_training/Comoros_cycle_20240427_0000UTC/Comoros_cycle_20240427_0000UTC/
     fim/${Commune}/stream_sat_stormlab/pluvial_overbank/

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - **Name** de la couche
     - nom de fichier, ajouté au préfixe ci-dessus
   * - ``Probabilité d'inondation à 100 cm``
     - ``prob_depth_ge_100cm_overbank.20240427.000000.tif``
   * - ``Probabilité d'inondation à 70 cm``
     - ``prob_depth_ge_70cm_overbank.20240427.000000.tif``
   * - ``Probabilité d'inondation à 30 cm``
     - ``prob_depth_ge_30cm_overbank.20240427.000000.tif``
   * - ``Probabilité d'inondation à 10 cm``
     - ``prob_depth_ge_10cm_overbank.20240427.000000.tif``

Ce sont les variantes **overbank**, dont l'eau stagnante permanente de Moroni a
été retirée — le dossier ``pluvial/`` à côté contient les quatre mêmes rasters
sans cette soustraction. Pour cette commune, les deux diffèrent sur exactement 47
cellules : le choix se voit donc à peine ici, mais c'est le bon. Un produit qui
dessinerait l'eau permanente comme une inondation crierait au loup à chaque
cycle.

Pour **chacune** des quatre :

#. À côté de **Layers**, cliquez sur **Add Layer**. L'éditeur de couches s'ouvre
   avec les onglets **Layer**, **Source**, **Style**, **Legend**,
   **Attributes/Table Popup** et **Custom Modal Popup**.

#. Sur l'onglet **Layer**, réglez :

   .. list-table::
      :header-rows: 1
      :widths: 24 76

      * - Champ
        - Valeur
      * - ``name``
        - *voir le tableau ci-dessus*
      * - ``opacity``
        - ``.5``

   La semi-transparence compte ici parce que les quatre seuils sont
   **emboîtés** : partout où la couche 100 cm a une valeur, la couche 10 cm en a
   une aussi. La couche 10 cm est ajoutée en dernier et se dessine donc au-dessus ;
   en opacité pleine, elle masquerait complètement les trois autres. À ``.5``,
   elles se teintent les unes à travers les autres et l'emboîtement reste visible.

#. Sur l'onglet **Source**, réglez **Source Type** sur **GeoTIFF** et
   renseignez :

   .. list-table::
      :header-rows: 1
      :widths: 24 76

      * - Champ
        - Valeur
      * - ``url``
        - *voir le tableau ci-dessus, y compris le segment* ``${Commune}``
      * - ``mask_below``
        - ``${Masque de Probabilité}``

   Les deux champs sont du texte libre : tous deux prennent donc la forme
   ``${Nom de la variable}`` saisie à la main, et les noms entre accolades doivent
   correspondre exactement à ``Commune`` et ``Masque de Probabilité``. Ils sont
   substitués différemment, et la différence mérite d'être remarquée :
   ``mask_below`` n'est *que* l'espace réservé, il se résout donc en le nombre
   lui-même, tandis que ``url`` contient l'espace réservé enchâssé dans une chaîne
   plus longue, si bien que le segment de commune est inséré dans le texte qui
   l'entoure.

   ``mask_below`` masque les cellules inférieures ou égales à la valeur donnée. À
   ``0``, toute cellule ayant la moindre chance est dessinée. Augmentez-la et la
   carte ne garde que les cellules qui dépassent cette probabilité — tout l'objet
   de l'étape 5.

#. Sur l'onglet **Style**, laissez le mode sur **Continuous** et choisissez la
   rampe **turbo**. Réglez **Min** = ``0`` et **Max** = ``1``.

   Fixer Min et Max à 0–1 est toute la raison d'être de ces quatre couches. La
   probabilité a une plage fixe et signifiante, et les quatre doivent utiliser la
   même, sinon elles ne sont pas comparables. Laissée en mise à l'échelle
   automatique, chaque couche étirerait sa rampe sur sa propre plage et 0,2
   paraîtrait d'une sévérité différente sur chacune.

   Cela compte plus qu'il n'y paraît. Les quatre couches atteignent 1,0 quelque
   part, mais elles couvrent des surfaces radicalement différentes : environ 7 600
   cellules portent une chance non nulle à 10 cm, contre 59 à 100 cm. Mises à
   l'échelle automatiquement, la couche 100 cm paraîtrait aussi étendue que la
   couche 10 cm.

#. **Sur la couche 100 cm uniquement**, allez sur l'onglet **Legend** et
   sélectionnez **Default Legend**. Les quatre partagent une échelle : quatre
   barres de couleurs identiques ne feraient que prendre de la place ; la couche
   la plus profonde porte l'unique légende et les trois autres n'en ont pas.

#. Enregistrez la couche en cliquant sur **Create** au bas de l'éditeur de
   couches.

.. figure:: images/ex1-layer-source-geotiff.png
   :alt: L'onglet Source configuré pour un GeoTIFF de probabilité
   :width: 100%

   **Capture :** l'onglet **Source** avec **Source Type** GeoTIFF, une URL de
   probabilité, et ``mask_below`` lié à ``${Masque de Probabilité}``.

.. figure:: images/ex1-layer-style-turbo.png
   :alt: L'onglet Style avec la rampe turbo fixée sur 0-1
   :width: 100%

   **Capture :** l'onglet **Style**, mode **Continuous**, **turbo** sélectionnée,
   **Min** 0 et **Max** 1.

.. figure:: images/ex1-layer-list.png
   :alt: La liste Layers montrant les quatre couches raster
   :width: 100%

   **Capture :** la liste **Layers** avec les quatre couches, la plus profonde en
   premier.


Étape 5 — Terminer la carte, puis la piloter
============================================

#. Dans l'argument **Map Extent**, choisissez **Use a Custom Extent** et
   saisissez :

   .. code-block:: text

      4814984.15,-1312113.30,13.83

   C'est ``centre-x,centre-y,zoom`` en mètres EPSG:3857, centré sur Moroni. La
   fenêtre de la commune ne fait qu'environ 5 km de large : le zoom est donc plus
   serré que les vues nationales sur lesquelles s'ouvrent les autres guides.

#. Sur l'onglet **Settings**, activez **Fill Viewport** pour que la carte occupe
   toute la fenêtre.

#. Enregistrez l'élément en cliquant sur **Save** dans le coin inférieur droit de
   l'éditeur de carte.

#. Si la carte recouvre les trois entrées, ouvrez son menu à 3 points, survolez
   **Order** et sélectionnez **Send to Back**. Les contrôles devraient réapparaître
   au-dessus.

#. Enregistrez le tableau de bord en cliquant sur **Save Changes** dans le coin
   supérieur droit.

.. figure:: images/ex1-settings-fill-viewport.png
   :alt: L'onglet Settings avec Fill Viewport activé
   :width: 100%

   **Capture :** l'onglet **Settings** avec **Fill Viewport** activé.

**Essayez le masque.** Augmentez **Masque de Probabilité** à partir de ``0`` et
regardez les quatre couches s'éclaircir ensemble :

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Masque
     - Ce qu'il reste sur la carte
   * - ``0``
     - Toute cellule qu'un membre quelconque inonde à cette profondeur.
   * - ``0.2``
     - Seulement les cellules atteintes par plus de 10 des 50 membres.
   * - ``0.5``
     - Seulement les cellules sur lesquelles plus de la moitié des membres
       s'accordent.
   * - ``0.9``
     - La poignée de cellules que presque tous les membres inondent.

**Essayez la commune.** Changez **Commune** et les quatre couches se rechargent
depuis un dossier différent. Mutsamudu et Jimlimé sur Anjouan, Fomboni sur
Mohéli, et Moroni ici sont quatre endroits bien différents.

**Avertissement** — **L'étendue de la carte ne suit pas la commune.** C'est une
chaîne fixe centrée sur Moroni : passer à une commune d'une autre île laisse donc
la vue au-dessus de la haute mer jusqu'à ce que vous fassiez un panoramique. Il
n'existe pas de variable contenant des coordonnées par commune, et une table de
correspondance de 55 entrées n'est pas quelque chose qu'une entrée variable sait
exprimer. Les possibilités sont donc : faire le panoramique à la main, effacer
l'étendue personnalisée et laisser la carte s'ajuster automatiquement à la
couche, ou garder une commune par tableau de bord. La solution livrée conserve
l'étendue fixe et suppose que vous fassiez le panoramique — à soulever comme une
question de conception plutôt qu'à traiter comme un défaut.


Positions des éléments
======================

La solution livrée, pour référence. Il n'est pas nécessaire de les reproduire au
pixel près — faites glisser jusqu'à une position proche et ajustez.

.. list-table::
   :header-rows: 1
   :widths: 34 16 16 16 18

   * - Élément
     - ``x``
     - ``y``
     - ``w``
     - ``h``
   * - Fond de Carte (entrée variable)
     - 0
     - 0
     - 14
     - 5
   * - Commune (entrée variable)
     - 42
     - 0
     - 18
     - 5
   * - Masque de Probabilité (entrée variable)
     - 86
     - 0
     - 14
     - 5
   * - Carte
     - 8
     - 4
     - 20
     - 20

Les trois entrées occupent une seule rangée en haut — gauche, centre, droite —
au-dessus d'une carte dont **Fill Viewport** est activé : sa propre largeur et sa
hauteur comptent donc moins que son ordre d'empilement.


Point de contrôle
=================

Vous devriez maintenant avoir :

* Une carte occupant toute la fenêtre, montrant Moroni sur le fond de carte que
  vous avez choisi.
* Un contrôle des couches listant cinq couches (fond de carte compris) ; basculer
  chacune change ce qui est dessiné.
* Un contrôle de légende avec une barre de couleurs, sur la couche 100 cm.
* Trois contrôles en haut : une liste déroulante de fonds de carte, une liste
  déroulante de communes listant les 55, et un nombre **Masque de Probabilité**.
* Augmenter le masque éclaircit les quatre couches à la fois ; le remettre à 0 les
  restaure.
* Changer de commune recharge les quatre couches — et laisse la vue là où elle
  était, pour la raison indiquée dans l'avertissement ci-dessus.
* La couche 10 cm couvrant une emprise visiblement plus grande que la couche
  100 cm — à Moroni, environ 7 600 cellules contre 59.

Si au contraire les couches ne se placent pas, ou si la carte saute loin des
Comores, relisez l'avertissement en haut de cette page : les rasters sont en
EPSG:5629 et le code doit être enregistré avant que quoi que ce soit ne
s'affiche.


Points de discussion
====================

* **Pourquoi les rampes de probabilité doivent être fixées.** Les quatre couches
  sont fixées à 0–1 parce que la plage est signifiante et identique pour chacune ;
  sans cela, la même couleur voudrait dire un nombre différent sur chaque couche
  et la pile ne pourrait pas se lire. À comparer avec la profondeur, qui n'a pas
  de borne supérieure naturelle et qu'on laisse normalement se mettre à l'échelle
  automatiquement — une raison parmi d'autres pour que les deux ne cohabitent pas
  sur la même carte sans précaution.
* **Deux variables, deux sortes de substitution.** ``${Masque de Probabilité}``
  occupe un champ entier : il se résout donc en un nombre, type compris.
  ``${Commune}`` se trouve à l'intérieur d'une URL plus longue : il est donc
  inséré dans le texte environnant. Même syntaxe, et l'application choisit le bon
  comportement — mais c'est ce qui permet à une variable de réécrire une partie
  d'un chemin, et c'est ce qui transforme une carte en 55.
* **Étiquette contre valeur.** La liste déroulante des communes affiche ``Moroni``
  et stocke ``KM274_Moroni``. Présenter une étiquette lisible à la place d'une clé
  opaque vaut presque toujours l'indirection, et cela signifie que le schéma de
  pcodes peut changer sans que l'utilisateur s'en aperçoive.
* **Ce que filtre réellement le masque.** Le porter à 0,2 ne garde pas « les
  cellules ayant 20 % de chances d'être inondées ». Il garde les cellules que
  **plus de 10 des 50 membres** de la prévision ont atteintes à cette profondeur.
  Ces 50 membres se réduisent à 16 scénarios distincts de la bibliothèque : les
  valeurs sont donc grossières — la couche 10 cm ne prend que 41 valeurs
  distinctes sur toute la commune — et la couche s'éclaircit par sauts visibles
  plutôt que progressivement. À démontrer : c'est la façon la plus claire de
  montrer à un auditoire que le nombre est une part d'ensemble, et non une
  probabilité calibrée.
* **L'ordre des couches est l'ordre de dessin, et les seuils sont emboîtés.** La
  première couche de la liste se dessine le plus bas et chacune des suivantes
  peint par-dessus : la couche 10 cm — ajoutée en dernier, la plus étendue — se
  retrouve donc au sommet. Partout où la couche 100 cm a une valeur, la couche
  10 cm en a une aussi : en opacité pleine, les trois couches plus profondes
  seraient invisibles. C'est l'opacité ``.5`` qui garde l'emboîtement lisible ; le
  contrôle des couches reste le moyen d'isoler un seuil.
* **Overbank contre pluvial.** Les quatre couches utilisées ici ont l'eau
  stagnante permanente de la commune soustraite. Pour Moroni, cela ne représente
  que 47 cellules : remplacer l'une d'elles par sa jumelle de ``pluvial/`` se voit
  à peine — mais c'est le principe qui compte, et d'autres communes portent une
  ligne de base plus importante.
* **La contrainte de projection.** Les rasters du Guatemala ont été copiés en
  EPSG:3857 pour que la carte puisse les lire. Les produits des Comores n'ont pas
  été copiés : la contrainte retombe donc sur l'application plutôt que sur les
  données. Les deux réponses sont valables ; l'avertissement de ce guide indique
  laquelle reste en suspens ici.


Suite
=====

L'exercice 2 ouvre la bibliothèque Zarr de cartes d'inondation de la commune —
les 200 scénarios, et pas seulement les 16 auxquels ce cycle correspond — et met
la tempête sur une entrée variable, de sorte que la profondeur délibérément
laissée de côté dans cet exercice arrive avec le contexte permettant de la lire.
