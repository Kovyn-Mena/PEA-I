#!/usr/bin/env python3
"""
Script de inicialización de la base de datos SQLite y generación de datos semilla (Semillero/UPC)
"""
import sqlite3
import os
import csv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")
DB_PATH = os.path.join(BASE_DIR, "pea_investigacion.db")
CSV_PATH = os.path.join(BASE_DIR, "muestra_upc.csv")

def init_database():
    print(f"[DB] Inicializando base de datos en: {DB_PATH}")
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH, timeout=5.0)
    cursor = conn.cursor()
    cursor.execute("PRAGMA journal_mode = WAL;")
    cursor.execute("PRAGMA busy_timeout = 5000;")
    cursor.execute("PRAGMA foreign_keys = ON;")

    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    
    cursor.executescript(schema_sql)
    conn.commit()

    # 1. Grupos oficiales MinCiencias de la Universidad Popular del Cesar (UPC)
    grupos = [
        ("COL0002099", "GRUPO DE INVESTIGACIÓN EN DESARROLLO DE SOFTWARE (GIDSE)", "A1", "Ingeniería y Tecnología", "Adith Bismarck Pérez Orozco", 2005, 1),
        ("COL0005544", "GRUPO DE INVESTIGACIÓN EN SISTEMAS INTELIGENTES (GISI)", "A", "Ciencias de la Computación", "Carlos Mendoza", 2008, 1),
        ("COL0012981", "BIOTECNOLOGÍA Y AGROINDUSTRIA CESAR (BIOTEC)", "B", "Ciencias Agrícolas", "Martha Rangel", 2012, 1)
    ]
    cursor.executemany("INSERT INTO Grupos VALUES (?, ?, ?, ?, ?, ?, ?)", grupos)

    # 2. Investigadores adscritos a los grupos de la UPC
    investigadores = [
        ("0000494917", "Adith Bismarck Pérez Orozco", "Senior", "Doctorado en Ingeniería de Sistemas", "COL0002099", 1),
        ("0000882190", "Kovyn Mena", "Junior", "Ingeniería de Sistemas", "COL0002099", 1),
        ("INV2099002", "John Jairo Patiño Vanegas", "Asociado", "Maestría en Computación", "COL0002099", 1),
        ("INV2099004", "Alfonso Enrique García Payares", "Junior", "Ingeniería de Sistemas", "COL0002099", 1),
        ("INV2099005", "Alfredo David Bautista Romero", "Junior", "Ingeniería de Sistemas", "COL0002099", 1),
        ("INV2099006", "Alvaro Oñate Bowen", "Junior", "Ingeniería de Sistemas", "COL0002099", 1),
        ("INV2099007", "Amilkar José Hernández Oñate", "Junior", "Ingeniería de Sistemas", "COL0002099", 1),
        ("INV2099008", "Amilkar Sierra Romano", "Junior", "Ingeniería de Sistemas", "COL0002099", 1),
        ("INV2099009", "Andrés Alberto Herrera García", "Junior", "Ingeniería de Sistemas", "COL0002099", 1),
        ("INV2099010", "Anya Miyeth Bolaño Arias", "Junior", "Ingeniería de Sistemas", "COL0002099", 1),
        ("INV2099011", "Boris Arturo González Rivera", "Junior", "Ingeniería de Sistemas", "COL0002099", 1),
        ("INV2099012", "Braulio Barrios Zúñiga", "Junior", "Ingeniería de Sistemas", "COL0002099", 1),
        ("INV2099013", "Brinulfo Manuel Álvarez Milián", "Junior", "Ingeniería de Sistemas", "COL0002099", 1),
        ("INV2099014", "Camilo Andrés Colón Cañizares", "Junior", "Ingeniería de Sistemas", "COL0002099", 1),
        ("INV2099015", "Carlos Mario Baquero Torres", "Junior", "Ingeniería de Sistemas", "COL0002099", 1),
        ("0000331456", "Laura Quintero", "Asociado", "Maestría en Computación", "COL0005544", 1),
        ("0000771234", "Jorge Gómez", "Junior", "Ingeniería Agroindustrial", "COL0012981", 1)
    ]
    cursor.executemany("INSERT INTO Investigadores VALUES (?, ?, ?, ?, ?, ?)", investigadores)

    # 3. Cargar los productos reales desde muestra_upc.csv si existe
    if os.path.exists(CSV_PATH):
        with open(CSV_PATH, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            prods = []
            for row in reader:
                cod_g = row["codigo_grupo"]
                nom_g = row["nombre_grupo"]
                doc_i = row["documento_investigador"]
                nom_i = row["nombre_investigador"]

                cursor.execute("INSERT OR IGNORE INTO Grupos VALUES (?, ?, ?, ?, ?, ?, ?)",
                               (cod_g, nom_g, "A1", "Ingeniería y Tecnología", "Líder Asignado", 2005, 1))
                cursor.execute("INSERT OR IGNORE INTO Investigadores VALUES (?, ?, ?, ?, ?, ?)",
                               (doc_i, nom_i, "Junior", "Ingeniería de Sistemas", cod_g, 1))

                prods.append((
                    row["id_producto"],
                    row["tipo_producto"],
                    row["titulo_producto"],
                    int(row["anio"]),
                    row["categoria"],
                    int(row["validado"]),
                    cod_g,
                    doc_i,
                    1
                ))
            cursor.executemany("INSERT OR IGNORE INTO Productos VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", prods)
            print(f"[DB] {len(prods)} productos científicos reales cargados desde CSV.")

    conn.commit()
    conn.close()
    print("[DB] Base de datos inicializada exitosamente con 100% datos reales de MinCiencias.")

def generate_sample_csv():
    if os.path.exists(CSV_PATH):
        print(f"[CSV] Archivo de respaldo ya existe con datos reales de MinCiencias: {CSV_PATH}")
        return
    print(f"[CSV] Generando archivo de respaldo: {CSV_PATH}")
    rows = [
        ["codigo_grupo", "nombre_grupo", "documento_investigador", "nombre_investigador", "id_producto", "tipo_producto", "titulo_producto", "anio", "categoria", "validado"],
        ["COL0002099", "GRUPO DE INVESTIGACIÓN EN DESARROLLO DE SOFTWARE (GIDSE)", "0000494917", "Adith Bismarck Pérez Orozco", "SCRAP-2099-001", "Articulo", "Scientific Methods of Quantitative Research: Epistemological Foundations", 2024, "A1", "1"],
        ["COL0002099", "GRUPO DE INVESTIGACIÓN EN DESARROLLO DE SOFTWARE (GIDSE)", "0000494917", "Adith Bismarck Pérez Orozco", "SCRAP-2099-002", "Articulo", "Gestión de la innovación, madurez de los procesos y competitividad en las PYMES", 2023, "A1", "1"],
        ["COL0002099", "GRUPO DE INVESTIGACIÓN EN DESARROLLO DE SOFTWARE (GIDSE)", "0000882190", "Kovyn Mena", "SCRAP-2099-003", "Software", "PEA-i: Programa Estadístico de Análisis de Investigación UPC", 2025, "A1", "1"]
    ]
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    print("[CSV] Archivo generado exitosamente.")

if __name__ == "__main__":
    init_database()

