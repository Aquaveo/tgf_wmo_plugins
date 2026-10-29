.. Solución del ejercicio práctico 3 de Guatemala, español. La versión en inglés
.. está junto a este archivo como exercise_3_en.rst.

==============================================================
Ejercicio 3: Clasificación de peligro con umbrales ajustables
==============================================================

Construcción de **Guatemala Práctica 3 (Español)**, paso a paso.

Recuerde que la interfaz está en inglés, así que los nombres de botones y
campos se dejan en inglés y en negrita.

.. contents:: En esta página
   :depth: 2
   :local:
   :backlinks: none


Qué va a construir
==================

Un mapa a pantalla completa con los cuatro rásteres del ejercicio 1 más dos capas
calculadas: una clasificación de peligro y los edificios y carreteras que caen
dentro de ella. Cuatro campos numéricos en la parte superior definen el umbral de
probabilidad de cada nivel de peligro, y debajo de ellos hay una tabla de impacto.
Al cambiar un umbral, la clasificación, los elementos afectados y la tabla se
vuelven a calcular.

.. figure:: images/ex3-finished.png
   :alt: El tablero terminado del ejercicio 3
   :width: 100%

   **Captura:** el tablero terminado: mapa a pantalla completa, cuatro campos de
   umbral en la parte superior y la tabla de impacto a la derecha.

**Consejo:** ``notebooks/Guatemala/03_hazard_classification_es.ipynb`` deriva esta
clasificación en Python, incluido el barrido de umbrales que muestra qué controla
cada uno. Vale la pena ejecutarlo primero si quiere entender el análisis antes de
armar la interfaz. El cuaderno todavía usa los archivos de capacitación
anteriores, así que sus números difieren de los de este tablero.


Entender los cuatro umbrales
============================

Cada nivel de peligro está ligado a **una** profundidad y tiene su **propio**
umbral de probabilidad:

.. list-table::
   :header-rows: 1
   :widths: 18 32 25 25

   * - Nivel
     - Determinado por
     - Color
     - Umbral inicial
   * - Bajo
     - P(≥ 10 cm)
     - verde
     - 0.8
   * - Medio
     - P(≥ 30 cm)
     - amarillo
     - 0.8
   * - Alto
     - P(≥ 70 cm)
     - rojo
     - 0.8
   * - Severo
     - P(≥ 100 cm)
     - morado
     - 0.8

Una celda toma el nivel del umbral **más profundo** que logra superar.

**Todos los niveles son alcanzables en la muestra.** Las probabilidades son
fracciones de 50 miembros del conjunto, así que cada valor es múltiplo de 0.02, y
cada uno de los cuatro rásteres llega a 1.0 en algún punto. Con los umbrales por
defecto de 0.8, el número de celdas que superan su umbral es:

.. list-table::
   :header-rows: 1
   :widths: 25 25 25 25

   * - P(≥ 10 cm)
     - P(≥ 30 cm)
     - P(≥ 70 cm)
     - P(≥ 100 cm)
   * - 3,900
     - 3,155
     - 2,880
     - 2,646

Así que los cuatro colores aparecen con los valores por defecto. Bajar un umbral
solo deja que más celdas lo superen: en las cuatro profundidades, 15,877, 12,269,
10,219 y 9,315 celdas, respectivamente, tienen alguna probabilidad. Una celda que
supera varios umbrales se muestra en el más profundo, así que estas cifras se
superponen y no se suman.


Paso 1: Crear el tablero
========================

#. Cree un tablero nuevo (vea
   `Crear un tablero <getting_started_es.rst#crear-un-tablero>`_) con:

   * **Name**: ``Guatemala Práctica 3 (Español)``
   * **Description**: ``Solución para el Ejercicio Práctico #3 de la OMM en Guatemala``

#. Busque su tablero en la página de inicio y haga doble clic para abrirlo. El
   tablero está vacío, así que la previsualización muestra un lienzo en blanco.

#. Abra **Dashboard Settings** en la esquina superior derecha y active
   **Unrestricted Grid Item Movement**. Guarde la configuración.

#. Salga de **Dashboard Settings** y haga clic en **Edit Dashboard**, en la
   esquina superior derecha, para entrar en modo de edición.


Paso 2: Agregar el selector de mapa base
========================================

El mapa base es una variable de entrada, para que el usuario pueda cambiarlo sin
editar nada. Construya primero la variable y después apunte el mapa a ella.

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
   derecho del editor. La solución entregada usa ``World Imagery``, pero
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


Paso 3: Agregar los cuatro campos de umbral
===========================================

Construya los cuatro antes que las capas que los consumen. Cada uno es un
**Variable Input** con ``variable_options_source`` en ``number``:

.. list-table::
   :header-rows: 1
   :widths: 100

   * - ``Variable Name``
   * - ``Umbral Bajo (P(≥10 cm))``
   * - ``Umbral Medio (P(≥30 cm))``
   * - ``Umbral Alto (P(≥70 cm))``
   * - ``Umbral Severo (P(≥100 cm))``

Para **cada** uno de los cuatro:

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
        - *vea la tabla anterior*
      * - ``show_label``
        - ``True``
      * - ``variable_options_source``
        - ``number``

#. En la pestaña **Settings**, ponga **Background Color** en ``#ffffff``.

#. En la pestaña **Settings**, agregue un borde superior haciendo clic en el icono
   del borde superior. Aparecerá una ventana emergente. Cambie el estilo a
   ``solid`` para que el borde se muestre.

   Dele además un borde izquierdo al campo de más a la izquierda
   (``Umbral Bajo``) y un borde derecho al de más a la derecha
   (``Umbral Severo``), para que los cuatro se lean como una sola franja.

#. Ponga el valor inicial en ``0.8`` desde la previsualización, en el lado derecho
   del editor.

#. Guarde el elemento haciendo clic en **Save**, en la esquina inferior derecha del
   editor del elemento.

#. Arrastre el elemento a su lugar, a lo largo de la parte superior del tablero y a
   la derecha del selector de mapa base, y cambie su tamaño según haga falta.

#. Guarde el tablero haciendo clic en **Save Changes**, en la esquina superior
   derecha del editor del tablero.

.. figure:: images/ex3-threshold-inputs.png
   :alt: Los cuatro campos de umbral a lo largo de la parte superior del tablero
   :width: 100%

   **Captura:** los cuatro campos de umbral uno al lado del otro, cada uno con su
   etiqueta y su valor.


Paso 4: Agregar el mapa y los cuatro rásteres
=============================================

Si tiene el ejercicio 1, siga los pasos de abajo. Si no lo tiene, construya el mapa
y los cuatro rásteres desde cero como en el
`Ejercicio 1 <exercise_1_es.rst>`_.

#. Abra el tablero del ejercicio 1.

#. Haga clic en el menú de 3 puntos del elemento del mapa y elija **Export**.

#. Abra el tablero nuevo de este ejercicio.

#. Haga clic en **Edit Dashboard**, en la esquina superior derecha, para entrar en
   modo de edición.

#. Haga clic en **Import Dashboard Item**, en la esquina superior derecha, e
   importe el elemento del ejercicio 1.

#. Si el mapa está cubriendo los selectores, haga clic en el menú de 3 puntos, pase
   el cursor sobre **Order** y seleccione **Send to Back**. Los selectores deberían
   quedar visibles sobre el mapa.

#. Edite el elemento del mapa. Para cada uno de los cuatro rásteres, edite la capa y
   desactive **Default Visibility** en la pestaña **Layer**. Así las capas quedarán
   ocultas cuando el tablero se cargue por primera vez. Asegúrese de guardar la
   capa después de editarla.

#. Guarde el tablero haciendo clic en **Save Changes**, en la esquina superior
   derecha del editor del tablero.


Paso 5: Agregar la capa de clasificación de peligro
===================================================

#. Ponga el tablero en modo de edición haciendo clic en el botón
   **Edit Dashboard**, en la esquina superior derecha.

#. Haga clic en el menú de 3 puntos del elemento del mapa y seleccione **Edit**.
   Puede que tenga que mover uno de los campos de umbral para poder ver el menú del
   mapa.

#. Junto a **Layers**, haga clic en **Add Layer**.

#. Vaya directamente a la pestaña **Source** y ponga **Source Type** en
   **Guatemala: Capa de Peligro** (en el grupo **UFFIS: Guatemala**).

#. Aparecen los argumentos del módulo. Complete:

   .. list-table::
      :header-rows: 1
      :widths: 26 74

      * - Argumento
        - Valor
      * - ``Umbral Bajo``
        - ``${Umbral Bajo (P(≥10 cm))}``
      * - ``Umbral Medio``
        - ``${Umbral Medio (P(≥30 cm))}``
      * - ``Umbral Alto``
        - ``${Umbral Alto (P(≥70 cm))}``
      * - ``Umbral Severo``
        - ``${Umbral Severo (P(≥100 cm))}``
      * - ``Ciclo``
        - **Evento de muestra** (``sample``)

   ``Ciclo`` elige el ciclo de TITO que clasifica el módulo. **Evento de muestra**
   es el ciclo de muestra publicado para el país, el mismo del que vienen las
   cuatro capas ráster. Si se deja vacío, el módulo lee el último ciclo en vivo, y
   el peligro dejaría de coincidir con los rásteres de abajo. Deje
   ``Fuente Inundacion`` vacío; su valor por defecto es la fuente combinada con
   desborde que usan los rásteres.

#. Haga clic en **Fetch plugin defaults**. La capa recibe el nombre
   **Clasificación de peligro**, un estilo con cuatro reglas sobre el atributo
   ``peligro`` y una leyenda **Peligro** de cuatro entradas.

#. Guarde la capa haciendo clic en **Create**, al pie del editor de capas.

.. figure:: images/ex3-hazard-layer-source.png
   :alt: La configuración de la fuente de la capa de peligro con los cuatro umbrales vinculados
   :width: 100%

   **Captura:** la pestaña **Source** de la capa de peligro, con los cuatro
   argumentos vinculados a las cuatro variables de umbral y ``Ciclo`` en
   **Evento de muestra**.


Paso 6: Agregar la capa de elementos afectados
==============================================

#. Junto a **Layers**, haga clic otra vez en **Add Layer**.

#. Vaya directamente a la pestaña **Source** y ponga **Source Type** en
   **Guatemala: Capa de Impacto**.

#. Vincule los mismos cuatro argumentos a las mismas cuatro variables que en el
   paso anterior, y ponga otra vez ``Ciclo`` en **Evento de muestra**.

#. Haga clic en **Fetch plugin defaults**. La capa llega con el nombre
   **Edificios y carreteras en peligro**, ocho reglas (polígono y línea por cada
   nivel) y una leyenda **Peligro**.

#. Guarde la capa haciendo clic en **Create**, al pie del editor de capas.

Las dos capas responden preguntas distintas a partir de los mismos umbrales: la
capa de peligro clasifica el *terreno* y esta clasifica los *bienes*. Mantenerlas
separadas permite que el usuario apague el sombreado del terreno y mire solo lo que
está afectado.


Paso 7: Terminar el mapa
========================

#. En el argumento **Map Extent**, elija **Use a Custom Extent** e ingrese:

   .. code-block:: text

      -10077781.20,1629865.34,15.13

#. En la pestaña **Settings**, active **Fill Viewport** para que el mapa ocupe
   toda la ventana.

#. Guarde el elemento haciendo clic en **Save**, en la esquina inferior derecha del
   editor del mapa.

#. Cambie el tamaño del elemento del mapa para que ocupe toda la ventana,
   arrastrando el controlador de su esquina inferior derecha.

#. Asegúrese de devolver el campo de umbral a su lugar.

#. Guarde el tablero haciendo clic en **Save Changes**, en la esquina superior
   derecha del editor del tablero.

**Importante:** Los rásteres deben estar en EPSG:3857 (o EPSG:4326), como los de
la muestra. Si alguna capa apunta a un ráster en otra proyección, como UTM, el
mapa se ajustará automáticamente a la proyección de ese ráster, saltará a un lugar
lejano de Guatemala y las capas vectoriales parecerán cargar y luego
desaparecerán. Este error exacto costó tiempo real de depuración en
este tablero.


Paso 8: Agregar la tabla de resumen de impacto
==============================================

#. Ponga el tablero en modo de edición haciendo clic en el botón
   **Edit Dashboard**, en la esquina superior derecha.

#. Agregue otro elemento haciendo clic en **Add Dashboard Item**, en la esquina
   superior derecha.

#. Haga clic en el menú de 3 puntos del elemento nuevo y seleccione **Edit**.

#. Ponga **Visualization Type** en **Guatemala: Resumen de Impacto** (en el grupo
   **UFFIS: Guatemala**).

#. Vincule los mismos cuatro argumentos a las mismas cuatro variables que en el
   paso 5, y ponga ``Ciclo`` en **Evento de muestra**.

   La tabla cuenta las personas, edificios y carreteras de cada nivel de peligro,
   con los mismos umbrales que el mapa, y termina con una fila
   **TOTAL en peligro**.

#. En la pestaña **Settings**, ponga **Background Color** en ``#ffffff`` y agregue
   bordes a la izquierda, a la derecha y abajo, para que se una a la franja de
   campos de umbral que está arriba.

#. Guarde el elemento haciendo clic en **Save**, en la esquina inferior derecha del
   editor del elemento.

#. Arrastre el elemento justo debajo de los campos de umbral, a la derecha, y
   cambie su tamaño según haga falta.

#. Guarde el tablero haciendo clic en **Save Changes**, en la esquina superior
   derecha del editor del tablero.

.. figure:: images/ex3-impact-summary.png
   :alt: La tabla de resumen de impacto con los cuatro umbrales vinculados
   :width: 100%

   **Captura:** los argumentos de la tabla de resumen de impacto vinculados a las
   cuatro variables de umbral, con ``Ciclo`` en **Evento de muestra**.


Paso 9: Probar las conexiones
=============================

Cambie un umbral. El sombreado de peligro, los elementos afectados y la tabla
deberían recalcularse juntos, con mensajes de progreso mientras las capas se
reconstruyen. Como demostración, baje el umbral Severo a 0.2. La clase Severo, en
morado, se extiende más a lo largo del cauce, y la tabla muestra más edificios y
carreteras en la fila Severo.

.. figure:: images/ex3-thresholds-before.png
   :alt: El tablero antes de bajar un umbral
   :width: 100%

   **Captura:** la misma vista antes de bajar el umbral Severo.

.. figure:: images/ex3-thresholds-after.png
   :alt: El tablero después de bajar un umbral
   :width: 100%

   **Captura:** la misma vista después de bajar el umbral Severo.


Punto de control
================

A estas alturas debería tener:

* Un mapa que ocupa la ventana, con siete capas en el control de capas (cuatro
  rásteres, las dos capas calculadas y el mapa base).
* Cuatro campos de umbral etiquetados en la parte superior, cada uno con paso de
  0.05.
* Con los umbrales por defecto de 0.8: 1,127 polígonos de peligro con los cuatro
  colores, 453 edificios y carreteras en peligro, y una tabla de impacto cuya fila
  **TOTAL en peligro** muestra 342 edificios y 886 personas.
* Al mover cualquier umbral se actualizan la capa de peligro, la capa de impacto y
  la tabla.
* Mensajes de progreso mientras las capas se recalculan.


Puntos de discusión
===================

* **Cuatro umbrales sobre cuatro preguntas distintas.** Con umbrales distintos,
  "Severo" podría significar P(≥100 cm) ≥ 0.15, mientras que "Alto" significa
  P(≥70 cm) ≥ 0.1. Son preguntas
  diferentes con cortes diferentes, así que los nombres de los niveles no son
  comparables entre sí y "severo" no significa nada por sí solo. Poner los cuatro
  umbrales en el mismo valor es una buena demostración: los niveles se diferencian
  entonces solo por la profundidad, que es mucho más fácil de explicar.
* **Una clase vacía es un problema de interfaz.** En la muestra todos los niveles
  son alcanzables, pero en un evento menor un umbral profundo puede no acercarse
  nunca al valor elegido, y entonces ese color simplemente no aparece. Quien mueva
  ese control no recibe ninguna señal que distinga entre "nada califica" y "el
  control está roto". Pregunte a los participantes cómo lo resolverían: ¿mostrar
  el rango de valores? ¿anotar la leyenda? No hay una única respuesta correcta, y
  la discusión es justamente el objetivo.
* **Las probabilidades van en pasos de 0.02.** Con 50 miembros, una probabilidad
  solo puede ser múltiplo de 0.02, así que un umbral de 0.8 significa "al menos 40
  de los 50 miembros". Presentar un umbral como un número de miembros suele ser
  más fácil de explicar que una probabilidad.
* **Vectorizar una clasificación.** Una capa de mapa solo puede apuntar a una URL, y
  aquí nada sirve un ráster calculado, así que el módulo vectoriza la cuadrícula
  clasificada en polígonos (1,127 con los umbrales por defecto). Las celdas
  contiguas de la misma clase se fusionan, así que esto es exacto y no una
  aproximación. Las celdas Normal y NoData, la mayor parte de la cuadrícula, se
  descartan, porque un mapa base muestra el terreno no afectado mejor que una
  capa de color.


Posiciones de los elementos
===========================

La solución entregada coloca sus elementos así, en la cuadrícula de 100 columnas:

.. list-table::
   :header-rows: 1
   :widths: 40 15 15 15 15

   * - Elemento
     - ``x``
     - ``y``
     - ``w``
     - ``h``
   * - Mapa
     - 0
     - 0
     - 99
     - 41
   * - Variable Mapa Base
     - 0
     - 0
     - 17
     - 6
   * - Umbral Bajo
     - 56
     - 0
     - 11
     - 7
   * - Umbral Medio
     - 67
     - 0
     - 11
     - 7
   * - Umbral Alto
     - 78
     - 0
     - 11
     - 7
   * - Umbral Severo
     - 89
     - 0
     - 11
     - 7
   * - Tabla de resumen de impacto
     - 56
     - 7
     - 44
     - 26
