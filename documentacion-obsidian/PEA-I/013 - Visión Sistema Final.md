# Visión Sistema Final (proyecto a futuro, Parte 5+)

Flujo ideal acordado con el usuario:

1. **Entrada:** el usuario escribe el nombre de la universidad.
2. **Búsqueda:** el sistema entra a `ciencia-war/busquedaGruposPorInstitucion.do`; si no existe → **"universidad no encontrada"**; si existe → "universidad encontrada".
3. **Carga:** "¿desea cargar sus grupos investigativos?" → descarga TODO desde los grupos hasta los investigadores + su CvLAC, dividido como pide el taller (ver [[011 - Problema de Negocio y Entidades]]).
4. **Listas + reportes:** menús de listas y opción "generar reporte de xxx sección": general, solo grupos o información básica del investigador.
5. **Guardar Sí/No (S38 ✅):** al salir se pregunta; **No** → se restaura la copia de sesión (BD al arranque + se borran snapshots/zips generados); **Sí** → se guarda limpio y el `.zip` queda vivo.

Estado: pasos 2–3 parciales (buscador por grupo + `--universidad`, ver S21/S23); el resto es Parte 5. Todo lo que se hace hoy debe dejar el camino limpio a esto (ver [[033 - Escalabilidad a 1M de registros]]).
