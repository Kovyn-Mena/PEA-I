# Contrato Relacional SQLite (`data/`)

Tablas: `Grupos`, `Investigadores`, `Productos` (FKs + `ON DELETE CASCADE`), `grupo_investigador` (N:M, PK compuesta), `HistorialAcciones` (Undo persistente), `perfiles_grupo` (S28: CCRG/líder/programa + indicadores por subtipo y cuartil).

Códigos COL originales (S28, `scripts/migrar_col.py`): GISICO→COL0018706, AITICE→COL0043834, GIELEHLA→COL0001351 (PK + FKs con FK OFF, `foreign_key_check` limpio).

Conexión siempre: `WAL + busy_timeout=5000 + foreign_keys=ON` (C++ y `init_db.py`).

Tabla `cache_fuentes` (S19): caché oficial con ETag/304 + dedup SHA-256 + LRU. Base del futuro staging Sí/No (Parte final) y de la carga perezosa a 1M de registros.

Semillas: **GISICO real** (1 grupo + 85 investigadores + 10 productos + 85 adscripciones, ver `data/gisico_semillas.json`). Los 85 `cod_rh` son ORIGINALES (hrefs CvLAC de GrupLAC, S17); categorías 1x1 en CvLAC: 1 Senior + 4 Asociado + 10 Junior, resto "No categorizado" (sin fila de categoría = no reconocido). Cero placeholders. `init_db.py` no duplica y migra adscripciones en BD viejas. `muestra_upc.csv` (12 filas) + `dataset_respaldo.csv` (157 filas: 85 miembros + 72 artículos) = plan B offline. Ejemplos anteriores (GIDSE/GISI/BIOTEC) eliminados por ser de otra institución.
