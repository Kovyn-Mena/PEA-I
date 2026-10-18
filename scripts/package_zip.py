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
import sys
import zipfile

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ZIP_NAME = os.path.join(BASE_DIR, "Taller2_EstructuraDatos_GrupoXX.zip")

FILES_TO_INCLUDE = [
    "CMakeLists.txt",
    "Makefile",
    "README.md",
    "integrantes.txt",
    "requirements.txt",
    "iniciar.bat",
    "README_WINDOWS.txt",
    "LEEME-PRIMERO.txt",
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
    ".vscode",
    ".devcpp",
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
    "Informe_GrupLAC_COL0218897.pdf",
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

def verificar_frescura() -> bool:
    """Gate anti-stale (incidente oct-2026: ZIP entregado sin los últimos fixes).
    Advierte si alguna fuente versionada es más nueva que el ZIP existente.
    No bloquea (el empaquetado actualiza el ZIP de todos modos)."""
    if not os.path.exists(ZIP_NAME):
        print("    [gate] Sin ZIP previo: se creará desde cero.")
        return True
    t_zip = os.path.getmtime(ZIP_NAME)
    rancios = []
    for d in ("src", "data", "docs", "scripts"):
        dd = os.path.join(BASE_DIR, d)
        for root, dirs, fs in os.walk(dd):
            dirs[:] = [x for x in dirs if x not in ("__pycache__",)]
            if "pylib" in root.split(os.sep):
                continue
            for f in fs:
                if not f.endswith((".py", ".h", ".cpp", ".json", ".sql")):
                    continue
                p = os.path.join(root, f)
                if os.path.getmtime(p) > t_zip:
                    rancios.append(os.path.relpath(p, BASE_DIR))
    for f in ("iniciar.bat", "Makefile", "requirements.txt", "Taller2_AB_PO_XX.py",
              "Taller2_AB_PO_XX.cpp", "README_WINDOWS.txt", "LEEME-PRIMERO.txt"):
        p = os.path.join(BASE_DIR, f)
        if os.path.exists(p) and os.path.getmtime(p) > t_zip:
            rancios.append(f)
    if rancios:
        print(f"    [gate] ZIP desactualizado: {len(rancios)} fuentes más nuevas "
              f"(ej. {', '.join(rancios[:4])}). Se regenerará ahora.")
        return False
    print("    [gate] ZIP al día con las fuentes.")
    return True


def verificar_formato_windows() -> bool:
    """Gate anti-repetición (fallo 'el .bat ni abre' oct-2026):
    los archivos cara-Windows deben ir en CRLF; los .py/.cpp/Makefile en LF.
    Normaliza automáticamente a CRLF y avisa. Retorna False si algo falla."""
    windows_crlf = [
        "iniciar.bat",
        "README_WINDOWS.txt",
        "integrantes.txt",
        "requirements.txt",
    ]
    ok = True
    for rel in windows_crlf:
        p = os.path.join(BASE_DIR, rel)
        if not os.path.exists(p):
            print(f"    [!] Gate formato: no encontrado — {rel}")
            ok = False
            continue
        with open(p, "rb") as f:
            data = f.read()
        lineas = data.split(b"\n")
        sin_cr = sum(1 for ln in lineas if ln and not ln.endswith(b"\r"))
        if sin_cr:
            with open(p, "wb") as f:
                f.write(b"\n".join(
                    ln if not ln or ln.endswith(b"\r") else ln + b"\r"
                    for ln in data.split(b"\n")
                ))
            print(f"    [gate] {rel}: {sin_cr} líneas LF→CRLF normalizadas")
    return ok

def asegurar_dashboard_python():
    """Genera dist/dashboard_python.html si falta.

    'make clean' elimina ese HTML generado; sin este paso el gate de contenido
    fallaría siempre tras una limpieza. No abre el navegador.
    """
    destino = os.path.join(BASE_DIR, "dist", "dashboard_python.html")
    if os.path.exists(destino):
        return
    print("[*] dist/dashboard_python.html ausente; generando dashboard analítico...")
    try:
        if BASE_DIR not in sys.path:
            sys.path.insert(0, BASE_DIR)
        from src.python.gui import DashboardApp
        app = DashboardApp(os.path.join(BASE_DIR, "data", "pea_investigacion.db"))
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        app.generar_html_dashboard(destino)
        print(f"    [OK] Dashboard generado: {os.path.relpath(destino, BASE_DIR)}")
    except Exception as e:
        print(f"    [!] No se pudo generar el dashboard automáticamente: {e}")
        print("        Genérelo manualmente con: python Taller2_AB_PO_XX.py --gui")

def empaquetar():
    print("[*] Gate F: frescura del ZIP previo (antes de reemplazarlo)...")
    asegurar_dashboard_python()
    verificar_frescura()
    if os.path.exists(ZIP_NAME):
        os.remove(ZIP_NAME)

    print("[*] Gate 0/3: matriz de dependencias...")
    import subprocess
    ver = subprocess.run([sys.executable, os.path.join(BASE_DIR, "scripts", "verificar_dependencias.py")])
    if ver.returncode != 0:
        print("[!] Gate 0/3 FALLA: corrija dependencias antes de empaquetar.")
        raise SystemExit(1)

    print("[*] Gate 1/3: formato Windows (CRLF en .bat/.txt)...")
    verificar_formato_windows()

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

    print("[*] Gate 2/3: contenido del ZIP (basura/duplicados/obligatorios)...")
    with zipfile.ZipFile(ZIP_NAME, "r") as zf:
        names = zf.namelist()
        mal = [n for n in names
               if n.endswith((".pyc", ".exe", ".bak", "-shm", "-wal"))
               or n.split("/")[-1] in ("pea_cpp", "test_tda", "test_sqlite", "sqlite3_amalg.o")
               or "/snapshots/zip/" in n or "__pycache__" in n]
        dups = len(names) - len(set(names))
        obligatorios = ["iniciar.bat", "Taller2_AB_PO_XX.py", "Taller2_AB_PO_XX.cpp",
                        "src/cpp/sqlite3.c", "dist/dashboard_python.html"]
        faltan = [o for o in obligatorios if o not in names]
        if mal:
            print(f"    [!] Gate 2/3 FALLA: basura en ZIP: {mal[:5]}")
        if dups:
            print(f"    [!] Gate 2/3 FALLA: {dups} duplicados")
        if faltan:
            print(f"    [!] Gate 2/3 FALLA: faltan obligatorios: {faltan}")
        if not mal and not dups and not faltan:
            print(f"    [gate] ZIP limpio: {len(names)} entradas, 0 basura, 0 duplicados")
    print(f"     • Listo para adjuntar y enviar a adithperez@unicesar.edu.co")

if __name__ == "__main__":
    empaquetar()
