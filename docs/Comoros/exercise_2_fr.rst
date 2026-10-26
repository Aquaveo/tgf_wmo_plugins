.. Solution de l'exercice pratique 2 des Comores, français. La version anglaise
.. se trouve à côté de ce fichier, sous le nom exercise_2.rst. Ce qui diffère du
.. guide du Guatemala est expliqué là où cela se présente : la bibliothèque de
.. profondeurs est par commune et non nationale, un second sélecteur la pilote
.. donc ; et les plugins sont la famille francophone `_comoros`, si bien que
.. leurs libellés et leurs sorties se lisent en français.
.. Le tableau de bord construit est dashboards/Comoros/Comoros_Hands_On_2.json.

=================================================
Exercice 2 — Impact d'une seule tempête
=================================================

Construction de **Comores Exercice 2**, pas à pas.

Rappel : l'interface est en anglais, donc les noms de boutons et de champs sont
laissés en anglais et en gras.

.. contents:: Sur cette page
   :depth: 2
   :local:
   :backlinks: none


Ce que vous allez construire
============================

Une carte à gauche montrant la profondeur d'inondation d'une tempête ainsi que
les bâtiments et les routes qu'elle inonde, et à droite un tableau de synthèse et
une carte de synthèse (« card ») avec les chiffres clés. Trois contrôles en haut
choisissent le fond de carte, la commune et la tempête, et tout se recalcule.

.. figure:: images/ex2-finished.png
   :alt: Le tableau de bord terminé de l'exercice 2
   :width: 100%

   **Capture :** le tableau de bord terminé, avec les trois sélecteurs, la carte,
   le tableau de synthèse et la card.

Idées nouvelles ici : lire une tranche d'un magasin Zarr, une couche vectorielle
dont les entités sont produites par un plugin plutôt que récupérées depuis une
URL, et deux entrées variables qui pilotent quatre choses distinctes à la fois.

L'exercice 1 dessinait des **probabilités** sur toute une prévision. Celui-ci
dessine la **profondeur** dans un scénario précis de la bibliothèque communale —
une grandeur physique, qui n'a donc besoin d'aucun seuil pour être interprétée. La
section 9 du notebook associé montre comment les deux se relient.

**Astuce** — ``notebooks/Comoros/02_storm_impact.ipynb`` dérive en Python simple
les chiffres que montre ce tableau de bord : comment la profondeur est
échantillonnée sur chaque bâtiment et chaque route, et comment le tableau de
synthèse est assemblé. Il reconstruit aussi le raster de probabilité de
l'exercice 1 à partir des 50 membres de la prévision et le compare à celui qui a
été publié. À exécuter d'abord si vous voulez comprendre l'analyse avant
d'assembler l'interface.

**Remarque** — Les plugins sont la famille francophone ``_comoros`` : leur groupe
s'affiche donc sous **Cartes d'Inondation (Français)** dans la liste déroulante,
et le tableau comme la card reviennent en français, dans un tableau de bord dont
le titre original est en anglais. C'est délibéré — les produits comoriens sont
francophones — mais c'est la première chose dont on vous parlera, alors dites-le
avant qu'on ne le demande.


Étape 1 — Créer le tableau de bord
==================================

#. Créez un nouveau tableau de bord (voir
   `Créer un tableau de bord <getting_started.rst#creating-a-dashboard>`_) avec :

   * **Name** : ``Comores Exercice 2``
   * **Description** : ``Solution pour l'exercice pratique OMM Comores n°2``

#. Retrouvez votre tableau de bord sur la page d'accueil et double-cliquez dessus
   pour l'ouvrir. Il est vide, la prévisualisation affiche donc une zone blanche.

#. Ouvrez **Dashboard Settings** dans le coin supérieur droit et activez
   **Unrestricted Grid Item Movement**. Enregistrez les paramètres.

#. Quittez **Dashboard Settings** et cliquez sur **Edit Dashboard** dans le coin
   supérieur droit pour passer en mode édition.


Étape 2 — Ajouter les trois entrées variables
=============================================

Construisez les trois avant tout ce qui les lit. Chaque élément ultérieur dépend
d'au moins l'une d'elles.

**Le sélecteur de fond de carte**

#. Vous verrez un élément déjà présent sur le tableau de bord. Cliquez sur son
   menu à 3 points et sélectionnez **Edit**.

#. Réglez **Visualization Type** sur **Variable Input** (dans le groupe
   **Default**), et renseignez :

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

#. Sur l'onglet **Settings**, réglez **Background Color** sur ``#ffffff``.

#. Choisissez **World Imagery** comme valeur initiale, enregistrez l'élément et
   faites-le glisser en haut du tableau de bord, juste à droite de l'emplacement
   où se trouvera la carte.

**Le sélecteur de commune**

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

#. Dans l'éditeur de **choices**, chaque entrée comporte une **label** que lit
   l'utilisateur et une **value** qui part dans l'URL — le nom de la commune et
   son segment de chemin, comme dans l'exercice 1 :

   .. list-table::
      :header-rows: 1
      :widths: 40 60

      * - Étiquette
        - Valeur
      * - ``Moroni``
        - ``KM274_Moroni``
      * - ``Fomboni``
        - ``KM321_Fomboni``
      * - …
        - …

   **Important** — Cette liste déroulante porte **22 communes, et non les 55 de
   l'exercice 1.** L'exercice 1 lit les rasters de probabilité, que le cycle
   publie pour chaque commune. Celui-ci lit les bibliothèques Zarr de cartes
   d'inondation, et seules 22 d'entre elles avaient fini d'être téléversées — tout
   à partir de ``KM251``. Proposer une commune dont la bibliothèque est absente
   produit une erreur d'ouverture du magasin nommant l'URL : la liste est donc
   réduite à ce qui existe. Revérifiez le bucket avant un atelier ; si les autres
   sont arrivées, élargissez-la.

#. Réglez **Background Color** sur ``#ffffff``, définissez la valeur initiale sur
   ``Moroni``, enregistrez, et faites glisser l'élément à côté du sélecteur de
   fond de carte.

**Le sélecteur de tempête**

#. Ajoutez un troisième élément, ouvrez son menu à 3 points, sélectionnez **Edit**
   et réglez **Visualization Type** sur **Variable Input**.

#. Renseignez :

   .. list-table::
      :header-rows: 1
      :widths: 32 68

      * - Argument
        - Valeur
      * - ``variable_name``
        - ``Tempête``
      * - ``show_label``
        - ``True``
      * - ``variable_options_source``
        - ``Cartes d'Inondation (Français): Résumé de Tempête (Comores) - Index``

   Cette source d'options est générée à partir d'un argument de plugin existant,
   sous la forme ``<groupe>: <libellé du plugin> - <Argument>``. La choisir revient
   à dire « proposer les mêmes choix que l'argument ``index`` de la card de
   tempête » : le contrôle est donc peuplé par le plugin et ne peut pas se
   désynchroniser de lui.

   Les choix sont les 200 positions de la bibliothèque d'une commune, étiquetées
   par position. Elles ne sont **pas** étiquetées en millimètres, et c'est
   délibéré : une magnitude comorienne est la pluie moyenne pondérée par la
   surface sur une seule commune, si bien que la même position vaut 346 mm dans
   une commune et 462 mm dans une autre. Ce qui est identique partout, c'est
   l'ordre — chaque bibliothèque contient 200 scénarios triés par magnitude, donc
   une position plus élevée est une tempête plus humide où que vous soyez. La card
   de l'étape 6 indique les millimètres réels une fois la commune choisie.

#. Sur l'onglet **Settings**, réglez **Background Color** sur ``#ffffff``.

#. Définissez la valeur initiale, enregistrez l'élément et faites-le glisser à
   l'extrême droite de la rangée du haut.

.. figure:: images/ex2-storm-input.png
   :alt: La configuration de l'entrée variable du sélecteur de tempête
   :width: 100%

   **Capture :** les arguments **Variable Input** du sélecteur de tempête, avec
   la source d'options dérivée du plugin sélectionnée.


Étape 3 — Ajouter la carte avec la couche de profondeur Zarr
============================================================

#. Ajoutez un autre élément, ouvrez son menu à 3 points, sélectionnez **Edit** et
   réglez **Visualization Type** sur **Map** (dans le groupe **Default**).

#. Dans l'argument **Base Map**, choisissez ``Base Map`` dans la section
   **Variable Inputs**, en bas de la liste déroulante. La valeur devient
   ``${Fond de Carte}``.

#. Activez **Layer Control**.

#. À côté de **Layers**, cliquez sur **Add Layer**.

#. Sur l'onglet **Layer**, réglez :

   .. list-table::
      :header-rows: 1
      :widths: 24 76

      * - Champ
        - Valeur
      * - ``name``
        - ``Profondeur d'inondation (m), bibliothèque communale``

#. Sur l'onglet **Source**, réglez **Source Type** sur **Zarr** et renseignez :

   .. list-table::
      :header-rows: 1
      :widths: 24 76

      * - Champ
        - Valeur
      * - ``url``
        - ``https://cog-s3-test-401506828094-us-east-1-an.s3.us-east-1.amazonaws.com/Comoros_IBF/Comoros/fim_store_${Commune}_v1.zarr``
      * - ``variable``
        - ``depth``
      * - ``index``
        - ``${Tempête}``
      * - ``mask_below``
        - ``0.05``

   Deux variables dans une même source, avec des rôles différents. ``${Commune}``
   est insérée dans l'URL : la changer ouvre donc un **magasin différent**.
   ``${Tempête}`` occupe tout le champ ``index`` : la changer lit donc une
   **tranche différente** du magasin déjà ouvert. Le magasin contient les 200
   scénarios dans un seul tableau et ``index`` en sélectionne un — pas de couches
   dupliquées, pas de fichiers séparés, et seule la quantité de données d'un
   scénario transite sur le réseau.

   ``mask_below`` vaut ``0.05`` parce que c'est l'``extent_threshold_m`` propre au
   magasin : le modèle ne considère pas une cellule comme inondée en dessous de
   5 cm. Réutiliser le nombre avec lequel les données ont été construites vaut
   mieux que d'en inventer un.

#. Sur l'onglet **Style**, laissez le mode sur **Continuous** et choisissez la
   rampe **Blues** (sous **Single hue**). Laissez **Min** et **Max** vides.

   Laisser les deux bornes vides signifie « les résoudre à partir des données au
   moment du rendu » : la rampe se ré-étire donc pour chaque scénario quand la
   tempête change. La profondeur est une propriété du scénario particulier, la
   mise à l'échelle automatique est donc juste ici — l'inverse des couches de
   probabilité de l'exercice 1, qui devaient être fixées à 0–1 pour pouvoir être
   comparées entre elles. Comme il n'y a rien d'autre sur cette carte, un bleu
   monochrome se lit comme de l'eau sans légende.

#. Sur l'onglet **Legend**, sélectionnez **Default Legend**.

#. Enregistrez la couche en cliquant sur **Create** au bas de l'éditeur de
   couches.

.. figure:: images/ex2-zarr-source.png
   :alt: L'onglet Source configuré pour le magasin Zarr
   :width: 100%

   **Capture :** l'onglet **Source** avec **Source Type** Zarr, l'URL du magasin
   portant ``${Commune}``, ``variable`` depth, ``index`` ``${Tempête}`` et
   ``mask_below`` 0.05.


Étape 4 — Ajouter la couche d'impact produite par le plugin
===========================================================

Les entités de cette couche sont calculées à chaque requête par un plugin. Il n'y
a pas d'URL GeoJSON — le plugin échantillonne la profondeur sur chaque bâtiment et
chaque route de la commune et renvoie le résultat.

#. À côté de **Layers**, cliquez de nouveau sur **Add Layer**.

#. Allez directement sur l'onglet **Source** et réglez **Source Type** sur
   **Couche d'Impact par Tempête (Comores)**. Les plugins de couches
   cartographiques dynamiques apparaissent dans la même liste **Source Type** que
   GeoTIFF et Zarr, classés sous leur groupe de plugins.

#. Les arguments du plugin apparaissent. Renseignez :

   .. list-table::
      :header-rows: 1
      :widths: 24 76

      * - Argument
        - Valeur
      * - ``commune``
        - ``${Commune}``
      * - ``index``
        - ``${Tempête}``

#. Cliquez sur **Fetch plugin defaults**.

   C'est l'étape qui épargne le plus de travail. Le ``run()`` du plugin renvoie
   une ossature toute faite — le nom de la couche, la liaison à la source, un
   style à base de règles fondé sur l'attribut ``bande`` (tranche de profondeur)
   et une légende assortie. Après récupération, vous devriez voir huit règles de
   style et une légende **Profondeur** à quatre entrées, dont aucune n'a eu besoin
   d'être écrite. Rédiger des règles de style vectoriel à la main est source
   d'erreurs : une règle mal formée ne correspond jamais à rien, silencieusement,
   et laisse toutes les entités en gris.

#. Renommez la couche en ``Bâtiments et routes inondés`` sur l'onglet **Layer**
   si vous voulez qu'elle corresponde à la solution livrée.

#. Consultez les onglets **Style** et **Legend** pour voir ce qui est arrivé. Les
   couleurs vont du vert au jaune, au rouge puis au violet sur quatre tranches de
   profondeur, avec des règles distinctes pour les polygones (bâtiments) et les
   lignes (routes), afin que les routes reçoivent un trait assez large pour être
   vues.

#. Enregistrez la couche en cliquant sur **Create** au bas de l'éditeur de
   couches.

#. Dans l'argument **Map Extent**, choisissez **Use a Custom Extent** et
   saisissez :

   .. code-block:: text

      4814984.15,-1312113.30,13.83

   C'est ``centre-x,centre-y,zoom`` en mètres EPSG:3857, centré sur Moroni.

   **Avertissement** — Comme dans l'exercice 1, **l'étendue ne suit pas la
   commune**. Passez à une commune d'une autre île et la vue reste sur Moroni
   jusqu'à ce que vous fassiez un panoramique. Les couches se rechargent
   correctement ; seule la caméra est figée.

#. Enregistrez l'élément, puis redimensionnez la carte pour qu'elle occupe à peu
   près les 60 % gauches de la fenêtre, en laissant la bande de droite au tableau
   et à la card.

#. Enregistrez le tableau de bord en cliquant sur **Save Changes** dans le coin
   supérieur droit.

.. figure:: images/ex2-dynamic-layer-source.png
   :alt: L'onglet Source avec un plugin de couche cartographique dynamique sélectionné
   :width: 100%

   **Capture :** l'onglet **Source** avec la couche d'impact par tempête
   sélectionnée, ``commune`` et ``index`` liés, et le bouton
   **Fetch plugin defaults**.

.. figure:: images/ex2-dynamic-layer-style.png
   :alt: L'onglet Style montrant le style à base de règles récupéré
   :width: 100%

   **Capture :** l'onglet **Style** après récupération, montrant les huit règles
   sur l'attribut ``bande``.


Étape 5 — Ajouter le tableau de synthèse
========================================

#. Mettez le tableau de bord en mode édition, ajoutez un autre élément, ouvrez son
   menu à 3 points et sélectionnez **Edit**.

#. Réglez **Visualization Type** sur **Résumé d'Impact par Tempête (Comores)**
   (dans le groupe **Cartes d'Inondation (Français)**).

#. Renseignez :

   .. list-table::
      :header-rows: 1
      :widths: 24 76

      * - Argument
        - Valeur
      * - ``commune``
        - ``${Commune}``
      * - ``index``
        - ``${Tempête}``

   Le tableau répartit les entités inondées du scénario en tranches de
   profondeur, la plus profonde en premier, avec le nombre de bâtiments, la
   population, la surface, la longueur de route et la part de la population **de
   la commune** touchée — et non celle de l'île ou du pays, ce qui explique
   pourquoi la commune doit parvenir au plugin sous forme d'argument plutôt que
   d'y être figée.

#. Enregistrez l'élément et faites-le glisser en haut à droite du tableau de bord.


Étape 6 — Ajouter la card de tempête
====================================

#. Ajoutez un autre élément, ouvrez son menu à 3 points et sélectionnez **Edit**.

#. Réglez **Visualization Type** sur **Résumé de Tempête (Comores)** (dans le même
   groupe), et liez les deux mêmes arguments :

   .. list-table::
      :header-rows: 1
      :widths: 24 76

      * - Argument
        - Valeur
      * - ``commune``
        - ``${Commune}``
      * - ``index``
        - ``${Tempête}``

   La card donne les chiffres clés — le cumul de pluie du scénario, la surface
   inondée, la hauteur d'eau maximale et la profondeur moyenne là où c'est
   mouillé — pour qui ne lira pas un tableau. C'est ici que la magnitude en
   millimètres apparaît enfin, parce que ce n'est qu'à ce moment que la commune et
   le scénario sont tous deux connus.

#. Enregistrez l'élément et faites-le glisser sous le tableau de synthèse.

#. Enregistrez le tableau de bord en cliquant sur **Save Changes** dans le coin
   supérieur droit.

.. figure:: images/ex2-table-card.png
   :alt: Le tableau de synthèse et la card de tempête
   :width: 100%

   **Capture :** le tableau de synthèse et la card pour un scénario.


Étape 7 — Tester le câblage
===========================

Changez l'entrée **Tempête**. Quatre choses doivent se mettre à jour : la couche
Zarr relit sa tranche, la couche d'impact se réexécute, et le tableau comme la
card se rechargent. Des messages de progression s'affichent pendant que la couche
d'impact recalcule.

Changez ensuite la **Commune**. Les quatre mêmes éléments se mettent à jour, mais
cette fois la couche Zarr ouvre un magasin entièrement différent et les plugins
lisent un autre jeu de bâtiments et de routes. Seule la caméra ne bouge pas.

À essayer aux deux extrémités de la bibliothèque :

.. list-table::
   :header-rows: 1
   :widths: 18 82

   * - Tempête
     - Ce que vous devriez voir
   * - ``0``
     - Presque rien — c'est l'eau stagnante permanente de la commune, pas une
       tempête. La card indique un cumul de pluie proche de zéro.
   * - ``150``
     - Une emprise importante. Pour Moroni, la card affiche environ 423 mm et
       12 km².
   * - ``199``
     - Le scénario le plus humide de la bibliothèque, et la seule extrémité où la
       tranche ``2 m ou plus`` a une chance d'apparaître.


Positions des éléments
======================

La solution livrée, pour référence. Il n'est pas nécessaire de les reproduire au
pixel près — faites glisser jusqu'à une position proche et ajustez.

.. list-table::
   :header-rows: 1
   :widths: 46 13 13 13 15

   * - Élément
     - ``x``
     - ``y``
     - ``w``
     - ``h``
   * - Carte
     - 0
     - 0
     - 60
     - 44
   * - Fond de Carte (entrée variable)
     - 60
     - 0
     - 13
     - 6
   * - Commune (entrée variable)
     - 74
     - 0
     - 13
     - 6
   * - Tempête (entrée variable)
     - 89
     - 0
     - 11
     - 6
   * - Résumé d'Impact par Tempête (tableau)
     - 60
     - 9
     - 40
     - 20
   * - Résumé de Tempête (card)
     - 62
     - 29
     - 37
     - 12

Contrairement à l'exercice 1, la carte **ne** remplit **pas** la fenêtre ici — elle
la partage avec le tableau et la card, laissez donc **Fill Viewport** désactivé.


Point de contrôle
=================

Vous devriez maintenant avoir :

* Trois sélecteurs en haut : fond de carte, commune et tempête.
* Une carte à gauche avec deux couches plus le fond de carte dans le contrôle des
  couches.
* La profondeur dessinée en bleu, se remettant à l'échelle quand la tempête
  change.
* Les bâtiments et les routes colorés par tranche de profondeur par-dessus, avec
  une légende **Profondeur**, et des routes visibles sous forme de lignes colorées
  plutôt que de traits fins.
* Un tableau de synthèse et une card à droite, tous deux en français, tous deux se
  mettant à jour avec l'un ou l'autre sélecteur.
* Le changement de commune remplaçant tout le jeu de données — magasin, entités et
  dénominateurs — pendant que la vue reste là où elle était.


Points de discussion
====================

* **Deux variables, quatre consommateurs.** ``${Tempête}`` apparaît dans l'index
  d'une source Zarr, dans un argument de couche plugin et dans deux arguments de
  visualisation ; ``${Commune}`` apparaît à tous les mêmes endroits, plus dans
  l'URL du magasin. Aucun des six éléments ne connaît les autres ; ils déclarent
  tous simplement une dépendance envers un nom.
* **Insertion contre substitution.** ``${Tempête}`` occupe un champ entier : elle
  se résout donc en une valeur, type compris. ``${Commune}`` se trouve à
  l'intérieur d'une URL plus longue : elle est donc insérée dans le texte
  environnant. Même syntaxe, comportement différent, et c'est ce qui permet à une
  seule couche d'atteindre 22 magasins différents.
* **Les couches dynamiques se réexécutent ; les couches statiques se
  rechargent.** La couche Zarr relit une tranche d'un tableau déjà ouvert. La
  couche d'impact réexécute du Python qui échantillonne un raster sur quelque
  25 000 géométries. Même déclencheur, coût très différent — d'où le fait que le
  plugin signale sa progression pendant qu'il travaille.
* **Pourquoi l'échantillonnage n'est pas une rastérisation.** Le plugin du
  Guatemala grave les identifiants des entités dans une grille et relit les
  profondeurs par identifiant, ce qui fonctionne avec ses cellules de 5 m. Ici les
  cellules font 30,57 m et la plupart des bâtiments sont plus petits qu'une
  cellule : beaucoup en partagent donc une — graver les identifiants garde le
  dernier et perd silencieusement les autres, soit environ 61 % des entités. Le
  plugin des Comores construit à la place une liste de paires (entité, cellule),
  qui autorise plusieurs entités par cellule. Même question, grille différente,
  méthode différente : il vaut la peine de vérifier la couverture chaque fois
  qu'une méthode d'échantillonnage rencontre une nouvelle grille.
* **Profondeur contre probabilité.** L'exercice 1 demandait « quelles sont les
  chances d'avoir 30 cm ici » sur toute une prévision. Celui-ci demande « quelle
  profondeur dans ce scénario précis ». Les deux utilisent les mêmes bâtiments.
  Lequel placeriez-vous devant un officier de protection civile, et que diriez-vous
  de l'autre ?
* **Pourquoi le plugin livre un style.** L'alternative — écrire huit règles à la
  main dans l'interface — échoue silencieusement dès qu'une règle est mal formée.
  Livrer le style depuis ``run()`` fait que la couche est correcte du premier coup
  et le reste si les tranches changent.


Suite
=====

L'exercice 3 confie les seuils de probabilité eux-mêmes à l'utilisateur, à l'aide
des couches d'aléa et d'impact qui classent les quatre rasters de dépassement de
l'exercice 1.
