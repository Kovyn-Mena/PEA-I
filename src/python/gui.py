"""
=====================================================================
PEA-i: DASHBOARD GRÁFICO INTERACTIVO (PYTHON - FASE 5)
Universidad Popular del Cesar — Estructura de Datos
Docente: Ing. Adith Pérez
=====================================================================
Cumple estrictamente los requisitos 12.b y 12.c del Taller 2:
  • 12.b: Dashboard con histogramas y diagramas de barras (Matplotlib).
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

Arquitectura Híbrida & Defensiva:
  - Intenta lanzar ventana de escritorio nativa Tkinter (Tkinter + FigureCanvasTkAgg).
  - Si el entorno carece de libtk / X11 (ej. Linux sin Tk o headless),
    conmuta automáticamente a la interfaz web interactiva HTML en el navegador.
=====================================================================
"""

import os
import sys
import webbrowser
import sqlite3

# Backend seguro para Matplotlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.python.structures.multilista import Multilista
from src.python.core.db import GestorPersistencia
from src.python.core.catalogo_2024 import CatalogoMinCiencias2024

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

class DashboardApp:
    def __init__(self, ruta_bd: str = "data/pea_investigacion.db"):
        self.ruta_bd = ruta_bd
        self.multi = Multilista()
        GestorPersistencia.cargar_desde_bd(self.multi, self.ruta_bd)
        self.ventana_anios = 0 # 0: Todos, 2: Últimos 2, 5: Últimos 5
        self.anio_actual = 2026

    def generar_graficos_matplotlib(self, dir_salida: str = "dist"):
        """Genera los gráficos estáticos exigidos en el Punto 12.b usando Matplotlib"""
        os.makedirs(dir_salida, exist_ok=True)

        cat_counts = {"A1": 0, "A": 0, "B": 0, "C": 0}
        anio_counts = {}
        val_counts = {"Avalados (MinCiencias)": 0, "Sin Aval": 0}
        tipos_counts = {}
        macro_counts = {
            "GNC (Nuevo Conocimiento)": 0,
            "DTI (Tecnología/Innov.)": 0,
            "ASC (Apropiación Social)": 0,
            "DPC (Divulgación Ciencia)": 0,
            "FRH (Formación Talento)": 0
        }
        total_puntos_ipp = 0

        g = self.multi.cabeza_grupos
        while g:
            p = g.primer_producto
            while p:
                pasa = True
                if self.ventana_anios > 0:
                    pasa = (p.anio >= (self.anio_actual - self.ventana_anios + 1)) and (p.anio <= self.anio_actual)
                if pasa:
                    cat = p.categoria_minciencias
                    if cat in cat_counts: cat_counts[cat] += 1
                    else: cat_counts[cat] = 1

                    anio_counts[p.anio] = anio_counts.get(p.anio, 0) + 1
                    if p.validado: val_counts["Avalados (MinCiencias)"] += 1
                    else: val_counts["Sin Aval"] += 1

                    tipos_counts[p.tipo] = tipos_counts.get(p.tipo, 0) + 1
                    
                    info = CatalogoMinCiencias2024.clasificar_producto(p.tipo, p.categoria_minciencias, p.titulo)
                    fam = info["familia"]
                    if fam == "GNC": macro_counts["GNC (Nuevo Conocimiento)"] += 1
                    elif fam == "DTI": macro_counts["DTI (Tecnología/Innov.)"] += 1
                    elif fam == "ASC": macro_counts["ASC (Apropiación Social)"] += 1
                    elif fam == "DPC": macro_counts["DPC (Divulgación Ciencia)"] += 1
                    elif fam == "FRH": macro_counts["FRH (Formación Talento)"] += 1

                    total_puntos_ipp += info["global_weight"] if p.validado else (info["global_weight"] // 2)
                p = p.sig_producto_grupo
            g = g.sig_grupo

        # Estilo visual de Matplotlib con identidad UPC
        plt.style.use('dark_background')
        fig, axes = plt.subplots(2, 2, figsize=(13, 9.5), facecolor='#080c16')

        # 1. Diagrama de Barras: Categorías MinCiencias / Publindex (12.b)
        ax1 = axes[0, 0]
        cats = list(cat_counts.keys())
        cant_cats = [cat_counts[c] for c in cats]
        barras1 = ax1.bar(cats, cant_cats, color=['#10b981', '#38bdf8', '#f59e0b', '#a855f7'], edgecolor='#1e293b')
        ax1.set_title("Calidad Editorial / Publindex (12.b)", color='#10b981', fontsize=11, fontweight='bold')
        ax1.set_facecolor('#0f172a')
        ax1.grid(axis='y', linestyle='--', alpha=0.3)
        for b in barras1:
            h = b.get_height()
            ax1.annotate(f'{h}', xy=(b.get_x() + b.get_width() / 2, h), xytext=(0, 3),
                         textcoords="offset points", ha='center', va='bottom', fontsize=9, color='#fff')

        # 2. Histograma: Producción Científica por Año (12.b)
        ax2 = axes[0, 1]
        anios_ordenados = sorted(anio_counts.keys())
        cant_anios = [anio_counts[a] for a in anios_ordenados]
        colores_anios = ['#10b981' if (self.ventana_anios == 0 or a >= self.anio_actual - self.ventana_anios + 1) else '#475569' for a in anios_ordenados]
        ax2.bar([str(a) for a in anios_ordenados], cant_anios, color=colores_anios, edgecolor='#1e293b')
        ax2.set_title("Histograma Temporal de Producción (1996-2026)", color='#f59e0b', fontsize=11, fontweight='bold')
        ax2.set_facecolor('#0f172a')
        ax2.tick_params(axis='x', rotation=45, labelsize=8)
        ax2.grid(axis='y', linestyle='--', alpha=0.3)

        # 3. 5 Familias Oficiales MinCiencias 2024 (GNC, DTI, ASC, DPC, FRH)
        ax3 = axes[1, 0]
        etiquetas_macro = list(macro_counts.keys())
        cant_macro = [macro_counts[k] for k in etiquetas_macro]
        ax3.barh(etiquetas_macro, cant_macro, color=['#006837', '#38bdf8', '#f59e0b', '#818cf8', '#ec4899'], edgecolor='#1e293b')
        ax3.set_title(f"5 Familias MinCiencias 2024 (IPP: {total_puntos_ipp} pts)", color='#38bdf8', fontsize=11, fontweight='bold')
        ax3.set_facecolor('#0f172a')
        ax3.grid(axis='x', linestyle='--', alpha=0.3)
        for b in ax3.patches:
            w = b.get_width()
            ax3.annotate(f'{int(w)}', xy=(w, b.get_y() + b.get_height() / 2), xytext=(4, 0),
                         textcoords="offset points", ha='left', va='center', fontsize=9, color='#fff')

        # 4. Estado de Aval Institucional UPC
        ax4 = axes[1, 1]
        etiquetas_val = list(val_counts.keys())
        cant_val = [val_counts[k] for k in etiquetas_val]
        ax4.pie(cant_val, labels=etiquetas_val, autopct='%1.1f%%', startangle=140,
                colors=['#006837', '#ED1C24'], textprops={'color': '#fff', 'fontsize': 9.5},
                wedgeprops={'edgecolor': '#080c16', 'linewidth': 2})
        ax4.set_title("Auditoría de Aval MinCiencias UPC", color='#ED1C24', fontsize=11, fontweight='bold')

        plt.tight_layout()
        ruta_img = os.path.join(dir_salida, "dashboard_metricas_python.png")
        fig.savefig(ruta_img, dpi=180, facecolor='#080c16')
        plt.close(fig)
        return ruta_img

    def generar_html_dashboard(self, ruta_salida: str = "dist/dashboard_python.html"):
        """Genera un archivo HTML enriquecido con las 3 vistas exigidas (12.c) y gráficos"""
        os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
        self.generar_graficos_matplotlib(os.path.dirname(ruta_salida))

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
                info_2024 = CatalogoMinCiencias2024.clasificar_producto(cur_p.tipo, cur_p.categoria_minciencias, cur_p.titulo)
                filas_prods.append({
                    "id": cur_p.id_producto,
                    "tipo": cur_p.tipo,
                    "familia": info_2024["familia"],
                    "codigo_2024": info_2024["codigo_2024"],
                    "peso": info_2024["global_weight"],
                    "titulo": cur_p.titulo,
                    "anio": cur_p.anio,
                    "categoria": cur_p.categoria_minciencias,
                    "validado": "Avalado" if cur_p.validado else "En Revisión"
                })
                cur_p = cur_p.sig_producto_grupo
            g = g.sig_grupo
        filas_prods.sort(key=lambda x: x["anio"], reverse=True)

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
        <div>
            <h1 style="margin:0; font-size:1.4rem;">PEA-i UPC &bull; Dashboard Analítico de Investigación</h1>
            <p style="margin:0.2rem 0 0 0; font-size:0.8rem; color:#cbd5e1;">Fase 5 Python &bull; Histogramas, Diagramas de Barras y Macro-Tipologías MinCiencias (Puntos 12.b y 12.c)</p>
        </div>
        <div class="badge-upc">UPC &bull; SCIENTI 2026</div>
    </header>

    <!-- GRÁFICOS MATPLOTLIB -->
    <div class="card">
        <h2>📊 Histogramas y Diagramas de Barras (Requisito 12.b - Matplotlib Engine)</h2>
        <img class="img-chart" src="dashboard_metricas_python.png" alt="Dashboard Matplotlib UPC">
    </div>

    <!-- TRES APROXIMACIONES (12.c) -->
    <div class="card">
        <h2>🏢 i. Vista por Grupo de Investigación (12.c.i)</h2>
        <table>
            <thead>
                <tr><th>Código</th><th>Nombre Oficial</th><th>Clasificación</th><th>Líder</th><th>Investigadores</th><th>Productos</th></tr>
            </thead>
            <tbody>
                {''.join(f"<tr><td><b>{g['codigo']}</b></td><td>{g['nombre']}</td><td>{g['clasificacion']}</td><td>{g['lider']}</td><td>{g['investigadores']}</td><td><b>{g['productos']}</b></td></tr>" for g in filas_grupos)}
            </tbody>
        </table>
    </div>

    <div class="card">
        <h2>👨‍🔬 ii. Vista por Investigador Autor (12.c.ii)</h2>
        <table>
            <thead>
                <tr><th>Documento</th><th>Nombre Completo</th><th>Categoría MinCiencias</th><th>Grupo</th><th>Producción Autorada</th></tr>
            </thead>
            <tbody>
                {''.join(f"<tr><td><code>{i['doc']}</code></td><td><b>{i['nombre']}</b></td><td>{i['categoria']}</td><td>{i['grupo']}</td><td><b>{i['obras']} obras</b></td></tr>" for i in filas_invs[:25])}
            </tbody>
        </table>
    </div>

    <div class="card">
        <h2>📑 iii. Vista por Productos de Investigación (12.c.iii — Modelo MinCiencias 2024)</h2>
        <table>
            <thead>
                <tr><th>ID</th><th>Familia 2024</th><th>Código</th><th>Peso IPP</th><th>Tipo</th><th>Título</th><th>Año</th><th>Categoría</th><th>Aval MinCiencias</th></tr>
            </thead>
            <tbody>
                {''.join(f"<tr><td><code>{p['id']}</code></td><td><span class='tag-macro'>{p['familia']}</span></td><td><b>{p['codigo_2024']}</b></td><td>{p['peso']} pts</td><td>{p['tipo']}</td><td>{p['titulo']}</td><td>{p['anio']}</td><td>{p['categoria']}</td><td>{p['validado']}</td></tr>" for p in filas_prods[:40])}
            </tbody>
        </table>
        <p style="font-size:0.75rem; color:#94a3b8; margin-top:0.8rem;">Mostrando las primeras 40 obras científicas de un total de {len(filas_prods)} en memoria RAM clasificadas bajo el Modelo MinCiencias 2024.</p>
    </div>
</body>
</html>
"""
        with open(ruta_salida, "w", encoding="utf-8") as f:
            f.write(html)
        return ruta_salida

    def lanzar_tkinter_desktop(self):
        """Intenta lanzar la ventana gráfica nativa con Tkinter si está disponible"""
        try:
            import tkinter as tk
            from tkinter import ttk
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
        except (ImportError, Exception):
            return False

        try:
            root = tk.Tk()
            root.title("PEA-i UPC — Dashboard Gráfico Tkinter (Puntos 12.b y 12.c)")
            root.geometry("1100x750")
            root.configure(bg="#0a0f1d")

            notebook = ttk.Notebook(root)
            notebook.pack(fill="both", expand=True, padx=10, pady=10)

            # Tab 1: Gráficos Matplotlib
            tab_graf = ttk.Frame(notebook)
            notebook.add(tab_graf, text="📊 Histogramas y Gráficos (12.b)")

            ruta_img = self.generar_graficos_matplotlib("dist")
            lbl_info = tk.Label(tab_graf, text="PEA-i: Dashboard Visual Matplotlib (UPC MinCiencias)",
                                font=("Segoe UI", 12, "bold"), bg="#0a0f1d", fg="#10b981")
            lbl_info.pack(pady=5)

            # Cargar imagen en Canvas o mostrar resumen
            lbl_status = tk.Label(tab_graf, text=f"Gráficos generados exitosamente en: {ruta_img}",
                                  bg="#0a0f1d", fg="#94a3b8")
            lbl_status.pack(pady=5)

            root.mainloop()
            return True
        except Exception:
            return False

    def iniciar(self):
        """Punto de entrada maestro para lanzar el Dashboard"""
        print("\n" + "=" * 65)
        print("     PEA-i UPC: DASHBOARD ANALÍTICO DE INVESTIGACIÓN (PYTHON)    ")
        print("=" * 65)
        print("[+] Analizando datos de la Multilista ortogonal en RAM...")
        print(f"[OK] {self.multi.contar_grupos(False)} grupos, {self.multi.contar_investigadores(False)} investigadores, {self.multi.contar_productos(False)} productos.")
        print("\n[+] Generando histogramas, diagramas de barras y Macro-Tipologías MinCiencias (Punto 12.b)...")

        # 1. Intentar interfaz de escritorio Tkinter nativa
        try:
            if self.lanzar_tkinter_desktop():
                print("[OK] Ventana nativa de Tkinter ejecutada exitosamente.")
                return True
        except Exception:
            pass

        # 2. Conmutación a Dashboard Web Interactivo
        ruta_html = self.generar_html_dashboard("dist/dashboard_python.html")
        print(f"[OK] Dashboard gráfico generado con éxito en: {ruta_html}")
        print("[+] Abriendo interfaz visual en el navegador del sistema...")

        try:
            ruta_abs = os.path.abspath(ruta_html)
            webbrowser.open(f"file://{ruta_abs}")
        except Exception as e:
            print(f"[!] No se pudo abrir automáticamente el navegador: {e}")

        print("\n[OK] Dashboard interactivo ejecutado exitosamente.")
        print("=" * 65 + "\n")
        return True

if __name__ == "__main__":
    app = DashboardApp("data/pea_investigacion.db")
    app.iniciar()
