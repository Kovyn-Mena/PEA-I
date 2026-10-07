# Hipercubo Ortogonal 3D (Multilista en RAM)

Ejes: **X Grupos** (`sigGrupo`) · **Y Investigadores** (`sigInvestigador`, N:M por copias + `grupo_investigador`) · **Z Productos** (doble enlace `sigProductoGrupo` / `sigProductoInvestigador`).

**Política de propiedad (BUG-03):** el único owner con `delete` es el eje del **grupo**; el eje investigador solo desenlaza. `eliminarProductoFisico` desenlaza ambos + 1 delete. `limpiar()` igual.

**Por qué:** matriz dispersa O(G+I+P+R) vs densa O(G×I×P). Lista simple = bloque base de cada eje. Pila LIFO = Undo. Cola FIFO = ingesta.

**Entrada consola:** toda opción con `leerOpcion()` (línea + ENTER, nunca `getch` en menús); todo número con `leerEntero()` (rango + reintento, sin `cin >>`); edición con ENTER = conservar + validadores (categoría A1/A/B/C/Reconocido, validación, tipo, correo, año 1900–2026).
