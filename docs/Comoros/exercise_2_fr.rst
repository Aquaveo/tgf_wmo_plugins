.. Solution de l'exercice pratique 2 des Comores, français. La version anglaise
.. se trouve à côté de ce fichier, sous le nom exercise_2.rst. Construit sur les
.. plugins de cycles TITO : une liste de cycles publie ${Date}, et chaque plugin
.. lit la commune, le cycle et une probabilité. La liste s'ouvre sur le cycle
.. d'exemple du 27 avril 2024. Les plugins sont la famille francophone
.. `_comoros`, si bien que leurs libellés et leurs sorties se lisent en français.
.. Le tableau de bord construit est dashboards/Comoros/Comoros_Hands_On_2.json.

=====================================================================
Exercice 2 : Profondeur probable sur les bâtiments et les routes
=====================================================================

Construction de **Comores Exercice 2**, pas à pas.

Rappel : l'interface est en anglais, donc les noms de boutons et de champs sont
laissés en anglais et en gras.

.. contents:: Sur cette page
   :depth: 2
   :local:
   :backlinks: none


Ce que vous allez construire
============================

Une carte à gauche montrant la classification de l'aléa d'un cycle de prévision
ainsi que les bâtiments et les routes qu'il risque d'inonder, colorés selon la
profondeur, et à droite un tableau de synthèse et une carte de synthèse
(« card ») avec les chiffres clés. Quatre contrôles en haut choisissent le fond
de carte, la commune, le cycle de prévision et la probabilité, et tout se
recalcule.

.. figure:: images/ex2-finished.png
   :alt: Le tableau de bord terminé de l'exercice 2
   :width: 100%

   **Capture :** le tableau de bord terminé, avec les quatre contrôles, la carte,
   le tableau de synthèse et la card.

Idées nouvelles ici : une entrée variable construite par un plugin (la liste des
cycles de prévision), une entrée variable dont les choix sont empruntés à un
argument de plugin (les communes), des couches vectorielles dont les entités sont
produites par un plugin plutôt que récupérées depuis une URL, et trois variables
qui pilotent quatre éléments distincts à la fois.

L'exercice 1 dessinait des **probabilités**, un raster par profondeur, cellule
par cellule. Celui-ci transforme ces mêmes probabilités en une **profondeur** par
bâtiment et par route. La *profondeur probable* d'une entité est le plus profond
des quatre seuils (10, 30, 70 et 100 cm) qu'elle atteint avec au moins la
probabilité choisie. À ``0.5``, cela signifie « l'eau la plus profonde qu'au
moins la moitié des 50 membres de la prévision mettent sur ce bâtiment ».

Le tableau de bord s'ouvre sur le **cycle d'exemple** de TITO, la prévision du
27 avril 2024 à 00:00 UTC : il y a donc toujours une inondation à regarder. La
même liste déroulante propose aussi les cycles en direct : passez à l'un d'eux
et tous les éléments suivent.

**Astuce :** ``notebooks/Comoros/02_storm_impact.ipynb`` traite en Python simple
la profondeur d'inondation sur les bâtiments et les routes : comment la
profondeur est échantillonnée sur chaque entité, et comment le tableau de
synthèse est assemblé. Il lit encore les anciens fichiers de formation (la
bibliothèque de tempêtes de l'ancienne version de cet exercice) plutôt que le
cycle d'exemple : ses chiffres diffèrent donc de ceux du tableau de bord. À
exécuter si vous voulez comprendre l'analyse avant d'assembler l'interface.

**Remarque :** Les plugins sont la famille francophone ``_comoros``, listés sous
le groupe **UFFIS: Comores** avec des libellés qui commencent par ``Comores:`` :
le tableau comme la card reviennent donc en français. C'est délibéré (les
produits comoriens sont francophones), mais c'est la première chose dont on vous
parlera, alors dites-le avant qu'on vous le demande.


Étape 1 : Créer le tableau de bord
==================================

#. Créez un nouveau tableau de bord (voir
   `Créer un tableau de bord <getting_started.rst#creating-a-dashboard>`_) avec :

   * **Name** : ``Comores Exercice 2``
   * **Description** : ``Prévision TITO en direct par commune : profondeur
     probable d'inondation sur les bâtiments et routes pour le cycle et la
     probabilité choisis``

#. Retrouvez votre tableau de bord sur la page d'accueil et double-cliquez dessus
   pour l'ouvrir. Il est vide, la prévisualisation affiche donc une zone blanche.

#. Ouvrez **Dashboard Settings** dans le coin supérieur droit et activez
   **Unrestricted Grid Item Movement**. Enregistrez les paramètres.

#. Quittez **Dashboard Settings** et cliquez sur **Edit Dashboard** dans le coin
   supérieur droit pour passer en mode édition.


Étape 2 : Ajouter les quatre contrôles
======================================

Construisez les quatre avant tout ce qui les lit. Chaque élément suivant dépend
d'au moins deux d'entre eux. Ils occupent une rangée en haut à droite, chacun
d'environ 10 colonnes de large sur 6 lignes de haut.

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

#. Choisissez **World Imagery** comme valeur initiale, enregistrez l'élément, et
   faites-le glisser en haut du tableau de bord, juste à droite de l'endroit où
   se trouvera la carte.

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
        - ``UFFIS: Comores: Comores: Résumé d'Impact par Tempête - Commune``

   Cette source d'options est générée à partir d'un argument de plugin existant,
   sous la forme ``<groupe>: <libellé du plugin> - <Argument>``. La choisir
   signifie « proposer les mêmes choix que l'argument ``commune`` du tableau de
   synthèse » : le contrôle liste donc les **55** communes et ne peut pas se
   désynchroniser des plugins.

   Ses valeurs sont des pcodes comme ``KM274_Moroni``, là où l'exercice 1
   stockait les dossiers de site TITO comme ``Comoros_Moroni``. Les deux
   conviennent ici : les plugins acceptent les deux formes, et rien dans ce
   tableau de bord n'insère la commune dans une URL.

#. Réglez **Background Color** sur ``#ffffff``, définissez la valeur initiale sur
   ``Moroni``, enregistrez, et faites glisser l'élément à côté du sélecteur de
   fond de carte.

**La liste des cycles**

Ce contrôle n'est pas du tout une **Variable Input**. C'est un plugin qui
construit lui-même la liste déroulante, à partir des cycles que TITO publie à ce
moment-là.

#. Ajoutez un troisième élément, ouvrez son menu à 3 points, sélectionnez
   **Edit**, et réglez **Visualization Type** sur **Comores: Cycles
   Disponibles** (dans le groupe **UFFIS: Comores**).

#. Renseignez :

   .. list-table::
      :header-rows: 1
      :widths: 32 68

      * - Argument
        - Valeur
      * - ``debut``
        - ``sample`` (affiché **Cycle d'exemple le plus récent**)
      * - ``texte_etiquette``
        - *laisser vide*
      * - ``afficher_etiquette``
        - *laisser tel quel*

   La liste propose chaque cycle horaire que TITO publie encore, du plus récent
   au plus ancien (environ une journée), puis les cycles d'exemple. Un cycle en
   direct s'affiche comme ``2026-10-29 12:00 UTC`` ; l'exemple s'affiche
   ``2024-04-27 00:00 UTC, ÉCHANTILLON``. ``debut`` choisit le point de départ :
   ``sample`` ouvre sur l'exemple, ``latest`` sur le cycle en direct le plus
   récent. Pour un atelier, l'exemple est le choix sûr, car un jour calme n'a
   aucune inondation à montrer.

   ``texte_etiquette`` est le libellé, et aussi le nom de la variable que publie
   l'élément. Laissée vide, la variable s'appelle ``Date``, et c'est à elle que
   se lient les plugins ci-dessous.

#. Enregistrez l'élément et faites-le glisser à droite du sélecteur de commune.

.. figure:: images/ex2-storm-input.png
   :alt: La configuration du plugin de liste des cycles
   :width: 100%

   **Capture :** les arguments de **Comores: Cycles Disponibles**, avec
   ``debut`` réglé sur le cycle d'exemple.

**L'entrée de probabilité**

#. Ajoutez un quatrième élément, ouvrez son menu à 3 points, sélectionnez
   **Edit**, et réglez **Visualization Type** sur **Variable Input**.

#. Renseignez :

   .. list-table::
      :header-rows: 1
      :widths: 32 68

      * - Argument
        - Valeur
      * - ``variable_name``
        - ``Probabilité``
      * - ``show_label``
        - ``True``
      * - ``variable_options_source``
        - ``number``

#. Définissez la valeur initiale sur ``0.5``. L'élément livré limite aussi
   l'entrée à ``0.05``-``1`` par pas de ``0.05``.

#. Enregistrez l'élément et faites-le glisser à l'extrême droite de la rangée du
   haut.


Étape 3 : Ajouter la carte avec la couche d'aléa
================================================

#. Ajoutez un autre élément, ouvrez son menu à 3 points, sélectionnez **Edit**,
   et réglez **Visualization Type** sur **Map** (dans le groupe **Default**).

#. Dans l'argument **Base Map**, choisissez ``Base Map`` dans la section
   **Variable Inputs**, en bas de la liste déroulante. La valeur devient
   ``${Fond de Carte}``.

#. Activez **Layer Control**.

#. À côté de **Layers**, cliquez sur **Add Layer**.

#. Allez directement sur l'onglet **Source** et réglez **Source Type** sur
   **Comores: Couche d'Aléa**. Les plugins de couche cartographique dynamique
   apparaissent dans la même liste **Source Type** que GeoTIFF, rangés sous leur
   groupe de plugins.

#. Les arguments du plugin apparaissent. Renseignez :

   .. list-table::
      :header-rows: 1
      :widths: 24 76

      * - Argument
        - Valeur
      * - ``commune``
        - ``${Commune}``
      * - ``cycle``
        - ``${Date}``

   Laissez vides les quatre portes (``seuil_faible`` et les autres) ainsi que
   ``source_inondation``. Les portes prennent alors les valeurs par défaut du
   plugin, 0,3, 0,2, 0,1 et 0,15 de Faible à Sévère, et les rasters la variante
   ``pluvial_overbank`` de l'exercice 1. L'exercice 3 met les quatre portes sur
   le tableau de bord ; ici, la couche sert de contexte aux bâtiments dessinés
   par-dessus.

#. Cliquez sur **Fetch plugin defaults**. La couche est nommée **Classification
   de l'aléa**, stylée avec quatre règles sur l'attribut ``alea``, et dotée d'une
   légende **Aléa** à quatre entrées.

#. Enregistrez la couche en cliquant sur **Create** au bas de l'éditeur de
   couches.

.. figure:: images/ex2-zarr-source.png
   :alt: L'onglet Source configuré pour le plugin de couche d'aléa
   :width: 100%

   **Capture :** l'onglet **Source** avec **Comores: Couche d'Aléa**
   sélectionnée, ``commune`` lié à ``${Commune}`` et ``cycle`` à ``${Date}``.


Étape 4 : Ajouter la couche de profondeur probable
==================================================

Les entités de cette couche sont calculées à chaque requête par un plugin. Il
n'y a pas d'URL GeoJSON : le plugin lit les bâtiments et les routes du cycle pour
la commune, chacun portant ses quatre probabilités, calcule la profondeur
probable de chacun, et renvoie ceux qui atteignent au moins 10 cm.

#. À côté de **Layers**, cliquez de nouveau sur **Add Layer**.

#. Allez directement sur l'onglet **Source** et réglez **Source Type** sur
   **Comores: Couche d'Impact par Tempête**.

#. Les arguments du plugin apparaissent. Renseignez :

   .. list-table::
      :header-rows: 1
      :widths: 30 70

      * - Argument
        - Valeur
      * - ``commune``
        - ``${Commune}``
      * - ``cycle``
        - ``${Date}``
      * - ``probabilite_minimale``
        - ``${Probabilité}``

#. Cliquez sur **Fetch plugin defaults**.

   C'est l'étape qui épargne le plus de travail. Le ``run()`` du plugin renvoie
   une structure toute prête : le nom de la couche, la liaison de la source, un
   style à base de règles fondé sur l'attribut ``bande`` (bande de profondeur), et
   une légende assortie. Après récupération, vous devriez voir la couche nommée
   **Profondeur probable sur les bâtiments et routes**, huit règles de style et
   une légende **Profondeur** à quatre entrées, sans avoir rien écrit vous-même.
   Écrire à la main des règles de style vectoriel est source d'erreurs : une
   règle mal formée ne correspond silencieusement à rien et laisse toutes les
   entités en gris.

#. Consultez les onglets **Style** et **Legend** pour voir ce qui est arrivé. Les
   couleurs vont du vert au jaune, au rouge puis au violet sur les quatre bandes
   (``0.1 - 0.3 m``, ``0.3 - 0.7 m``, ``0.7 - 1 m`` et ``1 m ou plus``), avec
   des règles distinctes pour les polygones (bâtiments) et les lignes (routes),
   pour que les routes aient un trait assez large pour être vues.

#. Enregistrez la couche en cliquant sur **Create** au bas de l'éditeur de
   couches.

#. Dans l'argument **Map Extent**, choisissez **Use a Custom Extent** et
   saisissez :

   .. code-block:: text

      4814984.15,-1312113.30,13.83

   C'est ``centre-x,centre-y,zoom`` en mètres EPSG:3857, centré sur Moroni.

   **Avertissement :** Comme dans l'exercice 1, **l'étendue ne suit pas la
   commune**. Passez à une commune d'une autre île et la vue reste sur Moroni
   jusqu'à ce que vous fassiez un panoramique. Les couches se rechargent
   correctement ; seule la caméra est fixe.

#. Enregistrez l'élément, puis redimensionnez la carte pour qu'elle occupe à peu
   près les 60 % gauches de la fenêtre, en laissant la bande de droite aux
   contrôles, au tableau et à la card.

#. Enregistrez le tableau de bord en cliquant sur **Save Changes** dans le coin
   supérieur droit.

.. figure:: images/ex2-dynamic-layer-source.png
   :alt: L'onglet Source avec un plugin de couche cartographique dynamique sélectionné
   :width: 100%

   **Capture :** l'onglet **Source** avec la couche de profondeur probable
   sélectionnée, ``commune``, ``cycle`` et ``probabilite_minimale`` liés, et le
   bouton **Fetch plugin defaults**.

.. figure:: images/ex2-dynamic-layer-style.png
   :alt: L'onglet Style montrant le style à base de règles récupéré
   :width: 100%

   **Capture :** l'onglet **Style** après récupération, montrant les huit règles
   sur l'attribut ``bande``.


Étape 5 : Ajouter le tableau de synthèse
========================================

#. Mettez le tableau de bord en mode édition, ajoutez un autre élément, ouvrez son
   menu à 3 points et sélectionnez **Edit**.

#. Réglez **Visualization Type** sur **Comores: Résumé d'Impact par Tempête**
   (dans le groupe **UFFIS: Comores**).

#. Renseignez :

   .. list-table::
      :header-rows: 1
      :widths: 30 70

      * - Argument
        - Valeur
      * - ``commune``
        - ``${Commune}``
      * - ``cycle``
        - ``${Date}``
      * - ``probabilite_minimale``
        - ``${Probabilité}``

   Le tableau répartit les entités inondées dans les quatre mêmes bandes de
   profondeur, de la plus profonde à la moins profonde, puis une ligne
   **TOTAL affecté**, avec le nombre de bâtiments, la population, la surface, la
   longueur de routes et la part de la population touchée. Cette part est
   rapportée aux personnes qui vivent dans les bâtiments **de la commune**, telles
   que les compte son fichier de récepteurs, et non à la population de l'île ou du
   pays : c'est pourquoi la commune doit parvenir au plugin sous forme d'argument
   plutôt que d'y être figée.

   Le titre indique la probabilité et le cycle, par exemple **Profondeur
   probable, probabilité ≥ 50% (2024-04-27 00:00 UTC, ÉCHANTILLON)**, pour qu'une
   capture du tableau ne puisse jamais passer pour une prévision en direct.

#. Enregistrez l'élément et faites-le glisser sous les contrôles, à droite.


Étape 6 : Ajouter la card de tempête
====================================

#. Ajoutez un autre élément, ouvrez son menu à 3 points et sélectionnez **Edit**.

#. Réglez **Visualization Type** sur **Comores: Résumé de Tempête** (dans le même
   groupe), et liez les trois mêmes arguments :

   .. list-table::
      :header-rows: 1
      :widths: 30 70

      * - Argument
        - Valeur
      * - ``commune``
        - ``${Commune}``
      * - ``cycle``
        - ``${Date}``
      * - ``probabilite_minimale``
        - ``${Probabilité}``

   La card donne les chiffres clés à qui ne lira pas un tableau : la pluie prévue
   sur la commune (médiane et membre le plus pluvieux des 50), la superficie
   inondée sur au moins 0,1 m avec la probabilité choisie, et les personnes et
   bâtiments **attendus** avec au moins 0,3 m. Un nombre attendu additionne la
   probabilité de chaque entité : il ne dépend donc pas de l'entrée de
   probabilité. Une commune que le cycle n'a pas déclenchée affiche à la place une
   seule ligne **Calme : non déclenchée**.

#. Enregistrez l'élément et faites-le glisser sous le tableau de synthèse.

#. Enregistrez le tableau de bord en cliquant sur **Save Changes** dans le coin
   supérieur droit.

.. figure:: images/ex2-table-card.png
   :alt: Le tableau de synthèse et la card de tempête
   :width: 100%

   **Capture :** le tableau de synthèse et la card pour Moroni sur le cycle
   d'exemple.


Étape 7 : Tester le câblage
===========================

Sur le cycle d'exemple, avec **Moroni** et **Probabilité** à ``0.5``, vous
devriez voir :

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Élément
     - Ce qu'il affiche
   * - Card
     - Pluie ``92 / 285 mm`` (médiane / membre le plus pluvieux) ; superficie
       inondée ≥ 0,1 m (P ≥ 50 %) ``1.10 km²`` ; ``1,647`` personnes et ``500``
       bâtiments attendus avec ≥ 0,3 m.
   * - Tableau
     - **TOTAL affecté** : 1 569 bâtiments, 5 805 personnes, 16,8 km de routes,
       8,33 % de la population.
   * - Couche de profondeur probable
     - 1 677 bâtiments et routes, annoncés par le message de progression pendant
       le chargement.

Essayez ensuite chaque contrôle :

* **Probabilité.** La couche de profondeur probable, le tableau et la superficie
  inondée de la card se mettent à jour ; la couche d'aléa non, car elle ne prend
  pas la probabilité. Abaissez-la et les entités deviennent plus profondes et
  plus nombreuses ; augmentez-la et il ne reste que ce sur quoi la plupart des
  membres s'accordent.
* **Commune.** Les quatre éléments produits par les plugins se rechargent sur les
  bâtiments, les routes et les rasters d'une autre commune. Seule la caméra reste
  en place.
* **Date.** Les quatre éléments produits par les plugins relisent un autre cycle.
  Sur un cycle en direct, beaucoup de communes sont calmes ; la card le dit alors
  et les couches reviennent vides, ce qui est une réponse et non une panne.


Positions des éléments
======================

La solution livrée, pour référence. Il n'est pas nécessaire de les reproduire au
pixel près : faites glisser jusqu'à une position proche et ajustez.

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
     - 10
     - 6
   * - Commune (entrée variable)
     - 70
     - 0
     - 10
     - 6
   * - Cycles Disponibles (liste des cycles)
     - 80
     - 0
     - 10
     - 6
   * - Probabilité (entrée variable)
     - 90
     - 0
     - 10
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

Contrairement à l'exercice 1, la carte n'occupe **pas** toute la fenêtre ici :
elle la partage avec les contrôles, le tableau et la card, laissez donc
**Fill Viewport** désactivé.


Point de contrôle
=================

Vous devriez maintenant avoir :

* Quatre contrôles en haut à droite : fond de carte, commune, cycle et
  probabilité.
* La liste des cycles ouverte sur ``2024-04-27 00:00 UTC, ÉCHANTILLON``, avec les
  cycles en direct listés au-dessus.
* Une carte à gauche avec deux couches plus le fond de carte dans le contrôle des
  couches.
* La classification de l'aléa en dessous, et les bâtiments et routes colorés
  selon leur profondeur probable par-dessus, avec une légende **Profondeur**, les
  routes visibles comme des lignes colorées et non comme des traits fins.
* Un tableau de synthèse et une card à droite, tous deux en français, tous deux
  mis à jour par chaque contrôle sauf le fond de carte.
* Le changement de commune remplaçant tout le jeu de données (entités, rasters
  et dénominateurs) pendant que la vue reste où elle était.


Points de discussion
====================

* **Trois variables, quatre consommateurs.** ``${Commune}`` et ``${Date}``
  atteignent les quatre éléments produits par les plugins ; ``${Probabilité}`` en
  atteint trois. Aucun des sept éléments ne connaît les autres ; tous se
  contentent de déclarer une dépendance à un nom.
* **Un plugin peut être un contrôle.** La liste des cycles est construite au
  chargement du tableau de bord, à partir de ce que TITO publie à ce moment-là :
  personne n'entretient de liste de dates. Les cycles en direct sont conservés
  environ une journée ; le cycle d'exemple reste, et c'est pourquoi un tableau
  de bord de formation s'ouvre dessus.
* **Des choix empruntés.** La liste des communes prend ses choix dans un argument
  de plugin : le tableau de bord et le plugin ne peuvent donc pas être en
  désaccord sur les communes qui existent. L'exercice 1 devait fournir sa propre
  liste, parce que ses valeurs devaient correspondre à des noms de dossiers dans
  une URL.
* **La profondeur probable est un choix de confiance.** « Profondeur probable à
  0,5 » est le seuil le plus profond qu'au moins la moitié des membres atteignent
  sur cette entité. À 0,2, la carte montre ce que prévoit un pessimiste ; à 0,8,
  ce sur quoi presque tous les membres s'accordent. Laquelle mettriez-vous devant
  un responsable de la protection civile, et que diriez-vous de l'autre ?
* **Nombres probables contre nombres attendus.** Le tableau compte les entités
  dont la profondeur probable atteint une bande à la probabilité choisie. Les
  personnes et bâtiments attendus de la card additionnent plutôt des
  probabilités : ils ne bougent donc pas avec l'entrée. Les deux sont honnêtes ;
  ils répondent à des questions différentes, et la différence mérite d'être
  montrée à l'écran.
* **Les couches dynamiques se ré-exécutent.** Chaque changement ré-exécute du
  Python qui lit le fichier de récepteurs du cycle et classe chaque bâtiment et
  chaque route de la commune. Même déclencheur qu'une couche statique, coût très
  différent : c'est pourquoi les plugins signalent leur progression pendant
  qu'ils travaillent.
* **Pourquoi le plugin livre un style.** L'alternative, écrire à la main huit
  règles dans l'interface, échoue silencieusement lorsqu'une règle est mal
  formée. Livrer le style depuis ``run()`` garantit que la couche est correcte du
  premier coup et le reste si les bandes changent.


Suite
=====

L'exercice 3 confie à l'utilisateur les seuils de probabilité de la couche
d'aléa, en utilisant les couches d'aléa et d'impact qui classent selon les quatre
rasters de dépassement de l'exercice 1.
