# Windows + Git (configuración que sí funciona)

- Toolchain: `C:\msys64\ucrt64\bin` (g++, gdb, **Python 3.14 MSYS SIN pip**) en PATH. VS Code extensiones C/C++, Python, SQLite Viewer.
- Python: **NO usar `pip`** (sin módulo; `ensurepip`/`get-pip` se cuelgan). Librerías vendored en `pylib/` (requests, bs4, pypdf…) y `sys.path` al inicio de cada script. `requirements.txt` es solo declarativo.
- **Compilar:** `Ctrl+Shift+B` (tarea con `-lsqlite3`). **Depurar:** `F5`. **Prohibido el botón play ▶** (inyecta tarea sin sqlite y rompe el build — BUG-06).
- `cwd` del programa = `PEA-I/` (la BD es `data/...` relativa). `core.autocrlf true` en Windows.
- Repo `Kovyn-Mena/PEA-I`, rama de trabajo `damianversion1`, PRs → `dev`. Comandos: `C:\msys64\ucrt64\bin\python.exe data\init_db.py`.
