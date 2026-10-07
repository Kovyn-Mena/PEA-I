===============================================================================
PEA-i: PROGRAMA ESTADISTICO DE ANALISIS DE INVESTIGACION (UPC)
GUIA DE EJECUCION RAPIDA PARA USUARIOS DE WINDOWS
===============================================================================
Universidad Popular del Cesar - Facultad de Ingenieria y Tecnologicas
Asignatura: Estructura de Datos (Taller 2) | Semestre 2026-I
Docente Evaluador: Ing. Adith Bismarck Perez Orozco
Estudiante: Kovyn B. Mena (kbmena@unicesar.edu.co)
===============================================================================

Estimado profesor y companeros:

Este proyecto esta completamente optimizado para ejecutarse en WINDOWS con
maxima compatibilidad y sin necesidad de instalar entornos complejos de Linux
ni requerir el comando 'make'.

-------------------------------------------------------------------------------
1. COMO INICIAR EN WINDOWS (FORMA MAS FACIL - 1 CLIC):
-------------------------------------------------------------------------------
Simplemente haga DOBLE CLIC en cualquiera de los siguientes archivos:

  • INICIAR_WINDOWS.bat (o iniciar.bat):
    Lanzador interactivo visual con menu de opciones:
      [1] Ejecutar consola autonoma (abre de inmediato).
      [2] Compilar y ejecutar C++ (autodetecta MSYS2, Code::Blocks, MinGW, g++).
      [3] Abrir Portal Web Ejecutivo (Visualizador del Hipercubo con CRUD).
      [4] Ver Documentacion Tecnica Oficial Word (.docx).
      [5] Ver Informe Oficial PDF de Investigacion (ReportLab).
      [6] Ejecutar suite de pruebas unitarias de los TDAs (100% verde).

  • ejecutar.bat (o ejecutar_windows.bat):
    Ejecuta directamente la aplicacion sin compilar nada, con los 3,351 productos,
    investigadores y grupos precargados en memoria RAM.

  • compilar.bat (o compilar_cpp_windows.bat):
    Compila el codigo fuente de C++17 hacia 'pea_cpp.exe' detectando
    automaticamente si tiene instalado MSYS2 (UCRT64/MinGW64), Code::Blocks,
    Dev-C++ o g++ en su PATH.

-------------------------------------------------------------------------------
2. CONTROL POR TECLADO EN LA CONSOLA (SOLICITUD ENTER):
-------------------------------------------------------------------------------
  • Todos los menus, submenus y paginaciones se controlan escribiendo la opcion
    deseada y presionando la tecla ENTER (control por linea estandar).
  • En cualquier menu, ingrese '0' y presione ENTER para regresar al menu anterior.
  • En tablas largas: 'S' (siguiente), 'A' (anterior), 'B' (buscar), '0' (salir).

-------------------------------------------------------------------------------
3. PORTAL WEB INTERACTIVO & GESTION CRUD (C++ / HTML5):
-------------------------------------------------------------------------------
  • Abra 'dist/visualizador_hipercubo.html' en cualquier navegador (Chrome, Edge, etc.).
  • Cuenta con:
    - Directorio completo de Grupos con balance MinCiencias 2024 e IPP.
    - Pestaña 'Gestion y Control CRUD': permite crear, editar y alternar estado
      (activo/inactivo) de Grupos, Investigadores y Productos.
    - Motor de Deshacer (Pila LIFO): boton 'Deshacer' con historial de pila.
    - Boton 'Sincronizar / SQLite': genera el archivo 'data/cambios_gui.json'
      y las sentencias SQL para sincronizar en doble via con la consola C++.

===============================================================================
