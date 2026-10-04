# UNIVERSIDAD POPULAR DEL CESAR (UPC) — Estructura de Datos 2026-I
# PEA-i — Entregable Python (archivo unico) — Fase 3 Ingesta masiva
# Modos: (1) consola (pendiente Fase 2) | (2) --gui (pendiente Fase 5)
#        (3) --scrape-url/--scrape-grupo/--scrape-todos | (4) --ingesta-archivo | --offline
# Regla punto 7: solo columnas del esquema; resto se descarta y reporta.
import os
import sys
import re
import csv
import json
import sqlite3
import argparse
import unicodedata
from urllib.parse import urlencode

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE, "pylib"))
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup

DB_DEF = os.path.join(BASE, "data", "pea_investigacion.db")
SNAP_DIR = os.path.join(BASE, "data", "snapshots")
GRUPOS_DEF = os.path.join(BASE, "data", "grupos_upc.txt")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) PEA-i-UPC/1.0"}

# Columnas canonicas del sistema (schema.sql). Todo lo demas se descarta.
GRUPO_COLS = ["codigo_grupo", "nombre", "lider", "plan_investigacion", "lineas_estrategicas"]
INV_COLS = ["cod_rh", "nombre_completo", "correo", "categoria_minciencias", "cvlac_url"]
PROD_COLS = ["titulo", "tipo_producto", "categoria", "estado_validacion", "anio_publicacion"]


def normalizar_clave(s):
    s = unicodedata.normalize("NFD", (s or "").lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^a-z0-9]+", "_", s).strip("_")
    return s


def codificacion_respuesta(r):
    """Charset declarado por el servidor (SCIENTI: iso-8859-1).
    JAMAS utf-8 forzado: rompia tildes en � (S30)."""
    ct = (r.headers.get("Content-Type") or "").lower()
    m = re.search(r"charset=([\w-]+)", ct)
    enc = (m.group(1) if m else "") or r.apparent_encoding or "utf-8"
    if enc.replace("_", "-") in ("iso-8859-1", "latin-1", "latin1"):
        enc = "windows-1252"
    return enc


def sin_raros(s):
    """Quita � residuales para comparaciones (nunca para guardar)."""
    return (s or "").replace("�", "")


# Alias POR ENTIDAD (sin colisiones: "nombre" solo = persona, "categoria" se resuelve por contexto).
ALIASES_GRUPO = {
    "codigo_grupo": {"codigo_grupo", "codigo", "cod_grupo", "nro_grupo", "codigo_colciencias"},
    "nombre": {"nombre_grupo", "grupo"},
    "lider": {"lider", "lider_grupo", "investigador_principal", "responsable", "director"},
    "plan_investigacion": {"plan_investigacion", "plan", "plan_de_trabajo", "plan_estrategico"},
    "lineas_estrategicas": {"lineas_estrategicas", "lineas", "lineas_de_investigacion"},
}
ALIASES_INV = {
    "cod_rh": {"cod_rh", "rh", "codigo_rh"},
    "nombre_completo": {"nombre_completo", "nombre", "nombre_investigador", "integrante"},
    "correo": {"correo", "correo_investigador", "email", "e_mail"},
    "categoria_minciencias": {"categoria_minciencias", "categoria", "clasificacion"},
    "cvlac_url": {"cvlac_url", "cvlac", "url_cvlac"},
}
ALIASES_PROD = {
    "titulo": {"titulo", "titulo_producto", "nombre_producto"},
    "tipo_producto": {"tipo_producto", "tipo"},
    "categoria": {"categoria", "categoria_producto"},
    "estado_validacion": {"estado_validacion", "validacion", "aval"},
    "anio_publicacion": {"anio_publicacion", "anio", "ano", "year"},
}


def _mapa(aliases):
    m = {}
    for canon, variantes in aliases.items():
        for v in variantes:
            m.setdefault(v, canon)
    return m


MAPAS = {"grupo": _mapa(ALIASES_GRUPO), "investigador": _mapa(ALIASES_INV),
         "producto": _mapa(ALIASES_PROD)}


def proyectar(fila_origen, entidad):
    """Devuelve (usadas, descartadas). Solo columnas canonicas de esa entidad."""
    mapa = MAPAS[entidad]
    norm = {normalizar_clave(k): v for k, v in fila_origen.items()}
    usadas, descartadas = {}, []
    for k, v in norm.items():
        canon = mapa.get(k)
        if canon and canon not in usadas:
            usadas[canon] = (v or "").strip()
        else:
            descartadas.append(k)
    return usadas, descartadas


# ---------------- SQLite ----------------
CACHE_DDL = ("CREATE TABLE IF NOT EXISTS cache_fuentes (url TEXT PRIMARY KEY,"
             " sha256 VARCHAR(64) NOT NULL, etag TEXT DEFAULT '',"
             " last_modified TEXT DEFAULT '', fecha DATETIME DEFAULT CURRENT_TIMESTAMP,"
             " ruta TEXT DEFAULT '');")


PERFILES_DDL = ("CREATE TABLE IF NOT EXISTS perfiles_grupo (codigo_grupo VARCHAR(50) NOT NULL,"
                " convocatoria VARCHAR(20) NOT NULL, seccion VARCHAR(120) NOT NULL,"
                " subtipo VARCHAR(200) NOT NULL, abreviatura VARCHAR(20) DEFAULT '',"
                " valor_grupo VARCHAR(50) DEFAULT '', cuartil_grupo VARCHAR(10) DEFAULT '',"
                " PRIMARY KEY (codigo_grupo, convocatoria, seccion, subtipo),"
                " FOREIGN KEY (codigo_grupo) REFERENCES Grupos(codigo_grupo) ON DELETE CASCADE);")


# S37: hoja de vida CvLAC por integrante (1:1 con Investigadores; FK en cascada).
HV_DDL = ("CREATE TABLE IF NOT EXISTS perfil_investigador (cod_rh VARCHAR(50) PRIMARY KEY,"
          " par_evaluador VARCHAR(10) DEFAULT '', nombre_citaciones VARCHAR(255) DEFAULT '',"
          " nacionalidad VARCHAR(100) DEFAULT '', sexo VARCHAR(20) DEFAULT '',"
          " scholar_url TEXT DEFAULT '', orcid VARCHAR(100) DEFAULT '',"
          " formacion_academica TEXT DEFAULT '', formacion_complementaria TEXT DEFAULT '',"
          " experiencia TEXT DEFAULT '', areas TEXT DEFAULT '', idiomas VARCHAR(600) DEFAULT '',"
          " FOREIGN KEY (cod_rh) REFERENCES Investigadores(cod_rh) ON DELETE CASCADE);")


def conectar(db):
    conn = sqlite3.connect(db)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout=5000;")
    conn.execute("PRAGMA foreign_keys=ON;")
    conn.execute(CACHE_DDL)
    conn.execute(PERFILES_DDL)
    conn.execute(HV_DDL)
    return conn


def descargar_cache(url, nombre_local, db):
    """Capa de cache oficial (S19): valida ETag/304 si el servidor los da;
    si no (SCIENTI hoy), compara hash: mismo sha256 = sin cambios ni duplicados.
    Devuelve (estado, html_or_ruta): nuevo | sin_cambios | duplicado."""
    import hashlib
    import datetime
    conn = conectar(db)
    row = conn.execute("SELECT sha256, etag, last_modified, ruta FROM cache_fuentes WHERE url=?;",
                       (url,)).fetchone()
    headers = dict(UA)
    if row:
        if row[1]:
            headers["If-None-Match"] = row[1]
        if row[2]:
            headers["If-Modified-Since"] = row[2]
    r = sesion_http().get(url, headers=headers, timeout=10)
    if r.status_code == 304 and row:
        conn.execute("UPDATE cache_fuentes SET fecha=? WHERE url=?;",
                     (datetime.datetime.now().isoformat(timespec="seconds"), url))
        conn.commit()
        conn.close()
        with open(row[3], encoding="utf-8", errors="replace") as f:
            return "sin_cambios", f.read()
    r.encoding = codificacion_respuesta(r)
    if r.status_code != 200:
        conn.close()
        return "error_%s" % r.status_code, ""
    digest = hashlib.sha256(r.content).hexdigest()
    if row and row[0] == digest:
        conn.execute("UPDATE cache_fuentes SET fecha=? WHERE url=?;",
                     (datetime.datetime.now().isoformat(timespec="seconds"), url))
        conn.commit()
        conn.close()
        return "sin_cambios", r.text
    dup = conn.execute("SELECT ruta FROM cache_fuentes WHERE sha256=? AND ruta<>'';",
                       (digest,)).fetchone()
    os.makedirs(SNAP_DIR, exist_ok=True)
    if dup and os.path.exists(dup[0]):
        conn.execute("REPLACE INTO cache_fuentes (url, sha256, etag, last_modified, fecha, ruta)"
                     " VALUES (?,?,?,?,?,?);",
                     (url, digest, r.headers.get("ETag", ""), r.headers.get("Last-Modified", ""),
                      datetime.datetime.now().isoformat(timespec="seconds"), dup[0]))
        conn.commit()
        conn.close()
        with open(dup[0], encoding="utf-8", errors="replace") as f:
            return "duplicado", f.read()
    destino = os.path.join(SNAP_DIR, nombre_local)
    with open(destino, "w", encoding="utf-8") as f:
        f.write(r.text)
    conn.execute("REPLACE INTO cache_fuentes (url, sha256, etag, last_modified, fecha, ruta)"
                 " VALUES (?,?,?,?,?,?);",
                 (url, digest, r.headers.get("ETag", ""), r.headers.get("Last-Modified", ""),
                  datetime.datetime.now().isoformat(timespec="seconds"), destino))
    conn.commit()
    conn.close()
    return "nuevo", r.text


def empaquetar_grupo(codigo, nro="", reutilizar=True):
    """Un zip por grupo con sus snapshots (S19: 66 zips, no 4.620 html).
    S32: si el zip vigente ya existe y es mas nuevo que sus fuentes, se
    reutiliza (no se reescribe ni se duplica)."""
    import zipfile
    import glob
    os.makedirs(os.path.join(SNAP_DIR, "zip"), exist_ok=True)
    dest = os.path.join(SNAP_DIR, "zip", "grupo_%s.zip" % codigo)
    claves = [codigo.lower()]
    if nro:
        claves.append(nro)
        claves.append(nro[-4:])
    files = [f for f in glob.glob(os.path.join(SNAP_DIR, "*.html"))
             if any(k in os.path.basename(f).lower() for k in claves)]
    if not files:
        # Sin fuentes propias: reutilizar el vigente si ya existe (idempotencia).
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


# Mapa de códigos legacy (sigla/G+nro) -> CCRG/COL vigente (S28 + S32).
# Evita zips huérfanos: el zip se nombra por código y el código cambió.
CODIGOS_LEGACY = {"GISICO": "COL0018706", "G002668": "COL0043834", "G003639": "COL0001351",
                  "G0002099": "COL0018706", "G002099": "COL0018706"}


def limpiar_zips_huerfanos():
    """Borra zips legacy cuyo COL vigente ya existe (S32: GISICO->COL0018706...).
    Devuelve lista de eliminados."""
    eliminados = []
    zipdir = os.path.join(SNAP_DIR, "zip")
    for viejo, nuevo in CODIGOS_LEGACY.items():
        fv = os.path.join(zipdir, "grupo_%s.zip" % viejo)
        fn = os.path.join(zipdir, "grupo_%s.zip" % nuevo)
        if os.path.exists(fv) and os.path.exists(fn):
            try:
                os.remove(fv)
                eliminados.append(os.path.basename(fv))
            except OSError as e:
                print("aviso zip %s: %s" % (fv, e))
    if eliminados:
        print("zips huerfanos eliminados: %s" % ", ".join(eliminados))
    return eliminados


def _snapshot_para_nro(nro):
    """Snapshot GrupLAC local para un nro (sin red)."""
    if not os.path.isdir(SNAP_DIR):
        return ""
    exacto = os.path.join(SNAP_DIR, "gruplac_%s.html" % nro)
    if os.path.exists(exacto):
        return exacto
    cands = [f for f in os.listdir(SNAP_DIR) if nro in f and f.endswith(".html")]
    if not cands:
        cands = [f for f in os.listdir(SNAP_DIR)
                 if f.endswith(".html") and nro[-4:] in f
                 and os.path.basename(f).startswith("gruplac")]
    if cands:
        return os.path.join(SNAP_DIR, sorted(cands)[0])
    return ""


def existe_grupo_en_bd(nro, db):
    """Chequeo offline (sin red): ¿el nro ya está cargado en la BD?
    Devuelve (codigo_vigente, nombre) o (None, None).
    Orden: 1) índice JSON nro->código, 2) ficha snapshot parseada vs Grupos."""
    conn = conectar(db)
    try:
        # 1) índice de grupos (nro -> ccrg) si existe
        idx = os.path.join(BASE, "data", "indice_grupos.json")
        if os.path.exists(idx):
            try:
                d = json.load(open(idx, encoding="utf-8"))
                grupos_idx = d if isinstance(d, list) else d.get("grupos", d)
                items = grupos_idx if isinstance(grupos_idx, list) else []
                for g in items:
                    if not isinstance(g, dict):
                        continue
                    nro_g = str(g.get("nro", ""))
                    if nro_g and (nro_g == nro or nro_g.endswith(nro[-6:])):
                        cod = g.get("ccrg") or g.get("codigo") or ""
                        if cod and conn.execute(
                                "SELECT 1 FROM Grupos WHERE codigo_grupo=?;", (cod,)).fetchone():
                            fila = conn.execute(
                                "SELECT codigo_grupo, nombre FROM Grupos WHERE codigo_grupo=?;",
                                (cod,)).fetchone()
                            return fila[0], fila[1]
            except Exception:
                pass
        # 2) snapshot local -> nombre -> Grupos (tolerante a �, S30)
        snap = _snapshot_para_nro(nro)
        if snap and os.path.exists(snap):
            with open(snap, encoding="utf-8", errors="replace") as f:
                ficha = parse_ficha(f.read())
            if ficha.get("nombre"):
                objetivo = sin_raros(_norm_txt(ficha["nombre"]))
                for cg, nm in conn.execute("SELECT codigo_grupo, nombre FROM Grupos;"):
                    if sin_raros(_norm_txt(nm)) == objetivo:
                        return cg, nm
    finally:
        conn.close()
    return None, None


def guardar_grupo(conn, g):
    if not g.get("codigo_grupo") or not g.get("nombre") or not g.get("lider"):
        return ("descartada", "sin PK/NOT NULL")
    cur = conn.execute(
        "INSERT OR IGNORE INTO Grupos (codigo_grupo, nombre, lider, plan_investigacion, lineas_estrategicas, estado)"
        " VALUES (?,?,?,?,?,1);",
        (g["codigo_grupo"], g["nombre"], g["lider"],
         g.get("plan_investigacion", ""), g.get("lineas_estrategicas", "")))
    return ("ok" if cur.rowcount > 0 else "existente", "")


def siguiente_rh(conn, cod_grupo):
    n = conn.execute(
        "SELECT COUNT(*) FROM Investigadores WHERE cod_rh LIKE ?;",
        (cod_grupo + "-RH-%",)).fetchone()[0]
    return "%s-RH-%03d" % (cod_grupo, n + 1)


def guardar_investigador(conn, cod_grupo, inv):
    if not inv.get("nombre_completo"):
        return ("descartado", "sin nombre", "")
    rh = inv.get("cod_rh", "")
    if not rh:
        rh = siguiente_rh(conn, cod_grupo)  # placeholder documentado (GrupLAC no publica cod_rh)
    cur = conn.execute(
        "INSERT OR IGNORE INTO Investigadores (cod_rh, nombre_completo, correo, categoria_minciencias, cvlac_url, estado)"
        " VALUES (?,?,?,?,?,1);",
        (rh, inv["nombre_completo"], inv.get("correo", ""),
         inv.get("categoria_minciencias", "") or "Por verificar", inv.get("cvlac_url", "")))
    conn.execute(
        "INSERT OR IGNORE INTO grupo_investigador (codigo_grupo_fk, cod_rh_fk) VALUES (?,?);",
        (cod_grupo, rh))
    return ("ok" if cur.rowcount > 0 else "existente", "", rh)


def guardar_producto(conn, cod_grupo, rh, p):
    if not p.get("titulo") or not p.get("anio_publicacion"):
        return "descartado"
    try:
        anio = int(str(p["anio_publicacion"])[:4])
    except ValueError:
        return "descartado"
    if not 1900 <= anio <= 2026:
        return "descartado"
    ya = conn.execute(
        "SELECT id_producto, estado_validacion FROM Productos WHERE titulo=? AND anio_publicacion=? AND codigo_grupo_fk=? AND cod_rh_investigador_fk=?;",
        (p["titulo"], anio, cod_grupo, rh)).fetchone()
    if ya:
        # S36: el re-scrape actualiza el aval (Pendiente -> Validado por chulito).
        if ya[1] == "Pendiente" and (p.get("estado_validacion") or "") == "Validado":
            conn.execute("UPDATE Productos SET estado_validacion='Validado' WHERE id_producto=?;",
                         (ya[0],))
            return "actualizado"
        return "existente"
    # El PDF trunca titulos al ancho de columna: mismo articulo, distinto largo.
    # Se comparan anio + autor + 30 primeros caracteres normalizados.
    pref = re.sub(r"\s+", " ", p["titulo"][:30]).strip()
    if len(pref) >= 15:
        ya2 = conn.execute(
            "SELECT id_producto, estado_validacion FROM Productos WHERE anio_publicacion=? AND cod_rh_investigador_fk=?"
            " AND substr(titulo,1,30)=?;",
            (anio, rh, p["titulo"][:30])).fetchone()
        if ya2:
            if ya2[1] == "Pendiente" and (p.get("estado_validacion") or "") == "Validado":
                conn.execute("UPDATE Productos SET estado_validacion='Validado' WHERE id_producto=?;",
                             (ya2[0],))
                return "actualizado"
            return "existente"
    conn.execute(
        "INSERT INTO Productos (titulo, tipo_producto, categoria, estado_validacion, anio_publicacion,"
        " codigo_grupo_fk, cod_rh_investigador_fk, estado) VALUES (?,?,?,?,?,?,?,1);",
        (p["titulo"], p.get("tipo_producto", "") or "Artículo",
         p.get("categoria", "") or "Por verificar",
         p.get("estado_validacion", "") or "Pendiente",
         anio, cod_grupo, rh))
    return "ok"


# ---------------- HTTP ----------------
def sesion_http():
    s = requests.Session()
    s.mount("https://", HTTPAdapter(max_retries=Retry(total=3, backoff_factor=1,
                                                       status_forcelist=[500, 502, 503, 504])))
    s.mount("http://", HTTPAdapter(max_retries=Retry(total=3, backoff_factor=1)))
    return s


# ---------------- Parsers GrupLAC ----------------
def parse_ficha(html):
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text("\n")
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    def bloque(a, b):
        i0, i1 = text.find(a), text.find(b)
        if 0 <= i0 < i1:
            return " ".join(text[i0 + len(a):i1].split())
        return ""

    # Existe = pagina real de grupo (seccion "Datos basicos"); si no, nro invalido.
    existe = any(l.startswith("Datos b") for l in lines)
    # Nombre = primera linea de contenido (tras el <title>); lider = linea tras "Lider".
    nombre, lider = "", ""
    for i, l in enumerate(lines):
        if l.startswith("GrupLAC -"):
            if i + 1 < len(lines):
                nombre = lines[i + 1]
            break
    for i, l in enumerate(lines):
        if l in ("Lider", "Líder") or l.startswith("L") and l.replace("\ufffd", "") == "Lder":
            if i + 1 < len(lines):
                lider = lines[i + 1]
            break
    # Instituciones: "N.- NOMBRE - (Avalado|No Avalado)" hasta "Plan Estra..."
    instituciones = []
    en_inst = False
    for l in lines:
        if l.startswith("Institu"):
            en_inst = True
            continue
        if en_inst:
            if l.startswith("Plan Estra"):
                break
            m = re.match(r"\d+\.-\s*(.+?)\s*-\s*\((Avalado|No Avalado)\)", l)
            if m:
                instituciones.append({"nombre": m.group(1).strip(), "aval": m.group(2)})
    m = re.search(r"[\w\.-]+@[\w\.-]+", text)
    mc = re.search(r"Clasificaci.n\s+([A-C1]+)", text)
    lineas = []
    i0 = text.find("declaradas por el grupo")
    if i0 > 0:
        seg = text[i0:text.find("Integrantes del grupo", i0)]
        lineas = [l.strip() for l in re.findall(r"\d+\.-\s*([A-Z\xc0-\xde][A-Z\xc0-\xde /]+)", seg)]
    sigla = ""
    ms = re.search(r"-([A-Z]{2,12})-\s*$", nombre)
    if ms:
        sigla = ms.group(1)
    return {
        "existe": existe,
        "nombre": nombre,
        "sigla": sigla,
        "lider": lider,
        "instituciones": instituciones,
        "plan_investigacion": bloque("Plan de trabajo:", "Estado del arte:")[:1200],
        "lineas_estrategicas": "; ".join(lineas),
        "email": m.group(0) if m else "",
        "categoria": mc.group(1) if mc else "",
    }


def parse_integrantes(html):
    soup = BeautifulSoup(html, "html.parser")
    out = []
    vistos = set()
    vistos = set()
    for t in soup.find_all("table"):
        th = " ".join(t.get_text(" ").split())
        if "Vinculaci" in th and "Nombre" in th and "Horas" in th:
            for tr in t.find_all("tr")[1:]:
                tds = [c.get_text(" ").strip() for c in tr.find_all(["td", "th"])]
                tds = [d for d in tds if d]
                if len(tds) >= 4 and tds[0] != "Nombre":
                    nom = re.sub(r"^\d+\.-\s*", "", tds[0]).strip()
                    # cod_rh ORIGINAL del href CvLAC (nunca inventado)
                    rh = ""
                    a = tr.find("a", href=True)
                    if a:
                        m = re.search(r"cod_rh=(\d+)", a.get("href", ""))
                        if m:
                            rh = m.group(1)
                    if nom and nom not in vistos:
                        vistos.add(nom)
                        out.append({"nombre_completo": nom, "periodo": tds[3], "cod_rh": rh})
    return out


def tipo_por_marcador(mk, seccion=""):
    """Clasifica por prefijos robustos al � (tildes rotas de SCIENTI).
    S35: 15 tipos propios; `seccion` resuelve ambiguos (Otro/Jurado/Maestria)."""
    m = mk.replace("_", " ")
    # --- Núcleo bibliográfico (S28, intacto) ---
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
    # --- Ampliación S35: resto de la ficha ---
    if m.startswith("revision") or "survey" in m:
        return "Articulo"
    if m.startswith("libros de divulgaci") or "compilacion de divulgaci" in m:
        return "Libro"
    if m.startswith("informe tecnico") or m == "informe":
        return "Informe"
    if "consultor" in m:
        return "Consultoria"
    if (m.startswith("encuentro") or m.startswith("congreso") or m.startswith("simposio")
            or m.startswith("seminario") or m.startswith("foro")
            or m == "taller"):
        # Taller/Seminario en Formación son cursos, no eventos.
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
        return "Compilacion"
    if m.startswith("regulacion") or m.startswith("norma"):
        return "Regulacion"
    if seccion == "evaluador":
        return "Jurado"  # todo acto en esa sección es evaluación
    return ""
TIPOS_OMITIDOS = {"diseno industrial", "spin-off", "consultor", "informes de investigacion",
                  "congreso", "encuentro", "seminario", "taller", "simposio", "pagina web",
                  "micrositio", "trabajos de grado", "trabajo de grado", "iniciacion cientifica",
                  "perfeccionamiento", "maestria", "pregrado", "especializacion",
                  "profesor titular", "demas trabajos", "corto (resumen)",
                  "investigacion, desarrollo e innovacion", "investigacion y desarrollo"}


def _norm_txt(s):
    s = unicodedata.normalize("NFD", (s or "").lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", s).strip()


# Secciones de producción de la ficha GrupLAC (S35: el parser es consciente
# de sección para resolver marcadores ambiguos como "Otro:" o "Taller:").
# Patrones sobre texto crudo, tolerantes a tildes rotas (�) de SCIENTI.
SECCIONES_FICHA = (
    ("biblio", r"PRODUCCI.N\s+BIBLIOGR.FICA"),
    ("tecnica", r"PRODUCCI.N\s+T.CNICA"),
    ("apropiacion", r"APROPIACI.N\s+SOCIAL"),
    ("formacion", r"ACTIVIDADES\s+DE\s+FORMACI.N|PRODUCCI.N\s+DE\s+FORMACI.N"),
    ("evaluador", r"COMO\s+EVALUADOR"),
)


def _spans_secciones(texto):
    spans = []
    for key, pat in SECCIONES_FICHA:
        for m in re.finditer(pat, texto, flags=re.IGNORECASE):
            spans.append([key, m.start(), len(texto)])
    spans.sort(key=lambda s: s[1])
    for i in range(len(spans) - 1):
        spans[i][2] = spans[i + 1][1]
    return spans


def seccion_de(pos, spans):
    sec = ""
    for key, ini, fin in spans:
        if ini <= pos < fin:
            sec = key
    return sec


def _titulo_bloque(bloque, mk):
    """Título del bloque: entrecomillado o primera línea con contenido real
    (nunca la línea del marcador `N. Marcador:`)."""
    mt = re.search(r'"([^"]{8,480})"', bloque)
    if not mt:
        blines = [l.strip() for l in bloque.split("\n") if l.strip()]
        for bl in blines:
            if len(bl) < 8 or re.match(r"^\d+\.-?\s*$", bl):
                continue
            core = re.sub(r"^\d+\.\-?\s*", "", bl).strip().rstrip(":").strip()
            if not core or _norm_txt(core) == mk:
                continue  # línea del marcador, no título
            mt = re.match(r"(.{8,480})", bl)
            break
    titulo = mt.group(1).strip() if mt else ""
    return titulo.lstrip(":;,.—- ").strip()


def _anio_bloque(bloque):
    """Año del bloque: `, AAAA`, luego `desde AAAA`, luego año suelto
    fuera de líneas ISSN/DOI/vol. 0 si no hay."""
    ma = re.search(r",\s*((?:19|20)\d{2})\b", bloque)
    anio = int(ma.group(1)) if ma and 1900 <= int(ma.group(1)) <= 2026 else 0
    if not anio:
        # Eventos/Tesis/Consultorías fechan con "desde ..." (sin ", AAAA").
        md = re.search(r"[Dd]esde\D{0,14}((?:19|20)\d{2})\b", bloque)
        if not md:
            # Último recurso: primer año suelto fuera de líneas ISSN/DOI/vol.
            for _bl in bloque.split("\n"):
                if re.search(r"ISSN|DOI|vol|fasc|p.g", _bl, flags=re.IGNORECASE):
                    continue
                md = re.search(r"\b((?:19|20)\d{2})\b", _bl)
                if md:
                    break
        if md and 1900 <= int(md.group(1)) <= 2026:
            anio = int(md.group(1))
    return anio


def mapa_chulos(soup):
    """S36: chulito GrupLAC (`chulo_1.jpg` = avalado/validado convocatoria,
    `chulo_0.jpg` = no). La img va en el <td> previo al ítem, mismo <tr>.
    Retorna {(marcador_norm, titulo_norm[:60], anio): validado_bool}."""
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


# S37: títulos que son solo el marcador (basura histórica, ej. ids 31-50).
# El _titulo_bloque ya los evita; esta red los rechaza si alguno se cuela.
def _es_titulo_marcador(titulo, mk):
    n = _norm_txt(titulo)
    if not n or n == mk:
        return True
    return n in {"revision survey", "otra", "otro"}


def parse_produccion_grupolac(html):
    """Extrae productos de la ficha GrupLAC: [{titulo, anio, tipo, autores[], validacion}].
    S35: cubre las 6 secciones (biblio/tecnica/apropiacion/formacion/evaluador);
    formatos `N.- X:` y `N. X:`; solo tipos del whitelist, el resto se cuenta
    como omitido (reporte, no se guarda).
    S36: `validacion` del chulito (`chulo_1.jpg` = Validado, si no Pendiente)."""
    soup = BeautifulSoup(html, "html.parser")
    texto = soup.get_text("\n")
    chulos = mapa_chulos(soup)
    spans = _spans_secciones(texto)
    marcas = [(m.start(), m.group(1).strip()) for m in
              re.finditer(r"\d+\.\-?\s*([^\n:]{3,60})\s*:", texto)]
    marcas.append((len(texto), ""))
    prods, omitidos = [], 0
    for idx in range(len(marcas) - 1):
        inicio, marcador_raw = marcas[idx]
        bloque = texto[inicio:marcas[idx + 1][0]]
        mk = _norm_txt(marcador_raw)
        sec = seccion_de(inicio, spans)
        tipo = tipo_por_marcador(mk, sec)
        if not tipo:
            # ¿marcador ambiguo "Otra"/"Otro" con contenido de software?
            if mk in ("otra", "otro") and any(
                    k in _norm_txt(bloque[:400]) for k in
                    ("disponibilidad", "nombre comercial", "financiadora", "sitio web")):
                tipo = "Software"
            elif mk in ("otra", "otro") and sec == "apropiacion":
                tipo = "Evento"
            else:
                omitidos += 1
                continue
        mt = _titulo_bloque(bloque, mk)
        mt = _titulo_bloque(bloque, mk)
        maut = re.search(r"Autores:\s*([^\n]+(?:\n[^\n:]+)?)", bloque)
        if not maut:
            # Tesis/Eventos/Jurados no traen "Autores:": Estudiante/Director/etc.
            # Misma regla (solo integrantes macheados, sin inventar).
            maut = re.search(
                r"(?:Tutor\(es\)/Cotutor\(es\)|Tutores?/Cotutores?|Estudiante|Director|"
                r"Tutor|Asesor|Orientador|Organizador|Ponente|Responsable|Compilador|"
                r"Consultor)[es]*\s*:\s*([^\n]+(?:\n[^\n:]+)?)",
                bloque)
        titulo = mt  # _titulo_bloque ya devuelve limpio
        if _es_titulo_marcador(titulo, mk):
            omitidos += 1  # marcador sin producto real (basura S37)
            continue
        if re.match(r"^[A-Za-záéíóúñü]+\s*,\s*(?:19|20)\d{2}\s*,?$", titulo):
            omitidos += 1  # resto pais-anio sin titulo real (basura del parseo)
            continue
        anio = _anio_bloque(bloque)
        autores = []
        if maut:
            autores = [a.strip().rstrip(".") for a in re.split(r",", maut.group(1)) if a.strip()]
        if titulo and anio:
            validado = chulos.get((mk, _norm_txt(titulo)[:60], anio), False)
            prods.append({"titulo": titulo, "anio": anio, "tipo": tipo,
                          "autores": autores,
                          "validacion": "Validado" if validado else "Pendiente"})
        else:
            omitidos += 1
    return prods, omitidos


def mapa_autores(conn):
    """nombre normalizado -> cod_rh (para atribuir autoria sin inventar)."""
    m = {}
    for rh, nom in conn.execute("SELECT cod_rh, nombre_completo FROM Investigadores;"):
        m[_norm_txt(nom)] = rh
    return m


def scrape_grupo(nro, db, usar_snapshot=True, universidad="", forzar=False, con_cvlac=True):
    """Verifica existencia (Grupo no existente) y filtra por universidad
    (universidad no encontrada). Sin filtro, informa las avaladoras y sigue.
    S32: si el nro ya está cargado (offline) y no se pasa forzar, informa
    "grupo ya existente" y retorna sin red ni zip nuevo (idempotencia).
    S37: con_cvlac descarga la hoja de vida CvLAC de cada integrante."""
    # Pre-chequeo offline de duplicado (sin red): evita 2.º zip (S32).
    if not forzar:
        cod_ex, nom_ex = existe_grupo_en_bd(nro, db)
        if cod_ex:
            z_ex = os.path.join(SNAP_DIR, "zip", "grupo_%s.zip" % cod_ex)
            if not os.path.exists(z_ex):
                z_ex = empaquetar_grupo(cod_ex, nro)
            print("[AVISO] grupo ya existente | CODIGO=%s | GRUPO=%s | ZIP=%s"
                  % (cod_ex, (nom_ex or "")[:60], z_ex if z_ex else "n/a"))
            print("No se descargo nada nuevo ni se duplico informacion."
                  " Use --forzar para re-scrapear desde SCIENTI.")
            return {"grupo": "existente", "integrantes": 0, "productos": 0}
    os.makedirs(SNAP_DIR, exist_ok=True)
    url = ("https://scienti.minciencias.gov.co/gruplac/jsp/visualiza/"
           "visualizagr.jsp?nro=%s" % nro)
    html = None
    if usar_snapshot:
        snap = os.path.join(SNAP_DIR, "gruplac_%s.html" % nro)
        if not os.path.exists(snap):  # tolera nombres tipo gruplac_gisico_2099.html
            cands = [f for f in os.listdir(SNAP_DIR) if nro in f and f.endswith(".html")]
            if not cands:
                cands = [f for f in os.listdir(SNAP_DIR)
                         if f.endswith(".html") and nro[-4:] in f]
            if cands:
                snap = os.path.join(SNAP_DIR, sorted(cands)[0])
        if os.path.exists(snap):
            with open(snap, encoding="utf-8", errors="replace") as f:
                html = f.read()
            origen = "snapshot"
    if html is None:
        origen, html = descargar_cache(url, "gruplac_%s.html" % nro, db)
        if origen.startswith("error"):
            print("ERROR scrape %s %s" % (nro, origen))
            return None
    ficha = parse_ficha(html)
    if not ficha["existe"] or not ficha["nombre"]:
        print("Grupo no existente (nro=%s): GrupLAC no devuelve ficha de grupo." % nro)
        return None
    avaladoras = ["%s (%s)" % (i["nombre"], i["aval"]) for i in ficha["instituciones"]]
    if universidad:
        q = normalizar_clave(universidad).replace("_", " ")
        ok = any(q in normalizar_clave(i["nombre"]).replace("_", " ")
                 for i in ficha["instituciones"])
        if not ok:
            quienes = "; ".join(avaladoras) if avaladoras else "nadie"
            print("Universidad no encontrada para este grupo (avalan: %s)." % quienes)
            return None
    integrantes = parse_integrantes(html)
    # CCRG via verPerfiles: el codigo original manda (si falla, sigla o G+nro)
    basicos_vp, perfiles_vp = {}, []
    try:
        vurl = ("https://scienti.minciencias.gov.co/gruplac/jsp/Medicion/graficas/"
                "verPerfiles.jsp?id_convocatoria=22&nroIdGrupo=%s" % nro)
        vorig, vhtml = descargar_cache(vurl, "verperfiles_%s.html" % nro, db)
        if vhtml and not vorig.startswith("error"):
            basicos_vp, perfiles_vp = parse_verperfiles(vhtml)
    except Exception as e:
        print("aviso verPerfiles %s: %s" % (nro, e))
    codigo = (basicos_vp.get("ccrg") or ficha["sigla"] or ("G" + nro[-6:])) if basicos_vp else (ficha["sigla"] or ("G" + nro[-6:]))
    conn = conectar(db)
    # Si el grupo ya existe (p.ej. migrado a CCRG/COL), se reutiliza su codigo vigente.
    # Comparacion tolerante a �: limpia ambos lados (S30).
    fila_ex = None
    if ficha["nombre"]:
        objetivo = sin_raros(_norm_txt(ficha["nombre"]))
        for cg, nm in conn.execute("SELECT codigo_grupo, nombre FROM Grupos;"):
            if sin_raros(_norm_txt(nm)) == objetivo:
                fila_ex = (cg,)
                break
    if fila_ex:
        codigo = fila_ex[0]
    g = {"codigo_grupo": codigo, "nombre": ficha["nombre"], "lider": ficha.get("lider", "") or "Por verificar",
         "plan_investigacion": ficha.get("plan_investigacion", ""),
         "lineas_estrategicas": ficha.get("lineas_estrategicas", "")}
    est, _ = guardar_grupo(conn, g)
    n_inv = n_hist = n_desc = 0
    rhs_grupo = []
    for inv in integrantes:
        es_actual = "Actual" in inv.get("periodo", "")
        if not es_actual:
            n_hist += 1  # se informa pero IGUAL se importa (grupo completo)
        u, d = proyectar({"nombre": inv["nombre_completo"],
                          "cod_rh": inv.get("cod_rh", "")}, "investigador")
        est_i, _, rh = guardar_investigador(conn, codigo, u)
        if est_i in ("ok", "existente"):
            n_inv += 1
            if rh and rh not in rhs_grupo:
                rhs_grupo.append(rh)
        else:
            n_desc += 1
    conn.commit()  # soltar escrituras antes de los CvLAC (otra conexión por rh)
    # Produccion del grupo: solo tipos whitelist, solo autores macheados (sin inventar autoria)
    prods, omit = parse_produccion_grupolac(html)
    mapa = mapa_autores(conn)
    n_prod = n_sin_autor = n_val = 0
    for p in prods:
        rhs = [mapa[a] for a in (_norm_txt(x) for x in p["autores"]) if a in mapa]
        if not rhs:
            n_sin_autor += 1
            continue
        for rh in dict.fromkeys(rhs):
            r_p = guardar_producto(conn, codigo, rh, {"titulo": p["titulo"],
                    "tipo_producto": p["tipo"], "categoria": "Por verificar",
                    "estado_validacion": p.get("validacion", "Pendiente"),
                    "anio_publicacion": p["anio"]})
            if r_p == "ok":
                n_prod += 1
                if p.get("validacion") == "Validado":
                    n_val += 1
            elif r_p == "actualizado":
                n_val += 1
    # Perfiles verPerfiles del mismo grupo (basicos + indicadores)
    n_perf = 0
    if basicos_vp or perfiles_vp:
        _guardar_perfiles(conn, codigo, "22", basicos_vp, perfiles_vp)
        n_perf = len(perfiles_vp)
    conn.commit()
    # S37: hoja de vida individual por integrante (CvLAC). Nunca tumba la carga.
    n_hv = 0
    if con_cvlac:
        for rh in rhs_grupo:
            try:
                if scrape_cvlac(rh, db, codigo):
                    n_hv += 1
            except Exception as e:
                print("aviso cvlac %s: %s" % (rh, e))
    conn.close()
    z = empaquetar_grupo(codigo, nro)
    rep = ("OK scrape-grupo %s (%s): [%s] %s | lider=%s | avalan=%s | grupo=%s integrantes=%d historicos_omitidos=%d descartados=%d productos=%d validados=%d hv=%d sin_autor=%d omitidos_tipo=%d perfiles=%d zip=%s"
           % (nro, origen, codigo, (ficha["nombre"] or "")[:60], (ficha["lider"] or "")[:40],
              "; ".join(avaladoras) if avaladoras else "s/d",
               est, n_inv, n_hist, n_desc, n_prod, n_val, n_hv, n_sin_autor, omit, n_perf, z if z else "n/a"))
    print(rep.replace("�", "?"))
    return {"grupo": est, "integrantes": n_inv, "productos": n_prod, "hv": n_hv}


# ---------------- CvLAC (punto 4: info personal + productos) ----------------
# S37: hoja de vida por integrante (Par evaluador, citaciones, nacionalidad,
# sexo, Scholar/ORCID, formación, experiencia, áreas, idiomas).
ETIQUETAS_HV = ("Nombre", "Nombre en citaciones", "Nacionalidad", "Sexo")
SECCIONES_HV = ("Formación Académica", "Formacion Academica",
                "Formación Complementaria", "Formacion Complementaria",
                "Experiencia profesional", "Experiencia Profesional",
                "Áreas de actuación", "Areas de actuacion", "Idiomas")
FIN_HV = ("Cursos de corta duración", "Trabajos dirigidos", "Eventos científicos",
          "Artículos", "Libros", "Capítulos", "Software", "Patentes", "Proyectos",
          "Reconocimientos", "Producción", "Líneas de", "Jurado",
          "Redes sociales", "Identificadores", "Hoja de vida", "Par evaluador")


def _lineas(html):
    soup = BeautifulSoup(html, "html.parser")
    return [l.strip() for l in soup.get_text("\n").split("\n") if l.strip()]


def _valor_etiqueta(lines, etiqueta):
    for i, l in enumerate(lines):
        if l == etiqueta and i + 1 < len(lines):
            v = lines[i + 1]
            if v not in ETIQUETAS_HV and not v.startswith("Categor"):
                return v
    return ""


def _seccion_hv(lines, inicio_markers, tope=2000):
    # El CvLAC repite encabezados en el menú de navegación: se toma la
    # sección más larga (el contenido real, no el menú).
    mejor = ""
    for i, l in enumerate(lines):
        if l in inicio_markers:
            partes = []
            for j in range(i + 1, len(lines)):
                lj = lines[j]
                if lj in SECCIONES_HV or any(lj.startswith(f) for f in FIN_HV):
                    break
                partes.append(lj)
            txt = " ".join(" ".join(partes).split())
            if len(txt) > len(mejor):
                mejor = txt
    return mejor[:tope]


def parse_hoja_vida(html):
    """S37: hoja de vida CvLAC (solo lo pedido: encabezado + formación +
    experiencia + áreas + idiomas). Sin inventar: vacío si no aparece."""
    lines = _lineas(html)
    unido = "\n".join(lines)
    par = "Si" if "Par evaluador reconocido" in unido else "No"
    m_sch = re.search(r'href="(https://scholar\.google[^"]*)"', html)
    m_orc = re.search(r'href="(https://orcid\.org/[^"]*)"', html)
    return {
        "par_evaluador": par,
        "nombre_citaciones": _valor_etiqueta(lines, "Nombre en citaciones"),
        "nacionalidad": _valor_etiqueta(lines, "Nacionalidad"),
        "sexo": _valor_etiqueta(lines, "Sexo"),
        "scholar_url": m_sch.group(1) if m_sch else "",
        "orcid": m_orc.group(1) if m_orc else "",
        "formacion_academica": _seccion_hv(lines, ("Formación Académica", "Formacion Academica")),
        "formacion_complementaria": _seccion_hv(lines, ("Formación Complementaria", "Formacion Complementaria"), 1200),
        "experiencia": _seccion_hv(lines, ("Experiencia profesional", "Experiencia Profesional")),
        "areas": _seccion_hv(lines, ("Áreas de actuación", "Areas de actuacion"), 600),
        "idiomas": _seccion_hv(lines, ("Idiomas",), 600),
    }


def parse_cvlac(html, cod_rh):
    lines = _lineas(html)
    idx = {l: i for i, l in enumerate(lines)}

    def siguiente(marcador):
        for i, l in enumerate(lines):
            if l == marcador and i + 1 < len(lines):
                return lines[i + 1]
        return ""

    nombre = siguiente("Nombre")
    cat = ""
    for i, l in enumerate(lines):
        if l.startswith("Categor"):
            seg = " ".join(lines[i:i + 3])
            m = re.search(r"Investigador\s+([A-Za-z\xc0-\xde]+)", seg)
            if m:
                c = m.group(1).lower()
                if "emerito" in c or "emérito" in c:
                    cat = "Emérito"
                elif c.startswith("senior") or c.startswith("sénior") or c.startswith("senio"):
                    cat = "Senior"
                elif c.startswith("asociado"):
                    cat = "Asociado"
                elif c.startswith("junior"):
                    cat = "Junior"
            break
    # formacion: mayor nivel declarado (solo se reporta; el esquema no tiene columna)
    formacion = ""
    for nivel in ("Doctorado", "Maestr", "Pregrado"):
        for i, l in enumerate(lines):
            if l.startswith(nivel):
                formacion = " | ".join(lines[i:i + 3])[:300]
                break
        if formacion:
            break
    correo = ""
    m = re.search(r"[\w\.-]+@[\w\.-]+", "\n".join(lines))
    if m:
        correo = m.group(0)
    # articulos: bloques "Publicado en revista especializada" ... titulo entrecomillado ... ,AAAA,
    texto = "\n".join(lines)
    articulos = []
    partes = re.split(r"Publicado en revista especializada", texto)
    for blk in partes[1:]:
        mt = re.search(r'"([^"]{8,480})"', blk)
        ma = re.search(r",\s*((?:19|20)\d{2})\s*,", blk)
        if mt:
            anio = int(ma.group(1)) if ma and 1900 <= int(ma.group(1)) <= 2026 else 0
            articulos.append({"titulo": mt.group(1).strip(), "anio": anio})
    return {"nombre": nombre, "categoria": cat or "Por verificar", "formacion": formacion,
            "correo": correo, "articulos": articulos}


def grupos_de(conn, rh):
    return [r[0] for r in conn.execute(
        "SELECT codigo_grupo_fk FROM grupo_investigador WHERE cod_rh_fk=?;", (rh,))]


def scrape_cvlac(cod_rh, db, cod_grupo=""):
    os.makedirs(SNAP_DIR, exist_ok=True)
    snap = os.path.join(SNAP_DIR, "cvlac_%s.html" % cod_rh)
    html = None
    if os.path.exists(snap):
        with open(snap, encoding="utf-8", errors="replace") as f:
            html = f.read()
        origen = "snapshot"
    else:
        url = ("https://scienti.minciencias.gov.co/cvlac/visualizador/"
               "generarCurriculoCv.do?cod_rh=%s" % cod_rh)
        origen, html = descargar_cache(url, "cvlac_%s.html" % cod_rh, db)
        if origen.startswith("error") or not html:
            print("ERROR cvlac %s %s" % (cod_rh, origen))
            return None
    cv = parse_cvlac(html, cod_rh)
    if not cv["nombre"]:
        print("ERROR cvlac %s: sin nombre (HTML inesperado)" % cod_rh)
        return None
    conn = conectar(db)
    conn.execute(
        "INSERT OR IGNORE INTO Investigadores (cod_rh, nombre_completo, correo, categoria_minciencias, cvlac_url, estado)"
        " VALUES (?,?,?,?,?,1);",
        (cod_rh, cv["nombre"], cv["correo"], cv["categoria"],
         "https://scienti.minciencias.gov.co/cvlac/visualizador/generarCurriculoCv.do?cod_rh=%s" % cod_rh))
    # S37-blindaje S31: jamás pisar dato limpio con snapshot sucio (�).
    viejo = conn.execute(
        "SELECT nombre_completo, categoria_minciencias FROM Investigadores WHERE cod_rh=?;",
        (cod_rh,)).fetchone() or ("", "")
    nom_nuevo = cv["nombre"]
    if "�" in (nom_nuevo or "") and "�" not in (viejo[0] or ""):
        nom_nuevo = viejo[0]
    cat_nueva = cv["categoria"]
    if cat_nueva == "Por verificar" and (viejo[1] or "") not in ("", "Por verificar"):
        cat_nueva = viejo[1]
    conn.execute(
        "UPDATE Investigadores SET nombre_completo=?, correo=COALESCE(NULLIF(?,''),correo),"
        " categoria_minciencias=?, cvlac_url=? WHERE cod_rh=?;",
        (nom_nuevo, cv["correo"], cat_nueva,
         "https://scienti.minciencias.gov.co/cvlac/visualizador/generarCurriculoCv.do?cod_rh=%s" % cod_rh,
         cod_rh))
    grupos = [cod_grupo] if cod_grupo else grupos_de(conn, cod_rh)
    # S37: hoja de vida del integrante (REPLACE = idempotente).
    hv = parse_hoja_vida(html)
    viejo_hv = conn.execute(
        "SELECT par_evaluador, nombre_citaciones, nacionalidad, sexo, scholar_url, orcid,"
        " formacion_academica, formacion_complementaria, experiencia, areas, idiomas"
        " FROM perfil_investigador WHERE cod_rh=?;", (cod_rh,)).fetchone()
    if viejo_hv:
        claves = ("par_evaluador", "nombre_citaciones", "nacionalidad", "sexo",
                  "scholar_url", "orcid", "formacion_academica",
                  "formacion_complementaria", "experiencia", "areas", "idiomas")
        for i, k in enumerate(claves):
            if "�" in (hv[k] or "") and "�" not in (viejo_hv[i] or ""):
                hv[k] = viejo_hv[i]
    conn.execute(
        "REPLACE INTO perfil_investigador (cod_rh, par_evaluador, nombre_citaciones,"
        " nacionalidad, sexo, scholar_url, orcid, formacion_academica,"
        " formacion_complementaria, experiencia, areas, idiomas)"
        " VALUES (?,?,?,?,?,?,?,?,?,?,?,?);",
        (cod_rh, hv["par_evaluador"], hv["nombre_citaciones"], hv["nacionalidad"],
         hv["sexo"], hv["scholar_url"], hv["orcid"], hv["formacion_academica"],
         hv["formacion_complementaria"], hv["experiencia"], hv["areas"], hv["idiomas"]))
    n_p = n_e = 0
    for a in cv["articulos"]:
        if not a["anio"]:
            continue
        for g in grupos:
            conn.execute(
                "INSERT OR IGNORE INTO grupo_investigador (codigo_grupo_fk, cod_rh_fk) VALUES (?,?);",
                (g, cod_rh))
            r_p = guardar_producto(conn, g, cod_rh,
                                   {"titulo": a["titulo"], "tipo_producto": "Artículo",
                                    "categoria": "Por verificar", "estado_validacion": "Pendiente",
                                    "anio_publicacion": a["anio"]})
            if r_p == "ok":
                n_p += 1
            elif r_p == "existente":
                n_e += 1
    conn.commit()
    conn.close()
    print("OK scrape-cvlac %s (%s): %s | cat=%s | par=%s | hv=%s | articulos_nuevos=%d existentes=%d grupos=%s"
          % (cod_rh, origen, cv["nombre"][:50], cv["categoria"], hv["par_evaluador"],
             ("citas+formacion" if hv["nombre_citaciones"] or hv["formacion_academica"] else "basica"),
             n_p, n_e, grupos if grupos else "ninguno"))
    return {"categoria": cv["categoria"], "articulos": n_p}


# ---------------- CSV / PDF / offline ----------------
CSV_COLS = ["codigo_grupo", "nombre_grupo", "lider_grupo", "cod_rh", "nombre_investigador",
            "correo_investigador", "titulo_producto", "tipo_producto", "categoria",
            "estado_validacion", "anio_publicacion"]


def ingesta_csv(path, db):
    conn = conectar(db)
    n_g = n_i = n_p = n_e = n_d = 0
    with open(path, encoding="utf-8-sig") as f:
        for fila in csv.DictReader(f):
            ug, _ = proyectar(fila, "grupo")
            ui, _ = proyectar(fila, "investigador")
            up, _ = proyectar(fila, "producto")
            cod = ug.get("codigo_grupo", "")
            if not cod:
                n_d += 1
                continue
            g = {"codigo_grupo": cod, "nombre": ug.get("nombre", ""),
                 "lider": ug.get("lider", "") or "Por verificar",
                 "plan_investigacion": ug.get("plan_investigacion", ""),
                 "lineas_estrategicas": ug.get("lineas_estrategicas", "")}
            if guardar_grupo(conn, g)[0] == "ok":
                n_g += 1
            if ui.get("nombre_completo", ""):
                est_i, _, rh = guardar_investigador(conn, cod, ui)
                if est_i in ("ok", "existente"):
                    if est_i == "ok":
                        n_i += 1
                    if up.get("titulo", ""):
                        r_p = guardar_producto(conn, cod, rh, up)
                        if r_p == "ok":
                            n_p += 1
                        elif r_p == "existente":
                            n_e += 1
                        else:
                            n_d += 1
                else:
                    n_d += 1
            else:
                n_d += 1
    conn.commit()
    conn.close()
    print("OK ingesta-csv: grupos=%d investigadores=%d productos=%d existentes=%d descartadas=%d"
          % (n_g, n_i, n_p, n_e, n_d))


def _palabras_pdf(path):
    """Palabras con coordenadas (x, y, texto) via visitor de pypdf."""
    from pypdf import PdfReader
    words = []

    def visit(text, cm, tm, font_dict, fs):
        t = (text or "").strip()
        if t:
            words.append((round(float(tm[4]), 1), round(float(tm[5]), 1), t))

    reader = PdfReader(path)
    for p in reader.pages:
        p.extract_text(visitor_text=visit)
    return words


def ingesta_pdf_tabular(path, db):
    """Nivel 1: tabla por coordenadas -> filas de 11 columnas -> misma persistencia que CSV."""
    words = _palabras_pdf(path)
    if not words:
        return None
    ys = sorted(set(y for _, y, _ in words), reverse=True)
    filas_y, cur, Tol = [], [], 3.0
    for y in ys:
        if not cur or abs(cur[0] - y) <= Tol:
            cur.append(y)
        else:
            filas_y.append(cur)
            cur = [y]
    if cur:
        filas_y.append(cur)
    bandas = []
    for grupo_y in filas_y:
        wy = [w for w in words if any(abs(w[1] - y) <= Tol for y in grupo_y)]
        wy.sort(key=lambda w: w[0])
        bandas.append(wy)
    # header = banda con mas coincidencias canonicas (cualquiera de las 3 entidades)
    todos_mapas = {}
    for m in MAPAS.values():
        todos_mapas.update(m)

    def puntaje(banda):
        return sum(1 for _, _, w in banda if normalizar_clave(w) in todos_mapas)

    hi = max(range(len(bandas)), key=lambda i: puntaje(bandas[i]))
    if puntaje(bandas[hi]) < 3:
        return None  # sin tabla reconocible -> fallback heuristico
    cab = bandas[hi]
    col_x = [x for x, _, _ in cab]
    col_nom = [normalizar_clave(w) for _, _, w in cab]

    def a_columna(x):
        # Pertenece a la columna donde EMPIEZA (tablas alineadas a la izquierda):
        # la palabra es de la ultima columna cuyo inicio <= x (+tolerancia de padding).
        idx = 0
        for i, cx in enumerate(col_x):
            if cx <= x + 2.0:
                idx = i
        return idx

    # Ensamble: nueva fila logica cuando la banda trae la columna 0 (codigo);
    # si no, es continuacion envuelta y se fusiona con la fila en curso.
    filas_logicas, actual = [], {}
    for banda in bandas[hi + 1:]:
        es_inicio = any(abs(x - col_x[0]) <= 4.0 for x, _, _ in banda)
        if es_inicio and actual:
            filas_logicas.append(actual)
            actual = {}
        for x, _, w in banda:
            i = a_columna(x)
            actual[i] = (actual.get(i, "") + " " + w).strip()
    if actual:
        filas_logicas.append(actual)
    n_g = n_i = n_p = n_e = n_desc = 0
    conn = conectar(db)
    for celdas in filas_logicas:
        fila = {col_nom[i]: celdas.get(i, "") for i in range(len(col_nom))}
        ug, _ = proyectar(fila, "grupo")
        ui, _ = proyectar(fila, "investigador")
        up, _ = proyectar(fila, "producto")
        cod = ug.get("codigo_grupo", "")
        if not cod or not ui.get("nombre_completo", ""):
            n_desc += 1
            continue
        g = {"codigo_grupo": cod, "nombre": ug.get("nombre", ""),
             "lider": ug.get("lider", "") or "Por verificar",
             "plan_investigacion": ug.get("plan_investigacion", ""),
             "lineas_estrategicas": ug.get("lineas_estrategicas", "")}
        if guardar_grupo(conn, g)[0] == "ok":
            n_g += 1
        est_i, _, rh = guardar_investigador(conn, cod, ui)
        if est_i not in ("ok", "existente"):
            n_desc += 1
            continue
        if est_i == "ok":
            n_i += 1
        if up.get("titulo", ""):
            r_p = guardar_producto(conn, cod, rh, up)
            if r_p == "ok":
                n_p += 1
            elif r_p == "existente":
                n_e += 1
            else:
                n_desc += 1
    conn.commit()
    conn.close()
    return {"grupos": n_g, "investigadores": n_i, "productos": n_p,
            "existentes": n_e, "descartadas": n_desc}


def ingesta_pdf_heuristica(path, db, cod_grupo, rh):
    """Nivel 2 (fallback): 1 producto desde texto plano."""
    from pypdf import PdfReader
    reader = PdfReader(path)
    texto = "\n".join([(p.extract_text() or "") for p in reader.pages])
    lineas = [l.strip() for l in texto.split("\n") if l.strip()]
    titulo = lineas[0][:480] if lineas else os.path.basename(path)
    cands = [int(x) for x in re.findall(r"(?:19|20)\d{2}", texto) if 1900 <= int(x) <= 2026]
    anio = cands[-1] if cands else 0
    conn = conectar(db)
    r = guardar_producto(conn, cod_grupo, rh,
                         {"titulo": titulo, "tipo_producto": "Artículo",
                          "categoria": "Por verificar", "estado_validacion": "Pendiente",
                          "anio_publicacion": anio})
    conn.commit()
    conn.close()
    return r


def ingesta_pdf(path, db, cod_grupo="", rh=""):
    res = None
    try:
        res = ingesta_pdf_tabular(path, db)
    except Exception as e:
        print("AVISO tabla no legible (%s); usando heuristica." % str(e)[:80])
    if res is not None:
        print("OK ingesta-pdf-tabular: grupos=%d investigadores=%d productos=%d existentes=%d descartadas=%d"
              % (res["grupos"], res["investigadores"], res["productos"], res["existentes"], res["descartadas"]))
        return
    if not cod_grupo or not rh:
        print("ERROR PDF sin tabla y sin --grupo/--rh para heuristica")
        return
    r = ingesta_pdf_heuristica(path, db, cod_grupo, rh)
    print("OK ingesta-pdf-heuristica: %s" % r)


# ---------------- Buscador SCIENTI (nombre grupo / universidad) ----------------
CIENCIA_BASE = "https://scienti.minciencias.gov.co/ciencia-war"
IDX_INST = os.path.join(BASE, "data", "indice_instituciones.json")
IDX_GRUPOS = os.path.join(BASE, "data", "indice_grupos.json")


def _tabla_grupos_ciencia(html):
    """Filas (COL, nombre, lider, avalado, estado, categoria, nro) de la pagina de institucion."""
    soup = BeautifulSoup(html, "html.parser")
    out = []
    candidatas = [t for t in soup.find_all("table")
                  if "Cod grupo" in " ".join(t.get_text(" ").split())
                  and "Nombre grupo" in " ".join(t.get_text(" ").split())]
    candidatas.sort(key=lambda t: 0 if t.get("id") else 1)  # la tabla con id primero
    for t in candidatas[:1]:
        th = " ".join(t.get_text(" ").split())
        if "Cod grupo" in th and "Nombre grupo" in th:
            for tr in t.find_all("tr")[1:]:
                tds = [c.get_text(" ").strip() for c in tr.find_all(["td", "th"], recursive=False)]
                # Fila de datos = la que tiene celda ^COL\d+ (hay columna de numero y filas de control)
                ic = next((i for i, d in enumerate(tds) if re.match(r"^COL\d+$", d)), -1)
                if ic < 0 or ic + 1 >= len(tds):
                    continue
                nombre = tds[ic + 1]
                if not nombre:
                    continue
                nro = ""
                for a in tr.find_all("a", href=True):
                    m = re.search(r"nro=(\d+)", a.get("href", ""))
                    if m:
                        nro = m.group(1)
                        break
                resto = tds[ic + 2:]
                out.append({"col": tds[ic], "nombre": nombre,
                            "lider": resto[0] if len(resto) > 0 else "",
                            "avalado": resto[2] if len(resto) > 2 else "",
                            "estado": resto[3] if len(resto) > 3 else "",
                            "categoria": resto[4] if len(resto) > 4 else "",
                            "nro": nro})
            break
    return out


def _tabla_id_grupos(html):
    soup = BeautifulSoup(html, "html.parser")
    for t in soup.find_all("table"):
        th = " ".join(t.get_text(" ").split())
        if "Cod grupo" in th and "Nombre grupo" in th and t.get("id"):
            return t.get("id")
    return ""


def indice_instituciones(db="", forzar=False):
    """Indice nombre -> (codInst, n_grupos). Un solo request (mr_=2000). Cache en JSON."""
    if os.path.exists(IDX_INST) and not forzar:
        return json.load(open(IDX_INST, encoding="utf-8"))
    url = CIENCIA_BASE + "/busquedaGruposPorInstitucion.do?" + urlencode({"all_grupos_ins_mr_": "2000"})
    r = sesion_http().get(url, headers=UA, timeout=30)
    r.encoding = codificacion_respuesta(r)
    if r.status_code != 200:
        print("ERROR instituciones status=%s" % r.status_code)
        return []
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
    json.dump(out, open(IDX_INST, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("OK indice-instituciones: %d instituciones" % len(out))
    return out


def grupos_de_institucion(codinst, nombre_inst="", forzar=False):
    """Grupos de una institucion con nro. Cache por institucion en indice_grupos.json."""
    idx = {}
    if os.path.exists(IDX_GRUPOS):
        idx = json.load(open(IDX_GRUPOS, encoding="utf-8"))
    if str(codinst) in idx and not forzar:
        return idx[str(codinst)]
    import requests as _rq  # sin sesion: la cookie JMesa ignora el mr_ (verificado)
    url = CIENCIA_BASE + "/busquedaGrupoXInstitucionGrupos.do?" + urlencode({"codInst": codinst})
    r = _rq.get(url, headers=UA, timeout=30)
    r.encoding = codificacion_respuesta(r)
    if r.status_code != 200:
        print("ERROR grupos-institucion %s status=%s" % (codinst, r.status_code))
        return []
    tid = _tabla_id_grupos(r.text)
    if tid:  # traer todos de una vez (JMesa: <id>_mr_)
        r2 = _rq.get(url + "&" + urlencode({tid + "_mr_": "500"}), headers=UA, timeout=30)
        if r2.status_code == 200:
            r = r2
            r.encoding = codificacion_respuesta(r)
    grupos = _tabla_grupos_ciencia(r.text)
    for g in grupos:
        g["institucion"] = nombre_inst
        g["codinst"] = str(codinst)
    idx[str(codinst)] = grupos
    json.dump(idx, open(IDX_GRUPOS, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return grupos


def buscar_universidad(texto):
    inst = indice_instituciones()
    q = normalizar_clave(texto).replace("_", " ")
    cands = [i for i in inst if q and q in normalizar_clave(i["nombre"]).replace("_", " ")]
    if not cands:
        print("Universidad no encontrada (texto=%s)." % texto)
        return []
    for i, c in enumerate(cands, 1):
        print("UNIV|%d|%s|%s|%s" % (i, c["codinst"], c["nombre"][:70], c["n_grupos"]))
    return cands


def buscar_grupo(nombre):
    idx = {}
    if os.path.exists(IDX_GRUPOS):
        idx = json.load(open(IDX_GRUPOS, encoding="utf-8"))
    inst_nom = {}
    if os.path.exists(IDX_INST):
        for i in json.load(open(IDX_INST, encoding="utf-8")):
            inst_nom[str(i.get("codinst", ""))] = i.get("nombre", "")
    q = normalizar_clave(nombre).replace("_", " ")
    cands = []
    for codinst, grupos in idx.items():
        for g in grupos:
            if q and q in normalizar_clave(g.get("nombre", "")).replace("_", " "):
                g = dict(g)
                g["institucion"] = g.get("institucion", "") or inst_nom.get(str(codinst), "")
                cands.append(g)
    if not cands:
        print("Grupo no encontrado en el indice local (texto=%s). Indexe su institucion con --grupos-institucion CODINST." % nombre)
        return []
    for i, g in enumerate(cands, 1):
        print("CAND|%d|%s|%s|%s|%s|%s|%s" % (i, g.get("nro", ""), g.get("nombre", "")[:60],
              g.get("col", ""), g.get("lider", "")[:40], g.get("institucion", "")[:50],
              g.get("categoria", "")))
    return cands


# ---------------- verPerfiles (basicos + indicadores por subtipo) ----------------
def parse_verperfiles(html):
    lines = _lineas(html)
    texto = "\n".join(lines)

    def campo(*etiquetas):
        for i, l in enumerate(lines):
            for et in etiquetas:
                if l.rstrip(":") == et and i + 1 < len(lines):
                    # valor puede ocupar varias lineas hasta la proxima etiqueta
                    vals = []
                    for j in range(i + 1, min(i + 6, len(lines))):
                        if lines[j].endswith(":") or lines[j].startswith("Programa") \
                                or lines[j].startswith("Gran ") or lines[j].startswith("Fecha de"):
                            break
                        vals.append(lines[j])
                    return " ".join(vals).strip()
        return ""

    ccrg = campo("CCRG")
    mcc = re.search(r"COL\d+", ccrg)
    nombre_grupo, sigla_vp = "", ""
    for l in lines[1:6]:
        if len(l) > 15 and not l.startswith("Perfil"):
            nombre_grupo = l
            ms = re.search(r"-([A-Z]{2,12})-\s*$", l)
            if ms:
                sigla_vp = ms.group(1)
            break
    basicos = {
        "nombre": nombre_grupo,
        "sigla": sigla_vp,
        "ccrg": mcc.group(0) if mcc else "",
        "lider": campo("Líder", "Lider"),
        "programa": campo("Programa Nacional"),
        "gran_area": campo("Gran Área", "Gran Area"),
        "area": campo("Área", "Area"),
        "fecha_creacion": campo("Fecha de creación", "Fecha de creacion"),
        "instituciones": campo("Instituciones"),
    }
    # Tablas de indicadores: seccion "Perfil de..." + filas de 11 celdas
    soup = BeautifulSoup(html, "html.parser")
    perfiles = []
    nt = 0
    for t in soup.find_all("table"):
        th = " ".join(t.get_text(" ").split())
        if "Valor del indicador para el Grupo" not in th:
            continue
        nt += 1
        # seccion = encabezado "Perfil de..." mas cercano hacia atras
        seccion = ""
        for prev in t.find_all_previous(["h1", "h2", "h3", "b", "strong"]):
            pt = " ".join(prev.get_text(" ").split())
            if pt.startswith("Perfil de"):
                seccion = pt[:100]
                break
        if not seccion:
            seccion = "general_t%d" % nt
        for tr in t.find_all("tr"):
            celdas = [c.get_text(" ").strip() for c in tr.find_all(["td", "th"], recursive=False)]
            if len(celdas) < 11 or not celdas[0]:
                continue
            if "uartil" in celdas[0] or "breviatura" in celdas[1]:
                continue  # fila de encabezado
            perfiles.append({"seccion": seccion, "subtipo": celdas[0],
                             "abreviatura": celdas[1], "valor": celdas[9],
                             "cuartil": celdas[10]})
    return basicos, perfiles


def _remap_codigo(conn, viejo, nuevo):
    """Migra un codigo de grupo (PK + FKs). FKs OFF durante el remapeo."""
    conn.execute("PRAGMA foreign_keys=OFF;")
    try:
        for tbl, col in (("Productos", "codigo_grupo_fk"),
                         ("grupo_investigador", "codigo_grupo_fk"),
                         ("perfiles_grupo", "codigo_grupo")):
            try:
                conn.execute("UPDATE %s SET %s=? WHERE %s=?;" % (tbl, col, col), (nuevo, viejo))
            except Exception:
                pass
        conn.execute("UPDATE Grupos SET codigo_grupo=? WHERE codigo_grupo=?;", (nuevo, viejo))
        conn.commit()
    finally:
        conn.execute("PRAGMA foreign_keys=ON;")
    mal = conn.execute("PRAGMA foreign_key_check;").fetchall()
    return not mal


def resolver_codigo(conn, nro, ccrg, sigla, nombre):
    """Devuelve el codigo vigente del grupo, migrando sigla/G+nro -> CCRG (COL original)."""
    if ccrg:
        for cand in (ccrg, sigla, "G" + nro[-6:]):
            if cand and conn.execute("SELECT 1 FROM Grupos WHERE codigo_grupo=?;",
                                     (cand,)).fetchone():
                if cand != ccrg:
                    _remap_codigo(conn, cand, ccrg)
                return ccrg
        fila_nom = conn.execute("SELECT codigo_grupo FROM Grupos WHERE nombre=?;",
                                (nombre,)).fetchone() if nombre else None
        if fila_nom and fila_nom[0] != ccrg:
            _remap_codigo(conn, fila_nom[0], ccrg)
            return ccrg
    return sigla or ("G" + nro[-6:])


def _guardar_perfiles(conn, codigo, convocatoria, basicos, perfiles):
    """Persiste basicos + indicadores (REPLACE = idempotente). Reutilizado por scrape_grupo."""
    if basicos.get("lider"):
        conn.execute("UPDATE Grupos SET lider=? WHERE codigo_grupo=? AND (lider='' OR lider='Por verificar');",
                     (basicos["lider"], codigo))
    for campo, valor in (("programa_nacional", basicos.get("programa", "")),
                         ("gran_area", basicos.get("gran_area", "")),
                         ("area", basicos.get("area", "")),
                         ("fecha_creacion", basicos.get("fecha_creacion", "")),
                         ("instituciones", basicos.get("instituciones", "")),
                         ("ccrg", basicos.get("ccrg", ""))):
        if valor:
            conn.execute("REPLACE INTO perfiles_grupo (codigo_grupo, convocatoria, seccion, subtipo,"
                         " abreviatura, valor_grupo, cuartil_grupo) VALUES (?,?,?,?,?,?,?);",
                         (codigo, convocatoria, "basicos", campo, "", valor, ""))
    for p in perfiles:
        conn.execute("REPLACE INTO perfiles_grupo (codigo_grupo, convocatoria, seccion, subtipo,"
                     " abreviatura, valor_grupo, cuartil_grupo) VALUES (?,?,?,?,?,?,?);",
                     (codigo, convocatoria, p["seccion"][:120], p["subtipo"][:200],
                      p["abreviatura"][:20], p["valor"][:50], p["cuartil"][:10]))


def scrape_perfiles(nro, db, convocatoria="22", usar_snapshot=True):
    """Descarga verPerfiles: basicos (CCRG/lider/instituciones) + indicadores por subtipo."""
    os.makedirs(SNAP_DIR, exist_ok=True)
    url = ("https://scienti.minciencias.gov.co/gruplac/jsp/Medicion/graficas/"
           "verPerfiles.jsp?id_convocatoria=%s&nroIdGrupo=%s" % (convocatoria, nro))
    html = None
    snap = os.path.join(SNAP_DIR, "verperfiles_%s.html" % nro)
    if usar_snapshot and os.path.exists(snap):
        with open(snap, encoding="utf-8", errors="replace") as f:
            html = f.read()
        origen = "snapshot"
    else:
        origen, html = descargar_cache(url, "verperfiles_%s.html" % nro, db)
        if origen.startswith("error") or not html:
            print("ERROR verPerfiles %s %s" % (nro, origen))
            return None
    basicos, perfiles = parse_verperfiles(html)
    if not basicos["ccrg"] and not perfiles:
        print("verPerfiles sin datos (nro=%s): pagina inesperada." % nro)
        return None
    conn = conectar(db)
    codigo = resolver_codigo(conn, nro, basicos["ccrg"], basicos.get("sigla", ""),
                             basicos.get("nombre", ""))
    if not conn.execute("SELECT 1 FROM Grupos WHERE codigo_grupo=?;", (codigo,)).fetchone():
        conn.close()
        print("Grupo %s no esta en la BD: ejecute primero --scrape-grupo %s." % (codigo, nro))
        return None
    _guardar_perfiles(conn, codigo, convocatoria, basicos, perfiles)
    n_ind = len(perfiles)
    conn.commit()
    conn.close()
    z = empaquetar_grupo(codigo, nro)
    print("OK verPerfiles %s (%s): [%s] CCRG=%s lider=%s indicadores=%d zip=%s"
          % (nro, origen, codigo, basicos["ccrg"], (basicos["lider"] or "")[:40],
             n_ind, z if z else "n/a"))
    return {"codigo": codigo, "ccrg": basicos["ccrg"], "indicadores": n_ind}


# ---------------- CLI ----------------
def main(argv=None):
    ap = argparse.ArgumentParser(description="PEA-i ingesta (Fase 3)")
    ap.add_argument("--db", default=DB_DEF)
    ap.add_argument("--gui", action="store_true")
    ap.add_argument("--scrape-url", default="")
    ap.add_argument("--scrape-grupo", default="")
    ap.add_argument("--scrape-todos", action="store_true")
    ap.add_argument("--grupos-archivo", default=GRUPOS_DEF)
    ap.add_argument("--ingesta-archivo", default="")
    ap.add_argument("--grupo", default="")
    ap.add_argument("--rh", default="")
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--universidad", default="")
    ap.add_argument("--buscar-universidad", default="")
    ap.add_argument("--buscar-grupo", default="")
    ap.add_argument("--grupos-institucion", default="")
    ap.add_argument("--indexar-instituciones", action="store_true")
    ap.add_argument("--perfiles", default="")
    ap.add_argument("--convocatoria", default="22")
    ap.add_argument("--forzar", action="store_true",
                    help="S32: re-scrapea aunque el grupo ya esté cargado")
    ap.add_argument("--sin-cvlac", action="store_true",
                    help="S37: omite la hoja de vida CvLAC por integrante (carga rápida)")
    ap.add_argument("--existe-grupo", default="",
                    help="S32: chequeo offline (sin red) ¿el nro ya está en BD?")
    ap.add_argument("--limpiar-zips", action="store_true",
                    help="S32: borra zips legacy huérfanos (GISICO->COL0018706...)")
    a = ap.parse_args(argv)

    if a.limpiar_zips:
        lim = limpiar_zips_huerfanos()
        return 0
    if a.existe_grupo:
        cod, nom = existe_grupo_en_bd(a.existe_grupo, a.db)
        if cod:
            print("[AVISO] grupo ya existente | CODIGO=%s | GRUPO=%s" % (cod, (nom or "")[:60]))
            print("No se descargo nada nuevo ni se duplico informacion.")
            return 0
        print("grupo no cargado (nro=%s)" % a.existe_grupo)
        return 1

    if a.perfiles:
        return 0 if scrape_perfiles(a.perfiles, a.db, convocatoria=a.convocatoria) else 1

    if a.indexar_instituciones:
        indice_instituciones(forzar=True)
        return 0
    if a.buscar_universidad:
        buscar_universidad(a.buscar_universidad)
        return 0
    if a.grupos_institucion:
        gs = grupos_de_institucion(a.grupos_institucion, forzar=True)
        print("OK grupos-institucion %s: %d grupos" % (a.grupos_institucion, len(gs)))
        for g in gs[:50]:
            print("G|%s|%s|%s" % (g.get("nro", ""), g.get("nombre", "")[:60], g.get("categoria", "")))
        return 0
    if a.buscar_grupo:
        buscar_grupo(a.buscar_grupo)
        return 0

    if a.gui:
        print("INFO dashboard Tkinter pendiente (Fase 5). Use la consola C++ (opcion 5) para el resumen 12.a.")
        return 0
    if a.scrape_todos:
        nros = [l.strip() for l in open(a.grupos_archivo, encoding="utf-8")
                if l.strip() and not l.startswith("#")]
        for nro in nros:
            try:
                scrape_grupo(nro, a.db, universidad=a.universidad, forzar=a.forzar,
                             con_cvlac=not a.sin_cvlac)
            except Exception as e:
                print("ERROR scrape-grupo %s: %s" % (nro, e))
        limpiar_zips_huerfanos()
        return 0
    if a.scrape_grupo:
        r = scrape_grupo(a.scrape_grupo, a.db, usar_snapshot=False,
                         universidad=a.universidad, forzar=a.forzar,
                         con_cvlac=not a.sin_cvlac)
        limpiar_zips_huerfanos()
        return 0 if r else 1
    if a.scrape_url:
        m1 = re.search(r"nro=(\d+)", a.scrape_url)
        m2 = re.search(r"cod_rh=(\d+)", a.scrape_url)
        if m1:
            r = scrape_grupo(m1.group(1), a.db, usar_snapshot=False,
                             universidad=a.universidad, forzar=a.forzar,
                             con_cvlac=not a.sin_cvlac)
            limpiar_zips_huerfanos()
            return 0 if r else 1
        if m2:
            return 0 if scrape_cvlac(m2.group(1), a.db, a.grupo) else 1
        print("ERROR URL no reconocida (se espera nro= o cod_rh=)")
        return 1
    if a.offline:
        ingesta_csv(os.path.join(BASE, "data", "dataset_respaldo.csv"), a.db)
        return 0
    if a.ingesta_archivo:
        if a.ingesta_archivo.lower().endswith(".pdf"):
            ingesta_pdf(a.ingesta_archivo, a.db, a.grupo, a.rh)
        else:
            ingesta_csv(a.ingesta_archivo, a.db)
        return 0
    print("PEA-i Python: use --scrape-grupo NRO | --perfiles NRO [--convocatoria 22] | --scrape-todos | --ingesta-archivo F | --offline | --gui")
    return 0


if __name__ == "__main__":
    # La consola Windows (cp1252) no puede imprimir los � de SCIENTI:
    # se fuerza UTF-8 con reemplazo para no tumbar la ingesta (BUG-10).
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(main())

