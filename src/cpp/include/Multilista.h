#ifndef MULTILISTA_H
#define MULTILISTA_H

#include "Nodo.h"
#include <iostream>
#include <string>
#include <cctype>
#include <cstdlib>

// =====================================================================
// TDA MULTILISTA / HIPERCUBO DE INFORMACIÓN
// Enlace Ortogonal tridimensional: Grupos <-> Investigadores <-> Productos
// =====================================================================

class Multilista {
private:
    NodoGrupo* cabezaGrupos;

public:
    Multilista() : cabezaGrupos(nullptr) {}

    ~Multilista() {
        liberar();
    }

    NodoGrupo* getCabezaGrupos() const {
        return cabezaGrupos;
    }

    // -----------------------------------------------------------------
    // 1. INSERCIÓN
    // -----------------------------------------------------------------

    // Inserta un Grupo al inicio de la lista de grupos (O(1) o O(n) verificando duplicado)
    bool insertarGrupo(const std::string& cod, const std::string& nom,
                       const std::string& clas, const std::string& area,
                       const std::string& lid, int anio, bool act = true) {
        if (buscarGrupo(cod) != nullptr) {
            return false; // Ya existe
        }
        NodoGrupo* nuevo = new NodoGrupo(cod, nom, clas, area, lid, anio, act);
        nuevo->sigGrupo = cabezaGrupos;
        cabezaGrupos = nuevo;
        return true;
    }

    // Inserta un Investigador dentro de su Grupo correspondiente
    bool insertarInvestigador(const std::string& cod_grupo, const std::string& doc,
                              const std::string& nom, const std::string& cat,
                              const std::string& form, bool act = true) {
        NodoGrupo* grupo = buscarGrupo(cod_grupo);
        if (!grupo) return false;

        if (buscarInvestigador(doc) != nullptr) {
            return false; // Ya existe con ese documento
        }

        NodoInvestigador* nuevo = new NodoInvestigador(doc, nom, cat, form, cod_grupo, act);
        nuevo->sigInvestigador = grupo->primerInvestigador;
        grupo->primerInvestigador = nuevo;
        return true;
    }

    // Inserta un Producto enlazándolo ortogonalmente al Grupo y al Investigador
    bool insertarProducto(const std::string& cod_grupo, const std::string& id_inv,
                          const std::string& id_prod, const std::string& tipo,
                          const std::string& titulo, int anio,
                          const std::string& cat_min, bool val, bool act = true) {
        NodoGrupo* grupo = buscarGrupo(cod_grupo);
        NodoInvestigador* inv = buscarInvestigador(id_inv);

        if (!grupo || !inv) return false;
        if (buscarProducto(id_prod) != nullptr) return false;

        // Se crea una única instancia física en memoria
        NodoProducto* nuevo = new NodoProducto(id_prod, tipo, titulo, anio, cat_min, val,
                                               cod_grupo, id_inv, act);

        // 1. Enlace ortogonal en la dimensión Grupo
        nuevo->sigProductoGrupo = grupo->primerProducto;
        grupo->primerProducto = nuevo;

        // 2. Enlace ortogonal en la dimensión Investigador
        nuevo->sigProductoInvestigador = inv->primerProducto;
        inv->primerProducto = nuevo;

        return true;
    }

    // -----------------------------------------------------------------
    // 2. BÚSQUEDA
    // -----------------------------------------------------------------

    NodoGrupo* buscarGrupo(const std::string& cod) const {
        NodoGrupo* act = cabezaGrupos;
        while (act != nullptr) {
            if (act->codigo_grupo == cod) return act;
            act = act->sigGrupo;
        }
        return nullptr;
    }

    NodoInvestigador* buscarInvestigador(const std::string& doc) const {
        NodoGrupo* g = cabezaGrupos;
        while (g != nullptr) {
            NodoInvestigador* inv = g->primerInvestigador;
            while (inv != nullptr) {
                if (inv->documento_id == doc) return inv;
                inv = inv->sigInvestigador;
            }
            g = g->sigGrupo;
        }
        return nullptr;
    }

    NodoProducto* buscarProducto(const std::string& id_prod) const {
        NodoGrupo* g = cabezaGrupos;
        while (g != nullptr) {
            NodoProducto* p = g->primerProducto;
            while (p != nullptr) {
                if (p->id_producto == id_prod) return p;
                p = p->sigProductoGrupo;
            }
            g = g->sigGrupo;
        }
        return nullptr;
    }

    // -----------------------------------------------------------------
    // BÚSQUEDA INTELIGENTE (POR TEXTO O EJEMPLO ALEATORIO)
    // -----------------------------------------------------------------

    static bool contieneSubcadena(std::string texto, std::string sub) {
        if (sub.empty()) return true;
        for (char &c : texto) c = std::tolower(static_cast<unsigned char>(c));
        for (char &c : sub) c = std::tolower(static_cast<unsigned char>(c));
        return texto.find(sub) != std::string::npos;
    }

    // Búsqueda inteligente por código o subcadena de nombre/líder
    NodoGrupo* buscarGrupoPorTexto(const std::string& termino) const {
        if (termino.empty()) return nullptr;
        NodoGrupo* exacto = buscarGrupo(termino);
        if (exacto) return exacto;

        NodoGrupo* act = cabezaGrupos;
        while (act != nullptr) {
            if (contieneSubcadena(act->nombre, termino) || contieneSubcadena(act->codigo_grupo, termino) || contieneSubcadena(act->lider, termino)) {
                return act;
            }
            act = act->sigGrupo;
        }
        return nullptr;
    }

    // Obtener un grupo de ejemplo aleatorio
    NodoGrupo* obtenerGrupoAleatorio() const {
        int total = contarGrupos(false);
        if (total == 0) return nullptr;
        int target = std::rand() % total;
        NodoGrupo* act = cabezaGrupos;
        for (int i = 0; i < target && act != nullptr; ++i) {
            act = act->sigGrupo;
        }
        return act ? act : cabezaGrupos;
    }

    // Búsqueda inteligente de investigador por documento o nombre
    NodoInvestigador* buscarInvestigadorPorTexto(const std::string& termino) const {
        if (termino.empty()) return nullptr;
        NodoInvestigador* exacto = buscarInvestigador(termino);
        if (exacto) return exacto;

        NodoGrupo* g = cabezaGrupos;
        while (g != nullptr) {
            NodoInvestigador* inv = g->primerInvestigador;
            while (inv != nullptr) {
                if (contieneSubcadena(inv->nombre_completo, termino) || contieneSubcadena(inv->documento_id, termino)) {
                    return inv;
                }
                inv = inv->sigInvestigador;
            }
            g = g->sigGrupo;
        }
        return nullptr;
    }

    // Obtener un investigador de ejemplo aleatorio
    NodoInvestigador* obtenerInvestigadorAleatorio() const {
        int total = contarInvestigadores(false);
        if (total == 0) return nullptr;
        int target = std::rand() % total;
        int contador = 0;
        NodoGrupo* g = cabezaGrupos;
        while (g != nullptr) {
            NodoInvestigador* inv = g->primerInvestigador;
            while (inv != nullptr) {
                if (contador == target) return inv;
                contador++;
                inv = inv->sigInvestigador;
            }
            g = g->sigGrupo;
        }
        return (cabezaGrupos && cabezaGrupos->primerInvestigador) ? cabezaGrupos->primerInvestigador : nullptr;
    }

    // Búsqueda inteligente de producto por ID o título
    NodoProducto* buscarProductoPorTexto(const std::string& termino) const {
        if (termino.empty()) return nullptr;
        NodoProducto* exacto = buscarProducto(termino);
        if (exacto) return exacto;

        NodoGrupo* g = cabezaGrupos;
        while (g != nullptr) {
            NodoProducto* p = g->primerProducto;
            while (p != nullptr) {
                if (contieneSubcadena(p->titulo, termino) || contieneSubcadena(p->id_producto, termino) || contieneSubcadena(p->tipo, termino)) {
                    return p;
                }
                p = p->sigProductoGrupo;
            }
            g = g->sigGrupo;
        }
        return nullptr;
    }

    // Obtener un producto de ejemplo aleatorio
    NodoProducto* obtenerProductoAleatorio() const {
        int total = contarProductos(false);
        if (total == 0) return nullptr;
        int target = std::rand() % total;
        int contador = 0;
        NodoGrupo* g = cabezaGrupos;
        while (g != nullptr) {
            NodoProducto* p = g->primerProducto;
            while (p != nullptr) {
                if (contador == target) return p;
                contador++;
                p = p->sigProductoGrupo;
            }
            g = g->sigGrupo;
        }
        return (cabezaGrupos && cabezaGrupos->primerProducto) ? cabezaGrupos->primerProducto : nullptr;
    }

    // -----------------------------------------------------------------
    // 3. DESACTIVACIÓN (Borrado Lógico)
    // -----------------------------------------------------------------

    bool desactivarGrupo(const std::string& cod, bool estado = false) {
        NodoGrupo* g = buscarGrupo(cod);
        if (!g) return false;
        g->activo = estado;
        return true;
    }

    bool desactivarInvestigador(const std::string& doc, bool estado = false) {
        NodoInvestigador* inv = buscarInvestigador(doc);
        if (!inv) return false;
        inv->activo = estado;
        return true;
    }

    bool desactivarProducto(const std::string& id_prod, bool estado = false) {
        NodoProducto* p = buscarProducto(id_prod);
        if (!p) return false;
        p->activo = estado;
        return true;
    }

    // -----------------------------------------------------------------
    // 4. ELIMINACIÓN FÍSICA (Desvinculación ortogonal y liberación de memoria)
    // -----------------------------------------------------------------

    // Elimina un producto desenlazándolo de ambas dimensiones
    bool eliminarProducto(const std::string& id_prod) {
        NodoProducto* target = buscarProducto(id_prod);
        if (!target) return false;

        NodoGrupo* grupo = buscarGrupo(target->codigo_grupo);
        NodoInvestigador* inv = buscarInvestigador(target->id_investigador);

        // 1. Desenlazar del Grupo
        if (grupo) {
            if (grupo->primerProducto == target) {
                grupo->primerProducto = target->sigProductoGrupo;
            } else {
                NodoProducto* ant = grupo->primerProducto;
                while (ant && ant->sigProductoGrupo != target) {
                    ant = ant->sigProductoGrupo;
                }
                if (ant) ant->sigProductoGrupo = target->sigProductoGrupo;
            }
        }

        // 2. Desenlazar del Investigador
        if (inv) {
            if (inv->primerProducto == target) {
                inv->primerProducto = target->sigProductoInvestigador;
            } else {
                NodoProducto* ant = inv->primerProducto;
                while (ant && ant->sigProductoInvestigador != target) {
                    ant = ant->sigProductoInvestigador;
                }
                if (ant) ant->sigProductoInvestigador = target->sigProductoInvestigador;
            }
        }

        delete target;
        return true;
    }

    // Elimina un investigador y sus productos autorados
    bool eliminarInvestigador(const std::string& doc) {
        NodoInvestigador* target = buscarInvestigador(doc);
        if (!target) return false;

        NodoGrupo* grupo = buscarGrupo(target->codigo_grupo);
        if (!grupo) return false;

        // Eliminar físicamente los productos asociados a este autor
        while (target->primerProducto != nullptr) {
            eliminarProducto(target->primerProducto->id_producto);
        }

        // Desenlazar del grupo
        if (grupo->primerInvestigador == target) {
            grupo->primerInvestigador = target->sigInvestigador;
        } else {
            NodoInvestigador* ant = grupo->primerInvestigador;
            while (ant && ant->sigInvestigador != target) {
                ant = ant->sigInvestigador;
            }
            if (ant) ant->sigInvestigador = target->sigInvestigador;
        }

        delete target;
        return true;
    }

    // Elimina un grupo y toda su cascada (investigadores y productos)
    bool eliminarGrupo(const std::string& cod) {
        NodoGrupo* target = buscarGrupo(cod);
        if (!target) return false;

        // Eliminar todos sus investigadores (que a su vez eliminan sus productos)
        while (target->primerInvestigador != nullptr) {
            eliminarInvestigador(target->primerInvestigador->documento_id);
        }

        // Desenlazar de la lista principal de grupos
        if (cabezaGrupos == target) {
            cabezaGrupos = target->sigGrupo;
        } else {
            NodoGrupo* ant = cabezaGrupos;
            while (ant && ant->sigGrupo != target) {
                ant = ant->sigGrupo;
            }
            if (ant) ant->sigGrupo = target->sigGrupo;
        }

        delete target;
        return true;
    }

    // -----------------------------------------------------------------
    // 5. ESTADÍSTICAS Y VENTANA DE OBSERVACIÓN
    // -----------------------------------------------------------------

    int contarGrupos(bool soloActivos = true) const {
        int c = 0;
        NodoGrupo* g = cabezaGrupos;
        while (g != nullptr) {
            if (!soloActivos || g->activo) c++;
            g = g->sigGrupo;
        }
        return c;
    }

    int contarInvestigadores(bool soloActivos = true) const {
        int c = 0;
        NodoGrupo* g = cabezaGrupos;
        while (g != nullptr) {
            NodoInvestigador* inv = g->primerInvestigador;
            while (inv != nullptr) {
                if (!soloActivos || (inv->activo && g->activo)) c++;
                inv = inv->sigInvestigador;
            }
            g = g->sigGrupo;
        }
        return c;
    }

    int contarProductos(bool soloActivos = true) const {
        int c = 0;
        NodoGrupo* g = cabezaGrupos;
        while (g != nullptr) {
            NodoProducto* p = g->primerProducto;
            while (p != nullptr) {
                if (!soloActivos || (p->activo && g->activo)) c++;
                p = p->sigProductoGrupo;
            }
            g = g->sigGrupo;
        }
        return c;
    }

    // Filtro por ventana de observación (rango de años)
    int contarProductosPorVentana(int anioInicio, int anioFin, bool soloActivos = true) const {
        int c = 0;
        NodoGrupo* g = cabezaGrupos;
        while (g != nullptr) {
            NodoProducto* p = g->primerProducto;
            while (p != nullptr) {
                if ((!soloActivos || (p->activo && g->activo)) &&
                    (p->anio >= anioInicio && p->anio <= anioFin)) {
                    c++;
                }
                p = p->sigProductoGrupo;
            }
            g = g->sigGrupo;
        }
        return c;
    }

    // -----------------------------------------------------------------
    // 6. LIBERACIÓN COMPLETA DE MEMORIA
    // -----------------------------------------------------------------
    void liberar() {
        while (cabezaGrupos != nullptr) {
            eliminarGrupo(cabezaGrupos->codigo_grupo);
        }
    }
};

#endif // MULTILISTA_H
