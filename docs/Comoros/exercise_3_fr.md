<!--
Solution de l'exercice pratique 3 des Comores, français. La version anglaise
se trouve à côté de ce fichier, sous le nom exercise_3.rst. Ce qui diffère du
guide du Guatemala est expliqué là où cela se présente : un cinquième contrôle
choisit la commune, car tout produit des Comores est par commune ; le seuil
Sévère n'a besoin d'aucun cas particulier ici ; et les plugins sont la famille
francophone `_comoros`, si bien que leurs libellés se lisent en français.
Chaque plugin lit le cycle d'exemple TITO du 27 avril 2024 (`cycle` = `sample`).
Le tableau de bord construit est dashboards/Comoros/Comoros_Hands_On_3.json.
-->

# Exercice 3 : Classification de l'aléa à seuils ajustables

Construction de **Comores Exercice 3**, pas à pas.

**Commencez ici :** Cet exercice réutilise les quatre couches de probabilité de
l'[Exercice 1](exercise_1_fr.md) : le construire d'abord vous fera gagner du
temps.

Rappel : l'interface est en anglais, donc les noms de boutons et de champs sont
laissés en anglais et en gras.

## Ce que vous allez construire

Une carte plein écran portant les quatre rasters de probabilité de l'exercice 1,
plus deux couches calculées : une classification de l'aléa, et les bâtiments et
routes qui tombent à l'intérieur. Quatre entrées numériques en haut fixent le
seuil de probabilité de chaque niveau d'aléa, une liste déroulante de communes
choisit l'endroit, et un tableau d'impact se place sous les seuils. Changez un
seuil et la classification, les entités touchées et le tableau se recalculent
tous.

![Le tableau de bord terminé de l'exercice 3](images/ex3-finished.png)

**Capture :** le tableau de bord terminé : carte plein écran, quatre entrées de
seuil en haut, sélecteur de commune en haut à gauche, tableau d'impact à
droite.

**Astuce :** `notebooks/Comoros/03_hazard_classification.ipynb` dérive cette
classification en Python simple, y compris le piège de l'échelle en pourcentage
et le filtre par commune que les plugins gèrent désormais pour vous. À exécuter
d'abord si vous voulez comprendre l'analyse avant d'assembler l'interface. Le
notebook lit encore les anciens fichiers de formation plutôt que le cycle
d'exemple : ses chiffres peuvent donc différer de ceux du tableau de bord.

## Comprendre les quatre seuils

Chaque niveau d'aléa est lié à **un** seuil de profondeur et possède **sa propre**
porte de probabilité :

| Niveau | Piloté par | Couleur | Porte par défaut |
| --- | --- | --- | --- |
| Faible (Low) | P(≥ 10 cm) | vert | 0.8 |
| Moyen (Medium) | P(≥ 30 cm) | jaune | 0.8 |
| Élevé (High) | P(≥ 70 cm) | rouge | 0.8 |
| Sévère (Severe) | P(≥ 100 cm) | violet | 0.8 |

Une cellule prend le niveau du seuil le **plus profond** dont elle franchit la
porte.

**Remarque :** **Les quatre portes peuvent toutes rester à 0,8 ici, et cela mérite
d'être dit à voix haute** si vous avez déjà enseigné la version du Guatemala.
Là-bas, le raster à 76 cm ne contient jamais que 0 ou 0,2 : sa porte Sévère doit
donc être abaissée à 0,2, sans quoi la classe ne peut jamais apparaître. À
Moroni, chaque couche du cycle d'exemple atteint 1,0, et des cellules franchissent
0,8 à chaque profondeur (861 cellules à 10 cm, 82 à 30 cm, 8 à 70 cm et 2 à
100 cm) : rien n'a donc à être affaibli pour que le niveau supérieur ait un
sens. La leçon survit à la différence : vérifiez
quelle plage une couche peut réellement atteindre avant d'exposer un contrôle
pour elle.

## Étape 1 : Créer le tableau de bord

1. Créez un nouveau tableau de bord (voir
   [Créer un tableau de bord](getting_started.rst#creating-a-dashboard)) avec :

   - **Name** : `Comores Exercice 3`
   - **Description** : `Solution pour l'exercice pratique OMM Comores n°3`

1. Retrouvez votre tableau de bord sur la page d'accueil et double-cliquez dessus
   pour l'ouvrir.

1. Ouvrez **Dashboard Settings** dans le coin supérieur droit et activez
   **Unrestricted Grid Item Movement**. Enregistrez les paramètres.

1. Quittez **Dashboard Settings** et cliquez sur **Edit Dashboard** pour passer en
   mode édition.

## Étape 2 : Ajouter les sélecteurs de fond de carte et de commune

Les deux sont exactement comme dans l'exercice 1 : si vous avez construit ce
tableau de bord, le plus rapide est **Export** dans le menu à 3 points de chaque
élément, puis **Import Dashboard Item** ici.

Pour les construire de zéro :

1. Cliquez sur le menu à 3 points de l'élément existant, sélectionnez **Edit**, et
   réglez **Visualization Type** sur **Variable Input**.

1. Renseignez `variable_name` `Fond de Carte`, `show_label` `True`,
   `variable_options_source` `Base Map Layers`. Réglez **Background Color** sur
   `#ffffff`, choisissez **World Imagery**, enregistrez, et faites glisser
   l'élément en haut à gauche.

1. Ajoutez un autre élément, réglez-le sur **Variable Input**, et renseignez
   `variable_name` `Commune`, `show_label` `True`,
   `variable_options_source` `dropdown`.

1. Remplissez l'éditeur de **choices** avec les communes, étiquette et valeur
   comme dans l'exercice 1 : `Moroni` / `Comoros_Moroni`, et ainsi de suite.
   La valeur est le dossier de site TITO, parce que les quatre URL raster
   l'insèrent dans leur chemin ; les plugins des étapes 5, 6 et 8 acceptent
   aussi cette forme (ainsi que la forme pcode, `KM274_Moroni`), si bien qu'un
   seul `${Commune}` alimente les deux.

   **Remarque :** La solution livrée ne porte que **22 communes**, toutes celles
   à partir de `Comoros_Ngouengoe`, une liste héritée d'une version antérieure
   de l'exercice 2. Cet exercice ne lit que les rasters de probabilité et le
   geopackage de récepteurs, et le cycle d'exemple **publie les deux pour les
   55** : la liste peut donc être élargie sans risque ici. L'exercice 1 propose
   déjà les 55 si vous préférez importer cet élément.

1. Réglez **Background Color** sur `#ffffff`, définissez la valeur initiale sur
   `Moroni`, enregistrez, et faites glisser l'élément à côté du sélecteur de
   fond de carte.

## Étape 3 : Ajouter les quatre entrées de seuil

Construisez les quatre avant les couches qui les consomment. Chacune est une
**Variable Input** dont `variable_options_source` vaut `number` :

| `variable_name` |
| --- |
| `Seuil Faible (P(≥10 cm))` |
| `Seuil Moyen (P(≥30 cm))` |
| `Seuil Élevé (P(≥70 cm))` |
| `Seuil Sévère (P(≥100 cm))` |

Pour **chacune** des quatre :

1. Ajoutez un élément au tableau de bord, ouvrez son menu à 3 points, sélectionnez
   **Edit**, et réglez **Visualization Type** sur **Variable Input**.

1. Renseignez :

   | Argument | Valeur |
   | --- | --- |
   | `variable_name` | *voir le tableau ci-dessus* |
   | `show_label` | `True` |
   | `variable_options_source` | `number` |

1. Sur l'onglet **Settings**, réglez **Background Color** sur `#ffffff` et
   ajoutez une bordure supérieure, en changeant son style en `solid` pour
   qu'elle s'affiche. Donnez à l'entrée la plus à gauche une bordure gauche et à
   celle la plus à droite une bordure droite, pour que les quatre se lisent comme
   une seule bande.

1. Définissez la valeur initiale sur `0.8`.

1. Enregistrez l'élément et faites-le glisser en place le long du haut du tableau
   de bord, à droite du sélecteur de commune.

Les noms portent la profondeur qu'ils contrôlent, `(P(≥10 cm))` et ainsi de
suite, parce que l'argument de plugin auquel ils se lient s'appelle seulement
`seuil_faible`. Sans la profondeur dans le nom de la variable, rien sur le
tableau de bord n'indique à quoi sert chaque seuil.

![Les quatre entrées variables de seuil en haut du tableau de bord](images/ex3-threshold-inputs.png)

**Capture :** les quatre entrées de seuil côte à côte, chacune affichant son
libellé et sa valeur.

## Étape 4 : Ajouter la carte et les quatre rasters de probabilité

Si vous avez l'exercice 1, réutilisez sa carte :

1. Ouvrez le tableau de bord de l'exercice 1, cliquez sur le menu à 3 points de
   l'élément carte, choisissez **Export**.

1. De retour dans ce tableau de bord, cliquez sur **Import Dashboard Item** et
   importez-le.

1. Modifiez l'élément carte. Pour chacun des quatre rasters, ouvrez la couche et
   désactivez **Default Visibility** sur l'onglet **Layer**, pour que ce soit la
   classification qui s'affiche au chargement et que les rasters soient là pour
   être activés à des fins de comparaison. Enregistrez chaque couche.

1. Sur l'onglet **Source** de chaque raster, remettez `mask_below` à `0`.
   L'exercice 1 le liait à une entrée `Masque de Probabilité` qui n'existe pas
   ici (ce sont les seuils qui assurent ce filtrage désormais), et une variable
   non résolue laisse le champ vide.

Si vous n'avez pas l'exercice 1, construisez la carte et les quatre rasters de
zéro comme il y est décrit, puis poursuivez. Dans les deux cas, les quatre URL
pointent vers le cycle d'exemple,
`https://tito.uffis.org/sample/comoros/20240427.000000/`, c'est-à-dire le
même cycle que lisent les plugins ci-dessous.

1. Si la carte recouvre les entrées, cliquez sur son menu à 3 points, survolez
   **Order** et sélectionnez **Send to Back**.

1. Enregistrez le tableau de bord.

## Étape 5 : Ajouter la couche de classification de l'aléa

1. Mettez le tableau de bord en mode édition, puis cliquez sur le menu à 3 points
   de l'élément carte et sélectionnez **Edit**. Vous devrez peut-être déplacer une
   entrée de seuil pour atteindre le menu de la carte.

1. À côté de **Layers**, cliquez sur **Add Layer**.

1. Allez directement sur l'onglet **Source** et réglez **Source Type** sur
   **Comores: Couche d'Aléa** (listée sous le groupe **UFFIS: Comores**).

1. Les arguments du plugin apparaissent. Renseignez :

   | Argument | Valeur |
   | --- | --- |
   | `seuil_faible` | `${Seuil Faible (P(≥10 cm))}` |
   | `seuil_moyen` | `${Seuil Moyen (P(≥30 cm))}` |
   | `seuil_eleve` | `${Seuil Élevé (P(≥70 cm))}` |
   | `seuil_severe` | `${Seuil Sévère (P(≥100 cm))}` |
   | `commune` | `${Commune}` |
   | `cycle` | `sample` (affiché **Événement d'exemple** dans la liste) |

   Six arguments, et non quatre. Tout produit des Comores est écrit par commune :
   le plugin ne peut donc pas savoir quels rasters classer tant que la commune ne
   lui est pas parvenue, la même raison pour laquelle les exercices 1 et 2
   portent chacun un sélecteur de commune. `cycle` indique quel cycle TITO
   lire, et `sample` désigne le cycle d'exemple publié pour le pays, les mêmes
   données du 27 avril 2024 que dessinent les quatre couches raster. Laissé vide,
   il lirait plutôt le dernier cycle en direct.

   Laissez `source_inondation` vide. Sa valeur par défaut est **Pluviale
   (débordement)**, la même variante `pluvial_overbank` que les quatre couches
   raster.

1. Cliquez sur **Fetch plugin defaults**. La couche est nommée **Classification
   de l'aléa**, stylée avec quatre règles sur l'attribut `alea`, et dotée d'une
   légende **Aléa** à quatre entrées.

1. Enregistrez la couche en cliquant sur **Create**.

![La configuration de la source de la couche d'aléa avec ses portes, sa commune et son cycle](images/ex3-hazard-layer-source.png)

**Capture :** l'onglet **Source** de la couche d'aléa, avec les quatre portes
et la commune liées à des variables, et `cycle` réglé sur l'exemple.

## Étape 6 : Ajouter la couche des entités touchées

1. À côté de **Layers**, cliquez de nouveau sur **Add Layer**.

1. Allez directement sur l'onglet **Source** et réglez **Source Type** sur
   **Comores: Couche d'Impact**.

1. Renseignez les mêmes arguments qu'à l'étape précédente : les quatre portes
   et la commune liées aux cinq mêmes variables, et `cycle` réglé sur
   `sample`. Ce plugin n'a pas de `source_inondation` : il lit les
   probabilités déjà portées par chaque bâtiment et chaque route.

1. Cliquez sur **Fetch plugin defaults**. La couche arrive sous le nom
   **Bâtiments et routes en danger**, avec huit règles (polygone et ligne par
   niveau) et une légende **Aléa**.

1. Enregistrez la couche en cliquant sur **Create**.

Les deux couches répondent à des questions différentes à partir des mêmes seuils :
la couche d'aléa classe le *terrain*, celle-ci classe les *biens*. Les garder
séparées permet à l'utilisateur de désactiver l'ombrage du sol et de ne regarder
que ce qui est touché.

## Étape 7 : Terminer la carte

1. Dans l'argument **Map Extent**, choisissez **Use a Custom Extent** et
   saisissez :

   ```text
   4814984.15,-1312113.30,13.83
   ```

1. Sur l'onglet **Settings**, activez **Fill Viewport** pour que la carte occupe
   toute la fenêtre.

1. Enregistrez l'élément, redimensionnez la carte pour remplir la fenêtre, et
   remettez en place toute entrée de seuil que vous auriez déplacée.

1. Enregistrez le tableau de bord.

**Avertissement :** Comme dans les exercices 1 et 2, **l'étendue ne suit pas la
commune**. Passez à une commune d'une autre île et les couches se rechargent
correctement, mais la vue reste sur Moroni jusqu'à ce que vous fassiez un
panoramique.

## Étape 8 : Ajouter le tableau de synthèse d'impact

1. Mettez le tableau de bord en mode édition, ajoutez un autre élément, ouvrez son
   menu à 3 points et sélectionnez **Edit**.

1. Réglez **Visualization Type** sur **Comores: Résumé d'Impact** (dans le groupe
   **UFFIS: Comores**).

1. Renseignez les mêmes arguments qu'à l'étape 6 : les quatre portes et la
   commune liées à leurs variables, et `cycle` réglé sur `sample`.

1. Sur l'onglet **Settings**, réglez **Background Color** sur `#ffffff` et
   ajoutez des bordures à gauche, à droite et en bas, pour qu'il rejoigne la bande
   des entrées de seuil au-dessus.

1. Enregistrez l'élément et faites-le glisser directement sous les entrées de
   seuil, à droite.

1. Enregistrez le tableau de bord.

La part indiquée dans la dernière colonne est rapportée aux personnes qui vivent
dans les bâtiments **de la commune**, telles que les compte son fichier de
récepteurs, et non à la population de l'île ou du pays. C'est l'autre raison pour
laquelle la commune doit parvenir au plugin sous forme d'argument plutôt que d'y
être figée. Le titre du tableau se termine par le cycle,
**(2024-04-27 00:00 UTC, ÉCHANTILLON)**, pour que personne ne prenne l'exemple
pour une prévision en direct.

![Le tableau de synthèse d'impact lié aux quatre seuils et à la commune](images/ex3-impact-summary.png)

**Capture :** les arguments du tableau de synthèse d'impact liés aux quatre
variables de seuil et à la commune, avec `cycle` réglé sur l'exemple.

## Étape 9 : Tester le câblage

Aux portes par défaut (0,8 pour les quatre), à Moroni, vous devriez voir 145
polygones d'aléa, un message de progression annonçant 1 339 éléments en danger
(bâtiments et routes), et ce tableau :

| Niveau | Bâtiments | Personnes |
| --- | --- | --- |
| Sévère | 29 | 29 |
| Élevé | 19 | 57 |
| Moyen | 241 | 828 |
| Faible | 961 | 3 468 |
| TOTAL en danger | 1 250 | 4 383 |

La ligne du total indique aussi 14,1 km de routes et 6,29 % de la population.

Changez un seuil. L'ombrage de l'aléa, les entités touchées et le tableau doivent
tous se recalculer ensemble, avec des messages de progression pendant que les
couches se reconstruisent.

Abaisser le **Seuil Faible** depuis 0,8 est la démonstration la plus claire : la
classe verte s'étend sur les terrains bas à mesure que des cellules inondées par
une minorité de membres seulement commencent à se qualifier.

Changez ensuite la **Commune**. Les trois éléments produits par les plugins se
rechargent sur les rasters et les récepteurs d'une autre commune, et le
pourcentage du tableau est mesuré par rapport à une autre population.

![Le tableau de bord avant l'abaissement d'un seuil](images/ex3-thresholds-before.png)

**Capture :** la vue avant l'abaissement du seuil Faible.

![Le tableau de bord après l'abaissement d'un seuil](images/ex3-thresholds-after.png)

**Capture :** la même vue après l'abaissement.

## Positions des éléments

La solution livrée, pour référence.

| Élément | `x` | `y` | `w` | `h` |
| --- | --- | --- | --- | --- |
| Carte | 0 | 0 | 99 | 41 |
| Fond de Carte (entrée variable) | 0 | 0 | 17 | 6 |
| Commune (entrée variable) | 18 | 0 | 16 | 6 |
| Seuil Faible (entrée variable) | 56 | 0 | 11 | 7 |
| Seuil Moyen (entrée variable) | 67 | 0 | 12 | 7 |
| Seuil Élevé (entrée variable) | 79 | 0 | 11 | 7 |
| Seuil Sévère (entrée variable) | 90 | 0 | 10 | 7 |
| Résumé d'Impact (tableau) | 56 | 7 | 44 | 21 |

## Point de contrôle

Vous devriez maintenant avoir :

- Une carte occupant toute la fenêtre, avec sept couches dans le contrôle des
  couches (quatre rasters, deux couches calculées, et le fond de carte).
- Les quatre rasters de probabilité désactivés au chargement, présents pour la
  comparaison.
- Quatre entrées de seuil libellées en haut, et un sélecteur de commune en haut à
  gauche.
- Le déplacement de n'importe quel seuil mettant à jour la couche d'aléa, la
  couche d'impact et le tableau.
- Le changement de commune rechargeant les trois sur des données différentes.
- Des messages de progression pendant que les couches se recalculent.

## Points de discussion

- **Quatre portes sur quatre questions différentes.** « Sévère » signifie
  P(≥100 cm) ≥ 0,8 tandis qu'« Élevé » signifie P(≥70 cm) ≥ 0,8. Ce sont des
  questions différentes au même seuil : les noms de niveaux ne sont donc pas
  comparables entre eux et « sévère » ne veut rien dire tout seul. Régler les
  quatre portes à la même valeur, comme le fait la configuration par défaut, est
  la version la plus facile à expliquer : les niveaux ne diffèrent alors que par
  la profondeur.
- **Une classe inatteignable est un problème d'interface.** Pas ici, mais
  l'histoire du Guatemala vaut d'être racontée : là-bas, la porte Sévère peut être
  placée là où rien ne peut se qualifier, et l'interface n'en donne aucun indice.
  Demandez aux participants comment ils l'éviteraient : plafonner l'entrée ?
  afficher la plage de valeurs ? annoter la légende ?
- **Ce que la porte filtre réellement.** Un seuil de 0,8 garde les cellules qu'au
  moins 40 des 50 membres de la prévision ont atteintes à cette profondeur.
  Chaque probabilité est un compte sur 50, un multiple de 0,02 : elle est donc
  grossière et la classification change par sauts visibles plutôt que
  progressivement.
- **Vectoriser une classification.** Une couche cartographique ne peut que pointer
  vers une URL, et rien ne sert de raster calculé : le plugin vectorise donc la
  grille classée : les cellules adjacentes de même classe fusionnent en un seul
  polygone, environ 145 pour Moroni aux portes par défaut. Normal et NoData sont
  écartés (soit l'essentiel de la grille) parce qu'un fond de carte montre mieux
  le terrain non touché qu'une couche colorée.
- **La commune est un argument, pas une constante.** Le Guatemala et
  Antigua-et-Barbuda ont chacun un seul domaine, leurs plugins le codent donc en
  dur. Les Comores en ont 55 : la commune voyage donc avec les seuils dans chacun
  des trois plugins. C'est aussi ce qui décide du dénominateur de la dernière
  colonne du tableau.
- **Le cycle est aussi un argument.** Ici, il est fixé à `sample` pour que
  l'exercice ait toujours une inondation à montrer. Liez-le plutôt à `${Date}`,
  la liste de cycles de l'exercice 2, et les trois plugins suivent les données en
  direct ; pour un cycle en direct, les quatre couches raster devraient alors
  pointer vers `https://tito.uffis.org/outputs/comoros/${Date}/...` pour rester
  synchronisées.

## Suite

Les trois exercices couvrent ensemble les produits raster, la profondeur
probable sur les bâtiments et les routes, et la classification. Les notebooks
associés, dans `notebooks/Comoros/`, dérivent la même analyse en Python simple,
et la section 6 du notebook de l'exercice 3 détaille comment ces plugins sont
assemblés. Les notebooks utilisent encore les anciens fichiers de formation :
leurs chiffres peuvent donc différer de ceux des tableaux de bord.
