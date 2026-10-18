#!/usr/bin/env python3
"""
=====================================================================
PEA-i: PURGA CONTROLADA DE GRUPOS (VACÍOS / NO-UPC / HUÉRFANOS)
Universidad Popular del Cesar — Estructura de Datos (Taller 2)
=====================================================================
Borra de data/pea_investigacion.db:

  1. Grupos sin investigadores y sin productos (53 en la auditoría).
  2. Grupos cuyo código no pertenece a la lista autoritativa UPC
     (ScienTI codInst=947 ∪ Datos Abiertos hrhc-c4wu).
  3. Grupos con productos cuyo autor pertenece a otro grupo
     (caso COL0027788: 438 productos con autor de GISICO).

Siempre escribe data/purga_reporte.csv. Por defecto NO borra:
hace falta --confirmar. Antes de borrar crea un backup con la API
de backup de SQLite (incluye WAL).

Uso:
    python3 scripts/purgar_grupos.py                 # simulación
    python3 scripts/purgar_grupos.py --confirmar     # aplica la purga
=====================================================================
"""

import argparse
import csv
import datetime
import os
import sqlite3
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "src"))
sys.path.insert(0, os.path.join(BASE_DIR, "pylib"))

from python.core.reconciliacion import (  # noqa: E402
    descargar_socrata_upc,
    lista_upc_autoritativa,
)

DB_PATH = os.path.join(BASE_DIR, "data", "pea_investigacion.db")
BACKUP_DIR = os.path.join(BASE_DIR, "data", "backup")
REPORTE = os.path.join(BASE_DIR, "data", "purga_reporte.csv")

# Grupo UPC con productos asignados a autores de otro grupo. Se borra y se
# vuelve a cargar en vivo (es un grupo real de la UPC).
GRUPO_HUERFANO = "COL0027788"


def _leer_grupos(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        filas = conn.execute(
            """
            SELECT g.codigo_grupo, g.nombre, g.lider,
                   (SELECT COUNT(*) FROM Investigadores i
                     WHERE i.codigo_grupo = g.codigo_grupo) AS n_inv,
                   (SELECT COUNT(*) FROM Productos p
                     WHERE p.codigo_grupo = g.codigo_grupo) AS n_prod,
                   (SELECT COUNT(*) FROM Productos p
                     WHERE p.codigo_grupo = g.codigo_grupo
                       AND NOT EXISTS (
                           SELECT 1 FROM Investigadores i
                            WHERE i.documento_id = p.id_investigador
                              AND i.codigo_grupo = p.codigo_grupo)) AS n_huerfanos
              FROM Grupos g
             ORDER BY g.codigo_grupo
            """
        ).fetchall()
        return [dict(f) for f in filas]
    finally:
        conn.close()


def _backup(db_path):
    os.makedirs(BACKUP_DIR, exist_ok=True)
    sello = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = os.path.join(BACKUP_DIR, f"pea_investigacion_{sello}.db")
    origen = sqlite3.connect(db_path)
    respaldo = sqlite3.connect(destino)
    try:
        origen.backup(respaldo)
    finally:
        respaldo.close()
        origen.close()
    return destino


def main():
    ap = argparse.ArgumentParser(description="Purga controlada de grupos PEA-i")
    ap.add_argument("--db", default=DB_PATH)
    ap.add_argument("--confirmar", action="store_true",
                    help="aplica los borrados (sin esto solo simula)")
    ap.add_argument("--sin-red", action="store_true",
                    help="no consulta datos.gov.co; usa solo la caché ScienTI")
    args = ap.parse_args()

    if not os.path.exists(args.db):
        print(f"[!] No existe la base de datos: {args.db}")
        return 1

    # 1. Lista autoritativa UPC
    socrata = {}
    error_red = ""
    if not args.sin_red:
        try:
            socrata = descargar_socrata_upc(timeout=25)
        except Exception as e:
            error_red = str(e)
    autoritativos = lista_upc_autoritativa(socrata)
    upc = set(autoritativos)

    # 2. Clasificar cada grupo
    grupos = _leer_grupos(args.db)
    filas_reporte = []
    a_borrar = []
    for g in grupos:
        col = g["codigo_grupo"]
        motivo = ""
        if g["n_huerfanos"] > 0:
            motivo = "productos_con_autor_ajeno"
        elif g["n_inv"] == 0 and g["n_prod"] == 0:
            motivo = "vacio_sin_investigadores_ni_productos"
        elif col not in upc:
            motivo = "no_pertenece_a_la_upc"
        accion = "BORRAR" if motivo else "CONSERVAR"
        if accion == "BORRAR":
            a_borrar.append((col, motivo))
        filas_reporte.append({
            "codigo": col,
            "nombre": g["nombre"],
            "investigadores": g["n_inv"],
            "productos": g["n_prod"],
            "productos_con_autor_ajeno": g["n_huerfanos"],
            "en_scienti_upc": "si" if col in autoritativos and autoritativos[col]["en_scienti"] else "no",
            "en_datos_abiertos_upc": "si" if col in autoritativos and autoritativos[col]["en_socrata"] else "no",
            "accion": accion,
            "motivo": motivo,
        })

    # 3. Reporte (siempre)
    os.makedirs(os.path.dirname(REPORTE), exist_ok=True)
    columnas = ["codigo", "nombre", "investigadores", "productos",
                "productos_con_autor_ajeno", "en_scienti_upc",
                "en_datos_abiertos_upc", "accion", "motivo"]
    with open(REPORTE, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columnas)
        w.writeheader()
        w.writerows(filas_reporte)

    # 4. Resumen
    por_motivo = {}
    for _, motivo in a_borrar:
        por_motivo[motivo] = por_motivo.get(motivo, 0) + 1
    print("=" * 65)
    print("   PURGA CONTROLADA DE GRUPOS — PEA-i")
    print("=" * 65)
    if error_red:
        print(f"[!] Sin conexión a datos.gov.co ({error_red}); usando caché ScienTI.")
    print(f"• Grupos autoritativos UPC: {len(autoritativos)}")
    print(f"• Grupos en la BD:          {len(grupos)}")
    print(f"• A borrar:                 {len(a_borrar)}")
    for motivo, n in sorted(por_motivo.items()):
        print(f"    - {motivo}: {n}")
    print(f"• A conservar:              {len(grupos) - len(a_borrar)}")
    print(f"• Reporte:                  {REPORTE}")
    print("=" * 65)

    if not a_borrar:
        print("[OK] No hay nada que purgar.")
        return 0
    if not args.confirmar:
        print("\n[modo simulación] No se borró nada. Use --confirmar para aplicar.")
        return 0

    # 5. Backup + borrado en una sola transacción
    backup = _backup(args.db)
    print(f"\n[backup] {backup}")

    conn = sqlite3.connect(args.db)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        cur = conn.cursor()
        for col, motivo in a_borrar:
            if motivo == "productos_con_autor_ajeno":
                # Primero los productos; el grupo se recargará en vivo.
                cur.execute("DELETE FROM Productos WHERE codigo_grupo = ?", (col,))
            cur.execute("DELETE FROM Grupos WHERE codigo_grupo = ?", (col,))
        # Limpieza global de productos cuyo autor no es del mismo grupo.
        cur.execute(
            """
            DELETE FROM Productos
             WHERE NOT EXISTS (
                 SELECT 1 FROM Investigadores i
                  WHERE i.documento_id = Productos.id_investigador
                    AND i.codigo_grupo = Productos.codigo_grupo)
            """
        )
        huerfanos_global = cur.rowcount
        # Investigadores/perfiles sin grupo (defensa extra).
        cur.execute(
            "DELETE FROM Investigadores WHERE codigo_grupo NOT IN "
            "(SELECT codigo_grupo FROM Grupos)"
        )
        inv_sueltos = cur.rowcount
        cur.execute(
            "DELETE FROM PerfilInvestigador WHERE documento_id NOT IN "
            "(SELECT documento_id FROM Investigadores)"
        )
        conn.commit()

        integridad = cur.execute("PRAGMA integrity_check").fetchone()[0]
        restantes = cur.execute("SELECT COUNT(*) FROM Grupos").fetchone()[0]
        vacios = cur.execute(
            """
            SELECT COUNT(*) FROM Grupos g
             WHERE NOT EXISTS (SELECT 1 FROM Investigadores i WHERE i.codigo_grupo=g.codigo_grupo)
               AND NOT EXISTS (SELECT 1 FROM Productos p WHERE p.codigo_grupo=g.codigo_grupo)
            """
        ).fetchone()[0]
        huerfanos = cur.execute(
            """
            SELECT COUNT(*) FROM Productos p
             WHERE NOT EXISTS (
                 SELECT 1 FROM Investigadores i
                  WHERE i.documento_id=p.id_investigador
                    AND i.codigo_grupo=p.codigo_grupo)
            """
        ).fetchone()[0]
    finally:
        conn.close()

    print(f"[OK] Purga aplicada. Grupos restantes: {restantes}")
    print(f"     • Productos con autor ajeno eliminados: {huerfanos_global}")
    print(f"     • Investigadores sin grupo eliminados:  {inv_sueltos}")
    print(f"     • Grupos vacíos restantes:              {vacios}")
    print(f"     • Productos con autor ajeno restantes:  {huerfanos}")
    print(f"     • integrity_check:                      {integridad}")
    print("=" * 65)
    return 0


if __name__ == "__main__":
    sys.exit(main())
