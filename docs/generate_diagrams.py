"""
Script para generar diagramas arquitectónicos de alta calidad en PNG
para incluir en el documento Word formal y en la documentación Markdown.
Colores institucionales UPC: Verde (#006837), Rojo (#ED1C24), Gris (#2D3748)
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches

OUTPUT_DIR = "docs/images"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Paleta UPC
COLOR_VERDE_UPC = "#006837"
COLOR_ROJO_UPC = "#ED1C24"
COLOR_GRIS_FONDO = "#F8F9FA"
COLOR_TEXTO = "#1A202C"
COLOR_AZUL = "#2B6CB0"
COLOR_DORADO = "#D69E2E"

def generar_diagrama_casos_uso():
    fig, ax = plt.subplots(figsize=(12, 8), dpi=200)
    ax.set_facecolor(COLOR_GRIS_FONDO)
    fig.patch.set_facecolor(COLOR_GRIS_FONDO)
    ax.axis("off")

    # Título
    ax.text(0.5, 0.95, "DIAGRAMA DE CASOS DE USO — SISTEMA PEA-i (UPC)",
            ha="center", va="top", fontsize=15, fontweight="bold", color=COLOR_VERDE_UPC)
    ax.text(0.5, 0.91, "Modelo de Interacción y Funcionalidades del Sistema de Investigación",
            ha="center", va="top", fontsize=10, style="italic", color="#4A5568")

    # Contenedor del Sistema
    rect_sys = patches.FancyBboxPatch((0.28, 0.05), 0.68, 0.82, boxstyle="round,pad=0.02,rounding_size=0.03",
                                      facecolor="#FFFFFF", edgecolor=COLOR_VERDE_UPC, linewidth=2)
    ax.add_patch(rect_sys)
    ax.text(0.62, 0.85, "Sistema PEA-i (Núcleo C++ / Python)", ha="center", va="center",
            fontsize=12, fontweight="bold", color=COLOR_VERDE_UPC)

    # Actor (Usuario / Investigador / Evaluador)
    actor_x, actor_y = 0.12, 0.48
    circle_head = patches.Circle((actor_x, actor_y + 0.12), 0.035, facecolor="#E2E8F0", edgecolor=COLOR_TEXTO, linewidth=2)
    ax.add_patch(circle_head)
    # Cuerpo y extremidades
    ax.plot([actor_x, actor_x], [actor_y + 0.085, actor_y - 0.03], color=COLOR_TEXTO, lw=2.5)
    ax.plot([actor_x - 0.05, actor_x + 0.05], [actor_y + 0.04, actor_y + 0.04], color=COLOR_TEXTO, lw=2.5)
    ax.plot([actor_x, actor_x - 0.04], [actor_y - 0.03, actor_y - 0.12], color=COLOR_TEXTO, lw=2.5)
    ax.plot([actor_x, actor_x + 0.04], [actor_y - 0.03, actor_y - 0.12], color=COLOR_TEXTO, lw=2.5)
    ax.text(actor_x, actor_y - 0.17, "Usuario / Evaluador\nMinCiencias UPC", ha="center", va="top",
            fontsize=10, fontweight="bold", color=COLOR_TEXTO)

    # Casos de Uso (Óvalos)
    casos = [
        ("CU01: Cargar Persistencia SQLite / Vacío", 0.77),
        ("CU02: Gestionar Grupos e Investigadores (CRUD)", 0.67),
        ("CU03: Registrar y Validar Productos Científicos", 0.57),
        ("CU04: Desactivar / Reactivar Entidades (Lógico)", 0.47),
        ("CU05: Deshacer Cambios (Pila LIFO)", 0.37),
        ("CU06: Ingesta Masiva GrupLAC/PDF/CSV (Cola)", 0.27),
        ("CU07: Filtrar por Ventana (2 / 5 Años)", 0.17),
        ("CU08: Dashboard y Visualización Multivista", 0.07),
    ]

    for texto, y_pos in casos:
        oval = patches.FancyBboxPatch((0.35, y_pos), 0.54, 0.07, boxstyle="round,pad=0.015,rounding_size=0.035",
                                      facecolor="#EBF8FF", edgecolor=COLOR_AZUL, linewidth=1.5)
        ax.add_patch(oval)
        ax.text(0.62, y_pos + 0.035, texto, ha="center", va="center", fontsize=9.5, fontweight="semibold", color="#2C5282")
        # Línea de asociación actor -> caso
        ax.annotate("", xy=(0.35, y_pos + 0.035), xytext=(actor_x + 0.05, actor_y + 0.04),
                    arrowprops=dict(arrowstyle="-", color="#718096", lw=1.2, ls="--"))

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "diagrama_casos_uso.png")
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] Diagrama de Casos de Uso generado: {path}")

def generar_diagrama_hipercubo():
    fig, ax = plt.subplots(figsize=(13, 8), dpi=200)
    ax.set_facecolor(COLOR_GRIS_FONDO)
    fig.patch.set_facecolor(COLOR_GRIS_FONDO)
    ax.axis("off")

    # Título
    ax.text(0.5, 0.96, "ARQUITECTURA DEL HIPERCUBO 3D: MULTILISTA ORTOGONAL",
            ha="center", va="top", fontsize=15, fontweight="bold", color=COLOR_VERDE_UPC)
    ax.text(0.5, 0.92, "Modelo en Memoria RAM sin Redundancia — O(G + I + P) Espacial y O(1) Enlaces Cruzados",
            ha="center", va="top", fontsize=10, style="italic", color="#4A5568")

    # Eje X: Grupos (Horizontal)
    grupos = [("GIDSE\n(COL0002099)\nCat: A1", 0.15), ("GISI\n(COL0005544)\nCat: A", 0.50), ("BIOTEC\n(COL0012981)\nCat: B", 0.85)]
    for nombre, x in grupos:
        rect = patches.FancyBboxPatch((x - 0.10, 0.72), 0.20, 0.14, boxstyle="round,pad=0.01,rounding_size=0.02",
                                      facecolor=COLOR_VERDE_UPC, edgecolor="#004724", linewidth=2)
        ax.add_patch(rect)
        ax.text(x, 0.79, nombre, ha="center", va="center", color="#FFFFFF", fontsize=9.5, fontweight="bold")

    # Flechas Eje X (sigGrupo)
    ax.annotate("", xy=(0.39, 0.79), xytext=(0.26, 0.79), arrowprops=dict(arrowstyle="->", lw=2.5, color=COLOR_VERDE_UPC))
    ax.text(0.325, 0.81, "sigGrupo", ha="center", va="bottom", fontsize=8, fontweight="bold", color=COLOR_VERDE_UPC)

    ax.annotate("", xy=(0.74, 0.79), xytext=(0.61, 0.79), arrowprops=dict(arrowstyle="->", lw=2.5, color=COLOR_VERDE_UPC))
    ax.text(0.675, 0.81, "sigGrupo", ha="center", va="bottom", fontsize=8, fontweight="bold", color=COLOR_VERDE_UPC)

    ax.annotate("", xy=(0.98, 0.79), xytext=(0.96, 0.79), arrowprops=dict(arrowstyle="-|>", lw=2, color="#A0AEC0"))
    ax.text(0.99, 0.79, "NULL", ha="left", va="center", fontsize=8, fontweight="bold", color="#A0AEC0")

    # Eje Y: Investigadores bajo GIDSE (Vertical)
    invs_gidse = [
        ("Ing. Adith Pérez Orozco\nLíder GIDSE (Senior)", 0.50),
        ("Kovyn Mena\nInvestigador Junior", 0.30),
        ("Eydy Del Carmen Suarez\nInvestigadora Asociada", 0.10)
    ]

    # Flecha primerInvestigador desde GIDSE
    ax.annotate("", xy=(0.15, 0.58), xytext=(0.15, 0.71), arrowprops=dict(arrowstyle="->", lw=2, color=COLOR_AZUL))
    ax.text(0.16, 0.65, "primerInvestigador", ha="left", va="center", fontsize=8, fontweight="bold", color=COLOR_AZUL)

    for i, (nombre, y) in enumerate(invs_gidse):
        rect = patches.FancyBboxPatch((0.04, y - 0.04), 0.22, 0.08, boxstyle="round,pad=0.01,rounding_size=0.02",
                                      facecolor="#2B6CB0", edgecolor="#1A365D", linewidth=1.5)
        ax.add_patch(rect)
        ax.text(0.15, y, nombre, ha="center", va="center", color="#FFFFFF", fontsize=8, fontweight="bold")
        if i < len(invs_gidse) - 1:
            next_y = invs_gidse[i+1][1]
            ax.annotate("", xy=(0.15, next_y + 0.05), xytext=(0.15, y - 0.05),
                        arrowprops=dict(arrowstyle="->", lw=1.8, color=COLOR_AZUL))
            ax.text(0.16, (y + next_y)/2, "sigInvestigador", ha="left", va="center", fontsize=7.5, color=COLOR_AZUL)

    # Eje Z: Productos cruzados vinculados a Investigador y a Grupo
    prods = [
        ("Artículo: Scientific Methods...\nAño: 2024 | Cat: A1 | Valid: Sí", 0.50),
        ("Software: PEA-i Sistema UPC\nAño: 2025 | Cat: A1 | Valid: Sí", 0.30),
        ("Capítulo: Gestión Innovación...\nAño: 2023 | Cat: A | Valid: Sí", 0.10),
    ]

    for (texto, y) in prods:
        rect = patches.FancyBboxPatch((0.48, y - 0.04), 0.38, 0.08, boxstyle="round,pad=0.01,rounding_size=0.02",
                                      facecolor="#FFFFFF", edgecolor=COLOR_ROJO_UPC, linewidth=2)
        ax.add_patch(rect)
        ax.text(0.67, y, texto, ha="center", va="center", color="#742A2A", fontsize=8, fontweight="bold")

    # Enlace Ortogonal 1: Adith -> Producto 1
    ax.annotate("", xy=(0.47, 0.50), xytext=(0.27, 0.50), arrowprops=dict(arrowstyle="->", lw=2, color=COLOR_ROJO_UPC))
    ax.text(0.37, 0.52, "primerProducto", ha="center", va="bottom", fontsize=7.5, fontweight="bold", color=COLOR_ROJO_UPC)

    # Enlace Ortogonal 2: Kovyn -> Producto 2
    ax.annotate("", xy=(0.47, 0.30), xytext=(0.27, 0.30), arrowprops=dict(arrowstyle="->", lw=2, color=COLOR_ROJO_UPC))
    ax.text(0.37, 0.32, "primerProducto", ha="center", va="bottom", fontsize=7.5, fontweight="bold", color=COLOR_ROJO_UPC)

    # Enlace Ortogonal 3: Eydy -> Producto 3
    ax.annotate("", xy=(0.47, 0.10), xytext=(0.27, 0.10), arrowprops=dict(arrowstyle="->", lw=2, color=COLOR_ROJO_UPC))
    ax.text(0.37, 0.12, "primerProducto", ha="center", va="bottom", fontsize=7.5, fontweight="bold", color=COLOR_ROJO_UPC)

    # Enlace del Grupo GIDSE directo hacia la cadena de productos del grupo (sigProductoGrupo)
    ax.annotate("", xy=(0.67, 0.55), xytext=(0.20, 0.71),
                arrowprops=dict(arrowstyle="->", lw=1.5, ls=":", color=COLOR_VERDE_UPC,
                                connectionstyle="angle,angleA=-90,angleB=180,rad=10"))
    ax.text(0.42, 0.66, "primerProductoGrupo (Eje Grupo-Producto)", ha="center", va="center",
            fontsize=8, fontweight="bold", color=COLOR_VERDE_UPC)

    # Leyenda explicativa
    rect_leyenda = patches.FancyBboxPatch((0.02, 0.01), 0.96, 0.05, boxstyle="round,pad=0.005",
                                          facecolor="#EDF2F7", edgecolor="#CBD5E0", linewidth=1)
    ax.add_patch(rect_leyenda)
    ax.text(0.5, 0.035, "Leyenda: [Verde] Dimensión Grupos | [Azul] Dimensión Investigadores | [Rojo] Dimensión Productos | Enlaces Cruzados O(1)",
            ha="center", va="center", fontsize=8.5, fontweight="bold", color="#2D3748")

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "hipercubo_multilista.png")
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] Diagrama de Hipercubo Multilista generado: {path}")

def generar_diagrama_arquitectura():
    fig, ax = plt.subplots(figsize=(12, 7.5), dpi=200)
    ax.set_facecolor(COLOR_GRIS_FONDO)
    fig.patch.set_facecolor(COLOR_GRIS_FONDO)
    ax.axis("off")

    # Título
    ax.text(0.5, 0.96, "ARQUITECTURA DEL SISTEMA PEA-i: DESACOPLAMIENTO Y MULTICAPA",
            ha="center", va="top", fontsize=15, fontweight="bold", color=COLOR_VERDE_UPC)
    ax.text(0.5, 0.92, "Principio Sagrado 'Consola Primero', Persistencia Central SQLite e IPC Bidireccional",
            ha="center", va="top", fontsize=10, style="italic", color="#4A5568")

    # Bloque 1: Consola Autónoma C++ (Izquierda)
    b_cpp = patches.FancyBboxPatch((0.05, 0.52), 0.28, 0.35, boxstyle="round,pad=0.015,rounding_size=0.02",
                                  facecolor="#EBF8FF", edgecolor="#2B6CB0", linewidth=2)
    ax.add_patch(b_cpp)
    ax.text(0.19, 0.83, "MÓDULO C++ (Core)", ha="center", va="center", fontsize=11, fontweight="bold", color="#2B6CB0")
    ax.text(0.19, 0.76, "• TDA Multilista 3D Nodos\n• TDA Pila LIFO (Undo)\n• TDA Cola FIFO (Ingesta)\n• Navegación getch interactiva\n• Reportes Tabulares MinCiencias",
            ha="center", va="top", fontsize=8.5, color="#1A202C")
    ax.text(0.19, 0.55, "Binario: ./pea_cpp", ha="center", va="center", fontsize=8, fontweight="bold", color="#2C5282")

    # Bloque 2: Consola Autónoma Python (Derecha)
    b_py = patches.FancyBboxPatch((0.67, 0.52), 0.28, 0.35, boxstyle="round,pad=0.015,rounding_size=0.02",
                                 facecolor="#FEFCBF", edgecolor="#B7791F", linewidth=2)
    ax.add_patch(b_py)
    ax.text(0.81, 0.83, "MÓDULO PYTHON (Core)", ha="center", va="center", fontsize=11, fontweight="bold", color="#B7791F")
    ax.text(0.81, 0.76, "• TDA Multilista 3D Nodos\n• TDA Pila LIFO (Undo)\n• TDA Cola FIFO (Ingesta)\n• Web Scraping GrupLAC/CvLAC\n• Parsers PDF y CSV Masivos",
            ha="center", va="top", fontsize=8.5, color="#1A202C")
    ax.text(0.81, 0.55, "Script: Taller2_AB_PO_XX.py", ha="center", va="center", fontsize=8, fontweight="bold", color="#744210")

    # Bloque Central: Persistencia Única SQLite
    b_db = patches.FancyBboxPatch((0.36, 0.38), 0.28, 0.24, boxstyle="round,pad=0.015,rounding_size=0.02",
                                 facecolor="#E6FFFA", edgecolor=COLOR_VERDE_UPC, linewidth=2.5)
    ax.add_patch(b_db)
    ax.text(0.50, 0.57, "PERSISTENCIA SAGRADA\nSQLite3 (WAL Mode)", ha="center", va="center", fontsize=10.5, fontweight="bold", color=COLOR_VERDE_UPC)
    ax.text(0.50, 0.47, "data/pea_investigacion.db\n• Grupos (Plan/Integrantes)\n• Investigadores\n• Productos Científicos\n• Historial Acciones",
            ha="center", va="center", fontsize=8, color="#234E52")

    # Flechas bidireccionales C++ <-> SQLite y Python <-> SQLite
    ax.annotate("", xy=(0.35, 0.50), xytext=(0.34, 0.65), arrowprops=dict(arrowstyle="<->", lw=2, color=COLOR_VERDE_UPC))
    ax.text(0.33, 0.57, "libsqlite3", ha="right", va="center", fontsize=8, fontweight="bold", color=COLOR_VERDE_UPC)

    ax.annotate("", xy=(0.65, 0.50), xytext=(0.66, 0.65), arrowprops=dict(arrowstyle="<->", lw=2, color=COLOR_VERDE_UPC))
    ax.text(0.67, 0.57, "sqlite3 native", ha="left", va="center", fontsize=8, fontweight="bold", color=COLOR_VERDE_UPC)

    # Puente IPC popen() entre C++ y Python
    ax.annotate("", xy=(0.66, 0.70), xytext=(0.34, 0.70),
                arrowprops=dict(arrowstyle="<->", lw=2, color=COLOR_ROJO_UPC, ls="--"))
    ax.text(0.50, 0.73, "Interoperabilidad C++ <-> Python\n(popen IPC Bridge --headless)", ha="center", va="bottom",
            fontsize=8.5, fontweight="bold", color=COLOR_ROJO_UPC)

    # Capa de Interfaces Visuales y Extras (Inferior)
    b_gui = patches.FancyBboxPatch((0.05, 0.08), 0.90, 0.22, boxstyle="round,pad=0.015,rounding_size=0.02",
                                  facecolor="#FFFFFF", edgecolor="#CBD5E0", linewidth=1.5)
    ax.add_patch(b_gui)
    ax.text(0.50, 0.26, "CAPA DE PRESENTACIÓN VISUAL Y COMPLEMENTOS (Desacoplada para el 5.0)",
            ha="center", va="center", fontsize=10.5, fontweight="bold", color=COLOR_TEXTO)

    # Sub-bloques GUI
    ax.text(0.20, 0.16, "C++ GUI Dashboard\n(Canvas HTML5 / ImGui)\nVista Interactiva Hipercubo",
            ha="center", va="center", fontsize=8.5, color="#2B6CB0", bbox=dict(boxstyle="round,pad=0.3", facecolor="#EBF8FF", ec="#bee3f8"))
    ax.text(0.50, 0.16, "Python GUI Dashboard\n(Matplotlib + 3 Vistas)\nHistogramas por Año y Barras",
            ha="center", va="center", fontsize=8.5, color="#B7791F", bbox=dict(boxstyle="round,pad=0.3", facecolor="#FEFCBF", ec="#fefcbf"))
    ax.text(0.80, 0.16, "Auditor de Invariantes\nMódulo Rust / Benchmarks\nVerificación μs y Concurrencia",
            ha="center", va="center", fontsize=8.5, color="#C53030", bbox=dict(boxstyle="round,pad=0.3", facecolor="#FFF5F5", ec="#feb2b2"))

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "arquitectura_sistema.png")
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] Diagrama de Arquitectura generado: {path}")

if __name__ == "__main__":
    generar_diagrama_casos_uso()
    generar_diagrama_hipercubo()
    generar_diagrama_arquitectura()
