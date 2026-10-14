#!/usr/bin/env python3
"""
=====================================================================
PEA-i: GATE DE MATRIZ DE DEPENDENCIAS (anti-repetición)
=====================================================================
Verifica que todo import de terceros usado en runtime esté cubierto por
requirements.txt y (salvo PIL, binario por plataforma) por pylib/.
Falla (exit 1) ante cualquier desface para que el empaquetado no avance.
Uso:  python3 scripts/verificar_dependencias.py
=====================================================================
"""

import ast
import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Módulo importado -> (paquete pip, vendored en pylib?, runtime?)
# runtime=False: solo herramientas de desarrollo/docs (no bloquean entrega).
MAPA = {
    "requests": ("requests", True, True),
    "bs4": ("beautifulsoup4", True, True),
    "pypdf": ("pypdf", True, True),
    "reportlab": ("reportlab", True, True),
    "PIL": ("pillow", False, True),  # binario por plataforma: pip, con aviso limpio
    "docx": ("python-docx", False, False),  # solo make docs
    "matplotlib": ("matplotlib", False, False),  # solo make docs
}

SCAN_DIRS = ["src", "data", "scripts"]
SCAN_FILES = ["Taller2_AB_PO_XX.py"]


def _imports_de(py_path: str) -> set:
    try:
        arbol = ast.parse(open(py_path, encoding="utf-8").read())
    except (SyntaxError, UnicodeDecodeError, OSError) as e:
        print(f"[!] No se pudo parsear {py_path}: {e}")
        return set()
    mods = set()
    for n in ast.walk(arbol):
        if isinstance(n, ast.Import):
            mods.update(a.name.split(".")[0] for a in n.names)
        elif isinstance(n, ast.ImportFrom) and n.module:
            mods.add(n.module.split(".")[0])
    return mods & set(MAPA)


def main() -> int:
    fallos = []
    usados = {}
    for d in SCAN_DIRS:
        dd = os.path.join(BASE_DIR, d)
        for root, dirs, fs in os.walk(dd):
            dirs[:] = [x for x in dirs if x not in ("__pycache__",)]
            if "pylib" in root.split(os.sep):
                continue
            for f in fs:
                if not f.endswith(".py"):
                    continue
                p = os.path.join(root, f)
                for m in _imports_de(p):
                    usados.setdefault(m, []).append(os.path.relpath(p, BASE_DIR))
    for f in SCAN_FILES:
        p = os.path.join(BASE_DIR, f)
        if os.path.exists(p):
            for m in _imports_de(p):
                usados.setdefault(m, []).append(f)

    req_txt = open(os.path.join(BASE_DIR, "requirements.txt"), encoding="utf-8").read()
    reqs = {ln.split(">")[0].split("=")[0].split("<")[0].strip().lower()
            for ln in req_txt.splitlines()
            if ln.strip() and not ln.strip().startswith("#")}
    pylib = os.path.join(BASE_DIR, "pylib")
    vendored = set()
    if os.path.isdir(pylib):
        for e in os.listdir(pylib):
            vendored.add(e.split("-")[0].lower())

    print("[*] Gate dependencias: importado vs requirements vs pylib")
    for mod in sorted(usados):
        pip, vend, runtime = MAPA[mod]
        en_req = pip.lower() in reqs
        en_pylib = mod.lower() in vendored or pip.lower() in vendored
        estado = "OK"
        if runtime and not en_req:
            estado = "FALLA: falta en requirements.txt"
            fallos.append(mod)
        elif runtime and vend and not en_pylib:
            estado = "FALLA: falta en pylib/"
            fallos.append(mod)
        print(f"    [{estado}] {mod} (pip:{pip} req:{en_req} pylib:{en_pylib}) "
              f"<- {', '.join(usados[mod][:3])}")

    # PIL es la excepción documentada: reportlab la exige al importar.
    if "PIL" in usados:
        print("    [nota] PIL/pillow solo vía pip (binario por plataforma); "
              "reporte_pdf.py degrada con aviso limpio sin ella.")

    if fallos:
        print(f"[!] Gate dependencias FALLA: {sorted(set(fallos))}")
        return 1
    print("[gate] Matriz de dependencias consistente.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
