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

#if __has_include("ConsolaApp.h")
    #include "ConsolaApp.h"
#else
    #include "src/cpp/include/ConsolaApp.h"
#endif

int main(int argc, char* argv[]) {
    // Inicializa la aplicación con la base de datos de persistencia SQLite
    ConsolaApp app("data/pea_investigacion.db");
    if (argc > 1 && (std::string(argv[1]) == "--gen" || std::string(argv[1]) == "--gui-gen")) {
        Multilista multi;
        GestorSQLite::cargarDesdeBD(multi, "data/pea_investigacion.db");
        VisualizadorGrafico::generarHTML(multi, "dist/visualizador_hipercubo.html");
        std::cout << "[OK] dist/visualizador_hipercubo.html generado exitosamente.\n";
        return 0;
    }
    if (argc > 1 && std::string(argv[1]) == "--stats-json") {
        Multilista multi;
        GestorSQLite::cargarDesdeBD(multi, "data/pea_investigacion.db");
        std::cout << "{\n"
                  << "  \"grupos_total\": " << multi.contarGrupos(false) << ",\n"
                  << "  \"grupos_activos\": " << multi.contarGrupos(true) << ",\n"
                  << "  \"investigadores_total\": " << multi.contarInvestigadores(false) << ",\n"
                  << "  \"investigadores_activos\": " << multi.contarInvestigadores(true) << ",\n"
                  << "  \"productos_total\": " << multi.contarProductos(false) << ",\n"
                  << "  \"productos_activos\": " << multi.contarProductos(true) << ",\n"
                  << "  \"ventana_2_anios\": " << multi.contarProductosPorVentana(2024, 2026, true) << ",\n"
                  << "  \"ventana_5_anios\": " << multi.contarProductosPorVentana(2021, 2026, true) << ",\n"
                  << "  \"ventana_modelo_2024\": " << multi.contarProductosModelo2024(2026, true) << "\n"
                  << "}\n";
        return 0;
    }
    if (argc > 1 && (std::string(argv[1]) == "--gui" || std::string(argv[1]) == "-g")) {
        app.iniciarGUI();
        return 0;
    }
    app.iniciar();
    return 0;
}
