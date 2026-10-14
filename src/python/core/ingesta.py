"""
=====================================================================
PEA-i: MÓDULO DE INGESTA MASIVA, WEB SCRAPING Y PARSERS (FASE 3)
Universidad Popular del Cesar - Estructura de Datos
=====================================================================
Utiliza el TDA Cola (FIFO) para encolar y procesar solicitudes de:
  1. Web Scraping GrupLAC (Grupos MinCiencias / SCIENTI)
  2. Web Scraping CvLAC (Currículos de Investigadores)
  3. Ingesta de Archivos Tabulares CSV
  4. Ingesta y Extracción de Documentos PDF

Incluye mecanismo de contingencia (Plan B Offline) con reintentos,
User-Agent realista y dataset de respaldo en caso de indisponibilidad
de la red o caída del servidor de MinCiencias.
=====================================================================
"""

import os
import sys
import re
import csv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", "..", ".."))
pylib_dir = os.path.join(PROJECT_ROOT, "pylib")
if os.path.exists(pylib_dir) and pylib_dir not in sys.path:
    sys.path.insert(0, pylib_dir)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import urllib3
import requests
from bs4 import BeautifulSoup

# Desactivar advertencias de certificados auto-firmados en MinCiencias
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from src.python.structures.cola import Cola
from src.python.structures.multilista import Multilista
from src.python.core.db import GestorPersistencia

try:
    from pypdf import PdfReader
    PYPDF_DISPONIBLE = True
except ImportError:
    PYPDF_DISPONIBLE = False


def _norm_txt(s: str) -> str:
    """Normaliza texto eliminando acentos y espacios excesivos."""
    import unicodedata
    s = unicodedata.normalize("NFD", (s or "").lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", s).strip()


def clasificar_marcador_gruplac(marcador: str, seccion: str = "") -> str:
    """Clasifica marcadores GrupLAC con whitelist estricta (port compañero).
    Retorna "" si no hay tipo válido (se cuenta como omitido, no se inventa)."""
    m = _norm_txt(marcador).replace("_", " ")
    if m.startswith("publicado en revista"):
        return "Articulo"
    if m.startswith("libro resultado"):
        return "Libro"
    if m.startswith("libros de formaci"):
        return "Libro"
    if m.startswith("otro libro publicado"):
        return "Libro"
    if "capitulo" in m or ("cap" in m and "tulo" in m):
        return "Capitulo"
    if m.startswith("computacional"):
        return "Software"
    if m.startswith("revista de divulgaci"):
        return "Articulo"
    if "de noticias" in m:
        return "Articulo"
    if m.startswith("documento de trabajo"):
        return "Articulo"
    if "patente" in m:
        return "Patente"
    if m.startswith("revision") or "survey" in m:
        return "Articulo"
    if m.startswith("libros de divulgaci") or "compilacion de divulgaci" in m:
        return "Libro"
    if m.startswith("informe tecnico") or m == "informe":
        return "Informe"
    if "consultor" in m:
        return "Consultoria"
    if (m.startswith("encuentro") or m.startswith("congreso") or m.startswith("simposio")
            or m.startswith("seminario") or m.startswith("foro") or m == "taller"):
        if seccion == "formacion" and (m == "taller" or m.startswith("seminario")):
            return "CursoCorto"
        return "Evento"
    if "trabajo de grado" in m or m.startswith("tesis"):
        return "Tesis"
    if "trabajo dirigido" in m or "tutoria" in m:
        return "Tesis"
    if (m.startswith("curso") or "perfeccionamiento" in m or "extension" in m
            or m.startswith("diplomado")):
        return "CursoCorto"
    if "jurado" in m or "comision evaluadora" in m or "comite evaluador" in m:
        return "Jurado"
    if "contenido digital" in m or "produccion de contenido" in m or "audiovisual" in m:
        return "Contenido"
    if m.startswith("edicion") or (m.startswith("compilacion") and "divulgaci" not in m):
        return "Libro"  # Compilación ~ Libro (contrato CHECK SQLite de 15 tipos)
    if m.startswith("regulacion") or m.startswith("norma"):
        return "Regulacion"
    if seccion == "evaluador":
        return "Jurado"
    return ""


SECCIONES_FICHA = (
    ("biblio", r"PRODUCCI.N\s+BIBLIOGR.FICA"),
    ("tecnica", r"PRODUCCI.N\s+T.CNICA"),
    ("apropiacion", r"APROPIACI.N\s+SOCIAL"),
    ("formacion", r"ACTIVIDADES\s+DE\s+FORMACI.N|PRODUCCI.N\s+DE\s+FORMACI.N"),
    ("evaluador", r"COMO\s+EVALUADOR"),
)


def _spans_secciones(texto: str):
    spans = []
    for key, pat in SECCIONES_FICHA:
        for mm in re.finditer(pat, texto, flags=re.IGNORECASE):
            spans.append([key, mm.start(), len(texto)])
    spans.sort(key=lambda s: s[1])
    for i in range(len(spans) - 1):
        spans[i][2] = spans[i + 1][1]
    return spans


def _seccion_de(pos: int, spans) -> str:
    sec = ""
    for key, ini, fin in spans:
        if ini <= pos < fin:
            sec = key
    return sec


def _titulo_bloque(bloque: str, mk: str) -> str:
    mt = re.search(r'"([^"]{8,480})"', bloque)
    if not mt:
        blines = [l.strip() for l in bloque.split("\n") if l.strip()]
        for bl in blines:
            if len(bl) < 8 or re.match(r"^\d+\.-?\s*$", bl):
                continue
            core = re.sub(r"^\d+\.\-?\s*", "", bl).strip().rstrip(":").strip()
            if not core or _norm_txt(core) == mk:
                continue
            mt = re.match(r"(.{8,480})", bl)
            break
    titulo = mt.group(1).strip() if mt else ""
    return titulo.lstrip(":;,.—- ").strip()


def _anio_bloque(bloque: str) -> int:
    ma = re.search(r",\s*((?:19|20)\d{2})\b", bloque)
    anio = int(ma.group(1)) if ma and 1900 <= int(ma.group(1)) <= 2026 else 0
    if not anio:
        md = re.search(r"[Dd]esde\D{0,14}((?:19|20)\d{2})\b", bloque)
        if not md:
            for _bl in bloque.split("\n"):
                if re.search(r"ISSN|DOI|vol|fasc|p.g", _bl, flags=re.IGNORECASE):
                    continue
                md = re.search(r"\b((?:19|20)\d{2})\b", _bl)
                if md:
                    break
        if md and 1900 <= int(md.group(1)) <= 2026:
            anio = int(md.group(1))
    return anio


def _es_titulo_marcador(titulo: str, mk: str) -> bool:
    n = _norm_txt(titulo)
    if not n or n == mk:
        return True
    return n in {"revision survey", "otra", "otro"}


def mapa_chulos_triple(soup) -> dict:
    """{(marcador_norm, titulo_norm[:60], anio): validado_bool}."""
    mapa = {}
    for tr in soup.find_all("tr"):
        imgs = tr.find_all("img")
        ch = [i.get("src", "") for i in imgs if "chulo_" in (i.get("src", ""))]
        if not ch:
            continue
        t = tr.get_text("\n")
        mm = re.search(r"\d+\.\-?\s*([^\n:]{3,60})\s*:", t)
        if not mm:
            continue
        mk = _norm_txt(mm.group(1).strip())
        tit = _titulo_bloque(t, mk)
        if not tit:
            continue
        key = (mk, _norm_txt(tit)[:60], _anio_bloque(t))
        mapa[key] = mapa.get(key, False) or any("chulo_1" in c for c in ch)
    return mapa


def parse_hoja_vida(html: str) -> dict:
    """Extrae datos enriquecidos de la hoja de vida CvLAC oficial."""
    soup = BeautifulSoup(html, "html.parser")
    lines = [l.strip() for l in soup.get_text("\n").split("\n") if l.strip()]
    unido = "\n".join(lines)

    par = "Si" if "Par evaluador reconocido" in unido else "No"
    m_sch = re.search(r'href="(https://scholar\.google[^"]*)"', html)
    m_orc = re.search(r'href="(https://orcid\.org/[^"]*)"', html)

    def _val_etiqueta(etiqueta: str) -> str:
        for i, l in enumerate(lines):
            if l.lower() == etiqueta.lower() and i + 1 < len(lines):
                val = lines[i + 1]
                if not val.startswith("Categor") and len(val) < 120:
                    return val
        return ""

    formacion = ""
    for nivel in ("Doctorado", "Maestr", "Pregrado"):
        for i, l in enumerate(lines):
            if l.startswith(nivel):
                formacion = " | ".join(lines[i:i + 3])[:250]
                break
        if formacion:
            break

    categoria = "Junior"
    for i, l in enumerate(lines):
        if l.startswith("Categor") and i + 1 < len(lines):
            seg = " ".join(lines[i:i + 3]).lower()
            if "senior" in seg or "sénior" in seg or "emerito" in seg or "emérito" in seg:
                categoria = "Senior"
            elif "asociado" in seg:
                categoria = "Asociado"
            elif "junior" in seg:
                categoria = "Junior"
            break

    return {
        "par_evaluador": par,
        "categoria": categoria,
        "nombre_citaciones": _val_etiqueta("Nombre en citaciones"),
        "nacionalidad": _val_etiqueta("Nacionalidad"),
        "sexo": _val_etiqueta("Sexo"),
        "scholar_url": m_sch.group(1) if m_sch else "",
        "orcid": m_orc.group(1) if m_orc else "",
        "formacion_academica": formacion,
        "experiencia": "",
        "areas": "",
        "idiomas": ""
    }


def guardar_perfil_bd(doc_id: str, perfil: dict, ruta_bd: str) -> bool:
    """Persiste los datos curriculares de CvLAC en la tabla PerfilInvestigador."""
    try:
        import sqlite3
        conn = sqlite3.connect(ruta_bd, timeout=5.0)
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode = WAL;")
        cursor.execute("PRAGMA busy_timeout = 5000;")
        cursor.execute("""
            INSERT INTO PerfilInvestigador (
                documento_id, par_evaluador, nombre_citaciones, nacionalidad,
                sexo, scholar_url, orcid, formacion_academica, experiencia, areas, idiomas
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(documento_id) DO UPDATE SET
                par_evaluador = excluded.par_evaluador,
                nombre_citaciones = excluded.nombre_citaciones,
                nacionalidad = excluded.nacionalidad,
                sexo = excluded.sexo,
                scholar_url = excluded.scholar_url,
                orcid = excluded.orcid,
                formacion_academica = excluded.formacion_academica,
                experiencia = excluded.experiencia,
                areas = excluded.areas,
                idiomas = excluded.idiomas;
        """, (
            doc_id,
            perfil.get("par_evaluador", "No"),
            perfil.get("nombre_citaciones", ""),
            perfil.get("nacionalidad", ""),
            perfil.get("sexo", ""),
            perfil.get("scholar_url", ""),
            perfil.get("orcid", ""),
            perfil.get("formacion_academica", ""),
            perfil.get("experiencia", ""),
            perfil.get("areas", ""),
            perfil.get("idiomas", "")
        ))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[!] Error al persistir PerfilInvestigador para {doc_id}: {e}")
        return False


CODIGOS_LEGACY = {
    "GISICO": "COL0018706",
    "COL0002099": "COL0018706",
    "G002668": "COL0043834",
    "G003639": "COL0001351",
    "G0002099": "COL0018706",
    "G002099": "COL0018706"
}


def empaquetar_grupo_zip(codigo: str, nro: str = "", reutilizar: bool = True) -> str:
    """
    Empaqueta los snapshots HTML de un grupo en un archivo .zip individual:
    data/snapshots/zip/grupo_{codigo}.zip (Optimización de Damian para evitar miles de archivos sueltos).
    """
    import zipfile
    snap_dir = os.path.join(PROJECT_ROOT, "data", "snapshots")
    zip_dir = os.path.join(snap_dir, "zip")
    os.makedirs(zip_dir, exist_ok=True)
    dest = os.path.join(zip_dir, f"grupo_{codigo}.zip")

    MAPA_ALIAS = {
        "col0018706": ["2099", "gisico", "col0018706"],
        "col0002099": ["2099", "gisico", "col0002099"],
        "col0043834": ["2668", "col0043834"],
        "col0001351": ["3639", "col0001351"],
        "col0049121": ["3202", "col0049121"]
    }
    claves = [codigo.lower()]
    for al in MAPA_ALIAS.get(codigo.lower(), []):
        if al not in claves:
            claves.append(al)
    if nro:
        claves.append(nro.lower())
        if len(nro) >= 4:
            claves.append(nro[-4:].lower())

    files = []
    if os.path.isdir(snap_dir):
        for root, _, fs in os.walk(snap_dir):
            if os.path.abspath(root).startswith(os.path.abspath(zip_dir)):
                continue
            for f in fs:
                if f.endswith(".html") and any(k in f.lower() for k in claves):
                    files.append(os.path.join(root, f))

    if not files:
        if reutilizar and os.path.exists(dest):
            return dest
        return ""

    if reutilizar and os.path.exists(dest):
        try:
            zt = os.path.getmtime(dest)
            if all(os.path.getmtime(f) <= zt for f in files):
                return dest
        except OSError:
            pass

    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as z:
        for f in files:
            z.write(f, os.path.basename(f))
    return dest


def limpiar_zips_huerfanos() -> list:
    """
    Borra zips legacy cuyo código vigente ya existe (evita zips duplicados / huérfanos).
    """
    eliminados = []
    zip_dir = os.path.join(PROJECT_ROOT, "data", "snapshots", "zip")
    if not os.path.isdir(zip_dir):
        return eliminados

    for viejo, nuevo in CODIGOS_LEGACY.items():
        fv = os.path.join(zip_dir, f"grupo_{viejo}.zip")
        fn = os.path.join(zip_dir, f"grupo_{nuevo}.zip")
        if os.path.exists(fv) and os.path.exists(fn):
            try:
                os.remove(fv)
                eliminados.append(os.path.basename(fv))
            except OSError as e:
                print(f"[!] Aviso al limpiar zip {fv}: {e}")
    if eliminados:
        print(f"[+] Zips huérfanos eliminados: {', '.join(eliminados)}")
    return eliminados


def empaquetar_todos_los_snapshots() -> dict:
    """
    Empaqueta todos los snapshots existentes en data/snapshots hacia sus respectivos zips.
    """
    codigos = ["COL0018706", "COL0002099", "COL0043834", "COL0001351", "COL0049121"]
    resultados = {}
    for cod in codigos:
        z = empaquetar_grupo_zip(cod)
        if z:
            resultados[cod] = z
    limpiar_zips_huerfanos()
    return resultados


def _buscar_snapshot_gruplac(nro_grupo: str) -> str:
    """Busca un snapshot de GrupLAC tanto en la raíz como recursivamente en subcarpetas."""
    snap_dir = os.path.join(PROJECT_ROOT, "data", "snapshots")
    if not os.path.isdir(snap_dir):
        return ""
    cands = [
        os.path.join(snap_dir, f"gruplac_{nro_grupo}.html"),
        os.path.join(snap_dir, f"gruplac_{int(nro_grupo):014d}.html") if nro_grupo.isdigit() else "",
        os.path.join(snap_dir, "gruplac_00000000002099.html") if "2099" in nro_grupo else ""
    ]
    for c in cands:
        if c and os.path.exists(c):
            return c
    zip_dir = os.path.join(snap_dir, "zip")
    for root, _, files in os.walk(snap_dir):
        if os.path.abspath(root).startswith(os.path.abspath(zip_dir)):
            continue
        for f in files:
            if f.endswith(".html") and (nro_grupo in f or (len(nro_grupo) >= 4 and nro_grupo[-4:] in f)):
                if f.startswith("gruplac"):
                    return os.path.join(root, f)
    return ""


def _buscar_snapshot_cvlac(cod_rh: str) -> str:
    """Busca un snapshot de CvLAC en data/snapshots/ o en cualquier subcarpeta de grupo."""
    snap_dir = os.path.join(PROJECT_ROOT, "data", "snapshots")
    if not os.path.isdir(snap_dir):
        return ""
    nom = f"cvlac_{cod_rh}.html"
    nom_pad = f"cvlac_{int(cod_rh):010d}.html" if cod_rh.isdigit() else ""
    if os.path.exists(os.path.join(snap_dir, nom)):
        return os.path.join(snap_dir, nom)
    if nom_pad and os.path.exists(os.path.join(snap_dir, nom_pad)):
        return os.path.join(snap_dir, nom_pad)
    zip_dir = os.path.join(snap_dir, "zip")
    for root, _, files in os.walk(snap_dir):
        if os.path.abspath(root).startswith(os.path.abspath(zip_dir)):
            continue
        if nom in files:
            return os.path.join(root, nom)
        if nom_pad and nom_pad in files:
            return os.path.join(root, nom_pad)
    return ""


def leer_snapshot_cvlac_html(cod_rh: str) -> str:
    """
    Lee el contenido HTML de un snapshot de CvLAC, ya sea de un archivo suelto
    o extrayéndolo directamente en memoria desde un archivo .zip empaquetado.
    """
    import zipfile
    # 1. Intentar archivo suelto
    ruta = _buscar_snapshot_cvlac(cod_rh)
    if ruta and os.path.exists(ruta):
        try:
            with open(ruta, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception:
            pass

    # 2. Intentar buscar en archivos .zip de data/snapshots/zip
    zip_dir = os.path.join(PROJECT_ROOT, "data", "snapshots", "zip")
    nom = f"cvlac_{cod_rh}.html"
    nom_pad = f"cvlac_{int(cod_rh):010d}.html" if cod_rh.isdigit() else ""
    if os.path.isdir(zip_dir):
        for zf in os.listdir(zip_dir):
            if zf.endswith(".zip"):
                ruta_z = os.path.join(zip_dir, zf)
                try:
                    with zipfile.ZipFile(ruta_z, "r") as z:
                        nombres = z.namelist()
                        for target in [nom, nom_pad]:
                            if target and target in nombres:
                                return z.read(target).decode("utf-8", errors="ignore")
                except Exception:
                    pass
    return ""



class MotorIngesta:
    """
    Motor central de procesamiento de fuentes de datos.
    Coordina la Cola TDA y actualiza la Multilista en memoria y SQLite.
    """

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    }

    def __init__(self, ruta_bd: str = "data/pea_investigacion.db"):
        self.ruta_bd = ruta_bd
        self.cola = Cola()

    # -----------------------------------------------------------------
    # WEB SCRAPING: GRUPLAC (MinCiencias)
    # -----------------------------------------------------------------
    def parsear_gruplac(self, url: str, multi: Multilista, procesar_cvlac: bool = True) -> dict:
        """Descarga y extrae los datos de un grupo de investigación desde GrupLAC."""
        resumen = {"grupos": 0, "investigadores": 0, "productos": 0, "validados": 0,
                   "omitidos": 0, "sin_autor": 0, "modo": "ONLINE"}

        # Extraer código de grupo de la URL o nombre de archivo snapshot (parámetro nro o gruplac_XXXX)
        match_cod = re.search(r'(?:nro=|gruplac_)(\d+)', url)
        nro_grupo = match_cod.group(1) if match_cod else "00000000002099"
        sufijo_nro = nro_grupo[-4:] if len(nro_grupo) >= 4 else nro_grupo

        # Resolver código COL oficial desde el índice (66 grupos UPC). Nunca inventa.
        cod_grupo = ""
        try:
            from python.core.busqueda_scienti import resolver_codigo_nro, buscar_grupo_en_indices
            cod_grupo = resolver_codigo_nro(nro_grupo)
            if not cod_grupo:
                cands = buscar_grupo_en_indices(nro_grupo)
                if cands and cands[0].get("col"):
                    cod_grupo = cands[0]["col"]
        except Exception:
            pass

        if not cod_grupo:
            print(f"[!] NRO {nro_grupo} sin código COL en el índice; se omite (no se inventa código).")
            resumen["modo"] = "SIN_CODIGO"
            return resumen

        html_text = ""
        # Verificar primero si url ya es ruta de archivo o si existe snapshot oficial local en data/snapshots/
        snapshot_local = url if os.path.isfile(url) else _buscar_snapshot_gruplac(nro_grupo)

        if snapshot_local and os.path.exists(snapshot_local):
            print(f"[Scraping] Usando snapshot oficial local: {os.path.basename(snapshot_local)}")
            with open(snapshot_local, "r", encoding="utf-8", errors="ignore") as f_snap:
                html_text = f_snap.read()
            resumen["modo"] = "OFFLINE_SNAPSHOT"
        else:
            try:
                print(f"[Scraping] Conectando a MinCiencias GrupLAC ({url})...")
                resp = requests.get(url, headers=self.HEADERS, timeout=8, verify=False)
                if resp.status_code == 200 and len(resp.text) > 1000:
                    html_text = resp.text
                else:
                    raise Exception(f"HTTP Status {resp.status_code}")
            except Exception as e:
                print(f"[!] Error: No se pudo conectar a MinCiencias ({e}) y no existe snapshot local para el grupo {nro_grupo}.")
                resumen["modo"] = "ERROR_SIN_CONEXION"
                return resumen

        soup = BeautifulSoup(html_text, "html.parser")
        texto_plano = soup.get_text("\n")
        lineas_plano = [l.strip() for l in texto_plano.split("\n") if l.strip()]
        existe_ficha = any(l.startswith("Datos b") for l in lineas_plano)
        tiene_encabezado = soup.find("span", class_="celdaEncabezado") is not None
        if not existe_ficha and not tiene_encabezado:
            print(f"[!] Grupo no existente (nro={nro_grupo}): GrupLAC no devuelve ficha.")
            resumen["modo"] = "GRUPO_NO_EXISTENTE"
            return resumen

        # 1. Nombre del Grupo
        nombre_grupo = ""
        span_encabezado = soup.find("span", class_="celdaEncabezado")
        if span_encabezado and span_encabezado.get_text(strip=True):
            nombre_grupo = span_encabezado.get_text(strip=True)
        if not nombre_grupo:
            for i, l in enumerate(lineas_plano):
                if l.startswith("GrupLAC -") and i + 1 < len(lineas_plano):
                    nombre_grupo = lineas_plano[i + 1]
                    break
        if not nombre_grupo:
            print(f"[!] Ficha sin nombre de grupo (nro={nro_grupo}); se omite.")
            resumen["modo"] = "SIN_NOMBRE"
            return resumen

        # 2. Líder
        lider = "Por verificar"
        td_lider = soup.find("td", string=re.compile(r"Líder|Lider", re.I))
        if td_lider and td_lider.find_next_sibling("td"):
            lider = td_lider.find_next_sibling("td").get_text(strip=True).title()

        # 3. Clasificación
        clasificacion = "C"
        td_clas = soup.find("td", string=re.compile(r"Clasificación|Clasificacion", re.I))
        if td_clas and td_clas.find_next_sibling("td"):
            txt_clas = td_clas.find_next_sibling("td").get_text(strip=True)
            for c in ["A1", "A", "B", "C"]:
                if txt_clas.startswith(c):
                    clasificacion = c
                    break

        # 4. Área de Conocimiento
        area = "Ingeniería y Tecnología"
        td_area = soup.find("td", string=re.compile(r"Área de conocimiento|Area de conocimiento", re.I))
        if td_area and td_area.find_next_sibling("td"):
            area = td_area.find_next_sibling("td").get_text(strip=True)
            if "--" in area:
                area = area.split("--")[0].strip()

        # 5. Año de Creación
        anio_creacion = 2005
        for tr in soup.find_all("tr"):
            txt_tr = tr.get_text(strip=True)
            if "Año y mes de formación" in txt_tr:
                m = re.search(r'\b(19\d\d|20\d\d)\b', txt_tr)
                if m:
                    anio_creacion = int(m.group(1))
                break

        # Insertar o actualizar Grupo en la Multilista
        # (los productos viejos solo se reemplazan si el scrape trae productos nuevos;
        # ver bloque 7 para no vaciar grupos existentes)
        g_existente = multi.buscar_grupo(cod_grupo)
        grupo_es_nuevo = g_existente is None
        if not g_existente:
            multi.insertar_grupo(cod_grupo, nombre_grupo, clasificacion, area, lider, anio_creacion, True)
            g_existente = multi.buscar_grupo(cod_grupo)
            resumen["grupos"] += 1
        else:
            g_existente.nombre = nombre_grupo
            g_existente.lider = lider
            g_existente.clasificacion = clasificacion
            g_existente.area_conocimiento = area
            g_existente.anio_creacion = anio_creacion

        # 6. Integrantes del Grupo (con cod_rh de CvLAC y vinculación a PerfilInvestigador)
        mapa_integrantes = {}
        rhs_grupo = []
        vistos_nombres = set()

        for t in soup.find_all("table"):
            th = " ".join(t.get_text(" ").split())
            if "Vinculaci" in th and "Nombre" in th and "Horas" in th:
                for tr in t.find_all("tr")[1:]:
                    tds = [c.get_text(" ").strip() for c in tr.find_all(["td", "th"])]
                    tds = [d for d in tds if d]
                    if len(tds) >= 2 and tds[0] != "Nombre" and "Integrantes del grupo" not in tds[0]:
                        nom_raw = re.sub(r"^\d+\.-\s*", "", tds[0]).strip()
                        if not nom_raw or len(nom_raw) < 3:
                            continue
                        if nom_raw in vistos_nombres:
                            continue
                        vistos_nombres.add(nom_raw)
                        nom_tit = nom_raw.title()

                        cod_rh = ""
                        a_cv = tr.find("a", href=True)
                        if a_cv:
                            m_rh = re.search(r"cod_rh=(\d+)", a_cv.get("href", ""))
                            if m_rh:
                                cod_rh = m_rh.group(1)
                                rhs_grupo.append(cod_rh)

                        # Placeholder documentado si GrupLAC no publica cod_rh (como compañero)
                        doc_inv = cod_rh if cod_rh else f"{cod_grupo}-RH-{len(mapa_integrantes)+1:03d}"

                        cat = "Por verificar"
                        formacion = area

                        # Comprobar si existe snapshot de CvLAC para este investigador (archivo suelto o empaquetado en .zip)
                        html_cv = leer_snapshot_cvlac_html(doc_inv) if cod_rh else ""
                        if html_cv:
                            try:
                                perfil_cv = parse_hoja_vida(html_cv)
                                if perfil_cv.get("formacion_academica"):
                                    formacion = perfil_cv["formacion_academica"][:90]
                                if perfil_cv.get("categoria"):
                                    cat = perfil_cv["categoria"]
                                guardar_perfil_bd(doc_inv, perfil_cv, self.ruta_bd)
                            except Exception:
                                pass

                        inv_prev = multi.buscar_investigador(doc_inv)
                        if not inv_prev:
                            multi.insertar_investigador(cod_grupo, doc_inv, nom_tit, cat, formacion, True)
                            resumen["investigadores"] += 1
                            inv_prev = multi.buscar_investigador(doc_inv)
                        elif inv_prev.codigo_grupo == cod_grupo:
                            inv_prev.nombre_completo = nom_tit
                            if cat != "Por verificar":
                                inv_prev.categoria = cat
                            if formacion != area:
                                inv_prev.formacion_academica = formacion

                        if inv_prev and inv_prev.codigo_grupo == cod_grupo:
                            mapa_integrantes[_norm_txt(nom_raw)] = doc_inv

        # Sin integrantes reales no se persiste grupo vacío (evita grupos vacíos)
        if not mapa_integrantes:
            print(f"[!] {cod_grupo}: sin integrantes parseables; se omite grupo vacío.")
            if grupo_es_nuevo:
                try:
                    multi.eliminar_grupo(cod_grupo)
                except Exception:
                    pass
            resumen["modo"] = "SIN_INTEGRANTES"
            return resumen

        # Pipeline Unificado: procesar en paralelo las hojas de vida CvLAC de los integrantes descubiertos (12 hilos)
        rhs_unicos = sorted(set(rhs_grupo)) if procesar_cvlac else []
        if rhs_unicos:
            print(f"[GrupLAC + CvLAC] Procesando {len(rhs_unicos)} hojas de vida CvLAC en paralelo (12 hilos)...")
            cv_ok = self.scrapear_cvlacs_paralelo(rhs_unicos, max_workers=12)
            print(f"[GrupLAC + CvLAC] Perfiles CvLAC procesados: {cv_ok}/{len(rhs_unicos)}")
            for rh in rhs_unicos:
                h_cv = leer_snapshot_cvlac_html(rh)
                if h_cv:
                    p_cv = parse_hoja_vida(h_cv)
                    nodo_inv = multi.buscar_investigador(rh)
                    if nodo_inv:
                        if p_cv.get("formacion_academica"):
                            nodo_inv.formacion_academica = p_cv["formacion_academica"][:90]
                        if p_cv.get("categoria"):
                            nodo_inv.categoria = p_cv["categoria"]

        # 7. Productos del Grupo (whitelist estricta, chulo triple, sin inventar autoría)
        chulos = mapa_chulos_triple(soup)
        spans = _spans_secciones(texto_plano)
        marcas = [(m.start(), m.group(1).strip()) for m in
                  re.finditer(r"\d+\.\-?\s*([^\n:]{3,60})\s*:", texto_plano)]
        marcas.append((len(texto_plano), ""))
        prods_parsed = []
        omitidos = 0
        for idx in range(len(marcas) - 1):
            inicio, marcador_raw = marcas[idx]
            bloque = texto_plano[inicio:marcas[idx + 1][0]]
            mk = _norm_txt(marcador_raw)
            sec = _seccion_de(inicio, spans)
            tipo = clasificar_marcador_gruplac(marcador_raw, sec)
            if not tipo:
                if mk in ("otra", "otro") and any(
                        k in _norm_txt(bloque[:400]) for k in
                        ("disponibilidad", "nombre comercial", "financiadora", "sitio web")):
                    tipo = "Software"
                elif mk in ("otra", "otro") and sec == "apropiacion":
                    tipo = "Evento"
                else:
                    omitidos += 1
                    continue
            titulo = _titulo_bloque(bloque, mk)
            if _es_titulo_marcador(titulo, mk):
                omitidos += 1
                continue
            if re.match(r"^[A-Za-záéíóúñü]+\s*,\s*(?:19|20)\d{2}\s*,?$", titulo):
                omitidos += 1
                continue
            anio = _anio_bloque(bloque)
            maut = re.search(r"Autores:\s*([^\n]+(?:\n[^\n:]+)?)", bloque)
            if not maut:
                maut = re.search(
                    r"(?:Tutor\(es\)/Cotutor\(es\)|Tutores?/Cotutores?|Estudiante|Director|"
                    r"Tutor|Asesor|Orientador|Organizador|Ponente|Responsable|Compilador|"
                    r"Consultor)[es]*\s*:\s*([^\n]+(?:\n[^\n:]+)?)",
                    bloque)
            autores = []
            if maut:
                autores = [a.strip().rstrip(".") for a in re.split(r",", maut.group(1)) if a.strip()]
            if titulo and anio:
                validado = chulos.get((mk, _norm_txt(titulo)[:60], anio), False)
                prods_parsed.append({"titulo": titulo[:110], "anio": anio, "tipo": tipo,
                                     "autores": autores,
                                     "validado": validado})
            else:
                omitidos += 1
        resumen["omitidos"] = omitidos

        # Solo reemplazar productos viejos si hay productos nuevos (no vaciar)
        if prods_parsed and g_existente and g_existente.primer_producto:
            prods_viejos = []
            p_cur = g_existente.primer_producto
            while p_cur:
                prods_viejos.append(p_cur.id_producto)
                p_cur = p_cur.sig_producto_grupo
            for pid_v in prods_viejos:
                multi.eliminar_producto(pid_v)

        # Atribuir autoría solo a integrantes macheados (sin inventar)
        prod_count = 0
        sin_autor = 0
        normas_vistas = set()
        for p in prods_parsed:
            rhs = []
            for a in p["autores"]:
                na = _norm_txt(a)
                if na in mapa_integrantes and mapa_integrantes[na] not in rhs:
                    rhs.append(mapa_integrantes[na])
            if not rhs:
                # Fallback por apellidos (como antes) antes de descartar
                for a in p["autores"]:
                    na = _norm_txt(a)
                    for nom_k, doc_k in mapa_integrantes.items():
                        apellidos = [w for w in nom_k.split() if len(w) > 3]
                        if (na in nom_k or nom_k in na or
                                (len(apellidos) >= 2 and apellidos[-1] in na and apellidos[-2] in na)):
                            if doc_k not in rhs:
                                rhs.append(doc_k)
                            break
                    if rhs:
                        break
            if not rhs:
                sin_autor += 1
                continue
            norma = re.sub(r"[^a-z0-9]+", "", _norm_txt(p["titulo"])) + f"|{p['anio']}"
            if norma in normas_vistas:
                continue
            normas_vistas.add(norma)
            for rh in dict.fromkeys(rhs):
                prod_count += 1
                id_prod = f"PROD-{sufijo_nro}-{prod_count:04d}"
                if not multi.buscar_producto(id_prod):
                    multi.insertar_producto(cod_grupo, rh, id_prod, p["tipo"], p["titulo"],
                                            p["anio"], "Por verificar", p["validado"], True)
                    resumen["productos"] += 1
                    if p["validado"]:
                        resumen["validados"] += 1
        resumen["sin_autor"] = sin_autor

        # Empaquetar snapshots del grupo en su archivo ZIP correspondiente
        try:
            empaquetar_grupo_zip(cod_grupo)
        except Exception:
            pass

        return resumen

    # -----------------------------------------------------------------
    # WEB SCRAPING: CVLAC (MinCiencias)
    # -----------------------------------------------------------------
    def parsear_cvlac(self, url: str, multi: Multilista) -> dict:
        """Descarga y extrae los datos de un investigador desde CvLAC."""
        resumen = {"grupos": 0, "investigadores": 0, "productos": 0, "modo": "ONLINE"}

        match_cod = re.search(r'cod_rh=(\d+)', url)
        cod_rh = match_cod.group(1) if match_cod else "0000494917"

        # Asegurar que exista un grupo receptor por defecto
        cod_grupo_def = "COL0018706"
        if not multi.buscar_grupo(cod_grupo_def):
            multi.insertar_grupo(cod_grupo_def, "GRUPO DE INVESTIGACIÓN GISICO (UPC)", "C", "Ingeniería y Tecnología", "John Jairo Patiño Vanegas", 2005, True)
            resumen["grupos"] += 1

        html_text = ""
        # Buscar snapshot CvLAC en disco o dentro de paquetes .zip
        html_snap = leer_snapshot_cvlac_html(cod_rh)
        if html_snap:
            print(f"[Scraping] Usando snapshot oficial local CvLAC (disco o .zip): cod_rh={cod_rh}")
            html_text = html_snap
            resumen["modo"] = "OFFLINE_SNAPSHOT"
        else:
            try:
                print(f"[Scraping] Conectando a MinCiencias CvLAC ({url})...")
                resp = requests.get(url, headers=self.HEADERS, timeout=12, verify=False)
                if resp.status_code == 200 and len(resp.text) > 1000:
                    html_text = resp.text
                else:
                    raise Exception(f"HTTP Status {resp.status_code}")
            except Exception as e:
                print(f"[!] Error: No se pudo conectar a CvLAC en vivo ({e}) y no existe snapshot para cod_rh={cod_rh}.")
                resumen["modo"] = "ERROR_SIN_CONEXION"
                return resumen

        # Parsear Hoja de Vida CvLAC enriquecida
        perfil_cv = parse_hoja_vida(html_text)

        soup = BeautifulSoup(html_text, "html.parser")
        lines = [l.strip() for l in soup.get_text("\n").split("\n") if l.strip()]

        # 1. Nombre Completo
        nombre_investigador = "Adith Bismarck Pérez Orozco"
        for i, l in enumerate(lines):
            if l == "Nombre" and i + 1 < len(lines):
                nombre_investigador = lines[i + 1].replace("\xa0", " ").strip()
                break

        # 2. Categoría MinCiencias
        categoria = "Senior"
        for i, l in enumerate(lines):
            if l.startswith("Categor"):
                seg = " ".join(lines[i:i + 3]).lower()
                if "senior" in seg or "sénior" in seg or "emerito" in seg:
                    categoria = "Senior"
                elif "asociado" in seg:
                    categoria = "Asociado"
                elif "junior" in seg:
                    categoria = "Junior"
                break

        # 3. Formación Académica
        formacion = perfil_cv.get("formacion_academica") or "Doctorado en Ingeniería de Sistemas"

        # Registrar o actualizar Investigador
        inv_existente = multi.buscar_investigador(cod_rh)
        if not inv_existente:
            multi.insertar_investigador(cod_grupo_def, cod_rh, nombre_investigador, categoria, formacion, True)
            resumen["investigadores"] += 1
        else:
            inv_existente.nombre_completo = nombre_investigador
            inv_existente.categoria = categoria

        # Guardar en la tabla PerfilInvestigador
        guardar_perfil_bd(cod_rh, perfil_cv, self.ruta_bd)

        # 4. Productos de CvLAC
        texto_unido = "\n".join(lines)
        partes_art = re.split(r"Publicado en revista especializada", texto_unido)
        prod_count = 0
        for blk in partes_art[1:]:
            mt = re.search(r'"([^"]{8,480})"', blk)
            ma = re.search(r",\s*((?:19|20)\d{2})\s*,", blk)
            if mt:
                prod_count += 1
                anio = int(ma.group(1)) if ma and 1900 <= int(ma.group(1)) <= 2026 else 2024
                id_p = f"CVLAC-{cod_rh[-4:]}-{prod_count:03d}"
                titulo = mt.group(1).strip()[:110]
                if not multi.buscar_producto(id_p):
                    multi.insertar_producto(cod_grupo_def, cod_rh, id_p, "Articulo", titulo, anio, "A1", True, True)
                    resumen["productos"] += 1
                if prod_count >= 20:
                    break

        return resumen

    # -----------------------------------------------------------------
    # PARSER DE ARCHIVOS CSV
    # -----------------------------------------------------------------
    def parsear_csv(self, ruta_csv: str, multi: Multilista) -> dict:
        """Procesa un archivo CSV con columnas de grupos, investigadores y productos."""
        resumen = {"grupos": 0, "investigadores": 0, "productos": 0, "modo": "ARCHIVO_CSV"}

        if not os.path.exists(ruta_csv):
            raise FileNotFoundError(f"Archivo CSV no encontrado: {ruta_csv}")

        with open(ruta_csv, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cod_g = row.get("codigo_grupo", "").strip()
                nom_g = row.get("nombre_grupo", "").strip()
                doc_i = row.get("documento_investigador", "").strip()
                nom_i = row.get("nombre_investigador", "").strip()
                id_p = row.get("id_producto", "").strip()
                tipo_p = row.get("tipo_producto", "Articulo").strip()
                tit_p = row.get("titulo_producto", "").strip()
                anio_p = int(row.get("anio", 2024))
                cat_p = row.get("categoria", "A1").strip()
                val_p = str(row.get("validado", "1")).strip() in ["1", "true", "True"]

                # 1. Grupo
                if cod_g and not multi.buscar_grupo(cod_g):
                    multi.insertar_grupo(cod_g, nom_g, "A1", "Ingeniería", "Líder Asignado", 2010, True)
                    resumen["grupos"] += 1

                # 2. Investigador
                if doc_i and not multi.buscar_investigador(doc_i):
                    multi.insertar_investigador(cod_g, doc_i, nom_i, "Asociado", "Ingeniería", True)
                    resumen["investigadores"] += 1

                # 3. Producto
                if id_p and not multi.buscar_producto(id_p):
                    multi.insertar_producto(cod_g, doc_i, id_p, tipo_p, tit_p, anio_p, cat_p, val_p, True)
                    resumen["productos"] += 1

        return resumen

    # -----------------------------------------------------------------
    # PARSER DE DOCUMENTOS PDF (pypdf)
    # -----------------------------------------------------------------
    def parsear_pdf(self, ruta_pdf: str, multi: Multilista) -> dict:
        """Extrae metadatos y publicaciones científicas de un archivo PDF."""
        resumen = {"grupos": 0, "investigadores": 0, "productos": 0, "modo": "ARCHIVO_PDF"}

        if not os.path.exists(ruta_pdf):
            raise FileNotFoundError(f"Archivo PDF no encontrado: {ruta_pdf}")

        if not PYPDF_DISPONIBLE:
            raise ImportError("La librería pypdf no está disponible en este entorno.")

        reader = PdfReader(ruta_pdf)
        texto_completo = ""
        for page in reader.pages[:5]: # Primeras 5 páginas
            t = page.extract_text()
            if t:
                texto_completo += t + "\n"

        meta = reader.metadata or {}
        titulo = meta.get("/Title")
        autor = meta.get("/Author")

        # Si no hay metadatos embebidos, extraer desde el texto
        if not titulo or len(titulo) < 5:
            lineas = [l.strip() for l in texto_completo.split("\n") if len(l.strip()) > 10]
            titulo = lineas[0] if lineas else "Artículo de Investigación Científica (PDF)"

        if not autor or len(autor) < 3:
            autor = "Adith Pérez (Investigador UPC)"

        # Extraer año
        m_anio = re.search(r'\b(20[0-2]\d|19[89]\d)\b', texto_completo)
        anio = int(m_anio.group(1)) if m_anio else 2024

        # Grupo e Investigador por defecto si no existen
        cod_grupo = "COL0018706"
        if not multi.buscar_grupo(cod_grupo):
            multi.insertar_grupo(cod_grupo, "GRUPO DE INVESTIGACIÓN GISICO (UPC)", "C", "Ingeniería y Tecnología", "John Jairo Patiño Vanegas", 2005, True)
            resumen["grupos"] += 1

        doc_inv = "0000494917"
        if not multi.buscar_investigador(doc_inv):
            multi.insertar_investigador(cod_grupo, doc_inv, autor, "Senior", "Ingeniería de Sistemas", True)
            resumen["investigadores"] += 1

        nombre_archivo = os.path.basename(ruta_pdf)
        import hashlib
        h_pdf = hashlib.sha256((nombre_archivo + titulo).encode("utf-8", errors="ignore")).hexdigest()[:8].upper()
        id_prod = f"PDF-{h_pdf}"
        if not multi.buscar_producto(id_prod):
            multi.insertar_producto(cod_grupo, doc_inv, id_prod, "Articulo", titulo[:110], anio, "A1", True, True)
            resumen["productos"] += 1

        return resumen

    def scrapear_cvlacs_paralelo(self, lista_cod_rh: list, max_workers: int = 12) -> int:
        """
        Descarga o procesa hojas de vida CvLAC en paralelo usando ThreadPoolExecutor(max_workers=12).
        Optimización basada en la solución de Damian para acelerar el procesamiento concurrente de perfiles.
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed
        import threading

        exitos = 0
        cerrojo = threading.Lock()

        def _procesar_uno(rh):
            try:
                html = leer_snapshot_cvlac_html(rh)
                if not html:
                    url = f"https://scienti.minciencias.gov.co/cvlac/visualizador/generarCurriculoCv.do?cod_rh={rh}"
                    r = requests.get(url, headers=self.HEADERS, timeout=12, verify=False)
                    if r.status_code == 200 and len(r.text) > 1000:
                        html = r.text
                if html:
                    p = parse_hoja_vida(html)
                    guardar_perfil_bd(rh, p, self.ruta_bd)
                    return rh, True
                return rh, False
            except Exception:
                return rh, False

        if not lista_cod_rh:
            return 0

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futuros = {executor.submit(_procesar_uno, rh): rh for rh in lista_cod_rh}
            for fut in as_completed(futuros):
                rh, ok = fut.result()
                if ok:
                    with cerrojo:
                        exitos += 1
        return exitos

    # -----------------------------------------------------------------
    # PROCESAMIENTO MEDIANTE TDA COLA (FIFO)
    # -----------------------------------------------------------------
    def ejecutar_ingesta(self, tipo_fuente: str, origen: str) -> bool:
        """
        Punto de entrada maestro: Encola en la Cola FIFO, carga RAM, procesa,
        y persiste el resultado en SQLite.
        """
        print("=================================================================")
        print("        PEA-i: MOTOR DE INGESTA Y PARSERS (TDA COLA FIFO)        ")
        print("=================================================================")
        print(f"[+] Encolando tarea de ingesta en la Cola FIFO...")
        print(f"    • Tipo de fuente: {tipo_fuente}")
        print(f"    • Origen / Ruta:  {origen}")

        # 1. Encolar en el TDA Cola
        self.cola.encolar(tipo_fuente, origen, f"Procesamiento de {origen}")
        print(f"[OK] Tarea encolada exitosamente. Elementos en cola: {self.cola.tamano()}")

        # 2. Desencolar para procesar (FIFO)
        tarea = self.cola.desencolar()
        print(f"\n[+] Desencolando tarea prioritaria del frente de la cola...")

        # 3. Cargar la Multilista actual desde SQLite
        multi = Multilista()
        GestorPersistencia.cargar_desde_bd(multi, self.ruta_bd)

        # 4. Procesar según el tipo de fuente
        resumen = {}
        try:
            if tarea.tipo_fuente in ["URL_GRUPLAC", "URL"]:
                if "cvlac" in tarea.ruta_o_url.lower():
                    resumen = self.parsear_cvlac(tarea.ruta_o_url, multi)
                else:
                    resumen = self.parsear_gruplac(tarea.ruta_o_url, multi)
            elif tarea.tipo_fuente == "URL_CVLAC":
                resumen = self.parsear_cvlac(tarea.ruta_o_url, multi)
            elif tarea.tipo_fuente in ["ARCHIVO_CSV", "CSV"]:
                resumen = self.parsear_csv(tarea.ruta_o_url, multi)
            elif tarea.tipo_fuente in ["ARCHIVO_PDF", "PDF"]:
                resumen = self.parsear_pdf(tarea.ruta_o_url, multi)
            else:
                print(f"[!] Tipo de fuente no reconocido: {tarea.tipo_fuente}")
                return False

            # 5. Persistir el nuevo estado a SQLite
            print("\n[+] Sincronizando datos extraídos con la Base de Datos SQLite...")
            if not GestorPersistencia.guardar_en_bd(multi, self.ruta_bd):
                print("[ERROR] No se pudo persistir en SQLite (revisa CHECK constraints / esquema).")
                print("        Los cambios quedan solo en RAM y NO se guardaron en disco.")
                return False

            # 6. Reporte de resultados
            print(f"[OK] Ingesta completada con éxito en modo: {resumen.get('modo', 'ESTÁNDAR')}")
            print("-----------------------------------------------------------------")
            print(f"  • Nuevos Grupos registrados:         {resumen.get('grupos', 0)}")
            print(f"  • Nuevos Investigadores registrados: {resumen.get('investigadores', 0)}")
            print(f"  • Nuevos Productos indexados:        {resumen.get('productos', 0)}")
            print(f"  • Omitidos por whitelist:            {resumen.get('omitidos', 0)}")
            print(f"  • Sin autor macheado (descartados):  {resumen.get('sin_autor', 0)}")
            print(f"  • Estado total en la Multilista:     {multi.contar_grupos(False)} grupos, "
                  f"{multi.contar_investigadores(False)} investigadores, "
                  f"{multi.contar_productos(False)} productos.")
            print("=================================================================\n")
            return True

        except Exception as e:
            print(f"[ERROR Ingesta] Falló el procesamiento de la fuente: {e}")
            import traceback
            traceback.print_exc()
            return False

    # -----------------------------------------------------------------
    # INGESTA AUTOMÁTICA EN LOTE DE WEB SCRAPING (GRUPLAC + CVLAC)
    # -----------------------------------------------------------------
    def ejecutar_ingesta_automatica(self, nros: list = None, forzar: bool = False,
                                        con_cvlac: bool = True, lote_checkpoint: int = 5,
                                        solo_snapshots: bool = True) -> bool:
        """
        Ingesta masiva de grupos UPC usando Cola FIFO con checkpoint por grupo.
        - Si nros es None, lee los 66 grupos de indice_grupos.json[947].
        - GISICO (02099) se procesa al final para no robar integrantes.
        - Cada `lote_checkpoint` grupos se persiste a SQLite (no se pierde avance).
        - Nunca persiste grupos vacíos (parsear_gruplac los descarta antes).
        - Con solo_snapshots=True (defecto) se omiten grupos sin snapshot local
          para no colgar la demo con 60 descargas en vivo; usar --con-red para vivo.
        """
        print("=================================================================")
        print("   PEA-i: INGESTA AUTOMATICA MASIVA DE WEB SCRAPING (COLA FIFO)  ")
        print("=================================================================")

        snap_dir = os.path.join(PROJECT_ROOT, "data", "snapshots")
        if nros is None:
            try:
                from python.core.busqueda_scienti import listar_grupos_upc
                grupos_upc = listar_grupos_upc()
                nros = [str(g.get("nro", "")).strip() for g in grupos_upc
                        if str(g.get("nro", "")).strip()]
            except Exception as e:
                print(f"[!] No se pudo leer el índice UPC ({e}); usando 4 base.")
                nros = []
            if not nros:
                nros = ["00000000003639", "00000000003202", "00000000002668", "00000000002099"]
        # GISICO al final
        nros_orden = [n for n in nros if not n.endswith("02099")]
        nros_orden += [n for n in nros if n.endswith("02099")]
        # Extras sueltos en snapshots raíz solo en modo completo (compatibilidad)
        if nros is None and os.path.isdir(snap_dir):
            for fname in sorted(os.listdir(snap_dir)):
                if fname.startswith("gruplac_") and fname.endswith(".html"):
                    m = re.search(r"gruplac_(\d{4,14})\.html", fname)
                    if m and m.group(1) not in nros_orden:
                        nros_orden.append(m.group(1))

        # Idempotencia S32: omitir ya cargados salvo forzar; omitir sin snapshot salvo --con-red
        from python.core.busqueda_scienti import existe_grupo_en_bd
        nros_pend = []
        nros_omit = 0
        nros_sin_snap = 0
        for nro in nros_orden:
            if not forzar:
                cod_ex, _ = existe_grupo_en_bd(nro, self.ruta_bd)
                if cod_ex:
                    nros_omit += 1
                    continue
            if solo_snapshots and not _buscar_snapshot_gruplac(nro):
                nros_sin_snap += 1
                continue
            nros_pend.append(nro)
        print(f"[+] Grupos en índice: {len(nros_orden)} | ya cargados (omitidos): {nros_omit} "
              f"| sin snapshot (omitidos): {nros_sin_snap} | a procesar: {len(nros_pend)}")
        for nro in nros_pend:
            url_g = f"https://scienti.minciencias.gov.co/gruplac/jsp/visualiza/visualizagr.jsp?nro={nro}"
            self.cola.encolar("URL_GRUPLAC", url_g, f"Scraping automático GrupLAC nro={nro}")

        print(f"[+] Se encolaron {self.cola.tamano()} fuentes GrupLAC en la Cola FIFO.")

        multi = Multilista()
        GestorPersistencia.cargar_desde_bd(multi, self.ruta_bd)

        tot_g, tot_i, tot_p, tot_val, tot_omit, tot_sinautor = 0, 0, 0, 0, 0, 0
        procesados = 0
        while not self.cola.esta_vacia():
            tarea = self.cola.desencolar()
            print(f"  -> Desencolando (FIFO): {tarea.descripcion}")
            try:
                res = self.parsear_gruplac(tarea.ruta_o_url, multi, procesar_cvlac=con_cvlac)
            except Exception as e:
                print(f"     [!] Fallo grupo ({e}); se continúa con el siguiente.")
                continue
            tot_g += res.get("grupos", 0)
            tot_i += res.get("investigadores", 0)
            tot_p += res.get("productos", 0)
            tot_val += res.get("validados", 0)
            tot_omit += res.get("omitidos", 0)
            tot_sinautor += res.get("sin_autor", 0)
            procesados += 1
            if procesados % lote_checkpoint == 0:
                print(f"     [checkpoint] {procesados} grupos -> guardando en SQLite...")
                if not GestorPersistencia.guardar_en_bd(multi, self.ruta_bd):
                    print("     [ERROR checkpoint] Falló el guardado; se aborta la masiva.")
                    return False

        # CvLAC en paralelo solo si hay integrantes nuevos y con_cvlac
        perfiles_ok = 0
        if con_cvlac:
            cods_cvlac = []
            if os.path.isdir(snap_dir):
                for root, _, fs in os.walk(snap_dir):
                    for f in fs:
                        m_cv = re.match(r"cvlac_(\d+)\.html", f)
                        if m_cv:
                            cods_cvlac.append(m_cv.group(1))
            cods_cvlac = sorted(set(cods_cvlac))
            if cods_cvlac:
                perfiles_ok = self.scrapear_cvlacs_paralelo(cods_cvlac, max_workers=12)

        # Empaquetar snapshots en .zip por grupo sin duplicados
        empaquetar_todos_los_snapshots()

        # Guardar Multilista actualizada en SQLite
        print("\n[+] Persistiendo Multilista enriquecida en SQLite...")
        if not GestorPersistencia.guardar_en_bd(multi, self.ruta_bd):
            print("[ERROR] Falló el guardado en SQLite; la BD conserva el estado previo.")
            return False

        print("[OK] Ingesta Automática de Web Scraping finalizada exitosamente:")
        print(f"     • Grupos nuevos en esta corrida:    {tot_g}")
        print(f"     • Investigadores nuevos:            {tot_i}")
        print(f"     • Perfiles CvLAC (Scholar/ORCID):   {perfiles_ok} actualizados en paralelo")
        print(f"     • Productos nuevos:                 {tot_p} ({tot_val} con chulo_1, "
              f"{tot_omit} omitidos por whitelist, {tot_sinautor} sin autor)")
        print(f"     • Grupos totales en BD:             {multi.contar_grupos(False)}")
        print("=================================================================\n")
        return True

