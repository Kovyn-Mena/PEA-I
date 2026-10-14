#!/usr/bin/env python3
"""
=====================================================================
PEA-i: EMPAQUETADOR DE ENTREGA FORMAL EN ARCHIVO ZIP
Universidad Popular del Cesar — Estructura de Datos
=====================================================================
Empaqueta la solución integral limpia para el envío al docente
(adithperez@unicesar.edu.co), excluyendo temporales, cachés y binarios.
=====================================================================
"""

import os
import zipfile

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ZIP_NAME = os.path.join(BASE_DIR, "Taller2_EstructuraDatos_GrupoXX.zip")

FILES_TO_INCLUDE = [
    "Makefile",
    "README.md",
    "integrantes.txt",
    "requirements.txt",
    "iniciar.bat",
    "README_WINDOWS.txt",
    "Documentacion_Tecnica_GrupoXX.docx",
    "Taller2_AB_PO_XX.cpp",
    "Taller2_AB_PO_XX.py",
    os.path.join("dist", "visualizador_hipercubo.html"),
    os.path.join("dist", "dashboard_python.html"),
    os.path.join("dist", "logo_upc.png"),
    # SQLite3 amalgamado — necesario para compilación C++ portable en Windows
    # sin requerir 'pacman -S sqlite3' en MSYS2/MinGW.
    # Descargue de: https://www.sqlite.org/download.html
    # (sqlite-amalgamation-XXXXXXX.zip → copie sqlite3.c y sqlite3.h a src/cpp/)
    os.path.join("src", "cpp", "sqlite3.c"),
    os.path.join("src", "cpp", "sqlite3.h"),
]

DIRS_TO_INCLUDE = [
    "src",
    "data",
    "docs",
    "reportes",
    "scripts",
    # pylib: bundle vendored intencional (Python MSYS/Windows sin pip).
    # Ver documentacion-obsidian S45/BUG-26. No retirar sin pip funcional.
    "pylib",
]

# Patrones que se verifican contra el directorio raíz del archivo (root)
SKIP_DIR_PATTERNS = [
    ".git",
    "__pycache__",
    ".pytest_cache",
    "build",
    "target",           # target/ de cargo (Rust)
    "dist",             # dist/ se incluye via FILES_TO_INCLUDE individualmente
    ".env",
    os.path.join("snapshots", "zip"),  # zips se regeneran con empaquetar_*
]

# Extensiones de archivo a excluir (en cualquier directorio)
SKIP_EXTENSIONS = {
    ".o", ".obj", ".exe", ".pyc", ".gitkeep", ".zip", ".bak",
    "-shm",   # memoria compartida WAL SQLite
    "-wal",   # WAL SQLite
}

# Nombres de archivo a excluir (exactos, en cualquier directorio o raíz)
SKIP_FILENAMES = {
    "pea_cpp",          # binario ELF Linux — no ejecutable en Windows
    "test_tda",         # binario ELF Linux de tests
    "test_sqlite",      # binario ELF Linux de tests
    ".DS_Store",        # metadatos macOS
    ".gitignore",       # innecesario en el entregable
    "GEMINI.md",        # notas internas de desarrollo
    "sqlite3_amalg.o",  # objeto temporal de compilación
}

# Archivos que se incluyen explícitamente via FILES_TO_INCLUDE y NO deben
# recogerse de nuevo por el walker de DIRS_TO_INCLUDE (evita duplicados en el ZIP)
SKIP_IF_ALREADY_IN_FILES = {
    os.path.join("src", "cpp", "sqlite3.c"),
    os.path.join("src", "cpp", "sqlite3.h"),
}

OFFICIAL_SAMPLE_REPORTS = {
    "Informe_GrupLAC_COL0018706.pdf",
    "Informe_GrupLAC_COL0002099.pdf",
    "Informe_GrupLAC_COL0043834.pdf",
    "Informe_GrupLAC_COL0005544.pdf",
    "Informe_GrupLAC_COL0001351.pdf",
    "Informe_GrupLAC_COL0000000.pdf",
    "Informe_GrupLAC_COL0002093.pdf",
}

def _debe_excluir(root: str, filename: str) -> bool:
    """Retorna True si el archivo debe excluirse del ZIP."""
    # Excluir por directorio padre
    if any(skip in root for skip in SKIP_DIR_PATTERNS):
        return True
    # Excluir por extensión
    if any(filename.endswith(ext) for ext in SKIP_EXTENSIONS):
        return True
    # Excluir por nombre exacto (captura binarios ELF sin extensión como pea_cpp)
    if filename in SKIP_FILENAMES:
        return True
    return False

def empaquetar():
    if os.path.exists(ZIP_NAME):
        os.remove(ZIP_NAME)

    print(f"[+] Creando archivo de entrega ZIP: {os.path.basename(ZIP_NAME)}...")
    archivos_incluidos = 0
    archivos_omitidos = 0

    with zipfile.ZipFile(ZIP_NAME, "w", zipfile.ZIP_DEFLATED) as zf:
        # Archivos individuales de la raíz (y dist/)
        for f in FILES_TO_INCLUDE:
            p = os.path.join(BASE_DIR, f)
            if os.path.exists(p):
                zf.write(p, arcname=f)
                archivos_incluidos += 1
            else:
                print(f"    [!] Advertencia: no encontrado — {f}")
                if f in (
                    os.path.join("src", "cpp", "sqlite3.c"),
                    os.path.join("src", "cpp", "sqlite3.h"),
                ):
                    print(f"        Para compilacion C++ portable en Windows descargue el amalgamado")
                    print(f"        de https://www.sqlite.org/download.html y coloque sqlite3.c")
                    print(f"        y sqlite3.h en src/cpp/")

        # Directorios recursivos
        for d in DIRS_TO_INCLUDE:
            dir_path = os.path.join(BASE_DIR, d)
            if not os.path.exists(dir_path):
                continue
            for root, dirs, filenames in os.walk(dir_path):
                # Excluir subdirectorios en el walk (modifica dirs in-place)
                dirs[:] = [
                    dd for dd in dirs
                    if not any(skip in os.path.join(root, dd) for skip in SKIP_DIR_PATTERNS)
                ]
                for file in filenames:
                    if _debe_excluir(root, file):
                        archivos_omitidos += 1
                        continue
                    full_p = os.path.join(root, file)
                    rel_p = os.path.relpath(full_p, BASE_DIR)
                    # Saltar si ya fue incluido explícitamente vía FILES_TO_INCLUDE
                    if rel_p in SKIP_IF_ALREADY_IN_FILES:
                        continue
                    # Reportes: solo incluir los oficiales de muestra
                    if (
                        rel_p.startswith("reportes")
                        and file.endswith(".pdf")
                        and file not in OFFICIAL_SAMPLE_REPORTS
                    ):
                        archivos_omitidos += 1
                        continue
                    zf.write(full_p, arcname=rel_p)
                    archivos_incluidos += 1

    size_kb = round(os.path.getsize(ZIP_NAME) / 1024, 1)
    print(f"[OK] Archivo de entrega generado exitosamente:")
    print(f"     • Ruta:     {ZIP_NAME}")
    print(f"     • Tamaño:   {size_kb} KB")
    print(f"     • Incluidos: {archivos_incluidos} archivos")
    print(f"     • Omitidos:  {archivos_omitidos} archivos (binarios/cache/temporales)")
    print(f"     • Listo para adjuntar y enviar a adithperez@unicesar.edu.co")

if __name__ == "__main__":
    empaquetar()
