#include <iostream>
#include <cassert>
#include "include/Nodo.h"
#include "include/Multilista.h"
#include "include/Pila.h"
#include "include/Cola.h"

void testMultilistaYHipercubo() {
    std::cout << "[TEST C++] 1. Multilista e Hipercubo de Información...\n";
    Multilista multi;

    // Inserción de 2 grupos
    assert(multi.insertarGrupo("COL0002099", "GIDSE", "A1", "Ingeniería", "Adith Pérez", 2005));
    assert(multi.insertarGrupo("COL0005544", "GISI", "A", "Computación", "Carlos Mendoza", 2008));
    assert(!multi.insertarGrupo("COL0002099", "DUPLICADO", "B", "Ing", "Nadie", 2010)); // Evita duplicados

    // Inserción de investigadores
    assert(multi.insertarInvestigador("COL0002099", "INV-01", "Adith Pérez", "Senior", "Doctor"));
    assert(multi.insertarInvestigador("COL0002099", "INV-02", "Kovyn Mena", "Junior", "Ingeniero"));
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
    assert(multi.buscarGrupoPorTexto("gidse") != nullptr);
    assert(multi.buscarInvestigadorPorTexto("kovyn") != nullptr);
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

    pila.push("CREAR", "GRUPO", "COL0002099", "Nuevo grupo GIDSE");
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

    cola.encolar("URL_GRUPLAC", "https://scienti.minciencias.gov.co/gruplac/...", "GrupLAC GIDSE");
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

int main() {
    std::cout << "========================================\n";
    std::cout << "TEST SUITE TDA C++ (Estructuras Puras)\n";
    std::cout << "========================================\n";

    testMultilistaYHipercubo();
    testPilaDeshacer();
    testColaIngesta();

    std::cout << "\n[EXITO TOTAL C++] Todos los TDA pasaron las pruebas rigurosamente.\n";
    return 0;
}
