# Contrato CLI C++ ↔ Python (`popen`)

`Taller2_KM_PO_XX.py` (existe, S11) acepta: `--scrape-grupo NRO` · `--scrape-todos` (lee `data/grupos_upc.txt`) · `--scrape-url "<url>"` · `--ingesta-archivo "<csv|pdf>"` (+`--grupo/--rh` para PDF) · `--offline` · `--db` · `--gui` (aviso Fase 5 pendiente) · consola interactiva pendiente Fase 2.

C++ (`GestorInterop`) dispara, captura salida, exige persistir RAM **antes** de recargar la multilista desde el `.db`. Comando python hoy hardcodeado a MSYS2 → hacerlo configurable.

## S32 — Idempotencia de carga (ver [[035 - Idempotencia de Carga y Zips Únicos]])

- `--scrape-grupo NRO` sin `--forzar`: si el nro ya está en `Grupos` (chequeo offline por índice/snapshot/nombre), imprime `grupo ya existente [CODIGO] ... zip=...` y retorna sin red ni zip nuevo.
- `--forzar`: re-scrapea aunque exista (uso: `migrar_encoding.py`, rescrapes dirigidos).
- `--sin-cvlac`: omite la hoja de vida por integrante (S37, carga rápida).
- `--existe-grupo NRO` (offline, exit 0/1) · `--limpiar-zips` (borra legacy `GISICO/G002668/G003639` si su COL existe).
- C++ `flujoCargaGrupoUPC()` pre-chequea con `salidaPython("--existe-grupo")` y avisa en consola sin llamar al scrape.
