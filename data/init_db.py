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

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    
    cursor.executescript(schema_sql)
    conn.commit()

    # Datos iniciales reales de la Universidad Popular del Cesar (Ejemplo ilustrativo)
    grupos = [
        ("COL0002099", "GRUPO DE INVESTIGACIÓN EN DESARROLLO DE SOFTWARE (GIDSE)", "A1", "Ingeniería y Tecnología", "Adith Pérez", 2005, 1),
        ("COL0005544", "GRUPO DE INVESTIGACIÓN EN SISTEMAS INTELIGENTES (GISI)", "A", "Ciencias de la Computación", "Carlos Mendoza", 2008, 1),
        ("COL0012981", "BIOTECNOLOGÍA Y AGROINDUSTRIA CESAR", "B", "Ciencias Agrícolas", "Martha Rangel", 2012, 1)
    ]
    cursor.executemany("INSERT INTO Grupos VALUES (?, ?, ?, ?, ?, ?, ?)", grupos)

    investigadores = [
        ("0000494917", "Adith Pérez", "Senior", "Doctorado en Ingeniería de Sistemas", "COL0002099", 1),
        ("0000882190", "Kovyn Mena", "Junior", "Ingeniería de Sistemas", "COL0002099", 1),
        ("0000331456", "Laura Quintero", "Asociado", "Maestría en Computación", "COL0005544", 1),
        ("0000771234", "Jorge Gómez", "Junior", "Ingeniería Agroindustrial", "COL0012981", 1)
    ]
    cursor.executemany("INSERT INTO Investigadores VALUES (?, ?, ?, ?, ?, ?)", investigadores)

    productos = [
        ("PROD-001", "Articulo", "Modelo de hipercubo para análisis multidimensional en MinCiencias", 2024, "A1", 1, "COL0002099", "0000494917", 1),
        ("PROD-002", "Software", "PEA-i: Sistema de analítica institucional de investigación", 2025, "A1", 1, "COL0002099", "0000882190", 1),
        ("PROD-003", "Articulo", "Algoritmos genéticos aplicados a la clasificación de grupos MinCiencias", 2023, "A", 1, "COL0005544", "0000331456", 1),
        ("PROD-004", "Capitulo", "Perspectivas tecnológicas en el departamento del Cesar", 2022, "B", 0, "COL0002099", "0000494917", 1),
        ("PROD-005", "Libro", "Fundamentos de Estructuras de Datos aplicadas a grafos y multilistas", 2021, "A1", 1, "COL0002099", "0000494917", 1),
        ("PROD-006", "Articulo", "Bioinformática en cultivos del Cesar mediante redes neuronales", 2025, "A", 1, "COL0012981", "0000771234", 1)
    ]
    cursor.executemany("INSERT INTO Productos VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", productos)

    conn.commit()
    conn.close()
    print("[DB] Base de datos creada con 3 grupos, 4 investigadores y 6 productos.")

def generate_sample_csv():
    print(f"[CSV] Generando archivo de respaldo: {CSV_PATH}")
    rows = [
        ["codigo_grupo", "nombre_grupo", "documento_investigador", "nombre_investigador", "id_producto", "tipo_producto", "titulo_producto", "anio", "categoria", "validado"],
        ["COL0002099", "GIDSE", "0000494917", "Adith Pérez", "CSV-001", "Articulo", "Estructuras enlazadas y persistencia", 2024, "A1", "1"],
        ["COL0002099", "GIDSE", "0000882190", "Kovyn Mena", "CSV-002", "Software", "Módulo de web scraping para GrupLAC", 2025, "A", "1"],
        ["COL0005544", "GISI", "0000331456", "Laura Quintero", "CSV-003", "Capitulo", "Procesamiento de lenguaje natural en MinCiencias", 2023, "B", "0"]
    ]
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    print("[CSV] Archivo generado exitosamente.")

if __name__ == "__main__":
    init_database()
    generate_sample_csv()
