.. Solución del ejercicio práctico 1 de Guatemala, español. La versión en inglés
.. está junto a este archivo como exercise_1_en.rst.

=================================================================
Ejercicio 1 — Un mapa de profundidad y probabilidad de inundación
=================================================================

Construcción de **Guatemala Práctica 1 (Español)**, paso a paso.

Recuerde que la interfaz está en inglés, así que los nombres de botones
y campos se dejan en inglés y en negrita.

.. contents:: En esta página
   :depth: 2
   :local:
   :backlinks: none


Qué va a construir
==================

Un mapa que ocupa toda la ventana, con cinco capas ráster —la profundidad de
inundación más cuatro probabilidades de excedencia— y un desplegable pequeño en la
esquina superior izquierda que cambia el mapa base que está debajo.

.. figure:: images/ex1-finished.png
   :alt: El tablero terminado del ejercicio 1
   :width: 100%

   **Captura:** el tablero terminado, con el control de capas abierto para que se
   vean las cinco capas.

Este ejercicio trata de las capas ráster: dónde va la URL, cómo se elige una rampa
de color y la diferencia entre dejar que la aplicación escale una capa o fijar la
escala usted mismo.


Paso 1 — Crear el tablero
=========================

#. Cree un tablero nuevo (vea
   `Crear un tablero <getting_started_es.rst#crear-un-tablero>`_) con:

   * **Name**: ``Guatemala Práctica 1 (Español)``
   * **Description**: ``Solución para el Ejercicio Práctico #1 de la OMM en Guatemala``

#. Busque su tablero en la página de inicio y haga doble clic para abrirlo. El
   tablero está vacío, así que la previsualización muestra un lienzo en blanco.

#. Abra **Dashboard Settings** en la esquina superior derecha y active
   **Unrestricted Grid Item Movement**. Guarde la configuración.

#. Salga de **Dashboard Settings** y haga clic en **Edit Dashboard**, en la
   esquina superior derecha, para entrar en modo de edición.


Paso 2 — Agregar el mapa
========================

#. Verá un elemento que ya existe en el tablero. Haga clic en el menú de 3 puntos
   del elemento y seleccione **Edit**.

#. Ponga **Visualization Type** en **Map** (en el grupo **Default**).

#. Aparecen cinco argumentos: **Base Map**, **Layer Control**, **Layers**,
   **Map Extent** y **Map Drawing**. Déjelos por ahora; los irá completando en los
   pasos siguientes.

#. En el argumento **Base Map**, elija ``World Light Gray Base`` por el momento.
   Más adelante lo cambiará para que sea dinámico.

.. figure:: images/ex1-map-args.png
   :alt: Los argumentos de la visualización Map en el visor de datos
   :width: 100%

   **Captura:** los cinco argumentos de la visualización **Map**, con un mapa base
   seleccionado por defecto.


Paso 3 — Agregar la capa de profundidad
=======================================

#. Junto a **Layers**, haga clic en **Add Layer**. El editor de capas se abre con
   las pestañas **Layer**, **Source**, **Style**, **Legend**,
   **Attributes/Table Popup** y **Custom Modal Popup**.

#. En la pestaña **Layer**, defina las siguientes propiedades:

   .. list-table::
      :header-rows: 1
      :widths: 24 76

      * - Campo
        - Valor
      * - ``name``
        - ``Profundidad (m)``
      * - ``opacity``
        - ``.5``

#. En la pestaña **Source**, ponga **Source Type** en **GeoTIFF** y complete:

   .. list-table::
      :header-rows: 1
      :widths: 24 76

      * - Campo
        - Valor
      * - ``url``
        - ``https://cog-s3-test-401506828094-us-east-1-an.s3.us-east-1.amazonaws.com/PBI_Actividad_2/depth_m.tif``
      * - ``mask_below``
        - ``0.01``

   ``mask_below`` oculta las celdas iguales o inferiores al valor indicado. En este
   ráster el suelo seco es 0, y sin una máscara todo el dominio se pintaría con el
   color bajo de la rampa en lugar de mostrar el mapa base.

#. En la pestaña **Style**, deje el modo en **Continuous** y elija la rampa
   **YlGnBu**. Deje **Min** y **Max** vacíos.

   Dejar ambos límites vacíos es una decisión deliberada, no descuido. Un límite
   vacío significa "resuélvelo a partir de las estadísticas del archivo al
   momento de dibujar", así que la rampa se extiende sobre el rango que tenga este
   ráster en particular: de 0 a unos 4.76 m en este caso. Si define ambos, se
   aplican los valores tal cual.

#. En la pestaña **Legend**, seleccione **Default Legend**. Para un ráster con
   rampa, la aplicación genera automáticamente una barra de color.

#. Guarde la capa haciendo clic en **Create**, al pie del editor de capas.

.. figure:: images/ex1-layer-source-geotiff.png
   :alt: La pestaña Source configurada para el GeoTIFF de profundidad
   :width: 100%

   **Captura:** la pestaña **Source** con **Source Type** en GeoTIFF, la URL de
   profundidad y ``mask_below`` en 0.01.

.. figure:: images/ex1-layer-style-ramp.png
   :alt: La pestaña Style con la rampa YlGnBu seleccionada
   :width: 100%

   **Captura:** la pestaña **Style**, modo **Continuous**, **YlGnBu**
   seleccionada, **Min** y **Max** vacíos.


Paso 4 — Agregar las cuatro capas de probabilidad
=================================================

Estas cuatro son idénticas salvo por la URL y el nombre, así que construya una y
repita. Agréguelas en este orden, para que el umbral más profundo quede más abajo
en la pila y el más superficial —que cubre la mayor superficie— quede arriba:

.. list-table::
   :header-rows: 1
   :widths: 34 66

   * - **Name** de la capa
     - ``url``
   * - ``Probabilidad de Inundación a 76 cm``
     - ``https://cog-s3-test-401506828094-us-east-1-an.s3.us-east-1.amazonaws.com/PBI_Actividad_2/prob_76cm.tif``
   * - ``Probabilidad de Inundación a 30 cm``
     - ``https://cog-s3-test-401506828094-us-east-1-an.s3.us-east-1.amazonaws.com/PBI_Actividad_2/prob_30cm.tif``
   * - ``Probabilidad de Inundación a 10 cm``
     - ``https://cog-s3-test-401506828094-us-east-1-an.s3.us-east-1.amazonaws.com/PBI_Actividad_2/prob_10cm.tif``
   * - ``Probabilidad de Inundación a 7.6 cm``
     - ``https://cog-s3-test-401506828094-us-east-1-an.s3.us-east-1.amazonaws.com/PBI_Actividad_2/prob_7p62.tif``

(Hay más información sobre los datos en
`Los datos <getting_started_es.rst#los-datos>`_.)

Para **cada** una de las cuatro:

#. En la pestaña **Layer**, defina las siguientes propiedades:

   .. list-table::
      :header-rows: 1
      :widths: 24 76

      * - Campo
        - Valor
      * - ``name``
        - *vea la tabla anterior*

#. En la pestaña **Source**, ponga **Source Type** en **GeoTIFF** y complete:

   .. list-table::
      :header-rows: 1
      :widths: 24 76

      * - Campo
        - Valor
      * - ``url``
        - *vea la tabla anterior*
      * - ``mask_below``
        - ``0``

   Cero significa "aquí no hay ninguna probabilidad de inundación".

#. En la pestaña **Style**, deje el modo en **Continuous** y elija la rampa
   **turbo**. Ponga **Min** = ``0`` y **Max** = ``1``.

   Fijar Min y Max en 0–1 es el punto central de estas cuatro capas. La
   probabilidad tiene un rango fijo y con significado propio, y las cuatro capas
   deben usar el mismo o no se pueden comparar. Si se dejan en escala automática,
   cada capa estiraría su rampa sobre su propio rango y un 0.2 se vería como una
   severidad distinta en cada una: el tono medio de la capa superficial y el de la
   capa profunda significarían números diferentes.

#. Si está configurando la primera capa, en la pestaña **Legend** seleccione
   **Default Legend**. Para un ráster con rampa, la aplicación genera
   automáticamente una barra de color.

   Solo la primera capa de probabilidad necesita su leyenda activada; las cuatro
   comparten una misma escala, así que cuatro barras de color idénticas solo
   ocuparían espacio. En la solución entregada, la capa de 76 cm es la que lleva la
   leyenda y las otras tres no tienen ninguna.

#. Guarde la capa haciendo clic en **Create**, al pie del editor de capas.

#. Guarde el elemento del mapa haciendo clic en **Save**, en la esquina inferior
   derecha del editor del mapa.

#. Cambie el tamaño del elemento del mapa para que ocupe toda la ventana,
   arrastrando el controlador de su esquina inferior derecha.

#. Guarde el tablero haciendo clic en **Save Changes**, en la esquina superior
   derecha del editor del tablero.

.. figure:: images/ex1-layer-list.png
   :alt: La lista Layers mostrando las cinco capas ráster
   :width: 100%

   **Captura:** la lista **Layers** con las cinco capas en orden.


Paso 5 — Agregar el selector de mapa base
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


Paso 6 — Actualizar el mapa base, la extensión y la ventana del mapa
====================================================================

#. Ponga el tablero en modo de edición haciendo clic en el botón
   **Edit Dashboard**, en la esquina superior derecha.

#. Haga clic en el menú de 3 puntos del elemento del mapa y seleccione **Edit**.

#. En el argumento **Base Map**, elija ``Mapa Base`` en la sección
   **Variable Inputs**, al final del desplegable. El valor pasa a ser
   ``${Mapa Base}``.

   Vea `Referenciar una variable de entrada
   <getting_started_es.rst#referenciar-una-variable-de-entrada>`_ para conocer las
   dos formas que puede tomar esta referencia.

#. En el argumento **Map Extent**, elija **Use a Custom Extent** e ingrese:

   .. code-block:: text

      -10078437.52,1629645.07,15

   Eso es ``centro-x,centro-y,zoom`` en metros de EPSG:3857.

#. En la pestaña **Settings**, active **Fill Viewport** para que el mapa ocupe
   toda la ventana.

#. Guarde el elemento haciendo clic en **Save**, en la esquina inferior derecha del
   editor del mapa.

#. Guarde el tablero haciendo clic en **Save Changes**, en la esquina superior
   derecha del editor del tablero.

.. figure:: images/ex1-settings-fill-viewport.png
   :alt: La pestaña Settings con Fill Viewport activado
   :width: 100%

   **Captura:** la pestaña **Settings** con **Fill Viewport** activado.


Punto de control
================

A estas alturas debería tener:

* Un mapa que ocupa la ventana y muestra la Ciudad de Guatemala.
* Un control de capas con seis capas (incluido el mapa base); al activar o
  desactivar cada una cambia lo que se dibuja.
* Un control de leyenda con una barra de color para la profundidad y otra para la
  probabilidad.
* Un desplegable de mapa base arriba a la izquierda que cambia las imágenes de
  fondo.
* La profundidad visible junto con las capas de probabilidad que están debajo,
  gracias a la opacidad de 0.5.


Puntos de discusión
===================

* **Escala automática frente a escala fija.** La profundidad usa escala automática
  porque su rango es una propiedad de este evento en particular. La probabilidad se
  fija en 0–1 porque el rango está definido por definición y las cuatro capas
  deben ser comparables. Es la idea más transferible de todo el ejercicio.
* **Para qué sirve** ``mask_below``. Los rásteres suelen codificar "aquí no hay
  nada" con un número real y, si no se enmascara, la rampa coloreará fielmente todo
  el dominio. Cada capa necesita un umbral distinto: ``0.01`` para la profundidad y
  ``0`` para la probabilidad.
* **El orden de las capas es el orden de dibujo.** La primera capa de la lista se
  dibuja más abajo, justo sobre el mapa base, y cada capa posterior pinta encima.
  La profundidad se agrega primero y por eso queda al fondo; las cuatro capas de
  probabilidad se apilan sobre ella, con el umbral más profundo más abajo. En la
  práctica nada queda oculto, porque cada capa está enmascarada donde no tiene
  datos: las probabilidades solo pintan donde hay alguna probabilidad distinta de
  cero, y la profundidad solo donde hay agua.
* **La restricción de proyección.** Los cinco rásteres son copias en EPSG:3857.
  Vea la advertencia en `Los datos <getting_started_es.rst#los-datos>`_; esto
  vuelve a aparecer en el ejercicio 3, donde equivocarse hace que las capas
  aparezcan y luego desaparezcan.


Siguiente
=========

`Ejercicio 2 — Impacto de una sola tormenta <exercise_2_es.rst>`_ agrega una capa
vectorial generada por un módulo y un selector alimentado por datos a lo que acaba
de construir.
