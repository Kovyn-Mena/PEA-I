#include "include/ConsolaApp.h"

// =====================================================================
// PEA-i (Programa Estadístico de Análisis de Investigación - UPC)
// Punto de Entrada Principal (C++)
// =====================================================================

int main() {
    ConsolaApp app("data/pea_investigacion.db");
    app.iniciar();
    return 0;
}
