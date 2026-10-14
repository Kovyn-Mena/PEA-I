#ifndef GESTOR_INTEROP_H
#define GESTOR_INTEROP_H

#include <iostream>
#include <string>
#include <vector>
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

#if !defined(_WIN32) && !defined(_WIN64)
#include <sys/wait.h>
#endif

// Representación de grupo candidato devuelto por la búsqueda en ScienTI
struct CandidatoGrupo {
    std::string nro;
    std::string nombre;
    std::string col;
    std::string lider;
    std::string inst;
    std::string cat;
};

class GestorInterop {
public:
    // Resuelve el intérprete Python real una sola vez (cacheado).
    // Orden: PEAI_PYTHON (exportado por iniciar.bat con el Python detectado)
    // -> "py -3" (Windows) -> PYTHON_CMD. Verifica ejecución real con -c,
    // no solo --version (evita el alias fantasma de Microsoft Store).
    // Retorna "" si no hay intérprete funcional.
    static std::string comandoPython() {
        static std::string cache;
        static bool resuelto = false;
        if (resuelto) return cache;
        resuelto = true;
        std::vector<std::string> candidatos;
        if (const char* env = std::getenv("PEAI_PYTHON")) {
            if (std::string(env).size() > 0) candidatos.push_back(env);
        }
#if defined(_WIN32) || defined(_WIN64)
        candidatos.push_back("py -3");
#endif
        candidatos.push_back(PYTHON_CMD);
        for (size_t i = 0; i < candidatos.size(); i++) {
            const std::string& c = candidatos[i];
            // Entrecomillar solo rutas con espacios (no comandos como "py -3")
            bool esRuta = (c.find('\\') != std::string::npos) ||
                          (c.find('/') != std::string::npos) ||
                          (c.find(':') != std::string::npos);
            std::string inv = esRuta ? ("\"" + c + "\"") : c;
            std::string prueba = inv + " -c \"import sys;sys.exit(0)\"";
#if defined(_WIN32) || defined(_WIN64)
            prueba += " >nul 2>&1";
#else
            prueba += " >/dev/null 2>&1";
#endif
            int rc = std::system(prueba.c_str());
#if !defined(_WIN32) && !defined(_WIN64)
            if (WIFEXITED(rc)) rc = WEXITSTATUS(rc);
#endif
            if (rc == 0) { cache = c; return cache; }
        }
        cache.clear();
        return cache;
    }

    static bool hayPython() { return !comandoPython().empty(); }

    // Ejecuta el script de Python y captura la salida silenciosamente (para parsers)
    // Retorna "[PEAI_SIN_PYTHON]" si no hay intérprete (distinguible de "sin resultados")
    static std::string salidaPython(const std::string& argumentos) {
        const std::string py = comandoPython();
        if (py.empty()) return "[PEAI_SIN_PYTHON]";
        bool esRuta = (py.find('\\') != std::string::npos) ||
                      (py.find('/') != std::string::npos) ||
                      (py.find(':') != std::string::npos);
        std::string inv = esRuta ? ("\"" + py + "\"") : py;
        std::string comando = inv + " Taller2_AB_PO_XX.py " + argumentos + " 2>&1";
        std::string out;
        FILE* pipe = POPEN(comando.c_str(), "r");
        if (!pipe) return out;
        std::array<char, 512> buffer;
        while (fgets(buffer.data(), buffer.size(), pipe) != nullptr) {
            out += buffer.data();
        }
        PCLOSE(pipe);
        return out;
    }

    // Parte una cadena por delimitador (helper para parsear CAND|...)
    static std::vector<std::string> partir(const std::string& s, char sep) {
        std::vector<std::string> v;
        std::string cur;
        for (size_t i = 0; i < s.size(); i++) {
            if (s[i] == sep) {
                v.push_back(cur);
                cur.clear();
            } else if (s[i] != '\r' && s[i] != '\n') {
                cur += s[i];
            }
        }
        v.push_back(cur);
        return v;
    }

    // Ejecuta un comando en Python a través de una tubería y muestra la salida en vivo
    static bool ejecutarComandoPython(const std::string& scriptArg, std::string& salidaCompleta) {
        salidaCompleta.clear();

        const std::string py = comandoPython();
        if (py.empty()) {
            salidaCompleta = "Error: no hay intérprete Python funcional (ni PEAI_PYTHON, ni py -3, ni "
                + std::string(PYTHON_CMD) + "). Instale Python o use datos locales.";
            std::cout << "[!] " << salidaCompleta << "\n";
            return false;
        }
        bool esRuta = (py.find('\\') != std::string::npos) ||
                      (py.find('/') != std::string::npos) ||
                      (py.find(':') != std::string::npos);
        std::string inv = esRuta ? ("\"" + py + "\"") : py;

        // Construir la línea de comando multiplataforma
        std::string comando = inv + " " + scriptArg + " 2>&1";

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

    // Ejecuta la ingesta automática en lote de Web Scraping (GrupLAC + CvLAC)
    static bool ejecutarIngestaAutomatica(std::string& salida) {
        std::string args = "Taller2_AB_PO_XX.py --auto-ingest";
        return ejecutarComandoPython(args, salida);
    }

    // Busca universidades e instituciones en MinCiencias ScienTI
    static bool buscarUniversidad(const std::string& texto, std::string& salida) {
        std::string args = "Taller2_AB_PO_XX.py --buscar-universidad \"" + texto + "\"";
        return ejecutarComandoPython(args, salida);
    }

    // Busca grupos por nombre o palabra clave en los índices institucionales
    static bool buscarGrupo(const std::string& nombre, std::string& salida) {
        std::string args = "Taller2_AB_PO_XX.py --buscar-grupo \"" + nombre + "\"";
        return ejecutarComandoPython(args, salida);
    }

    // Lista los 66 grupos institucionales de la UPC
    static bool listarGruposUPC(std::string& salida) {
        std::string args = "Taller2_AB_PO_XX.py --listar-upc";
        return ejecutarComandoPython(args, salida);
    }

    // Ejecuta Web Scraping de un grupo por su código NRO de MinCiencias
    static bool scrapearGrupoNro(const std::string& nro, std::string& salida) {
        std::string args = "Taller2_AB_PO_XX.py --scrape-grupo \"" + nro + "\"";
        return ejecutarComandoPython(args, salida);
    }

    // Genera informe PDF formal con ReportLab de forma multiplataforma
    static bool generarReportePDF(const std::string& codGrupo, std::string& salida) {
        std::string args = "src/python/core/reporte_pdf.py \"" + codGrupo + "\"";
        return ejecutarComandoPython(args, salida);
    }
};

#endif // GESTOR_INTEROP_H
