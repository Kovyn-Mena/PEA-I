# Migracion de encoding SCIENTI (S30).
# Causa: el codigo forzaba utf-8 pero SCIENTI declara iso-8859-1.
# Lo nuevo ya sale limpio (codificacion_respuesta -> windows-1252),
# pero la BD real quedo sucia: 132/248 productos y 56/236 investigadores con �.
# Este script hace el rescrape limpio a temporal + UPDATE in place:
#   - investigadores por cod_rh, grupos por codigo COL (o nombre si cambio sigla),
#   - productos por fuzzy (titulo, mismo grupo+rh+anio, umbral 0.82),
#   - solo pisa donde el real tiene � y el temporal viene limpio,
#   - refresca gisico_semillas.json y CSVs con el mismo mapa viejo->nuevo.
# Uso:
#   python scripts/migrar_encoding.py [--db data/pea_investigacion.db] [--solo-informe]
#   python scripts/migrar_encoding.py --nros 00000000002099,00000000002668,00000000003639
import os
import sys
import json
import csv
import shutil
import sqlite3
import tempfile
import argparse
import difflib
import datetime

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)
sys.path.insert(0, os.path.join(BASE, "pylib"))
import Taller2_KM_PO_XX as pea

RARO = "\ufffd"
# Nros detectados de data/snapshots/gruplac_*.html:
# 2099=GISICO COL0018706, 2668=AITICE COL0043834, 3639=GIELEHLA COL0001351
NROS_DEF = ["00000000002099", "00000000002668", "00000000003639"]


def tiene_raro(s):
    return bool(s) and RARO in (s or "")


def contar_raros(db):
    conn = sqlite3.connect(db)
    out = {}
    for tabla, col in (("Grupos", "lider"), ("Grupos", "nombre"),
                       ("Investigadores", "nombre_completo"),
                       ("Productos", "titulo")):
        try:
            filas = conn.execute("SELECT %s FROM %s;" % (col, tabla)).fetchall()
            out["%s.%s" % (tabla, col)] = sum(1 for (v,) in filas if tiene_raro(v))
        except Exception as e:
            out["%s.%s" % (tabla, col)] = "err:%s" % e
    conn.close()
    return out


def crear_temp_db():
    fd, tmp = tempfile.mkstemp(prefix="pea_limpio_", suffix=".db")
    os.close(fd)
    conn = sqlite3.connect(tmp)
    with open(os.path.join(BASE, "data", "schema.sql"), encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    return tmp


def rescrape_a_temporal(nros, temp_db):
    ok, fallos = [], []
    for nro in nros:
        try:
            # usar_snapshot=False = red limpia con codificacion_respuesta (S30).
            r = pea.scrape_grupo(nro, temp_db, usar_snapshot=False, con_cvlac=False)
            if r:
                ok.append(nro)
            else:
                fallos.append(nro)
        except Exception as e:
            print("ERROR red %s: %s" % (nro, e))
            fallos.append(nro)
    return ok, fallos


def rescrape_cvlac_a_temporal(rhs_list, temp_db, grupo=""):
    """Segunda fase S30: productos CvLAC-origen (no salen en ficha GrupLAC).
    Fuerza red limpia (borra snapshot sucio para no reusar �)."""
    ok, fallos = [], []
    for rh in rhs_list:
        snap = os.path.join(pea.SNAP_DIR, "cvlac_%s.html" % rh)
        bak = ""
        try:
            if os.path.exists(snap):
                bak = snap + ".sucio-bak"
                shutil.move(snap, bak)
            r = pea.scrape_cvlac(rh, temp_db, grupo)
            if r:
                ok.append(rh)
            else:
                fallos.append(rh)
        except Exception as e:
            print("ERROR cvlac %s: %s" % (rh, e))
            fallos.append(rh)
        finally:
            # No restaurar el snapshot sucio: el fresco ya quedo en cache_fuentes.
            # Si el scrape fallo, devolver el bak para no perder nada.
            if bak and os.path.exists(bak) and rh in fallos:
                shutil.move(bak, snap)
            elif bak and os.path.exists(bak):
                try:
                    os.remove(bak)
                except Exception:
                    pass
    return ok, fallos


def leer_temporal(temp_db):
    conn = sqlite3.connect(temp_db)
    grupos = {}
    for cg, nom, lid, plan, lin in conn.execute(
            "SELECT codigo_grupo, nombre, lider, plan_investigacion, lineas_estrategicas FROM Grupos;"):
        grupos[cg] = {"nombre": nom, "lider": lid, "plan": plan, "lineas": lin}
        grupos[pea.sin_raros(pea._norm_txt(nom))] = grupos[cg]
    invs = {}
    for rh, nom in conn.execute("SELECT cod_rh, nombre_completo FROM Investigadores;"):
        invs[rh] = nom
    prods = []
    for pid, tit, anio, grp, rh in conn.execute(
            "SELECT id_producto, titulo, anio_publicacion, codigo_grupo_fk,"
            " cod_rh_investigador_fk FROM Productos;"):
        prods.append((tit, anio, grp, rh))
    conn.close()
    return grupos, invs, prods


def mejor_titulo(candidatos, objetivo_norm):
    best, best_score = None, 0.0
    for tit in candidatos:
        s = difflib.SequenceMatcher(None, objetivo_norm, pea._norm_txt(tit)).ratio()
        if s > best_score:
            best, best_score = tit, s
    return best, best_score


def migrar(db, grupos_t, invs_t, prods_t, umbral, solo_informe):
    conn = sqlite3.connect(db)
    n_g = n_i = n_p = 0
    mapa = {}  # texto viejo -> texto nuevo (para semillas/CSVs)
    # 1) Grupos por codigo; si el temporal trajo otra sigla, cae por nombre sin raros.
    for cg, nom, lid in conn.execute("SELECT codigo_grupo, nombre, lider FROM Grupos;").fetchall():
        nuevo = grupos_t.get(cg)
        if nuevo is None:
            nuevo = grupos_t.get(pea.sin_raros(pea._norm_txt(nom or "")))
        if not nuevo:
            continue
        cambios, params = [], []
        if tiene_raro(nom) and nuevo["nombre"] and not tiene_raro(nuevo["nombre"]):
            cambios.append("nombre=?")
            params.append(nuevo["nombre"])
            mapa[nom] = nuevo["nombre"]
        if tiene_raro(lid) and nuevo["lider"] and not tiene_raro(nuevo["lider"]):
            cambios.append("lider=?")
            params.append(nuevo["lider"])
            mapa[lid] = nuevo["lider"]
        if cambios and not solo_informe:
            conn.execute("UPDATE Grupos SET %s WHERE codigo_grupo=?;" % ",".join(cambios),
                         tuple(params) + (cg,))
            n_g += 1
        elif cambios:
            n_g += 1
    # 2) Investigadores por cod_rh directo.
    for rh, nom in conn.execute("SELECT cod_rh, nombre_completo FROM Investigadores;").fetchall():
        limpio = invs_t.get(rh)
        if limpio and tiene_raro(nom) and not tiene_raro(limpio):
            if not solo_informe:
                conn.execute("UPDATE Investigadores SET nombre_completo=? WHERE cod_rh=?;",
                             (limpio, rh))
            mapa[nom] = limpio
            n_i += 1
    # 3) Productos por fuzzy (mismo grupo+rh+anio; fallback por grupo+anio
    # para coautorias con rh distinto: mismo titulo limpio atribuido a otro coautor).
    por_clave = {}
    por_grupo_anio = {}
    for tit, anio, grp, rh in prods_t:
        if tiene_raro(tit):
            continue
        por_clave.setdefault((grp, rh, anio), []).append(tit)
        por_grupo_anio.setdefault((grp, anio), []).append(tit)
    for pid, tit, anio, grp, rh in conn.execute(
            "SELECT id_producto, titulo, anio_publicacion, codigo_grupo_fk,"
            " cod_rh_investigador_fk FROM Productos;").fetchall():
        if not tiene_raro(tit):
            continue
        cands = por_clave.get((grp, rh, anio), [])
        if cands:
            best, score = mejor_titulo(cands, pea.sin_raros(pea._norm_txt(tit)))
            if best and score >= umbral:
                if not solo_informe:
                    conn.execute("UPDATE Productos SET titulo=? WHERE id_producto=?;", (best, pid))
                mapa[tit] = best
                n_p += 1
                continue
        # Fallback coautoria: mismo grupo+anio, umbral alto 0.90 (solo titulo, sin tocar rh).
        cands2 = por_grupo_anio.get((grp, anio), [])
        if cands2:
            best2, score2 = mejor_titulo(cands2, pea.sin_raros(pea._norm_txt(tit)))
            if best2 and score2 >= max(umbral, 0.90):
                if not solo_informe:
                    conn.execute("UPDATE Productos SET titulo=? WHERE id_producto=?;", (best2, pid))
                mapa[tit] = best2
                n_p += 1
    if not solo_informe:
        conn.commit()
    mal = conn.execute("PRAGMA foreign_key_check;").fetchall()
    conn.close()
    return n_g, n_i, n_p, mapa, mal


def refrescar_archivos(mapa):
    tocados = []
    if not mapa:
        return tocados
    # semillas JSON (texto exacto)
    sp = os.path.join(BASE, "data", "gisico_semillas.json")
    if os.path.exists(sp):
        txt = open(sp, encoding="utf-8").read()
        nuevo = txt
        for viejo, limpio in mapa.items():
            if viejo in nuevo:
                nuevo = nuevo.replace(viejo, limpio)
        if nuevo != txt:
            open(sp, "w", encoding="utf-8").write(nuevo)
            tocados.append("gisico_semillas.json")
    for fn in ("muestra_upc.csv", "dataset_respaldo.csv"):
        fp = os.path.join(BASE, "data", fn)
        if not os.path.exists(fp):
            continue
        txt = open(fp, encoding="utf-8").read()
        nuevo = txt
        for viejo, limpio in mapa.items():
            if viejo in nuevo:
                nuevo = nuevo.replace(viejo, limpio)
        if nuevo != txt:
            open(fp, "w", encoding="utf-8", newline="").write(nuevo)
            tocados.append(fn)
    return tocados


def main():
    ap = argparse.ArgumentParser(description="Migracion encoding S30 (rescrape limpio + UPDATE).")
    ap.add_argument("--db", default=os.path.join(BASE, "data", "pea_investigacion.db"))
    ap.add_argument("--nros", default=",".join(NROS_DEF))
    ap.add_argument("--umbral", type=float, default=0.82)
    ap.add_argument("--solo-informe", action="store_true",
                    help="rescrapea a temporal e informa cuantos se arreglarian, sin tocar la real")
    ap.add_argument("--sin-archivos", action="store_true")
    ap.add_argument("--fase-cvlac", action="store_true",
                    help="segunda fase: rescrapea CvLAC de los rh con titulos aun sucios")
    a = ap.parse_args()
    nros = [x.strip() for x in a.nros.split(",") if x.strip()]
    print("Antes:", contar_raros(a.db))
    temp_db = crear_temp_db()
    try:
        if a.fase_cvlac:
            conn0 = sqlite3.connect(a.db)
            rhs = sorted({r for (r,) in conn0.execute(
                "SELECT DISTINCT cod_rh_investigador_fk FROM Productos;").fetchall()
                if conn0.execute("SELECT COUNT(*) FROM Productos WHERE cod_rh_investigador_fk=? AND titulo LIKE '%'||x'efbfbd'||'%';", (r,)).fetchone()[0] > 0})
            # fallback si LIKE no caza por encoding: barrido python
            if not rhs:
                rhs = sorted({rh for _, _, _, _, rh in
                              [(pid, t, an, g, r) for pid, t, an, g, r in
                               conn0.execute("SELECT id_producto, titulo, anio_publicacion, codigo_grupo_fk, cod_rh_investigador_fk FROM Productos;").fetchall()]
                              if tiene_raro(_[1])})
            conn0.close()
            print("rhs con raro:", rhs)
            ok, fallos = rescrape_cvlac_a_temporal(rhs, temp_db)
            print("cvlac ok=%d fallos=%s" % (len(ok), fallos))
            if not ok:
                print("Sin datos CvLAC de red: no se toca la BD real.")
                return 1
        else:
            ok, fallos = rescrape_a_temporal(nros, temp_db)
            print("rescrape ok=%s fallos=%s" % (ok, fallos))
            if not ok:
                print("Sin datos limpios de red: no se toca la BD real."
                      " Revise conexion a SCIENTI e intente de nuevo.")
                return 1
        grupos_t, invs_t, prods_t = leer_temporal(temp_db)
        print("temporal: grupos=%d investigadores=%d productos=%d"
              % (len([k for k in grupos_t if not k.startswith(" ")]), len(invs_t), len(prods_t)))
        n_g, n_i, n_p, mapa, mal = migrar(a.db, grupos_t, invs_t, prods_t, a.umbral, a.solo_informe)
        print("grupos=%d investigadores=%d productos=%d (umbral fuzzy %s)%s"
              % (n_g, n_i, n_p, a.umbral, " [SOLO INFORME]" if a.solo_informe else ""))
        tocados = []
        if mapa and not a.solo_informe and not a.sin_archivos:
            # backup antes de tocar archivos
            stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            bk = a.db + ".bak-%s" % stamp
            conn = sqlite3.connect(a.db)
            conn.execute("PRAGMA wal_checkpoint(TRUNCATE);")
            conn.close()
            shutil.copy2(a.db, bk)
            print("backup:", bk)
            tocados = refrescar_archivos(mapa)
            print("archivos refrescados:", tocados if tocados else "ninguno")
        print("FK check:", "OK" if not mal else mal)
        print("Despues:", contar_raros(a.db))
        return 0
    finally:
        try:
            os.remove(temp_db)
        except Exception:
            pass


if __name__ == "__main__":
    sys.exit(main())
