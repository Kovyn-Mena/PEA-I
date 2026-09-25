#ifndef NODO_H
#define NODO_H

#include <string>

// =====================================================================
// DEFINICIÓN DE ENTIDADES Y NODOS PARA EL HIPERCUBO DE INFORMACIÓN
// Modelado mediante Multilista jerárquica ortogonal basada en punteros
// =====================================================================

// ---------------------------------------------------------------------
// 1. Nodo de Producto de Investigación (Dimensión 3: Producción)
// ---------------------------------------------------------------------
struct NodoProducto {
    std::string id_producto;
    std::string tipo;                 // Articulo, Libro, Capitulo, Software, Patente
    std::string titulo;
    int anio;
    std::string categoria_minciencias;// A1, A, B, C
    bool validado;                    // true: avalado por MinCiencias, false: no
    std::string codigo_grupo;
    std::string id_investigador;
    bool activo;                      // true: activo, false: desactivado (borrado lógico)

    // Punteros ortogonales (Hipercubo multidimensional)
    NodoProducto* sigProductoGrupo;        // Siguiente producto en el mismo Grupo
    NodoProducto* sigProductoInvestigador; // Siguiente producto del mismo Investigador

    // Constructor para inicialización limpia
    NodoProducto(const std::string& id, const std::string& tp, const std::string& tit,
                 int a, const std::string& cat, bool val,
                 const std::string& cod_g, const std::string& id_inv, bool act = true)
        : id_producto(id), tipo(tp), titulo(tit), anio(a), categoria_minciencias(cat),
          validado(val), codigo_grupo(cod_g), id_investigador(id_inv), activo(act),
          sigProductoGrupo(nullptr), sigProductoInvestigador(nullptr) {}
};

// ---------------------------------------------------------------------
// 2. Nodo de Investigador (Dimensión 2: Talento Humano)
// ---------------------------------------------------------------------
struct NodoInvestigador {
    std::string documento_id;
    std::string nombre_completo;
    std::string categoria;            // Senior, Asociado, Junior, Sin Categoria
    std::string formacion_academica;
    std::string codigo_grupo;
    bool activo;                      // true: activo, false: desactivado

    NodoInvestigador* sigInvestigador;// Siguiente investigador en el grupo
    NodoProducto* primerProducto;     // Sublista de productos generados por este autor

    NodoInvestigador(const std::string& doc, const std::string& nom,
                     const std::string& cat, const std::string& form,
                     const std::string& cod_g, bool act = true)
        : documento_id(doc), nombre_completo(nom), categoria(cat),
          formacion_academica(form), codigo_grupo(cod_g), activo(act),
          sigInvestigador(nullptr), primerProducto(nullptr) {}
};

// ---------------------------------------------------------------------
// 3. Nodo de Grupo de Investigación (Dimensión 1: Unidades de Investigación)
// ---------------------------------------------------------------------
struct NodoGrupo {
    std::string codigo_grupo;
    std::string nombre;
    std::string clasificacion;        // A1, A, B, C, Reconocido
    std::string area_conocimiento;
    std::string lider;
    int anio_creacion;
    bool activo;                      // true: activo, false: desactivado

    NodoGrupo* sigGrupo;              // Siguiente grupo en la lista principal
    NodoInvestigador* primerInvestigador; // Sublista de investigadores adscritos
    NodoProducto* primerProducto;     // Sublista de todos los productos del grupo

    NodoGrupo(const std::string& cod, const std::string& nom,
              const std::string& clas, const std::string& area,
              const std::string& lid, int anio, bool act = true)
        : codigo_grupo(cod), nombre(nom), clasificacion(clas),
          area_conocimiento(area), lider(lid), anio_creacion(anio), activo(act),
          sigGrupo(nullptr), primerInvestigador(nullptr), primerProducto(nullptr) {}
};

#endif // NODO_H
