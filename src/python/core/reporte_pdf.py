#!/usr/bin/env python3
"""
=====================================================================
PEA-i: GENERADOR DE INFORMES PDF INSTITUCIONALES (ESTILO GRUPLAC)
Universidad Popular del Cesar — Facultad de Ingeniería y Tecnológicas
Docente: Ing. Adith Bismarck Pérez Orozco
=====================================================================
Genera un informe técnico formal en formato PDF para cualquier grupo
de investigación de la Universidad Popular del Cesar con ReportLab.
Incluye:
  1. Membrete institucional con paleta oficial UPC (#006837 y #ED1C24).
  2. Ficha técnica completa del grupo y su liderazgo MinCiencias.
  3. Balance consolidado bajo el Modelo MinCiencias 2024 (5 Familias e IPP).
  4. Directorio de integrantes e investigadores adscritos.
  5. Catálogo discriminado de productos científicos con estado de validación.
=====================================================================
"""

import os
import sys
import sqlite3
from datetime import datetime
from typing import Dict, List, Any, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
    PageBreak,
    HRFlowable
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.python.core.catalogo_2024 import CatalogoMinCiencias2024

# Colores institucionales UPC y corporativos
COLOR_UPC_VERDE = colors.HexColor("#006837")
COLOR_UPC_ROJO = colors.HexColor("#ED1C24")
COLOR_AZUL_CORP = colors.HexColor("#1e3a5f")
COLOR_GRIS_FONDO = colors.HexColor("#f8fafc")
COLOR_GRIS_LINEA = colors.HexColor("#cbd5e1")
COLOR_TEXTO = colors.HexColor("#1e293b")
COLOR_SUBTEXTO = colors.HexColor("#64748b")

# Estilos tipográficos
_FONT = "Helvetica"
_FONT_BOLD = "Helvetica-Bold"

STYLE_TITULO = ParagraphStyle(
    "TituloReporte",
    fontName=_FONT_BOLD,
    fontSize=14,
    leading=18,
    textColor=COLOR_UPC_VERDE,
    spaceAfter=2
)

STYLE_SUBTITULO = ParagraphStyle(
    "SubtituloReporte",
    fontName=_FONT,
    fontSize=8.5,
    leading=11,
    textColor=COLOR_SUBTEXTO,
    spaceAfter=8
)

STYLE_SECCION = ParagraphStyle(
    "SeccionHeader",
    fontName=_FONT_BOLD,
    fontSize=10,
    leading=13,
    textColor=colors.white,
    backColor=COLOR_UPC_VERDE,
    borderPadding=(4, 6),
    spaceBefore=10,
    spaceAfter=5
)

STYLE_ETIQUETA = ParagraphStyle(
    "CeldaEtiqueta",
    fontName=_FONT_BOLD,
    fontSize=8,
    leading=10,
    textColor=COLOR_AZUL_CORP
)

STYLE_VALOR = ParagraphStyle(
    "CeldaValor",
    fontName=_FONT,
    fontSize=8,
    leading=10,
    textColor=COLOR_TEXTO
)

STYLE_TABLA_HEAD = ParagraphStyle(
    "TablaHead",
    fontName=_FONT_BOLD,
    fontSize=8,
    leading=10,
    textColor=colors.white
)

def _p(txt: Any, estilo: ParagraphStyle) -> Paragraph:
    return Paragraph(str(txt if txt is not None else ""), estilo)

def _cabecera_pie(canvas, doc):
    canvas.saveState()
    ancho, alto = A4

    # Barra superior verde institucional
    canvas.setFillColor(COLOR_UPC_VERDE)
    canvas.rect(0, alto - 1.0 * cm, ancho, 1.0 * cm, stroke=0, fill=1)

    # Acento rojo UPC
    canvas.setFillColor(COLOR_UPC_ROJO)
    canvas.rect(0, alto - 1.05 * cm, ancho, 0.05 * cm, stroke=0, fill=1)

    canvas.setFillColor(colors.white)
    canvas.setFont(_FONT_BOLD, 8)
    canvas.drawString(1.5 * cm, alto - 0.7 * cm, "UNIVERSIDAD POPULAR DEL CESAR  ·  SISTEMA PEA-i (SCIENTI / MINCIENCIAS)")
    canvas.setFont(_FONT, 8)
    canvas.drawRightString(ancho - 1.5 * cm, alto - 0.7 * cm, "Modelo MinCiencias 2024")

    # Pie de página
    canvas.setFillColor(COLOR_SUBTEXTO)
    canvas.setFont(_FONT, 7.5)
    canvas.drawString(1.5 * cm, 0.8 * cm, f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} | Grupo de Investigación Oficial")
    canvas.drawRightString(ancho - 1.5 * cm, 0.8 * cm, f"Página {doc.page}")

    canvas.setStrokeColor(COLOR_GRIS_LINEA)
    canvas.setLineWidth(0.5)
    canvas.line(1.5 * cm, 1.1 * cm, ancho - 1.5 * cm, 1.1 * cm)

    canvas.restoreState()

def generar_informe_grupo_pdf(codigo_grupo: str, ruta_bd: str = "data/pea_investigacion.db", ruta_salida: str = None) -> str:
    """
    Construye y emite el archivo PDF institucional para un grupo de investigación.
    Retorna la ruta absoluta del archivo PDF generado.
    """
    if not os.path.isabs(ruta_bd):
        ruta_bd = os.path.join(PROJECT_ROOT, ruta_bd)

    conn = sqlite3.connect(ruta_bd)
    cur = conn.cursor()

    # 1. Obtener Datos del Grupo
    cur.execute("SELECT codigo_grupo, nombre, clasificacion, area_conocimiento, lider, anio_creacion, activo FROM Grupos WHERE codigo_grupo = ?", (codigo_grupo,))
    g_row = cur.fetchone()
    if not g_row:
        # Búsqueda por coincidencia
        cur.execute("SELECT codigo_grupo, nombre, clasificacion, area_conocimiento, lider, anio_creacion, activo FROM Grupos WHERE nombre LIKE ? LIMIT 1", (f"%{codigo_grupo}%",))
        g_row = cur.fetchone()
        if not g_row:
            conn.close()
            raise ValueError(f"Grupo con código o nombre '{codigo_grupo}' no encontrado en la base de datos.")

    cod_g, nom_g, clas_g, area_g, lid_g, anio_g, act_g = g_row

    # 2. Obtener Integrantes
    cur.execute("SELECT documento_id, nombre_completo, categoria, formacion_academica, activo FROM Investigadores WHERE codigo_grupo = ? ORDER BY nombre_completo", (cod_g,))
    investigadores = cur.fetchall()

    # 3. Obtener Productos
    cur.execute("SELECT id_producto, tipo, titulo, anio, categoria_minciencias, validado, id_investigador, activo FROM Productos WHERE codigo_grupo = ? ORDER BY anio DESC, titulo ASC", (cod_g,))
    productos = cur.fetchall()
    conn.close()

    # 4. Calcular Métricas Modelo 2024
    conteos_2024 = {"GNC": 0, "DTI": 0, "ASC": 0, "DPC": 0, "FRH": 0}
    puntos_2024 = {"GNC": 0, "DTI": 0, "ASC": 0, "DPC": 0, "FRH": 0}
    total_ipp = 0
    total_validados = 0

    productos_enriquecidos = []
    for p in productos:
        pid, tipo, tit, anio, cat_m, val, id_inv, act = p
        clas_info = CatalogoMinCiencias2024.clasificar_producto(tipo, cat_m, tit)
        fam = clas_info["familia"]
        pts = clas_info["global_weight"] if val else 0
        conteos_2024[fam] = conteos_2024.get(fam, 0) + 1
        puntos_2024[fam] = puntos_2024.get(fam, 0) + pts
        total_ipp += pts
        if val:
            total_validados += 1
        productos_enriquecidos.append((pid, tipo, tit, anio, cat_m, val, id_inv, fam, pts, clas_info["codigo_2024"]))

    # Ruta de salida
    if not ruta_salida:
        dir_reportes = os.path.join(PROJECT_ROOT, "reportes")
        os.makedirs(dir_reportes, exist_ok=True)
        nombre_limpio = "".join(c for c in cod_g if c.isalnum() or c in ("-", "_"))
        ruta_salida = os.path.join(dir_reportes, f"Informe_GrupLAC_{nombre_limpio}.pdf")

    # Construcción del Documento ReportLab
    doc = SimpleDocTemplate(
        ruta_salida,
        pagesize=A4,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.8 * cm,
        bottomMargin=1.8 * cm
    )

    historia = []

    # Encabezado
    historia.append(_p("INFORME OFICIAL DE GRUPO DE INVESTIGACIÓN", STYLE_TITULO))
    historia.append(_p(f"{nom_g} ({cod_g}) · Modelo MinCiencias Convocatoria 957 de 2024", STYLE_SUBTITULO))
    historia.append(HRFlowable(width="100%", thickness=1, color=COLOR_UPC_VERDE, spaceBefore=0, spaceAfter=8))

    # Sección 1: Ficha Técnica
    historia.append(_p("1. FICHA TÉCNICA Y DATOS GENERALES", STYLE_SECCION))

    datos_basicos = [
        [_p("Código GrupLAC:", STYLE_ETIQUETA), _p(cod_g, STYLE_VALOR), _p("Categoría MinCiencias:", STYLE_ETIQUETA), _p(f"Categoría {clas_g}", STYLE_VALOR)],
        [_p("Líder del Grupo:", STYLE_ETIQUETA), _p(lid_g, STYLE_VALOR), _p("Año de Creación:", STYLE_ETIQUETA), _p(str(anio_g), STYLE_VALOR)],
        [_p("Área de Conocimiento:", STYLE_ETIQUETA), _p(area_g, STYLE_VALOR), _p("Total Integrantes:", STYLE_ETIQUETA), _p(str(len(investigadores)), STYLE_VALOR)],
        [_p("Institución Avaladora:", STYLE_ETIQUETA), _p("Universidad Popular del Cesar (UPC)", STYLE_VALOR), _p("Total Productos:", STYLE_ETIQUETA), _p(f"{len(productos)} ({total_validados} con aval)", STYLE_VALOR)]
    ]
    t_basicos = Table(datos_basicos, colWidths=[3.2 * cm, 5.8 * cm, 3.5 * cm, 5.5 * cm])
    t_basicos.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COLOR_GRIS_FONDO),
        ("GRID", (0, 0), (-1, -1), 0.5, COLOR_GRIS_LINEA),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    historia.append(t_basicos)
    historia.append(Spacer(1, 8))

    # Sección 2: Balance Modelo MinCiencias 2024
    historia.append(_p("2. BALANCE CONSOLIDADO — MODELO MINCIENCIAS 2024 (5 FAMILIAS E IPP)", STYLE_SECCION))

    filas_2024 = [
        [_p("Familia MinCiencias 2024", STYLE_TABLA_HEAD), _p("Descripción Oficial", STYLE_TABLA_HEAD), _p("Productos", STYLE_TABLA_HEAD), _p("Puntos IPP", STYLE_TABLA_HEAD)],
        [_p("GNC", STYLE_ETIQUETA), _p("Generación de Nuevo Conocimiento (Artículos, Libros, Patentes)", STYLE_VALOR), _p(str(conteos_2024["GNC"]), STYLE_VALOR), _p(f"{puntos_2024['GNC']} pts", STYLE_VALOR)],
        [_p("DTI", STYLE_ETIQUETA), _p("Desarrollo Tecnológico e Innovación (Software, Prototipos)", STYLE_VALOR), _p(str(conteos_2024["DTI"]), STYLE_VALOR), _p(f"{puntos_2024['DTI']} pts", STYLE_VALOR)],
        [_p("ASC", STYLE_ETIQUETA), _p("Apropiación Social del Conocimiento (Ciencia Comunitaria)", STYLE_VALOR), _p(str(conteos_2024["ASC"]), STYLE_VALOR), _p(f"{puntos_2024['ASC']} pts", STYLE_VALOR)],
        [_p("DPC", STYLE_ETIQUETA), _p("Divulgación Pública de la Ciencia (Ponencias, Eventos)", STYLE_VALOR), _p(str(conteos_2024["DPC"]), STYLE_VALOR), _p(f"{puntos_2024['DPC']} pts", STYLE_VALOR)],
        [_p("FRH", STYLE_ETIQUETA), _p("Formación de Recurso Humano (Tesis, Ondas APO)", STYLE_VALOR), _p(str(conteos_2024["FRH"]), STYLE_VALOR), _p(f"{puntos_2024['FRH']} pts", STYLE_VALOR)],
        [_p("TOTAL IPP", STYLE_TABLA_HEAD), _p("Índice de Producción Ponderada Acumulada", STYLE_TABLA_HEAD), _p(str(len(productos)), STYLE_TABLA_HEAD), _p(f"{total_ipp} pts", STYLE_TABLA_HEAD)],
    ]
    t_2024 = Table(filas_2024, colWidths=[2.5 * cm, 10.5 * cm, 2.5 * cm, 2.5 * cm])
    t_2024.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_AZUL_CORP),
        ("BACKGROUND", (0, -1), (-1, -1), COLOR_UPC_VERDE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, COLOR_GRIS_FONDO]),
        ("GRID", (0, 0), (-1, -1), 0.5, COLOR_GRIS_LINEA),
        ("ALIGN", (2, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    historia.append(t_2024)
    historia.append(Spacer(1, 8))

    # Sección 3: Investigadores
    historia.append(_p(f"3. CUERPO DE INVESTIGADORES E INTEGRANTES ({len(investigadores)})", STYLE_SECCION))

    filas_inv = [
        [_p("Documento / Cód.", STYLE_TABLA_HEAD), _p("Nombre Completo del Investigador", STYLE_TABLA_HEAD), _p("Escalafón MinCiencias", STYLE_TABLA_HEAD), _p("Formación Académica", STYLE_TABLA_HEAD)]
    ]
    for inv in investigadores[:35]:  # Muestra representativa para formato formal
        doc_i, nom_i, cat_i, form_i, _ = inv
        filas_inv.append([_p(doc_i, STYLE_VALOR), _p(nom_i, STYLE_ETIQUETA), _p(cat_i, STYLE_VALOR), _p(form_i, STYLE_VALOR)])

    if len(investigadores) > 35:
        filas_inv.append([_p("...", STYLE_VALOR), _p(f"(... y {len(investigadores) - 35} integrantes adicionales registrados en la multilista ...)", STYLE_VALOR), _p("-", STYLE_VALOR), _p("-", STYLE_VALOR)])

    t_inv = Table(filas_inv, colWidths=[3.2 * cm, 6.8 * cm, 3.5 * cm, 4.5 * cm])
    t_inv.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_UPC_VERDE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COLOR_GRIS_FONDO]),
        ("GRID", (0, 0), (-1, -1), 0.5, COLOR_GRIS_LINEA),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    historia.append(t_inv)
    historia.append(Spacer(1, 8))

    # Sección 4: Producción Científica
    historia.append(_p(f"4. CATÁLOGO DE PRODUCCIÓN CIENTÍFICA (MUESTRA DE REGISTROS)", STYLE_SECCION))

    filas_prod = [
        [_p("Año", STYLE_TABLA_HEAD), _p("Familia / Cód.", STYLE_TABLA_HEAD), _p("Título del Producto Científico", STYLE_TABLA_HEAD), _p("Tipo", STYLE_TABLA_HEAD), _p("Aval", STYLE_TABLA_HEAD), _p("IPP", STYLE_TABLA_HEAD)]
    ]

    for p in productos_enriquecidos[:50]:  # Mostrar los primeros 50 productos más recientes
        _, tipo, tit, anio, _, val, _, fam, pts, cod_2024 = p
        aval_str = "Aprobado" if val else "Revisión"
        tit_trunc = tit[:85] + ("..." if len(tit) > 85 else "")
        filas_prod.append([
            _p(str(anio), STYLE_VALOR),
            _p(f"{fam}-{cod_2024}", STYLE_ETIQUETA),
            _p(tit_trunc, STYLE_VALOR),
            _p(tipo, STYLE_VALOR),
            _p(aval_str, STYLE_VALOR),
            _p(f"{pts} pts", STYLE_VALOR)
        ])

    if len(productos_enriquecidos) > 50:
        filas_prod.append([
            _p("...", STYLE_VALOR),
            _p("...", STYLE_VALOR),
            _p(f"(... y {len(productos_enriquecidos) - 50} productos adicionales en la base de datos institucional ...)", STYLE_VALOR),
            _p("...", STYLE_VALOR),
            _p("...", STYLE_VALOR),
            _p("...", STYLE_VALOR)
        ])

    t_prod = Table(filas_prod, colWidths=[1.3 * cm, 2.5 * cm, 9.2 * cm, 2.3 * cm, 1.4 * cm, 1.3 * cm])
    t_prod.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_AZUL_CORP),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COLOR_GRIS_FONDO]),
        ("GRID", (0, 0), (-1, -1), 0.5, COLOR_GRIS_LINEA),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
    ]))
    historia.append(t_prod)

    # Generar PDF
    doc.build(historia, onFirstPage=_cabecera_pie, onLaterPages=_cabecera_pie)
    return ruta_salida

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generador de Informes PDF GrupLAC UPC")
    parser.add_argument("codigo", nargs="?", default="COL0002099", help="Código GrupLAC o nombre del grupo")
    parser.add_argument("-o", "--output", default=None, help="Ruta de salida del PDF")
    args = parser.parse_args()

    pdf_path = generar_informe_grupo_pdf(args.codigo, ruta_salida=args.output)
    print(f"[OK] Informe PDF generado exitosamente en: {pdf_path}")
