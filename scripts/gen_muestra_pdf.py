# Genera data/muestra_upc.pdf con la tabla de 11 columnas (gemelo del CSV).
# Uso: C:\msys64\ucrt64\bin\python.exe scripts\gen_muestra_pdf.py
import os
import sys
import csv

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, "pylib"))
from fpdf import FPDF

HDR = ["codigo_grupo", "nombre_grupo", "lider_grupo", "cod_rh", "nombre_investigador",
       "correo_investigador", "titulo_producto", "tipo_producto", "categoria",
       "estado_validacion", "anio_publicacion"]
ANCHOS = [18, 22, 28, 20, 32, 36, 55, 14, 10, 16, 11]  # suma 262 <= 277 (A4 horizontal)

rows = list(csv.DictReader(open(os.path.join(BASE, "data", "muestra_upc.csv"), encoding="utf-8")))
pdf = FPDF(orientation="L", format="A4")
pdf.set_auto_page_break(auto=True, margin=10)
# Helvetica (core, WinAnsi): pypdf la lee perfecto. Se sanea a latin-1
# (el � de la fuente upstream no existe en latin-1 y romperia el font).
pdf.add_page()
pdf.set_font("Helvetica", "B", 5)
for h, w in zip(HDR, ANCHOS):
    pdf.cell(w, 6, h, border=1)  # nombres canonicos completos ( legibles para el lector )
pdf.ln()
pdf.set_font("Helvetica", "", 6)
for r in rows:
    vals = [r.get(h, "").replace("�", "N").encode("latin-1", "replace").decode("latin-1")
            for h in HDR]
    vals[6] = vals[6][:60]
    vals[4] = vals[4][:32]
    vals[5] = vals[5][:36]
    # Una linea por fila con cell() (multi_cell no emite en este entorno).
    # El CSV gemelo conserva el texto completo; el PDF prueba la tabla.
    if pdf.get_y() + 6 > 200:
        pdf.add_page()
    for v, w in zip(vals, ANCHOS):
        pdf.cell(w, 5, v[:int(w / 1.5)], border=1)
    pdf.ln()
out = os.path.join(BASE, "data", "muestra_upc.pdf")
pdf.output(out)
print("PDF OK:", out, "filas:", len(rows))
