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

def main():
    db_path = os.path.join(BASE_DIR, "..", "..", "data", "pea_investigacion.db")
    # Normalizar ruta
    if not os.path.exists(db_path):
        db_path = "data/pea_investigacion.db"
    app = ConsolaApp(db_path)
    app.iniciar()

if __name__ == "__main__":
    main()
