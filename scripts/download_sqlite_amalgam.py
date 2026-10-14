#!/usr/bin/env python3
"""
Descarga el amalgamado SQLite3 y extrae sqlite3.c + sqlite3.h en src/cpp/
Ejecutar una sola vez desde la raíz del proyecto:
    python3 scripts/download_sqlite_amalgam.py
"""
import os
import sys
import urllib.request
import zipfile
import tempfile

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEST_DIR = os.path.join(BASE_DIR, "src", "cpp")

# URLs candidatas (sqlite.org usa año como subdirectorio)
URLS = [
    "https://www.sqlite.org/2026/sqlite-amalgamation-3540000.zip",
    "https://www.sqlite.org/2025/sqlite-amalgamation-3490000.zip",
    "https://www.sqlite.org/2025/sqlite-amalgamation-3470000.zip",
]

def descargar_amalgamado():
    sqlite3_c = os.path.join(DEST_DIR, "sqlite3.c")
    sqlite3_h = os.path.join(DEST_DIR, "sqlite3.h")

    if os.path.exists(sqlite3_c) and os.path.exists(sqlite3_h):
        size_c = os.path.getsize(sqlite3_c)
        size_h = os.path.getsize(sqlite3_h)
        if size_c > 1_000_000 and size_h > 100_000:
            print(f"[OK] sqlite3.c ({size_c//1024} KB) y sqlite3.h ({size_h//1024} KB) ya existen en src/cpp/")
            return True

    print("[+] Descargando amalgamado SQLite3...")
    tmp_zip = None
    for url in URLS:
        try:
            print(f"    Probando: {url}")
            with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as f:
                tmp_zip = f.name
            urllib.request.urlretrieve(url, tmp_zip)
            size = os.path.getsize(tmp_zip)
            if size < 100_000:
                print(f"    [!] Archivo muy pequeño ({size} bytes), saltando...")
                os.remove(tmp_zip)
                continue
            print(f"    [OK] Descargado: {size//1024} KB")
            break
        except Exception as e:
            print(f"    [!] Error: {e}")
            if tmp_zip and os.path.exists(tmp_zip):
                os.remove(tmp_zip)
            tmp_zip = None
            continue

    if not tmp_zip or not os.path.exists(tmp_zip):
        print("[!] No se pudo descargar el amalgamado.")
        print("    Descárgalo manualmente de: https://www.sqlite.org/download.html")
        print("    (busca 'sqlite-amalgamation-XXXXXXX.zip')")
        print(f"    Extrae sqlite3.c y sqlite3.h en: {DEST_DIR}")
        return False

    try:
        with zipfile.ZipFile(tmp_zip, "r") as z:
            extraidos = 0
            for member in z.namelist():
                nombre = os.path.basename(member)
                if nombre in ("sqlite3.c", "sqlite3.h"):
                    destino = os.path.join(DEST_DIR, nombre)
                    with z.open(member) as src, open(destino, "wb") as dst:
                        dst.write(src.read())
                    size_kb = os.path.getsize(destino) // 1024
                    print(f"    [OK] Extraído: {nombre} ({size_kb} KB) → src/cpp/")
                    extraidos += 1
            if extraidos < 2:
                print("[!] No se encontraron ambos archivos en el ZIP.")
                return False
    finally:
        os.remove(tmp_zip)

    print("[OK] SQLite3 amalgamado listo en src/cpp/")
    print("     La opción [4] del iniciar.bat ahora compila sin -lsqlite3 externo.")
    return True

if __name__ == "__main__":
    ok = descargar_amalgamado()
    sys.exit(0 if ok else 1)
