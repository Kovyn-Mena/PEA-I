"""
=====================================================================
PEA-i: MÓDULO DE BÚSQUEDA Y DESCUBRIMIENTO INSTITUCIONAL (SCIENTI)
Universidad Popular del Cesar — Estructura de Datos (Taller 2)
=====================================================================
Permite explorar universidades e instituciones de investigación en
Colombia y descubrir sus grupos de investigación adscritos, indexando
y consultando la base de datos de MinCiencias (GrupLAC / ScienTI).
Opera con fallback 100% offline sobre la caché local en JSON.
=====================================================================
"""

import json
import os
import sys
import re
import unicodedata
from urllib.parse import urlencode

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
pylib_dir = os.path.join(PROJECT_ROOT, "pylib")
if os.path.exists(pylib_dir) and pylib_dir not in sys.path:
    sys.path.insert(0, pylib_dir)
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
IDX_INSTITUCIONES = os.path.join(DATA_DIR, "indice_instituciones.json")
IDX_GRUPOS = os.path.join(DATA_DIR, "indice_grupos.json")

CIENCIA_BASE = "https://scienti.minciencias.gov.co/ciencia-war"
USER_AGENT = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}


def normalizar_clave(s: str) -> str:
    """Normaliza texto para búsquedas difusas sin tildes ni caracteres especiales."""
    if not s:
        return ""
    texto = unicodedata.normalize("NFD", s.lower())
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    texto = re.sub(r"[^a-z0-9]+", " ", texto).strip()
    return texto


def obtener_indice_instituciones(forzar: bool = False) -> list:
    """
    Retorna el listado de instituciones de Colombia con su codInst y total de grupos.
    Si existe caché local y forzar=False, lee desde indice_instituciones.json.
    Si forzar=True o no existe, intenta consultar MinCiencias.
    """
    if os.path.exists(IDX_INSTITUCIONES) and not forzar:
        try:
            with open(IDX_INSTITUCIONES, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    try:
        import requests
        from bs4 import BeautifulSoup

        url = CIENCIA_BASE + "/busquedaGruposPorInstitucion.do?" + urlencode({"all_grupos_ins_mr_": "2000"})
        r = requests.get(url, headers=USER_AGENT, timeout=20)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            t = soup.find("table", id="all_grupos_ins")
            out = []
            if t:
                for tr in t.find_all("tr")[1:]:
                    tds = [c.get_text(" ").strip() for c in tr.find_all(["td", "th"])]
                    if len(tds) < 2:
                        continue
                    a = tr.find("a", href=True)
                    cod = ""
                    if a:
                        m = re.search(r"codInst=(\d+)", a.get("href", ""))
                        if m:
                            cod = m.group(1)
                    try:
                        n = int(re.sub(r"\D", "", tds[1]))
                    except ValueError:
                        n = 0
                    out.append({"nombre": tds[0], "codinst": cod, "n_grupos": n})
            if out:
                os.makedirs(DATA_DIR, exist_ok=True)
                with open(IDX_INSTITUCIONES, "w", encoding="utf-8") as f:
                    json.dump(out, f, ensure_ascii=False, indent=1)
                return out
    except Exception as e:
        print(f"[!] Aviso: No se pudo conectar a MinCiencias ({e}). Usando índice local.")

    if os.path.exists(IDX_INSTITUCIONES):
        with open(IDX_INSTITUCIONES, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def buscar_universidad(texto: str) -> list:
    """Busca instituciones cuyo nombre coincida con el texto de búsqueda."""
    insts = obtener_indice_instituciones()
    q = normalizar_clave(texto)
    if not q:
        return []

    candidatos = []
    for inst in insts:
        nombre_norm = normalizar_clave(inst.get("nombre", ""))
        if q in nombre_norm or q == str(inst.get("codinst", "")):
            candidatos.append(inst)
    return candidatos


def obtener_grupos_institucion(codinst: str, nombre_inst: str = "", forzar: bool = False) -> list:
    """
    Retorna la lista de grupos asociados a una institución (e.g. codinst='947' para UPC).
    Lee desde indice_grupos.json o consulta MinCiencias si se fuerza.
    """
    idx = {}
    if os.path.exists(IDX_GRUPOS):
        try:
            with open(IDX_GRUPOS, "r", encoding="utf-8") as f:
                idx = json.load(f)
        except Exception:
            idx = {}

    cod_str = str(codinst).strip()
    if cod_str in idx and not forzar:
        return idx[cod_str]

    try:
        import requests
        from bs4 import BeautifulSoup

        url = CIENCIA_BASE + "/busquedaGrupoXInstitucionGrupos.do?" + urlencode({"codInst": cod_str})
        r = requests.get(url, headers=USER_AGENT, timeout=25)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            tid = ""
            for t in soup.find_all("table"):
                th = " ".join(t.get_text(" ").split())
                if "Cod grupo" in th and "Nombre grupo" in th and t.get("id"):
                    tid = t.get("id")
                    break

            if tid:
                url_all = url + "&" + urlencode({tid + "_mr_": "500"})
                r2 = requests.get(url_all, headers=USER_AGENT, timeout=25)
                if r2.status_code == 200:
                    r = r2

            soup2 = BeautifulSoup(r.text, "html.parser")
            out = []
            for t in soup2.find_all("table"):
                th = " ".join(t.get_text(" ").split())
                if "Cod grupo" in th and "Nombre grupo" in th:
                    for tr in t.find_all("tr")[1:]:
                        tds = [c.get_text(" ").strip() for c in tr.find_all(["td", "th"], recursive=False)]
                        ic = next((i for i, d in enumerate(tds) if re.match(r"^COL\d+$", d)), -1)
                        if ic < 0 or ic + 1 >= len(tds):
                            continue
                        nom = tds[ic + 1]
                        if not nom:
                            continue
                        nro = ""
                        for a in tr.find_all("a", href=True):
                            m = re.search(r"nro=(\d+)", a.get("href", ""))
                            if m:
                                nro = m.group(1)
                                break
                        resto = tds[ic + 2:]
                        out.append({
                            "col": tds[ic],
                            "nombre": nom,
                            "lider": resto[0] if len(resto) > 0 else "",
                            "avalado": resto[2] if len(resto) > 2 else "",
                            "estado": resto[3] if len(resto) > 3 else "",
                            "categoria": resto[4] if len(resto) > 4 else "",
                            "nro": nro,
                            "institucion": nombre_inst,
                            "codinst": cod_str
                        })
                    break

            if out:
                idx[cod_str] = out
                os.makedirs(DATA_DIR, exist_ok=True)
                with open(IDX_GRUPOS, "w", encoding="utf-8") as f:
                    json.dump(idx, f, ensure_ascii=False, indent=1)
                return out
    except Exception as e:
        print(f"[!] Aviso: No se pudieron descargar grupos en vivo ({e}).")

    return idx.get(cod_str, [])


def listar_grupos_upc() -> list:
    """Retorna los grupos registrados para la Universidad Popular del Cesar (codinst=947)."""
    return obtener_grupos_institucion("947", "Universidad Popular del Cesar")


def buscar_grupo_en_indices(termino: str) -> list:
    """
    Busca grupos por término clave en todos los índices institucionales almacenados.
    """
    q = normalizar_clave(termino)
    if not q:
        return []

    idx = {}
    if os.path.exists(IDX_GRUPOS):
        try:
            with open(IDX_GRUPOS, "r", encoding="utf-8") as f:
                idx = json.load(f)
        except Exception:
            idx = {}

    inst_nom = {}
    if os.path.exists(IDX_INSTITUCIONES):
        try:
            with open(IDX_INSTITUCIONES, "r", encoding="utf-8") as f:
                for i in json.load(f):
                    inst_nom[str(i.get("codinst", ""))] = i.get("nombre", "")
        except Exception:
            pass

    candidatos = []
    for codinst, grupos in idx.items():
        for g in grupos:
            nom_norm = normalizar_clave(g.get("nombre", ""))
            col_norm = normalizar_clave(g.get("col", ""))
            lid_norm = normalizar_clave(g.get("lider", ""))
            nro_str = str(g.get("nro", "")).strip()

            if q in nom_norm or q in col_norm or q in lid_norm or q == nro_str:
                copia = dict(g)
                copia["institucion"] = copia.get("institucion", "") or inst_nom.get(str(codinst), "")
                candidatos.append(copia)
    return candidatos


def _mapa_nro_a_col_dinamico() -> dict:
    """Construye nro->COL desde indice_grupos.json (66 grupos UPC).
    Se combina con el mapa hardcodeado de 4 grupos base."""
    base = {
        "00000000002099": "COL0018706",
        "2099": "COL0018706",
        "COL0002099": "COL0018706",
        "00000000002668": "COL0043834",
        "2668": "COL0043834",
        "00000000003202": "COL0049121",
        "3202": "COL0049121",
        "00000000003639": "COL0001351",
        "3639": "COL0001351",
    }
    try:
        if os.path.exists(IDX_GRUPOS):
            with open(IDX_GRUPOS, "r", encoding="utf-8") as f:
                idx = json.load(f)
            items = []
            if isinstance(idx, dict):
                for v in idx.values():
                    if isinstance(v, list):
                        items.extend(v)
            elif isinstance(idx, list):
                items = idx
            for g in items:
                if not isinstance(g, dict):
                    continue
                nro = str(g.get("nro", "")).strip()
                col = str(g.get("col", "")).strip()
                if nro and col:
                    base.setdefault(nro, col)
                    base.setdefault(nro.lstrip("0"), col)
                    if len(nro) >= 4:
                        base.setdefault(nro[-4:], col)
    except Exception:
        pass
    return base


def resolver_codigo_nro(nro: str) -> str:
    """Resuelve nro GrupLAC -> código COL oficial usando el índice.
    Retorna "" si no hay coincidencia (nunca inventa COL...)."""
    nro_limpio = str(nro or "").strip()
    if not nro_limpio:
        return ""
    mapa = _mapa_nro_a_col_dinamico()
    if nro_limpio in mapa:
        return mapa[nro_limpio]
    # Búsqueda por nro en índice (comparación exacta de sufijos)
    try:
        if os.path.exists(IDX_GRUPOS):
            with open(IDX_GRUPOS, "r", encoding="utf-8") as f:
                idx = json.load(f)
            items = []
            if isinstance(idx, dict):
                for v in idx.values():
                    if isinstance(v, list):
                        items.extend(v)
            elif isinstance(idx, list):
                items = idx
            for g in items:
                if not isinstance(g, dict):
                    continue
                gnro = str(g.get("nro", "")).strip()
                if gnro and (gnro == nro_limpio or (
                        len(nro_limpio) >= 4 and gnro.endswith(nro_limpio[-4:]))):
                    col = str(g.get("col", "")).strip()
                    if col:
                        return col
    except Exception:
        pass
    return ""


def existe_grupo_en_bd(nro: str, db_path: str = None) -> tuple:
    """
    Chequeo offline (sin red): ¿el nro o código ya está cargado en la BD?
    Devuelve (codigo_vigente, nombre) o (None, None).
    S32 / BUG-11: Detecta grupos existentes y resuelve alias canónicos (ej. GISICO -> COL0018706).
    """
    import sqlite3
    if not db_path:
        db_path = os.path.join(DATA_DIR, "pea_investigacion.db")
    if not os.path.exists(db_path):
        return None, None

    nro_limpio = str(nro).strip()
    if not nro_limpio:
        return None, None

    # Mapeo canónico de NRO MinCiencias a código COL oficial (66 grupos UPC)
    MAPA_NRO_CANONICO = _mapa_nro_a_col_dinamico()
    cod_objetivo = MAPA_NRO_CANONICO.get(nro_limpio, "")

    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        # 1. Búsqueda por código canónico mapeado
        if cod_objetivo:
            row = cur.execute("SELECT codigo_grupo, nombre FROM Grupos WHERE codigo_grupo = ?;", (cod_objetivo,)).fetchone()
            if row:
                conn.close()
                return row[0], row[1]

        # 2. Búsqueda directa por código de grupo o nombre
        row = cur.execute("SELECT codigo_grupo, nombre FROM Grupos WHERE codigo_grupo = ? OR codigo_grupo = ? OR UPPER(nombre) LIKE ?;", (nro_limpio, f"COL{nro_limpio}", f"%{nro_limpio.upper()}%")).fetchone()
        if row:
            conn.close()
            return row[0], row[1]

        # 3. Búsqueda por sufijo o nro en indice_grupos.json
        idx = {}
        if os.path.exists(IDX_GRUPOS):
            try:
                with open(IDX_GRUPOS, "r", encoding="utf-8") as f:
                    idx = json.load(f)
            except Exception:
                idx = {}
            items = []
            if isinstance(idx, dict):
                for v in idx.values():
                    if isinstance(v, list):
                        items.extend(v)
            elif isinstance(idx, list):
                items = idx
            for g in items:
                gnro = str(g.get("nro", "")).strip()
                if gnro and (gnro == nro_limpio or gnro.endswith(nro_limpio[-4:])):
                    col = g.get("col", "")
                    col_canonico = MAPA_NRO_CANONICO.get(col, col)
                    if col_canonico:
                        r = cur.execute("SELECT codigo_grupo, nombre FROM Grupos WHERE codigo_grupo = ?;", (col_canonico,)).fetchone()
                        if r:
                            conn.close()
                            return r[0], r[1]

        conn.close()
    except Exception:
        pass

    return None, None

