"""
=====================================================================
PEA-i: RECONCILIACIÓN CON DATOS ABIERTOS DE COLOMBIA (MINCIENCIAS)
Universidad Popular del Cesar — Estructura de Datos (Taller 2)
=====================================================================
Cruce entre la base local (GrupLAC / ScienTI) y el dataset abierto
``hrhc-c4wu`` de datos.gov.co, restringido a la Universidad Popular
del Cesar (UPC).

Reglas:
  * La lista autoritativa de grupos UPC es la unión de:
      - ScienTI, instituciones -> grupos (codInst=947)
      - Datos Abiertos, inst_aval contiene "UNIVERSIDAD POPULAR DEL CESAR"
  * El detalle (integrantes, productos) se toma de GrupLAC.
  * Los metadatos oficiales (clasificación, área, año) se contrastan
    contra la convocatoria más reciente publicada en Datos Abiertos.

Uso:
    python3 -m python.core.reconciliacion [--db RUTA] [--sin-red]

No modifica la base de datos: solo escribe data/reconciliacion_upc.csv.
=====================================================================
"""

import csv
import json
import os
import re
import sqlite3
import unicodedata
import urllib.parse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", "..", ".."))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
IDX_GRUPOS = os.path.join(DATA_DIR, "indice_grupos.json")
DB_DEFAULT = os.path.join(DATA_DIR, "pea_investigacion.db")
CSV_SALIDA = os.path.join(DATA_DIR, "reconciliacion_upc.csv")

SOCRATA_URL = "https://www.datos.gov.co/resource/hrhc-c4wu.json"
UPC_MATCH = "POPULAR DEL CESAR"
UPC_CODINST = "947"

CAMPOS_SOCRATA = ",".join([
    "cod_grupo_gr",
    "nme_grupo_gr",
    "nme_clasificacion_gr",
    "nme_area_gr",
    "nme_gran_area_gr",
    "nme_municipio_gr",
    "nme_departamento_gr",
    "inst_aval",
    "fcreacion_gr",
    "ano_convo",
])


def normalizar(texto: str) -> str:
    """Normaliza para comparar nombres sin tildes, mayúsculas ni puntuación."""
    if not texto:
        return ""
    t = unicodedata.normalize("NFD", str(texto).lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


def area_compatible(area_bd: str, area_socrata: str):
    """Compara el área amplia de GrupLAC con el área específica de Socrata.

    GrupLAC guarda el primer nivel ("Ciencias Sociales"); Socrata publica el
    nivel específico ("Ciencias de la Educación"). Se consideran compatibles
    cuando el área específica pertenece a la gran área almacenada.
    Devuelve True/False/None (None si falta un dato).
    """
    a, b = normalizar(area_bd), normalizar(area_socrata)
    if not a or not b:
        return None
    if a == b or a in b or b in a:
        return True
    grandes = {
        "ciencias sociales": ("educacion", "sociolog", "derecho", "econom",
                              "psicolog", "comunicaci", "antropolog", "politic",
                              "geograf", "trabajo social"),
        "ciencias naturales": ("biolog", "matematic", "fisic", "quimic",
                               "geolog", "tierra", "ambiente", "microbiolog"),
        "ciencias medicas y de la salud": ("medicin", "salud", "enfermer",
                                           "odontolog", "farmac"),
        "ciencias agricolas": ("agronom", "veterinar", "zootecn", "agricol"),
        "ingenieria y tecnologia": ("ingenier", "tecnolog", "biotecnolog",
                                    "arquitect", "industrial"),
        "humanidades": ("arte", "historia", "filosof", "literatur", "teolog"),
    }
    for grande, subs in grandes.items():
        if grande in a and any(s in b for s in subs):
            return True
        if grande in b and any(s in a for s in subs):
            return True
    return False


def _get_json(url: str, timeout: int = 30):
    import requests
    r = requests.get(
        url,
        timeout=timeout,
        headers={"Accept": "application/json", "User-Agent": "PEA-i/2.0"},
    )
    r.raise_for_status()
    return r.json()


def descargar_socrata_upc(timeout: int = 30) -> dict:
    """Descarga los grupos UPC de datos.gov.co y deduplica por código.

    El dataset repite cada grupo por convocatoria. Se ordena por
    ``ano_convo`` descendente y se conserva la primera fila de cada
    ``cod_grupo_gr`` (la más reciente). Devuelve {codigo: fila}.
    """
    salida = {}
    offset = 0
    tamano = 1000
    while True:
        params = {
            "$select": CAMPOS_SOCRATA,
            "$where": "upper(inst_aval) like '%{}%'".format(UPC_MATCH),
            "$order": "ano_convo DESC",
            "$limit": str(tamano),
            "$offset": str(offset),
        }
        url = SOCRATA_URL + "?" + urllib.parse.urlencode(params)
        filas = _get_json(url, timeout=timeout)
        if not isinstance(filas, list) or not filas:
            break
        for fila in filas:
            col = (fila.get("cod_grupo_gr") or "").strip()
            if col and col not in salida:
                salida[col] = fila
        if len(filas) < tamano:
            break
        offset += tamano
    return salida


def cargar_indice_upc() -> dict:
    """Lee los grupos UPC de la caché ScienTI (indice_grupos.json[947])."""
    try:
        with open(IDX_GRUPOS, "r", encoding="utf-8") as f:
            idx = json.load(f)
    except Exception:
        return {}
    grupos = idx.get(UPC_CODINST) or []
    return {g.get("col"): g for g in grupos if g.get("col")}


def lista_upc_autoritativa(socrata: dict = None) -> dict:
    """Unión ScienTI (947) + Datos Abiertos UPC, indexada por código COL."""
    base = cargar_indice_upc()
    salida = {}
    for col, g in base.items():
        salida[col] = {
            "col": col,
            "nro": g.get("nro", ""),
            "nombre": g.get("nombre", ""),
            "lider": g.get("lider", ""),
            "categoria": g.get("categoria", ""),
            "estado": g.get("estado", ""),
            "en_scienti": True,
            "en_socrata": False,
            "socrata": None,
        }
    for col, fila in (socrata or {}).items():
        if col in salida:
            salida[col]["en_socrata"] = True
            salida[col]["socrata"] = fila
        else:
            salida[col] = {
                "col": col,
                "nro": "",
                "nombre": fila.get("nme_grupo_gr", ""),
                "lider": "",
                "categoria": "",
                "estado": "",
                "en_scienti": False,
                "en_socrata": True,
                "socrata": fila,
            }
    return salida


def _grupos_bd(db_path: str) -> list:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        filas = conn.execute(
            """
            SELECT g.codigo_grupo, g.nombre, g.lider, g.clasificacion,
                   g.area_conocimiento,
                   (SELECT COUNT(*) FROM Investigadores i
                     WHERE i.codigo_grupo = g.codigo_grupo) AS n_inv,
                   (SELECT COUNT(*) FROM Productos p
                     WHERE p.codigo_grupo = g.codigo_grupo) AS n_prod
              FROM Grupos g
             ORDER BY g.codigo_grupo
            """
        ).fetchall()
        return [dict(f) for f in filas]
    finally:
        conn.close()


def reconciliar(db_path: str = None, socrata: dict = None,
                escribir_csv: bool = True) -> dict:
    """Compara la BD local contra la lista autoritativa UPC.

    Devuelve un resumen con conteos y la lista de diferencias.
    """
    db_path = db_path or DB_DEFAULT
    error_red = ""
    if socrata is None:
        try:
            socrata = descargar_socrata_upc()
        except Exception as e:  # sin red: se usa solo la caché ScienTI
            error_red = str(e)
            socrata = {}

    autoritativos = lista_upc_autoritativa(socrata)
    filas_bd = _grupos_bd(db_path)

    filas = []
    resumen = {
        "total_bd": len(filas_bd),
        "ok": 0,
        "diferencia": 0,
        "diferencia_metadatos": 0,
        "solo_scienti": 0,
        "no_upc": 0,
        "grupos_autoritativos": len(autoritativos),
        "en_scienti": sum(1 for a in autoritativos.values() if a["en_scienti"]),
        "en_socrata": sum(1 for a in autoritativos.values() if a["en_socrata"]),
        "error_red": error_red,
    }

    for g in filas_bd:
        col = g["codigo_grupo"]
        aut = autoritativos.get(col)
        soc = (aut or {}).get("socrata") or {}
        nombre_soc = soc.get("nme_grupo_gr", "")
        clas_soc = soc.get("nme_clasificacion_gr", "")
        area_soc = soc.get("nme_area_gr", "")
        inst_soc = soc.get("inst_aval", "")
        coincide_nombre = None
        if nombre_soc:
            coincide_nombre = normalizar(g["nombre"]) == normalizar(nombre_soc)
        coincide_clas = None
        if clas_soc:
            coincide_clas = normalizar(g["clasificacion"]) == normalizar(clas_soc)
        coincide_area = area_compatible(g["area_conocimiento"], area_soc)

        if aut is None:
            estado = "NO_UPC"
            resumen["no_upc"] += 1
        elif not soc:
            estado = "SOLO_SCIENTI"
            resumen["solo_scienti"] += 1
        elif coincide_nombre is False:
            estado = "DIFERENCIA"
            resumen["diferencia"] += 1
        elif coincide_clas is False or coincide_area is False:
            estado = "DIFERENCIA_METADATOS"
            resumen["diferencia_metadatos"] += 1
        else:
            estado = "OK"
            resumen["ok"] += 1

        filas.append({
            "codigo": col,
            "nombre_bd": g["nombre"],
            "nombre_socrata": nombre_soc,
            "en_scienti": "si" if (aut and aut["en_scienti"]) else "no",
            "en_socrata": "si" if (aut and aut["en_socrata"]) else "no",
            "clasificacion_bd": g["clasificacion"],
            "clasificacion_socrata": clas_soc,
            "area_bd": g["area_conocimiento"],
            "area_socrata": area_soc,
            "institucion_socrata": inst_soc,
            "investigadores": g["n_inv"],
            "productos": g["n_prod"],
            "coincide_nombre": "" if coincide_nombre is None else ("si" if coincide_nombre else "no"),
            "coincide_clasificacion": "" if coincide_clas is None else ("si" if coincide_clas else "no"),
            "coincide_area": "" if coincide_area is None else ("si" if coincide_area else "no"),
            "estado": estado,
        })

    # Grupos autoritativos que aún no están en la BD (pendientes de cargar).
    en_bd = {f["codigo"] for f in filas}
    faltantes = [a for col, a in autoritativos.items() if col not in en_bd]
    resumen["faltantes_en_bd"] = len(faltantes)
    resumen["faltantes_sin_scienti"] = sum(1 for a in faltantes if not a["en_scienti"])

    if escribir_csv:
        columnas = [
            "codigo", "nombre_bd", "nombre_socrata", "en_scienti", "en_socrata",
            "clasificacion_bd", "clasificacion_socrata", "area_bd", "area_socrata",
            "institucion_socrata", "investigadores", "productos",
            "coincide_nombre", "coincide_clasificacion", "coincide_area", "estado",
        ]
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(CSV_SALIDA, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=columnas)
            w.writeheader()
            for fila in filas:
                w.writerow(fila)

    return {"resumen": resumen, "filas": filas, "faltantes": faltantes}


def imprimir_resumen(resultado: dict) -> None:
    r = resultado["resumen"]
    print("=" * 65)
    print("   RECONCILIACIÓN PEA-i <-> DATOS ABIERTOS DE COLOMBIA (UPC)")
    print("=" * 65)
    if r.get("error_red"):
        print(f"[!] Sin conexión a datos.gov.co: {r['error_red']}")
        print("    Se usó únicamente la caché ScienTI (indice_grupos.json).")
    print(f"• Grupos autoritativos UPC: {r['grupos_autoritativos']} "
          f"(ScienTI: {r['en_scienti']}, Datos Abiertos: {r['en_socrata']})")
    print(f"• Grupos en la BD:          {r['total_bd']} "
          f"(OK: {r['ok']}, diferencia de nombre: {r['diferencia']}, "
          f"diferencia de metadatos: {r['diferencia_metadatos']}, "
          f"solo ScienTI: {r['solo_scienti']}, NO UPC: {r['no_upc']})")
    print(f"• UPC aún no cargados:      {r['faltantes_en_bd']} "
          f"(sin ficha ScienTI: {r['faltantes_sin_scienti']})")
    print(f"• Reporte: {CSV_SALIDA}")
    if r["diferencia_metadatos"]:
        print("  Nota: la clasificación/área puede diferir porque Datos Abiertos")
        print("  publica la última convocatoria (2021) y GrupLAC muestra la")
        print("  vigencia actual. El reporte detalla cada caso.")
    if resultado["filas"]:
        print("\n  Código       Inv   Prod  Estado        Nombre BD")
        print("  " + "-" * 70)
        for f in resultado["filas"]:
            print(f"  {f['codigo']:<12} {f['investigadores']:>3}   "
                  f"{f['productos']:>4}  {f['estado']:<13} {f['nombre_bd'][:34]}")
    if resultado["faltantes"]:
        print("\n  UPC pendientes de cargar (primeros 15):")
        for a in resultado["faltantes"][:15]:
            print(f"    {a['col']:<12} nro={a['nro'] or '—':<14} {a['nombre'][:40]}")
    print("=" * 65)


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="Reconciliación PEA-i vs Datos Abiertos (UPC)")
    ap.add_argument("--db", default=DB_DEFAULT)
    ap.add_argument("--sin-red", action="store_true", help="usar solo la caché ScienTI")
    args = ap.parse_args()
    soc = {} if args.sin_red else None
    imprimir_resumen(reconciliar(args.db, socrata=soc))
