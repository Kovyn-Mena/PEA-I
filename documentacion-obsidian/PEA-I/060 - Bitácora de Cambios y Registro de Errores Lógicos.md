---
tipo: Bitácora de Proyecto
estado: Activo (En Vivo)
---

# 📜 Bitácora (reconstruida en nueva sede `PEA-I/documentacion-obsidian/`)

> **Directiva:** leer el cerebro antes de modificar; registrar cada cambio; documentar bugs con causa raíz.

## Sesiones 1–5 (2026-09-27)
S1 bóveda 19 notas · S2 plan 6 fases · S3 monolito único (Notas 1/8) · S4 `Taller2_KM_PO_XX.cpp` + `schema/init_db/CSVs/Makefile/run.bat/requirements/integrantes` (compila limpio) · S5 `.vscode` (g++, `-lsqlite3`, MSYS2).

## Sesión 6 — C-2 + CRUD + persistencia
`grupo_investigador` N:M + `insertarProducto` exige adscripción; CRUD grupo/investigador/producto (editar, desactivar/reactivar, eliminación física en cascada, detalles); persistencia total (`last_insert_rowid`, updates, `setEstado`, bajas, `guardarProductoConId`); menús 1–8; Undo ejecuta reversa. BUG-03: owner único.

## Sesión 7 — Fases A/B/C
`crearVacia` + `crearSistemaVacio` (Nota 10); `verTope/verFrente/tamano/listar`; `HistorialAcciones` vía `apilarConPersistencia`; opción 9 `demoTDAs()` 7×4 autolimpiable; `MODELO_FALTANTE_Punto5.md`.

## Sesión 8 — Parte 1 tablas
`truncarSeguro/celda/lineaTabla`; `listarGrupos` 12+16+22+24=74 ≤80, headers ASCII.

## Sesión 9 — Menús con ENTER + validación
`leerOpcion` (7 selecciones, `getch` solo en `pausar`); fin de `cin >>` (bug salto de línea); `leerEntero/leerTextoVal` + validadores (categoría, validación, tipo, correo, año); edición ENTER=conservar, creación obliga válido.

## Sesión 10 — Mudanza al repo
Archivos raíz perdidos al copiar el repo (papelera y disco revisados: sin copias). Recompuesto VS Code (paths a `PEA-I`, build sqlite por defecto, `cwd=PEA-I`, `c_cpp_properties` recreado). Reconstruido `.cpp` completo + `data/` + root files + cerebro en `PEA-I/documentacion-obsidian/`. Compila `-Wall -Wextra` limpio; BD verificada 3+3+4+4.

## Sesión 11 — GISICO real + sistema N-grupos (lógica intacta)

- **Archivos:** `Taller2_KM_PO_XX.py` (nuevo, ingesta), `data/grupos_upc.txt`, `data/gisico_semillas.json`, `data/snapshots/`, `pylib/` (requests/bs4/pypdf/typing_extensions vendored), `data/*.csv` regenerados, `init_db.py` (lee semillas JSON), BD fresca 1+85+10+85, opción 4 ingesta en C++.
- **Datos:** GISICO verificado vivo (`nro=00000000002099`, líder John Jairo Patiño Vanegas, cat. C): 85 integrantes (67 actuales + 18 históricos), 91 artículos (83 con autor macheado). Ejemplos UFPS fuera. `codigo_grupo=GISICO` (la ficha no publica COL; nro vive en `grupos_upc.txt`). rh `GISICO-RH-xxx` = placeholder documentado (GrupLAC no da cod_rh); único real `0000494917`.
- **E2E en BD temporal:** `--offline` 68+4+0 e idempotente; `--scrape-todos` (snapshot) 67+18+0. Bugs hallados y corregidos: colisión alias `nombre/categoria` (mapas por entidad), contadores fila vs entidad (`rowcount`), duplicados en rerun (anti-duplicado título+año+rh), snapshot por nombre flexible, años del ISSN descartados.
- **Corrupción fuente:** SCIENTI sirve � literales (irrecuperable, se conserva fiel); página es UTF-8 (latin-1 la rompía).

## Sesión 12 — Auditoría del cerebro (recordatorio de directiva del usuario)

- **Origen:** el usuario recordó la directiva (leer todo Obsidian antes de actuar; registrar cambios y errores detectados por él).
- **Acción:** lectura 19/19 notas; 8 correcciones: 010-fila 7, 012 (.py 🟡), 024 (flags reales), 030 (F3✅/F4✅), 032 (roadmap S11), 040 M-03 (mitigado), 050 (siguiente real), 052 (py ingesta ✅); 1 error corregido en 051 (Python MSYS 3.14 sin pip → `pylib/` vendored, `pip install` no aplica); Hub con BD GISICO.
- **Errores de usuario ya registrados:** tablas desordenadas (S8), menús sin ENTER + validación (BUG-05), compilación VS Code (BUG-06), ejemplos vs UPC (S11). Sin pendientes de registro.

## Sesión 13 — "No compila/no corre" (reporte del usuario)

- **Causa raíz:** el botón play ▶ regeneraba la tarea `C/C++: g++.exe compilar archivo activo` sin `-lsqlite3` y le robaba el default (3.ª recurrencia). El código estaba sano: `g++ -Wall -Wextra` limpio, `py_compile` OK, sin `pea_cpp.exe` colgados.
- **Fix durable:** `tasks.json` con build oficial por defecto + la etiqueta autogenerada pre-definida CON `-lsqlite3` (el ▶ ahora también compila). `launch.json` intacto.

## Sesión 27 — Tablas más anchas (reporte del usuario)

- **Pedido:** no se apreciaba la información (mucho `...`). Anchos nuevos: grupos 109, ventana 110, resumen 99, investigadores 91, productos 108, candidatos 109, selector 90. Compila en cero warnings. Requisito: terminal ancha.

## Sesión 26 — Tablas con estructura + 3 notas nuevas (reportes del usuario)

- **Plan A (tablas):** la causa del desorden era triple: celdas pegadas sin `|`, `celda()` medía bytes (tildes/`�` recorrían todo) y anchos incoherentes. Nuevo renderer (`anchoVisual/truncarVisual/celdaV/bordeTabla/filaTabla/tituloTabla`) + 6 salidas + candidatos + `elegirGrupo()` migrados a `+---+`/`+===+`/`| a | b |` ≤ 80. Helpers viejos retirados: `g++ -Wall -Wextra` en cero warnings.
- **Plan B (red):** notas nuevas `013` (visión sistema final), `025` (estándar de presentación), `033` (escalabilidad 1M) + hub + retoque `022`. Regla del usuario aplicada: en Obsidian también se CREA según la lógica, no solo se actualiza.

## Sesión 25 — Sin códigos a la vista + investigadores por grupo + AITICE completo (reporte del usuario)

- **Causa AITICE incompleto:** el filtro "Actual" descartaba 60 históricos (95 filas: 35 actuales + 60 históricos). Ahora se importa TODO (contador `historicos_omitidos` solo informa). BD: AITICE 94 adscripciones, total 165 investigadores / 179 adscripciones.
- **`listarGrupos` sin códigos:** numerado + nombre + líder (74→72 col). Códigos solo internos.
- **Nuevo `elegirGrupo()`:** lista numerada sin códigos, devuelve código interno; usado en ver/editar/desactivar/reactivar/eliminar grupo, destino de investigadores (crear/adscribir/eliminar) y grupo de producto nuevo.
- **Nuevo `listarInvestigadoresDeGrupo()`:** opción 1 de investigadores pide el grupo y enlista todos los suyos. Compila limpio.

## Sesión 24 — Arranque corregido (reporte del usuario, con razón)

- **Fallos:** (1) Nota 10 se mostraba ANTES de la pregunta sí/no (sin sentido); (2) pedía nro y rechazaba nombres ("aitice" → aviso).
- **Fix:** sí/no primero; Sí → `menuBuscarGrupo()` (nombre → candidatos con universidad → elegir → cargar); No → Nota 10. Sin nro a la vista. Compila limpio.

## Sesión 23 — Buscador por nombre en SCIENTI (usuario: "no es lo que yo quiero")

- **Reclamo justo:** el arranque solo ofrecía GISICO (dato ya cargado). Lo pedido: escribir el nombre → buscar en SCIENTI → verificar → si hay homónimos en varias universidades, escoger → cargar el nuevo.
- **Hallazgo:** no existe endpoint de búsqueda por nombre (400 en rutas inventadas; el form CvLAC es find-in-page). Cadena real: `busquedaGruposPorInstitucion.do` (JMesa: `all_grupos_ins_mr_=2000` de un tiro → 1.084 instituciones) → `busquedaGrupoXInstitucionGrupos.do?codInst=` (tabla id `grupos`, `grupos_mr_=500`) → nro. UPC = codInst 947 con **66 grupos** (coincide con lo dicho por el usuario).
- **Implementado:** `--indexar-instituciones/--buscar-universidad/--grupos-institucion/--buscar-grupo` (índices JSON en `data/`, formato `CAND|...`), menú C++ 7.5 buscar→listar con universidad→elegir→cargar (`--scrape-grupo` + `--universidad`). Bonus: COL real de GISICO = **COL0018706**.
- **Trampas JMesa:** sin sesión la cookie ignora el `mr_`... al revés: CON sesión lo ignora; sin sesión obedece. La tabla útil es la que tiene `id` (las envolturas contaminan). Multi-homónimo real = Parte 5 (indexar más instituciones).

## Sesión 22 — UnicodeEncodeError desde C++ (reporte del usuario, BUG-10)

- Ver BUG-10 en la tabla: `reconfigure(utf-8, replace)` en el `.py` + `set PYTHONIOENCODING=utf-8&&` en el `popen`; verificado sin la variable (exit 0).

## Sesión 21 — Verificación existencia + universidad (usuario)

- **Antes:** `scrape_grupo` importaba sin verificar; líder siempre "Por verificar"; nombre/sigla hardcodeados a GISICO.
- **Ahora:** `parse_ficha` extrae nombre real, líder real, instituciones con aval y flag `existe`. `--universidad FILTRO`: sin coincidencia → "Universidad no encontrada para este grupo (avalan: …)"; ficha inválida → "Grupo no existente"; sin filtro informa avaladoras y sigue. Sigla real del nombre (GISICO) o `G+nro`.
- **E2E:** UPC → OK con líder y avaladoras; "universidad de colombia" → no encontrada; HTML basura → no existente. C++ pide universidad opcional (ENTER = sin filtro) en arranque y 7.4. Compila limpio.

## Sesión 20 — Pregunta inicial de carga por grupo (usuario)

- **Flujo en `iniciar()`:** "Desea cargar algun grupo de investigacion de la universidad popular del cesar? (si/no)". Sí → nro (ENTER = GISICO) → `[Cargando datos...]` → scrape GrupLAC (ficha + integrantes, **sin CvLAC**, pendiente siguiente) → recarga RAM → `[Datos cargados con exito.]` → `Presione ENTER para continuar...` (`pausarEnter`) → menú. No → Nota 10 como antes.
- **Sin duplicar lógica:** opción 7.4 reutiliza `flujoCargaGrupoUPC()`. Compila `-Wall -Wextra` limpio.

## Sesión 19 — Caché oficial + matriz E2E 4 casos (aprobado por el usuario)

- **Medición:** 1 grupo = 90 archivos / 19.5 MB → 66 grupos ≈ 5,600 archivos / ~1 GB. Adoptada híbrida refinada.
- **Implementado:** `cache_fuentes` en `schema.sql` + `conectar()`; `descargar_cache()` (ETag/304 + hash-dedup + row `duplicado`); `empaquetar_grupo()` (GISICO 647 KB → 66 KB); `scrape_grupo`/`scrape_cvlac` cableados; anti-duplicado por prefijo-30 para el truncado PDF.
- **Hallazgo honesto:** SCIENTI no envía ETag/Last-Modified (verificado con HEAD) → el 304 queda implementado pero inactivo; el ahorro real hoy es hash-dedup + zips.
- **Matriz E2E en BD temporal (real intacta 1+85+10+85):** GrupLAC 67+18+0, CvLAC 26 nuevos, PDF 2, CSV 2; rerun total en ceros (idempotente incl. cruce PDF↔CSV).

## Sesión 18 — Parte 2 PDF tabular + spec Parte 5 (usuario)

- **PDF tabular:** `scripts/gen_muestra_pdf.py` genera `data/muestra_upc.pdf` (gemelo del CSV, 1 línea/fila, Helvetica latin-1). Lector en 2 niveles: coordenadas (visitor pypdf → bandas Y → header por score → ensamble por columna-0 → asignación por inicio de columna) con misma persistencia del CSV; fallback heurístico 1-producto (sigue exigiendo `--grupo/--rh`).
- **E2E en BD temporal:** muestra.pdf → 0+0+2+0+0; rerun idempotente 0+0+0+2+0. BD real intacta (1+85+10+85).
- **Lecciones:** fpdf2 `multi_cell` + subset Arial sin ToUnicode = texto irrecuperable (se usa `cell()` + Helvetica); � se sanea a latin-1 en el generador; E2E exige `wal_checkpoint` antes de copiar la BD (copiar solo el `.db` da vista vieja).
- **Spec Parte 5 recibida (pesada, después):** buscador `ciencia-war/busquedaGruposPorInstitucion.do`; ideal: el usuario escribe institución → si no existe, "universidad no encontrada"; por ahora solo UPC; **todos** los grupos divididos por sus 7 facultades (consultar link oficial).

## Sesión 29 — Columna GRUPO + filtro por grupo + limpieza de títulos (reporte del usuario)

- **Pedidos:** (1) "¿de qué grupo es?" → columna GRUPO con sigla (`etiquetaGrupo`, sin códigos) en `listarProductos` y ventana; (2) control de filtrado → opción 1 ahora pide grupo (`elegirGrupo`) y enlista con `listarProductosDeGrupo`.
- **Calidad de títulos:** el parser capturaba ": " inicial y una fila basura "Colombia, 2016,". Fix en `parse_produccion_grupolac` (strip prefijo + rechazo país-año) + `scripts/limpiar_titulos.py` (173 limpiados, 1 basura id=242 eliminada, 2 duplicados fusionados; nada referencia `id_producto` como FK). 246→243, `foreign_key_check` vacío. C++ compila limpio.

## Sesión 30 — Orden por año + causa raíz del � (reporte del usuario)

- **Orden:** `ORDER BY anio_publicacion DESC` en `cargarEnMultilista` (C++): como se inserta por cabeza, todas las vistas quedan de lo nuevo a lo viejo.
- **Causa raíz del �:** el código forzaba `r.encoding = "utf-8"` pero SCIENTI declara `iso-8859-1` (verificado: bytes `PATI\xd1O` crudos). Nuevo helper `codificacion_respuesta()` (mapea a windows-1252) en los 4 fetches; match de grupo tolerante a �; red de seguridad `sinRaros()` (�→`?`) en `celdaV`. Compila limpio.
- **Pendiente:** `scripts/migrar_encoding.py` (rescrape limpio a temporal + UPDATE in place por rh/código + fuzzy en productos + refresh semillas/CSVs/PDF).

## Sesión 28 — Parte A: productos del grupo + verPerfiles + códigos COL (aprobado por el usuario)

- **Parser producción** (`parse_produccion_grupolac` + `tipo_por_marcador` robusto al �): 244 ítems GISICO (102 Articulo, 99 Software, 23 Capitulo, 20 Libro; 399 omitidos no-modelo con conteo; 0 Patentes con parser listo). Solo autores macheados (`mapa_autores`).
- **Capitulo** como valor propio (C++ `esTipoValido` + prompt; BD sin CHECK, sin romper nada).
- **verPerfiles** (`--perfiles NRO`, conv. 22 configurable): CCRG/COL, líder, instituciones, programa + 125 indicadores en `perfiles_grupo` (sección granular `general_tN`).
- **Migración COL** (`scripts/migrar_col.py` + `resolver_codigo` al vuelo): GISICO→COL0018706, AITICE→COL0043834, GIELEHLA→COL0001351; FK OFF + `foreign_key_check` limpio; semillas/CSV migrados (solo 1ª columna, nombres intactos).
- **E2E BD real**: 246 productos (85/26/27/108), rerun 0 nuevos; `foreign_key_check` vacío. C++ compila limpio.
- **Docs**: nota nueva `034`, `023` (perfiles_grupo + COL), `041` (verPerfiles), `010` punto 2.

## Sesión 17 — Cero inventados: 85 cod_rh originales + 15 categorías (reporte del usuario)

- **Origen:** el usuario notó que solo Adith tenía código real y el resto parecía inventado — tenía razón.
- **Causa raíz (error mío):** mi parser ignoró los `<a href>` de la tabla de integrantes; GrupLAC SÍ publica el CvLAC de cada uno. Verificado: 85/85 links `cod_rh=` reales.
- **Acción:** consultados los 85 CvLAC (snapshots `cvlac_<rh>.html`): 1 Senior + 4 Asociado + 10 Junior; 70 sin fila de categoría = "No categorizado" (no reconocidos, verificado caso por caso). Semillas/CSVs/BD regenerados sin placeholders (`por_verificar` = 0). `parse_integrantes` ahora captura el href; validador C++ acepta "No categorizado".
- **Nota:** PDFs 957 listan por documento (inútiles sin documentos); la vía correcta era el href, no el PDF.

## Sesión 16 — Punto 7: CvLAC real (Parte 1, aprobado por el usuario)

- **Antes:** `--scrape-url` con `cod_rh=` era stub (avisaba y no extraía).
- **Ahora:** `parse_cvlac()` (nombre, categoría, formación reportada, correo si aparece, artículos con título+año) + `scrape_cvlac()` (upsert con rh real, snapshot, UPDATE sin borrar correo, productos al grupo `--grupo` o a grupos ya adscritos). `--scrape-url` deriva a GrupLAC o CvLAC según `nro=`/`cod_rh=`.
- **E2E en BD temporal:** `cod_rh=0000494917` por red → Asociado + 26 artículos nuevos a GISICO; rerun idempotente (0+26). BD real intacta.
- **Límite:** libros/software/patentes del CvLAC no se extraen aún (solo artículos).

## Sesión 15 — Parte 2 tablas (reporte del usuario: "muy desordenado")

- **Causa:** Parte 1 solo migró `listarGrupos`; las otras 4 salidas seguían con `setw` + tildes/emoji + campos sin tope.
- **Fix:** `listarProductosPorVentanaAnios` (70) + `listarProductos` (70) + `listarInvestigadores` (74, con header por grupo y columna ESTADO) + `generarResumenEstadistico` (70, sin 📍, etiquetas fijas) migradas a `celda()/lineaTabla()`. Verificado: 0 `setw`, 0 emojis, 0 tildes en zonas tabulares; `g++ -Wall -Wextra` limpio.

## Sesión 14 — Categorías verificadas (observación del usuario)

- **Origen:** el usuario advirtió que "Por verificar" no aplica a todos y exigió consultar.
- **Consulta real:** CvLAC no tiene búsqueda por nombre (el form es find-in-page JS; `jsp/index` y `buscarInvestigadores.jsp` → 404); PDFs 957/894/737 listan por N.º de documento (inútil sin documentos); sin roster UPC publicado. **Único verificable:** Adith Bismarck Pérez Orozco = **Investigador Asociado (I)** (CvLAC `cod_rh=0000494917` en vivo).
- **Aplicado:** `CAT_VERIFICADAS` en `emit_gisico.py`, semillas/CSVs/BD regenerados (Adith=Asociado; 84 restantes "Por verificar" = consultado-sin-fuente, no inventado).
- **Incidente:** `pea_investigacion.db` bloqueado por otro proceso (no era `pea_cpp.exe`; sospecha: extensión SQLite Viewer de VS Code) → reseed in-place (DELETE+re-semilla) en vez de borrar el archivo.

---

## 🐛 Bugs
| ID | Bug | Estado |
|:--:|-----|:------:|
| BUG-01 | `SQLITE_BUSY` | mitigado (WAL+timeout) |
| BUG-02 | Scraping frágil | pendiente py robusto |
| BUG-03 | double-free/leaks | mitigado (owner único) |
| BUG-04 | Nomenclatura 2 vs 3 iniciales | pendiente docente |
| BUG-05 (nuevo) | Menús avanzaban con `getch` + `cin>>getline` tragaba ENTER | **corregido S9** |
| BUG-06 (nuevo) | `.vscode` apuntaba a ruta inexistente + build sin `-lsqlite3` | **corregido S10** |
| BUG-07 (nuevo, detectado por el usuario) | "No compila/no corre": el botón play ▶ regenera la tarea `cppbuild` sin `-lsqlite3` y le quita el default a la buena (3 recurrencias) | **corregido S13**: etiqueta autogenerada pre-definida CON `-lsqlite3`; build oficial por defecto; verificado `g++` limpio + `py_compile` OK + sin procesos colgados |
| BUG-09 (nuevo, detectado por el usuario) | "Solo corre con Ctrl+Shift+B": el ▶ compila a `Taller2_KM_PO_XX.exe` (otro nombre) y lo deja corriendo invisible → `Permission denied` en cada rebuild ("no compila") | **corregido S15**: proceso fantasma (PID 21556) terminado, rebuild OK; regla: cerrar la consola del programa antes de recompilar |
| BUG-10 (nuevo, detectado por el usuario) | `UnicodeEncodeError` en `--scrape-grupo` desde C++: la tubería hereda consola cp1252 y los � de SCIENTI tumbaban el print final (exit 1). En mis pruebas no salía porque siempre fijaba `PYTHONIOENCODING=utf-8` | **corregido S22**: `sys.stdout/stderr.reconfigure(utf-8, replace)` en el `.py` + `set PYTHONIOENCODING=utf-8&&` en el `popen` de C++; verificado sin la variable (exit 0) |
| BUG-08 (nuevo) | `pea_investigacion.db` bloqueado por otro proceso (no `pea_cpp.exe`; sospecha SQLite Viewer) impide borrar el archivo | workaround S14: reseed in-place; **recomendación: cerrar la pestaña del .db en VS Code antes de re-sembrar** |
