# Hallazgos M-01 a M-10

| ID | Hallazgo | Estado |
|----|----------|:------:|
| M-01 | Fecha entrega / semestre inconsistentes | confirmar docente |
| M-02 | Nomenclatura 2 vs 3 iniciales | confirmar docente |
| M-03 | Scraping frágil sin plan B | mitigado (py con timeout/retry/UA + snapshot + `--offline` idempotente, S11) |
| M-04 | Recarga total sin lock | mitigado (WAL+timeout; falta persistir-antes-de-recargar ritual) |
| M-05 | Riesgo punteros multilista | mitigado (owner único) |
| M-06 | `make test` vacío | pendiente |
| M-07 | URLs hardcodeadas | pendiente (`config`) |
| M-08 | Ambigüedad "no usar listas" | aclarado en demo/menú (Word pendiente) |
| M-09 | Rust opcional | solo al final |
| M-10 | Falta documento Modelo | ver `MODELO_FALTANTE_Punto5.md` |
