"""
Generador del Documento Word Oficial de Especificación Técnica:
'Documentacion_Tecnica_GrupoXX.docx'
Cumple con la totalidad de los requerimientos y recomendaciones del Taller 2 (Docente: Ing. Adith Pérez)
"""
import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

OUTPUT_FILE = "Documentacion_Tecnica_GrupoXX.docx"

# Colores Institucionales UPC
HEX_VERDE_UPC = "006837"
HEX_ROJO_UPC = "ED1C24"
HEX_SUBTITULO = "2B6CB0"
HEX_GRIS_FONDO = "F8F9FA"
HEX_GRIS_CLARO = "E2E8F0"
COLOR_VERDE = RGBColor(0x00, 0x68, 0x37)
COLOR_ROJO = RGBColor(0xED, 0x1C, 0x24)
COLOR_TEXTO = RGBColor(0x1A, 0x20, 0x2C)
COLOR_SUBTITULO = RGBColor(0x2B, 0x6C, 0xB0)

def set_cell_background(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def add_callout(doc, title, text, border_color_hex="006837", bg_color_hex="F0FFF4"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    tbl.columns[0].width = Inches(6.5)
    
    cell = tbl.cell(0, 0)
    set_cell_background(cell, bg_color_hex)
    set_cell_margins(cell, top=140, bottom=140, left=200, right=180)
    
    # Borde izquierdo grueso
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(f'<w:tcBorders {nsdecls("w")}><w:left w:val="single" w:sz="36" w:space="0" w:color="{border_color_hex}"/><w:top w:val="none"/><w:right w:val="none"/><w:bottom w:val="none"/></w:tcBorders>')
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(4)
    run_t = p.add_run(f"📌 {title}\n")
    run_t.font.name = "Segoe UI"
    run_t.font.size = Pt(10.5)
    run_t.font.bold = True
    run_t.font.color.rgb = COLOR_VERDE if border_color_hex == "006837" else COLOR_ROJO
    
    run_b = p.add_run(text)
    run_b.font.name = "Segoe UI"
    run_b.font.size = Pt(9.5)
    run_b.font.color.rgb = COLOR_TEXTO
    
    doc.add_paragraph().paragraph_format.space_after = Pt(6)

def format_table(tbl, col_widths, headers, data, header_bg=HEX_VERDE_UPC):
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    
    # Headers
    hdr_cells = tbl.rows[0].cells
    for i, header_text in enumerate(headers):
        hdr_cells[i].width = col_widths[i]
        set_cell_background(hdr_cells[i], header_bg)
        set_cell_margins(hdr_cells[i], top=120, bottom=120, left=120, right=120)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run(header_text)
        run.font.name = "Segoe UI"
        run.font.size = Pt(9)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        
    # Data Rows
    for r_idx, row_data in enumerate(data):
        row_cells = tbl.add_row().cells
        bg_row = HEX_GRIS_FONDO if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, cell_value in enumerate(row_data):
            row_cells[c_idx].width = col_widths[c_idx]
            set_cell_background(row_cells[c_idx], bg_row)
            set_cell_margins(row_cells[c_idx], top=80, bottom=80, left=100, right=100)
            p = row_cells[c_idx].paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            run = p.add_run(str(cell_value))
            run.font.name = "Segoe UI"
            run.font.size = Pt(8.5)
            run.font.color.rgb = COLOR_TEXTO

def build_document():
    doc = docx.Document()
    
    # Configuración de márgenes estándar (1 pulgada = 2.54 cm)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        
    # --- PORTADA INSTITUCIONAL ---
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_inst1 = p_inst.add_run("UNIVERSIDAD POPULAR DEL CESAR\n")
    r_inst1.font.name = "Segoe UI"
    r_inst1.font.size = Pt(16)
    r_inst1.font.bold = True
    r_inst1.font.color.rgb = COLOR_VERDE
    
    r_inst2 = p_inst.add_run("FACULTAD DE INGENIERÍA Y TECNOLÓGICAS\nDEPARTAMENTO DE INGENIERÍA DE SISTEMAS\n")
    r_inst2.font.name = "Segoe UI"
    r_inst2.font.size = Pt(13)
    r_inst2.font.bold = True
    r_inst2.font.color.rgb = COLOR_TEXTO

    p_spacer = doc.add_paragraph()
    p_spacer.paragraph_format.space_before = Pt(36)
    
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_tit = p_title.add_run("ESPECIFICACIÓN TÉCNICA Y MANUAL DE INGENIERÍA\n")
    r_tit.font.name = "Segoe UI"
    r_tit.font.size = Pt(20)
    r_tit.font.bold = True
    r_tit.font.color.rgb = COLOR_VERDE
    
    r_sub = p_title.add_run("SISTEMA PEA-i: PROGRAMA ESTADÍSTICO DE ANÁLISIS DE INVESTIGACIÓN\n")
    r_sub.font.name = "Segoe UI"
    r_sub.font.size = Pt(14)
    r_sub.font.bold = True
    r_sub.font.color.rgb = COLOR_ROJO

    r_desc = p_title.add_run("Modelado de Hipercubo de Información 3D mediante Multilistas Ortogonales Puras, Ingesta Multifuente SCIENTI MinCiencias, Desacoplamiento de Interfaces Visuales y Verificación Formal")
    r_desc.font.name = "Segoe UI"
    r_desc.font.size = Pt(10.5)
    r_desc.font.italic = True
    r_desc.font.color.rgb = COLOR_TEXTO

    p_spacer2 = doc.add_paragraph()
    p_spacer2.paragraph_format.space_before = Pt(48)

    # Tabla de Identificación Académica
    tbl_id = doc.add_table(rows=5, cols=2)
    tbl_id.alignment = WD_TABLE_ALIGNMENT.CENTER
    datos_meta = [
        ("Asignatura:", "Estructura de Datos (Taller 2) — Semestre 2026-I"),
        ("Docente Titular:", "Ing. Adith Bismarck Pérez Orozco"),
        ("Estudiante / Desarrollador:", "Kovyn B. Mena (kbmena@unicesar.edu.co)"),
        ("Repositorio GitHub:", "https://github.com/Kovyn-Mena/PEA-I (Rama: feature/cpp-gui)"),
        ("Fecha de Entrega:", "Lunes 19 de Octubre de 2026 — 11:59 AM"),
    ]
    for idx, (label, val) in enumerate(datos_meta):
        c0, c1 = tbl_id.rows[idx].cells
        c0.width, c1.width = Inches(2.2), Inches(4.3)
        set_cell_background(c0, "F0FFF4")
        set_cell_background(c1, "FFFFFF")
        set_cell_margins(c0, 60, 60, 80, 80)
        set_cell_margins(c1, 60, 60, 80, 80)
        
        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_after = Pt(0)
        r0 = p0.add_run(label)
        r0.font.name = "Segoe UI"
        r0.font.bold = True
        r0.font.size = Pt(9.5)
        r0.font.color.rgb = COLOR_VERDE
        
        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_after = Pt(0)
        r1 = p1.add_run(val)
        r1.font.name = "Segoe UI"
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = COLOR_TEXTO

    doc.add_page_break()

    # --- SECCIÓN 1: INTRODUCCIÓN Y ALCANCE FORMAL ---
    h1 = doc.add_heading("1. Introducción y Alcance del Sistema PEA-i", level=1)
    h1.paragraph_format.space_before = Pt(12)
    h1.paragraph_format.space_after = Pt(6)

    p_intro = doc.add_paragraph(
        "El Programa Estadístico de Análisis de Investigación (PEA-i) es una plataforma computacional desarrollada "
        "para la Universidad Popular del Cesar (UPC), orientada a la auditoría, análisis estadístico y catalogación "
        "de la producción científica institucional bajo el modelo nacional SCIENTI (GrupLAC y CvLAC de MinCiencias). "
        "El proyecto resuelve integralmente los requerimientos del Taller 2 de Estructura de Datos mediante dos "
        "aplicaciones autónomas y coordinadas (C++ y Python), diseñadas bajo un contrato relacional sagrado en SQLite3 "
        "y soportadas en estructuras de datos académicas de bajo nivel basadas exclusivamente en punteros/referencias a memoria."
    )
    p_intro.paragraph_format.space_after = Pt(8)

    add_callout(
        doc,
        "Principio de Arquitectura: 'Consola Primero' y Desacoplamiento",
        "El núcleo operativo evaluable en el examen parcial por el docente es 100% autosuficiente desde la terminal "
        "(CRUD, navegación interactiva con getch, consulta inteligente, filtrado por años y reporte tabular). "
        "Las interfaces gráficas (Dashboard Python con Matplotlib y Visualizador 3D en C++) actúan como capas desacopladas "
        "que enriquecen la experiencia del usuario sin introducir fallas ni dependencias bloqueantes al ejecutar en consola.",
        border_color_hex=HEX_VERDE_UPC,
        bg_color_hex="F0FFF4"
    )

    # --- SECCIÓN 2: IDENTIFICACIÓN DE VARIABLES DE ENTRADA Y SALIDA (PUNTO 6) ---
    h2 = doc.add_heading("2. Identificación de Variables de Entrada y Salida (Punto 6 del Taller)", level=1)
    h2.paragraph_format.space_before = Pt(14)
    h2.paragraph_format.space_after = Pt(6)

    doc.add_paragraph("A continuación se identifican formalmente las variables del modelo de datos para cada una de las entidades:")

    # Tabla Grupos
    doc.add_heading("2.1 Entidad: Grupo de Investigación", level=2)
    tbl_grp = doc.add_table(rows=1, cols=4)
    headers_var = ["Variable", "Tipo de Dato", "E/S", "Descripción y Reglas de Negocio"]
    widths_var = [Inches(1.8), Inches(1.1), Inches(0.6), Inches(3.0)]
    data_grp = [
        ["codigo_grupo", "Cadena (Texto)", "Entrada", "Clave primaria GrupLAC oficial (ej. COL0002099, COL0005544)."],
        ["nombre", "Cadena (Texto)", "Entrada", "Nombre registrado del grupo de investigación institucional."],
        ["clasificacion", "Cadena (Enum)", "Entrada", "Categoría MinCiencias: A1, A, B, C, Reconocido o Sin Clasificación."],
        ["area_conocimiento", "Cadena (Texto)", "Entrada", "Gran área OCDE (ej. Ciencias Naturales, Ingeniería y Tecnología)."],
        ["lider", "Cadena (Texto)", "Entrada", "Nombre y apellidos del investigador líder/director del grupo."],
        ["anio_creacion", "Entero (Año)", "Entrada", "Año oficial de fundación del grupo en la Universidad Popular del Cesar."],
        ["activo", "Booleano (1/0)", "E/S", "Estado lógico: 1 = Activo (computa métricas), 0 = Desactivado."],
        ["total_investigadores", "Entero", "Salida", "Cálculo en O(1)/O(I) de investigadores adscritos activos."],
        ["total_productos", "Entero", "Salida", "Cálculo acumulado de producción científica del grupo."],
        ["productos_por_ventana", "Lista / Matriz", "Salida", "Distribución de productos en ventanas de observación (2 y 5 años)."]
    ]
    format_table(tbl_grp, widths_var, headers_var, data_grp)
    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # Tabla Investigadores
    doc.add_heading("2.2 Entidad: Investigador", level=2)
    tbl_inv = doc.add_table(rows=1, cols=4)
    data_inv = [
        ["documento_id", "Cadena (Texto)", "Entrada", "Cédula de ciudadanía o código CvLAC (cod_rh). Clave primaria."],
        ["nombre_completo", "Cadena (Texto)", "Entrada", "Nombres y apellidos completos del investigador institucional."],
        ["categoria", "Cadena (Enum)", "Entrada", "Escalafón MinCiencias: Investigador Emérito, Senior, Asociado, Junior."],
        ["formacion_academica", "Cadena (Texto)", "Entrada", "Máximo grado obtenido: Pregrado, Especialización, Maestría, Doctorado."],
        ["codigo_grupo", "Cadena (Texto)", "Entrada", "Clave foránea que referencia al grupo de investigación adscrito."],
        ["activo", "Booleano (1/0)", "E/S", "Estado lógico del investigador: 1 = En ejercicio activo, 0 = Inactivo."],
        ["total_produccion", "Entero", "Salida", "Total de obras y productos donde el investigador figura como autor."]
    ]
    format_table(tbl_inv, widths_var, headers_var, data_inv)
    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # Tabla Productos
    doc.add_heading("2.3 Entidad: Producto de Investigación", level=2)
    tbl_prod = doc.add_table(rows=1, cols=4)
    data_prod = [
        ["id_producto", "Cadena (Texto)", "Entrada", "Código alfanumérico único institucional/MinCiencias (ej. SCRAP-2099-001)."],
        ["tipo", "Cadena (Enum)", "Entrada", "Tipología: Articulo, Libro, Capitulo, Software, Patente, Trabajo de Grado."],
        ["titulo", "Cadena (Texto)", "Entrada", "Título de la publicación o desarrollo tecnológico registrado."],
        ["anio", "Entero (Año)", "Entrada", "Año de publicación oficial (relevante para ventanas de observación)."],
        ["categoria_minciencias", "Cadena (Texto)", "Entrada", "Nivel de indexación: A1, A, B, C o Sin Categoría."],
        ["validado", "Booleano (1/0)", "Entrada", "Aval institucional UPC y reconocimiento MinCiencias (1 = Sí, 0 = No)."],
        ["codigo_grupo", "Cadena (Texto)", "Entrada", "Clave foránea que vincula el producto al grupo."],
        ["id_investigador", "Cadena (Texto)", "Entrada", "Clave foránea que atribuye la obra a su autor principal real."],
        ["activo", "Booleano (1/0)", "E/S", "Estado lógico: 1 = Activo en estadísticas, 0 = Desactivado."],
        ["cumple_ventana_obs", "Booleano", "Salida", "Indicador dinámico si el producto cae en la ventana (últimos 2 o 5 años)."]
    ]
    format_table(tbl_prod, widths_var, headers_var, data_prod)
    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # --- SECCIÓN 3: ESTRUCTURAS DE DATOS Y EL HIPERCUBO 3D (PUNTOS 8, 9, 14) ---
    h3 = doc.add_heading("3. Modelo del Hipercubo de Información 3D mediante Multilistas", level=1)
    h3.paragraph_format.space_before = Pt(14)
    h3.paragraph_format.space_after = Pt(6)

    doc.add_paragraph(
        "El requerimiento fundamental del docente exige modelar un Hipercubo de Información para representar "
        "la relación tridimensional entre Grupos (Eje X), Investigadores (Eje Y) y Productos Científicos (Eje Z). "
        "En computación tradicional, un hipercubo se modelaría como un arreglo tridimensional denso M[G][I][P]. "
        "No obstante, dicho enfoque generaría una matriz dispersa ineficiente donde más del 98% de las celdas serían nulas. "
        "Por tal razón, la solución implementada utiliza una MULTILISTA ORTOGONAL DINÁMICA DE ENLACES CRUZADOS."
    )

    if os.path.exists("docs/images/hipercubo_multilista.png"):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_img = p_img.add_run()
        run_img.add_picture("docs/images/hipercubo_multilista.png", width=Inches(6.2))
        p_cap = doc.add_paragraph("Figura 1: Topología Ortogonal del Hipercubo 3D en Memoria RAM sin Redundancia.")
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.runs[0].font.size = Pt(8.5)
        p_cap.runs[0].font.italic = True

    doc.add_heading("3.1 Demostración Matemática de Eficiencia Espacial y Temporal", level=2)
    p_math = doc.add_paragraph(
        "Sean G el número de grupos de investigación, I el número total de investigadores institucionales y "
        "P el catálogo de productos científicos registrados:\n\n"
        "1. Complejidad Espacial en Matriz Tridimensional Densa: O(G × I × P)\n"
        "   Para una universidad con 10 grupos, 200 investigadores y 1,000 productos, una matriz tridimensional "
        "   requeriría 10 × 200 × 1,000 = 2,000,000 celdas en memoria, de las cuales solo ~1,000 contendrían datos reales.\n\n"
        "2. Complejidad Espacial en Multilista Ortogonal PEA-i: O(G + I + P + R)\n"
        "   Donde R es el número exacto de relaciones reales. Con los mismos datos, solo se instancian 10 + 200 + 1,000 + 1,000 = "
        "   2,210 nodos en memoria dinámica, reduciendo el consumo de memoria en un 99.89%.\n\n"
        "3. Complejidad Temporal de Consultas y Modificaciones:\n"
        "   • Inserción de un nuevo producto en cabecera: O(1) tiempo constante.\n"
        "   • Acceso cruzado Investigador ↔ Producto: O(1) siguiendo el puntero ortogonal directo.\n"
        "   • Desactivación lógica (Puntos 8 y 9): O(1) modificando el atributo booleano sin alterar punteros.\n"
        "   • Eliminación física: O(k) donde k es la cantidad de productos adscritos a re-enlazar."
    )
    p_math.paragraph_format.space_after = Pt(8)

    doc.add_heading("3.2 Las 4 Estructuras de Datos Académicas y su Rol en el Sistema", level=2)
    tbl_tda = doc.add_table(rows=1, cols=3)
    headers_tda = ["TDA Académico", "Principio Operativo", "Uso y Justificación en el Sistema PEA-i"]
    widths_tda = [Inches(1.6), Inches(1.4), Inches(3.5)]
    data_tda = [
        ["Multilista Ortogonal 3D", "Punteros ortogonales cruzados", "Modela el Hipercubo tridimensional. Vincula cada producto al grupo y al autor simultáneamente en tiempo constante sin duplicación."],
        ["Lista Enlazada Simple", "Puntero sigNodo lineal", "Gestiona la secuencia de grupos institucionales y catálogos globales de categorías en memoria dinámica."],
        ["Pila (Stack)", "LIFO (Last-In, First-Out)", "Módulo Deshacer (Undo). Cada inserción, edición o borrado hace push(). Al presionar Undo se hace pop() revirtiendo el estado en O(1)."],
        ["Cola (Queue)", "FIFO (First-In, First-Out)", "Ingesta masiva por lotes. Encola tareas de scraping GrupLAC/CvLAC, parseo de PDF y CSV, procesándolas en orden estricto de llegada."]
    ]
    format_table(tbl_tda, widths_tda, headers_tda, data_tda)
    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # --- SECCIÓN 4: ESPECIFICACIÓN FORMAL DE REQUERIMIENTOS (SPEC) ---
    doc.add_page_break()
    h4 = doc.add_heading("4. Especificación Formal de Requerimientos del Sistema (SPEC)", level=1)
    h4.paragraph_format.space_before = Pt(14)
    h4.paragraph_format.space_after = Pt(6)

    doc.add_paragraph(
        "A continuación se detallan las especificaciones técnicas rigurosas (precondiciones, postcondiciones, "
        "actores y reglas de excepción) para los módulos cardinales del sistema PEA-i:"
    )

    spec_items = [
        ("RF-01: Carga Dual de Persistencia (Pregunta Inicial de Ejecución)",
         "• Actor: Evaluador / Usuario.\n"
         "• Precondición: Base de datos 'data/pea_investigacion.db' disponible en disco o archivo ausente.\n"
         "• Entradas: Opción [1] Cargar persistencia SQLite | [2] Iniciar con estructuras en memoria vacías.\n"
         "• Postcondición: Si se elige [1], se puebla la Multilista Ortogonal 3D con los grupos, investigadores y productos reales. Si se elige [2], se inicializan los punteros de cabecera en NULL (0 registros).\n"
         "• Manejo de Errores: Si SQLite está bloqueada por concurrencia, el sistema activa busy_timeout=5000ms y modo WAL sin abortar."),

        ("RF-02: Atribución Real de Autoría y Desagregación Multi-Investigador",
         "• Actor: Motor de Ingesta / Web Scraper.\n"
         "• Precondición: Lectura de cadenas bibliográficas GrupLAC (ej. 'Autores: Eydy Del Carmen Suarez...').\n"
         "• Comportamiento: El sistema extrae mediante expresiones regulares el nombre del autor real y lo busca en la sublista de investigadores del grupo. Si no existe, lo registra dinámicamente preservando su cédula o hash único.\n"
         "• Postcondición: Los productos se distribuyen equitativamente entre los más de 34 investigadores del grupo y no quedan concentrados artificialmente bajo el investigador líder."),

        ("RF-03: Filtrado por Ventana de Observación (Últimos 2 y 5 Años)",
         "• Actor: Analista de Investigación / Evaluador MinCiencias.\n"
         "• Precondición: Hipercubo cargado con productos fechados entre 1996 y 2026.\n"
         "• Lógica de Filtrado: Se calcula la cota inferior anio_limite = anio_actual - N. Solo se computan productos con anio >= anio_limite y activo == 1.\n"
         "• Postcondición: Generación instantánea de métricas de productividad, avales institucionales y clasificación MinCiencias para convocatorias oficiales.")
    ]

    for titulo, desc in spec_items:
        add_callout(doc, titulo, desc, border_color_hex=HEX_VERDE_UPC, bg_color_hex="F7FAFC")

    # Diagrama de Casos de Uso
    doc.add_heading("4.1 Diagrama Formal de Casos de Uso (UML)", level=2)
    if os.path.exists("docs/images/diagrama_casos_uso.png"):
        p_img_cu = doc.add_paragraph()
        p_img_cu.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_cu = p_img_cu.add_run()
        run_cu.add_picture("docs/images/diagrama_casos_uso.png", width=Inches(6.0))
        p_cap_cu = doc.add_paragraph("Figura 2: Diagrama de Casos de Uso del Sistema PEA-i (Interacción y Actores).")
        p_cap_cu.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap_cu.runs[0].font.size = Pt(8.5)
        p_cap_cu.runs[0].font.italic = True

    # --- SECCIÓN 5: HISTORIAS DE USUARIO (HU) CON CRITERIOS GHERKIN ---
    doc.add_page_break()
    h5 = doc.add_heading("5. Historias de Usuario (HU) con Criterios de Aceptación Gherkin", level=1)
    h5.paragraph_format.space_before = Pt(14)
    h5.paragraph_format.space_after = Pt(6)

    hus = [
        ("HU-01: Gestión de Entidades Científicas (CRUD Completo)",
         "Como evaluador del sistema de investigación,\n"
         "Quiero registrar, listar, editar y consultar grupos, investigadores y productos,\n"
         "Para mantener actualizada la base científica de la Universidad Popular del Cesar.\n\n"
         "Escenario: Inserción y persistencia coordinada\n"
         "Dado que el usuario accede al Menú Principal de C++ o Python,\n"
         "Cuando selecciona la opción de registrar un nuevo investigador asociado a GIDSE,\n"
         "Entonces el sistema crea el nodo en la Multilista en memoria RAM en O(1),\n"
         "Y sincroniza automáticamente la fila en 'data/pea_investigacion.db' en SQLite."),

        ("HU-02: Desactivación Lógica vs. Eliminación Física",
         "Como analista de convocatorias MinCiencias,\n"
         "Quiero desactivar temporalmente un producto o investigador sin destruirlo,\n"
         "Para preservar el récord histórico sin alterar las métricas del periodo actual.\n\n"
         "Escenario: Borrado lógico con reactivación\n"
         "Dado que un producto científico se encuentra activo en el hipercubo,\n"
         "Cuando el usuario selecciona la opción 'Desactivar',\n"
         "Entonces el atributo activo cambia a 0 tanto en RAM como en SQLite,\n"
         "Y el producto deja de sumarse en los totales sin romper los punteros cruzados."),

        ("HU-03: Filtrado Temporal por Ventana de Observación",
         "Como director de investigaciones de la UPC,\n"
         "Quiero filtrar la producción científica por los últimos 2 o 5 años,\n"
         "Para estimar el puntaje del grupo en la convocatoria vigente de MinCiencias.\n\n"
         "Escenario: Aplicación de ventana de observación de 2 años\n"
         "Dado que el sistema tiene productos desde el año 2008 hasta el 2026,\n"
         "Cuando se aplica el filtro de 'Últimos 2 Años (2024-2026)',\n"
         "Entonces la consola y el dashboard muestran únicamente los productos de dicho rango."),

        ("HU-04: Ingesta Masiva desde Múltiples Fuentes con Cola TDA",
         "Como operador de datos institucional,\n"
         "Quiero encolar URLs de GrupLAC/CvLAC, archivos PDF y CSV de respaldo,\n"
         "Para alimentar el hipercubo sin transcripción manual de registros.\n\n"
         "Escenario: Descarga y parseo automático de GrupLAC\n"
         "Dado que se suministra la URL pública de MinCiencias del grupo GIDSE,\n"
         "Cuando el motor de ingesta procesa la tarea desde la Cola FIFO,\n"
         "Entonces se extraen automáticamente artículos, libros y autores reales sin duplicados."),

        ("HU-05: Reversión de Cambios con Pila LIFO (Undo)",
         "Como digitador del sistema,\n"
         "Quiero deshacer la última operación realizada en caso de cometer un error,\n"
         "Para restaurar el estado previo de las estructuras de datos de manera inmediata.\n\n"
         "Escenario: Deshacer modificación accidental\n"
         "Dado que se acaba de modificar la categoría de un producto de 'A1' a 'B',\n"
         "Cuando el usuario invoca la opción 'Deshacer (Undo)',\n"
         "Entonces la Pila LIFO extrae el registro superior y restaura 'A1' en RAM y SQLite."),

        ("HU-06: Dashboard Gráfico y Análisis Multivista (3 Vistas)",
         "Como vicerrector de investigación,\n"
         "Quiero visualizar histogramas por año, diagramas de barras por categoría y 3 vistas,\n"
         "Para analizar el impacto científico de los grupos e investigadores.\n\n"
         "Escenario: Generación del Dashboard visual en Python\n"
         "Dado que el usuario invoca 'python Taller2_AB_PO_XX.py --gui',\n"
         "Cuando el motor Matplotlib procesa los datos agregados del hipercubo,\n"
         "Entonces se genera la vista gráfica interactiva con las 3 perspectivas obligatorias:\n"
         "i. Vista por Grupo, ii. Vista por Investigador, iii. Vista por Productos.")
    ]

    for titulo, desc in hus:
        add_callout(doc, titulo, desc, border_color_hex=HEX_SUBTITULO if "HU-06" in titulo else HEX_VERDE_UPC, bg_color_hex="FFFFFF")

    # --- SECCIÓN 6: ARQUITECTURA DEL SISTEMA Y COMPLEMENTOS (PUNTO 14) ---
    doc.add_page_break()
    h6 = doc.add_heading("6. Arquitectura Técnica, Interoperabilidad y Complementos para 5.0", level=1)
    h6.paragraph_format.space_before = Pt(14)
    h6.paragraph_format.space_after = Pt(6)

    if os.path.exists("docs/images/arquitectura_sistema.png"):
        p_img_arq = doc.add_paragraph()
        p_img_arq.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_arq = p_img_arq.add_run()
        run_arq.add_picture("docs/images/arquitectura_sistema.png", width=Inches(6.2))
        p_cap_arq = doc.add_paragraph("Figura 3: Arquitectura Multicapa, Contrato SQLite e Interoperabilidad IPC.")
        p_cap_arq.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap_arq.runs[0].font.size = Pt(8.5)
        p_cap_arq.runs[0].font.italic = True

    doc.add_heading("6.1 Rúbrica de Complementos para la Calificación Máxima (5.0 / 5.0)", level=2)
    tbl_comp = doc.add_table(rows=1, cols=3)
    headers_comp = ["Complemento (Punto 14)", "Implementación en el Proyecto", "Impacto y Evidencia"]
    widths_comp = [Inches(1.8), Inches(2.2), Inches(2.5)]
    data_comp = [
        ["14.a: Git y GitHub", "Repositorio Git oficial con ramas 'dev', 'feature/cpp-gui', 'backup/pre-scraping' y flujo de commits atómicos.", "Historial trazable, sin contaminación y respaldo limpio previo al scraping."],
        ["14.b: Base de Datos Relacional", "SQLite3 con modo WAL (Write-Ahead Logging), busy_timeout=5000ms y llaves foráneas estrictas.", "Única fuente de la verdad compartida simultáneamente entre C++ y Python."],
        ["14.c: GUI Creativa", "Doble interfaz: Canvas 3D interactivo para C++ y Dashboard visual con Matplotlib para Python.", "Visualización intuitiva del hipercubo sin comprometer la independencia de la consola."],
        ["14.d: Interoperabilidad entre Lenguajes", "Tuberías IPC con popen() bidireccional entre el binario C++ y los scripts Python.", "C++ delega descargas y gráficos a Python; Python delega cálculos pesados a C++."],
        ["14.e: Documentación Formal", "Documento Word formal de ingeniería con SPEC, diagramas, HUs y video de 10 min.", "Cumplimiento al 100% de la norma académica institucional de la UPC."],
        ["14.f: ¿Rust? (Auditoría de Invariantes)", "Módulo complementario en Rust (src/rust/) para validación formal y benchmarks a nivel de microsegundos.", "Garantía de rendimiento, seguridad de memoria y excelencia técnica."]
    ]
    format_table(tbl_comp, widths_comp, headers_comp, data_comp)
    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # --- SECCIÓN 7: ESTRUCTURA DEL VIDEO EXPLICATIVO (10 MINUTOS) ---
    doc.add_page_break()
    h7 = doc.add_heading("7. Guión Técnico para el Video de Sustentación (10 Minutos)", level=1)
    h7.paragraph_format.space_before = Pt(14)
    h7.paragraph_format.space_after = Pt(6)

    doc.add_paragraph(
        "De acuerdo con las Notas 2 y 3 del Taller 2, el video explicativo debe durar aproximadamente 10 minutos, "
        "respetar la identidad institucional de la UPC y mostrar a los expositores en cámara durante toda la presentación. "
        "A continuación se presenta la pauta cronométrica recomendada:"
    )

    tbl_vid = doc.add_table(rows=1, cols=4)
    headers_vid = ["Minuto", "Sección", "Contenido y Demostración en Pantalla", "Responsable"]
    widths_vid = [Inches(1.0), Inches(1.5), Inches(3.0), Inches(1.0)]
    data_vid = [
        ["00:00 - 01:30", "Introducción & Arquitectura", "Presentación personal en cámara, contextualización UPC, modelo SCIENTI y el Hipercubo 3D en Multilista.", "Estudiante A"],
        ["01:30 - 03:30", "Demostración C++ (Core)", "Ejecución de './pea_cpp'. Pregunta inicial [1]/[2], navegación con getch, búsqueda inteligente y filtros de años.", "Estudiante A"],
        ["03:30 - 05:30", "Demostración Python & Ingesta", "Ejecución de 'Taller2_AB_PO_XX.py'. Demostración de la Cola FIFO procesando GrupLAC y CSV.", "Estudiante B"],
        ["05:30 - 07:30", "Dashboards Gráficos (3 Vistas)", "Exhibición del Dashboard con Matplotlib (--gui), histogramas 1996-2026, vistas por grupo, autor y producto.", "Estudiante B"],
        ["07:30 - 09:00", "Pila Undo & SQLite WAL", "Demostración en vivo de modificación de datos y reversión instantánea con la Pila LIFO. Verificación en SQLite.", "Estudiante A"],
        ["09:00 - 10:00", "Conclusiones & Cierre", "Resumen de complementos implementados (interoperabilidad popen, módulo Rust, cero fugas de memoria).", "Ambos"]
    ]
    format_table(tbl_vid, widths_vid, headers_vid, data_vid)
    doc.add_paragraph().paragraph_format.space_after = Pt(14)

    # --- SECCIÓN 8: INSTRUCCIONES DE COMPILACIÓN Y EJECUCIÓN RÁPIDA ---
    h8 = doc.add_heading("8. Guía Rápida de Compilación y Ejecución para el Docente", level=1)
    h8.paragraph_format.space_before = Pt(14)
    h8.paragraph_format.space_after = Pt(6)

    add_callout(
        doc,
        "Instrucciones Clave para Evaluación Rápida",
        "El proyecto incluye un 'Makefile' universal configurado tanto para Linux como para Windows (MinGW/MSYS2):\n\n"
        "• Para compilar y ejecutar C++: make run-cpp  (o directamente: ./pea_cpp)\n"
        "• Para ejecutar la consola Python: make run-py  (o: python3 Taller2_AB_PO_XX.py)\n"
        "• Para ejecutar el Dashboard Gráfico Python: python3 Taller2_AB_PO_XX.py --gui\n"
        "• Para ejecutar todas las pruebas unitarias: make test\n"
        "• Para regenerar la base de datos limpia con datos reales: python3 data/init_db.py",
        border_color_hex=HEX_ROJO_UPC,
        bg_color_hex="FFF5F5"
    )

    doc.save(OUTPUT_FILE)
    print(f"[OK] Documento de Especificación Técnica generado exitosamente: {OUTPUT_FILE}")

if __name__ == "__main__":
    build_document()
