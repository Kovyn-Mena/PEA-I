# Idempotencia de Carga y Zips Únicos (S32, reporte del usuario)

> Notas hermanas: [[034 - Producción por Tipo del Grupo]] (qué se guarda por carga) ·
> [[024 - Contrato de Interoperabilidad CLI (popen)]] (flags `--forzar/--existe-grupo/--limpiar-zips`).

El usuario cargó GISICO dos veces y apareció un 2.º zip. Causa triple:

1. El zip se nombra por `codigo` y el código cambió entre cargas
   (`GISICO` por sigla → `COL0018706` por CCRG de verPerfiles).
2. `scrape_grupo()` detectaba `existente` en `guardar_grupo()` pero seguía:
   re-scrapeaba, re-guardaba y re-empaquetaba incondicional.
3. C++ `flujoCargaGrupoUPC()` nunca preguntaba si el nro ya estaba en BD.

## Regla

- **1 grupo lógico = 1 fila en `Grupos` = 1 zip `grupo_<COL>.zip`.**
- Recargar sin `--forzar` → `grupo ya existente [COL...]` (sin red, sin zip nuevo).
- `empaquetar_grupo()` reutiliza el zip vigente si es más nuevo que sus fuentes.
- Migración de código usa `resolver_codigo()+_remap_codigo()`; los zips
  legacy huérfanos (`grupo_GISICO.zip`, `grupo_G002668.zip`, `grupo_G003639.zip`)
  se eliminan cuando su COL existe (`--limpiar-zips`, auto al final de cada scrape).
- `migrar_encoding.py` no se ve afectado: trabaja sobre BD temporal vacía.

## Verificación

`--existe-grupo 00000000002099` → `grupo ya existente [COL0018706]`;
`--scrape-grupo 00000000002099` sin `--forzar` → mismo aviso, 0 red;
`zip/` queda en 3 COL; `g++ -Wall -Wextra` limpio.

## S33 — Mensajes claros (segundo reporte del usuario)

El aviso funcionaba pero confundía: Python decía "ya existente" y C++
remataba con "[Datos cargados con exito.]" aunque no había cargado nada,
y el buscador por nombre (`menuBuscarGrupo()`) ni siquiera pasaba por el
pre-chequeo.

- Python: aviso en 2 líneas `CODIGO=... | GRUPO=... | ZIP=...` +
  `No se descargo nada nuevo ni se duplico informacion.`
- C++: helper `cargarGrupoDesdeSCIENTI()` usado por `flujoCargaGrupoUPC()`
  y `menuBuscarGrupo()` — captura la salida, la reenvía con `[PYTHON]` y,
  si hubo duplicado, cierra con `[AVISO] Este grupo ya estaba cargado...
  Todo sigue igual.` sin prometer recarga.

## S34 — Submenú tras búsqueda sin carga (reporte grave del usuario)

Decir sí en el arranque + grupo ya existente (o cancelar/fallar) entraba
al menú con la RAM vacía en automático. Fix con la lógica del No:
`menuBuscarGrupo()` retorna `bool`; `iniciar()` en bucle con submenú
1 volver a buscar (repite el si/no) / 2 precargar SQLite / 3 sin datos
explícito. Ver bitácora S34 (BUG-12).
