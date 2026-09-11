"""Every user-facing string, in English, Spanish and French.

The plugins come in an `_en`, an `_es` and an `_fr` variant. Keeping the text in
one table rather than in parallel sets of modules is what stops the variants
drifting: a new string has to be added to every dictionary or `check_parity()`
fails, and nothing that computes a number lives here.

Hazard levels and depth bands are keyed by their numeric class value, which is
what the raster and the feature attributes actually carry, so a translation can
never change a classification.
"""

import itertools

LANGUAGES = ("en", "es", "fr")

STRINGS = {
    "en": {
        "language": "English",
        "group": "Flood Maps (English)",
        # Hazard levels, keyed by the `peligro` class value.
        "levels": {1: "Low", 2: "Medium", 3: "High", 4: "Severe"},
        # Depth bands, keyed by the `banda` class value.
        "bands": {
            1: "0.05 - 0.3 m",
            2: "0.3 - 1 m",
            3: "1 - 2 m",
            4: "2 m or more",
        },
        "buildings": "buildings",
        "roads": "roads",
        # Shared table columns.
        "col_level": "Level",
        "col_depth": "Depth",
        "col_buildings": "Buildings",
        "col_population": "Population",
        "col_area": "Area (m²)",
        "col_roads_km": "Roads (km)",
        "col_pop_share": "% of population",
        "row_total_hazard": "TOTAL at risk",
        "row_total_flooded": "TOTAL affected",
        "out_of_range": "Out of range",
        # Hazard (probability-gated) plugins.
        "hazard_summary_title": "Impact by hazard level",
        "hazard_summary_label": "Flood Impact Summary",
        "hazard_summary_desc": (
            "People, buildings and roads in each flood hazard level, "
            "classified from the same probability gates as the hazard map."
        ),
        "hazard_layer_name": "Hazard classification",
        "hazard_layer_label": "Flood Hazard Layer",
        "hazard_layer_desc": (
            "Flood hazard classification from four EF5 exceedance-probability "
            "rasters, as map polygons. Re-classifies when a gate changes."
        ),
        "hazard_legend": "Hazard",
        "impact_layer_name": "Buildings and roads at risk",
        "impact_layer_label": "Flood Impact Layer",
        "impact_layer_desc": (
            "Buildings and roads coloured by flood hazard level, using the "
            "same probability gates as the hazard map."
        ),
        # Storm (depth-sampled) plugins.
        "storm_summary_title": "Impact by depth — storm {index}",
        "storm_summary_label": "Storm Impact Summary",
        "storm_summary_desc": (
            "People, buildings and roads by flood depth for one storm of the "
            "ensemble. The bands are depths, so they read without reference "
            "to a threshold."
        ),
        "storm_layer_name": "Flooded buildings and roads",
        "storm_layer_label": "Storm Impact Layer",
        "storm_layer_desc": (
            "Buildings and roads coloured by how deep the water gets on them "
            "in one storm of the ensemble."
        ),
        "depth_legend": "Depth",
        "storm_card_label": "Storm Summary",
        "storm_card_desc": (
            "Magnitude, flooded area and depth for one storm of the ensemble."
        ),
        "card_magnitude": "Magnitude",
        "card_flooded_area": "Flooded area",
        "card_max_depth": "Max depth",
        "card_mean_depth": "Mean depth (wet)",
        "card_flooding": "Flooding",
        "card_no_flooding": "None at this magnitude",
        # Progress messages.
        "msg_reading": "Reading probability layers...",
        "msg_classifying": "Classifying hazard...",
        "msg_polygons": "Building polygons...",
        "msg_loading_features": "Loading buildings and roads...",
        "msg_sampling": "Sampling depth...",
        "msg_done": "Done",
        "msg_at_risk": "{count:,} elements at risk",
        "msg_flooded": "{count:,} elements flooded",
        # Search tags for the hazard layer; the plugin adds nothing else.
        "hazard_layer_tags": [
            "flood", "hazard", "EF5", "map_layer", "dynamic", "english"
        ],
    },
    "es": {
        "language": "Español",
        "group": "Mapas de Inundación (Español)",
        "levels": {1: "Bajo", 2: "Medio", 3: "Alto", 4: "Severo"},
        "bands": {
            1: "0.05 - 0.3 m",
            2: "0.3 - 1 m",
            3: "1 - 2 m",
            4: "2 m o más",
        },
        "buildings": "edificios",
        "roads": "carreteras",
        "col_level": "Nivel",
        "col_depth": "Profundidad",
        "col_buildings": "Edificios",
        "col_population": "Población",
        "col_area": "Área (m²)",
        "col_roads_km": "Carreteras (km)",
        "col_pop_share": "% de la población",
        "row_total_hazard": "TOTAL en peligro",
        "row_total_flooded": "TOTAL afectado",
        "out_of_range": "Fuera de rango",
        "hazard_summary_title": "Impacto por nivel de peligro",
        "hazard_summary_label": "Resumen de Impacto",
        "hazard_summary_desc": (
            "Personas, edificios y carreteras en cada nivel de peligro por "
            "inundación, clasificados con los mismos umbrales de probabilidad "
            "que el mapa de peligro."
        ),
        "hazard_layer_name": "Clasificación de peligro",
        "hazard_layer_label": "Capa de Peligro",
        "hazard_layer_desc": (
            "Clasificación de peligro por inundación a partir de cuatro "
            "rásteres de probabilidad de excedencia EF5, como polígonos. Se "
            "reclasifica cuando cambia un umbral."
        ),
        "hazard_legend": "Peligro",
        "impact_layer_name": "Edificios y carreteras en peligro",
        "impact_layer_label": "Capa de Impacto",
        "impact_layer_desc": (
            "Edificios y carreteras coloreados por nivel de peligro, usando "
            "los mismos umbrales de probabilidad que el mapa de peligro."
        ),
        "storm_summary_title": "Impacto por profundidad — tormenta {index}",
        "storm_summary_label": "Resumen de Impacto por Tormenta",
        "storm_summary_desc": (
            "Personas, edificios y carreteras por profundidad de inundación "
            "para una tormenta del conjunto. Las bandas son profundidades, "
            "así que se leen sin referencia a un umbral."
        ),
        "storm_layer_name": "Edificios y carreteras inundados",
        "storm_layer_label": "Capa de Impacto por Tormenta",
        "storm_layer_desc": (
            "Edificios y carreteras coloreados según la profundidad que "
            "alcanza el agua sobre ellos en una tormenta del conjunto."
        ),
        "depth_legend": "Profundidad",
        "storm_card_label": "Resumen de Tormenta",
        "storm_card_desc": (
            "Magnitud, área inundada y profundidad de una tormenta del conjunto."
        ),
        "card_magnitude": "Magnitud",
        "card_flooded_area": "Área inundada",
        "card_max_depth": "Profundidad máxima",
        "card_mean_depth": "Profundidad media (mojado)",
        "card_flooding": "Inundación",
        "card_no_flooding": "Ninguna con esta magnitud",
        "msg_reading": "Leyendo capas de probabilidad...",
        "msg_classifying": "Clasificando peligro...",
        "msg_polygons": "Generando polígonos...",
        "msg_loading_features": "Cargando edificios y carreteras...",
        "msg_sampling": "Muestreando profundidad...",
        "msg_done": "Listo",
        "msg_at_risk": "{count:,} elementos en peligro",
        "msg_flooded": "{count:,} elementos inundados",
        "hazard_layer_tags": [
            "inundación", "peligro", "EF5", "map_layer", "dinámico", "español"
        ],
    },
    "fr": {
        "language": "Français",
        "group": "Cartes d'Inondation (Français)",
        "levels": {1: "Faible", 2: "Moyen", 3: "Élevé", 4: "Sévère"},
        "bands": {
            1: "0.05 - 0.3 m",
            2: "0.3 - 1 m",
            3: "1 - 2 m",
            4: "2 m ou plus",
        },
        "buildings": "bâtiments",
        "roads": "routes",
        "col_level": "Niveau",
        "col_depth": "Profondeur",
        "col_buildings": "Bâtiments",
        "col_population": "Population",
        "col_area": "Superficie (m²)",
        "col_roads_km": "Routes (km)",
        "col_pop_share": "% de la population",
        "row_total_hazard": "TOTAL en danger",
        "row_total_flooded": "TOTAL affecté",
        "out_of_range": "Hors limites",
        "hazard_summary_title": "Impact par niveau d'aléa",
        "hazard_summary_label": "Résumé d'Impact",
        "hazard_summary_desc": (
            "Personnes, bâtiments et routes dans chaque niveau d'aléa "
            "d'inondation, classés selon les mêmes seuils de probabilité que "
            "la carte d'aléa."
        ),
        "hazard_layer_name": "Classification de l'aléa",
        "hazard_layer_label": "Couche d'Aléa",
        "hazard_layer_desc": (
            "Classification de l'aléa d'inondation à partir de quatre rasters "
            "de probabilité de dépassement EF5, sous forme de polygones. "
            "Reclassée lorsqu'un seuil change."
        ),
        "hazard_legend": "Aléa",
        "impact_layer_name": "Bâtiments et routes en danger",
        "impact_layer_label": "Couche d'Impact",
        "impact_layer_desc": (
            "Bâtiments et routes colorés par niveau d'aléa, selon les mêmes "
            "seuils de probabilité que la carte d'aléa."
        ),
        "storm_summary_title": "Impact par profondeur — tempête {index}",
        "storm_summary_label": "Résumé d'Impact par Tempête",
        "storm_summary_desc": (
            "Personnes, bâtiments et routes par profondeur d'inondation pour "
            "une tempête de l'ensemble. Les bandes sont des profondeurs, "
            "elles se lisent donc sans référence à un seuil."
        ),
        "storm_layer_name": "Bâtiments et routes inondés",
        "storm_layer_label": "Couche d'Impact par Tempête",
        "storm_layer_desc": (
            "Bâtiments et routes colorés selon la profondeur que l'eau "
            "atteint sur eux lors d'une tempête de l'ensemble."
        ),
        "depth_legend": "Profondeur",
        "storm_card_label": "Résumé de Tempête",
        "storm_card_desc": (
            "Magnitude, superficie inondée et profondeur d'une tempête de "
            "l'ensemble."
        ),
        "card_magnitude": "Magnitude",
        "card_flooded_area": "Superficie inondée",
        "card_max_depth": "Profondeur maximale",
        "card_mean_depth": "Profondeur moyenne (mouillé)",
        "card_flooding": "Inondation",
        "card_no_flooding": "Aucune à cette magnitude",
        "msg_reading": "Lecture des couches de probabilité...",
        "msg_classifying": "Classification de l'aléa...",
        "msg_polygons": "Génération des polygones...",
        "msg_loading_features": "Chargement des bâtiments et des routes...",
        "msg_sampling": "Échantillonnage de la profondeur...",
        "msg_done": "Terminé",
        "msg_at_risk": "{count:,} éléments en danger",
        "msg_flooded": "{count:,} éléments inondés",
        "hazard_layer_tags": [
            "inondation", "aléa", "EF5", "map_layer", "dynamique", "français"
        ],
    },
}


# Plugin argument names for the four probability gates, one per language.
#
# Each language variant exposes its arguments in its own language, so an English
# dashboard reads `low_threshold` and a Spanish one `umbral_bajo`. Keyed by the
# `peligro` class value, like `levels` and `bands` above, so the gates stay tied
# to the classification rather than to a spelling -- renaming an argument can
# never silently reorder them.
THRESHOLD_ARGS = {
    "en": {
        1: "low_threshold",
        2: "medium_threshold",
        3: "high_threshold",
        4: "severe_threshold",
    },
    "es": {
        1: "umbral_bajo",
        2: "umbral_medio",
        3: "umbral_alto",
        4: "umbral_severo",
    },
    "fr": {
        1: "seuil_faible",
        2: "seuil_moyen",
        3: "seuil_eleve",
        4: "seuil_severe",
    },
}


def threshold_args(lang):
    """The four gate arguments as a plugin `args` schema, in `lang`."""
    return {name: "number" for name in THRESHOLD_ARGS[lang].values()}


def check_parity():
    """Raise if the language dictionaries have drifted apart.

    Called at import so a missing translation is a hard failure at install time
    rather than a KeyError in front of a room of trainees. English is the
    reference every other language is compared against.
    """
    if set(STRINGS) != set(LANGUAGES):
        raise ValueError("STRINGS does not cover every language")

    en = set(STRINGS["en"])
    for lang in LANGUAGES:
        if lang == "en":
            continue
        other = set(STRINGS[lang])
        if en != other:
            raise ValueError(
                f"strings out of sync -- missing from {lang}: "
                f"{sorted(en - other)}, missing from en: {sorted(other - en)}"
            )
        for key in ("levels", "bands"):
            if set(STRINGS["en"][key]) != set(STRINGS[lang][key]):
                raise ValueError(f"{key} class values differ in {lang}")

    if set(THRESHOLD_ARGS) != set(LANGUAGES):
        raise ValueError("THRESHOLD_ARGS does not cover every language")
    values = [set(names) for names in THRESHOLD_ARGS.values()]
    if any(v != set(STRINGS["en"]["levels"]) for v in values):
        raise ValueError("THRESHOLD_ARGS class values differ from levels")
    # A name shared between languages would make one dashboard silently valid
    # against another language's plugin.
    for a, b in itertools.combinations(sorted(THRESHOLD_ARGS), 2):
        shared = set(THRESHOLD_ARGS[a].values()) & set(THRESHOLD_ARGS[b].values())
        if shared:
            raise ValueError(
                f"argument names shared between {a} and {b}: {sorted(shared)}"
            )


check_parity()
