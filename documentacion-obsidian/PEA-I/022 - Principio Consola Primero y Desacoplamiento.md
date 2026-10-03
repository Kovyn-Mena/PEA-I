# Principio sagrado: Consola Primero

El sistema **NUNCA** depende de la GUI. La consola C++ es 100 % autosuficiente (CRUD, Undo, filtros, resumen 12.a, ingesta) y el dashboard Python / GUI C++ son capas externas opcionales (`--gui`).

Reglas de entrada (Sesión 9): menús con `leerOpcion()` (línea + ENTER, `getch` solo en `pausar`), números con `leerEntero()` (rango + reintento, prohibido `cin >>`), edición con ENTER = conservar + validadores por dato. Tablas ≤ 80 col, headers ASCII, bordes `+---+`/`+===+` y filas `| a | b |` con ancho visual (S26, ver [[025 - Capa de Presentación y Tablas de Consola]]).
