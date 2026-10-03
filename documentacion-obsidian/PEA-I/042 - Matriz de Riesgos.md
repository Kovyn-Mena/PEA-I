# Riesgos top

1. Scraping cae en defensa → plan B `--offline` + snapshot HTML (crítico).
2. `database is locked` → WAL+timeout ✅ + no escribir desde 2 procesos a la vez.
3. Double-free → owner único ✅.
4. SPEC/HU/CU sin redactar → pérdida directa (programar Word).
5. Dashboard pendiente → 12.b/c (Python).
