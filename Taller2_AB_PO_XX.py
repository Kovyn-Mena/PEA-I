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
from python.core.ingesta import MotorIngesta

def main():
    db_path = os.path.join(BASE_DIR, "data", "pea_investigacion.db")
    args = sys.argv[1:]

    if "--scrape-url" in args:
        idx = args.index("--scrape-url")
        if idx + 1 < len(args):
            url = args[idx + 1]
            motor = MotorIngesta(db_path)
            exito = motor.ejecutar_ingesta("URL", url)
            sys.exit(0 if exito else 1)
        else:
            print("[!] Falta especificar la URL para --scrape-url")
            sys.exit(1)

    elif "--scrape-csv" in args:
        idx = args.index("--scrape-csv")
        if idx + 1 < len(args):
            ruta_csv = args[idx + 1]
            motor = MotorIngesta(db_path)
            exito = motor.ejecutar_ingesta("CSV", ruta_csv)
            sys.exit(0 if exito else 1)
        else:
            print("[!] Falta especificar la ruta del archivo CSV para --scrape-csv")
            sys.exit(1)

    elif "--scrape-pdf" in args:
        idx = args.index("--scrape-pdf")
        if idx + 1 < len(args):
            ruta_pdf = args[idx + 1]
            motor = MotorIngesta(db_path)
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
            motor = MotorIngesta(db_path)
            exito = motor.ejecutar_ingesta(tipo, ruta)
            sys.exit(0 if exito else 1)
        else:
            print("[!] Falta especificar la ruta para --ingesta-archivo")
            sys.exit(1)

    app = ConsolaApp(db_path)
    app.iniciar()

if __name__ == "__main__":
    main()
