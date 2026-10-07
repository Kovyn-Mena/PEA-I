# TDAs auxiliares (nodos puros, sin colecciones STL)

- **Pila Undo (`PilaUndo`, LIFO):** `apilar` (con persistencia doble a `HistorialAcciones` vía `apilarConPersistencia`), `desapilar` (ejecuta la reversa en `ejecutarUndo`), `verTope` (consulta no destructiva), `tamano`, `listar`, `crearVacia`.
- **Cola Ingesta (`ColaIngesta`, FIFO):** `encolar(URL_SCIENTI/CSV/PDF/OFFLINE)`, `desencolar` (procesa en orden), `verFrente`, `tamano`, `listarPendientes`, `crearVacia`.
- **Lista simple:** bloque base de cada eje (`sigGrupo`, `sigInvestigador`, `sigProductoGrupo`); la multilista las cruza en 3D (ver [[020 - Hipercubo Ortogonal 3D (Multilista)]]).
- Demo 7 operaciones × 4 TDAs: opción 9 del menú (`demoTDAs()`).
