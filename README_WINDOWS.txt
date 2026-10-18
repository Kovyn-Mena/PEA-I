===============================================================================
PEA-i: PROGRAMA ESTADISTICO DE ANALISIS DE INVESTIGACION (UPC)
GUIA DE EJECUCION RAPIDA PARA USUARIOS DE WINDOWS
===============================================================================
Universidad Popular del Cesar - Facultad de Ingenieria y Tecnologicas
Asignatura: Estructura de Datos (Taller 2) | Semestre 2026-I
Docente Evaluador: Ing. Adith Bismarck Perez Orozco
Estudiante: Kovyn B. Mena (kbmena@unicesar.edu.co)
===============================================================================

1. COMO INICIAR EN WINDOWS (UN SOLO ARCHIVO: iniciar.bat):
-------------------------------------------------------------------------------
Haga DOBLE CLIC en el archivo:

  * iniciar.bat

Este lanzador unificado detecta automaticamente la carpeta del proyecto (incluso
si la ruta contiene espacios) y verifica instalaciones reales de Python 3 y C++17
(evitando el alias vacio de Microsoft Store):

  [1] Consola Interactiva Python (Recomendado - Abre al instante sin compilar)
  [2] Dashboard Grafico Interactivo Python (HTML5 + 3 Vistas --gui)
  [3] Portal Web Interactivo del Hipercubo y CRUD (HTML5 Offline)
  [4] Compilar y Ejecutar en C++17 (Autodetecta MSYS2, MinGW, Code::Blocks)
  [5] Ejecutar Pruebas Unitarias de Estructuras de Datos (TDAs Python + C++)
  [6] Abrir Documentacion Tecnica Oficial Word (.docx)
  [7] Empaquetar Entrega Formal en ZIP (Limpio para envio al docente)
  [8] Ingesta Masiva UPC - 66 grupos con hojas de vida CvLAC
      [8-1] Rapida offline (snapshots locales, sin CvLAC)
      [8-2] Completa en vivo (red MinCiencias + CvLAC, 1-2 horas)
      [8-3] Completa forzada (reprocesa todo)
  [9] Diagnostico del sistema (reporte para soporte)

2. EJECUCION DIRECTA DEL PORTAL WEB (SIN CONSOLA):
-------------------------------------------------------------------------------
Tambien puede abrir directamente el archivo:
  * dist\visualizador_hipercubo.html
en cualquier navegador (Edge, Chrome, Brave, Firefox) sin conexion a internet.
===============================================================================

3. DEPENDENCIAS PYTHON (requests, bs4, pypdf, reportlab):
-------------------------------------------------------------------------------
El proyecto incluye el bundle local pylib\ que cubre lo esencial sin instalar
nada (portable). Si alguna funcion falla con ModuleNotFoundError, instale con:

  pip install -r requirements.txt

4. INGESTA MASIVA POR TERMINAL (alternativa a la opcion [8]):
-------------------------------------------------------------------------------
  python Taller2_AB_PO_XX.py --auto-ingest --sin-cvlac    (rapida offline)
  python Taller2_AB_PO_XX.py --auto-ingest --en-vivo --forzar --sin-cvlac
                                                          (vivo, sin CvLAC)
  python Taller2_AB_PO_XX.py --auto-ingest --en-vivo --forzar --reanudar
                                                          (reanudable)
  python Taller2_AB_PO_XX.py --auto-ingest --en-vivo --forzar --limite 5
                                                          (muestra de 5 grupos)
  python Taller2_AB_PO_XX.py --auto-ingest --en-vivo --forzar-vacios
                                                          (recarga vacios)
  python Taller2_AB_PO_XX.py --purgar-grupos               (simulacion)
  python Taller2_AB_PO_XX.py --purgar-grupos --confirmar   (purga real)
  python Taller2_AB_PO_XX.py --reconciliar-datos-abiertos  (cruce con Socrata)
  python Taller2_AB_PO_XX.py --listar-upc                  (ver los 66 grupos)

  La purga crea un respaldo en data/backup/ y escribe
  data/purga_reporte.csv. La reconciliacion escribe
  data/reconciliacion_upc.csv y no modifica la base.
  La cola de reanudacion se guarda en data/ingesta_cola.json.
===============================================================================
