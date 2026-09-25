#ifndef CONSOLA_APP_H
#define CONSOLA_APP_H

#include <iostream>
#include <iomanip>
#include <string>
#include <cstdlib>
#include "Multilista.h"
#include "Pila.h"
#include "Cola.h"
#include "GestorSQLite.h"

// =====================================================================
// APLICACIÓN DE CONSOLA AUTÓNOMA (C++) - PEA-i
// 100% Independiente de GUI | Limpieza de pantalla multiplataforma
// Validación robusta de teclado (manejo de ENTER y retroceso con 0)
// =====================================================================

class ConsolaApp {
private:
    Multilista multi;
    Pila historial;
    Cola colaIngesta;
    std::string rutaBD;

public:
    ConsolaApp(const std::string& bd = "data/pea_investigacion.db")
        : rutaBD(bd) {}

    // -----------------------------------------------------------------
    // HELPERS MULTIPLATAFORMA DE PANTALLA Y ENTRADA
    // -----------------------------------------------------------------

    // Borrado de pantalla independiente del Sistema Operativo (Windows, Linux, macOS)
    static void limpiarPantalla() {
    #if defined(_WIN32) || defined(_WIN64)
        std::system("cls");
    #else
        // Secuencia ANSI universal de limpieza y reposicionamiento del cursor
        std::cout << "\033[2J\033[H" << std::flush;
    #endif
    }

    // Pausa amigable que espera ENTER para avanzar o retroceder
    static void pausar(const std::string& mensaje = "\n[Presione ENTER para continuar / regresar]... ") {
        std::cout << mensaje << std::flush;
        std::string linea;
        std::getline(std::cin, linea);
    }

    // Lectura segura de texto (evita trampas de saltos de línea residuales)
    static std::string leerLinea(const std::string& mensaje, bool permitirVacio = false) {
        while (true) {
            std::cout << mensaje;
            std::string linea;
            if (!std::getline(std::cin, linea)) return "";

            // Si se permite vacío (ej: presionar ENTER para omitir o volver)
            if (permitirVacio) return linea;

            size_t first = linea.find_first_not_of(" \t\r\n");
            if (first != std::string::npos) {
                return linea;
            }
            std::cout << "  [!] El campo no puede estar vacío. Intente de nuevo.\n";
        }
    }

    // Lectura segura de enteros: si presiona solo ENTER, maneja el valor por defecto
    static int leerEntero(const std::string& mensaje, int valorPorDefecto = -1) {
        while (true) {
            std::cout << mensaje;
            std::string linea;
            if (!std::getline(std::cin, linea)) return valorPorDefecto;

            size_t first = linea.find_first_not_of(" \t\r\n");
            if (first == std::string::npos) {
                if (valorPorDefecto != -1) return valorPorDefecto;
                std::cout << "  [!] Ingrese un número válido (o 0 para regresar).\n";
                continue;
            }
            try {
                return std::stoi(linea.substr(first));
            } catch (...) {
                std::cout << "  [!] Entrada inválida. Ingrese un número (o 0 para regresar).\n";
            }
        }
    }

    // -----------------------------------------------------------------
    // PUNTO DE ENTRADA INTERACTIVO (Punto 10 pág 3)
    // -----------------------------------------------------------------
    void iniciar() {
        limpiarPantalla();
        std::cout << "=================================================================\n";
        std::cout << "     PEA-i: PROGRAMA ESTADISTICO DE ANALISIS DE INVESTIGACION   \n";
        std::cout << "    Universidad Popular del Cesar (UPC) - Estructura de Datos   \n";
        std::cout << "=================================================================\n";
        std::cout << "Seleccione el modo de inicio del sistema:\n";
        std::cout << "  [1] Cargar datos persistidos desde la BD SQLite (" << rutaBD << ")\n";
        std::cout << "  [2] Iniciar con estructuras en memoria vacias\n";
        std::cout << "-----------------------------------------------------------------\n";
        
        int opcion = leerEntero("Opción [1 o 2]: ", 1);
        if (opcion == 1) {
            std::cout << "\n[+] Cargando datos desde SQLite hacia la Multilista...\n";
            if (GestorSQLite::cargarDesdeBD(multi, rutaBD)) {
                std::cout << "[OK] Datos cargados exitosamente:\n";
                std::cout << "     • Grupos:         " << multi.contarGrupos(false) << "\n";
                std::cout << "     • Investigadores: " << multi.contarInvestigadores(false) << "\n";
                std::cout << "     • Productos:      " << multi.contarProductos(false) << "\n";
            } else {
                std::cout << "[!] No se pudo cargar la BD. Se iniciará en memoria vacía.\n";
            }
        } else {
            std::cout << "\n[+] Iniciando con estructuras en memoria vacías.\n";
        }

        pausar("\n[Presione ENTER para ingresar al Menú Principal]... ");
        menuPrincipal();
    }

    // -----------------------------------------------------------------
    // MENÚ PRINCIPAL
    // -----------------------------------------------------------------
    void menuPrincipal() {
        int op = -1;
        while (op != 0) {
            limpiarPantalla();
            std::cout << "=================================================================\n";
            std::cout << "                  PEA-i UPC > MENU PRINCIPAL (C++)               \n";
            std::cout << "=================================================================\n";
            std::cout << "  1. Gestion de Grupos de Investigacion (CRUD)\n";
            std::cout << "  2. Gestion de Investigadores (CRUD)\n";
            std::cout << "  3. Gestion de Productos de Investigacion (CRUD)\n";
            std::cout << "  4. Deshacer ultima accion (Pila Undo - LIFO) [" << historial.tamano() << " en pila]\n";
            std::cout << "  5. Resumen Estadistico y Filtro por Ventana de Años\n";
            std::cout << "  6. Guardar cambios en la Base de Datos (Persistencia)\n";
            std::cout << "  0. Salir del Sistema\n";
            std::cout << "-----------------------------------------------------------------\n";
            op = leerEntero("Seleccione una opción: ");

            switch (op) {
                case 1: menuGrupos(); break;
                case 2: menuInvestigadores(); break;
                case 3: menuProductos(); break;
                case 4: ejecutarDeshacer(); break;
                case 5: menuEstadisticasYFiltro(); break;
                case 6: guardarEnBD(); break;
                case 0:
                    limpiarPantalla();
                    std::cout << "=================================================================\n";
                    std::cout << "                       SALIDA DEL SISTEMA                        \n";
                    std::cout << "=================================================================\n";
                    std::cout << "¿Desea guardar los cambios en SQLite antes de salir?\n";
                    std::cout << "  [1] Sí, guardar y salir\n";
                    std::cout << "  [2] No guardar y salir\n";
                    std::cout << "  [0] Cancelar y regresar al menú\n";
                    std::cout << "-----------------------------------------------------------------\n";
                    {
                        int confirm = leerEntero("Opción [1/2/0]: ", 2);
                        if (confirm == 1) {
                            guardarEnBD();
                            std::cout << "\n[+] Cambios guardados. ¡Éxitos en el taller!\n";
                        } else if (confirm == 0) {
                            op = -1; // No salir
                        } else {
                            std::cout << "\n[+] Saliendo sin guardar cambios recientes.\n";
                        }
                    }
                    break;
                default:
                    std::cout << "  [!] Opción no válida.\n";
                    pausar();
            }
        }
    }

    // -----------------------------------------------------------------
    // CRUD: GRUPOS
    // -----------------------------------------------------------------
    void menuGrupos() {
        int op = -1;
        while (op != 0) {
            limpiarPantalla();
            std::cout << "=================================================================\n";
            std::cout << "     PEA-i UPC > Menú Principal > Gestión de Grupos             \n";
            std::cout << "=================================================================\n";
            std::cout << "  1. Listar Grupos Registrados\n";
            std::cout << "  2. Incluir Nuevo Grupo\n";
            std::cout << "  3. Consultar Detalle de un Grupo (Hipercubo)\n";
            std::cout << "  4. Modificar Grupo\n";
            std::cout << "  5. Desactivar / Reactivar Grupo (Borrado Lógico)\n";
            std::cout << "  6. Eliminar Grupo Físicamente (Cascada)\n";
            std::cout << "  0. Anterior / Regresar al Menú Principal\n";
            std::cout << "-----------------------------------------------------------------\n";
            op = leerEntero("Opción: ");

            if (op == 1) {
                limpiarPantalla();
                std::cout << "=========================================================================================\n";
                std::cout << "                             LISTADO DE GRUPOS DE INVESTIGACIÓN                          \n";
                std::cout << "=========================================================================================\n";
                std::cout << std::left 
                          << std::setw(14) << "CODIGO"
                          << std::setw(35) << "NOMBRE"
                          << std::setw(12) << "CLASIF."
                          << std::setw(20) << "LIDER"
                          << std::setw(8)  << "ESTADO" << "\n";
                std::cout << std::string(89, '-') << "\n";
                NodoGrupo* g = multi.getCabezaGrupos();
                if (!g) std::cout << "  (No hay grupos registrados en memoria)\n";
                while (g != nullptr) {
                    std::string nomCorto = g->nombre.length() > 33 ? g->nombre.substr(0, 30) + "..." : g->nombre;
                    std::cout << std::left 
                              << std::setw(14) << g->codigo_grupo
                              << std::setw(35) << nomCorto
                              << std::setw(12) << g->clasificacion
                              << std::setw(20) << g->lider
                              << std::setw(8)  << (g->activo ? "[ACTIVO]" : "[INACT]") << "\n";
                    g = g->sigGrupo;
                }
                std::cout << "=========================================================================================\n";
                pausar();
            } else if (op == 2) {
                limpiarPantalla();
                std::cout << "--- INCLUIR NUEVO GRUPO (Ingrese 0 para cancelar) ---\n";
                std::string cod = leerLinea("Código MinCiencias (ej. COL0009999): ");
                if (cod == "0") continue;

                std::string nom = leerLinea("Nombre del Grupo: ");
                std::string clas = leerLinea("Clasificación (A1, A, B, C, Reconocido): ");
                std::string area = leerLinea("Área de Conocimiento: ");
                std::string lid = leerLinea("Nombre del Líder: ");
                int anio = leerEntero("Año de Creación: ");

                if (multi.insertarGrupo(cod, nom, clas, area, lid, anio, true)) {
                    historial.push("CREAR", "GRUPO", cod, "");
                    std::cout << "\n[OK] Grupo registrado exitosamente en memoria.\n";
                } else {
                    std::cout << "\n[!] Error: Ya existe un grupo con el código " << cod << "\n";
                }
                pausar();
            } else if (op == 3) {
                limpiarPantalla();
                std::cout << "--- CONSULTAR DETALLE DE GRUPO (Ingrese 0 para regresar) ---\n";
                std::string cod = leerLinea("Código del Grupo: ");
                if (cod == "0") continue;

                NodoGrupo* g = multi.buscarGrupo(cod);
                if (!g) {
                    std::cout << "\n[!] Grupo no encontrado.\n";
                } else {
                    std::cout << "\n=================================================================\n";
                    std::cout << "DETALLE DEL GRUPO: " << g->nombre << "\n";
                    std::cout << "Código: " << g->codigo_grupo << " | Clasificación: " << g->clasificacion << "\n";
                    std::cout << "Líder: " << g->lider << " | Área: " << g->area_conocimiento << " | Año: " << g->anio_creacion << "\n";
                    std::cout << "Estado: " << (g->activo ? "ACTIVO" : "DESACTIVADO (Borrado lógico)") << "\n";

                    std::cout << "\n  -- Investigadores Adscritos --\n";
                    NodoInvestigador* inv = g->primerInvestigador;
                    if (!inv) std::cout << "     (Sin investigadores registrados)\n";
                    while (inv) {
                        std::cout << "     • " << inv->nombre_completo << " (" << inv->categoria << ") - " 
                                  << (inv->activo ? "Activo" : "Inactivo") << "\n";
                        inv = inv->sigInvestigador;
                    }

                    std::cout << "\n  -- Productos Generados (Hipercubo) --\n";
                    NodoProducto* p = g->primerProducto;
                    if (!p) std::cout << "     (Sin productos registrados)\n";
                    while (p) {
                        std::cout << "     • [" << p->tipo << " " << p->anio << "] " << p->titulo 
                                  << " (Cat: " << p->categoria_minciencias << ", " 
                                  << (p->validado ? "Validado" : "No validado") << ") ["
                                  << (p->activo ? "Activo" : "Inactivo") << "]\n";
                        p = p->sigProductoGrupo;
                    }
                    std::cout << "=================================================================\n";
                }
                pausar();
            } else if (op == 4) {
                limpiarPantalla();
                std::cout << "--- MODIFICAR GRUPO (Ingrese 0 para regresar) ---\n";
                std::string cod = leerLinea("Código del Grupo a modificar: ");
                if (cod == "0") continue;

                NodoGrupo* g = multi.buscarGrupo(cod);
                if (!g) {
                    std::cout << "\n[!] Grupo no encontrado.\n";
                } else {
                    std::string prev = "nom=" + g->nombre + ";clas=" + g->clasificacion + ";lid=" + g->lider;
                    g->nombre = leerLinea("Nuevo Nombre (" + g->nombre + "): ");
                    g->clasificacion = leerLinea("Nueva Clasificación (" + g->clasificacion + "): ");
                    g->lider = leerLinea("Nuevo Líder (" + g->lider + "): ");
                    historial.push("MODIFICAR", "GRUPO", cod, prev);
                    std::cout << "\n[OK] Grupo modificado exitosamente.\n";
                }
                pausar();
            } else if (op == 5) {
                limpiarPantalla();
                std::cout << "--- DESACTIVAR / REACTIVAR GRUPO (Borrado Lógico) ---\n";
                std::string cod = leerLinea("Código del Grupo (0 para regresar): ");
                if (cod == "0") continue;

                NodoGrupo* g = multi.buscarGrupo(cod);
                if (!g) {
                    std::cout << "\n[!] Grupo no encontrado.\n";
                } else {
                    bool nuevoEstado = !g->activo;
                    multi.desactivarGrupo(cod, nuevoEstado);
                    historial.push("DESACTIVAR", "GRUPO", cod, nuevoEstado ? "desactivar" : "activar");
                    std::cout << "\n[OK] Estado lógico cambiado a: " << (nuevoEstado ? "ACTIVO" : "DESACTIVADO") << "\n";
                }
                pausar();
            } else if (op == 6) {
                limpiarPantalla();
                std::cout << "--- ELIMINAR GRUPO FÍSICAMENTE (Ingrese 0 para regresar) ---\n";
                std::string cod = leerLinea("Código del Grupo a ELIMINAR: ");
                if (cod == "0") continue;

                std::cout << "\n  [ADVERTENCIA] Se eliminará el grupo, sus investigadores y productos asociados.\n";
                if (leerEntero("¿Confirmar eliminación física definitiva? (1: Sí / 0: Cancelar): ", 0) == 1) {
                    if (multi.eliminarGrupo(cod)) {
                        historial.push("ELIMINAR", "GRUPO", cod, "");
                        std::cout << "\n[OK] Grupo y dependencias eliminados físicamente de memoria.\n";
                    } else {
                        std::cout << "\n[!] Grupo no encontrado.\n";
                    }
                } else {
                    std::cout << "\n[+] Operación cancelada.\n";
                }
                pausar();
            }
        }
    }

    // -----------------------------------------------------------------
    // CRUD: INVESTIGADORES
    // -----------------------------------------------------------------
    void menuInvestigadores() {
        int op = -1;
        while (op != 0) {
            limpiarPantalla();
            std::cout << "=================================================================\n";
            std::cout << "   PEA-i UPC > Menú Principal > Gestión de Investigadores        \n";
            std::cout << "=================================================================\n";
            std::cout << "  1. Listar Investigadores\n";
            std::cout << "  2. Incluir Nuevo Investigador\n";
            std::cout << "  3. Consultar Detalle (Productos Autorados)\n";
            std::cout << "  4. Modificar Investigador\n";
            std::cout << "  5. Desactivar / Reactivar Investigador (Borrado Lógico)\n";
            std::cout << "  6. Eliminar Investigador Físicamente\n";
            std::cout << "  0. Anterior / Regresar al Menú Principal\n";
            std::cout << "-----------------------------------------------------------------\n";
            op = leerEntero("Opción: ");

            if (op == 1) {
                limpiarPantalla();
                std::cout << "=================================================================================\n";
                std::cout << "                             LISTADO DE INVESTIGADORES                           \n";
                std::cout << "=================================================================================\n";
                std::cout << std::left 
                          << std::setw(15) << "DOCUMENTO/ID"
                          << std::setw(28) << "NOMBRE"
                          << std::setw(15) << "CATEGORIA"
                          << std::setw(15) << "GRUPO"
                          << std::setw(8)  << "ESTADO" << "\n";
                std::cout << std::string(81, '-') << "\n";
                NodoGrupo* g = multi.getCabezaGrupos();
                bool hayDatos = false;
                while (g) {
                    NodoInvestigador* inv = g->primerInvestigador;
                    while (inv) {
                        hayDatos = true;
                        std::cout << std::left 
                                  << std::setw(15) << inv->documento_id
                                  << std::setw(28) << inv->nombre_completo
                                  << std::setw(15) << inv->categoria
                                  << std::setw(15) << inv->codigo_grupo
                                  << std::setw(8)  << (inv->activo ? "[ACTIVO]" : "[INACT]") << "\n";
                        inv = inv->sigInvestigador;
                    }
                    g = g->sigGrupo;
                }
                if (!hayDatos) std::cout << "  (No hay investigadores registrados)\n";
                std::cout << "=================================================================================\n";
                pausar();
            } else if (op == 2) {
                limpiarPantalla();
                std::cout << "--- INCLUIR NUEVO INVESTIGADOR (Ingrese 0 para cancelar) ---\n";
                std::string codG = leerLinea("Código del Grupo al que pertenece: ");
                if (codG == "0") continue;

                if (!multi.buscarGrupo(codG)) {
                    std::cout << "\n[!] El grupo " << codG << " no existe. Debe crearlo primero.\n";
                    pausar();
                    continue;
                }
                std::string doc = leerLinea("Documento / ID CvLAC: ");
                if (doc == "0") continue;

                std::string nom = leerLinea("Nombre Completo: ");
                std::string cat = leerLinea("Categoría (Senior, Asociado, Junior, Sin Categoria): ");
                std::string form = leerLinea("Formación Académica: ");

                if (multi.insertarInvestigador(codG, doc, nom, cat, form, true)) {
                    historial.push("CREAR", "INVESTIGADOR", doc, codG);
                    std::cout << "\n[OK] Investigador registrado exitosamente.\n";
                } else {
                    std::cout << "\n[!] Error: Ya existe un investigador con ese documento.\n";
                }
                pausar();
            } else if (op == 3) {
                limpiarPantalla();
                std::cout << "--- CONSULTAR DETALLE DE INVESTIGADOR (Ingrese 0 para regresar) ---\n";
                std::string doc = leerLinea("Documento del Investigador: ");
                if (doc == "0") continue;

                NodoInvestigador* inv = multi.buscarInvestigador(doc);
                if (!inv) {
                    std::cout << "\n[!] Investigador no encontrado.\n";
                } else {
                    std::cout << "\n=================================================================\n";
                    std::cout << "INVESTIGADOR: " << inv->nombre_completo << "\n";
                    std::cout << "Documento: " << inv->documento_id << " | Categoría: " << inv->categoria << "\n";
                    std::cout << "Formación: " << inv->formacion_academica << " | Grupo: " << inv->codigo_grupo << "\n";
                    std::cout << "Estado: " << (inv->activo ? "ACTIVO" : "DESACTIVADO") << "\n";

                    std::cout << "\n  -- Producción Autorada (Hipercubo Ortogonal) --\n";
                    NodoProducto* p = inv->primerProducto;
                    if (!p) std::cout << "     (Sin productos asociados)\n";
                    while (p) {
                        std::cout << "     • [" << p->tipo << " " << p->anio << "] " << p->titulo 
                                  << " (Cat: " << p->categoria_minciencias << ", " 
                                  << (p->validado ? "Validado" : "No validado") << ") ["
                                  << (p->activo ? "Activo" : "Inactivo") << "]\n";
                        p = p->sigProductoInvestigador;
                    }
                    std::cout << "=================================================================\n";
                }
                pausar();
            } else if (op == 4) {
                limpiarPantalla();
                std::cout << "--- MODIFICAR INVESTIGADOR (Ingrese 0 para regresar) ---\n";
                std::string doc = leerLinea("Documento del Investigador: ");
                if (doc == "0") continue;

                NodoInvestigador* inv = multi.buscarInvestigador(doc);
                if (!inv) {
                    std::cout << "\n[!] Investigador no encontrado.\n";
                } else {
                    std::string prev = "nom=" + inv->nombre_completo + ";cat=" + inv->categoria;
                    inv->nombre_completo = leerLinea("Nuevo Nombre (" + inv->nombre_completo + "): ");
                    inv->categoria = leerLinea("Nueva Categoría (" + inv->categoria + "): ");
                    inv->formacion_academica = leerLinea("Nueva Formación (" + inv->formacion_academica + "): ");
                    historial.push("MODIFICAR", "INVESTIGADOR", doc, prev);
                    std::cout << "\n[OK] Investigador modificado exitosamente.\n";
                }
                pausar();
            } else if (op == 5) {
                limpiarPantalla();
                std::cout << "--- DESACTIVAR / REACTIVAR INVESTIGADOR (Borrado Lógico) ---\n";
                std::string doc = leerLinea("Documento del Investigador (0 para regresar): ");
                if (doc == "0") continue;

                NodoInvestigador* inv = multi.buscarInvestigador(doc);
                if (!inv) {
                    std::cout << "\n[!] Investigador no encontrado.\n";
                } else {
                    bool nuevo = !inv->activo;
                    multi.desactivarInvestigador(doc, nuevo);
                    historial.push("DESACTIVAR", "INVESTIGADOR", doc, nuevo ? "desactivar" : "activar");
                    std::cout << "\n[OK] Estado lógico cambiado a: " << (nuevo ? "ACTIVO" : "DESACTIVADO") << "\n";
                }
                pausar();
            } else if (op == 6) {
                limpiarPantalla();
                std::cout << "--- ELIMINAR INVESTIGADOR FÍSICAMENTE (Ingrese 0 para regresar) ---\n";
                std::string doc = leerLinea("Documento del Investigador a ELIMINAR: ");
                if (doc == "0") continue;

                if (leerEntero("¿Confirmar eliminación física? (1: Sí / 0: Cancelar): ", 0) == 1) {
                    if (multi.eliminarInvestigador(doc)) {
                        historial.push("ELIMINAR", "INVESTIGADOR", doc, "");
                        std::cout << "\n[OK] Investigador y sus productos eliminados de la memoria.\n";
                    } else {
                        std::cout << "\n[!] Investigador no encontrado.\n";
                    }
                } else {
                    std::cout << "\n[+] Operación cancelada.\n";
                }
                pausar();
            }
        }
    }

    // -----------------------------------------------------------------
    // CRUD: PRODUCTOS
    // -----------------------------------------------------------------
    void menuProductos() {
        int op = -1;
        while (op != 0) {
            limpiarPantalla();
            std::cout << "=================================================================\n";
            std::cout << "     PEA-i UPC > Menú Principal > Gestión de Productos           \n";
            std::cout << "=================================================================\n";
            std::cout << "  1. Listar Productos\n";
            std::cout << "  2. Incluir Nuevo Producto\n";
            std::cout << "  3. Consultar Detalle de Producto\n";
            std::cout << "  4. Modificar Producto (Categoría y Validación)\n";
            std::cout << "  5. Desactivar / Reactivar Producto (Borrado Lógico)\n";
            std::cout << "  6. Eliminar Producto Físicamente\n";
            std::cout << "  0. Anterior / Regresar al Menú Principal\n";
            std::cout << "-----------------------------------------------------------------\n";
            op = leerEntero("Opción: ");

            if (op == 1) {
                limpiarPantalla();
                std::cout << "===================================================================================\n";
                std::cout << "                            LISTADO DE PRODUCTOS DE INVESTIGACIÓN                  \n";
                std::cout << "===================================================================================\n";
                std::cout << std::left 
                          << std::setw(12) << "ID"
                          << std::setw(12) << "TIPO"
                          << std::setw(32) << "TITULO"
                          << std::setw(6)  << "AÑO"
                          << std::setw(6)  << "CAT"
                          << std::setw(7)  << "VAL"
                          << std::setw(8)  << "ESTADO" << "\n";
                std::cout << std::string(83, '-') << "\n";
                NodoGrupo* g = multi.getCabezaGrupos();
                bool hayDatos = false;
                while (g) {
                    NodoProducto* p = g->primerProducto;
                    while (p) {
                        hayDatos = true;
                        std::string titCorto = p->titulo.length() > 30 ? p->titulo.substr(0, 27) + "..." : p->titulo;
                        std::cout << std::left 
                                  << std::setw(12) << p->id_producto
                                  << std::setw(12) << p->tipo
                                  << std::setw(32) << titCorto
                                  << std::setw(6)  << p->anio
                                  << std::setw(6)  << p->categoria_minciencias
                                  << std::setw(7)  << (p->validado ? "SI" : "NO")
                                  << std::setw(8)  << (p->activo ? "[ACT]" : "[INA]") << "\n";
                        p = p->sigProductoGrupo;
                    }
                    g = g->sigGrupo;
                }
                if (!hayDatos) std::cout << "  (No hay productos registrados)\n";
                std::cout << "===================================================================================\n";
                pausar();
            } else if (op == 2) {
                limpiarPantalla();
                std::cout << "--- INCLUIR NUEVO PRODUCTO (Ingrese 0 para cancelar) ---\n";
                std::string codG = leerLinea("Código del Grupo asociado: ");
                if (codG == "0") continue;
                std::string idInv = leerLinea("Documento del Investigador autor: ");
                if (idInv == "0") continue;

                if (!multi.buscarGrupo(codG) || !multi.buscarInvestigador(idInv)) {
                    std::cout << "\n[!] Error: El Grupo o el Investigador no existen en la Multilista.\n";
                    pausar();
                    continue;
                }
                std::string idP = leerLinea("ID del Producto (ej. PROD-999): ");
                if (idP == "0") continue;

                std::string tipo = leerLinea("Tipo (Articulo, Libro, Capitulo, Software, Patente): ");
                std::string tit = leerLinea("Título de la obra: ");
                int anio = leerEntero("Año de publicación: ");
                std::string cat = leerLinea("Categoría MinCiencias (A1, A, B, C): ");
                int val = leerEntero("¿Validado/Avalado por MinCiencias? (1: Sí / 0: No): ", 0);

                if (multi.insertarProducto(codG, idInv, idP, tipo, tit, anio, cat, val == 1, true)) {
                    historial.push("CREAR", "PRODUCTO", idP, codG);
                    std::cout << "\n[OK] Producto registrado y enlazado ortogonalmente en el Hipercubo.\n";
                } else {
                    std::cout << "\n[!] Ya existe un producto con el ID " << idP << "\n";
                }
                pausar();
            } else if (op == 3) {
                limpiarPantalla();
                std::cout << "--- CONSULTAR DETALLE DE PRODUCTO (0 para regresar) ---\n";
                std::string idP = leerLinea("ID del Producto: ");
                if (idP == "0") continue;

                NodoProducto* p = multi.buscarProducto(idP);
                if (!p) {
                    std::cout << "\n[!] Producto no encontrado.\n";
                } else {
                    std::cout << "\n=================================================================\n";
                    std::cout << "PRODUCTO: [" << p->id_producto << "] " << p->titulo << "\n";
                    std::cout << "Tipo: " << p->tipo << " | Año: " << p->anio << "\n";
                    std::cout << "Categoría MinCiencias: " << p->categoria_minciencias 
                              << " | Aval MinCiencias: " << (p->validado ? "VALIDADO" : "NO VALIDADO") << "\n";
                    std::cout << "Grupo: " << p->codigo_grupo << " | Investigador Autor: " << p->id_investigador << "\n";
                    std::cout << "Estado: " << (p->activo ? "ACTIVO" : "DESACTIVADO") << "\n";
                    std::cout << "=================================================================\n";
                }
                pausar();
            } else if (op == 4) {
                limpiarPantalla();
                std::cout << "--- MODIFICAR PRODUCTO (0 para regresar) ---\n";
                std::string idP = leerLinea("ID del Producto a modificar: ");
                if (idP == "0") continue;

                NodoProducto* p = multi.buscarProducto(idP);
                if (!p) {
                    std::cout << "\n[!] Producto no encontrado.\n";
                } else {
                    std::string prev = "tit=" + p->titulo + ";cat=" + p->categoria_minciencias;
                    p->titulo = leerLinea("Nuevo Título (" + p->titulo + "): ");
                    p->anio = leerEntero("Nuevo Año: ");
                    p->categoria_minciencias = leerLinea("Nueva Categoría (" + p->categoria_minciencias + "): ");
                    p->validado = (leerEntero("¿Validado? (1: Sí / 0: No): ", 0) == 1);
                    historial.push("MODIFICAR", "PRODUCTO", idP, prev);
                    std::cout << "\n[OK] Producto actualizado exitosamente.\n";
                }
                pausar();
            } else if (op == 5) {
                limpiarPantalla();
                std::cout << "--- DESACTIVAR / REACTIVAR PRODUCTO (Borrado Lógico) ---\n";
                std::string idP = leerLinea("ID del Producto (0 para regresar): ");
                if (idP == "0") continue;

                NodoProducto* p = multi.buscarProducto(idP);
                if (!p) {
                    std::cout << "\n[!] Producto no encontrado.\n";
                } else {
                    bool nuevo = !p->activo;
                    multi.desactivarProducto(idP, nuevo);
                    historial.push("DESACTIVAR", "PRODUCTO", idP, nuevo ? "desactivar" : "activar");
                    std::cout << "\n[OK] Estado lógico cambiado a: " << (nuevo ? "ACTIVO" : "DESACTIVADO") << "\n";
                }
                pausar();
            } else if (op == 6) {
                limpiarPantalla();
                std::cout << "--- ELIMINAR PRODUCTO FÍSICAMENTE (0 para regresar) ---\n";
                std::string idP = leerLinea("ID del Producto a ELIMINAR: ");
                if (idP == "0") continue;

                if (leerEntero("¿Confirmar eliminación física? (1: Sí / 0: Cancelar): ", 0) == 1) {
                    if (multi.eliminarProducto(idP)) {
                        historial.push("ELIMINAR", "PRODUCTO", idP, "");
                        std::cout << "\n[OK] Producto desenlazado ortogonalmente y liberado de memoria.\n";
                    } else {
                        std::cout << "\n[!] Producto no encontrado.\n";
                    }
                } else {
                    std::cout << "\n[+] Operación cancelada.\n";
                }
                pausar();
            }
        }
    }

    // -----------------------------------------------------------------
    // DESHACER (PILA UNDO - LIFO)
    // -----------------------------------------------------------------
    void ejecutarDeshacer() {
        limpiarPantalla();
        std::cout << "=================================================================\n";
        std::cout << "           DESHACER ÚLTIMA ACCIÓN (TDA PILA - LIFO)              \n";
        std::cout << "=================================================================\n";

        AccionHistorial acc;
        if (!historial.pop(acc)) {
            std::cout << "\n[!] La Pila de historial está vacía. No hay acciones por deshacer.\n";
            pausar();
            return;
        }

        std::cout << "\n[<-- Deshacer] Revertiendo última acción: " 
                  << acc.tipo_operacion << " en " << acc.tipo_entidad << " (" << acc.id_registro << ")...\n";

        if (acc.tipo_operacion == "DESACTIVAR") {
            if (acc.tipo_entidad == "GRUPO") {
                NodoGrupo* g = multi.buscarGrupo(acc.id_registro);
                if (g) g->activo = !g->activo;
            } else if (acc.tipo_entidad == "INVESTIGADOR") {
                NodoInvestigador* inv = multi.buscarInvestigador(acc.id_registro);
                if (inv) inv->activo = !inv->activo;
            } else if (acc.tipo_entidad == "PRODUCTO") {
                NodoProducto* p = multi.buscarProducto(acc.id_registro);
                if (p) p->activo = !p->activo;
            }
            std::cout << "[OK] Estado lógico restaurado con éxito mediante pop() de la Pila.\n";
        } else if (acc.tipo_operacion == "CREAR") {
            if (acc.tipo_entidad == "GRUPO") multi.eliminarGrupo(acc.id_registro);
            else if (acc.tipo_entidad == "INVESTIGADOR") multi.eliminarInvestigador(acc.id_registro);
            else if (acc.tipo_entidad == "PRODUCTO") multi.eliminarProducto(acc.id_registro);
            std::cout << "[OK] Inserción revertida (registro retirado de memoria).\n";
        } else {
            std::cout << "[OK] Acción procesada desde la cima de la Pila.\n";
        }

        std::cout << "\nAcciones restantes en la Pila: " << historial.tamano() << "\n";
        pausar();
    }

    // -----------------------------------------------------------------
    // RESUMEN ESTADÍSTICO Y FILTRO POR VENTANA DE AÑOS
    // -----------------------------------------------------------------
    void menuEstadisticasYFiltro() {
        limpiarPantalla();
        std::cout << "=================================================================\n";
        std::cout << "           RESUMEN ESTADÍSTICO INSTITUCIONAL (SCIENTI - UPC)    \n";
        std::cout << "=================================================================\n";
        
        int totalGruposActivos = multi.contarGrupos(true);
        int totalGruposTotal = multi.contarGrupos(false);
        int totalInvActivos = multi.contarInvestigadores(true);
        int totalProdActivos = multi.contarProductos(true);

        std::cout << "• Grupos de Investigación:  " << totalGruposActivos << " activos (" << totalGruposTotal << " en total)\n";
        std::cout << "• Investigadores Activos:   " << totalInvActivos << "\n";
        std::cout << "• Productos Activos:        " << totalProdActivos << "\n";

        int articulos = 0, libros = 0, software = 0, capitulos = 0, patentes = 0;
        int catA1 = 0, catA = 0, catB = 0, catC = 0, validados = 0;

        NodoGrupo* g = multi.getCabezaGrupos();
        while (g) {
            NodoProducto* p = g->primerProducto;
            while (p) {
                if (p->activo && g->activo) {
                    if (p->tipo == "Articulo") articulos++;
                    else if (p->tipo == "Libro") libros++;
                    else if (p->tipo == "Software") software++;
                    else if (p->tipo == "Capitulo") capitulos++;
                    else if (p->tipo == "Patente") patentes++;

                    if (p->categoria_minciencias == "A1") catA1++;
                    else if (p->categoria_minciencias == "A") catA++;
                    else if (p->categoria_minciencias == "B") catB++;
                    else if (p->categoria_minciencias == "C") catC++;

                    if (p->validado) validados++;
                }
                p = p->sigProductoGrupo;
            }
            g = g->sigGrupo;
        }

        std::cout << "\n--- Desglose por Tipo de Producto ---\n";
        std::cout << "  - Artículos científicos: " << articulos << "\n";
        std::cout << "  - Libros / Obras:        " << libros << "\n";
        std::cout << "  - Capítulos de libro:    " << capitulos << "\n";
        std::cout << "  - Desarrollos software:  " << software << "\n";
        std::cout << "  - Patentes registradas:  " << patentes << "\n";

        std::cout << "\n--- Calidad MinCiencias & Validación ---\n";
        std::cout << "  - Categoría A1: " << catA1 << " | Categoría A: " << catA 
                  << " | Categoría B: " << catB << " | Categoría C: " << catC << "\n";
        std::cout << "  - Avalados por MinCiencias: " << validados 
                  << " (" << (totalProdActivos > 0 ? (validados * 100 / totalProdActivos) : 0) << "%)\n";

        // Filtro por ventana de años (Punto 10)
        std::cout << "\n-----------------------------------------------------------------\n";
        std::cout << "FILTRO POR VENTANA DE OBSERVACIÓN (Años MinCiencias)\n";
        std::cout << "  [1] Últimos 2 años (2024 - 2026)\n";
        std::cout << "  [2] Últimos 5 años (2021 - 2026)\n";
        std::cout << "  [3] Rango de años personalizado\n";
        std::cout << "  [0] Anterior / Regresar al Menú Principal\n";
        std::cout << "-----------------------------------------------------------------\n";
        int opFiltro = leerEntero("Opción: ", 0);

        int anioInicio = 0, anioFin = 9999;
        if (opFiltro == 1) {
            anioInicio = 2024; anioFin = 2026;
        } else if (opFiltro == 2) {
            anioInicio = 2021; anioFin = 2026;
        } else if (opFiltro == 3) {
            anioInicio = leerEntero("Año inicial: ");
            anioFin = leerEntero("Año final: ");
        } else {
            return; // Regresar
        }

        int prodsVentana = multi.contarProductosPorVentana(anioInicio, anioFin, true);
        std::cout << "\n[RESULTADO VENTANA " << anioInicio << " - " << anioFin << "]\n";
        std::cout << "Total de productos en la ventana: " << prodsVentana << "\n";
        std::cout << "\n" << std::left 
                  << std::setw(12) << "ID"
                  << std::setw(6)  << "AÑO"
                  << std::setw(12) << "TIPO"
                  << std::setw(35) << "TITULO"
                  << std::setw(14) << "GRUPO" << "\n";
        std::cout << std::string(79, '-') << "\n";

        g = multi.getCabezaGrupos();
        while (g) {
            NodoProducto* p = g->primerProducto;
            while (p) {
                if (p->activo && g->activo && p->anio >= anioInicio && p->anio <= anioFin) {
                    std::string titCorto = p->titulo.length() > 33 ? p->titulo.substr(0, 30) + "..." : p->titulo;
                    std::cout << std::left 
                              << std::setw(12) << p->id_producto
                              << std::setw(6)  << p->anio
                              << std::setw(12) << p->tipo
                              << std::setw(35) << titCorto
                              << std::setw(14) << p->codigo_grupo << "\n";
                }
                p = p->sigProductoGrupo;
            }
            g = g->sigGrupo;
        }
        std::cout << "=================================================================\n";
        pausar();
    }

    void guardarEnBD() {
        limpiarPantalla();
        std::cout << "=================================================================\n";
        std::cout << "       PERSISTENCIA: GUARDAR DATOS EN SQLITE (data.db)           \n";
        std::cout << "=================================================================\n";
        std::cout << "[+] Sincronizando Multilista en memoria con SQLite...\n";
        if (GestorSQLite::guardarEnBD(multi, rutaBD)) {
            std::cout << "[OK] Todos los registros fueron persistidos exitosamente en " << rutaBD << "\n";
        } else {
            std::cout << "[!] Error al guardar datos en SQLite.\n";
        }
        pausar();
    }
};

#endif // CONSOLA_APP_H
