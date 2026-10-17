#!/usr/bin/env python3
"""
=====================================================================
PEA-i: IMPORTADOR DE CAMBIOS DEL PORTAL WEB (CRUD -> SQLite)
Universidad Popular del Cesar — Estructura de Datos
=====================================================================
Cierra el ciclo de interoperabilidad:

    Portal HTML5 (CRUD en RAM)
        -> botón "Sincronizar SQLite" -> data/cambios_gui.json
        -> este módulo -> SQLite (data/pea_investigacion.db)
        -> la consola C++/Python recarga la Multilista desde SQLite.

El archivo cambios_gui.json lo genera el portal con la MISMA estructura
que la Multilista (serializarMultilistaAJSON): grupos -> investigadores
-> productos, de modo que el reemplazo es fiel (round-trip sin pérdida).

Seguridad: antes de escribir se crea una copia de respaldo
(pea_investigacion.db.bak) y todo el reemplazo ocurre en una única
transacción; ante cualquier error se revierte y la BD queda intacta.
=====================================================================
"""
import os
import sys
import json
import shutil
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", "..", ".."))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
for _p in (SRC_DIR, PROJECT_ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)

try:
    from python.core.catalogo_2024 import CatalogoMinCiencias2024
except Exception:  # pragma: no cover - degradación defensiva
    from core.catalogo_2024 import CatalogoMinCiencias2024

CLASES_VALIDAS = {"A1", "A", "B", "C", "Reconocido", "Sin Clasificacion"}
CATEGORIAS_VALIDAS = {"Senior", "Asociado", "Junior", "Sin Categoria"}
FAMILIAS_VALIDAS = {"GNC", "DTI", "ASC", "DPC", "FRH", "OTRO"}


def _clasificacion_segura(valor: str) -> str:
    v = (valor or "").strip()
    return v if v in CLASES_VALIDAS else "Reconocido"


def _categoria_segura(valor: str) -> str:
    v = (valor or "").strip()
    return v if v in CATEGORIAS_VALIDAS else "Sin Categoria"


def _familia_segura(valor: str) -> str:
    v = (valor or "").strip().upper()
    return v if v in FAMILIAS_VALIDAS else "OTRO"


def importar_cambios_gui(ruta_json=None, ruta_bd=None, ruta_schema=None,
                         hacer_respaldo=True) -> dict:
    """Aplica data/cambios_gui.json a la base SQLite.

    Retorna un dict con el resumen: {ok, grupos, investigadores, productos,
    operaciones, mensaje}. No lanza excepción por datos malformados: devuelve
    ok=False y un mensaje claro.
    """
    ruta_json = ruta_json or os.path.join(PROJECT_ROOT, "data", "cambios_gui.json")
    ruta_bd = ruta_bd or os.path.join(PROJECT_ROOT, "data", "pea_investigacion.db")
    ruta_schema = ruta_schema or os.path.join(PROJECT_ROOT, "data", "schema.sql")

    if not os.path.exists(ruta_json):
        return {"ok": False, "grupos": 0, "investigadores": 0, "productos": 0,
                "operaciones": 0,
                "mensaje": f"No se encontró el archivo de cambios: {ruta_json}"}

    try:
        with open(ruta_json, "r", encoding="utf-8") as f:
            datos = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        return {"ok": False, "grupos": 0, "investigadores": 0, "productos": 0,
                "operaciones": 0,
                "mensaje": f"JSON inválido o ilegible: {e}"}

    grupos = datos.get("grupos")
    if not isinstance(grupos, list) or not grupos:
        return {"ok": False, "grupos": 0, "investigadores": 0, "productos": 0,
                "operaciones": len(datos.get("operaciones_historial") or []),
                "mensaje": "El JSON no contiene una lista 'grupos' válida."}

    # Validación mínima: todo grupo debe tener código.
    for g in grupos:
        if not isinstance(g, dict) or not (g.get("codigo") or "").strip():
            return {"ok": False, "grupos": 0, "investigadores": 0, "productos": 0,
                    "operaciones": 0,
                    "mensaje": "Hay un grupo sin 'codigo'; se aborta para no corromper la BD."}

    respaldo = None
    if hacer_respaldo and os.path.exists(ruta_bd):
        try:
            respaldo = ruta_bd + ".bak"
            shutil.copy2(ruta_bd, respaldo)
        except OSError:
            respaldo = None

    conn = sqlite3.connect(ruta_bd)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA busy_timeout = 5000;")
    try:
        with open(ruta_schema, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
    except OSError:
        pass  # si no hay schema, asumimos que ya existe

    n_inv = n_prod = 0
    try:
        cur = conn.cursor()
        # Reemplazo transaccional y fiel del estado del portal.
        cur.execute("BEGIN;")
        cur.execute("DELETE FROM Productos;")
        cur.execute("DELETE FROM PerfilInvestigador;")
        cur.execute("DELETE FROM Investigadores;")
        cur.execute("DELETE FROM Grupos;")

        # PASADA 1: grupos e investigadores (las FK de Productos apuntan a
        # Investigadores que pueden pertenecer a cualquier grupo, así que
        # primero se insertan TODOS antes de cualquier producto).
        primer_inv_por_grupo = {}
        for g in grupos:
            codigo = (g.get("codigo") or "").strip()
            cur.execute(
                "INSERT INTO Grupos (codigo_grupo, nombre, clasificacion, "
                "area_conocimiento, lider, anio_creacion, activo) "
                "VALUES (?, ?, ?, ?, ?, ?, ?);",
                (codigo,
                 (g.get("nombre") or "").strip() or codigo,
                 _clasificacion_segura(g.get("clasificacion")),
                 (g.get("area") or "").strip(),
                 (g.get("lider") or "").strip(),
                 int(g.get("anio_creacion") or g.get("anio") or 2024),
                 1 if g.get("activo", True) else 0))

            primer_inv = None
            for inv in (g.get("investigadores") or []):
                doc = (inv.get("documento") or "").strip()
                if not doc:
                    continue
                if primer_inv is None:
                    primer_inv = doc
                cur.execute(
                    "INSERT OR REPLACE INTO Investigadores (documento_id, "
                    "nombre_completo, categoria, formacion_academica, "
                    "codigo_grupo, activo) VALUES (?, ?, ?, ?, ?, ?);",
                    (doc,
                     (inv.get("nombre") or "").strip(),
                     _categoria_segura(inv.get("categoria")),
                     (inv.get("formacion") or "").strip(),
                     codigo,
                     1 if inv.get("activo", True) else 0))
                n_inv += 1
                # Perfil CvLAC enriquecido (si viene en el export)
                if any(inv.get(k) for k in ("par_evaluador", "scholar_url",
                                            "orcid", "formacion")):
                    cur.execute(
                        "INSERT OR REPLACE INTO PerfilInvestigador "
                        "(documento_id, par_evaluador, scholar_url, orcid, "
                        "formacion_academica) VALUES (?, ?, ?, ?, ?);",
                        (doc,
                         (inv.get("par_evaluador") or "No").strip() or "No",
                         (inv.get("scholar_url") or "").strip(),
                         (inv.get("orcid") or "").strip(),
                         (inv.get("formacion") or "").strip()))
            primer_inv_por_grupo[codigo] = primer_inv

        # PASADA 2: productos (ya existen todos los investigadores).
        for g in grupos:
            codigo = (g.get("codigo") or "").strip()
            primer_inv = primer_inv_por_grupo.get(codigo)
            for p in (g.get("productos") or []):
                pid = (p.get("id") or "").strip()
                if not pid:
                    continue
                id_inv = (p.get("id_investigador") or "").strip() or (primer_inv or "")
                if not id_inv:
                    continue  # sin investigador en el grupo: no se puede respetar la FK
                tipo = (p.get("tipo") or "Articulo").strip() or "Articulo"
                categoria = (p.get("categoria") or "A1").strip() or "A1"
                info = CatalogoMinCiencias2024.clasificar_producto(
                    p.get("subtipo_codigo") or tipo, categoria, p.get("titulo") or "")
                peso = p.get("peso_calculado")
                if peso in (None, 0, 0.0):
                    peso = float(info.get("global_weight", 0.0) or 0.0)
                cur.execute(
                    "INSERT OR REPLACE INTO Productos (id_producto, tipo, titulo, "
                    "anio, categoria_minciencias, validado, codigo_grupo, "
                    "id_investigador, activo, subtipo_codigo, familia, "
                    "clase_medicion, peso_calculado) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);",
                    (pid, tipo, (p.get("titulo") or "").strip(),
                     int(p.get("anio") or 2024), categoria,
                     1 if p.get("validado") else 0, codigo, id_inv,
                     1 if p.get("activo", True) else 0,
                     (p.get("subtipo_codigo") or info.get("codigo_2024") or "ART"),
                     _familia_segura(p.get("familia") or info.get("familia")),
                     (p.get("clase_medicion") or "GNC-A"),
                     float(peso)))
                n_prod += 1

        n_ops = len(datos.get("operaciones_historial") or [])
        cur.execute(
            "INSERT INTO HistorialAcciones (tipo_operacion, entidad_afectada, "
            "id_registro, detalles) VALUES (?, ?, ?, ?);",
            ("SINCRONIZAR", "PORTAL_GUI", "cambios_gui.json",
             f"Importación del portal: {len(grupos)} grupos, {n_inv} "
             f"investigadores, {n_prod} productos, {n_ops} operaciones."))
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        conn.close()
        return {"ok": False, "grupos": 0, "investigadores": 0, "productos": 0,
                "operaciones": 0,
                "mensaje": f"Error de SQLite, se revirtió todo: {e}"}
    finally:
        try:
            conn.close()
        except Exception:
            pass

    return {"ok": True, "grupos": len(grupos), "investigadores": n_inv,
            "productos": n_prod,
            "operaciones": len(datos.get("operaciones_historial") or []),
            "respaldo": respaldo,
            "mensaje": (f"Sincronizados {len(grupos)} grupos, {n_inv} "
                        f"investigadores y {n_prod} productos en SQLite.")}


def main(argv):
    ruta_json = argv[1] if len(argv) > 1 else None
    res = importar_cambios_gui(ruta_json)
    etiqueta = "[OK]" if res["ok"] else "[!]"
    print(f"{etiqueta} {res['mensaje']}")
    if res["ok"]:
        print(f"    Grupos:         {res['grupos']}")
        print(f"    Investigadores: {res['investigadores']}")
        print(f"    Productos:      {res['productos']}")
        if res.get("respaldo"):
            print(f"    Respaldo:       {os.path.basename(res['respaldo'])}")
    return 0 if res["ok"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
