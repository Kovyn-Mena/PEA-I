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
    "INICIAR_WINDOWS.bat",
    "compilar_cpp_windows.bat",
    "ejecutar_windows.bat",
    "Documentacion_Tecnica_GrupoXX.docx",
    "Taller2_AB_PO_XX.cpp",
    "Taller2_AB_PO_XX.py",
    os.path.join("dist", "visualizador_hipercubo.html")
]

DIRS_TO_INCLUDE = [
    "src",
    "data",
    "docs",
    "reportes",
    "scripts"
]

SKIP_PATTERNS = [
    ".git",
    "__pycache__",
    ".pytest_cache",
    "build",
    "dist",
    ".env",
    "pea_cpp",
    "test_tda",
    "test_sqlite",
    ".o",
    ".obj",
    ".exe",
    ".pyc",
    ".DS_Store"
]

def empaquetar():
    if os.path.exists(ZIP_NAME):
        os.remove(ZIP_NAME)

    print(f"[+] Creando archivo de entrega ZIP: {os.path.basename(ZIP_NAME)}...")
    with zipfile.ZipFile(ZIP_NAME, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in FILES_TO_INCLUDE:
            p = os.path.join(BASE_DIR, f)
            if os.path.exists(p):
                zf.write(p, arcname=f)

        for d in DIRS_TO_INCLUDE:
            dir_path = os.path.join(BASE_DIR, d)
            if not os.path.exists(dir_path):
                continue
            for root, _, filenames in os.walk(dir_path):
                if any(skip in root for skip in SKIP_PATTERNS):
                    continue
                for file in filenames:
                    if any(file.endswith(ext) for ext in [".o", ".obj", ".exe", ".pyc", ".gitkeep"]) or file in SKIP_PATTERNS:
                        continue
                    full_p = os.path.join(root, file)
                    rel_p = os.path.relpath(full_p, BASE_DIR)
                    zf.write(full_p, arcname=rel_p)

    size_kb = round(os.path.getsize(ZIP_NAME) / 1024, 1)
    print(f"[OK] Archivo de entrega generado exitosamente:")
    print(f"     • Ruta: {ZIP_NAME}")
    print(f"     • Tamaño: {size_kb} KB")
    print(f"     • Listo para adjuntar y enviar a adithperez@unicesar.edu.co")

if __name__ == "__main__":
    empaquetar()
