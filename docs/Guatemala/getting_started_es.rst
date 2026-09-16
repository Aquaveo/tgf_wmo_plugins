.. Portada compartida de las guías de ejercicios prácticos de Guatemala, español.
.. La versión en inglés está junto a este archivo como getting_started_en.rst.

==============================================================
Ejercicios Prácticos de Guatemala: Para Empezar
==============================================================

Instalación, contexto y los pasos que se repiten en todos los ejercicios. Lea esta
página una vez y luego trabaje el ejercicio que necesite.

**Nota sobre el idioma** — La interfaz de TethysDash está en inglés. Por eso los
nombres de botones, pestañas y campos se dejan en inglés y **en negrita**
(**Add Layer**, **Save Changes**), tal como aparecen en la pantalla. El texto
explicativo está en español.

.. contents:: En esta página
   :depth: 2
   :local:
   :backlinks: none


Los tres ejercicios
===================

Cada ejercicio construye un tablero de visualización y tiene su propio archivo:

.. list-table::
   :header-rows: 1
   :widths: 30 22 48

   * - Guía
     - Tablero
     - Qué muestra
   * - `Ejercicio 1 — Un mapa de profundidad y probabilidad de inundación <exercise_1_es.rst>`_
     - Guatemala Práctica 1 (Español)
     - Un ráster de profundidad de inundación y cuatro rásteres de probabilidad de
       excedencia en un solo mapa, con un mapa base intercambiable.
   * - `Ejercicio 2 — Impacto de una sola tormenta <exercise_2_es.rst>`_
     - Guatemala Práctica 2 (Español)
     - La profundidad de una sola tormenta de un conjunto de 198 miembros, junto
       con los edificios y las carreteras que esa tormenta inunda, una tabla
       resumen y una tarjeta con las cifras principales.
   * - `Ejercicio 3 — Clasificación de peligro con umbrales ajustables <exercise_3_es.rst>`_
     - Guatemala Práctica 3 (Español)
     - Una clasificación de peligro controlada por cuatro umbrales de probabilidad
       que el usuario puede mover, con los edificios y carreteras afectados y una
       tabla de impacto.

Los ejercicios son acumulativos en dificultad, no en contenido: cada uno es un
tablero independiente y se puede construir por separado. El ejercicio 1 enseña las
capas ráster, el 2 agrega una capa vectorial generada por un módulo y un
selector alimentado por datos, y el 3 agrega interactividad mediante variables de
entrada.

Cuadernos complementarios
-------------------------

``notebooks/Guatemala/02_storm_impact_es.ipynb`` y
``notebooks/Guatemala/03_hazard_classification_es.ipynb`` derivan en Python los números que
están detrás de los ejercicios 2 y 3. Estas guías tratan de *cómo construir el
tablero*; los cuadernos tratan de *por qué los números son los que son*. Se
complementan bien: ejecute el cuaderno primero si quiere entender el análisis, y
siga la guía si quiere armar la interfaz.

Convenciones
------------

* La **negrita** marca algo en lo que se hace clic, o la etiqueta de un campo tal
  como aparece en la interfaz, por ejemplo **Add Layer** o **Source Type**.
* El ``monoespaciado`` marca un valor que se escribe o se pega.
* Los pasos están numerados. Cuando el orden no importa, se dice explícitamente.
* Cada ejercicio termina con un **Punto de control** que enumera lo que debería
  poder ver, y con **Puntos de discusión** que vale la pena mencionar si usted es
  quien enseña.

**Nota** — Las capturas de pantalla de estas guías son marcadores de posición.
Cada bloque ``figure`` describe lo que debe mostrar la imagen; coloque un PNG en
la ruta indicada dentro de ``docs/Guatemala/images/`` y se mostrará.


Antes de empezar
================

Lo que necesita
---------------

#. **Una instancia de TethysDash donde pueda crear tableros.** Debe poder llegar a
   la página de inicio y crear un tablero, lo que implica una cuenta con permiso
   para crear tableros.
#. **El paquete** ``tgf_wmo_plugins`` **instalado en el servidor**, no solo en su
   computadora. Los módulos de visualización se descubren en el backend mediante
   los puntos de entrada de Intake, así que el proceso de la aplicación debe poder
   importarlos:

   .. code-block:: bash

      pip install git+https://github.com/Aquaveo/tgf_wmo_plugins.git

   Reinicie la aplicación de Tethys después de instalar. Para confirmar que
   funcionó, abra el desplegable **Visualization Type** de cualquier elemento del
   tablero y busque el grupo **Mapas de Inundación (Español)**.
#. **Salida HTTPS desde el servidor.** Cada módulo lee sus datos de un bucket
   público de S3 en el momento de la solicitud. Nada viene incluido en el paquete.
#. **Permisos de visualización**, si su instancia restringe los tipos de módulo.
   Los ejercicios usan los tipos ``table``, ``card`` y ``map_layer``.

**Advertencia** — Si el grupo **Mapas de Inundación (Español)** no aparece en el
desplegable, el paquete no está instalado en el entorno donde realmente se ejecuta
la aplicación. Este es, por mucho, el problema de instalación más común. Instalarlo
en el Python de su terminal no es suficiente cuando la aplicación corre bajo otro
intérprete o en otro contenedor.

Los datos
---------

Todo proviene de un solo bucket público. La raíz es la misma en todos los casos, y
los ejercicios se refieren a ella como ``.../``:

.. code-block:: text

   https://cog-s3-test-401506828094-us-east-1-an.s3.us-east-1.amazonaws.com

Importan tres prefijos:

.. list-table::
   :header-rows: 1
   :widths: 26 74

   * - Prefijo
     - Contenido
   * - ``PBI_Actividad_2/``
     - Los rásteres que usan las capas del mapa: un GeoTIFF de profundidad, cuatro
       GeoTIFF de probabilidad de excedencia y los archivos que acompañan al
       almacén Zarr del conjunto. Todos son copias en EPSG:3857 sobre una única
       cuadrícula compartida.
   * - ``Guatemala_IBF/``
     - Los elementos de impacto (edificios y carreteras) y los rásteres originales
       en UTM de los que fueron muestreados. Los módulos leen de aquí el CSV
       reducido.
   * - ``floodmaps_test/``
     - El almacén Zarr del conjunto de 198 miembros que usa el ejercicio 2.

**Importante** — Los rásteres a los que apuntan los tableros son las copias en
**EPSG:3857** dentro de ``PBI_Actividad_2/``, no los originales en UTM de
``Guatemala_IBF/``. Esto no es un detalle cosmético. TethysDash no incluye proj4,
por lo que OpenLayers solo puede resolver EPSG:4326 y EPSG:3857 para los datos de
una capa. Si apunta una capa a un ráster en UTM, parecerá cargar y luego
desaparecerá, o arrastrará todo el mapa a UTM. Si una capa aparece y desaparece,
revise primero su proyección.


Pasos comunes a los tres ejercicios
===================================

Estos pasos se repiten en todos los ejercicios. Se explican una sola vez aquí, y
los ejercicios se refieren a ellos como "crear el tablero" y "agregar un elemento
al tablero".

Crear un tablero
----------------

#. En la página de inicio, haga clic en la tarjeta **Create a New Dashboard**.
#. Complete **Name** y **Description**, y luego haga clic en **Create**.
#. El tablero nuevo se abre vacío.

.. figure:: images/00-landing-page.png
   :alt: La página de inicio de TethysDash con la tarjeta Create a New Dashboard
   :width: 100%

   **Captura:** la página de inicio, con la tarjeta **Create a New Dashboard** a
   la vista.

.. figure:: images/00-new-dashboard-modal.png
   :alt: La ventana de tablero nuevo con los campos Name y Description
   :width: 100%

   **Captura:** la ventana de tablero nuevo, con Name y Description completados.

Entrar en modo de edición
-------------------------

Un tablero solo puede ser modificado por su propietario, y solo en modo de
edición. Haga clic en el botón **Edit Dashboard** en el encabezado. El encabezado
ofrece entonces lo siguiente:

.. list-table::
   :header-rows: 1
   :widths: 34 66

   * - Botón
     - Qué hace
   * - **Add Dashboard Item**
     - Agrega un elemento nuevo, sin configurar, a la distribución.
   * - **Lock/Unlock Movement**
     - Fija la posición de los elementos para que pueda hacer clic sin arrastrar.
   * - **Import Dashboard Item**
     - Carga un elemento desde un archivo de configuración exportado.
   * - **Dashboard Settings**
     - Nombre, descripción, miniatura, opciones para compartir, notas y
       **Unrestricted Grid Item Movement**.
   * - **Save Changes**
     - Guarda la distribución.
   * - **Cancel**
     - Descarta los cambios y vuelve al último guardado.

.. figure:: images/00-edit-mode-toolbar.png
   :alt: La barra de herramientas del encabezado en modo de edición
   :width: 100%

   **Captura:** la barra de herramientas del encabezado en modo de edición, con
   los botones anteriores a la vista.

**Consejo** — Guarde con frecuencia. **Cancel** revierte al último guardado, así
que una sesión larga de edición sin guardar está a un solo error de perderse.

Agregar y configurar un elemento del tablero
--------------------------------------------

#. En modo de edición, haga clic en **Add Dashboard Item**. Aparece un elemento
   vacío.
#. Haga clic en el **menú de 3 puntos** del elemento y seleccione **Edit**. Se
   abre la ventana del visor de datos.
#. En la pestaña **Visualization**, elija un **Visualization Type**. Debajo
   aparecen los argumentos de esa visualización.
#. Complete los argumentos. La previsualización se actualiza a medida que avanza.
#. Cambie a la pestaña **Settings** para las opciones del elemento: bordes, color
   de fondo, **Fill Viewport**. Las opciones solo están disponibles una vez que la
   visualización está configurada y previsualizándose.
#. Haga clic en **Save**, en la esquina inferior derecha del editor del elemento,
   para aplicar los cambios; después haga clic en **Save Changes**, en la esquina
   superior derecha del editor del tablero, para guardarlos.

.. figure:: images/00-dataviewer.png
   :alt: La ventana del visor de datos con el desplegable Visualization Type
   :width: 100%

   **Captura:** el visor de datos con el desplegable **Visualization Type**
   abierto, mostrando el grupo **Mapas de Inundación (Español)**.

.. figure:: images/00-griditem-menu.png
   :alt: El menú de 3 puntos de un elemento del tablero, abierto
   :width: 100%

   **Captura:** el menú de 3 puntos de un elemento, mostrando Edit, Create Copy,
   Export y Delete.

Dimensionar y ubicar los elementos
----------------------------------

Arrastre un elemento por su cuerpo y cambie su tamaño desde el controlador de la
esquina inferior derecha. La cuadrícula tiene 100 columnas de ancho. Las tres
soluciones activan **Unrestricted Grid Item Movement** (en **Dashboard
Settings**), que permite colocar los elementos en cualquier lugar y superponerlos;
aquí es necesario para que los controles y los paneles puedan flotar sobre un mapa
a pantalla completa.

Cada ejercicio termina con una tabla de **Posiciones de los elementos** que indica
los valores exactos de ``x``, ``y``, ``w`` y ``h`` de cada elemento de esa
solución. No hace falta reproducirlos al píxel: arrastre a una posición parecida y
ajuste.

Referenciar una variable de entrada
-----------------------------------

Los tres ejercicios conectan visualizaciones a variables de entrada. Hay dos
formas de escribir la referencia, según el argumento:

* Los **argumentos de tipo desplegable** enumeran las variables disponibles en una
  sección **Variable Inputs** al final del desplegable: elíjala de allí.
* Los **argumentos de texto libre** usan la sintaxis de plantilla
  ``${Nombre de la Variable}``, escrita a mano.

El nombre dentro de las llaves debe coincidir exactamente con el ``variable_name``
de la variable de entrada, incluidos los espacios y la puntuación. Construya la
variable de entrada *antes* de los elementos que la referencian, o no habrá nada
que seleccionar.


Importar una solución terminada
===============================

Para reiniciar entre sesiones, o para verificar su trabajo, los tableros
terminados están en este repositorio dentro de ``dashboards/``:

.. code-block:: text

   dashboards/Guatemala/Guatemala_Hands_On_1_Espanol.json
   dashboards/Guatemala/Guatemala_Hands_On_2_Espanol.json
   dashboards/Guatemala/Guatemala_Hands_On_3_Espanol.json

Las versiones en inglés están junto a ellos, con ``_English`` en lugar de
``_Espanol``. Los tableros en español usan los módulos ``_es`` en todo momento, de
modo que cada tablero es coherente en un solo idioma: no los mezcle.

Estos archivos son exportaciones de tableros completos. Los elementos individuales
también se pueden mover entre tableros con **Export** en el menú de 3 puntos de un
elemento y **Import Dashboard Item** en el encabezado, que es la forma más rápida
de reutilizar las cinco capas ráster del ejercicio 1 en el ejercicio 3.


Solución de problemas
=====================

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Síntoma
     - Causa y solución
   * - El grupo **Mapas de Inundación (Español)** no aparece en
       **Visualization Type**.
     - ``tgf_wmo_plugins`` no está instalado en el entorno donde corre la
       aplicación, o la aplicación no se reinició. Instálelo en el servidor y
       reinicie.
   * - Una visualización dice que una variable está vacía.
     - El nombre en ``${...}`` no coincide exactamente con un ``variable_name``, o
       la variable de entrada se agregó después del elemento que la referencia.
       Revise la ortografía, los espacios y la puntuación, y vuelva a seleccionar
       la variable.
   * - Una capa aparece y luego desaparece.
     - Casi siempre es un problema de proyección. Confirme que la capa apunta a la
       copia en EPSG:3857 de ``PBI_Actividad_2``, no a un original en UTM de
       ``Guatemala_IBF``.
   * - Todo el mapa salta a algún lugar de África.
     - La misma causa. Un GeoTIFF en una proyección que no se puede resolver hace
       que el ajuste automático adopte coordenadas que caen cerca de 0°, 0°.
   * - Todos los elementos vectoriales se ven grises.
     - Las reglas de estilo no coinciden. Use **Fetch plugin defaults** en lugar de
       escribir las reglas a mano; una regla mal formada nunca coincide y falla en
       silencio.
   * - Un ráster se ve de un solo color plano.
     - Los límites de la rampa no corresponden a los datos, o ``mask_below`` no
       está definido y por eso se está coloreando el suelo seco. Revise ambos.
   * - El color morado nunca aparece en el ejercicio 3.
     - Es lo esperado si el umbral Severo está por encima de 0.2. El ráster de
       76 cm solo contiene 0 o 0.2. Baje el umbral a 0.2 o menos.
   * - El tablero no se puede editar.
     - Solo el propietario puede editar, y solo en modo de edición. Busque el botón
       **Edit Dashboard** en el encabezado.
