import sqlite3
import os
import json

DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "pea_investigacion.db")
SCHEMA_PATH = os.path.join(DB_DIR, "schema.sql")
SEMILLAS_PATH = os.path.join(DB_DIR, "gisico_semillas.json")

# Semillas reales GISICO (UPC) extraidas de GrupLAC nro=00000000002099.
# cod_rh ORIGINALES tomados de los href CvLAC de la tabla de integrantes (S17).
# Categorias consultadas 1x1 en CvLAC: Senior/Asociado/Junior reales; resto "No categorizado"
# (CvLAC sin fila de categoria = no reconocido; verificado, no inventado).

def init_database():
    print(f"[INFO] Inicializando base de datos SQLite en: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Activar WAL mode y busy timeout (Blindaje BUG-01)
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute("PRAGMA busy_timeout=5000;")
    cursor.execute("PRAGMA foreign_keys=ON;")

    # Cargar y ejecutar esquema DDL
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    cursor.executescript(schema_sql)

    # Insertar Datos Semilla Reales GISICO (Si no existen)
    cursor.execute("SELECT COUNT(*) FROM Grupos;")
    if cursor.fetchone()[0] == 0:
        print("[INFO] Precargando semillas reales GISICO (GrupLAC 00000000002099)...")
        with open(SEMILLAS_PATH, "r", encoding="utf-8") as f:
            sem = json.load(f)

        g = sem["grupo"]
        cursor.execute(
            "INSERT INTO Grupos (codigo_grupo, nombre, lider, plan_investigacion, lineas_estrategicas) VALUES (?, ?, ?, ?, ?);",
            (g["codigo"], g["nombre"], g["lider"], g["plan"], g["lineas"]))

        for inv in sem["investigadores"]:
            cursor.execute(
                "INSERT OR IGNORE INTO Investigadores (cod_rh, nombre_completo, correo, categoria_minciencias, cvlac_url) VALUES (?, ?, ?, ?, ?);",
                (inv["cod_rh"], inv["nombre"], inv["correo"], inv["categoria"], inv["cvlac"]))
            cursor.execute(
                "INSERT OR IGNORE INTO grupo_investigador (codigo_grupo_fk, cod_rh_fk) VALUES (?, ?);",
                (g["codigo"], inv["cod_rh"]))

        for p in sem["productos"]:
            cursor.execute(
                "INSERT INTO Productos (titulo, tipo_producto, categoria, estado_validacion, anio_publicacion, codigo_grupo_fk, cod_rh_investigador_fk) VALUES (?, ?, ?, ?, ?, ?, ?);",
                (p["titulo"], p["tipo"], p["categoria"], p["validacion"], p["anio"], g["codigo"], p["rh"]))

        conn.commit()
        print(f"[SUCCESS] GISICO: 1 grupo, {len(sem['investigadores'])} investigadores, {len(sem['productos'])} productos.")
    else:
        print("[INFO] La base de datos ya contiene registros. No se duplicaron datos.")
        # Migracion suave: si la BD vieja no tiene la tabla/filas de adscripcion, crearlas
        try:
            cursor.execute("SELECT COUNT(*) FROM grupo_investigador;")
            if cursor.fetchone()[0] == 0:
                print("[INFO] Migrando adscripciones grupo_investigador...")
                with open(SEMILLAS_PATH, "r", encoding="utf-8") as f:
                    sem = json.load(f)
                for inv in sem["investigadores"]:
                    cursor.execute(
                        "INSERT OR IGNORE INTO grupo_investigador (codigo_grupo_fk, cod_rh_fk) VALUES (?, ?);",
                        (sem["grupo"]["codigo"], inv["cod_rh"]))
                conn.commit()
                print("[SUCCESS] Adscripciones migradas.")
        except sqlite3.OperationalError:
            pass

    conn.close()

if __name__ == "__main__":
    init_database()
