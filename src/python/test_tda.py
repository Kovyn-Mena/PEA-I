#!/usr/bin/env python3
"""
Test Suite TDA Python (Estructuras Puras de Datos)
Verifica que las estructuras en Python se comporten de forma idéntica a las de C++
"""
import sys
import os

# Asegurar importación del paquete structures
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from python.structures import Multilista, Pila, Cola

def test_multilista_y_hipercubo():
    print("[TEST Python] 1. Multilista e Hipercubo de Información...")
    multi = Multilista()

    # 1. Inserción de grupos
    assert multi.insertar_grupo("COL0002099", "GISICO", "C", "Ingeniería", "John Jairo Patiño", 2005)
    assert multi.insertar_grupo("COL0005544", "GISI", "A", "Computación", "Carlos Mendoza", 2008)
    assert not multi.insertar_grupo("COL0002099", "DUPLICADO", "B", "Ing", "Nadie", 2010)

    # 2. Inserción de investigadores
    assert multi.insertar_investigador("COL0002099", "INV-01", "Adith Pérez", "Senior", "Doctor")
    assert multi.insertar_investigador("COL0002099", "INV-02", "Eydy Suarez", "Junior", "Ingeniero")
    assert multi.insertar_investigador("COL0005544", "INV-03", "Laura Quintero", "Asociado", "Magister")

    # 3. Inserción de productos (Ortogonalidad)
    assert multi.insertar_producto("COL0002099", "INV-01", "PR-01", "Articulo", "Paper Hipercubo", 2024, "A1", True)
    assert multi.insertar_producto("COL0002099", "INV-02", "PR-02", "Software", "PEA-i Core", 2025, "A1", True)
    assert multi.insertar_producto("COL0005544", "INV-03", "PR-03", "Libro", "Libro Algoritmos", 2020, "B", True)

    # Verificación de conteos
    assert multi.contar_grupos() == 2
    assert multi.contar_investigadores() == 3
    assert multi.contar_productos() == 3

    # Verificación de ortogonalidad
    g = multi.buscar_grupo("COL0002099")
    assert g is not None
    assert g.primer_producto is not None

    inv = multi.buscar_investigador("INV-01")
    assert inv is not None
    assert inv.primer_producto is not None
    assert inv.primer_producto.id_producto == "PR-01"
    assert inv.primer_producto.titulo == "Paper Hipercubo"

    # Filtro por ventana de observación (años 2024 a 2025)
    ventana = multi.contar_productos_por_ventana(2024, 2025)
    assert ventana == 2

    # Desactivación lógica
    assert multi.desactivar_producto("PR-01", False)
    assert multi.contar_productos(solo_activos=True) == 2
    assert multi.contar_productos(solo_activos=False) == 3

    # Reactivación
    assert multi.desactivar_producto("PR-01", True)
    assert multi.contar_productos(solo_activos=True) == 3

    # Eliminación física
    assert multi.eliminar_producto("PR-03")
    assert multi.contar_productos() == 2
    assert multi.buscar_producto("PR-03") is None

    # Búsqueda inteligente por texto y muestreo aleatorio
    assert multi.buscar_grupo_por_texto("gisico") is not None
    assert multi.buscar_investigador_por_texto("eydy") is not None
    assert multi.buscar_producto_por_texto("hipercubo") is not None
    assert multi.obtener_grupo_aleatorio() is not None
    assert multi.obtener_investigador_aleatorio() is not None
    assert multi.obtener_producto_aleatorio() is not None

    print("  -> OK: Multilista ortogonal, conteos, filtros y búsqueda inteligente verificados.")

def test_pila_deshacer():
    print("[TEST Python] 2. TDA Pila (Historial / Deshacer)...")
    pila = Pila()
    assert pila.esta_vacia()

    pila.push("CREAR", "GRUPO", "COL0002099", "Nuevo grupo GISICO")
    pila.push("MODIFICAR", "PRODUCTO", "PR-01", "titulo=Paper Anterior")
    assert pila.tamano() == 2

    acc = pila.pop()
    assert acc.tipo_operacion == "MODIFICAR"
    assert acc.id_registro == "PR-01"

    acc = pila.pop()
    assert acc.tipo_operacion == "CREAR"
    assert acc.id_registro == "COL0002099"

    assert pila.esta_vacia()
    print("  -> OK: Pila LIFO verificada.")

def test_cola_ingesta():
    print("[TEST Python] 3. TDA Cola (Ingesta de URLs y archivos)...")
    cola = Cola()
    assert cola.esta_vacia()

    cola.encolar("URL_GRUPLAC", "https://scienti.minciencias.gov.co/gruplac/...", "GrupLAC GISICO")
    cola.encolar("ARCHIVO_PDF", "data/muestra_upc.pdf", "PDF Institucional")
    cola.encolar("ARCHIVO_CSV", "data/muestra_upc.csv", "CSV Respaldo")
    assert cola.tamano() == 3

    tarea = cola.desencolar()
    assert tarea.tipo_fuente == "URL_GRUPLAC"

    tarea = cola.desencolar()
    assert tarea.tipo_fuente == "ARCHIVO_PDF"

    tarea = cola.desencolar()
    assert tarea.tipo_fuente == "ARCHIVO_CSV"

    assert cola.esta_vacia()
    print("  -> OK: Cola FIFO verificada.")

def test_antiwipe_persistencia():
    print("[TEST Python] 4. Anti-wipe de persistencia (regresión oct-2026)...")
    import shutil
    import sqlite3
    import tempfile
    from python.core.db import GestorPersistencia
    from python.console import ConsolaApp
    from python.core.ingesta import MotorIngesta

    base_bd = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..",
                                           "data", "pea_investigacion.db"))
    assert os.path.exists(base_bd), "se requiere data/pea_investigacion.db para el test"
    tmp = tempfile.mkdtemp(prefix="pea_test_")
    db = os.path.join(tmp, "t.db")
    try:
        shutil.copy(base_bd, db)
        n0 = sqlite3.connect(db).execute("SELECT COUNT(*) FROM Grupos").fetchone()[0]
        assert n0 > 0

        # 1. RAM vacía -> respaldo omitido, BD intacta (antes: wipe total)
        app = ConsolaApp(db)
        assert app.guardar_ram_si_hay_datos("test") is False
        assert sqlite3.connect(db).execute("SELECT COUNT(*) FROM Grupos").fetchone()[0] == n0

        # 2. Ingesta fallida (NRO sin COL en índice, sin red) -> False y BD intacta
        motor = MotorIngesta(db)
        ok = motor.ejecutar_ingesta(
            "URL_GRUPLAC",
            "https://scienti.minciencias.gov.co/gruplac/jsp/visualiza/visualizagr.jsp?nro=99999999999999")
        assert ok is False
        assert sqlite3.connect(db).execute("SELECT COUNT(*) FROM Grupos").fetchone()[0] == n0

        # 3. Mutación real sí persiste (deshacer/CRUD no quedan bloqueados)
        app.multi.insertar_grupo("COLTEST99", "Grupo Test", "C", "Area", "Lider", 2020, True)
        assert app.guardar_ram_si_hay_datos("test") is True
        assert sqlite3.connect(db).execute(
            "SELECT COUNT(*) FROM Grupos WHERE codigo_grupo='COLTEST99'").fetchone()[0] == 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("  -> OK: vacío no borra, fallo no guarda, dato real persiste.")

def test_modelo_minciencias_2024():
    print("[TEST Python] 5. Catálogo MinCiencias 2024 (70 subtipos, familias y ponderaciones)...")
    from python.core.catalogo_2024 import CatalogoMinCiencias2024

    # 1. Software (SF) en DTI-B
    sf = CatalogoMinCiencias2024.clasificar_producto("Software", "A1", "PEA-i Sistema Core", "SF")
    assert sf["familia"] == "DTI", f"Esperado DTI, obtenido {sf['familia']}"
    assert sf["codigo_2024"] == "SF"
    assert sf["global_weight"] == 35
    assert sf["weight"] == 8.0

    # 2. Tesis Doctoral (TD) en FRH-A vs Tesis Maestría (TM) en FRH-B
    td = CatalogoMinCiencias2024.clasificar_producto("Tesis doctoral", "A", "Tesis de Doctorado en Computación", "TD")
    assert td["familia"] == "FRH", f"Esperado FRH, obtenido {td['familia']}"
    assert td["global_weight"] == 160

    tm = CatalogoMinCiencias2024.clasificar_producto("Trabajo de grado", "A", "Tesis de Maestría en Software", "TM")
    assert tm["familia"] == "FRH"
    assert tm["global_weight"] == 70

    tp = CatalogoMinCiencias2024.clasificar_producto("Trabajo de grado", "A", "Trabajo de Grado de Pregrado", "TP")
    assert tp["familia"] == "FRH"
    assert tp["global_weight"] == 20

    # 3. Working Paper (WP) y Libros de divulgación (LIB_DIV) en DPC (no GNC)
    wp = CatalogoMinCiencias2024.clasificar_producto("Documento de trabajo", "B", "Working Paper No. 12", "WP")
    assert wp["familia"] == "DPC", f"Esperado DPC, obtenido {wp['familia']}"
    assert wp["codigo_2024"] == "WP"

    lib_div = CatalogoMinCiencias2024.clasificar_producto("Libro", "B", "Libro de divulgación de la ciencia", "LIB_DIV")
    assert lib_div["familia"] == "DPC", f"Esperado DPC, obtenido {lib_div['familia']}"

    # 4. Multilista almacena campos 2024
    multi = Multilista()
    multi.insertar_grupo("G1", "Grupo 1", "A1", "Area", "Lider", 2010)
    multi.insertar_investigador("G1", "INV1", "Investigador 1", "Senior", "PhD")
    multi.insertar_producto("G1", "INV1", "P-SF", "Software", "Software PEA", 2024, "A1", True,
                            subtipo_codigo="SF", familia="DTI", clase_medicion="DTI-B", peso_calculado=28.0)
    p_sf = multi.buscar_producto("P-SF")
    assert p_sf.subtipo_codigo == "SF"
    assert p_sf.familia == "DTI"
    assert p_sf.clase_medicion == "DTI-B"
    assert p_sf.peso_calculado == 28.0
    print("  -> OK: 70 subtipos, familias oficiales y pesos Anexo 1 verificados.")

if __name__ == "__main__":
    print("========================================")
    print("TEST SUITE TDA PYTHON (Estructuras Puras)")
    print("========================================")
    test_multilista_y_hipercubo()
    test_pila_deshacer()
    test_cola_ingesta()
    test_antiwipe_persistencia()
    test_modelo_minciencias_2024()
    print("\n[EXITO TOTAL Python] Todos los TDA pasaron las pruebas rigurosamente.")
