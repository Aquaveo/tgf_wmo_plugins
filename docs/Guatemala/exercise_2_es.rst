.. Solución del ejercicio práctico 2 de Guatemala, español. La versión en inglés
.. está junto a este archivo como exercise_2_en.rst.

==============================================================
Ejercicio 2 — Impacto de una sola tormenta
==============================================================

Construcción de **Guatemala Práctica 2 (Español)**, paso a paso.

Recuerde que la interfaz está en inglés, así que los nombres
de botones y campos se dejan en inglés y en negrita.

.. contents:: En esta página
   :depth: 2
   :local:
   :backlinks: none


Qué va a construir
==================

Un mapa a la izquierda que muestra la profundidad de inundación de una tormenta y
los edificios y carreteras que esa tormenta inunda; a la derecha, una tabla y una
tarjeta que resumen esa misma tormenta. Un desplegable selecciona la tormenta y
todo se vuelve a calcular.

.. figure:: images/ex2-finished.png
   :alt: El tablero terminado del ejercicio 2
   :width: 100%

   **Captura:** el tablero terminado, con el desplegable de tormenta, el mapa, la
   tabla resumen y la tarjeta.

Ideas nuevas en este ejercicio: leer un corte de un almacén Zarr, una capa
vectorial cuyos elementos los produce un módulo en lugar de descargarse de una URL,
y una sola variable de entrada que controla cuatro cosas a la vez.

**Consejo** — ``notebooks/Guatemala/02_storm_impact_es.ipynb`` deriva en Python los números
que muestra este tablero: cómo se muestrea la profundidad sobre cada edificio y
carretera, y cómo se arma la tabla resumen. Vale la pena ejecutarlo primero si
quiere entender el análisis antes de armar la interfaz.


Paso 1 — Crear el tablero
=========================

#. Cree un tablero nuevo (vea
   `Crear un tablero <getting_started_es.rst#crear-un-tablero>`_) con:

   * **Name**: ``Guatemala Práctica 2 (Español)``
   * **Description**: ``Solución para el Ejercicio Práctico #2 de la OMM en Guatemala``

#. Busque su tablero en la página de inicio y haga doble clic para abrirlo. El
   tablero está vacío, así que la previsualización muestra un lienzo en blanco.

#. Abra **Dashboard Settings** en la esquina superior derecha y active
   **Unrestricted Grid Item Movement**. Guarde la configuración.

#. Salga de **Dashboard Settings** y haga clic en **Edit Dashboard**, en la
   esquina superior derecha, para entrar en modo de edición.


Paso 2 — Agregar el selector de tormenta
========================================

#. Verá un elemento que ya existe en el tablero. Haga clic en el menú de 3 puntos
   del elemento y seleccione **Edit**.

#. Ponga **Visualization Type** en **Variable Input** (en el grupo **Default**).

#. Complete:

   .. list-table::
      :header-rows: 1
      :widths: 32 68

      * - Argumento
        - Valor
      * - ``variable_name``
        - ``Tormenta``
      * - ``show_label``
        - ``True``
      * - ``variable_options_source``
        - ``Mapas de Inundación (Español): Resumen de Impacto por Tormenta (Español) - Index``

   Esa fuente de opciones se genera a partir de un argumento de un módulo ya
   existente, con la forma ``<grupo>: <etiqueta del módulo> - <Argumento>``.
   Elegirla significa "ofrece las mismas opciones que ofrece el argumento
   ``index`` del módulo Resumen de Impacto por Tormenta", de modo que el
   desplegable se llena desde el módulo y no puede desincronizarse de él.

#. En la pestaña **Settings**, ponga **Background Color** en ``#ffffff`` y agregue
   un borde solo en el lado derecho.

#. Elija un valor inicial para el desplegable desde la previsualización, en el lado
   derecho del editor. La solución entregada usa la primera opción, pero cualquier
   tormenta sirve.

#. Guarde el elemento haciendo clic en **Save**, en la esquina inferior derecha del
   editor del elemento.

#. Arrastre el elemento a la parte superior del tablero y cambie su tamaño según
   haga falta. Deje espacio a su izquierda para el selector de mapa base.

#. Guarde el tablero haciendo clic en **Save Changes**, en la esquina superior
   derecha del editor del tablero.

.. figure:: images/ex2-storm-input.png
   :alt: La configuración de la variable de entrada del selector de tormenta
   :width: 100%

   **Captura:** los argumentos de **Variable Input** del selector de tormenta, con
   la fuente de opciones derivada del módulo ya seleccionada.


Paso 3 — Agregar el selector de mapa base
=========================================

El mapa base es una variable de entrada, para que el usuario pueda cambiarlo sin
editar nada. Construya primero la variable y después apunte el mapa a ella.

#. Ponga el tablero en modo de edición haciendo clic en el botón
   **Edit Dashboard**, en la esquina superior derecha.

#. Agregue otro elemento haciendo clic en **Add Dashboard Item**, en la esquina
   superior derecha.

#. Haga clic en el menú de 3 puntos del elemento nuevo y seleccione **Edit**.

#. Ponga **Visualization Type** en **Variable Input** (en el grupo **Default**).

#. Complete:

   .. list-table::
      :header-rows: 1
      :widths: 32 68

      * - Argumento
        - Valor
      * - ``variable_name``
        - ``Mapa Base``
      * - ``show_label``
        - ``True``
      * - ``variable_options_source``
        - ``Base Map Layers``

   ``Base Map Layers`` es una fuente de opciones incorporada: llena el desplegable
   con los mapas base que ofrece la instancia, así que no hace falta enumerarlos.

#. En la pestaña **Settings**, ponga **Background Color** en ``#ffffff``. Sin eso,
   el desplegable flota sobre el mapa sin fondo y es difícil de leer.

#. Elija un valor inicial para el desplegable desde la previsualización, en el lado
   derecho del editor. La solución entregada usa ``World Light Gray Base``, pero
   cualquier mapa base sirve.

#. Guarde el elemento haciendo clic en **Save**, en la esquina inferior derecha del
   editor del elemento.

#. Arrastre el elemento a la esquina superior izquierda, sobre el mapa, y cambie su
   tamaño según haga falta.

#. Guarde el tablero haciendo clic en **Save Changes**, en la esquina superior
   derecha del editor del tablero.

   Ya tiene un selector de mapa base en el tablero, pero todavía no controla el
   mapa.

.. figure:: images/ex1-variable-input-basemap.png
   :alt: La configuración de la variable de entrada del mapa base
   :width: 100%

   **Captura:** los argumentos de **Variable Input** del selector de mapa base.


Paso 4 — Agregar el mapa con la capa Zarr de profundidad
========================================================

#. Ponga el tablero en modo de edición haciendo clic en el botón
   **Edit Dashboard**, en la esquina superior derecha.

#. Agregue otro elemento haciendo clic en **Add Dashboard Item**, en la esquina
   superior derecha.

#. Haga clic en el menú de 3 puntos del elemento nuevo y seleccione **Edit**.

#. Ponga **Visualization Type** en **Map** (en el grupo **Default**).

#. En el argumento **Base Map**, elija ``Mapa Base`` en la sección
   **Variable Inputs**, al final del desplegable. El valor pasa a ser
   ``${Mapa Base}``.

#. Junto a **Layers**, haga clic en **Add Layer**.

#. En la pestaña **Layer**, defina las siguientes propiedades:

   .. list-table::
      :header-rows: 1
      :widths: 24 76

      * - Campo
        - Valor
      * - ``name``
        - ``Profundidad de Inundación``

#. En la pestaña **Source**, ponga **Source Type** en **Zarr** y complete:

   .. list-table::
      :header-rows: 1
      :widths: 24 76

      * - Campo
        - Valor
      * - ``url``
        - ``https://cog-s3-test-401506828094-us-east-1-an.s3.us-east-1.amazonaws.com/floodmaps_test``
      * - ``variable``
        - ``depth``
      * - ``index``
        - ``${Tormenta}``

   El campo ``index`` es donde este ejercicio se vuelve interactivo. El almacén
   Zarr contiene las 198 tormentas en un solo arreglo, e ``index`` selecciona el
   corte. Vincularlo a ``${Tormenta}`` significa que cambiar el desplegable lee un
   corte distinto: sin capas duplicadas y sin archivos separados.

#. En la pestaña **Style**, deje el modo en **Continuous** y elija la rampa de un
   solo tono **Blues**. Deje **Min** y **Max** vacíos.

#. En la pestaña **Legend**, seleccione **Default Legend**. Para un ráster con
   rampa, la aplicación genera automáticamente una barra de color.

#. Guarde la capa haciendo clic en **Create**, al pie del editor de capas.

.. figure:: images/ex2-zarr-source.png
   :alt: La pestaña Source configurada para el almacén Zarr
   :width: 100%

   **Captura:** la pestaña **Source** con **Source Type** en Zarr, la URL del
   almacén, ``variable`` en depth e ``index`` en ``${Tormenta}``.


Paso 5 — Agregar la capa de impacto generada por el módulo
==========================================================

Los elementos de esta capa los calcula un módulo en cada solicitud. No hay una URL
de GeoJSON: el módulo muestrea la profundidad sobre cada edificio y carretera y
devuelve el resultado.

#. Junto a **Layers**, haga clic otra vez en **Add Layer**.

#. Vaya directamente a la pestaña **Source** y ponga **Source Type** en
   **Capa de Impacto por Tormenta (Español)**. Los módulos de capa dinámica
   aparecen en el mismo desplegable **Source Type** que GeoTIFF y Zarr, listados
   bajo el grupo de su módulo.

#. Aparecen los argumentos del módulo. Complete:

   .. list-table::
      :header-rows: 1
      :widths: 24 76

      * - Argumento
        - Valor
      * - ``index``
        - ``${Tormenta}``

#. Haga clic en **Fetch plugin defaults**.

   Este es el paso que ahorra más trabajo. El método ``run()`` del módulo devuelve
   un armazón ya hecho: el nombre de la capa, la vinculación de la fuente, un
   estilo basado en reglas sobre el atributo ``banda`` (la banda de profundidad) y
   una leyenda que corresponde. Después de la descarga debería ver la capa llamada
   **Edificios y carreteras inundados**, ocho reglas de estilo y una leyenda
   **Profundidad** de cuatro entradas, nada de lo cual tuvo que escribir. Escribir
   reglas de estilo vectorial a mano es propenso a errores: una regla con la forma
   equivocada nunca coincide, en silencio, y deja todos los elementos en gris.

#. Revise las pestañas **Style** y **Legend** para ver lo que llegó. Los colores
   van de verde → amarillo → rojo → morado en cuatro bandas de profundidad, con
   reglas separadas para polígonos (edificios) y líneas (carreteras), de modo que
   las carreteras reciben un trazo lo bastante ancho para verse.

#. Guarde la capa haciendo clic en **Create**, al pie del editor de capas.

#. En el argumento **Map Extent**, elija **Use a Custom Extent** e ingrese:

   .. code-block:: text

      -10078413.13,1629754.90,14.83

#. En la pestaña **Settings**, ponga **Background Color** en ``#ffffff`` y agregue
   un borde en los cuatro lados.

   Este mapa *no* ocupa toda la ventana: la comparte con la tabla y la tarjeta, así
   que deje **Fill Viewport** desactivado.

#. Guarde el elemento haciendo clic en **Save**, en la esquina inferior derecha del
   editor del mapa.

#. Cambie el tamaño del elemento del mapa para que ocupe la mitad izquierda de la
   ventana, arrastrando el controlador de su esquina inferior derecha.

#. Si el mapa está cubriendo el selector de tormenta y el de mapa base, haga clic
   en el menú de 3 puntos, pase el cursor sobre **Order** y seleccione
   **Send to Back**. Los selectores deberían quedar visibles sobre el mapa.

#. Guarde el tablero haciendo clic en **Save Changes**, en la esquina superior
   derecha del editor del tablero.

.. figure:: images/ex2-dynamic-layer-source.png
   :alt: La pestaña Source con un módulo de capa dinámica seleccionado
   :width: 100%

   **Captura:** la pestaña **Source** con **Capa de Impacto por Tormenta
   (Español)** seleccionada, ``index`` vinculado a ``${Tormenta}`` y el botón
   **Fetch plugin defaults**.

.. figure:: images/ex2-dynamic-layer-style.png
   :alt: La pestaña Style mostrando el estilo basado en reglas descargado
   :width: 100%

   **Captura:** la pestaña **Style** después de la descarga, mostrando las ocho
   reglas sobre el atributo ``banda``.


Paso 6 — Agregar la tabla resumen
=================================

#. Ponga el tablero en modo de edición haciendo clic en el botón
   **Edit Dashboard**, en la esquina superior derecha.

#. Agregue otro elemento haciendo clic en **Add Dashboard Item**, en la esquina
   superior derecha.

#. Haga clic en el menú de 3 puntos del elemento nuevo y seleccione **Edit**.

#. Ponga **Visualization Type** en **Resumen de Impacto por Tormenta (Español)**
   (en el grupo **Mapas de Inundación (Español)**).

#. Complete:

   .. list-table::
      :header-rows: 1
      :widths: 24 76

      * - Argumento
        - Valor
      * - ``index``
        - ``${Tormenta}``

   La tabla divide los elementos inundados por la tormenta en bandas de
   profundidad, de la más profunda a la menos profunda, con el número de edificios,
   la población, el área, la longitud de carretera y la proporción de la población
   del municipio afectada.

#. Guarde el elemento haciendo clic en **Save**, en la esquina inferior derecha del
   editor del elemento.

#. Arrastre el elemento a la derecha del mapa y cambie su tamaño según haga falta.

#. Guarde el tablero haciendo clic en **Save Changes**, en la esquina superior
   derecha del editor del tablero.


Paso 7 — Agregar la tarjeta de la tormenta
==========================================

#. Ponga el tablero en modo de edición, agregue otro elemento y abra su menú de
   3 puntos y seleccione **Edit**, igual que en el paso anterior.

#. Ponga **Visualization Type** en **Resumen de Tormenta (Español)** (en el grupo
   **Mapas de Inundación (Español)**).

#. Complete:

   .. list-table::
      :header-rows: 1
      :widths: 24 76

      * - Argumento
        - Valor
      * - ``index``
        - ``${Tormenta}``

   La tarjeta da las cifras principales —la tormenta, su magnitud, el área inundada
   y la población afectada— para quien no va a leer una tabla.

#. Guarde el elemento haciendo clic en **Save**, en la esquina inferior derecha del
   editor del elemento.

#. Arrastre el elemento debajo de la tabla resumen y cambie su tamaño según haga
   falta.

#. Guarde el tablero haciendo clic en **Save Changes**, en la esquina superior
   derecha del editor del tablero.

.. figure:: images/ex2-table-card.png
   :alt: La tabla resumen y la tarjeta de la tormenta
   :width: 100%

   **Captura:** la tabla resumen y la tarjeta para una tormenta.


Paso 8 — Probar las conexiones
==============================

Cambie el desplegable de tormenta. Los cuatro elementos deberían actualizarse: la
capa Zarr vuelve a leer su corte, la capa de impacto se vuelve a ejecutar y la
tabla y la tarjeta se vuelven a consultar. Aparecen mensajes de progreso mientras
la capa de impacto se recalcula.


Punto de control
================

A estas alturas debería tener:

* Un desplegable de tormenta etiquetado con magnitudes en milímetros, no con
  índices.
* Al cambiarlo se actualizan el ráster de profundidad, los edificios y carreteras
  coloreados, la tabla y la tarjeta: los cuatro.
* Un control de capas con tres capas (incluido el mapa base).
* La capa de impacto coloreada por banda de profundidad, con una leyenda
  **Profundidad**, y las carreteras visibles como líneas de color y no como hilos.


Puntos de discusión
===================

* **Una variable, cuatro consumidores.** ``${Tormenta}`` aparece en el índice de
  una fuente Zarr, en el argumento de una capa de módulo y en los argumentos de dos
  visualizaciones. Ninguno de los cuatro elementos sabe de los otros; todos
  simplemente declaran que dependen de un nombre.
* **Las capas dinámicas se vuelven a ejecutar; las estáticas se vuelven a
  consultar.** La capa Zarr vuelve a leer un corte de un arreglo que ya existe. La
  capa de impacto vuelve a ejecutar código de Python que muestrea un ráster sobre
  unas 5,000 geometrías. El mismo disparador, con costos muy distintos, y por eso
  el módulo informa su progreso mientras trabaja.
* **Etiquetas frente a valores.** El desplegable muestra la magnitud y el módulo
  recibe un índice. Presentar una etiqueta con significado en lugar de una clave
  opaca casi siempre justifica el paso intermedio.
* **Las magnitudes son valores de relleno.** Son ilustrativas, no medidas. Son
  únicas y monótonas, así que identifican una tormenta de forma confiable y se
  ordenan de manera sensata, pero no las presente como totales físicos de lluvia.
* **Por qué el módulo entrega un estilo.** La alternativa —escribir a mano ocho
  reglas en la interfaz— falla en silencio cuando una regla está mal formada.
  Entregar el estilo desde ``run()`` hace que la capa esté correcta desde la
  primera vez y siga estándolo si cambian las bandas.


Siguiente
=========

`Ejercicio 3 — Clasificación de peligro con umbrales ajustables
<exercise_3_es.rst>`_ pone los umbrales mismos en manos del usuario.
