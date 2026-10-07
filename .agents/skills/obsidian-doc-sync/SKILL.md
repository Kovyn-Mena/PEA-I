---
name: obsidian-doc-sync
description: >-
  Reglas, procedimientos y plantillas para automatizar la documentación técnica,
  el registro de sesiones y la sincronización con la bóveda de Obsidian en `documentacion-obsidian/PEA-I/`.
  Usar cada vez que se realicen cambios lógicos, diseño de arquitectura, corrección de bugs o generación de entregables.
---

# Obsidian Documentation & Project Sync Skill

Esta habilidad guía al asistente en la actualización constante y sincronizada de la bóveda de conocimiento en Obsidian ubicada en:
`documentacion-obsidian/PEA-I/`

## Estructura de la Bóveda Obsidian
- `000 - PEA-i Hub Principal.md`: MOC (*Map of Content*) principal del proyecto.
- `010 a 014`: Requisitos, problema de negocio, matriz MinCiencias, entregables y entidades.
- `020 a 025`: Arquitectura del sistema (Hipercubo 3D, TDAs Pila/Cola, SQLite, CLI popen, Capa de presentación).
- `030 a 035`: Fases, roles, roadmap y escalabilidad.
- `040 a 042`: Auditorías, inconsistencias (M-01 a M-10) y matriz de riesgos.
- `050 a 052`: Recomendaciones priorizadas y guías de configuración.
- `060 - Bitácora de Cambios y Registro de Errores Lógicos.md`: **Bitácora viva de sesiones y registro de bugs.**

---

## Procedimientos de Sincronización Automática

### 1. Registro Obligatorio en la Bitácora (`060`)
Al completar una tarea, bugfix, refactor o feature:
1. Abrir `documentacion-obsidian/PEA-I/060 - Bitácora de Cambios y Registro de Errores Lógicos.md`.
2. Añadir la nueva sesión (`## Sesión N — [Título claro]`) en la parte superior o cronológica según corresponda.
3. Especificar:
   - **Archivos modificados / creados**.
   - **Causa raíz y solución** (si fue un bug).
   - **Resultados de compilación y pruebas** (`g++ -Wall -Wextra`, pruebas E2E, etc.).

### 2. Creación o Actualización de Notas Técnicas
Si el cambio introduce nuevas estructuras o componentes:
1. Crear la nota en `documentacion-obsidian/PEA-I/` con formato `NNN - Nombre.md`.
2. Usar frontmatter YAML:
   ```yaml
   ---
   tipo: Arquitectura / Requisito / Guía
   estado: Activo
   ---
   ```
3. Enlazar la nueva nota dentro de `000 - PEA-i Hub Principal.md`.
4. Usar enlaces bidireccionales `[[Nombre de Nota]]` para conectar conceptos relacionados.

### 3. Diagramas y Matemáticas
- Usar bloques de código `mermaid` para flujos, diagramas de clases y TDAs.
- Usar notación LaTeX (`$...$` o `$$...$$`) para fórmulas de cálculo de puntajes y ponderaciones MinCiencias.
