// =====================================================================
// PEA-i: CATÁLOGO Y TAXONOMÍA MINCIENCIAS 2024 (C++ CORE)
// Universidad Popular del Cesar — Estructura de Datos
// Docente: Ing. Adith Bismarck Pérez Orozco
// =====================================================================
// Implementa la clasificación del Modelo de Medición MinCiencias 2024:
//   • 5 Familias: GNC, DTI, ASC, DPC, FRH.
//   • Clases de Medición (measurement_class: GNC-A, DTI-A, FRH-B, etc.)
//   • Pesos de evaluación para cálculo de producción ponderada.
// =====================================================================

#ifndef CATALOGO_2024_H
#define CATALOGO_2024_H

#include <string>
#include <algorithm>

struct InfoTipologia2024 {
    std::string familia;           // GNC, DTI, ASC, DPC, FRH
    std::string codigo_2024;       // ART_A1, ART_OPEN_A1, SF, TD, TM, TP, WP, etc.
    std::string measurement_class; // GNC-TOP, GNC-A, DTI-B, FRH-A, FRH-B, DPC, etc.
    double weight;                 // Peso relativo oficial (Anexo 1)
    int global_weight;             // Peso global oficial (Tabla 6)

    double peso_final() const {
        return (double)global_weight * (weight / 10.0);
    }
};

class Catalogo2024 {
public:
    static InfoTipologia2024 clasificar(const std::string& tipo, const std::string& categoria,
                                        const std::string& titulo = "", const std::string& subtipo = "") {
        // 0. Si el producto ya cuenta con subtipo canónico MinCiencias 2024, resolver directamente
        std::string sub = subtipo;
        std::transform(sub.begin(), sub.end(), sub.begin(), ::toupper);

        if (sub == "TD" || sub == "TD_A") return { "FRH", "TD_A", "FRH-A", 10.0, 160 };
        if (sub == "TD_B") return { "FRH", "TD_B", "FRH-A", 5.0, 160 };
        if (sub == "TM" || sub == "TM_A") return { "FRH", "TM_A", "FRH-B", 10.0, 70 };
        if (sub == "TM_B") return { "FRH", "TM_B", "FRH-B", 5.0, 70 };
        if (sub == "TP" || sub == "TP_A") return { "FRH", "TP_A", "FRH-B", 10.0, 20 };
        if (sub == "TP_B") return { "FRH", "TP_B", "FRH-B", 5.0, 20 };
        if (sub == "APO") return { "FRH", "APO", "FRH-B", 5.0, 30 };
        if (sub == "WP") return { "DPC", "WP", "DPC", 10.0, 100 };
        if (sub == "LIB_DIV") return { "DPC", "LIB_DIV", "DPC", 10.0, 100 };
        if (sub == "LIB_FOR") return { "DPC", "LIB_FOR", "DPC", 10.0, 100 };
        if (sub == "SF") return { "DTI", "SF", "DTI-B", 8.0, 35 };
        if (sub == "PAT_INV" || sub == "PA") return { "GNC", "PAT_INV", "GNC-TOP", 10.0, 300 };
        if (sub == "MOD_UTIL" || sub == "PMU") return { "GNC", "MOD_UTIL", "GNC-TOP", 10.0, 100 };
        if (sub == "PCD") return { "DPC", "PCD", "DPC", 10.0, 100 };
        if (sub == "EC") return { "DPC", "EC", "DPC", 10.0, 50 };
        if (sub == "INF" || sub == "IFI") return { "DPC", "INF", "DPC", 10.0, 100 };
        if (sub == "CON_CT") return { "DPC", "CON_CT", "DPC", 10.0, 50 };

        std::string t = tipo;
        std::string cat = categoria;
        std::string tit = titulo;
        std::transform(t.begin(), t.end(), t.begin(), ::tolower);
        std::transform(cat.begin(), cat.end(), cat.begin(), ::toupper);
        std::transform(tit.begin(), tit.end(), tit.begin(), ::tolower);

        bool es_open = (t.find("open") != std::string::npos || t.find("abierto") != std::string::npos ||
                        tit.find("open") != std::string::npos || tit.find("abierto") != std::string::npos);

        // 1. DPC: Divulgación Pública de la Ciencia (Working Papers y Libros de Divulgación)
        if (t.find("documento de trabajo") != std::string::npos || t.find("working paper") != std::string::npos ||
            tit.find("working paper") != std::string::npos || t.find("wp") != std::string::npos) {
            return { "DPC", "WP", "DPC", 10.0, 100 };
        }
        if (t.find("libros de divulgacion") != std::string::npos || t.find("libros de divulgación") != std::string::npos ||
            t.find("divulgacion") != std::string::npos || t.find("divulgación") != std::string::npos) {
            return { "DPC", "LIB_DIV", "DPC", 10.0, 100 };
        }
        if (t.find("libros de formacion") != std::string::npos || t.find("libros de formación") != std::string::npos) {
            return { "DPC", "LIB_FOR", "DPC", 10.0, 100 };
        }

        // 2. FRH: Formación de Recurso Humano (Separación estricta de Doctorados vs Maestrías vs Pregrados)
        if (t.find("grado") != std::string::npos || t.find("tesis") != std::string::npos ||
            t.find("direccion") != std::string::npos || t.find("dirección") != std::string::npos ||
            t.find("trabajo dirigido") != std::string::npos) {
            if (tit.find("doctor") != std::string::npos || tit.find("doc") != std::string::npos || t.find("doctor") != std::string::npos)
                return { "FRH", "TD", "FRH-A", 10.0, 160 };
            else if (tit.find("maestr") != std::string::npos || tit.find("master") != std::string::npos || t.find("maestr") != std::string::npos)
                return { "FRH", "TM", "FRH-B", 10.0, 70 };
            else if (tit.find("ondas") != std::string::npos || tit.find("apo") != std::string::npos || tit.find("semillero") != std::string::npos)
                return { "FRH", "APO", "FRH-B", 5.0, 30 };
            return { "FRH", "TP", "FRH-B", 10.0, 20 };
        }
        if (t.find("jurado") != std::string::npos || t.find("evaluador") != std::string::npos) {
            return { "FRH", "JUR_EVAL", "FRH-B", 4.0, 20 };
        }
        if (t.find("cursocorto") != std::string::npos || t.find("curso") != std::string::npos) {
            return { "FRH", "CUR_COR", "FRH-B", 3.0, 20 };
        }

        // 3. DTI: Desarrollo Tecnológico e Innovación (Software registrado: Anexo 1 -> DTI-B, peso relativo 8, global 35)
        if (t.find("software") != std::string::npos || t.find("computacional") != std::string::npos || t.find("soporte logico") != std::string::npos) {
            return { "DTI", "SF", "DTI-B", 8.0, 35 };
        }
        if (t.find("prototipo") != std::string::npos) {
            return { "DTI", "PI", "DTI-A", 4.0, 35 };
        }
        if (t.find("planta piloto") != std::string::npos || t.find("plantas piloto") != std::string::npos) {
            return { "DTI", "PP", "DTI-A", 4.0, 35 };
        }
        if (t.find("diseno") != std::string::npos || t.find("diseño") != std::string::npos) {
            return { "DTI", "DI", "DTI-A", 10.0, 35 };
        }
        if (t.find("esquema") != std::string::npos || t.find("circuito") != std::string::npos) {
            return { "DTI", "ECI", "DTI-A", 4.0, 35 };
        }
        if (t.find("signo") != std::string::npos || t.find("marca") != std::string::npos) {
            return { "DTI", "SD", "DTI-A", 4.0, 35 };
        }
        if (t.find("nutraceutico") != std::string::npos || t.find("nutracéutico") != std::string::npos) {
            return { "DTI", "PN", "DTI-B", 6.0, 35 };
        }
        if (t.find("coleccion") != std::string::npos || t.find("colección") != std::string::npos) {
            return { "DTI", "CC", "DTI-B", 10.0, 35 };
        }
        if (t.find("secreto") != std::string::npos || t.find("spin-off") != std::string::npos || t.find("empresa de base") != std::string::npos) {
            return { "DTI", "EBT", "DTI-A", 10.0, 100 };
        }
        if (t.find("regulacion") != std::string::npos || t.find("regulación") != std::string::npos || t.find("norma") != std::string::npos) {
            return { "DTI", "REG_NORM", "DTI-A", 10.0, 70 };
        }
        if (t.find("informe") != std::string::npos) {
            return { "DPC", "INF", "DPC", 10.0, 100 };
        }
        if (t.find("consultoria") != std::string::npos || t.find("consultoría") != std::string::npos) {
            return { "DPC", "CON_CT", "DPC", 10.0, 50 };
        }

        // 4. GNC: Generación de Nuevo Conocimiento
        if (t.find("articulo") != std::string::npos || t.find("artículo") != std::string::npos || t.find("nota cientifica") != std::string::npos) {
            if (t.find("nota") != std::string::npos || cat == "D")
                return { "GNC", "N_A1", "GNC-B", 10.0, 4 };
            if (cat.find("A1") != std::string::npos)
                return { "GNC", es_open ? "ART_OPEN_A1" : "ART_A1", "GNC-TOP", es_open ? 10.0 : 9.5, 100 };
            if (cat.find("A2") != std::string::npos || cat == "A")
                return { "GNC", es_open ? "ART_OPEN_A2" : "ART_A2", "GNC-TOP", es_open ? 6.0 : 5.5, 100 };
            if (cat.find("B") != std::string::npos)
                return { "GNC", es_open ? "ART_OPEN_B" : "ART_B", "GNC-A", es_open ? 3.5 : 3.0, 100 };
            return { "GNC", es_open ? "ART_OPEN_C" : "ART_C", "GNC-A", es_open ? 2.0 : 1.5, 100 };
        }
        if (t.find("libro") != std::string::npos && t.find("capitulo") == std::string::npos && t.find("capítulo") == std::string::npos) {
            if (cat.find("A1") != std::string::npos)
                return { "GNC", "LIB_A1", "GNC-TOP", 10.0, 300 };
            if (cat.find("A") != std::string::npos)
                return { "GNC", "LIB_A", "GNC-TOP", 9.0, 300 };
            return { "GNC", "LIB_B", "GNC-A", 8.0, 300 };
        }
        if (t.find("capitulo") != std::string::npos || t.find("capítulo") != std::string::npos) {
            if (cat.find("A1") != std::string::npos)
                return { "GNC", "CAP_A1", "GNC-TOP", 10.0, 100 };
            if (cat.find("A") != std::string::npos)
                return { "GNC", "CAP_A", "GNC-TOP", 9.0, 100 };
            return { "GNC", "CAP_B", "GNC-A", 8.0, 100 };
        }
        if (t.find("patente") != std::string::npos || t.find("modelo de utilidad") != std::string::npos) {
            if (t.find("utilidad") != std::string::npos)
                return { "GNC", "MOD_UTIL", "GNC-TOP", 10.0, 100 };
            return { "GNC", "PAT_INV", "GNC-TOP", 10.0, 300 };
        }
        if (t.find("variedad") != std::string::npos || t.find("raza") != std::string::npos || t.find("pecuaria") != std::string::npos) {
            return { "GNC", "VV", "GNC-TOP", 10.0, 300 };
        }
        if (t.find("creacion") != std::string::npos || t.find("creación") != std::string::npos || t.find("obra") != std::string::npos) {
            return { "GNC", "AAD", "GNC-TOP", 8.0, 80 };
        }

        // 5. ASC: Apropiación Social del Conocimiento
        if (t.find("apropiacion") != std::string::npos || t.find("apropiación") != std::string::npos || t.find("ciudadana") != std::string::npos) {
            return { "ASC", "PP", "ASC", 10.0, 80 };
        }
        if (t.find("contenido") != std::string::npos || t.find("audiovisual") != std::string::npos || t.find("multimedia") != std::string::npos) {
            return { "DPC", "PCD", "DPC", 10.0, 100 };
        }
        if (t.find("evento") != std::string::npos || t.find("ponencia") != std::string::npos) {
            return { "DPC", "EC", "DPC", 10.0, 50 };
        }

        // Por defecto: GNC
        return { "GNC", "ART_B", "GNC-A", 3.0, 100 };
    }
};

#endif // CATALOGO_2024_H
