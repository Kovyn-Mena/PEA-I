#include "include/ConsolaApp.h"

// =====================================================================
// PEA-i (Programa Estadístico de Análisis de Investigación - UPC)
// Punto de Entrada Principal (C++)
// =====================================================================

int main(int argc, char* argv[]) {
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
