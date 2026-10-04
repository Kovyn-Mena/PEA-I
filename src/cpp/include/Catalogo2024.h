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
    std::string codigo_2024;       // ART_A1, LIB_A, SOFT_REG, APO, etc.
    std::string measurement_class; // GNC-A, GNC-B, DTI-A, FRH-B, etc.
    int weight;                    // Peso relativo (1 a 10)
    int global_weight;             // Peso global (10 a 100)
};

class Catalogo2024 {
public:
    static InfoTipologia2024 clasificar(const std::string& tipo, const std::string& categoria, const std::string& titulo = "") {
        std::string t = tipo;
        std::string cat = categoria;
        std::string tit = titulo;
        std::transform(t.begin(), t.end(), t.begin(), ::tolower);
        std::transform(cat.begin(), cat.end(), cat.begin(), ::toupper);
        std::transform(tit.begin(), tit.end(), tit.begin(), ::tolower);

        // 1. GNC: Generación de Nuevo Conocimiento
        if (t.find("articulo") != std::string::npos || t.find("artículo") != std::string::npos) {
            if (cat.find("A1") != std::string::npos)
                return { "GNC", "ART_A1", "GNC-A", 10, 100 };
            else if (cat.find("A2") != std::string::npos || cat == "A")
                return { "GNC", "ART_A2", "GNC-A", 8, 80 };
            else if (cat.find("B") != std::string::npos)
                return { "GNC", "ART_B", "GNC-B", 6, 60 };
            else
                return { "GNC", "ART_C", "GNC-B", 4, 40 };
        }
        else if (t.find("libro") != std::string::npos) {
            if (cat.find("A") != std::string::npos)
                return { "GNC", "LIB_A", "GNC-A", 10, 100 };
            return { "GNC", "LIB_B", "GNC-B", 7, 70 };
        }
        else if (t.find("capitulo") != std::string::npos || t.find("capítulo") != std::string::npos) {
            if (cat.find("A") != std::string::npos)
                return { "GNC", "CAP_LIB_A", "GNC-A", 5, 50 };
            return { "GNC", "CAP_LIB_B", "GNC-B", 3, 30 };
        }
        else if (t.find("patente") != std::string::npos) {
            return { "GNC", "PAT_INV", "GNC-A", 10, 100 };
        }
        // 2. DTI: Desarrollo Tecnológico e Innovación
        else if (t.find("software") != std::string::npos) {
            return { "DTI", "SOFT_REG", "DTI-A", 9, 90 };
        }
        else if (t.find("prototipo") != std::string::npos || t.find("planta") != std::string::npos) {
            return { "DTI", "PROT_IND", "DTI-A", 8, 80 };
        }
        else if (t.find("diseno") != std::string::npos || t.find("diseño") != std::string::npos) {
            return { "DTI", "DIS_IND", "DTI-A", 8, 80 };
        }
        else if (t.find("regulacion") != std::string::npos || t.find("regulación") != std::string::npos || t.find("norma") != std::string::npos) {
            return { "DTI", "REG_NORM", "DTI-A", 7, 70 };
        }
        else if (t.find("informe") != std::string::npos) {
            return { "DTI", "INF_TEC", "DTI-B", 5, 50 };
        }
        else if (t.find("consultoria") != std::string::npos || t.find("consultoría") != std::string::npos) {
            return { "DTI", "CONS_TEC", "DTI-B", 5, 50 };
        }
        // 3. FRH: Formación de Recurso Humano
        else if (t.find("grado") != std::string::npos || t.find("tesis") != std::string::npos) {
            if (tit.find("doctor") != std::string::npos || tit.find("doc") != std::string::npos)
                return { "FRH", "TES_DOC", "FRH-A", 10, 100 };
            else if (tit.find("maestr") != std::string::npos || tit.find("master") != std::string::npos)
                return { "FRH", "TGM", "FRH-A", 7, 70 };
            else if (tit.find("ondas") != std::string::npos || tit.find("apo") != std::string::npos)
                return { "FRH", "APO", "FRH-B", 5, 30 };
            return { "FRH", "TGP", "FRH-B", 4, 40 };
        }
        else if (t.find("jurado") != std::string::npos || t.find("evaluador") != std::string::npos) {
            return { "FRH", "JUR_EVAL", "FRH-B", 4, 40 };
        }
        else if (t.find("cursocorto") != std::string::npos || t.find("curso") != std::string::npos) {
            return { "FRH", "CUR_COR", "FRH-B", 3, 30 };
        }
        // 4. ASC: Apropiación Social del Conocimiento
        else if (t.find("apropiacion") != std::string::npos || t.find("apropiación") != std::string::npos) {
            return { "ASC", "PROC_ASC", "ASC-A", 8, 80 };
        }
        else if (t.find("contenido") != std::string::npos || t.find("audiovisual") != std::string::npos) {
            return { "ASC", "CONT_DIG", "ASC-B", 4, 40 };
        }
        // 5. DPC: Divulgación Pública de la Ciencia
        else if (t.find("evento") != std::string::npos || t.find("ponencia") != std::string::npos || t.find("documento") != std::string::npos) {
            if (t.find("documento") != std::string::npos)
                return { "DPC", "DOC_TRAB", "DPC-B", 5, 50 };
            return { "DPC", "EVT_INT", "DPC-A", 6, 60 };
        }

        // Por defecto: GNC
        return { "GNC", "ART_B", "GNC-B", 6, 60 };
    }
};

#endif // CATALOGO_2024_H
