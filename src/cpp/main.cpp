#include "include/ConsolaApp.h"

// =====================================================================
// PEA-i (Programa Estadístico de Análisis de Investigación - UPC)
// Punto de Entrada Principal (C++)
// =====================================================================

int main(int argc, char* argv[]) {
    ConsolaApp app("data/pea_investigacion.db");
    if (argc > 1 && (std::string(argv[1]) == "--gui" || std::string(argv[1]) == "-g")) {
        app.iniciarGUI();
        return 0;
    }
    app.iniciar();
    return 0;
}
