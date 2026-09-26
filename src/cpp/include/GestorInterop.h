#ifndef GESTOR_INTEROP_H
#define GESTOR_INTEROP_H

#include <iostream>
#include <string>
#include <array>
#include <cstdlib>

// =====================================================================
// GESTOR DE INTEROPERABILIDAD C++ <-> PYTHON (PEA-i)
// Comunicación mediante tuberías de procesos (IPC con popen)
// Permite que la consola en C++ invoque el módulo de Web Scraping
// e Ingesta de Python (Fase 3) y el Dashboard (Fase 5).
// =====================================================================

#if defined(_WIN32) || defined(_WIN64)
    #define POPEN _popen
    #define PCLOSE _pclose
    #define PYTHON_CMD "python"
#else
    #define POPEN popen
    #define PCLOSE pclose
    #define PYTHON_CMD "python3"
#endif

class GestorInterop {
public:
    // Ejecuta un comando en Python a través de una tubería y muestra la salida en vivo
    static bool ejecutarComandoPython(const std::string& scriptArg, std::string& salidaCompleta) {
        salidaCompleta.clear();

        // Construir la línea de comando multiplataforma
        std::string comando = std::string(PYTHON_CMD) + " " + scriptArg + " 2>&1";

        std::cout << "\n[C++ -> Python Bridge] Ejecutando: " << comando << "\n";
        std::cout << std::string(65, '-') << "\n";

        FILE* pipe = POPEN(comando.c_str(), "r");
        if (!pipe) {
            salidaCompleta = "Error: No se pudo abrir la tubería de comunicación con Python.";
            std::cout << "[!] " << salidaCompleta << "\n";
            return false;
        }

        std::array<char, 256> buffer;
        while (fgets(buffer.data(), buffer.size(), pipe) != nullptr) {
            std::cout << buffer.data() << std::flush;
            salidaCompleta += buffer.data();
        }

        int exitCode = PCLOSE(pipe);
        std::cout << std::string(65, '-') << "\n";

        if (exitCode == 0) {
            std::cout << "[C++ -> Python Bridge] Proceso finalizado exitosamente (código 0).\n";
            return true;
        } else {
            std::cout << "[C++ -> Python Bridge] El proceso retornó código de estado: " << exitCode << "\n";
            return false;
        }
    }

    // Ejecuta Web Scraping de URL (GrupLAC o CvLAC)
    static bool ejecutarScrapingURL(const std::string& url, std::string& salida) {
        std::string args = "Taller2_AB_PO_XX.py --scrape-url \"" + url + "\"";
        return ejecutarComandoPython(args, salida);
    }

    // Ejecuta la ingesta desde un archivo CSV
    static bool ejecutarIngestaCSV(const std::string& rutaCSV, std::string& salida) {
        std::string args = "Taller2_AB_PO_XX.py --scrape-csv \"" + rutaCSV + "\"";
        return ejecutarComandoPython(args, salida);
    }

    // Ejecuta la ingesta desde un archivo PDF
    static bool ejecutarIngestaPDF(const std::string& rutaPDF, std::string& salida) {
        std::string args = "Taller2_AB_PO_XX.py --scrape-pdf \"" + rutaPDF + "\"";
        return ejecutarComandoPython(args, salida);
    }

    // Lanza el dashboard gráfico de Python
    static bool lanzarDashboardPython(std::string& salida) {
        std::string args = "Taller2_AB_PO_XX.py --gui";
        return ejecutarComandoPython(args, salida);
    }
};

#endif // GESTOR_INTEROP_H
