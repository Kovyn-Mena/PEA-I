#include <iostream>
#include <sqlite3.h>
#include <string>

// Test de conectividad C++ <-> SQLite (Contrato Fase 0)
int main() {
    std::cout << "========================================\n";
    std::cout << "[C++] Test de Conectividad SQLite3\n";
    std::cout << "========================================\n";

    sqlite3* db = nullptr;
    const std::string db_path = "data/pea_investigacion.db";

    int rc = sqlite3_open(db_path.c_str(), &db);
    if (rc != SQLITE_OK) {
        std::cerr << "[ERROR C++] No se pudo abrir la BD: " << sqlite3_errmsg(db) << "\n";
        return 1;
    }
    std::cout << "[OK C++] Base de datos abierta exitosamente: " << db_path << "\n\n";

    // Consulta de prueba a Grupos
    const char* sql = "SELECT codigo_grupo, nombre, clasificacion, anio_creacion FROM Grupos WHERE activo = 1;";
    sqlite3_stmt* stmt = nullptr;

    rc = sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr);
    if (rc != SQLITE_OK) {
        std::cerr << "[ERROR C++] Error al preparar la consulta: " << sqlite3_errmsg(db) << "\n";
        sqlite3_close(db);
        return 1;
    }

    std::cout << "--- Grupos Registrados (Activos) ---\n";
    while (sqlite3_step(stmt) == SQLITE_ROW) {
        std::string codigo = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 0));
        std::string nombre = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 1));
        std::string clasif = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 2));
        int anio = sqlite3_column_int(stmt, 3);

        std::cout << "• [" << codigo << "] " << nombre << " | Clasif: " << clasif << " | Creación: " << anio << "\n";
    }

    sqlite3_finalize(stmt);
    sqlite3_close(db);
    std::cout << "\n[OK C++] Prueba finalizada exitosamente sin fugas.\n";
    return 0;
}
