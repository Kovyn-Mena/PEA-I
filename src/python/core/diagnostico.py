#!/usr/bin/env python3
"""
=====================================================================
PEA-i: DIAGNÓSTICO DEL SISTEMA (pre-vuelo Windows / soporte remoto)
Universidad Popular del Cesar — Estructura de Datos
=====================================================================
Revisa en un solo reporte copiable: intérprete Python, dependencias
(requests/bs4/pypdf/reportlab/PIL con y sin pylib/), rutas del proyecto
(BD, snapshots, dist), estado de la BD, red hacia MinCiencias (latencia
real) y cobertura de snapshots. No modifica nada: solo lectura + 1 GET.
Uso:  python3 Taller2_AB_PO_XX.py --diagnostico
=====================================================================
"""

import os
import sys
import time
import sqlite3

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(BASE_DIR, "src"))
pylib_dir = os.path.join(BASE_DIR, "pylib")
if os.path.exists(pylib_dir):
    sys.path.insert(0, pylib_dir)


def _ok(cond):
    return "[OK]" if cond else "[NO]"


def ejecutar_diagnostico(db_path: str = None) -> bool:
    if db_path is None:
        db_path = os.path.join(BASE_DIR, "data", "pea_investigacion.db")
    print("=" * 70)
    print("PEA-i: DIAGNÓSTICO DEL SISTEMA (copie este reporte si pide soporte)")
    print("=" * 70)

    # 1. Intérprete
    print(f"\n[1] Python: {sys.version.split()[0]} | exe: {sys.executable}")
    print(f"    pylib/ presente: {_ok(os.path.isdir(pylib_dir))}")

    # 2. Dependencias (sistema + pylib)
    todo_ok = True
    for mod in ("requests", "bs4", "pypdf", "reportlab", "PIL"):
        try:
            __import__(mod)
            print(f"    {_ok(True)}  import {mod}")
        except ImportError:
            todo_ok = False
            print(f"    {_ok(False)}  import {mod}  -> pip install -r requirements.txt")
    if not todo_ok:
        print("    (pylib/ cubre requests/bs4/pypdf/reportlab; PIL/pillow requiere pip)")

    # 3. Rutas del proyecto
    for rel in ("data/pea_investigacion.db", "data/snapshots",
                "data/indice_grupos.json", "dist/visualizador_hipercubo.html",
                "dist/dashboard_python.html"):
        p = os.path.join(BASE_DIR, rel)
        print(f"    {_ok(os.path.exists(p))}  {rel}")

    # 4. Estado de la BD (solo lectura)
    try:
        uri = "file:" + db_path.replace("\\", "/") + "?mode=ro"
        c = sqlite3.connect(uri, uri=True, timeout=5.0)
        g = c.execute("SELECT COUNT(*) FROM Grupos").fetchone()[0]
        i = c.execute("SELECT COUNT(*) FROM Investigadores").fetchone()[0]
        p = c.execute("SELECT COUNT(*) FROM Productos").fetchone()[0]
        v = c.execute("SELECT COUNT(*) FROM PerfilInvestigador").fetchone()[0]
        integ = c.execute("PRAGMA integrity_check").fetchone()[0]
        c.close()
        print(f"\n[4] BD: {g} grupos, {i} investigadores, {p} productos, {v} perfiles")
        print(f"    integrity_check: {integ}")
        if g == 0:
            print("    [AVISO] BD vacía: restaure data/pea_investigacion.db desde el ZIP.")
    except Exception as e:
        print(f"\n[4] BD: ERROR al abrir ({e})")

    # 5. Snapshots locales
    try:
        snap_dir = os.path.join(BASE_DIR, "data", "snapshots")
        n_gru, n_cv = 0, 0
        for root, _, fs in os.walk(snap_dir):
            for f in fs:
                if f.startswith("gruplac_") and f.endswith(".html"):
                    n_gru += 1
                elif f.startswith("cvlac_") and f.endswith(".html"):
                    n_cv += 1
        print(f"\n[5] Snapshots: {n_gru} GrupLAC + {n_cv} CvLAC (offline instantáneo)")
    except Exception as e:
        print(f"\n[5] Snapshots: ERROR ({e})")

    # 6. Red hacia MinCiencias (1 GET liviano con timeout corto)
    print("\n[6] Red a MinCiencias (https://scienti.minciencias.gov.co)...")
    try:
        import requests
        t0 = time.time()
        r = requests.get("https://scienti.minciencias.gov.co/",
                         headers={"User-Agent": "PEA-i-diagnostico/1.0"},
                         timeout=15, verify=False)
        dt = time.time() - t0
        print(f"    {_ok(r.status_code < 500)}  HTTP {r.status_code} en {dt:.1f}s")
        if dt > 10:
            print("    [AVISO] Red muy lenta: el scraping en vivo puede agotar timeouts.")
    except Exception as e:
        print(f"    [NO]  sin acceso ({e})")
        print("    Solo funcionará lo offline (snapshots). Revise firewall/proxy/DNS.")

    print("\n" + "=" * 70)
    return True


if __name__ == "__main__":
    ejecutar_diagnostico()
