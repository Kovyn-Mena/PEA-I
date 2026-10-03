# Limpieza de titulos con artefactos del parseo (S29).
# 1) Quita prefijos ": ; , . — -" heredados del HTML.
# 2) Elimina filas "pais, AAAA," sin titulo real (basura del parseo, sin dato recuperable).
# 3) Fusiona duplicados exactos (titulo+anio+grupo+rh) quedandose con el id menor.
# Uso: python scripts/limpiar_titulos.py [--db data/pea_investigacion.db]
# Nada referencia Productos.id_producto como FK: borrar filas es seguro.
import os
import re
import sqlite3
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAIS_ANIO = re.compile(r"^[A-Za-záéíóúñü]+\s*,\s*(?:19|20)\d{2}\s*,?$")


def limpiar(t):
    return t.strip().lstrip(":;,.—- ").strip()


def main():
    db = sys.argv[1] if len(sys.argv) > 1 else os.path.join(BASE, "data", "pea_investigacion.db")
    conn = sqlite3.connect(db)
    n_upd = n_del_basura = n_del_dup = 0
    for pid, titulo in conn.execute("SELECT id_producto, titulo FROM Productos;").fetchall():
        if PAIS_ANIO.match((titulo or "").strip()):
            conn.execute("DELETE FROM Productos WHERE id_producto=?;", (pid,))
            n_del_basura += 1
            print(("BASURA id=%d %s" % (pid, (titulo or "")[:50])).replace("�", "?"))
        else:
            c = limpiar(titulo or "")
            if c != titulo:
                conn.execute("UPDATE Productos SET titulo=? WHERE id_producto=?;", (c, pid))
                n_upd += 1
    for titulo, anio, grp, rh, n, keep in conn.execute(
            "SELECT titulo, anio_publicacion, codigo_grupo_fk, cod_rh_investigador_fk,"
            " COUNT(*), MIN(id_producto) FROM Productos"
            " GROUP BY titulo, anio_publicacion, codigo_grupo_fk, cod_rh_investigador_fk"
            " HAVING COUNT(*) > 1;").fetchall():
        cur = conn.execute("DELETE FROM Productos WHERE titulo=? AND anio_publicacion=?"
                           " AND codigo_grupo_fk=? AND cod_rh_investigador_fk=? AND id_producto<>?;",
                           (titulo, anio, grp, rh, keep))
        n_del_dup += cur.rowcount
        print(("DUP '%s' (%s) x%d -> queda id=%d" % (titulo[:45], anio, n, keep)).replace("�", "?"))
    conn.commit()
    print("limpiados=%d basura=%d duplicados=%d" % (n_upd, n_del_basura, n_del_dup))
    print("fk:", conn.execute("PRAGMA foreign_key_check;").fetchall())
    conn.close()


if __name__ == "__main__":
    main()
