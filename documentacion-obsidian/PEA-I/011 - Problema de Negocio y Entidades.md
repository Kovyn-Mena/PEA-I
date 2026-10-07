# Problema de negocio y entidades (modelo SCIENTI adoptado)

La UPC necesita gestionar su producción científica (modelo nacional SCIENTI de MinCiencias): **grupos, investigadores y productos**, con plan/líneas por grupo y categorías/aval por producto.

| Entidad | Campos canónicos | Relaciones |
|---------|------------------|------------|
| Grupo | `codigo_grupo` (PK), nombre, líder, `plan_investigacion`, `lineas_estrategicas`, estado | 1:N productos · N:M investigadores |
| Investigador | `cod_rh` (PK CvLAC), nombre, correo, categoría, `cvlac_url`, estado | N:M grupos · N autorías |
| Producto | id, título, tipo, **categoría** (A1/A/B/C), **validación**, año, FK grupo, FK investigador, estado | N:1 grupo · N:1 autor principal |

Detalle completo del faltante punto 5 en `MODELO_FALTANTE_Punto5.md` (raíz del repo).
