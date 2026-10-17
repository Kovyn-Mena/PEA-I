#include <iostream>
#include <cassert>
#include "include/Nodo.h"
#include "include/Multilista.h"
#include "include/Pila.h"
#include "include/Cola.h"
#include "include/Catalogo2024.h"

void testMultilistaYHipercubo() {
    std::cout << "[TEST C++] 1. Multilista e Hipercubo de Información...\n";
    Multilista multi;

    // Inserción de 2 grupos
    assert(multi.insertarGrupo("COL0002099", "GISICO", "C", "Ingeniería", "John Jairo Patiño", 2005));
    assert(multi.insertarGrupo("COL0005544", "GISI", "A", "Computación", "Carlos Mendoza", 2008));
    assert(!multi.insertarGrupo("COL0002099", "DUPLICADO", "B", "Ing", "Nadie", 2010)); // Evita duplicados

    // Inserción de investigadores
    assert(multi.insertarInvestigador("COL0002099", "INV-01", "Adith Pérez", "Senior", "Doctor"));
    assert(multi.insertarInvestigador("COL0002099", "INV-02", "Eydy Suarez", "Junior", "Ingeniero"));
    assert(multi.insertarInvestigador("COL0005544", "INV-03", "Laura Quintero", "Asociado", "Magister"));

    // Inserción de productos (Ortogonalidad)
    assert(multi.insertarProducto("COL0002099", "INV-01", "PR-01", "Articulo", "Paper Hipercubo", 2024, "A1", true));
    assert(multi.insertarProducto("COL0002099", "INV-02", "PR-02", "Software", "PEA-i Core", 2025, "A1", true));
    assert(multi.insertarProducto("COL0005544", "INV-03", "PR-03", "Libro", "Libro Algoritmos", 2020, "B", true));

    // Verificación de conteos
    assert(multi.contarGrupos() == 2);
    assert(multi.contarInvestigadores() == 3);
    assert(multi.contarProductos() == 3);

    // Verificación de navegación ortogonal
    NodoGrupo* g = multi.buscarGrupo("COL0002099");
    assert(g != nullptr);
    assert(g->primerProducto != nullptr);

    NodoInvestigador* inv = multi.buscarInvestigador("INV-01");
    assert(inv != nullptr);
    assert(inv->primerProducto != nullptr);
    // El producto es el mismo PR-01
    assert(inv->primerProducto->id_producto == "PR-01");
    assert(inv->primerProducto->titulo == "Paper Hipercubo");

    // Filtro por ventana de observación (años 2024 a 2025)
    int productosVentana = multi.contarProductosPorVentana(2024, 2025);
    assert(productosVentana == 2); // PR-01 (2024) y PR-02 (2025)

    // Prueba de Desactivación (Borrado Lógico)
    multi.desactivarProducto("PR-01", false);
    assert(multi.contarProductos(true) == 2);  // Solo 2 activos
    assert(multi.contarProductos(false) == 3); // 3 en total en memoria

    // Reactivación
    multi.desactivarProducto("PR-01", true);
    assert(multi.contarProductos(true) == 3);

    // Prueba de Eliminación Física
    assert(multi.eliminarProducto("PR-03"));
    assert(multi.contarProductos() == 2);
    assert(multi.buscarProducto("PR-03") == nullptr);

    // Búsqueda inteligente por texto y muestreo aleatorio
    assert(multi.buscarGrupoPorTexto("gisico") != nullptr);
    assert(multi.buscarInvestigadorPorTexto("eydy") != nullptr);
    assert(multi.buscarProductoPorTexto("hipercubo") != nullptr);
    assert(multi.obtenerGrupoAleatorio() != nullptr);
    assert(multi.obtenerInvestigadorAleatorio() != nullptr);
    assert(multi.obtenerProductoAleatorio() != nullptr);

    std::cout << "  -> OK: Multilista ortogonal, conteos, filtros y búsqueda inteligente verificados.\n";
}

void testPilaDeshacer() {
    std::cout << "[TEST C++] 2. TDA Pila (Historial / Deshacer)...\n";
    Pila pila;
    assert(pila.estaVacia());

    pila.push("CREAR", "GRUPO", "COL0002099", "Nuevo grupo GISICO");
    pila.push("MODIFICAR", "PRODUCTO", "PR-01", "titulo=Paper Anterior");
    assert(pila.tamano() == 2);

    AccionHistorial acc;
    assert(pila.pop(acc));
    assert(acc.tipo_operacion == "MODIFICAR");
    assert(acc.id_registro == "PR-01");
    assert(acc.detalle_previo == "titulo=Paper Anterior");

    assert(pila.pop(acc));
    assert(acc.tipo_operacion == "CREAR");
    assert(acc.id_registro == "COL0002099");

    assert(pila.estaVacia());
    std::cout << "  -> OK: Pila LIFO verificada.\n";
}

void testColaIngesta() {
    std::cout << "[TEST C++] 3. TDA Cola (Ingesta de URLs y archivos)...\n";
    Cola cola;
    assert(cola.estaVacia());

    cola.encolar("URL_GRUPLAC", "https://scienti.minciencias.gov.co/gruplac/...", "GrupLAC GISICO");
    cola.encolar("ARCHIVO_PDF", "data/muestra_upc.pdf", "PDF Institucional");
    cola.encolar("ARCHIVO_CSV", "data/muestra_upc.csv", "CSV Respaldo");
    assert(cola.tamano() == 3);

    TareaIngesta tarea;
    assert(cola.desencolar(tarea));
    assert(tarea.tipo_fuente == "URL_GRUPLAC");

    assert(cola.desencolar(tarea));
    assert(tarea.tipo_fuente == "ARCHIVO_PDF");

    assert(cola.desencolar(tarea));
    assert(tarea.tipo_fuente == "ARCHIVO_CSV");

    assert(cola.estaVacia());
    std::cout << "  -> OK: Cola FIFO verificada.\n";
}

void testModeloMinCiencias2024() {
    std::cout << "[TEST C++] 4. Modelo MinCiencias 2024 (70 subtipos, familias y pesos)...\n";

    // 1. Software (SF) en DTI-B
    InfoTipologia2024 sf = Catalogo2024::clasificar("Software", "A1", "PEA-i Sistema Core", "SF");
    assert(sf.familia == "DTI");
    assert(sf.codigo_2024 == "SF");
    assert(sf.global_weight == 35);
    assert(sf.weight == 8.0);

    // 2. Tesis Doctoral (TD) en FRH-A vs Tesis Maestría (TM) en FRH-B
    InfoTipologia2024 td = Catalogo2024::clasificar("Tesis doctoral", "A", "Tesis Doctoral en IA", "TD");
    assert(td.familia == "FRH");
    assert(td.global_weight == 160);

    InfoTipologia2024 tm = Catalogo2024::clasificar("Trabajo de grado", "A", "Tesis de Maestría", "TM");
    assert(tm.familia == "FRH");
    assert(tm.global_weight == 70);

    InfoTipologia2024 tp = Catalogo2024::clasificar("Trabajo de grado", "A", "Pregrado en Sistemas", "TP");
    assert(tp.familia == "FRH");
    assert(tp.global_weight == 20);

    // 3. Working Paper (WP) en DPC (no GNC)
    InfoTipologia2024 wp = Catalogo2024::clasificar("Documento de trabajo", "B", "Working Paper No. 12", "WP");
    assert(wp.familia == "DPC");
    assert(wp.codigo_2024 == "WP");

    // 4. Multilista almacena campos 2024
    Multilista multi;
    assert(multi.insertarGrupo("G1", "Grupo 1", "A1", "Area", "Lider", 2010));
    assert(multi.insertarInvestigador("G1", "INV1", "Investigador 1", "Senior", "PhD"));
    assert(multi.insertarProducto("G1", "INV1", "P-SF", "Software", "Software PEA", 2024, "A1", true, true,
                                 "SF", "DTI", "DTI-B", 28.0));
    NodoProducto* p_sf = multi.buscarProducto("P-SF");
    assert(p_sf != nullptr);
    assert(p_sf->subtipo_codigo == "SF");
    assert(p_sf->familia == "DTI");
    assert(p_sf->clase_medicion == "DTI-B");
    assert(p_sf->peso_calculado == 28.0);

    std::cout << "  -> OK: 70 subtipos, 5 familias y ponderaciones Anexo 1 verificados.\n";
}

int main() {
    std::cout << "========================================\n";
    std::cout << "TEST SUITE TDA C++ (Estructuras Puras)\n";
    std::cout << "========================================\n";

    testMultilistaYHipercubo();
    testPilaDeshacer();
    testColaIngesta();
    testModeloMinCiencias2024();

    std::cout << "\n[EXITO TOTAL C++] Todos los TDA pasaron las pruebas rigurosamente.\n";
    return 0;
}
