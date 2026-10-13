#!/usr/bin/env python3
"""
Punto de Entrada Modular (Python) - PEA-i
Universidad Popular del Cesar — Estructura de Datos
Delega directamente al script raíz de entrega Taller2_AB_PO_XX.py
"""
import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, BASE_DIR)

import Taller2_AB_PO_XX

if __name__ == "__main__":
    Taller2_AB_PO_XX.main()
