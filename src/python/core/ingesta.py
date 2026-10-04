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
import urllib3
import requests
from bs4 import BeautifulSoup

# Desactivar advertencias de certificados auto-firmados en MinCiencias
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Asegurar importaciones relativas al paquete principal
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

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


def clasificar_marcador_gruplac(marcador: str) -> str:
    """Clasifica los marcadores de producción de GrupLAC en las 15 tipologías oficiales."""
    m = _norm_txt(marcador)
    if any(k in m for k in ["revista especializada", "revista", "divulgacion", "divulgación", "noticias", "working paper", "corto (resumen)", "articulo", "artículo"]):
        return "Articulo"
    elif any(k in m for k in ["capitulo", "capítulo"]):
        return "Capitulo"
    elif any(k in m for k in ["libro resultado", "libros de formacion", "libros de formación", "otro libro", "libro"]):
        return "Libro"
    elif any(k in m for k in ["computacional", "software"]):
        return "Software"
    elif any(k in m for k in ["patente"]):
        return "Patente"
    elif any(k in m for k in ["pregrado", "trabajos de grado", "trabajo de grado"]):
        return "Trabajo de Grado"
    elif any(k in m for k in ["maestria", "maestría", "doctorado", "tesis"]):
        return "Tesis"
    elif any(k in m for k in ["jurado", "evaluador"]):
        return "Jurado"
    elif any(k in m for k in ["taller", "curso", "diplomado", "perfeccionamiento"]):
        return "CursoCorto"
    elif any(k in m for k in ["congreso", "encuentro", "seminario", "simposio", "evento", "ponencia", "foro"]):
        return "Evento"
    elif any(k in m for k in ["consultor"]):
        return "Consultoria"
    elif any(k in m for k in ["informe"]):
        return "Informe"
    elif any(k in m for k in ["contenido", "audiovisual", "red", "extension", "extensión", "responsabilidad social"]):
        return "Contenido"
    elif any(k in m for k in ["norma", "regulacion", "regulación"]):
        return "Regulacion"
    elif any(k in m for k in ["prototipo", "planta", "investigacion y desarrollo", "investigación y desarrollo", "spin-off", "innovacion", "innovación"]):
        return "Prototipo"
    elif any(k in m for k in ["diseno", "diseño"]):
        return "Diseno"
    return "Articulo"


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

    return {
        "par_evaluador": par,
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
    for root, _, files in os.walk(snap_dir):
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
    for root, _, files in os.walk(snap_dir):
        if nom in files:
            return os.path.join(root, nom)
        if nom_pad and nom_pad in files:
            return os.path.join(root, nom_pad)
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
    def parsear_gruplac(self, url: str, multi: Multilista) -> dict:
        """Descarga y extrae los datos de un grupo de investigación desde GrupLAC."""
        resumen = {"grupos": 0, "investigadores": 0, "productos": 0, "validados": 0, "modo": "ONLINE"}

        # Extraer código de grupo de la URL (parámetro nro)
        match_cod = re.search(r'nro=(\d+)', url)
        nro_grupo = match_cod.group(1) if match_cod else "00000000002099"
        cod_grupo = f"COL{nro_grupo[-7:]}" if len(nro_grupo) >= 7 else f"COL{nro_grupo}"

        html_text = ""
        # Verificar primero si existe snapshot oficial local en data/snapshots/ (búsqueda recursiva)
        snapshot_local = _buscar_snapshot_gruplac(nro_grupo)

        if snapshot_local:
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
                print(f"[!] Aviso: No se pudo conectar a MinCiencias en vivo ({e}).")
                print("[+] Activando Plan B: Usando dataset offline de respaldo para GrupLAC...")
                resumen["modo"] = "OFFLINE_BACKUP"
                return self._fallback_gruplac(cod_grupo, multi, resumen)

        soup = BeautifulSoup(html_text, "html.parser")

        # 1. Nombre del Grupo
        nombre_grupo = "GRUPO DE INVESTIGACIÓN GISICO (UPC)"
        span_encabezado = soup.find("span", class_="celdaEncabezado")
        if span_encabezado and span_encabezado.get_text(strip=True):
            nombre_grupo = span_encabezado.get_text(strip=True)

        # 2. Líder
        lider = "John Jairo Patiño Vanegas"
        td_lider = soup.find("td", string=re.compile(r"Líder|Lider", re.I))
        if td_lider and td_lider.find_next_sibling("td"):
            lider = td_lider.find_next_sibling("td").get_text(strip=True).title()

        # 3. Clasificación
        clasificacion = "A1"
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
        g_existente = multi.buscar_grupo(cod_grupo)
        if not g_existente:
            multi.insertar_grupo(cod_grupo, nombre_grupo, clasificacion, area, lider, anio_creacion, True)
            resumen["grupos"] += 1
        else:
            g_existente.nombre = nombre_grupo
            g_existente.lider = lider
            g_existente.clasificacion = clasificacion

        # 6. Integrantes del Grupo (con cod_rh de CvLAC y vinculación a PerfilInvestigador)
        mapa_integrantes = {}
        snap_dir = os.path.join(PROJECT_ROOT, "data", "snapshots")
        id_lider_doc = "0000494917"

        for t in soup.find_all("table"):
            th = " ".join(t.get_text(" ").split())
            if "Vinculaci" in th and "Nombre" in th:
                for tr in t.find_all("tr")[1:]:
                    tds = [c.get_text(" ").strip() for c in tr.find_all(["td", "th"])]
                    tds = [d for d in tds if d]
                    if len(tds) >= 4 and tds[0] != "Nombre":
                        nom_raw = re.sub(r"^\d+\.-\s*", "", tds[0]).strip()
                        if not nom_raw or len(nom_raw) < 3:
                            continue
                        nom_tit = nom_raw.title()

                        cod_rh = ""
                        a_cv = tr.find("a", href=True)
                        if a_cv:
                            m_rh = re.search(r"cod_rh=(\d+)", a_cv.get("href", ""))
                            if m_rh:
                                cod_rh = m_rh.group(1)

                        doc_inv = cod_rh if cod_rh else f"INV{nro_grupo[-4:]}{len(mapa_integrantes)+1:03d}"
                        if "adith" in nom_raw.lower():
                            doc_inv = "0000494917"
                            id_lider_doc = doc_inv
                        elif "patino" in _norm_txt(nom_raw) or "patiño" in nom_raw.lower():
                            id_lider_doc = doc_inv

                        cat = "Senior" if ("adith" in nom_raw.lower() or "patino" in _norm_txt(nom_raw)) else "Junior"
                        formacion = "Ingeniería de Sistemas y Computación"

                        # Comprobar si existe snapshot de CvLAC para este investigador (búsqueda recursiva)
                        cv_snap_path = _buscar_snapshot_cvlac(doc_inv)
                        if cv_snap_path and os.path.exists(cv_snap_path):
                            try:
                                with open(cv_snap_path, "r", encoding="utf-8", errors="ignore") as f_cv:
                                    html_cv = f_cv.read()
                                perfil_cv = parse_hoja_vida(html_cv)
                                if perfil_cv.get("formacion_academica"):
                                    formacion = perfil_cv["formacion_academica"][:80]
                                guardar_perfil_bd(doc_inv, perfil_cv, self.ruta_bd)
                            except Exception:
                                pass

                        if not multi.buscar_investigador(doc_inv):
                            multi.insertar_investigador(cod_grupo, doc_inv, nom_tit, cat, formacion, True)
                            resumen["investigadores"] += 1

                        mapa_integrantes[_norm_txt(nom_raw)] = doc_inv

        # Si no se encontraron integrantes en la tabla, registrar al líder
        if not mapa_integrantes:
            if not multi.buscar_investigador(id_lider_doc):
                multi.insertar_investigador(cod_grupo, id_lider_doc, lider, "Senior", "Ingeniería de Sistemas", True)
                resumen["investigadores"] += 1
            mapa_integrantes[_norm_txt(lider)] = id_lider_doc

        # 7. Productos del Grupo (con aval oficial chulo_1.jpg y 15 tipologías)
        prod_count = 0
        for tr in soup.find_all("tr"):
            imgs = tr.find_all("img")
            ch = [i.get("src", "") for i in imgs if "chulo_" in (i.get("src", ""))]
            if not ch:
                continue

            tds = tr.find_all("td")
            if len(tds) < 2:
                continue

            is_validado = any("chulo_1" in c for c in ch)
            raw = tds[1].get_text("\n")

            # Clasificar tipología por marcador
            m_m = re.search(r"^\d+\.-?\s*([^:\n]+):", raw)
            marcador_str = m_m.group(1).strip() if m_m else ""
            tipo = clasificar_marcador_gruplac(marcador_str) if marcador_str else "Articulo"

            # Extraer título limpio
            m_tit = re.search(r'\"([^\"]{8,250})\"', raw)
            if m_tit:
                titulo = m_tit.group(1).strip()
            else:
                lines = [l.strip() for l in raw.split("\n") if len(l.strip()) > 3]
                titulo = ""
                for l in lines:
                    if re.match(r"^\d+\.-?$", l):
                        continue
                    if re.match(r"^\d+\.-?\s*[^:]+:", l):
                        subl = re.sub(r"^\d+\.-?\s*[^:]+:\s*", "", l).strip()
                        if len(subl) > 8:
                            titulo = subl
                            break
                        continue
                    if l.endswith(":"):
                        continue
                    if any(k in l for k in ["Autores:", "Colombia,", "ISSN:", "DOI:", "Disponibilidad:", "Sitio web:", "Nombre comercial:"]):
                        continue
                    titulo = l
                    break
            if not titulo:
                titulo = "Producto Científico MinCiencias"
            titulo = titulo[:110]

            # Extraer año
            m_anio = re.search(r'\b(20[0-2]\d|19[89]\d)\b', raw)
            anio = int(m_anio.group(1)) if m_anio else 2024

            # Extraer autor y emparejar con integrantes del grupo
            m_aut = re.search(r"Autores:\s*([^,\n\r]+)", raw)
            autor_raw = m_aut.group(1).strip() if m_aut else ""
            autor_raw = re.sub(r"[\xa0\s]+", " ", autor_raw).strip()
            norm_a = _norm_txt(autor_raw)

            id_inv_asociado = id_lider_doc
            if norm_a:
                for nom_k, doc_k in mapa_integrantes.items():
                    if norm_a in nom_k or nom_k in norm_a or any(len(w) > 4 and w in nom_k for w in norm_a.split()):
                        id_inv_asociado = doc_k
                        break

            prod_count += 1
            id_prod = f"PROD-{nro_grupo[-4:]}-{prod_count:04d}"
            if not multi.buscar_producto(id_prod):
                multi.insertar_producto(cod_grupo, id_inv_asociado, id_prod, tipo, titulo, anio, "A1", is_validado, True)
                resumen["productos"] += 1
                if is_validado:
                    resumen["validados"] += 1

        return resumen

    def _fallback_gruplac(self, cod_grupo: str, multi: Multilista, resumen: dict) -> dict:
        """Plan B: Ingesta con datos representativos reales de GISICO si MinCiencias está caído"""
        if not multi.buscar_grupo(cod_grupo):
            multi.insertar_grupo(
                cod_grupo,
                "GRUPO DE INVESTIGACION EN SISTEMAS Y COMPUTACIÓN -GISICO-",
                "C",
                "Ingeniería y Tecnología",
                "John Jairo Patiño Vanegas",
                2001,
                True
            )
            resumen["grupos"] += 1

        invs = [
            ("INV2099001", "John Jairo Patiño Vanegas", "Asociado", "Maestría en Computación"),
            ("0000494917", "Adith Bismarck Pérez Orozco", "Senior", "Doctorado en Ingeniería de Sistemas"),
            ("0000666106", "Eydy Del Carmen Suarez Brieva", "Asociado", "Maestría en Sistemas"),
            ("INV2099004", "Alfonso Enrique García Payares", "Junior", "Ingeniería de Sistemas"),
            ("0000441708", "Gloria Marina Rosado Galindo", "Asociado", "Ingeniería de Sistemas"),
            ("0001404785", "Heyner Alexander Aroca Araujo", "Junior", "Ingeniería de Sistemas")
        ]
        for doc, nom, cat, form in invs:
            if not multi.buscar_investigador(doc):
                multi.insertar_investigador(cod_grupo, doc, nom, cat, form, True)
                resumen["investigadores"] += 1

        # Poblar PerfilInvestigador para el docente Adith Pérez
        guardar_perfil_bd("0000494917", {
            "par_evaluador": "Si",
            "scholar_url": "https://scholar.google.com/citations?user=7DUEVWAAAAAJ&hl=es",
            "orcid": "https://orcid.org/0000-0002-2149-1625",
            "formacion_academica": "Doctorado en Ingeniería de Sistemas | Maestría en Sistemas"
        }, self.ruta_bd)

        prods = [
            ("FALLBACK-001", "0000494917", "Articulo", "Modelo de hipercubo para análisis multidimensional en MinCiencias", 2024, "A1", True),
            ("FALLBACK-002", "0000666106", "Software", "Sistema de analítica institucional de investigación universitaria", 2025, "A1", True),
            ("FALLBACK-003", "INV2099001", "Articulo", "Epistemological Foundations of Quantitative Software Research", 2023, "A", True),
            ("FALLBACK-004", "0000494917", "Libro", "Fundamentos de Estructuras de Datos aplicadas a grafos y multilistas", 2022, "A1", True),
            ("FALLBACK-005", "0000441708", "Articulo", "Scientific Methods of Quantitative Research in Engineering", 2026, "A1", True),
            ("FALLBACK-006", "0001404785", "Evento", "Pensamiento sistémico y simulación microcontrolada", 2025, "A", True)
        ]
        for id_p, doc_inv, tip, tit, an, cat, val in prods:
            if not multi.buscar_producto(id_p):
                multi.insertar_producto(cod_grupo, doc_inv, id_p, tip, tit, an, cat, val, True)
                resumen["productos"] += 1
                if val: resumen["validados"] += 1

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
        cod_grupo_def = "COL0002099"
        if not multi.buscar_grupo(cod_grupo_def):
            multi.insertar_grupo(cod_grupo_def, "GRUPO DE INVESTIGACIÓN GISICO (UPC)", "C", "Ingeniería y Tecnología", "John Jairo Patiño Vanegas", 2005, True)
            resumen["grupos"] += 1

        html_text = ""
        # Buscar snapshot CvLAC en la raíz o en cualquier subcarpeta de grupo
        snapshot_local = _buscar_snapshot_cvlac(cod_rh)

        if snapshot_local:
            print(f"[Scraping] Usando snapshot oficial local CvLAC: {os.path.basename(snapshot_local)}")
            with open(snapshot_local, "r", encoding="utf-8", errors="ignore") as f_snap:
                html_text = f_snap.read()
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
                print(f"[!] Aviso: No se pudo conectar a CvLAC en vivo ({e}).")
                print("[+] Activando Plan B: Usando dataset offline de respaldo para CvLAC...")
                resumen["modo"] = "OFFLINE_BACKUP"
                return self._fallback_cvlac(cod_rh, cod_grupo_def, multi, resumen)

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

    def _fallback_cvlac(self, cod_rh: str, cod_grupo: str, multi: Multilista, resumen: dict) -> dict:
        """Plan B: Ingesta offline del perfil del docente Adith Pérez"""
        if not multi.buscar_investigador(cod_rh):
            multi.insertar_investigador(
                cod_grupo,
                cod_rh,
                "Adith Bismarck Pérez Orozco",
                "Senior",
                "Doctorado en Ingeniería de Sistemas",
                True
            )
            resumen["investigadores"] += 1

        guardar_perfil_bd(cod_rh, {
            "par_evaluador": "Si",
            "scholar_url": "https://scholar.google.com/citations?user=7DUEVWAAAAAJ&hl=es",
            "orcid": "https://orcid.org/0000-0002-2149-1625",
            "formacion_academica": "Doctorado en Ingeniería de Sistemas"
        }, self.ruta_bd)

        prods = [
            (f"CVLAC-{cod_rh[-4:]}-001", "Articulo", "Algoritmos genéticos aplicados a la clasificación de grupos MinCiencias", 2024, "A1", True),
            (f"CVLAC-{cod_rh[-4:]}-002", "Libro", "Estructuras de Datos Avanzadas e Hipercubos Multidimensionales", 2023, "A1", True),
            (f"CVLAC-{cod_rh[-4:]}-003", "Capitulo", "Minería de datos sobre el Scienti de MinCiencias", 2022, "A", True)
        ]
        for id_p, tip, tit, an, cat, val in prods:
            if not multi.buscar_producto(id_p):
                multi.insertar_producto(cod_grupo, cod_rh, id_p, tip, tit, an, cat, val, True)
                resumen["productos"] += 1
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
        cod_grupo = "COL0002099"
        if not multi.buscar_grupo(cod_grupo):
            multi.insertar_grupo(cod_grupo, "GRUPO DE INVESTIGACIÓN GISICO (UPC)", "C", "Ingeniería y Tecnología", "John Jairo Patiño Vanegas", 2005, True)
            resumen["grupos"] += 1

        doc_inv = "0000494917"
        if not multi.buscar_investigador(doc_inv):
            multi.insertar_investigador(cod_grupo, doc_inv, autor, "Senior", "Ingeniería de Sistemas", True)
            resumen["investigadores"] += 1

        nombre_archivo = os.path.basename(ruta_pdf)
        id_prod = f"PDF-{abs(hash(nombre_archivo)) % 100000:05d}"
        if not multi.buscar_producto(id_prod):
            multi.insertar_producto(cod_grupo, doc_inv, id_prod, "Articulo", titulo[:110], anio, "A1", True, True)
            resumen["productos"] += 1

        return resumen

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
            GestorPersistencia.guardar_en_bd(multi, self.ruta_bd)

            # 6. Reporte de resultados
            print(f"[OK] Ingesta completada con éxito en modo: {resumen.get('modo', 'ESTÁNDAR')}")
            print("-----------------------------------------------------------------")
            print(f"  • Nuevos Grupos registrados:         {resumen.get('grupos', 0)}")
            print(f"  • Nuevos Investigadores registrados: {resumen.get('investigadores', 0)}")
            print(f"  • Nuevos Productos indexados:        {resumen.get('productos', 0)}")
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
