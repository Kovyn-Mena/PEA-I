# Migra codigos internos (sigla/G+nro) a CCRG/COL originales (S28).
# Uso: python scripts/migrar_col.py [--db data/pea_investigacion.db]
# Actualiza: Grupos PK + FKs (Productos, grupo_investigador, perfiles_grupo),
# data/gisico_semillas.json y primera columna de los CSV (nombre_grupo intacto).
import os
import sys
import json
import csv
import sqlite3

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAPA = {"GISICO": "COL0018706", "G002668": "COL0043834", "G003639": "COL0001351"}


def migrar_db(db):
    conn = sqlite3.connect(db)
    conn.execute("PRAGMA foreign_keys=OFF;")
    n = 0
    for viejo, nuevo in MAPA.items():
        if not conn.execute("SELECT 1 FROM Grupos WHERE codigo_grupo=?;", (viejo,)).fetchone():
            continue
        if conn.execute("SELECT 1 FROM Grupos WHERE codigo_grupo=?;", (nuevo,)).fetchone():
            print("OMITIDO %s: ya existe %s" % (viejo, nuevo))
            continue
        for tbl, col in (("Productos", "codigo_grupo_fk"),
                         ("grupo_investigador", "codigo_grupo_fk"),
                         ("perfiles_grupo", "codigo_grupo")):
            try:
                conn.execute("UPDATE %s SET %s=? WHERE %s=?;" % (tbl, col, col), (nuevo, viejo))
            except Exception as e:
                print("aviso %s: %s" % (tbl, e))
        conn.execute("UPDATE Grupos SET codigo_grupo=? WHERE codigo_grupo=?;", (nuevo, viejo))
        n += 1
        print("MIGRADO %s -> %s" % (viejo, nuevo))
    conn.commit()
    conn.execute("PRAGMA foreign_keys=ON;")
    mal = conn.execute("PRAGMA foreign_key_check;").fetchall()
    print("FK check:", "OK" if not mal else mal)
    conn.close()
    return n


def migrar_archivos():
    sp = os.path.join(BASE, "data", "gisico_semillas.json")
    if os.path.exists(sp):
        d = json.load(open(sp, encoding="utf-8"))
        if d.get("grupo", {}).get("codigo") in MAPA:
            d["grupo"]["codigo"] = MAPA[d["grupo"]["codigo"]]
            json.dump(d, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            print("semillas.json actualizado")
    for fn in ("muestra_upc.csv", "dataset_respaldo.csv"):
        fp = os.path.join(BASE, "data", fn)
        if not os.path.exists(fp):
            continue
        rows = list(csv.reader(open(fp, encoding="utf-8")))
        head, body = rows[0], rows[1:]
        for r in body:
            if r and r[0] in MAPA:
                r[0] = MAPA[r[0]]
        csv.writer(open(fp, "w", encoding="utf-8", newline="")).writerows([head] + body)
        print("CSV actualizado:", fn)


if __name__ == "__main__":
    db = sys.argv[1] if len(sys.argv) > 1 else os.path.join(BASE, "data", "pea_investigacion.db")
    migrar_db(db)
    if db == os.path.join(BASE, "data", "pea_investigacion.db"):
        migrar_archivos()
