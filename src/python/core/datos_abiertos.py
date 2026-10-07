"""
=====================================================================
PEA-i: MÓDULO DE DATOS ABIERTOS DE COLOMBIA (SOCRATA API + OFFLINE)
Universidad Popular del Cesar — Estructura de Datos
Docente: Ing. Adith Bismarck Pérez Orozco
=====================================================================
Integra la consulta y enriquecimiento de investigadores y grupos desde
la API pública Socrata de Datos Abiertos de Colombia (datos.gov.co):
  • Dataset Investigadores Reconocidos: https://www.datos.gov.co/resource/bqtm-4y2h.json
  • Dataset Grupos Reconocidos: https://www.datos.gov.co/resource/hrhc-c4wu.json
  • Resolución de códigos GrupLAC (COLxxxxxxx -> URL oficial Scienti)
  • Modo Offline-First: Usa caché local y SQLite3 sin consumir datos móviles
    a menos que el usuario solicite explícitamente consulta en línea.
=====================================================================
"""

import os
import json
import sqlite3
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", "..", ".."))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "pea_investigacion.db")
CACHE_PATH = os.path.join(PROJECT_ROOT, "data", "cache_socrata_minciencias.json")

SOCRATA_INVESTIGADORES_URL = "https://www.datos.gov.co/resource/bqtm-4y2h.json"
SOCRATA_GRUPOS_URL = "https://www.datos.gov.co/resource/hrhc-c4wu.json"
GRUPLAC_VIEWER_BASE = "https://scienti.minciencias.gov.co/gruplac/jsp/visualiza/visualizagr.jsp?nro="
REQUEST_TIMEOUT = 12


def normalizar_cod_rh(codigo_externo: str) -> Optional[str]:
    """Normaliza el código CvLAC/cod_rh al formato id_persona_pr de 10 dígitos."""
    digits = "".join(c for c in (codigo_externo or "") if c.isdigit())
    if not digits:
        return None
    return digits.zfill(10)


def gruplac_url_from_code(cod_grupo_gr: str) -> str:
    """Convierte un código de grupo o número GrupLAC en URL oficial del visor Scienti."""
    digits = "".join(c for c in (cod_grupo_gr or "") if c.isdigit())
    if not digits:
        return ""
    return f"{GRUPLAC_VIEWER_BASE}{digits.zfill(14)}"


def cargar_cache_local() -> Dict[str, Any]:
    """Carga el caché local de Datos Abiertos si existe en disco."""
    if os.path.exists(CACHE_PATH):
        try:
            with open(CACHE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"investigadores": {}, "grupos": {}}


def guardar_cache_local(cache_data: Dict[str, Any]) -> None:
    """Persiste en disco las respuestas de Socrata para operación 100% offline posterior."""
    try:
        os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
        with open(CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def consultar_socrata_investigador(cod_rh: str, permitir_red: bool = False) -> Optional[Dict[str, Any]]:
    """
    Consulta el registro más reciente de un investigador en el dataset oficial
    bqtm-4y2h de MinCiencias (Datos Abiertos de Colombia).
    Si permitir_red=False, consulta únicamente caché local y base de datos SQLite3.
    """
    norm = normalizar_cod_rh(cod_rh)
    if not norm:
        return None

    cache = cargar_cache_local()
    if norm in cache.get("investigadores", {}):
        return cache["investigadores"][norm]

    if not permitir_red:
        return None

    query = urllib.parse.urlencode({
        "$where": f"id_persona_pr='{norm}'",
        "$order": "ano_convo DESC",
        "$limit": 1,
    })
    url = f"{SOCRATA_INVESTIGADORES_URL}?{query}"
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "PEA-i-UPC/2.0"})
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
            rows = json.loads(resp.read().decode("utf-8"))
            if rows:
                record = rows[0]
                cache.setdefault("investigadores", {})[norm] = record
                guardar_cache_local(cache)
                return record
    except Exception:
        return None
    return None


def auditar_grupos_e_investigadores_locales(db_path: str = DB_PATH) -> Dict[str, Any]:
    """
    Ejecuta una auditoría local cruzando los grupos e investigadores almacenados en SQLite3
    con los metadatos de reconocimiento MinCiencias (Categorías A1, A, B, C y Senior/Asociado/Junior)
    sin requerir conexión a Internet.
    """
    resultado = {
        "total_grupos": 0,
        "grupos_por_categoria": {},
        "total_investigadores": 0,
        "investigadores_por_categoria": {},
        "investigadores_con_orcid_o_cvlac": 0,
        "grupos_detalle": [],
    }
    if not os.path.exists(db_path):
        return resultado

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()
        cur.execute("SELECT codigo_grupo, nombre, clasificacion, area_conocimiento, lider FROM grupos WHERE activo=1 ORDER BY codigo_grupo")
        for g in cur.fetchall():
            resultado["total_grupos"] += 1
            cat = (g["clasificacion"] or "Sin categoría").strip()
            resultado["grupos_por_categoria"][cat] = resultado["grupos_por_categoria"].get(cat, 0) + 1

            cur.execute("SELECT COUNT(*) FROM investigadores WHERE codigo_grupo=? AND activo=1", (g["codigo_grupo"],))
            n_inv = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM productos WHERE codigo_grupo=? AND activo=1", (g["codigo_grupo"],))
            n_prod = cur.fetchone()[0]

            resultado["grupos_detalle"].append({
                "codigo": g["codigo_grupo"],
                "nombre": g["nombre"],
                "categoria": cat,
                "lider": g["lider"],
                "url_scienti": gruplac_url_from_code(g["codigo_grupo"]),
                "investigadores_activos": n_inv,
                "productos_activos": n_prod,
            })

        cur.execute("SELECT documento_id, nombre_completo, categoria, formacion_academica FROM investigadores WHERE activo=1")
        for inv in cur.fetchall():
            resultado["total_investigadores"] += 1
            cat_i = (inv["categoria"] or "Integrante").strip()
            resultado["investigadores_por_categoria"][cat_i] = resultado["investigadores_por_categoria"].get(cat_i, 0) + 1
            if inv["documento_id"] and str(inv["documento_id"]).strip():
                resultado["investigadores_con_orcid_o_cvlac"] += 1
    finally:
        conn.close()

    return resultado
