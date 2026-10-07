# Escalabilidad a 1M de registros (diseño a futuro)

Para que el programa no se rompa con 1 millón de datos (exigencia del usuario):

- **SQLite primero, RAM después:** la multilista opera sobre ventanas paginadas, nunca el millón completo (hoy el arranque precarga todo: refactorizar a carga perezosa).
- **Reportes por SQL agregado** (`COUNT/GROUP BY` en streaming, memoria O(1)) en vez de recorrer nodos.
- **Staging Sí/No:** scrapea a BD temporal + `cache_fuentes`; Sí = `COMMIT`, No = `ROLLBACK` + borrado (base del controlador de salida).
- **Ingesta por lotes** en una transacción, índices en `anio/categoria/codigo`, Cola persistida para reanudar.
- **Caché ETag/hash/LRU** (ver [[041 - Puntos Frágiles e Ingesta Masiva (Scraping)]]): re-corridas casi gratis en red, almacenamiento acotado a ~66 zips.

Todo lo que se implementa hoy (idempotencia, proyección, contadores entidad, WAL) ya apunta aquí.
