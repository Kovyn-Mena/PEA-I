# Punto frágil: ingesta (Fase 3)

URLs obligatorias: GrupLAC `...nro=00000000002099` y CvLAC `...cod_rh=0000494917` (+ CSV/PDF). Riesgos: HTML cambiante, captcha/JS, PDF a 2 columnas, red caída en defensa.

Blindaje: `timeout=10` + `Retry(3)` + User-Agent + SQL parametrizado, **plan B `--offline`** con `dataset_respaldo.csv` (siempre demoable), snapshot HTML para tests. Regla de proyección punto 7: **solo columnas del sistema, resto se descarta y reporta**; fila sin PK/NOT NULL se descarta. CvLAC real desde S16 (ficha + artículos; libros/software pendientes).

verPerfiles por grupo (S28): `verPerfiles.jsp?id_convocatoria=22&nroIdGrupo=` → CCRG/COL real, líder, instituciones, programa + indicadores por subtipo y cuartil en `perfiles_grupo` (125 filas GISICO). Incluye migración sigla/G+nro → COL con FK OFF + `foreign_key_check` limpio.

## Arquitectura de caché oficial (S19, aprobada)

Medido: 1 grupo = 90 archivos / 19.5 MB → a 66 grupos serían ~5,600 archivos y ~1 GB. Se adopta la **híbrida refinada**:

- Tabla `cache_fuentes(url PK, sha256, etag, last_modified, fecha, ruta)`: ETag/304 si el servidor los da (**verificado: SCIENTI hoy NO envía validadores**, se honran si aparecen); si no, dedup por hash (mismo sha256 = sin cambios ni duplicados).
- CvLAC: sin HTML en disco — datos en BD + hash en caché (re-descargable).
- `empaquetar_grupo()`: 1 zip por grupo (GISICO: 647 KB → 66 KB). Límite: ≤66 zips + 2 tablas.
- Anti-duplicado extendido: título exacto + (año + autor + 30 prefijos) para el truncado del PDF.
