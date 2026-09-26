// =====================================================================
// UNIVERSIDAD POPULAR DEL CESAR - FACULTAD DE INGENIERÍA Y TECNOLÓGICAS
// ASIGNATURA: ESTRUCTURA DE DATOS (TALLER 2) - 2026-I
// DOCENTE: ING. ADITH PÉREZ
// ARCHIVO DE ENTREGA PRINCIPAL C++: Taller2_AB_PO_XX.cpp
//
// INSTRUCCIONES DE COMPILACIÓN:
//   Opción A (Recomendada con Makefile):
//       make
//       make run
//   Opción B (Compilación directa con g++):
//       g++ -std=c++17 -Wall -Isrc/cpp/include Taller2_AB_PO_XX.cpp -lsqlite3 -o Taller2_AB_PO_XX
//       ./Taller2_AB_PO_XX
// =====================================================================

#include "src/cpp/include/ConsolaApp.h"

int main(int argc, char* argv[]) {
    // Inicializa la aplicación con la base de datos de persistencia SQLite
    ConsolaApp app("data/pea_investigacion.db");
    if (argc > 1 && (std::string(argv[1]) == "--gui" || std::string(argv[1]) == "-g")) {
        app.iniciarGUI();
        return 0;
    }
    app.iniciar();
    return 0;
}
