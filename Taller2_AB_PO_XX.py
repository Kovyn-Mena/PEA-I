#!/usr/bin/env python3
# =====================================================================
# UNIVERSIDAD POPULAR DEL CESAR - FACULTAD DE INGENIERÍA Y TECNOLÓGICAS
# ASIGNATURA: ESTRUCTURA DE DATOS (TALLER 2) - 2026-I
# DOCENTE: ING. ADITH PÉREZ
# ARCHIVO DE ENTREGA PRINCIPAL PYTHON: Taller2_AB_PO_XX.py
#
# INSTRUCCIONES DE EJECUCIÓN:
#   Opción A (Con Makefile):
#       make run-py
#   Opción B (Directo con Python 3):
#       python3 Taller2_AB_PO_XX.py
# =====================================================================

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, "src"))

from python.console import ConsolaApp

def _crear_motor_ingesta(db_path):
    try:
        from python.core.ingesta import MotorIngesta
        return MotorIngesta(db_path)
    except ImportError as e:
        print(f"\n[!] Dependencias faltantes para ingesta masiva: {e}")
        print("    Para habilitar scraping y procesamiento de PDF ejecute:")
        print("    pip install -r requirements.txt\n")
        return None

def main():
    db_path = os.path.join(BASE_DIR, "data", "pea_investigacion.db")
    args = sys.argv[1:]

    if "--scrape-url" in args:
        idx = args.index("--scrape-url")
        if idx + 1 < len(args):
            url = args[idx + 1]
            motor = _crear_motor_ingesta(db_path)
            if not motor:
                sys.exit(1)
            exito = motor.ejecutar_ingesta("URL", url)
            sys.exit(0 if exito else 1)
        else:
            print("[!] Falta especificar la URL para --scrape-url")
            sys.exit(1)

    elif "--scrape-csv" in args:
        idx = args.index("--scrape-csv")
        if idx + 1 < len(args):
            ruta_csv = args[idx + 1]
            motor = _crear_motor_ingesta(db_path)
            if not motor:
                sys.exit(1)
            exito = motor.ejecutar_ingesta("CSV", ruta_csv)
            sys.exit(0 if exito else 1)
        else:
            print("[!] Falta especificar la ruta del archivo CSV para --scrape-csv")
            sys.exit(1)

    elif "--scrape-pdf" in args:
        idx = args.index("--scrape-pdf")
        if idx + 1 < len(args):
            ruta_pdf = args[idx + 1]
            motor = _crear_motor_ingesta(db_path)
            if not motor:
                sys.exit(1)
            exito = motor.ejecutar_ingesta("PDF", ruta_pdf)
            sys.exit(0 if exito else 1)
        else:
            print("[!] Falta especificar la ruta del archivo PDF para --scrape-pdf")
            sys.exit(1)

    elif "--ingesta-archivo" in args:
        idx = args.index("--ingesta-archivo")
        if idx + 1 < len(args):
            ruta = args[idx + 1]
            tipo = "PDF" if ruta.lower().endswith(".pdf") else "CSV"
            motor = _crear_motor_ingesta(db_path)
            if not motor:
                sys.exit(1)
            exito = motor.ejecutar_ingesta(tipo, ruta)
            sys.exit(0 if exito else 1)
        else:
            print("[!] Falta especificar la ruta para --ingesta-archivo")
            sys.exit(1)

    elif "--gui" in args or "-g" in args:
        from python.gui import DashboardApp
        app_gui = DashboardApp(db_path)
        app_gui.iniciar()
        sys.exit(0)

    elif "--verify" in args:
        from python.core.verificacion_cruzada import ejecutar_verificacion_cruzada
        ok = ejecutar_verificacion_cruzada(db_path)
        sys.exit(0 if ok else 1)

    elif "--buscar-universidad" in args:
        idx = args.index("--buscar-universidad")
        q = args[idx + 1] if idx + 1 < len(args) else ""
        from python.core.busqueda_scienti import buscar_universidad
        res = buscar_universidad(q)
        print(f"=== RESULTADOS BÚSQUEDA UNIVERSIDAD: '{q}' ({len(res)} encontradas) ===")
        for i, c in enumerate(res[:30], 1):
            print(f"UNIV|{i}|{c.get('codinst','')}|{c.get('nombre','')[:70]}|{c.get('n_grupos',0)} grupos")
        sys.exit(0)

    elif "--buscar-grupo" in args:
        idx = args.index("--buscar-grupo")
        q = args[idx + 1] if idx + 1 < len(args) else ""
        from python.core.busqueda_scienti import buscar_grupo_en_indices
        res = buscar_grupo_en_indices(q)
        print(f"=== RESULTADOS BÚSQUEDA GRUPO: '{q}' ({len(res)} encontrados) ===")
        for i, g in enumerate(res[:40], 1):
            print(f"GRUPO|{i}|{g.get('nro','')}|{g.get('col','')}|{g.get('nombre','')[:60]}|Líder: {g.get('lider','')[:30]}|Cat: {g.get('estado','')}")
        sys.exit(0)

    elif "--listar-upc" in args:
        from python.core.busqueda_scienti import listar_grupos_upc
        res = listar_grupos_upc()
        print(f"=== GRUPOS INSTITUCIONALES UNIVERSIDAD POPULAR DEL CESAR ({len(res)} grupos) ===")
        for i, g in enumerate(res, 1):
            print(f"UPC|{i:02d}|{g.get('nro','')}|{g.get('col','')}|{g.get('nombre','')[:55]}|{g.get('lider','')[:25]}|{g.get('estado','')}")
        sys.exit(0)

    elif "--scrape-grupo" in args:
        idx = args.index("--scrape-grupo")
        if idx + 1 < len(args):
            nro = args[idx + 1]
            url = f"https://scienti.minciencias.gov.co/gruplac/jsp/visualiza/visualizagr.jsp?nro={nro}"
            motor = _crear_motor_ingesta(db_path)
            if not motor:
                sys.exit(1)
            exito = motor.ejecutar_ingesta("URL_GRUPLAC", url)
            sys.exit(0 if exito else 1)
        else:
            print("[!] Falta especificar el NRO para --scrape-grupo")
            sys.exit(1)

    elif "--auto-ingest" in args:
        motor = _crear_motor_ingesta(db_path)
        if not motor:
            sys.exit(1)
        ok = motor.ejecutar_ingesta_automatica()
        sys.exit(0 if ok else 1)

    app = ConsolaApp(db_path)
    app.iniciar()

if __name__ == "__main__":
    main()
