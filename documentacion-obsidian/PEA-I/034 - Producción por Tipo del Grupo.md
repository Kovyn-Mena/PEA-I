# Producción por Tipo del Grupo (mapeo SCIENTI → sistema, S28)

Cada grupo gestionado descarga sus productos desde su ficha GrupLAC
(`parse_produccion_grupolac` + `--scrape-grupo`). Solo se guardan los tipos
del whitelist; el resto se cuenta como omitido (reporte, no se pierde el dato
en el snapshot/zip).

| Marcador SCIENTI | Tipo sistema | GISICO (nro 2099) |
|---|---|---|
| Publicado en revista especializada | Articulo | 91 |
| Revista de divulgación / Periódico de noticias | Articulo | 11 |
| Documento de trabajo (Working Paper) | Articulo | 3 |
| Libro resultado de investigación | Libro | 13 |
| Libros de formación / Otro libro publicado | Libro | 7 |
| Capítulo de libro / Otro capítulo | Capitulo (valor nuevo S28, no Libro) | 23 |
| Computacional (+ "Otra" con keywords software) | Software | ~90 |
| Patente / Modelo de utilidad | Patente | 0 (parser listo) |
| Diseño Industrial, Spin-off, Consultorías, Informes, Eventos, Formación | — (omitido con conteo) | ~399 |

Reglas: título + año obligatorios; autoría solo a integrantes macheados
(`mapa_autores`, sin inventar); idempotencia por (titulo, año, grupo, rh) +
prefijo-30 (truncado PDF). Categoría "Por verificar", validación "Pendiente".

Resultado carga GISICO (S28, BD real): 246 productos
(85 Articulo, 26 Capitulo, 27 Libro, 108 Software), 23 sin autor, 399 omitidos
por tipo. Rerun idempotente (0 nuevos). Códigos COL migrados (ver S28).
