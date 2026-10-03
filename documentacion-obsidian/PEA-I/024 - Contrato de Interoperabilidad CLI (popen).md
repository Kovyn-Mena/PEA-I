# Contrato CLI C++ ↔ Python (`popen`)

`Taller2_KM_PO_XX.py` (existe, S11) acepta: `--scrape-grupo NRO` · `--scrape-todos` (lee `data/grupos_upc.txt`) · `--scrape-url "<url>"` · `--ingesta-archivo "<csv|pdf>"` (+`--grupo/--rh` para PDF) · `--offline` · `--db` · `--gui` (aviso Fase 5 pendiente) · consola interactiva pendiente Fase 2.

C++ (`GestorInterop`) dispara, captura salida, exige persistir RAM **antes** de recargar la multilista desde el `.db`. Comando python hoy hardcodeado a MSYS2 → hacerlo configurable.
