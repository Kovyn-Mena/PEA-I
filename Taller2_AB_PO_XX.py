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

def main():
    db_path = os.path.join(BASE_DIR, "data", "pea_investigacion.db")
    app = ConsolaApp(db_path)
    app.iniciar()

if __name__ == "__main__":
    main()
