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
import re
import unicodedata
from urllib.parse import urlencode

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
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
