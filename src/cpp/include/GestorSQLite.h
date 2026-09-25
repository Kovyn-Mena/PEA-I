#ifndef GESTOR_SQLITE_H
#define GESTOR_SQLITE_H

#include <iostream>
#include <string>
#include <sqlite3.h>
#include "Multilista.h"

// =====================================================================
// GESTOR DE PERSISTENCIA SQLITE (C++)
// Conecta el contrato de base de datos con la Multilista en memoria RAM
// =====================================================================

class GestorSQLite {
public:
    // Carga todos los Grupos, Investigadores y Productos desde SQLite a la Multilista
    static bool cargarDesdeBD(Multilista& multi, const std::string& rutaBD = "data/pea_investigacion.db") {
        sqlite3* db = nullptr;
        if (sqlite3_open(rutaBD.c_str(), &db) != SQLITE_OK) {
            std::cerr << "[ERROR Persistencia] No se pudo abrir la BD: " << sqlite3_errmsg(db) << "\n";
            return false;
        }

        // 1. Cargar Grupos
        const char* sqlGrupos = "SELECT codigo_grupo, nombre, clasificacion, area_conocimiento, lider, anio_creacion, activo FROM Grupos;";
        sqlite3_stmt* stmtG = nullptr;
        if (sqlite3_prepare_v2(db, sqlGrupos, -1, &stmtG, nullptr) == SQLITE_OK) {
            while (sqlite3_step(stmtG) == SQLITE_ROW) {
                std::string cod = reinterpret_cast<const char*>(sqlite3_column_text(stmtG, 0));
                std::string nom = reinterpret_cast<const char*>(sqlite3_column_text(stmtG, 1));
                std::string clas = reinterpret_cast<const char*>(sqlite3_column_text(stmtG, 2));
                std::string area = reinterpret_cast<const char*>(sqlite3_column_text(stmtG, 3));
                std::string lid = reinterpret_cast<const char*>(sqlite3_column_text(stmtG, 4));
                int anio = sqlite3_column_int(stmtG, 5);
                bool act = sqlite3_column_int(stmtG, 6) != 0;

                multi.insertarGrupo(cod, nom, clas, area, lid, anio, act);
            }
            sqlite3_finalize(stmtG);
        }

        // 2. Cargar Investigadores
        const char* sqlInv = "SELECT documento_id, nombre_completo, categoria, formacion_academica, codigo_grupo, activo FROM Investigadores;";
        sqlite3_stmt* stmtI = nullptr;
        if (sqlite3_prepare_v2(db, sqlInv, -1, &stmtI, nullptr) == SQLITE_OK) {
            while (sqlite3_step(stmtI) == SQLITE_ROW) {
                std::string doc = reinterpret_cast<const char*>(sqlite3_column_text(stmtI, 0));
                std::string nom = reinterpret_cast<const char*>(sqlite3_column_text(stmtI, 1));
                std::string cat = reinterpret_cast<const char*>(sqlite3_column_text(stmtI, 2));
                std::string form = reinterpret_cast<const char*>(sqlite3_column_text(stmtI, 3));
                std::string cod_g = reinterpret_cast<const char*>(sqlite3_column_text(stmtI, 4));
                bool act = sqlite3_column_int(stmtI, 5) != 0;

                multi.insertarInvestigador(cod_g, doc, nom, cat, form, act);
            }
            sqlite3_finalize(stmtI);
        }

        // 3. Cargar Productos
        const char* sqlProd = "SELECT id_producto, tipo, titulo, anio, categoria_minciencias, validado, codigo_grupo, id_investigador, activo FROM Productos;";
        sqlite3_stmt* stmtP = nullptr;
        if (sqlite3_prepare_v2(db, sqlProd, -1, &stmtP, nullptr) == SQLITE_OK) {
            while (sqlite3_step(stmtP) == SQLITE_ROW) {
                std::string id_p = reinterpret_cast<const char*>(sqlite3_column_text(stmtP, 0));
                std::string tipo = reinterpret_cast<const char*>(sqlite3_column_text(stmtP, 1));
                std::string tit = reinterpret_cast<const char*>(sqlite3_column_text(stmtP, 2));
                int anio = sqlite3_column_int(stmtP, 3);
                std::string cat_m = reinterpret_cast<const char*>(sqlite3_column_text(stmtP, 4));
                bool val = sqlite3_column_int(stmtP, 5) != 0;
                std::string cod_g = reinterpret_cast<const char*>(sqlite3_column_text(stmtP, 6));
                std::string id_inv = reinterpret_cast<const char*>(sqlite3_column_text(stmtP, 7));
                bool act = sqlite3_column_int(stmtP, 8) != 0;

                multi.insertarProducto(cod_g, id_inv, id_p, tipo, tit, anio, cat_m, val, act);
            }
            sqlite3_finalize(stmtP);
        }

        sqlite3_close(db);
        return true;
    }

    // Guarda el estado completo de la Multilista en SQLite usando una transacción atómica
    static bool guardarEnBD(const Multilista& multi, const std::string& rutaBD = "data/pea_investigacion.db") {
        sqlite3* db = nullptr;
        if (sqlite3_open(rutaBD.c_str(), &db) != SQLITE_OK) {
            std::cerr << "[ERROR Persistencia] No se pudo abrir la BD para guardar: " << sqlite3_errmsg(db) << "\n";
            return false;
        }

        char* errMsg = nullptr;
        sqlite3_exec(db, "PRAGMA foreign_keys = OFF;", nullptr, nullptr, nullptr);
        sqlite3_exec(db, "BEGIN TRANSACTION;", nullptr, nullptr, nullptr);

        // Limpiar tablas para sincronización completa
        sqlite3_exec(db, "DELETE FROM Productos;", nullptr, nullptr, nullptr);
        sqlite3_exec(db, "DELETE FROM Investigadores;", nullptr, nullptr, nullptr);
        sqlite3_exec(db, "DELETE FROM Grupos;", nullptr, nullptr, nullptr);

        // 1. Insertar Grupos
        const char* sqlInsG = "INSERT INTO Grupos (codigo_grupo, nombre, clasificacion, area_conocimiento, lider, anio_creacion, activo) VALUES (?, ?, ?, ?, ?, ?, ?);";
        sqlite3_stmt* stmtG = nullptr;
        sqlite3_prepare_v2(db, sqlInsG, -1, &stmtG, nullptr);

        // 2. Insertar Investigadores
        const char* sqlInsI = "INSERT INTO Investigadores (documento_id, nombre_completo, categoria, formacion_academica, codigo_grupo, activo) VALUES (?, ?, ?, ?, ?, ?);";
        sqlite3_stmt* stmtI = nullptr;
        sqlite3_prepare_v2(db, sqlInsI, -1, &stmtI, nullptr);

        // 3. Insertar Productos
        const char* sqlInsP = "INSERT INTO Productos (id_producto, tipo, titulo, anio, categoria_minciencias, validado, codigo_grupo, id_investigador, activo) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);";
        sqlite3_stmt* stmtP = nullptr;
        sqlite3_prepare_v2(db, sqlInsP, -1, &stmtP, nullptr);

        NodoGrupo* g = multi.getCabezaGrupos();
        while (g != nullptr) {
            // Bind Grupo
            sqlite3_bind_text(stmtG, 1, g->codigo_grupo.c_str(), -1, SQLITE_TRANSIENT);
            sqlite3_bind_text(stmtG, 2, g->nombre.c_str(), -1, SQLITE_TRANSIENT);
            sqlite3_bind_text(stmtG, 3, g->clasificacion.c_str(), -1, SQLITE_TRANSIENT);
            sqlite3_bind_text(stmtG, 4, g->area_conocimiento.c_str(), -1, SQLITE_TRANSIENT);
            sqlite3_bind_text(stmtG, 5, g->lider.c_str(), -1, SQLITE_TRANSIENT);
            sqlite3_bind_int(stmtG, 6, g->anio_creacion);
            sqlite3_bind_int(stmtG, 7, g->activo ? 1 : 0);
            sqlite3_step(stmtG);
            sqlite3_reset(stmtG);

            // Investigadores del Grupo
            NodoInvestigador* inv = g->primerInvestigador;
            while (inv != nullptr) {
                sqlite3_bind_text(stmtI, 1, inv->documento_id.c_str(), -1, SQLITE_TRANSIENT);
                sqlite3_bind_text(stmtI, 2, inv->nombre_completo.c_str(), -1, SQLITE_TRANSIENT);
                sqlite3_bind_text(stmtI, 3, inv->categoria.c_str(), -1, SQLITE_TRANSIENT);
                sqlite3_bind_text(stmtI, 4, inv->formacion_academica.c_str(), -1, SQLITE_TRANSIENT);
                sqlite3_bind_text(stmtI, 5, inv->codigo_grupo.c_str(), -1, SQLITE_TRANSIENT);
                sqlite3_bind_int(stmtI, 6, inv->activo ? 1 : 0);
                sqlite3_step(stmtI);
                sqlite3_reset(stmtI);

                inv = inv->sigInvestigador;
            }

            // Productos del Grupo
            NodoProducto* p = g->primerProducto;
            while (p != nullptr) {
                sqlite3_bind_text(stmtP, 1, p->id_producto.c_str(), -1, SQLITE_TRANSIENT);
                sqlite3_bind_text(stmtP, 2, p->tipo.c_str(), -1, SQLITE_TRANSIENT);
                sqlite3_bind_text(stmtP, 3, p->titulo.c_str(), -1, SQLITE_TRANSIENT);
                sqlite3_bind_int(stmtP, 4, p->anio);
                sqlite3_bind_text(stmtP, 5, p->categoria_minciencias.c_str(), -1, SQLITE_TRANSIENT);
                sqlite3_bind_int(stmtP, 6, p->validado ? 1 : 0);
                sqlite3_bind_text(stmtP, 7, p->codigo_grupo.c_str(), -1, SQLITE_TRANSIENT);
                sqlite3_bind_text(stmtP, 8, p->id_investigador.c_str(), -1, SQLITE_TRANSIENT);
                sqlite3_bind_int(stmtP, 9, p->activo ? 1 : 0);
                sqlite3_step(stmtP);
                sqlite3_reset(stmtP);

                p = p->sigProductoGrupo;
            }

            g = g->sigGrupo;
        }

        sqlite3_finalize(stmtG);
        sqlite3_finalize(stmtI);
        sqlite3_finalize(stmtP);

        sqlite3_exec(db, "COMMIT;", nullptr, nullptr, nullptr);
        sqlite3_exec(db, "PRAGMA foreign_keys = ON;", nullptr, nullptr, &errMsg);

        sqlite3_close(db);
        return true;
    }
};

#endif // GESTOR_SQLITE_H
