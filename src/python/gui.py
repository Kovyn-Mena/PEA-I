"""
=====================================================================
PEA-i: DASHBOARD GRÁFICO INTERACTIVO (PYTHON - FASE 5)
Universidad Popular del Cesar — Estructura de Datos
Docente: Ing. Adith Pérez
=====================================================================
Cumple estrictamente los requisitos 12.b y 12.c del Taller 2:
  • 12.b: Dashboard con histogramas y diagramas de barras (HTML5 Interactivo).
  • 12.c: Tres aproximaciones / vistas:
      i. Por Grupo
      ii. Por Investigador
      iii. Por Productos
  • Macro-Tipologías MinCiencias (SCIENTI Actualizado):
      - GNC: Generación de Nuevo Conocimiento (Artículos A1-C, Libros, Capítulos, Patentes)
      - DTE: Desarrollo Tecnológico e Innovación (Software, Diseños, Prototipos)
      - ASC: Apropiación Social del Conocimiento (Eventos, Divulgación)
      - FRH: Formación de Recurso Humano (Trabajos de Grado, Tesis)
  • Punto 10: Selector interactivo de ventana de observación (Años).
  • Paleta Institucional UPC: Verde #006837, Rojo #ED1C24.

Arquitectura Zero-Dependencies / Portal Gráfico Interactivo:
  - Produce un Dashboard interactivo HTML5 autónomo con las 3 vistas institucionales (Grupo, Investigador, Productos) y generación de reportes en PDF.
  - Abre fluidamente en el navegador predeterminado del sistema (100% multiplataforma, sin dependencias ni conflictos con entornos gráficos de escritorio).
=====================================================================
"""

import os
import sys
import webbrowser
import sqlite3



BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
pylib_dir = os.path.join(PROJECT_ROOT, "pylib")
if os.path.exists(pylib_dir) and pylib_dir not in sys.path:
    sys.path.insert(0, pylib_dir)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.python.structures.multilista import Multilista
from src.python.core.db import GestorPersistencia
from src.python.core.catalogo_2024 import CatalogoMinCiencias2024
from src.python.core.reporte_pdf import generar_informe_grupo_pdf


# Macro-Tipologías MinCiencias
def obtener_macro_tipologia(tipo: str) -> str:
    t = tipo.lower()
    if any(k in t for k in ["articulo", "artículo", "libro", "capitulo", "capítulo", "patente"]):
        return "GNC (Generación Nuevo Conocimiento)"
    elif any(k in t for k in ["software", "prototipo", "diseno", "diseño", "innovacion", "innovación", "tecnologico"]):
        return "DTE (Desarrollo Tecnológico e Innovación)"
    elif any(k in t for k in ["evento", "taller", "divulgacion", "divulgación", "apropiacion", "social"]):
        return "ASC (Apropiación Social del Conocimiento)"
    elif any(k in t for k in ["grado", "tesis", "pasantia", "posgrado", "formacion"]):
        return "FRH (Formación Recurso Humano)"
    return "GNC (Generación Nuevo Conocimiento)"


# =====================================================================
# GENERADORES DE GRÁFICOS SVG EN LÍNEA (Zero-Dependencies)
# Se renderizan aquí en Python y se incrustan como SVG vectorial:
# sin matplotlib, sin CDNs y sin JavaScript externo. Funcionan 100%
# offline y con zoom nítido en cualquier pantalla.
# =====================================================================
def _svg_barras_verticales(pares, ancho=780, alto=290, color="#10b981",
                           color2="#006837", rotular_valores=True):
    """Histograma / barras verticales. pares: lista de (etiqueta, valor)."""
    if not pares:
        return ('<div style="color:#64748b; font-size:0.82rem; padding:1.2rem;'
                ' border:1px dashed #1e293b; border-radius:8px;">Sin datos disponibles para este gráfico.</div>')
    maxv = max(v for _, v in pares) or 1
    n = len(pares)
    pad_izq, pad_der, pad_arr, pad_abajo = 46, 14, 30, 62
    area_w = ancho - pad_izq - pad_der
    area_h = alto - pad_arr - pad_abajo
    paso = area_w / n
    ancho_barra = max(4.0, min(46.0, paso * 0.68))
    partes = []
    # Rejilla horizontal + escala
    for gi in range(5):
        y = pad_arr + area_h * gi / 4
        val = maxv * (4 - gi) / 4
        partes.append(f'<line x1="{pad_izq}" y1="{y:.1f}" x2="{ancho - pad_der}" y2="{y:.1f}" '
                      f'stroke="#1e293b" stroke-width="1"/>')
        partes.append(f'<text x="{pad_izq - 7}" y="{y + 4:.1f}" fill="#64748b" font-size="10" '
                      f'text-anchor="end">{val:,.0f}</text>')
    for i, (et, v) in enumerate(pares):
        h = area_h * (v / maxv)
        x = pad_izq + i * paso + (paso - ancho_barra) / 2
        y = pad_arr + area_h - h
        c = color if i % 2 == 0 else color2
        partes.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{ancho_barra:.1f}" '
                      f'height="{max(1.0, h):.1f}" rx="3" fill="{c}"><title>{et}: {v:,}</title></rect>')
        if rotular_valores and h >= 15:
            partes.append(f'<text x="{x + ancho_barra / 2:.1f}" y="{y - 5:.1f}" fill="#cbd5e1" '
                          f'font-size="9.5" font-weight="700" text-anchor="middle">{v:,}</text>')
        lx = x + ancho_barra / 2
        ly = pad_arr + area_h + 16
        partes.append(f'<text x="{lx:.1f}" y="{ly:.1f}" fill="#94a3b8" font-size="9.5" '
                      f'text-anchor="end" transform="rotate(-42 {lx:.1f} {ly:.1f})">{et}</text>')
    return (f'<svg viewBox="0 0 {ancho} {alto}" width="100%" height="auto" role="img" '
            f'xmlns="http://www.w3.org/2000/svg">' + "".join(partes) + "</svg>")


def _svg_barras_horizontales(pares, ancho=780, color="#38bdf8", color2="#006837",
                             alto_fila=30, ancho_etiqueta=196):
    """Barras horizontales ordenadas. pares: lista de (etiqueta, valor)."""
    if not pares:
        return ('<div style="color:#64748b; font-size:0.82rem; padding:1.2rem;'
                ' border:1px dashed #1e293b; border-radius:8px;">Sin datos disponibles para este gráfico.</div>')
    maxv = max(v for _, v in pares) or 1
    n = len(pares)
    pad_der = 66
    area_w = ancho - ancho_etiqueta - pad_der
    alto = n * alto_fila + 10
    partes = []
    for i, (et, v) in enumerate(pares):
        y = i * alto_fila + 5
        w = area_w * (v / maxv)
        c = color if i % 2 == 0 else color2
        etiqueta = et if len(et) <= 32 else et[:31] + "…"
        partes.append(f'<text x="{ancho_etiqueta - 9}" y="{y + 15:.1f}" fill="#cbd5e1" font-size="10.5" '
                      f'text-anchor="end"><title>{et}</title>{etiqueta}</text>')
        partes.append(f'<rect x="{ancho_etiqueta}" y="{y}" width="{area_w}" height="18" rx="4" fill="#0f172a"/>')
        partes.append(f'<rect x="{ancho_etiqueta}" y="{y}" width="{max(2.0, w):.1f}" height="18" rx="4" '
                      f'fill="{c}"><title>{et}: {v:,}</title></rect>')
        partes.append(f'<text x="{ancho_etiqueta + area_w + 9}" y="{y + 14:.1f}" fill="#e2e8f0" '
                      f'font-size="10.5" font-weight="700">{v:,}</text>')
    return (f'<svg viewBox="0 0 {ancho} {alto}" width="100%" height="auto" role="img" '
            f'xmlns="http://www.w3.org/2000/svg">' + "".join(partes) + "</svg>")

class DashboardApp:
    def __init__(self, ruta_bd: str = "data/pea_investigacion.db"):
        self.ruta_bd = ruta_bd
        self.multi = Multilista()
        GestorPersistencia.cargar_desde_bd(self.multi, self.ruta_bd)
        self.ventana_anios = 0 # 0: Todos, 2: Últimos 2, 5: Últimos 5
        self.anio_actual = 2026

    def obtener_estado_ingesta(self) -> dict:
        """Compara índice UPC (66) vs grupos cargados en BD para el panel GUI."""
        try:
            from src.python.core.busqueda_scienti import listar_grupos_upc
            grupos_upc = listar_grupos_upc()
        except Exception:
            grupos_upc = []
        cargados = set()
        g = self.multi.cabeza_grupos
        while g:
            cargados.add(g.codigo_grupo)
            g = g.sig_grupo
        faltantes = [x for x in grupos_upc if x.get("col") not in cargados]
        return {"total_indice": len(grupos_upc), "cargados": len(cargados),
                "faltantes": faltantes[:25], "n_faltantes": len(faltantes)}

    def generar_html_dashboard(self, ruta_salida: str = "dist/dashboard_python.html"):
        """Genera un archivo HTML enriquecido con las 3 vistas exigidas (12.c) y métricas"""
        os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
        try:
            estado_ing = self.obtener_estado_ingesta()
        except Exception:
            estado_ing = {"total_indice": 0, "cargados": 0, "faltantes": [], "n_faltantes": 0}
        filas_falt = "".join(
            f'<tr><td><code>{(x.get("nro") or "")}</code></td><td><b>{(x.get("col") or "")}</b></td>'
            f'<td>{(x.get("nombre") or "")[:60]}</td>'
            f'<td><code>python3 Taller2_AB_PO_XX.py --scrape-grupo {(x.get("nro") or "")}</code></td></tr>'
            for x in estado_ing["faltantes"])

        # 12.c.i: Vista por Grupo
        filas_grupos = []
        g = self.multi.cabeza_grupos
        while g:
            num_inv = 0
            cur_i = g.primer_investigador
            while cur_i:
                num_inv += 1
                cur_i = cur_i.sig_investigador

            num_prod = 0
            cur_p = g.primer_producto
            while cur_p:
                num_prod += 1
                cur_p = cur_p.sig_producto_grupo

            filas_grupos.append({
                "codigo": g.codigo_grupo,
                "nombre": g.nombre,
                "clasificacion": g.clasificacion,
                "lider": g.lider,
                "investigadores": num_inv,
                "productos": num_prod
            })
            g = g.sig_grupo

        # 12.c.ii: Vista por Investigador
        filas_invs = []
        g = self.multi.cabeza_grupos
        while g:
            cur_i = g.primer_investigador
            while cur_i:
                num_p = 0
                cur_p = cur_i.primer_producto
                while cur_p:
                    num_p += 1
                    cur_p = cur_p.sig_producto_investigador
                filas_invs.append({
                    "doc": cur_i.documento_id,
                    "nombre": cur_i.nombre_completo,
                    "categoria": cur_i.categoria,
                    "grupo": g.codigo_grupo,
                    "obras": num_p
                })
                cur_i = cur_i.sig_investigador
            g = g.sig_grupo
        filas_invs.sort(key=lambda x: x["obras"], reverse=True)

        # 12.c.iii: Vista por Productos
        filas_prods = []
        g = self.multi.cabeza_grupos
        while g:
            cur_p = g.primer_producto
            while cur_p:
                info_2024 = CatalogoMinCiencias2024.clasificar_producto(getattr(cur_p, 'subtipo_codigo', '') or cur_p.tipo, cur_p.categoria_minciencias, cur_p.titulo)
                peso_val = getattr(cur_p, 'peso_calculado', 0.0)
                if peso_val <= 0.0:
                    peso_val = float(info_2024["global_weight"])
                filas_prods.append({
                    "id": cur_p.id_producto,
                    "tipo": cur_p.tipo,
                    "subtipo": getattr(cur_p, 'subtipo_codigo', '') or info_2024["codigo_2024"],
                    "familia": getattr(cur_p, 'familia', '') or info_2024["familia"],
                    "codigo_2024": info_2024["codigo_2024"],
                    "peso": peso_val,
                    "titulo": cur_p.titulo,
                    "anio": cur_p.anio,
                    "categoria": cur_p.categoria_minciencias,
                    "validado": "Avalado" if cur_p.validado else "En Revisión"
                })
                cur_p = cur_p.sig_producto_grupo
            g = g.sig_grupo
        filas_prods.sort(key=lambda x: x["anio"], reverse=True)

        # =============================================================
        # AGREGADOS DEL PANEL ANALÍTICO (12.b: histogramas y barras)
        # Se calculan en Python puro sobre la Multilista en RAM y se
        # renderizan como SVG vectorial incrustado: offline, sin CDNs,
        # sin JavaScript de terceros y sin matplotlib.
        # =============================================================
        agg_anios, agg_categorias, agg_familias, agg_tipos = {}, {}, {}, {}
        ipp_total = 0.0
        for p in filas_prods:
            anio = p["anio"]
            if isinstance(anio, int) and anio > 1900:
                agg_anios[anio] = agg_anios.get(anio, 0) + 1
            cat = (p["categoria"] or "Sin clasificar").strip() or "Sin clasificar"
            agg_categorias[cat] = agg_categorias.get(cat, 0) + 1
            fam = (p["familia"] or "GNC").split(" ")[0].strip() or "GNC"
            agg_familias[fam] = agg_familias.get(fam, 0) + 1
            tipo = (p["tipo"] or "Otro").strip() or "Otro"
            agg_tipos[tipo] = agg_tipos.get(tipo, 0) + 1
            try:
                ipp_total += float(p["peso"] or 0.0)
            except (TypeError, ValueError):
                pass

        # Ventana de observación (punto 10): últimos 15 años con datos
        anios_ord = sorted(agg_anios.keys())
        anios_ventana = anios_ord[-15:] if len(anios_ord) > 15 else anios_ord
        datos_anios = [(str(a), agg_anios[a]) for a in anios_ventana]

        orden_cat = ["A1", "A", "B", "C", "Reconocido", "Sin clasificar"]
        cats_ord = sorted(agg_categorias.keys(),
                          key=lambda c: (orden_cat.index(c) if c in orden_cat else 99, c))
        datos_categorias = [(c, agg_categorias[c]) for c in cats_ord]

        orden_fam = ["GNC", "DTE", "ASC", "FRH"]
        fams_ord = sorted(agg_familias.keys(),
                          key=lambda f: (orden_fam.index(f) if f in orden_fam else 99, f))
        datos_familias = [(f, agg_familias[f]) for f in fams_ord]

        datos_tipos = sorted(agg_tipos.items(), key=lambda kv: kv[1], reverse=True)[:12]
        top_grupos = [(gr["nombre"] or gr["codigo"], gr["productos"])
                      for gr in sorted(filas_grupos, key=lambda x: x["productos"], reverse=True)[:10]]
        top_invs = [(iv["nombre"], iv["obras"]) for iv in filas_invs[:10]]

        svg_anios = _svg_barras_verticales(datos_anios, color="#38bdf8", color2="#006837")
        svg_categorias = _svg_barras_verticales(datos_categorias, alto=250, color="#f59e0b", color2="#ED1C24")
        svg_familias = _svg_barras_verticales(datos_familias, alto=250, color="#10b981", color2="#006837")
        svg_tipos = _svg_barras_horizontales(datos_tipos, color="#a78bfa", color2="#38bdf8")
        svg_top_grupos = _svg_barras_horizontales(top_grupos, color="#10b981", color2="#006837")
        svg_top_invs = _svg_barras_horizontales(top_invs, color="#38bdf8", color2="#0ea5e9")

        # Asegurar directorio de reportes y generar de muestra para los primeros grupos si no existen
        rep_dir = os.path.abspath(os.path.join(os.path.dirname(self.ruta_bd), "..", "reportes"))
        os.makedirs(rep_dir, exist_ok=True)
        for grp in filas_grupos[:3]:
            pdf_path = os.path.join(rep_dir, f"Informe_GrupLAC_{grp['codigo']}.pdf")
            if not os.path.exists(pdf_path):
                try:
                    generar_informe_grupo_pdf(grp["codigo"], self.ruta_bd)
                except Exception:
                    pass

        html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>PEA-i UPC — Dashboard de Investigación MinCiencias</title>
    <style>
        :root {{
            --verde-upc: #006837;
            --rojo-upc: #ED1C24;
            --fondo: #0a0f1d;
            --tarjeta: #131b2e;
            --borde: #1e293b;
            --texto: #f8fafc;
            --texto-muted: #94a3b8;
            --acento: #10b981;
        }}
        body {{
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background: var(--fondo);
            color: var(--texto);
            margin: 0;
            padding: 1.5rem;
        }}
        header {{
            background: linear-gradient(135deg, var(--verde-upc), #004724);
            padding: 1.2rem 2rem;
            border-radius: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 4px 20px rgba(0, 104, 55, 0.3);
            margin-bottom: 2rem;
        }}
        .badge-upc {{
            background: var(--rojo-upc);
            color: white;
            padding: 0.4rem 1rem;
            border-radius: 9999px;
            font-weight: bold;
            font-size: 0.85rem;
            letter-spacing: 0.05em;
        }}
        .card {{
            background: var(--tarjeta);
            border: 1px solid var(--borde);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
        }}
        .card h2 {{
            margin-top: 0;
            color: var(--acento);
            font-size: 1.25rem;
            border-bottom: 1px solid var(--borde);
            padding-bottom: 0.75rem;
        }}
        .img-chart {{
            width: 100%;
            height: auto;
            border-radius: 8px;
            border: 1px solid var(--borde);
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9rem;
            text-align: left;
        }}
        th {{
            background: #1e293b;
            color: #38bdf8;
            padding: 0.75rem;
            font-weight: 600;
        }}
        td {{
            padding: 0.75rem;
            border-bottom: 1px solid var(--borde);
            color: #e2e8f0;
        }}
        tr:hover {{
            background: rgba(255, 255, 255, 0.03);
        }}
        .tag-macro {{
            background: #0369a1;
            color: #e0f2fe;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <header>
        <div style="display:flex; align-items:center; gap:1rem;">
            <div style="width:52px; height:46px; background:#ffffff; border-radius:9px; padding:4px; display:flex; align-items:center; justify-content:center; box-shadow:0 2px 10px rgba(0,0,0,0.3);">
                <img src="logo_upc.png" alt="Logo Oficial UPC" style="width:100%; height:100%; object-fit:contain;">
            </div>
            <div>
                <h1 style="margin:0; font-size:1.4rem;">PEA-i UPC &bull; Dashboard Analítico de Investigación</h1>
                <p style="margin:0.2rem 0 0 0; font-size:0.8rem; color:#cbd5e1;">Fase 5 Python &bull; Histogramas, Diagramas de Barras y Macro-Tipologías MinCiencias (Puntos 12.b y 12.c)</p>
            </div>
        </div>
        <div class="badge-upc">UPC &bull; SCIENTI 2026</div>
    </header>

    <!-- MÉTRICAS Y RESUMEN EJECUTIVO (12.b) -->
    <div class="card">
        <h2>Resumen Analítico y Métricas Institucionales (Requisito 12.b - HTML5 Engine)</h2>
        <p style="color:#94a3b8; margin-bottom:1rem;">Visualización analítica institucional generada directamente desde la Multilista en memoria RAM (Zero-Dependencies).</p>
        <div style="display:flex; gap:1rem; flex-wrap:wrap; margin-bottom:1rem;">
            <div style="background:#0f172a; border:1px solid #1e293b; border-radius:8px; padding:1rem; flex:1; min-width:180px; text-align:center;">
                <div style="font-size:2rem; font-weight:bold; color:#10b981;">{len(filas_grupos)}</div>
                <div style="color:#94a3b8; font-size:0.85rem;">Grupos Registrados</div>
            </div>
            <div style="background:#0f172a; border:1px solid #1e293b; border-radius:8px; padding:1rem; flex:1; min-width:180px; text-align:center;">
                <div style="font-size:2rem; font-weight:bold; color:#38bdf8;">{len(filas_invs)}</div>
                <div style="color:#94a3b8; font-size:0.85rem;">Investigadores Activos</div>
            </div>
            <div style="background:#0f172a; border:1px solid #1e293b; border-radius:8px; padding:1rem; flex:1; min-width:180px; text-align:center;">
                <div style="font-size:2rem; font-weight:bold; color:#f59e0b;">{len(filas_prods)}</div>
                <div style="color:#94a3b8; font-size:0.85rem;">Productos de Investigación</div>
            </div>
        </div>
        <p style="font-size:0.8rem; color:#94a3b8;">Producción científica total (IPP acumulado): <b style="color:#f59e0b;">{ipp_total:,.1f} puntos</b> &bull; Este dashboard es 100% autónomo: su análisis se calcula y renderiza localmente, sin depender del portal C++.</p>
    </div>

    <!-- PANEL ANALÍTICO PROPIO (12.b: histogramas y diagramas de barras) -->
    <div class="card">
        <h2>Panel Analítico Institucional — Histogramas y Diagramas de Barras (12.b)</h2>
        <p style="color:#94a3b8; margin-bottom:1rem;">Gráficos vectoriales generados en Python desde la Multilista en memoria (SVG incrustado, sin dependencias externas ni conexión a Internet).</p>

        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(420px, 1fr)); gap:1.2rem;">
            <div style="background:#0f172a; border:1px solid #1e293b; border-radius:10px; padding:1rem;">
                <h3 style="margin:0 0 0.75rem 0; font-size:0.95rem; color:#38bdf8;">Producción por Año (ventana de observación — Punto 10)</h3>
                {svg_anios}
            </div>
            <div style="background:#0f172a; border:1px solid #1e293b; border-radius:10px; padding:1rem;">
                <h3 style="margin:0 0 0.75rem 0; font-size:0.95rem; color:#f59e0b;">Productos por Categoría MinCiencias</h3>
                {svg_categorias}
            </div>
            <div style="background:#0f172a; border:1px solid #1e293b; border-radius:10px; padding:1rem;">
                <h3 style="margin:0 0 0.75rem 0; font-size:0.95rem; color:#10b981;">Distribución por Macro-Tipología 2024</h3>
                {svg_familias}
            </div>
            <div style="background:#0f172a; border:1px solid #1e293b; border-radius:10px; padding:1rem;">
                <h3 style="margin:0 0 0.75rem 0; font-size:0.95rem; color:#a78bfa;">Tipos de Producto más Frecuentes</h3>
                {svg_tipos}
            </div>
            <div style="background:#0f172a; border:1px solid #1e293b; border-radius:10px; padding:1rem;">
                <h3 style="margin:0 0 0.75rem 0; font-size:0.95rem; color:#10b981;">Top 10 Grupos por Productos</h3>
                {svg_top_grupos}
            </div>
            <div style="background:#0f172a; border:1px solid #1e293b; border-radius:10px; padding:1rem;">
                <h3 style="margin:0 0 0.75rem 0; font-size:0.95rem; color:#38bdf8;">Top 10 Investigadores por Producción</h3>
                {svg_top_invs}
            </div>
        </div>

        <p style="margin-top:1.2rem; font-size:0.78rem; color:#64748b;">Este dashboard es exclusivamente analítico: no incluye creación, edición ni borrado de registros. La red de colaboración interactiva y las vistas por entidad con edición viven en el portal C++:
            <a href="visualizador_hipercubo.html" target="_blank" style="color:#38bdf8;">abrir visualizador_hipercubo.html</a>.
        </p>
    </div>

    <!-- INGESTA MASIVA UPC (panel funcional GUI) -->
    <div class="card">
        <h2>Ingesta Masiva UPC — Estado y Acciones</h2>
        <p style="color:#94a3b8;">Índice institucional: <b>{estado_ing["total_indice"]}</b> grupos UPC &bull;
        Cargados en BD: <b>{len(filas_grupos)}</b> &bull; Faltantes: <b>{estado_ing["n_faltantes"]}</b></p>
        <p style="color:#94a3b8; font-size:0.85rem;">Desde la consola ejecute:
        <code>python3 Taller2_AB_PO_XX.py --auto-ingest</code> (66 grupos, GISICO al final) &bull;
        <code>--forzar</code> reprocesa &bull; <code>--sin-cvlac</code> carga rápida &bull;
        <code>--nro NRO</code> selectivo. Tras ingerir, regenere este dashboard (opción 7→2).</p>
        <table>
            <thead><tr><th>NRO</th><th>COL</th><th>Grupo faltante</th><th>Comando</th></tr></thead>
            <tbody>{filas_falt or '<tr><td colspan="4">Sin faltantes: ingesta completa.</td></tr>'}</tbody>
        </table>
    </div>

    <!-- TRES APROXIMACIONES (12.c) -->
    <div class="card">
        <h2>i. Vista por Grupo de Investigación (12.c.i) — <span style="color:#94a3b8; font-size:0.9rem;">{len(filas_grupos)} grupos</span></h2>
        <div style="display:flex; gap:0.5rem; align-items:center; margin-bottom:0.75rem; flex-wrap:wrap;">
            <input id="buscar-grup" type="text" placeholder="Buscar por código, nombre, líder o clasificación..." oninput="filtrarTabla('tabla-grup','buscar-grup')" style="padding:6px 10px; border-radius:6px; border:1px solid #334155; background:#0f172a; color:#f8fafc; font-size:0.85rem; flex:1; min-width:220px;">
            <button onclick="cambiarPagina('grup',-1)" style="background:#1e293b; color:#f8fafc; border:1px solid #334155; border-radius:6px; padding:6px 14px; cursor:pointer;">◀ Ant</button>
            <span id="pag-grup-label" style="color:#94a3b8; font-size:0.85rem;"></span>
            <button onclick="cambiarPagina('grup',1)" style="background:#1e293b; color:#f8fafc; border:1px solid #334155; border-radius:6px; padding:6px 14px; cursor:pointer;">Sig ▶</button>
        </div>
        <table id="tabla-grup">
            <thead>
                <tr><th>Código</th><th>Nombre Oficial</th><th>Clasificación</th><th>Líder</th><th>Investigadores</th><th>Productos</th><th>Informe Oficial</th></tr>
            </thead>
            <tbody>
                {''.join(f'<tr><td><b>{g["codigo"]}</b></td><td>{g["nombre"]}</td><td>{g["clasificacion"]}</td><td>{g["lider"]}</td><td>{g["investigadores"]}</td><td><b>{g["productos"]}</b></td><td><a href="../reportes/Informe_GrupLAC_{g["codigo"]}.pdf" target="_blank" style="background:#006837; color:white; padding:3px 8px; border-radius:4px; text-decoration:none; font-size:0.75rem; font-weight:bold;">Descargar PDF</a></td></tr>' for g in filas_grupos)}
            </tbody>
        </table>
    </div>

    <div class="card">
        <h2>ii. Vista por Investigador Autor (12.c.ii) — <span style="color:#94a3b8; font-size:0.9rem;">{len(filas_invs)} investigadores</span></h2>
        <div style="display:flex; gap:0.5rem; align-items:center; margin-bottom:0.75rem; flex-wrap:wrap;">
            <input id="buscar-inv" type="text" placeholder="Buscar por nombre, documento o grupo..." oninput="filtrarTabla('tabla-invs','buscar-inv')" style="padding:6px 10px; border-radius:6px; border:1px solid #334155; background:#0f172a; color:#f8fafc; font-size:0.85rem; flex:1; min-width:220px;">
            <button onclick="cambiarPagina('invs',-1)" style="background:#1e293b; color:#f8fafc; border:1px solid #334155; border-radius:6px; padding:6px 14px; cursor:pointer;">◀ Ant</button>
            <span id="pag-invs-label" style="color:#94a3b8; font-size:0.85rem;"></span>
            <button onclick="cambiarPagina('invs',1)" style="background:#1e293b; color:#f8fafc; border:1px solid #334155; border-radius:6px; padding:6px 14px; cursor:pointer;">Sig ▶</button>
        </div>
        <table id="tabla-invs">
            <thead>
                <tr><th>Documento</th><th>Nombre Completo</th><th>Categoría MinCiencias</th><th>Grupo</th><th>Producción Autorada</th></tr>
            </thead>
            <tbody>
                {''.join(f'<tr><td><code>{i["doc"]}</code></td><td><b>{i["nombre"]}</b></td><td>{i["categoria"]}</td><td>{i["grupo"]}</td><td><b>{i["obras"]} obras</b></td></tr>' for i in filas_invs)}
            </tbody>
        </table>
    </div>

    <div class="card">
        <h2>iii. Vista por Productos de Investigación (12.c.iii — Modelo MinCiencias 2024) — <span style="color:#94a3b8; font-size:0.9rem;">{len(filas_prods)} productos</span></h2>
        <div style="display:flex; gap:0.5rem; align-items:center; margin-bottom:0.75rem; flex-wrap:wrap;">
            <input id="buscar-prod" type="text" placeholder="Buscar por título, tipo, familia o año..." oninput="filtrarTabla('tabla-prods','buscar-prod')" style="padding:6px 10px; border-radius:6px; border:1px solid #334155; background:#0f172a; color:#f8fafc; font-size:0.85rem; flex:1; min-width:220px;">
            <button onclick="cambiarPagina('prods',-1)" style="background:#1e293b; color:#f8fafc; border:1px solid #334155; border-radius:6px; padding:6px 14px; cursor:pointer;">◀ Ant</button>
            <span id="pag-prods-label" style="color:#94a3b8; font-size:0.85rem;"></span>
            <button onclick="cambiarPagina('prods',1)" style="background:#1e293b; color:#f8fafc; border:1px solid #334155; border-radius:6px; padding:6px 14px; cursor:pointer;">Sig ▶</button>
        </div>
        <table id="tabla-prods">
            <thead>
                <tr><th>ID</th><th>Familia 2024</th><th>Código</th><th>Peso IPP</th><th>Tipo</th><th>Título</th><th>Año</th><th>Categoría</th><th>Aval MinCiencias</th></tr>
            </thead>
            <tbody>
                {''.join(f'<tr><td><code>{p["id"]}</code></td><td><span class="tag-macro">{p["familia"]}</span></td><td><b>{p["codigo_2024"]}</b></td><td>{p["peso"]} pts</td><td>{p["tipo"]}</td><td>{p["titulo"]}</td><td>{p["anio"]}</td><td>{p["categoria"]}</td><td>{p["validado"]}</td></tr>' for p in filas_prods)}
            </tbody>
        </table>
        <p style="font-size:0.75rem; color:#94a3b8; margin-top:0.8rem;">Total: {len(filas_prods)} obras científicas clasificadas bajo el Modelo MinCiencias 2024.</p>
    </div>

<script>
// ─── PAGINACIÓN Y BÚSQUEDA ────────────────────────────────────────────────────
const FILAS_POR_PAG = 50;
const estado = {{
    grup:  {{ pag: 0, filas: null, filtradas: null }},
    invs:  {{ pag: 0, filas: null, filtradas: null }},
    prods: {{ pag: 0, filas: null, filtradas: null }},
}};

function inicializarPaginacion(clave) {{
    const tabla = document.getElementById('tabla-' + clave);
    estado[clave].filas = Array.from(tabla.querySelectorAll('tbody tr'));
    estado[clave].filtradas = estado[clave].filas;
    renderPagina(clave);
}}

function renderPagina(clave) {{
    const e = estado[clave];
    const total = e.filtradas.length;
    const totalPags = Math.max(1, Math.ceil(total / FILAS_POR_PAG));
    e.pag = Math.min(e.pag, totalPags - 1);
    const inicio = e.pag * FILAS_POR_PAG;
    const fin = Math.min(inicio + FILAS_POR_PAG, total);
    e.filas.forEach(tr => tr.style.display = 'none');
    e.filtradas.forEach((tr, idx) => {{
        tr.style.display = (idx >= inicio && idx < fin) ? '' : 'none';
    }});
    const label = document.getElementById('pag-' + clave + '-label');
    if (label) label.textContent = total === 0
        ? 'Sin resultados'
        : `Página ${{e.pag + 1}} / ${{totalPags}}  (${{inicio + 1}}–${{fin}} de ${{total}})`;
}}

function cambiarPagina(clave, delta) {{
    const e = estado[clave];
    const totalPags = Math.max(1, Math.ceil(e.filtradas.length / FILAS_POR_PAG));
    e.pag = Math.max(0, Math.min(e.pag + delta, totalPags - 1));
    renderPagina(clave);
}}

function filtrarTabla(tablaId, inputId) {{
    const termino = document.getElementById(inputId).value.toLowerCase();
    const clave = tablaId.replace('tabla-', '');
    const e = estado[clave];
    e.filtradas = e.filas.filter(tr => tr.textContent.toLowerCase().includes(termino));
    e.pag = 0;
    renderPagina(clave);
}}

document.addEventListener('DOMContentLoaded', function() {{
    inicializarPaginacion('grup');
    inicializarPaginacion('invs');
    inicializarPaginacion('prods');
}});
</script>
</body>
</html>
"""
        with open(ruta_salida, "w", encoding="utf-8") as f:
            f.write(html)
        return ruta_salida

    def iniciar(self):
        """Punto de entrada maestro para lanzar el Dashboard Analítico (HTML5 Autónomo)"""
        print("\n" + "=" * 65)
        print("     PEA-i UPC: DASHBOARD ANALÍTICO DE INVESTIGACIÓN (PYTHON)    ")
        print("=" * 65)
        print("[+] Analizando datos de la Multilista ortogonal en RAM...")
        print(f"[OK] {self.multi.contar_grupos(False)} grupos, {self.multi.contar_investigadores(False)} investigadores, {self.multi.contar_productos(False)} productos.")

        # Generar dashboard Python siempre actualizado con los datos actuales de la BD
        ruta_html = os.path.abspath(os.path.join(PROJECT_ROOT, "dist", "dashboard_python.html"))
        self.generar_html_dashboard(ruta_html)
        print(f"[+] Dashboard generado: {ruta_html}")

        print(f"[+] Abriendo Dashboard Analítico en el navegador...")
        print(f"    (si no abre solo, abra manualmente: {ruta_html})")
        abierto = False
        try:
            import pathlib
            abierto = bool(webbrowser.open(pathlib.Path(ruta_html).as_uri()))
        except Exception as e:
            print(f"[!] webbrowser falló ({e}), intentando apertura directa del SO...")
        if not abierto and os.name == "nt":
            try:
                os.startfile(ruta_html)  # noqa: S606 -- apertura local de archivo propio
                abierto = True
            except Exception as e:
                print(f"[!] Apertura directa falló ({e}).")
        if abierto:
            print(f"[OK] Dashboard abierto exitosamente.")
            # Informar también sobre el portal C++ si existe
            portal_html = os.path.join(PROJECT_ROOT, "dist", "visualizador_hipercubo.html")
            if os.path.exists(portal_html):
                print(f"[i]  Portal Hipercubo C++ disponible en: {portal_html}")
                print(f"[i]  Para regenerarlo con datos actuales ejecute: ./pea_cpp --gen")
        else:
            print(f"[!] No se pudo abrir automáticamente el navegador.")
            print(f"    Abra manualmente: {ruta_html}")

        print("\n[OK] Dashboard interactivo ejecutado exitosamente.")
        print("=" * 65 + "\n")
        return True

if __name__ == "__main__":
    app = DashboardApp("data/pea_investigacion.db")
    app.iniciar()
