"""Every user-facing string, in English, Spanish and French.

Each country's plugins speak that country's language (`Country.lang`). Keeping
the text in one table is what stops the languages drifting: a new string has to
be added to every dictionary or `check_parity()` fails, and nothing that
computes a number lives here.

Hazard levels and depth bands are keyed by their numeric class value, which is
what the raster and the feature attributes actually carry, so a translation can
never change a classification.
"""

import itertools

LANGUAGES = ("en", "es", "fr")

STRINGS = {
    "en": {
        "language": "English",
        # Hazard levels, keyed by the `peligro` class value.
        "levels": {1: "Low", 2: "Medium", 3: "High", 4: "Severe"},
        # Feature attribute names the plugins emit and their own style rules key
        # on. These reach the viewer -- they are the column headers in the
        # attribute popup -- so they are translated like any other string. They
        # are also a published interface: a dashboard stores the field name in
        # its style rules, so changing one means re-fetching plugin defaults on
        # every dashboard already using it.
        "attr_hazard": "hazard",
        "attr_level": "level",
        "attr_band": "band",
        "attr_depth": "depth_m",
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
        "storm_summary_title": "Impact by depth, storm {index}",
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
        # Live TITO cycles.
        "cycle_latest": "Latest cycle",
        "cycle_training": "Training data",
        "cycle_sample": "Sample event",
        "sample_tag": "SAMPLE",
        "variants": {
            "combined_overbank": "Combined (overbank)",
            "combined": "Combined",
            "pluvial_overbank": "Pluvial (overbank)",
            "pluvial": "Pluvial",
            "fluvial_overbank": "Fluvial (overbank)",
            "fluvial": "Fluvial",
        },
        "msg_not_triggered": "{site}: no flood mapping triggered in the {cycle} cycle",
        "msg_no_receptors": "{site}: no buildings or roads published in the {cycle} cycle",
        "msg_no_training": "There is no training data for this plugin; choose a cycle",
        "discharge_label": "River Discharge Forecast",
        "discharge_desc": (
            "Forecast discharge at a river gauge for one TITO cycle: the range "
            "and median of each rainfall forcing's members."
        ),
        "discharge_tags": ["flood", "discharge", "hydrograph", "forecast", "plotly", "english"],
        "discharge_title": "Discharge forecast: {gauge}",
        "axis_discharge": "Discharge (m³/s)",
        "axis_time": "Time (UTC)",
        # The cycle dropdown.
        "cycle_times_label": "Available Cycles",
        "cycle_times_desc": (
            "Every hourly TITO cycle still published, newest first, then any "
            "sample cycles. Bind other plugins' cycle to ${Date}."
        ),
        "cycle_times_tags": ["tito", "cycle", "date", "forecast", "english"],
        "start_latest": "Latest live cycle",
        "start_sample": "Newest sample cycle",
        # Ensemble rainfall accumulation from a TITO cycle.
        "precip_layer_label": "Rainfall Accumulation",
        "precip_layer_desc": (
            "Ensemble rainfall accumulation from one TITO cycle. Bind the cycle "
            "to an Available Cycles input, or leave it at the latest."
        ),
        "precip_layer_tags": ["rainfall", "forecast", "raster", "map_layer", "dynamic", "english"],
        "precip_layer_name": "Rainfall accumulation",
        "precip_legend": "Rainfall accumulation (mm)",
        "or_more": "{value} or more",
        "rain_statistics": {"median": "Median", "min": "Minimum", "max": "Maximum"},
        "rain_periods": {"forecast": "Forecast", "nowcast": "Nowcast"},
        "rain_grid_kinds": {"national": "national", "flood_sites": "flood sites"},
        "msg_no_summary": "The {cycle} cycle published no {period} {statistic} {product} on {grid}",
        "soil_layer_label": "Soil Saturation",
        "soil_layer_desc": (
            "Ensemble maximum soil saturation from one TITO cycle. Bind the cycle "
            "to an Available Cycles input, or leave it at the latest."
        ),
        "soil_layer_tags": ["soil moisture", "forecast", "raster", "map_layer", "dynamic", "english"],
        "soil_layer_name": "Soil saturation",
        "soil_legend": "Soil saturation (%)",
        "unitq_layer_label": "Max Unit Streamflow",
        "unitq_layer_desc": (
            "Ensemble maximum unit streamflow (discharge per km² of catchment) "
            "from one TITO cycle. Bind the cycle to an Available Cycles input, "
            "or leave it at the latest."
        ),
        "unitq_layer_tags": ["streamflow", "forecast", "raster", "map_layer", "dynamic", "english"],
        "unitq_layer_name": "Max unit streamflow",
        "unitq_legend": "Max unit streamflow (m³/s per km²)",
        "summary_products": {"qpeaccum": "rainfall", "maxsm": "soil saturation", "maxunitq": "unit streamflow"},
        # Flood probability rasters, as TITO publishes them.
        "flood_map_layer_label": "Flood Probability Layer",
        "flood_map_layer_desc": (
            "TITO's probability of flood depth reaching a threshold, for one "
            "cycle, as a raster. Cells under the minimum probability are hidden."
        ),
        "flood_map_layer_tags": ["flood", "probability", "raster", "map_layer", "dynamic", "english"],
        "flood_map_layer_name": "Flood probability",
        "flood_map_legend": "Flood probability",
        "depth_choices": {"10cm": "≥ 10 cm", "30cm": "≥ 30 cm", "70cm": "≥ 70 cm", "100cm": "≥ 100 cm"},
        # SFFS/FGS flood risk matrix (Speight et al., 2018), from live cycles.
        "risk_levels": {0: "VERY LOW", 1: "LOW", 2: "MEDIUM", 3: "HIGH"},
        "severity_levels": {0: "Minimal", 1: "Minor", 2: "Significant", 3: "Severe"},
        "likelihood_levels": {0: "Very Low", 1: "Low", 2: "Medium", 3: "High"},
        "risk_filter_choices": {0: "All", 1: "Yellow and up", 2: "Amber and up", 3: "Red only"},
        "attr_risk": "warning",
        "attr_risk_level": "warning_level",
        "risk_matrix_label": "Flood Risk Matrix",
        "risk_matrix_desc": (
            "The SFFS and FGS flood risk matrix: likelihood against impact "
            "severity, with the cycle's overall warning."
        ),
        "risk_matrix_tags": ["flood", "risk", "matrix", "warning", "IBF", "english"],
        "risk_matrix_title": "Flood risk matrix (SFFS and FGS standard)",
        "axis_likelihood": "Likelihood",
        "axis_severity": "Impact severity",
        "overall_warning": "Overall warning",
        "depth_filter_label": "Flood Probability",
        "depth_filter_desc": "Chooses the flood depth whose probability a layer shows.",
        "depth_filter_tags": ["flood", "probability", "depth", "filter", "english"],
        "depth_filter_variable": "Flood probability",
        "depth_filter_choices": {
            "10cm": "Low (10 cm)", "30cm": "Medium (30 cm)",
            "70cm": "High (70 cm)", "100cm": "Severe (100 cm)",
        },
        "risk_filter_label": "Risk Level Filter",
        "risk_filter_desc": "Shows buildings and roads at or above a warning level.",
        "risk_filter_tags": ["flood", "risk", "warning", "filter", "english"],
        "risk_filter_variable": "Risk level",
        "risk_layer_label": "Features by Warning Level",
        "risk_layer_desc": (
            "Buildings and roads coloured by their SFFS/FGS warning level for "
            "one TITO cycle, filtered by a minimum level."
        ),
        "risk_layer_tags": ["flood", "risk", "warning", "map_layer", "dynamic", "english"],
        "risk_layer_name": "Buildings and roads by warning level",
        "risk_legend": "Warning level",
        "event_summary_label": "Event Summary",
        "event_summary_desc": (
            "Buildings, road km and districts at each SFFS/FGS warning level for "
            "one TITO cycle."
        ),
        "event_summary_tags": ["flood", "risk", "warning", "summary", "IBF", "english"],
        "event_summary_title": "Event summary",
        "col_warning": "Warning level",
        "col_road_km": "Road km",
        "col_districts": "Districts",
        "population_yellow": "Population in buildings at yellow (LOW) or worse",
        # Live depth-likelihood view of the storm family.
        "likely_bands": {
            1: "0.1 - 0.3 m",
            2: "0.3 - 0.7 m",
            3: "0.7 - 1 m",
            4: "1 m or more",
        },
        "likely_summary_title": "Likely flood depth, probability ≥ {p:.0%}",
        "likely_layer_name": "Likely flood depth on buildings and roads",
        "likely_legend": "Likely depth (P ≥ {p:.0%})",
        "likely_card_desc": (
            "Live forecast at a glance for one TITO cycle: trigger status, "
            "forecast rainfall, area likely to flood and expected people and "
            "buildings with at least 0.3 m of water."
        ),
        "likely_summary_desc": (
            "People, buildings and roads by the flood depth they reach with at "
            "least the chosen probability, from one TITO cycle."
        ),
        "likely_layer_desc": (
            "Buildings and roads coloured by the flood depth they reach with at "
            "least the chosen probability, from one TITO cycle."
        ),
        "card_status": "Forecast",
        "status_triggered": "Flood mapping triggered",
        "status_quiet": "Quiet: not triggered",
        "card_rain": "Forecast rainfall (median / max member)",
        "card_likely_area": "Area flooded ≥ 0.1 m (P ≥ {p:.0%})",
        "card_expected_people": "Expected people with ≥ 0.3 m",
        "card_expected_buildings": "Expected buildings with ≥ 0.3 m",
        "forcings": {
            "stream_sat": "Satellite rainfall (STREAM-SAT)",
            "scampr": "Nowcast (SCaMPR)",
            "stormlab": "Forecast (StormLab)",
        },
        "members": "{n} members",
        "median_peaks": "Median peaks",
        "peak_at": "{value:.1f} m³/s at {time}",
        "observed": "Observed",
        "msg_no_gauge": "{gauge}: no forecast published in the {cycle} cycle",
        # Search tags, one list per plugin family.
        "hazard_layer_tags": [
            "flood", "hazard", "EF5", "map_layer", "dynamic", "english"
        ],
        "hazard_summary_tags": ["flood", "impact", "IBF", "exposure", "table", "english"],
        "impact_layer_tags": ["flood", "impact", "IBF", "map_layer", "dynamic", "english"],
        "storm_summary_tags": ["flood", "impact", "zarr", "storm", "table", "english"],
        "storm_layer_tags": ["flood", "impact", "zarr", "storm", "map_layer", "dynamic", "english"],
        "storm_card_tags": ["flood", "zarr", "storm", "card", "english"],
    },
    "es": {
        "language": "Español",
        "levels": {1: "Bajo", 2: "Medio", 3: "Alto", 4: "Severo"},
        # Feature attribute names the plugins emit and their own style rules key
        # on. These reach the viewer -- they are the column headers in the
        # attribute popup -- so they are translated like any other string. They
        # are also a published interface: a dashboard stores the field name in
        # its style rules, so changing one means re-fetching plugin defaults on
        # every dashboard already using it.
        "attr_hazard": "peligro",
        "attr_level": "nivel",
        "attr_band": "banda",
        "attr_depth": "profundidad_m",
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
        "storm_summary_title": "Impacto por profundidad, tormenta {index}",
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
        "cycle_latest": "Último ciclo",
        "cycle_training": "Datos de capacitación",
        "cycle_sample": "Evento de muestra",
        "sample_tag": "MUESTRA",
        "variants": {
            "combined_overbank": "Combinada (desborde)",
            "combined": "Combinada",
            "pluvial_overbank": "Pluvial (desborde)",
            "pluvial": "Pluvial",
            "fluvial_overbank": "Fluvial (desborde)",
            "fluvial": "Fluvial",
        },
        "msg_not_triggered": "{site}: no se activó el mapeo de inundaciones en el ciclo {cycle}",
        "msg_no_receptors": "{site}: no se publicaron edificios ni carreteras en el ciclo {cycle}",
        "msg_no_training": "No hay datos de capacitación para este complemento; elija un ciclo",
        "discharge_label": "Pronóstico de Caudal",
        "discharge_desc": (
            "Caudal pronosticado en una estación para un ciclo de TITO: el rango "
            "y la mediana de los miembros de cada forzante de lluvia."
        ),
        "discharge_tags": ["inundación", "caudal", "hidrograma", "pronóstico", "plotly", "español"],
        "discharge_title": "Pronóstico de caudal: {gauge}",
        "axis_discharge": "Caudal (m³/s)",
        "axis_time": "Hora (UTC)",
        "cycle_times_label": "Ciclos Disponibles",
        "cycle_times_desc": (
            "Cada ciclo horario de TITO aún publicado, del más reciente al más "
            "antiguo, y luego los ciclos de muestra. Vincule el ciclo de los "
            "demás complementos a ${Date}."
        ),
        "cycle_times_tags": ["tito", "ciclo", "fecha", "pronóstico", "español"],
        "start_latest": "Último ciclo en vivo",
        "start_sample": "Ciclo de muestra más reciente",
        "precip_layer_label": "Lluvia Acumulada",
        "precip_layer_desc": (
            "Lluvia acumulada del conjunto para un ciclo de TITO. Vincule el "
            "ciclo a una entrada de Ciclos Disponibles o deje el más reciente."
        ),
        "precip_layer_tags": ["lluvia", "pronóstico", "ráster", "map_layer", "dinámico", "español"],
        "precip_layer_name": "Lluvia acumulada",
        "precip_legend": "Lluvia acumulada (mm)",
        "or_more": "{value} o más",
        "rain_statistics": {"median": "Mediana", "min": "Mínimo", "max": "Máximo"},
        "rain_periods": {"forecast": "Pronóstico", "nowcast": "Pronóstico inmediato"},
        "rain_grid_kinds": {"national": "nacional", "flood_sites": "sitios de inundación"},
        "msg_no_summary": "El ciclo {cycle} no publicó datos de {product} ({period}, {statistic}) en {grid}",
        "soil_layer_label": "Humedad de Suelo",
        "soil_layer_desc": (
            "Humedad máxima de suelo del conjunto para un ciclo de TITO. "
            "Vincule el ciclo a una entrada de Ciclos Disponibles o deje el más "
            "reciente."
        ),
        "soil_layer_tags": ["humedad del suelo", "pronóstico", "ráster", "map_layer", "dinámico", "español"],
        "soil_layer_name": "Humedad de suelo",
        "soil_legend": "Humedad de suelo (%)",
        "unitq_layer_label": "Caudal Unitario Máximo",
        "unitq_layer_desc": (
            "Caudal unitario máximo del conjunto (caudal por km² de cuenca) para "
            "un ciclo de TITO. Vincule el ciclo a una entrada de Ciclos "
            "Disponibles o deje el más reciente."
        ),
        "unitq_layer_tags": ["caudal", "pronóstico", "ráster", "map_layer", "dinámico", "español"],
        "unitq_layer_name": "Caudal unitario máximo",
        "unitq_legend": "Caudal unitario máximo (m³/s por km²)",
        "summary_products": {"qpeaccum": "lluvia", "maxsm": "humedad de suelo", "maxunitq": "caudal unitario"},
        "flood_map_layer_label": "Capa de Probabilidad de Inundación",
        "flood_map_layer_desc": (
            "La probabilidad de que la profundidad de inundación alcance un "
            "umbral, según TITO, para un ciclo, como ráster. Se ocultan las "
            "celdas bajo la probabilidad mínima."
        ),
        "flood_map_layer_tags": ["inundación", "probabilidad", "ráster", "map_layer", "dinámico", "español"],
        "flood_map_layer_name": "Probabilidad de inundación",
        "flood_map_legend": "Probabilidad de inundación",
        "depth_choices": {"10cm": "≥ 10 cm", "30cm": "≥ 30 cm", "70cm": "≥ 70 cm", "100cm": "≥ 100 cm"},
        "risk_levels": {0: "MUY BAJO", 1: "BAJO", 2: "MEDIO", 3: "ALTO"},
        "severity_levels": {0: "Mínima", 1: "Menor", 2: "Significativa", 3: "Severa"},
        "likelihood_levels": {0: "Muy baja", 1: "Baja", 2: "Media", 3: "Alta"},
        "risk_filter_choices": {0: "Todos", 1: "Amarillo o más", 2: "Ámbar o más", 3: "Solo rojo"},
        "attr_risk": "alerta",
        "attr_risk_level": "nivel_alerta",
        "risk_matrix_label": "Matriz de Riesgo de Inundación",
        "risk_matrix_desc": (
            "La matriz de riesgo de inundación SFFS y FGS: probabilidad frente a "
            "severidad del impacto, con la alerta general del ciclo."
        ),
        "risk_matrix_tags": ["inundación", "riesgo", "matriz", "alerta", "IBF", "español"],
        "risk_matrix_title": "Matriz de riesgo de inundación (estándar SFFS y FGS)",
        "axis_likelihood": "Probabilidad",
        "axis_severity": "Severidad del impacto",
        "overall_warning": "Alerta general",
        "depth_filter_label": "Probabilidad de Inundación",
        "depth_filter_desc": "Elige la profundidad de inundación cuya probabilidad muestra una capa.",
        "depth_filter_tags": ["inundación", "probabilidad", "profundidad", "filtro", "español"],
        "depth_filter_variable": "Probabilidad de inundación",
        "depth_filter_choices": {
            "10cm": "Mínima (10 cm)", "30cm": "Menor (30 cm)",
            "70cm": "Significativa (70 cm)", "100cm": "Severa (100 cm)",
        },
        "risk_filter_label": "Filtro de Nivel de Riesgo",
        "risk_filter_desc": "Muestra edificios y carreteras con un nivel de alerta igual o superior.",
        "risk_filter_tags": ["inundación", "riesgo", "alerta", "filtro", "español"],
        "risk_filter_variable": "Nivel de riesgo",
        "risk_layer_label": "Elementos por Nivel de Alerta",
        "risk_layer_desc": (
            "Edificios y carreteras coloreados según su nivel de alerta SFFS/FGS "
            "para un ciclo de TITO, filtrados por un nivel mínimo."
        ),
        "risk_layer_tags": ["inundación", "riesgo", "alerta", "map_layer", "dinámico", "español"],
        "risk_layer_name": "Edificios y carreteras por nivel de alerta",
        "risk_legend": "Nivel de alerta",
        "event_summary_label": "Resumen del Evento",
        "event_summary_desc": (
            "Edificios, km de carretera y distritos en cada nivel de alerta "
            "SFFS/FGS para un ciclo de TITO."
        ),
        "event_summary_tags": ["inundación", "riesgo", "alerta", "resumen", "IBF", "español"],
        "event_summary_title": "Resumen del evento",
        "col_warning": "Nivel de alerta",
        "col_road_km": "Km de carretera",
        "col_districts": "Distritos",
        "population_yellow": "Población en edificios en amarillo (BAJO) o peor",
        "likely_bands": {
            1: "0.1 - 0.3 m",
            2: "0.3 - 0.7 m",
            3: "0.7 - 1 m",
            4: "1 m o más",
        },
        "likely_summary_title": "Profundidad probable, probabilidad ≥ {p:.0%}",
        "likely_layer_name": "Profundidad probable en edificios y carreteras",
        "likely_legend": "Profundidad probable (P ≥ {p:.0%})",
        "likely_card_desc": (
            "Resumen del pronóstico de un ciclo de TITO: activación, lluvia "
            "pronosticada, área probablemente inundada y personas y edificios "
            "esperados con al menos 0.3 m de agua."
        ),
        "likely_summary_desc": (
            "Personas, edificios y carreteras según la profundidad que alcanzan "
            "con al menos la probabilidad elegida, de un ciclo de TITO."
        ),
        "likely_layer_desc": (
            "Edificios y carreteras coloreados según la profundidad que alcanzan "
            "con al menos la probabilidad elegida, de un ciclo de TITO."
        ),
        "card_status": "Pronóstico",
        "status_triggered": "Mapeo de inundaciones activado",
        "status_quiet": "Sin activación",
        "card_rain": "Lluvia pronosticada (mediana / máx. miembro)",
        "card_likely_area": "Área inundada ≥ 0.1 m (P ≥ {p:.0%})",
        "card_expected_people": "Personas esperadas con ≥ 0.3 m",
        "card_expected_buildings": "Edificios esperados con ≥ 0.3 m",
        "forcings": {
            "stream_sat": "Lluvia satelital (STREAM-SAT)",
            "scampr": "Pronóstico inmediato (SCaMPR)",
            "stormlab": "Pronóstico (StormLab)",
        },
        "members": "{n} miembros",
        "median_peaks": "Picos de la mediana",
        "peak_at": "{value:.1f} m³/s a las {time}",
        "observed": "Observado",
        "msg_no_gauge": "{gauge}: no se publicó pronóstico en el ciclo {cycle}",
        "hazard_layer_tags": [
            "inundación", "peligro", "EF5", "map_layer", "dinámico", "español"
        ],
        "hazard_summary_tags": ["inundación", "impacto", "IBF", "exposición", "tabla", "español"],
        "impact_layer_tags": ["inundación", "impacto", "IBF", "map_layer", "dinámico", "español"],
        "storm_summary_tags": ["inundación", "impacto", "zarr", "tormenta", "tabla", "español"],
        "storm_layer_tags": ["inundación", "impacto", "zarr", "tormenta", "map_layer", "dinámico", "español"],
        "storm_card_tags": ["inundación", "zarr", "tormenta", "tarjeta", "español"],
    },
    "fr": {
        "language": "Français",
        "levels": {1: "Faible", 2: "Moyen", 3: "Élevé", 4: "Sévère"},
        # Feature attribute names the plugins emit and their own style rules key
        # on. These reach the viewer -- they are the column headers in the
        # attribute popup -- so they are translated like any other string. They
        # are also a published interface: a dashboard stores the field name in
        # its style rules, so changing one means re-fetching plugin defaults on
        # every dashboard already using it.
        "attr_hazard": "alea",
        "attr_level": "niveau",
        "attr_band": "bande",
        "attr_depth": "profondeur_m",
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
        "storm_summary_title": "Impact par profondeur, tempête {index}",
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
        "cycle_latest": "Dernier cycle",
        "cycle_training": "Données de formation",
        "cycle_sample": "Événement d'exemple",
        "sample_tag": "ÉCHANTILLON",
        "variants": {
            "combined_overbank": "Combinée (débordement)",
            "combined": "Combinée",
            "pluvial_overbank": "Pluviale (débordement)",
            "pluvial": "Pluviale",
            "fluvial_overbank": "Fluviale (débordement)",
            "fluvial": "Fluviale",
        },
        "msg_not_triggered": "{site} : aucune cartographie d'inondation déclenchée au cycle {cycle}",
        "msg_no_receptors": "{site} : aucun bâtiment ni route publié au cycle {cycle}",
        "msg_no_training": "Aucune donnée de formation pour ce module ; choisissez un cycle",
        "discharge_label": "Prévision de Débit",
        "discharge_desc": (
            "Débit prévu à une station pour un cycle TITO : l'étendue et la "
            "médiane des membres de chaque forçage de pluie."
        ),
        "discharge_tags": ["inondation", "débit", "hydrogramme", "prévision", "plotly", "français"],
        "discharge_title": "Prévision de débit : {gauge}",
        "axis_discharge": "Débit (m³/s)",
        "axis_time": "Heure (UTC)",
        "cycle_times_label": "Cycles Disponibles",
        "cycle_times_desc": (
            "Chaque cycle horaire TITO encore publié, du plus récent au plus "
            "ancien, puis les cycles d'exemple. Liez le cycle des autres "
            "modules à ${Date}."
        ),
        "cycle_times_tags": ["tito", "cycle", "date", "prévision", "français"],
        "start_latest": "Dernier cycle en direct",
        "start_sample": "Cycle d'exemple le plus récent",
        "precip_layer_label": "Cumul de Pluie",
        "precip_layer_desc": (
            "Cumul de pluie de l'ensemble pour un cycle TITO. Liez le cycle à "
            "une entrée Cycles Disponibles, ou laissez le plus récent."
        ),
        "precip_layer_tags": ["pluie", "prévision", "raster", "map_layer", "dynamique", "français"],
        "precip_layer_name": "Cumul de pluie",
        "precip_legend": "Cumul de pluie (mm)",
        "or_more": "{value} ou plus",
        "rain_statistics": {"median": "Médiane", "min": "Minimum", "max": "Maximum"},
        "rain_periods": {"forecast": "Prévision", "nowcast": "Prévision immédiate"},
        "rain_grid_kinds": {"national": "national", "flood_sites": "sites d'inondation"},
        "msg_no_summary": ("Le cycle {cycle} n'a publié aucune donnée pour : "
                           "{product} ({period}, {statistic}) sur {grid}"),
        "soil_layer_label": "Humidité du Sol",
        "soil_layer_desc": (
            "Humidité maximale du sol de l'ensemble pour un cycle TITO. Liez le "
            "cycle à une entrée Cycles Disponibles, ou laissez le plus récent."
        ),
        "soil_layer_tags": ["humidité du sol", "prévision", "raster", "map_layer", "dynamique", "français"],
        "soil_layer_name": "Humidité du sol",
        "soil_legend": "Humidité du sol (%)",
        "unitq_layer_label": "Débit Unitaire Maximal",
        "unitq_layer_desc": (
            "Débit unitaire maximal de l'ensemble (débit par km² de bassin) pour "
            "un cycle TITO. Liez le cycle à une entrée Cycles Disponibles, ou "
            "laissez le plus récent."
        ),
        "unitq_layer_tags": ["débit", "prévision", "raster", "map_layer", "dynamique", "français"],
        "unitq_layer_name": "Débit unitaire maximal",
        "unitq_legend": "Débit unitaire maximal (m³/s par km²)",
        "summary_products": {"qpeaccum": "pluie", "maxsm": "humidité du sol", "maxunitq": "débit unitaire"},
        "flood_map_layer_label": "Couche de Probabilité d'Inondation",
        "flood_map_layer_desc": (
            "La probabilité que la profondeur d'inondation atteigne un seuil, "
            "selon TITO, pour un cycle, sous forme de raster. Les cellules sous "
            "la probabilité minimale sont masquées."
        ),
        "flood_map_layer_tags": ["inondation", "probabilité", "raster", "map_layer", "dynamique", "français"],
        "flood_map_layer_name": "Probabilité d'inondation",
        "flood_map_legend": "Probabilité d'inondation",
        "depth_choices": {"10cm": "≥ 10 cm", "30cm": "≥ 30 cm", "70cm": "≥ 70 cm", "100cm": "≥ 100 cm"},
        "risk_levels": {0: "TRÈS FAIBLE", 1: "FAIBLE", 2: "MOYEN", 3: "ÉLEVÉ"},
        "severity_levels": {0: "Minimale", 1: "Mineure", 2: "Significative", 3: "Sévère"},
        "likelihood_levels": {0: "Très faible", 1: "Faible", 2: "Moyenne", 3: "Élevée"},
        "risk_filter_choices": {0: "Tous", 1: "Jaune et plus", 2: "Orange et plus", 3: "Rouge seulement"},
        "attr_risk": "alerte",
        "attr_risk_level": "niveau_alerte",
        "risk_matrix_label": "Matrice de Risque d'Inondation",
        "risk_matrix_desc": (
            "La matrice de risque d'inondation SFFS et FGS : probabilité contre "
            "sévérité de l'impact, avec l'alerte globale du cycle."
        ),
        "risk_matrix_tags": ["inondation", "risque", "matrice", "alerte", "IBF", "français"],
        "risk_matrix_title": "Matrice de risque d'inondation (norme SFFS et FGS)",
        "axis_likelihood": "Probabilité",
        "axis_severity": "Sévérité de l'impact",
        "overall_warning": "Alerte globale",
        "depth_filter_label": "Probabilité d'Inondation",
        "depth_filter_desc": "Choisit la profondeur d'inondation dont une couche montre la probabilité.",
        "depth_filter_tags": ["inondation", "probabilité", "profondeur", "filtre", "français"],
        "depth_filter_variable": "Probabilité d'inondation",
        "depth_filter_choices": {
            "10cm": "Faible (10 cm)", "30cm": "Moyen (30 cm)",
            "70cm": "Élevé (70 cm)", "100cm": "Sévère (100 cm)",
        },
        "risk_filter_label": "Filtre de Niveau de Risque",
        "risk_filter_desc": "Affiche les bâtiments et routes à partir d'un niveau d'alerte.",
        "risk_filter_tags": ["inondation", "risque", "alerte", "filtre", "français"],
        "risk_filter_variable": "Niveau de risque",
        "risk_layer_label": "Éléments par Niveau d'Alerte",
        "risk_layer_desc": (
            "Bâtiments et routes colorés selon leur niveau d'alerte SFFS/FGS pour "
            "un cycle TITO, filtrés par un niveau minimal."
        ),
        "risk_layer_tags": ["inondation", "risque", "alerte", "map_layer", "dynamique", "français"],
        "risk_layer_name": "Bâtiments et routes par niveau d'alerte",
        "risk_legend": "Niveau d'alerte",
        "event_summary_label": "Résumé de l'Événement",
        "event_summary_desc": (
            "Bâtiments, km de routes et districts à chaque niveau d'alerte "
            "SFFS/FGS pour un cycle TITO."
        ),
        "event_summary_tags": ["inondation", "risque", "alerte", "résumé", "IBF", "français"],
        "event_summary_title": "Résumé de l'événement",
        "col_warning": "Niveau d'alerte",
        "col_road_km": "Km de routes",
        "col_districts": "Districts",
        "population_yellow": "Population des bâtiments en jaune (FAIBLE) ou pire",
        "likely_bands": {
            1: "0.1 - 0.3 m",
            2: "0.3 - 0.7 m",
            3: "0.7 - 1 m",
            4: "1 m ou plus",
        },
        "likely_summary_title": "Profondeur probable, probabilité ≥ {p:.0%}",
        "likely_layer_name": "Profondeur probable sur les bâtiments et routes",
        "likely_legend": "Profondeur probable (P ≥ {p:.0%})",
        "likely_card_desc": (
            "La prévision d'un cycle TITO en un coup d'œil : déclenchement, "
            "pluie prévue, superficie probablement inondée et personnes et "
            "bâtiments attendus avec au moins 0.3 m d'eau."
        ),
        "likely_summary_desc": (
            "Personnes, bâtiments et routes selon la profondeur atteinte avec "
            "au moins la probabilité choisie, pour un cycle TITO."
        ),
        "likely_layer_desc": (
            "Bâtiments et routes colorés selon la profondeur atteinte avec au "
            "moins la probabilité choisie, pour un cycle TITO."
        ),
        "card_status": "Prévision",
        "status_triggered": "Cartographie des inondations déclenchée",
        "status_quiet": "Calme : non déclenchée",
        "card_rain": "Pluie prévue (médiane / membre max.)",
        "card_likely_area": "Superficie inondée ≥ 0.1 m (P ≥ {p:.0%})",
        "card_expected_people": "Personnes attendues avec ≥ 0.3 m",
        "card_expected_buildings": "Bâtiments attendus avec ≥ 0.3 m",
        "forcings": {
            "stream_sat": "Pluie satellitaire (STREAM-SAT)",
            "scampr": "Prévision immédiate (SCaMPR)",
            "stormlab": "Prévision (StormLab)",
        },
        "members": "{n} membres",
        "median_peaks": "Pics de la médiane",
        "peak_at": "{value:.1f} m³/s à {time}",
        "observed": "Observé",
        "msg_no_gauge": "{gauge} : aucune prévision publiée au cycle {cycle}",
        "hazard_layer_tags": [
            "inondation", "aléa", "EF5", "map_layer", "dynamique", "français"
        ],
        "hazard_summary_tags": ["inondation", "impact", "IBF", "exposition", "tableau", "français"],
        "impact_layer_tags": ["inondation", "impact", "IBF", "map_layer", "dynamique", "français"],
        "storm_summary_tags": ["inondation", "impact", "zarr", "tempête", "tableau", "français"],
        "storm_layer_tags": ["inondation", "impact", "zarr", "tempête", "map_layer", "dynamique", "français"],
        "storm_card_tags": ["inondation", "zarr", "tempête", "carte", "français"],
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


# Argument names for the live-data choices, one per language like the gates.
LIVE_ARGS = {
    "en": {"cycle": "cycle", "variant": "flood_source", "gauge": "gauge",
           "likelihood": "min_probability", "min_risk": "min_risk_level", "depth": "depth",
           "grid": "grid", "statistic": "statistic", "period": "period", "start": "start",
           "label_text": "label_text", "show_label": "show_label"},
    "es": {"cycle": "ciclo", "variant": "fuente_inundacion", "gauge": "estacion",
           "likelihood": "probabilidad_minima", "min_risk": "nivel_riesgo_minimo",
           "depth": "profundidad", "grid": "malla", "statistic": "estadistica",
           "period": "periodo", "start": "inicio", "label_text": "texto_etiqueta",
           "show_label": "mostrar_etiqueta"},
    "fr": {"cycle": "cycle", "variant": "source_inondation", "gauge": "station",
           "likelihood": "probabilite_minimale", "min_risk": "niveau_risque_minimal",
           "depth": "profondeur", "grid": "grille", "statistic": "statistique",
           "period": "periode", "start": "debut", "label_text": "texte_etiquette",
           "show_label": "afficher_etiquette"},
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
        for key in ("levels", "bands", "variants", "forcings", "likely_bands",
                    "risk_levels", "severity_levels", "likelihood_levels",
                    "risk_filter_choices", "depth_choices", "rain_statistics",
                    "rain_periods", "rain_grid_kinds", "summary_products",
                    "depth_filter_choices"):
            if set(STRINGS["en"][key]) != set(STRINGS[lang][key]):
                raise ValueError(f"{key} class values differ in {lang}")

    if set(LIVE_ARGS) != set(LANGUAGES):
        raise ValueError("LIVE_ARGS does not cover every language")
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
