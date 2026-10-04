# Matriz 1–14 del taller (cobertura en C++)

| # | Requisito | Estado C++ |
|---|-----------|:----------:|
| 1 | Gestionar grupos e investigadores | ✅ menuGrupos/menuInvestigadores + N:M |
| 2 | Productos por grupo y por investigador | ✅ doble enlace + detalles; 1161 prod. en 14 tipos (ver [[034 - Producción por Tipo del Grupo]]); col. GRUPO + filtro por grupo (S29) + pie por tipo (S35) |
| 3 | Integrantes, **plan** y productos por grupo | ✅ `verDetalleGrupo` |
| 4 | Info personal + productos del investigador | ✅ `verDetalleInvestigador` + hoja de vida CvLAC S37 (`verPerfilInvestigador`: par evaluador, citaciones, nacionalidad, sexo, Scholar/ORCID, formación, experiencia, áreas, idiomas) |
| 5 | Documento **Modelo** | ⚠️ No suministrado → ver `MODELO_FALTANTE_Punto5.md` |
| 6 | Variables de entrada/salida | ✅ validadores + pendiente tabla consola |
| 7 | Scraping URL o PDF/CSV | ✅ py `--scrape-grupo/--scrape-todos/--ingesta-archivo/--offline` idempotente + snapshot; PDF tabular E2E ✅ (S18) |
| 8 | Estructura de LISTAS | ✅ Multilista (listas simples como base) + Pila + Cola |
| 9 | Ingresar/eliminar/desactivar/modificar + categoría y validación | ✅ CRUD + validación por dato |
| 10 | Filtrar por año | ✅ 2/5 años + rango validado |
| 11 | Editar cualquier dato | ✅ ENTER conserva + validación |
| 12.a | C: tablas y números | ✅ 5 salidas fijas (74/70/70/74/70 ≤ 80, ASCII, S15) |
| 12.b/c | Python dashboard + 3 vistas | ⬜ Python |
| 13 | 1–12 ⇒ 4.0 | meta |
| 14 | Git+BD+GUI+interop+docs(+Rust) | 🟡 BD✅ Git🟡 resto pendiente |

7 operaciones por TDA: creación (`crearVacia`/arranque Nota 10), inclusión (`insertar*/encolar/apilar`), eliminación (física + `desencolar/desapilar`), desactivación lógica, consulta (`listar*/verDetalle*/verTope/verFrente`), modificación (`editar*`), persistencia (SQLite + `HistorialAcciones`).
