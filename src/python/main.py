#!/usr/bin/env python3
"""
Punto de Entrada Principal (Python) - PEA-i
Universidad Popular del Cesar
"""
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, ".."))

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
    db_path = os.path.join(BASE_DIR, "..", "..", "data", "pea_investigacion.db")
    if not os.path.exists(db_path):
        db_path = "data/pea_investigacion.db"

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

    app = ConsolaApp(db_path)
    app.iniciar()

if __name__ == "__main__":
    main()
