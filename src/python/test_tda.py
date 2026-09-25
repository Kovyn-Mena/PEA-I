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
    assert multi.insertar_grupo("COL0002099", "GIDSE", "A1", "Ingeniería", "Adith Pérez", 2005)
    assert multi.insertar_grupo("COL0005544", "GISI", "A", "Computación", "Carlos Mendoza", 2008)
    assert not multi.insertar_grupo("COL0002099", "DUPLICADO", "B", "Ing", "Nadie", 2010)

    # 2. Inserción de investigadores
    assert multi.insertar_investigador("COL0002099", "INV-01", "Adith Pérez", "Senior", "Doctor")
    assert multi.insertar_investigador("COL0002099", "INV-02", "Kovyn Mena", "Junior", "Ingeniero")
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
    assert multi.buscar_grupo_por_texto("gidse") is not None
    assert multi.buscar_investigador_por_texto("kovyn") is not None
    assert multi.buscar_producto_por_texto("hipercubo") is not None
    assert multi.obtener_grupo_aleatorio() is not None
    assert multi.obtener_investigador_aleatorio() is not None
    assert multi.obtener_producto_aleatorio() is not None

    print("  -> OK: Multilista ortogonal, conteos, filtros y búsqueda inteligente verificados.")

def test_pila_deshacer():
    print("[TEST Python] 2. TDA Pila (Historial / Deshacer)...")
    pila = Pila()
    assert pila.esta_vacia()

    pila.push("CREAR", "GRUPO", "COL0002099", "Nuevo grupo GIDSE")
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

    cola.encolar("URL_GRUPLAC", "https://scienti.minciencias.gov.co/gruplac/...", "GrupLAC GIDSE")
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

if __name__ == "__main__":
    print("========================================")
    print("TEST SUITE TDA PYTHON (Estructuras Puras)")
    print("========================================")
    test_multilista_y_hipercubo()
    test_pila_deshacer()
    test_cola_ingesta()
    print("\n[EXITO TOTAL Python] Todos los TDA pasaron las pruebas rigurosamente.")
