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

## Sesión 31 — migrar_encoding.py pendiente S30 (ejecutado)

- **Archivo:** `scripts/migrar_encoding.py` (nuevo): rescrape limpio a temporal con `codificacion_respuesta` + UPDATE in place por rh/código + fuzzy en productos (umbral 0.82; fallback coautoría grupo+anio 0.90, sin tocar rh) + refresh `gisico_semillas.json`/CSVs + backup `.bak-*` + `foreign_key_check`.
- **Nros:** `00000000002099` GISICO + `00000000002668` AITICE + `00000000003639` GIELEHLA (deducidos de `snapshots/gruplac_*.html`).
- **Resultado BD real:** antes 1 líder + 56 inv + 132 prod con � → después 0 + 0 + 4. Investigadores 56/56, grupos 1/1 (GIELEHLA `Araújo`), productos 128/132 (118 directos + 10 por coautoría).
- **Restan 4 irrecuperables** (ids 23,24,25,26 GISICO, sin contraparte limpia en GrupLAC fresco ni en CvLAC de sus 10 rh; scores 0.21–0.35, ej. `Investigaci?n` suelto): se dejan intactos y documentados, no se borran. `g++ -Wall -Wextra` limpio; `FK check` OK.
- **Fase CvLAC probada:** 10 rh con raro rescrapeados en vivo (0 artículos nuevos) → confirma que esos 4 no son CvLAC-origen sino artefactos del parseo viejo.

## Sesión 32 — "Grupo ya existente" + zips únicos (reporte del usuario)

- **Reclamo justo:** cargar GISICO 2 veces generaba 2.º zip (`grupo_GISICO.zip` + `grupo_COL0018706.zip`; igual en AITICE/GIELEHLA). Causa: zip nombrado por `codigo` + código que migró de sigla a COL + `scrape_grupo` que seguía tras `existente` + C++ sin pre-chequeo.
- **Fix:** `existe_grupo_en_bd()` offline (índice/snapshot/nombre, tolerante a �) al inicio de `scrape_grupo` → `grupo ya existente [COL] ... zip=...` sin red; `empaquetar_grupo()` reutiliza zip vigente; `CODIGOS_LEGACY` + `limpiar_zips_huerfanos()` (auto al final de cada scrape); flags `--forzar/--existe-grupo/--limpiar-zips`; C++ `flujoCargaGrupoUPC()` pre-chequea con `salidaPython()` y avisa sin scrapear.
- **Verificado:** `--existe-grupo 2099` y `--scrape-grupo 2099` → ya existente, 0 red; `zip/` de 6 a 3 COL; `py_compile` + `g++ -Wall -Wextra` limpios.
- **Docs (regla de oro):** nota nueva `035`, `024` (contrato CLI S32).

## Sesión 33 — Mensaje "ya existente" más claro (segundo reporte del usuario)

- **Reclamo justo:** el aviso funcionaba pero confundía — Python decía
  "ya existente" y C++ remataba "[Datos cargados con exito.]" sin haber
  cargado nada; además `menuBuscarGrupo()` (carga con `--universidad`)
  ni pasaba por el pre-chequeo.
- **Fix:** Python avisa en 2 líneas (`CODIGO/GRUPO/ZIP` + `No se descargo
  nada nuevo...`); C++ helper `cargarGrupoDesdeSCIENTI()` en ambos flujos:
  reenvía `[PYTHON]`, y ante duplicado cierra con `[AVISO] Este grupo ya
  estaba cargado... Todo sigue igual.` sin recarga prometida.
- **Verificado:** `--scrape-grupo 2099 --universidad ...` → aviso, 0 red,
  `zip/` sigue en 3; `g++ -Wall -Wextra` limpio.

## Sesión 34 — Submenú tras búsqueda sin carga (reporte del usuario, grave)

- **Error:** decir sí en el arranque + buscar un grupo ya existente (o
  cancelar/fallar la búsqueda) entraba al menú principal con la RAM vacía
  en automático, sin datos ni aviso. Agravado por S33 (el helper no
  recargaba ante duplicado) + `iniciar()` sin guardián.
- **Fix (idea del usuario, misma lógica del No):** `menuBuscarGrupo()`
  retorna `bool`; `iniciar()` envuelto en bucle — si no hubo carga nueva,
  submenú espejo del No: 1 volver a buscar (repite el si/no inicial),
  2 precargar SQLite, 3 sin datos explícito. El vacío solo entra por
  elección consciente (opción 3 o Nota 10-2), nunca en automático.
  Menú 7 sin cambios (RAM ya cargada: aviso y se conserva).
- **Verificado:** `g++ -Wall -Wextra` limpio; test interactivo pendiente
  (el binario usa `_getch`, no admite stdin por tubería).

## Sesión 35 — Producción completa por tipos (reporte del usuario)

- **Pedido:** la ficha GrupLAC trae miembros + productos por tipos; al cargar un grupo deben entrar ambos. Brecha: el parser solo cubría biblio (~146/450 en GIELEHLA); eventos/tesis/consultorías/informes/cursos/jurados se perdían (~2/3) y encima `1. X:` con punto simple era invisible al regex.
- **Fix Python:** parser consciente de sección (6 secciones, resuelve `Otro:`/`Taller:`) + 11 tipos propios (`Evento/Tesis/Consultoria/Informe/CursoCorto/Jurado/Contenido/Compilacion/Regulacion`, todos ≤11 col) + año `desde AAAA` + autoría por rol (Tutor(es)/Cotutor(es) → Tesis 0→50 en GIELEHLA). Sin tocar esquema (VARCHAR sin CHECK). Decisión usuario: estricto, lo sin autor no se guarda.
- **Fix C++ (opción B):** `esTipoValido()` 15 valores + prompt; TIPO 11→12 en 3 tablas; pie por tipo en `listarProductosDeGrupo()`; `[tipo]` en `verDetalleGrupo()`. `g++ -Wall -Wextra` limpio.
- **Backfill `--forzar` 3 grupos:** 248→**1161 productos** (Jurado 257, Articulo 247, Software 195, Tesis 140, Capitulo 118, CursoCorto 106, Libro 97, Compilacion 1); Evento/Informe/Consultoria/Contenido/Regulacion en 0 (ficha sin persona; ~610 sin_autor reportados). `foreign_key_check` vacío; `zip/` intacto en 3 COL.
- **Docs (regla de oro):** `034` reescrita (tabla 15 tipos), `010` p.2, `025` (TIPO 12 + pie), Hub (BD actual + todas las notas enlazadas), `035` con links a `034`/`024`.

## Sesión 36 — Chulito GrupLAC → Validado (pregunta del usuario)
- **Pregunta:** el ítem 39 trae chulito — es `chulo_1.jpg` (187 en GIELEHLA vs 185 `chulo_0`): **avalado MinCiencias última convocatoria**, justo el campo `estado_validacion` que dejábamos todo en `Pendiente`.
- **Fix:** `mapa_chulos()` por `<tr>` (img en el `<td>` previo) con clave (marcador, título, año — el año evita falsos por eventos homónimos de años distintos) + `validacion` en el dict + `guardar_producto()` actualiza `Pendiente→Validado` en re-scrape (retorno `actualizado`, sin duplicar) + contador `validados=` en el reporte. De paso: helper `_titulo_bloque()` (nunca toma la línea `N. Marcador:` como título) y `_anio_bloque()` compartidos (BD verificada: 0 títulos-marcador).
- **Backfill `--forzar` 3 grupos:** 0 nuevos (idempotente) + **307 a Validado** (146 Articulo, 75 Software, 40 Tesis, 26 Capitulo, 20 Libro); 854 siguen `Pendiente`. `foreign_key_check` vacío. Sin cambios C++ (columna VALID 11 ya cabe).

## Sesión 37 — Hoja de vida CvLAC por integrante (pedido del usuario)
- **Pedido:** al cargar un grupo, descargar también lo individual de cada integrante (ej. CvLAC `cod_rh=0000447650`, Carmen Araújo): Par evaluador, categoría, citaciones, nacionalidad, sexo, Scholar/ORCID, formación, experiencia, áreas, idiomas.
- **Fix Python:** `parse_hoja_vida()` (etiquetas + secciones, sección más larga gana al menú duplicado) + tabla nueva `perfil_investigador` 1:1 (FK cascada, en `schema.sql` + `conectar()`, sin tocar lo existente) + `scrape_cvlac()` la guarda (REPLACE) + `scrape_grupo(..., con_cvlac=True)` la descarga por cada rh (con `commit` previo, nunca tumba la carga) + flag `--sin-cvlac` + blindaje S31 (jamás pisar limpio con �) + `migrar_encoding` con `con_cvlac=False`.
- **Fix C++:** `GestorSQLite::verPerfilInvestigador()` (lee directo de SQLite, la RAM sigue con TDAs puros) + opción investigadores-2 la muestra tras el detalle.
- **Incidente y reparación:** los snapshots CvLAC viejos (era S30, con �) re-ensuciaron 21 nombres + 133 títulos `Artículo`; blindaje + `migrar_encoding` (nombres 21→0) + borrado quirúrgico de `Artículo` con � (133, re-derivables) + snapshots sucios a `bak-sucio-s30/` + red limpia.
- **Backfill `--forzar` 3 grupos:** **236/236 perfiles** (0 �; 25 par=Sí, 28 Scholar, 38 ORCID), productos 1161→1755 (artículos CvLAC limpios), nombres 0 �, `foreign_key_check` vacío.
- **Refinamiento 2 (pedido del usuario):** productos basura en el detalle (`Publicado en revista especializada:` sin título, duplicados por mayúsculas/puntuación) + CV sin header de redes + sin topes + palabras pegadas + idiomas frágil.
  - Parser blindado (`_es_titulo_marcador()`); BD: 159 marker-titles + 3 `Revisión (Survey):` + 64 duplicados borrados con backup (1755→1532; se prefiere limpio→Validado→menor id; FK vacío).
  - CV estilo currículo final: header REDES SOCIALES E IDENTIFICADORES, **flujo de muestra** (solo secciones con datos; topes áreas 300 / formación 5 viñetas o 1200 / complementaria 600 / experiencia 1500 con `(...)`), `espaciar()` (`Septiembrede2007`→`Septiembre de 2007`, nunca URLs), `truncarVisual()` en cortes, idiomas con fallback sin encabezados. Correo vacío → `No`; Nacionalidad/Sexo en líneas propias.
  - `py_compile` + `g++ -Wall -Wextra` limpios; parse sin regresión (563/495/675).
- **Orden CV (pedido del usuario):** investigador arriba → banner HOJA DE VIDA → adscripciones/productos → formulario (`verCabeceraInvestigador` + `verCuerpoInvestigador`; `verDetalleInvestigador` los reutiliza).
- **Datos básicos a DATOS PERSONALES (pedido del usuario):** Correo/Categoría/CvLAC salen del encabezado `===` y abren la sección con etiquetas alineadas (`etiquetaCV()`); correo vacío → `No`.
- **CV sin productos (pedido del usuario, dos veces):** la hoja de vida no lista productos ni adscripciones (eso vive en las vistas del grupo); solo currículo personal y formación.
- **Incidente (causa del "todo sigue igual"):** el usuario probaba con una instancia vieja aún corriendo (`Taller2_KM_PO_XX.exe` bloqueaba la copia al recompilar) — regla: cerrar TODO antes de probar; ambos exes se sincronizan al mismo binario.

## Sesión 38 — Salir Sí/No + detalle sin volcado + CvLAC paralelo + snapshots por grupo (4 pedidos)

- **1. Salir con guardar (visión 013):** `iniciar()` crea `pea_investigacion.db.bak-sesion` (con WAL checkpoint); opción `0` pregunta 1=Sí (conserva) / 2=No (`descartarSesion()`: restaura backup + borra `-wal`/`-shm` + snapshots/zips más nuevos que el backup). Sin tocar TDAs ni ingesta. `.gitignore` ignora `*.bak-sesion`.
- **2. Detalle sin volcado:** `verDetalleGrupo()` ya no lista cientos de productos: conteo total + por tipo + top 10 recientes (la cadena viene nueva-primero, S30) + aviso al listado completo. Punto 3 intacto.
- **3. Velocidad (12 hilos, lógica intacta):** `ThreadPoolExecutor(12)` por ficha CvLAC (cada una con conexión propia; parse/guardado/reglas iguales) + `quiet=True` con progreso `CvLAC i/N` + flag `--hilos` (1=secuencial). Medido: 72 frescas en 24s (~5 min secuencial). De paso: `guardar_producto()` con anti-duplicado normalizado (los 6 gemelos que volvían ya no entran; idempotencia verificada productos=0).
- **4. Orden snapshots:** `data/snapshots/<CODIGO>/` (478 archivos migrados con `--organizar-snapshots`); `zip/` intacto; rutas recursivas en `_snapshot_para_nro/_snapshot_cvlac/empaquetar_grupo`; `cache_fuentes` actualizada al mover; `migrar_encoding` no afectado.
- **Estado:** 4 grupos, 359 invs, 359 perfiles, 2352 productos, 2 � (irrecuperables S31), FK vacío. `py_compile` + `g++` limpios.

## Sesión 39 — El No no borraba + sesión temporal a prueba de X (reporte grave del usuario)

- **Reporte:** EIDGA cargado + No al salir, pero quedó guardado. Evidencia: backup 4:58:42pm pre-EIDGA existía pero el restore nunca corrió (cierre con X, binario previo o Sí marcado).
- **Limpieza inmediata:** EIDGA (`COL0240762`) eliminado con cascade seguro (backup previo): 116 productos, 182 perfiles-grupo, 26 invs exclusivos + hv, 29 filas caché, 27 snapshots + zip; el compartido se conserva. FK vacío; quedan 4 grupos.
- **Blindaje real (a prueba de X):** la sesión corre sobre `data/pea_sesion.db` (copia al arrancar; Python vía `--db` automático en `conDB()`); Sí la promueve a real (+`.bak-previa`), No la borra + limpia snapshots nuevos. Cerrar con X = la real intacta por construcción. `.gitignore`: `*.db-wal/shm`, `*.bak-previa`.
- **Verificado:** `g++` + `py_compile` limpios (test interactivo lo hace el usuario: cargar → salir-No → debe quedar igual).

## Sesión 40 — Red de Colaboración, Modelo 2024 (5/10 años), Logo Oficial UPC, Arreglo de Recorte CSS y Ventana Previa de Login

- **Archivos modificados:** `src/cpp/include/VisualizadorGrafico.h`, `src/cpp/include/ConsolaApp.h`, `src/cpp/include/Multilista.h`, `src/cpp/main.cpp`, `src/python/gui.py`, `src/python/console.py`, `src/python/multilista.py`, `src/python/report_generator.py`, `Taller2_AB_PO_XX.py`, `iniciar.bat`, `scripts/package_zip.py`.
- **1. Ventana Diferenciada Modelo MinCiencias 2024 (5/10 años):** Incorporada en C++ (`filtrarProductosPorVentanaModelo2024`) y Python (`filtrar_productos_modelo_2024`), aplicando 10 años a Artículos A1/A2/B/C, Libros (`LIB`), Capítulos (`CAP`) y Patentes (`PAT`), y 5 años al resto.
- **2. Red de Colaboración Científica y Popover Pila LIFO:** Pestaña interactiva Canvas 2D con métricas de centralidad y exportación PNG, más Popover flotante de Pila LIFO en tiempo real con atajo global `Ctrl+Z`.
- **3. Exportación CSV Excel (UTF-8 BOM) y Auditoría `--verify`:** Descarga `.csv` en un clic desde cualquier tabla del portal web y comando `--verify` (`make verify`) que comprueba 100% de equivalencia entre C++17 y Python.
- **4. Identidad Visual UPC y Limpieza de `.bat`:** Unificados los scripts de Windows en un único `iniciar.bat` e incorporado el escudo oficial de la Universidad Popular del Cesar (`data/logo_upc.png`) en Portal Web (Base64 autónomo), GUI Tkinter, PDFs y Word.
- **5. Corrección de Recorte CSS y Ventana Previa de Login (`usuario` / `contraseña`):**
  - **Causa raíz del recorte visual:** El `header` con `position: sticky` se superponía al hacer scroll sobre `.portal-layout` (que tenía altura fija `calc(100vh - 210px)`), y `.data-table-container` tenía `overflow: hidden` junto con `grid-template-columns: 360px 1fr`, cortando el botón `Desactivar` a la derecha.
  - **Solución:** `header` cambiado a flujo normal (`position: relative`), grilla ajustada a `290px minmax(0, 1fr)` con `overflow-x: auto` en contenedores de tabla y celdas compactas.
  - **Login previo:** Añadida ventana previa de validación de usuario y contraseña (`admin` / `1234`) en el Portal Web (`#login-overlay` + botón `Salir`), en la GUI nativa Tkinter (`Toplevel` modal previo) y en las consolas C++ y Python.

## Sesión 41 — Eliminación Total de Tkinter y Consolidación del Flujo Gráfico (Auditoría Técnica)

- **Archivos modificados:** `src/python/gui.py`, `src/python/console.py`, `iniciar.bat`, `README_WINDOWS.txt`, `docs/guia-desarrollo-equipo.md`, `documentacion-obsidian/PEA-I/030 - Mapa de Fases (Fase 0 a Fase 6B).md`, `documentacion-obsidian/PEA-I/060 - Bitácora de Cambios y Registro de Errores Lógicos.md`.
- **Causa raíz del problema:** La implementación de Tkinter requería dependencias nativas del sistema operativo (`libtk`, servidor X11/Wayland o drivers de ventana de escritorio), lo que provocaba bloqueos silenciosos o excepciones al ejecutar en terminales de desarrollo, entornos headless y diversas plataformas. Además, duplicaba innecesariamente la lógica visual que ya resuelve con mayor sofisticación el Portal Web interactivo y los gráficos de alta resolución con Matplotlib (backend `Agg`).
- **Solución implementada:**
  1. **Purga completa de Tkinter en `src/python/gui.py`:** Eliminado el método `lanzar_tkinter_desktop()` (~275 líneas de widgets de escritorio frágiles) y la bifurcación condicional en `iniciar()`. Ahora `DashboardApp.iniciar()` compila directamente los gráficos estadísticos institucionales con Matplotlib y genera el Portal HTML5 autónomo (`dist/dashboard_python.html`) con las 3 vistas obligatorias (Grupos, Investigadores, Productos) y enlaces a reportes PDF.
  2. **Actualización de menús y lanzadores:** En `src/python/console.py`, `iniciar.bat` y `README_WINDOWS.txt`, se renombró la opción 2 a *Dashboard Gráfico Interactivo Python (Matplotlib + 3 Vistas --gui)*, garantizando que el usuario y el docente experimenten una apertura instantánea y sin errores en su navegador predeterminado.
  3. **Verificación de calidad:** Ejecutados exitosamente `make test` (pruebas de TDAs C++ y Python sin regresiones) y `python3 Taller2_AB_PO_XX.py --gui`.

## Sesión 42 — Corrección Integral de Auditorías Técnicas y Unificación ScienTI (Fases 1, 2 y 3)

- **Archivos modificados:** `src/python/core/busqueda_scienti.py`, `src/python/core/ingesta.py`, `src/python/console.py`, `src/cpp/include/ConsolaApp.h`, `src/cpp/include/GestorInterop.h`, `Taller2_AB_PO_XX.py`, `src/python/main.py`, `iniciar.bat`, `scripts/package_zip.py`, `documentacion-obsidian/PEA-I/060 - Bitácora de Cambios y Registro de Errores Lógicos.md`.
- **Causa raíz de los problemas:**
  1. **Falla tipográfica y ausencia de búsquedas institucionales:** El Menú de Ingesta (opción 8) en Python arrojaba `TypeError: leer_linea() got an unexpected keyword argument 'permite_vacio'` debido al parámetro incorrecto, y no exponía las búsquedas de universidades/grupos ni el catálogo UPC de 66 grupos (`data/indice_instituciones.json`, `data/indice_grupos.json`, `data/grupos_upc.txt`).
  2. **Desarticulación GrupLAC y CvLAC con datos sintéticos:** El scraper procesaba grupos de manera aislada sin concurrencia para los CvLAC de sus miembros, y recurría a métodos ficticios (`_fallback_gruplac`, `_fallback_cvlac`) que contaminaban la base de datos con registros falsos (`FALLBACK-001`, `Paper Hipercubo ficticio`).
  3. **Deshacer LIFO incompleto:** La función de Deshacer solo manejaba `DESACTIVAR` y `CREAR`. Ante `MODIFICAR` no restauraba los valores previos de los campos, y ante `ELIMINAR` no reinsertaba el nodo ortogonalmente en la Multilista ni sincronizaba la base de datos SQLite.
  4. **IDs no deterministas en PDFs:** La función nativa `hash()` de Python dependía de la semilla del proceso, generando identificadores variables e inestables entre ejecuciones.
- **Soluciones implementadas:**
  1. **Fase 1 (Búsquedas ScienTI y Reestructuración Menú 8):**
     - Módulo `src/python/core/busqueda_scienti.py` con resolución offline y online de universidades y grupos UPC.
     - Menú 8 reestructurado en 9 subopciones claras tanto en Python (`console.py`) como en C++ (`ConsolaApp.h` vía `GestorInterop`).
     - CLI enriquecido en `Taller2_AB_PO_XX.py` con `--buscar-universidad`, `--buscar-grupo`, `--listar-upc`, `--scrape-grupo`.
  2. **Fase 2 (Pipeline Unificado GrupLAC + CvLAC y Supresión de Datos Sintéticos):**
     - En `src/python/core/ingesta.py`, la extracción de GrupLAC dispara inmediatamente `ThreadPoolExecutor(12)` para capturar las hojas de vida CvLAC de todos los integrantes y poblar `perfil_investigador`.
     - Eliminados definitivamente `_fallback_gruplac` y `_fallback_cvlac`. La base de datos `data/pea_investigacion.db` contiene cero registros sintéticos.
     - Atribución estricta de autoría con fallback al líder institucional para productos huérfanos.
     - Generación determinista de IDs de productos en PDFs con SHA-256 truncado a 8 caracteres hexadecimales.
  3. **Fase 3 (Deshacer LIFO Real en C++ y Python):**
     - En `src/python/console.py` y `src/cpp/include/ConsolaApp.h`, captura exhaustiva de atributos en `detalle_previo` (`clave=valor;...`) antes de modificar o eliminar grupos, investigadores o productos.
     - En `ejecutar_deshacer` / `ejecutarDeshacer`, parseo atómico del estado previo, restauración de campos en RAM (`MODIFICAR`), re-inserción ortogonal de nodos (`ELIMINAR`) y sincronización inmediata con SQLite.
  4. **Fase 4 (Blindaje de Persistencia, Verificación Cruzada y Rendimiento):**
     - En `src/cpp/include/GestorSQLite.h` y `src/cpp/test_sqlite.cpp`, implementada la función `columnaTextoSegura()` para evitar lecturas de punteros nulos ante campos vacíos en SQLite.
     - Protegido `guardarEnBD()` con `BEGIN IMMEDIATE TRANSACTION` y `ROLLBACK` ante errores de preparación.
     - En `src/python/core/verificacion_cruzada.py`, eliminado el falso positivo `v_cpp = v_py if not cpp_stats else -2`. Si el binario C++ no existe, se compila en caliente con `make`, y si no se encuentra disponible, se reporta falla estricta sin declarar equivalencias ficticias.
     - En `src/python/gui.py`, eliminada la pre-generación síncrona bloqueante de 62 PDFs en el arranque del dashboard.
  5. **Fase 5 (Unificación de Catálogo 2024 e IPP):**
     - En `src/python/core/reporte_pdf.py`, filtrado estricto `activo = 1` en integrantes y productos para que el informe no contabilice registros eliminados lógicamente.
     - Estandarizada la ponderación del IPP al 100% para productos validados y 50% (`global_weight // 2`) para pendientes en C++, Python, GUI y PDF.
  6. **Fase 6 (Paridad de Entrypoints, Empaquetado y Verificación Final):**
     - Sincronizados los flags de línea de comandos (`--stats-json`, `--gen`, `--gui`) en `Taller2_AB_PO_XX.cpp` para paridad completa con `src/cpp/main.cpp`.
     - Añadida la opción `[7]` a `iniciar.bat` para empaquetar la entrega final en ZIP con un solo clic.
     - Regenerado el archivo formal `Taller2_EstructuraDatos_GrupoXX.zip` mediante `scripts/package_zip.py`.
- **Verificación:**
  - `make clean && make` compiló en C++17 con `-Wall -Wextra` y cero advertencias.
  - `make test` ejecutó exitosamente el 100% de las pruebas unitarias de TDAs en C++ y Python.
  - `make verify` ejecutó la verificación cruzada real con 100% de paridad en todas las métricas de las Multilistas C++ y Python.

### Sesión 43 (13/10/2026) — Auditoría de Limpieza, Supresión de Activos Huérfanos y Optimización de Empaque ZIP
- **Objetivo:** Auditar integralmente el repositorio para eliminar archivos duplicados o huérfanos, simplificar el flujo operativo y evitar empaquetados inflados o desordenados (evitando la proliferación de archivos `.bat` rotos o scripts no funcionales).
- **Archivos modificados:** `data/catalog_2024.json` (eliminado), `data/logo_upc_icon.png` (eliminado), `data/logo_upc_transparent.png` (eliminado), `scripts/package_zip.py`, `Documentacion_Tecnica_GrupoXX.docx`, `Taller2_EstructuraDatos_GrupoXX.zip`, `documentacion-obsidian/PEA-I/060 - Bitácora de Cambios y Registro de Errores Lógicos.md`.
- **Causa raíz de los problemas:**
  1. **Activos duplicados y huérfanos en `data/`:** `data/catalog_2024.json` era un clon byte a byte (46 KB) de `data/catalogo_minciencias_2024.json` jamás invocado por el código fuente. Igualmente, existían dos imágenes `data/logo_upc_icon.png` y `data/logo_upc_transparent.png` que no formaban parte de la tubería gráfica ni de generación de reportes (el sistema emplea exclusivamente `data/logo_upc.png` y `dist/logo_upc.png`).
  2. **Sobrecarga de PDFs y ZIPs anidados en el empaquetado formal:** `scripts/package_zip.py` recorría el directorio `reportes/` incluyendo indiscriminadamente los 62 PDFs generados dinámicamente en ejecuciones previas, además de empaquetar archivos ZIP anidados de `data/snapshots/zip/`, inflando el archivo `Taller2_EstructuraDatos_GrupoXX.zip` hasta 8.1 MB.
  3. **Verificación de flujos y archivos de arranque:** Históricamente existían múltiples scripts `.bat` dispersos e inestables; se requería auditar que el lanzador `iniciar.bat` fuera único, robusto y que no existieran dependencias ni llamadas huérfanas a tecnologías deprecadas (como Tkinter).
- **Soluciones implementadas:**
  1. **Depuración de activos innecesarios:** Eliminación de los archivos huérfanos `data/catalog_2024.json`, `data/logo_upc_icon.png` y `data/logo_upc_transparent.png` mediante `git rm`.
  2. **Reglas estrictas de empaquetado:** En `scripts/package_zip.py`, se incorporó `.zip` y `data/snapshots/zip` a `SKIP_PATTERNS`, y se restringió la inclusión en `reportes/` exclusivamente a los 2 informes canónicos del taller (`Informe_GrupLAC_COL0002099.pdf` e `Informe_GrupLAC_COL0043834.pdf`). El tamaño del archivo ZIP de entrega final se redujo a 5.1 MB.
  3. **Validación de flujo limpio:** Se comprobó que solo existe un único lanzador `iniciar.bat` con detección inteligente de Python/MinGW y 7 opciones claramente delimitadas; cero scripts `.bat` o `.cmd` huérfanos; cero residuos de código Tkinter en el repositorio.
- **Verificación:**
  - `make clean && make` compiló sin advertencias en C++17.
  - `make test` superó el 100% de pruebas unitarias en C++ y Python.
  - `make verify` ratificó el 100% de paridad e invariantes estructurales.
  - `python3 scripts/package_zip.py` empaquetó el entregable limpio de 5.1 MB sin PDFs temporales ni zips redundantes.

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
| BUG-10 (nuevo, detectado por el usuario) | `UnicodeEncodeError` en `--scrape-grupo` desde C++: la tubería hereda consola cp1252 y los  de SCIENTI tumbaban el print final (exit 1). En mis pruebas no salía porque siempre fijaba `PYTHONIOENCODING=utf-8` | **corregido S22**: `sys.stdout/stderr.reconfigure(utf-8, replace)` en el `.py` + `set PYTHONIOENCODING=utf-8&&` en el `popen` de C++; verificado sin la variable (exit 0) |
| BUG-08 (nuevo) | `pea_investigacion.db` bloqueado por otro proceso (no `pea_cpp.exe`; sospecha SQLite Viewer) impide borrar el archivo | workaround S14: reseed in-place; **recomendación: cerrar la pestaña del .db en VS Code antes de re-sembrar** |
| BUG-11 (nuevo, detectado por el usuario) | Doble carga GISICO generaba 2.º zip (`grupo_GISICO.zip` + `grupo_COL0018706.zip`): zip por código + código migrado sigla→COL + scrape que seguía tras `existente` + C++ sin pre-chequeo | **corregido S32**: pre-chequeo offline `existe_grupo_en_bd()` → `grupo ya existente`, zip reutilizado, legacy limpiados, flags `--forzar/--existe-grupo/--limpiar-zips`, C++ avisa antes del `popen` |
| BUG-12 (nuevo, detectado por el usuario, grave) | Arranque con sí + grupo ya existente (o búsqueda cancelada/fallida) entraba al menú sin datos en automático: `iniciar()` sin guardián + S33 sin recarga | **corregido S34**: `menuBuscarGrupo()` retorna bool + `iniciar()` en bucle con submenú 1-buscar otro (repite si/no) / 2-precargar SQLite / 3-sin datos explícito |
| BUG-13 (nuevo, detectado por el usuario, grave) | Salir con No no borraba (EIDGA quedó guardado): el restore backup nunca corrió en esa sesión | **corregido S39**: sesión sobre BD temporal (`pea_sesion.db`, Python con `--db` automático); Sí promueve, No elimina; X-close seguro por construcción |
| BUG-14 (nuevo, detectado por el usuario) | Recorte superior e izquierdo/derecho en tablas del Portal Web (`Desacti...` cortado y `header` sticky tapando buscador al hacer scroll) | **corregido S40**: `header` en flujo relativo, `.portal-layout` con `290px minmax(0, 1fr)` y `.data-table-container` con `overflow-x: auto` |
| BUG-15 (nuevo, auditoría) | Interfaz nativa Tkinter generaba cuelgues, fallos por dependencias (`_tkinter`) y problemas en entornos sin display | **corregido S41**: purga completa de Tkinter; adopción exclusiva del flujo Matplotlib (Agg) + Dashboard HTML5 interactivo multiplataforma |
| BUG-16 (nuevo, auditoría) | Ingesta Menú 8 arrojaba `TypeError: leer_linea() got an unexpected keyword argument 'permite_vacio'` y carecía de búsqueda ScienTI | **corregido S42**: corregido tipográfico `permitir_vacio` e integrado módulo `busqueda_scienti.py` con 9 opciones en Python y C++ |
| BUG-17 (nuevo, auditoría) | GrupLAC y CvLAC desarticulados con presencia de funciones de datos sintéticos `_fallback_gruplac` y `_fallback_cvlac` | **corregido S42**: unificación con `ThreadPoolExecutor(12)`, eliminación total de sintéticos y atribución institucional estricta |
| BUG-18 (nuevo, auditoría) | Deshacer (TDA Pila - LIFO) ignoraba valores previos de `MODIFICAR` y no reinsertaba registros en `ELIMINAR` | **corregido S42**: serialización en `detalle_previo`, restauración completa en memoria RAM y sincronización atómica con SQLite |
| BUG-19 (nuevo, auditoría) | IDs de productos en PDFs generados con `hash()` no-determinista | **corregido S42**: cálculo criptográfico determinista con SHA-256 de 8 caracteres hexadecimales |
| BUG-20 (nuevo, auditoría) | Punteros inseguros `reinterpret_cast<const char*>(sqlite3_column_text)` sin validación NULL en C++ | **corregido S42**: función `columnaTextoSegura()` y transacciones con `BEGIN IMMEDIATE` + `ROLLBACK` |
| BUG-21 (nuevo, auditoría) | Verificación cruzada declaraba falsamente "100% equivalencia" ante binario C++ inexistente | **corregido S42**: compilación en caliente con `make` y reporte estricto de discrepancias |
| BUG-22 (nuevo, auditoría) | Pre-generación bloqueante de 62 PDFs al abrir el dashboard GUI | **corregido S42**: optimización a generación bajo demanda/muestra rápida |
| BUG-23 (nuevo, auditoría) | Inconsistencia en fórmula del IPP y falta de filtro de borrado lógico en reportes PDF | **corregido S42**: filtrado estricto `activo = 1` y fórmula estándar unificada |
| BUG-24 (nuevo, auditoría) | Activos huérfanos y duplicados en `data/` (`catalog_2024.json`, `logo_upc_icon.png`, `logo_upc_transparent.png`) | **corregido S43**: purga total con `git rm`; uso estricto de archivos canónicos |
| BUG-25 (nuevo, auditoría) | Empaquetador `package_zip.py` incluía 60 reportes PDF temporales y zips anidados inflando el archivo formal a >8 MB | **corregido S43**: filtros estrictos en empaquetador para incluir solo las muestras oficiales; ZIP reducido a 5.1 MB |
