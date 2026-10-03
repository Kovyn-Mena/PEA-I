# Punto 5 — Documento "Modelo" faltante (declaración + modelo adoptado)

## Declaración
El enunciado remite a "el siguiente documento: Modelo", pero dicho documento
**no fue suministrado** (solo están el PDF del taller de 3 páginas y la GUIA
de 14). Para no bloquear los puntos 1–4 y 6, se adopta el **modelo estándar
SCIENTI GrupLAC/CvLAC** como modelo de referencia.

## Modelo adoptado (fuente: MinCiencias SCIENTI)
- **Grupo:** código (`codigo_grupo`), nombre, líder, plan de investigación,
  líneas estratégicas, estado, integrantes (N:M vía `grupo_investigador`),
  productos (1:N vía `Productos.codigo_grupo_fk`).
- **Investigador:** `cod_rh` (CvLAC), nombre completo, correo, categoría
  MinCiencias, URL CvLAC, estado, grupos adscritos (N:M), productos (vía
  `Productos.cod_rh_investigador_fk`).
- **Producto:** id, título, tipo (Artículo/Libro/Software/Patente), categoría
  (A1/A/B/C), validación/aval (Validado/Pendiente/Rechazado), año, grupo FK,
  investigador FK, estado.

## Trazabilidad a puntos 1–4
- P1 (grupos + investigadores): `Grupos`, `Investigadores`, `grupo_investigador`.
- P2 (productos por grupo y por investigador): doble enlace
  `sigProductoGrupo` / `sigProductoInvestigador` + FKs en `Productos`.
- P3 (integrantes + plan + productos por grupo): `verDetalleGrupo` muestra los
  tres; `plan_investigacion` y `lineas_estrategicas` son columnas obligatorias.
- P4 (info personal + productos del investigador): `verDetalleInvestigador`.

## Acción pendiente con el docente
Solicitar el documento "Modelo" oficial. Si difiere (otros campos/tipos),
actualizar `schema.sql` + semillas + `verDetalle*` sin cambiar la arquitectura
de TDAs.
