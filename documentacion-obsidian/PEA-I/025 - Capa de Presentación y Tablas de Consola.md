# Capa de Presentación y Tablas de Consola (estándar S26)

Solo presentación: **cero cambios en TDAs, datos o lógica**. Reglas:

- Bordes ASCII: marcos `+---+`, cabecera `+===+`, filas `| a | b |`. Nada de celdas pegadas.
- Ancho por **columnas visibles** (`anchoVisual()`: continuación UTF-8 = 0), no por bytes — las tildes/`�` de SCIENTI no descuadran.
- Truncado visual con `...` + relleno (`celdaV()`), 1 línea por fila, headers ASCII, tablas anchas ~90-110 (S27: ensanchar la terminal para verlas sin cortes).
- Helpers en `Taller2_KM_PO_XX.cpp`: `anchoVisual/truncarVisual/celdaV/bordeTabla/filaTabla/tituloTabla`.
- Las 6 salidas migradas (S15/S25/S26): grupos, ventana años, resumen 12.a, investigadores (global + por grupo), productos, más candidatos y `elegirGrupo()`.
- S35: columna TIPO a 12 (los 15 tipos caben, ver [[034 - Producción por Tipo del Grupo]]); `listarProductosDeGrupo()` con pie de conteo por tipo; líneas de `verDetalleGrupo()` con `[tipo/...]`.
