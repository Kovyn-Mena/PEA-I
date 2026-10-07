# Producción por Tipo del Grupo (mapeo SCIENTI → sistema, S28 + S35)

Cada grupo gestionado descarga miembros y productos desde su ficha GrupLAC
(`parse_produccion_grupolac` + `--scrape-grupo`, ver [[024 - Contrato de Interoperabilidad CLI (popen)]]).
El parser es **consciente de sección** (S35): primero corta la ficha en sus
6 secciones y luego clasifica marcadores dentro de cada una — así resuelve
`Otro:`/`Taller:` ambiguos y captura el formato `1. X:` con punto simple
(informes/consultorías eran invisibles al regex viejo). Solo se guardan los
tipos del whitelist con autoría macheada (`mapa_autores`, sin inventar);
el resto se cuenta como omitido + `sin_autor` (reporte, no se pierde el dato
en el snapshot/zip, ver [[035 - Idempotencia de Carga y Zips Únicos]]).

| Marcador SCIENTI | Tipo sistema | Desde |
|---|---|---|
| Publicado en revista especializada / Divulgación / Periódico / Working Paper / **Revisión (Survey)** / Otra divulgativa | Articulo | S28 + S35 |
| Libro resultado / Formación / Otro libro / **Divulgación-Compilación** | Libro | S28 + S35 |
| Capítulo de libro / Otro capítulo | Capitulo (valor propio, no Libro) | S28 |
| Computacional (+ "Otra" con keywords software) | Software | S28 |
| Patente / Modelo de utilidad | Patente | S28 (parser listo) |
| Encuentro / Congreso / Simposio / Taller / Seminario / Foro (+ Otro en Apropiación) | Evento | S35 |
| Trabajo de grado / Tesis / Tutorías dirigidas | Tesis | S35 |
| Consultorías científico-tecnológicas | Consultoria | S35 |
| Informe técnico | Informe | S35 |
| Curso corto / Perfeccionamiento / Extensión (+ Taller en Formación) | CursoCorto | S35 |
| Jurado / Comisiones (toda la sección Evaluador) | Jurado | S35 |
| Contenido digital (audiovisual, sonoro) | Contenido | S35 |
| Ediciones / Compilación | Compilacion | S35 |
| Regulaciones y Normas | Regulacion | S35 |
| Diseño Industrial, Spin-off, Demás trabajos, Programa académico | — (omitido con conteo) | — |

Reglas: título + año obligatorios (año acepta `, AAAA`, `desde AAAA` y año
suelto fuera de ISSN/DOI); autoría por `Autores:` o rol
(Estudiante/Director/Tutor(es)/Cotutor(es)/Organizador/…); idempotencia por
(titulo, año, grupo, rh) + prefijo-30. Categoría "Por verificar".
**Validación (S36):** el chulito GrupLAC (`chulo_1.jpg` en el `<td>` previo
al ítem = avalado MinCiencias última convocatoria) se captura por `<tr>` con
clave (marcador, título, año) → `Validado`; sin chulo → `Pendiente`.
El re-scrape actualiza `Pendiente→Validado` sin duplicar.

Resultado backfill S35 (BD real, `--forzar` 3 grupos): **1161 productos**
(Jurado 257, Articulo 247, Software 195, Tesis 140, Capitulo 118, CursoCorto 106,
Libro 97, Compilacion 1). Evento/Informe/Consultoria/Contenido/Regulacion en 0:
la ficha no nombra persona (ponente anónimo/institución) y la regla estricta
los deja fuera — se cuentan como `sin_autor` (~610 entre los 3 grupos).

**S36 (chulito):** re-scrape `--forzar` sin productos nuevos (idempotente)
actualizó **307 a `Validado`** (Articulo 146, Software 75, Tesis 40, Capitulo 26,
Libro 20); resto 854 `Pendiente`. Decisión S35 (estricta): lo sin autor NO se guarda.
