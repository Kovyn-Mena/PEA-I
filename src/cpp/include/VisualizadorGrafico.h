#ifndef VISUALIZADOR_GRAFICO_H
#define VISUALIZADOR_GRAFICO_H

#include <iostream>
#include <string>
#include <fstream>
#include <sstream>
#include <vector>
#include <cstdlib>
#include <filesystem>
#include "Multilista.h"
#include "GestorSQLite.h"

// =====================================================================
// PEA-i: PORTAL EJECUTIVO Y DASHBOARD DE CIENCIA ABIERTA (UPC)
// Universidad Popular del Cesar — Facultad de Ingeniería y Tecnológicas
// Docente: Ing. Adith Bismarck Pérez Orozco
// =====================================================================
// Arquitectura Zero-Dependencies:
// - Genera un portal HTML5/CSS3/JavaScript autónomo y moderno.
// - Directorio de Grupos con búsqueda en tiempo real y fichas de perfil.
// - Balance consolidado del Modelo MinCiencias 2024 (5 familias e IPP).
// - Enlaces directos a los Informes Oficiales en PDF (ReportLab).
// - Dashboard analítico con gráficos interactivos y filtros por ventana (Punto 10).
// - Vistas formales por entidad (Punto 12.c: Grupos, Investigadores, Productos).
// =====================================================================

class VisualizadorGrafico {
private:
    static std::string escaparJSON(const std::string& str) {
        std::ostringstream o;
        for (char c : str) {
            if (c == '"') o << "\\\"";
            else if (c == '\\') o << "\\\\";
            else if (c == '\b') o << "\\b";
            else if (c == '\f') o << "\\f";
            else if (c == '\n') o << "\\n";
            else if (c == '\r') o << "\\r";
            else if (c == '\t') o << "\\t";
            else if (static_cast<unsigned char>(c) <= 0x1f) {
                // Omitir caracteres de control no imprimibles
            } else {
                o << c;
            }
        }
        return o.str();
    }

    // Serializa los nodos en memoria RAM a una estructura JSON
    static std::string serializarMultilistaAJSON(const Multilista& multi) {
        std::ostringstream json;
        json << "{\n";
        json << "  \"grupos\": [\n";

        NodoGrupo* g = multi.getCabezaGrupos();
        bool primerG = true;

        while (g != nullptr) {
            if (!primerG) json << ",\n";
            primerG = false;

            json << "    {\n";
            json << "      \"codigo\": \"" << escaparJSON(g->codigo_grupo) << "\",\n";
            json << "      \"nombre\": \"" << escaparJSON(g->nombre) << "\",\n";
            json << "      \"clasificacion\": \"" << escaparJSON(g->clasificacion) << "\",\n";
            json << "      \"area\": \"" << escaparJSON(g->area_conocimiento) << "\",\n";
            json << "      \"lider\": \"" << escaparJSON(g->lider) << "\",\n";
            json << "      \"anio\": " << g->anio_creacion << ",\n";
            json << "      \"activo\": " << (g->activo ? "true" : "false") << ",\n";

            // Investigadores del grupo (Eje Y)
            json << "      \"investigadores\": [\n";
            NodoInvestigador* inv = g->primerInvestigador;
            bool primerInv = true;
            while (inv != nullptr) {
                if (!primerInv) json << ",\n";
                primerInv = false;

                std::string parEval, scholar, orcid, formExtra;
                bool tieneP = GestorSQLite::obtenerPerfilInvestigador(inv->documento_id, parEval, scholar, orcid, formExtra);

                json << "        {\n";
                json << "          \"documento\": \"" << escaparJSON(inv->documento_id) << "\",\n";
                json << "          \"nombre\": \"" << escaparJSON(inv->nombre_completo) << "\",\n";
                json << "          \"categoria\": \"" << escaparJSON(inv->categoria) << "\",\n";
                json << "          \"formacion\": \"" << escaparJSON(inv->formacion_academica) << "\",\n";
                json << "          \"par_evaluador\": \"" << (tieneP ? parEval : "No") << "\",\n";
                json << "          \"scholar_url\": \"" << (tieneP ? escaparJSON(scholar) : "") << "\",\n";
                json << "          \"orcid\": \"" << (tieneP ? escaparJSON(orcid) : "") << "\",\n";
                json << "          \"activo\": " << (inv->activo ? "true" : "false") << "\n";
                json << "        }";
                inv = inv->sigInvestigador;
            }
            json << "\n      ],\n";

            // Productos del grupo (Eje Z / Ortogonal)
            json << "      \"productos\": [\n";
            NodoProducto* p = g->primerProducto;
            bool primerP = true;
            while (p != nullptr) {
                if (!primerP) json << ",\n";
                primerP = false;

                json << "        {\n";
                json << "          \"id\": \"" << escaparJSON(p->id_producto) << "\",\n";
                json << "          \"tipo\": \"" << escaparJSON(p->tipo) << "\",\n";
                json << "          \"titulo\": \"" << escaparJSON(p->titulo) << "\",\n";
                json << "          \"anio\": " << p->anio << ",\n";
                json << "          \"categoria\": \"" << escaparJSON(p->categoria_minciencias) << "\",\n";
                json << "          \"validado\": " << (p->validado ? "true" : "false") << ",\n";
                json << "          \"activo\": " << (p->activo ? "true" : "false") << ",\n";
                json << "          \"id_investigador\": \"" << escaparJSON(p->id_investigador) << "\"\n";
                json << "        }";
                p = p->sigProductoGrupo;
            }
            json << "\n      ]\n";
            json << "    }";

            g = g->sigGrupo;
        }

        json << "\n  ]\n";
        json << "}\n";
        return json.str();
    }

public:
    static bool generarHTML(const Multilista& multi, const std::string& rutaSalida = "dist/visualizador_hipercubo.html") {
        try {
            std::filesystem::path p(rutaSalida);
            if (p.has_parent_path()) {
                std::filesystem::create_directories(p.parent_path());
            }
        } catch (...) {}

        std::ofstream out(rutaSalida, std::ios::out | std::ios::trunc);
        if (!out.is_open()) {
            std::cerr << "[!] Error: No se pudo crear el archivo visualizador en " << rutaSalida << "\n";
            return false;
        }

        std::string datosJSON = serializarMultilistaAJSON(multi);

        out << R"HTML(<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PEA-i UPC — Portal de Ciencia Abierta y Dashboard Analítico</title>
    <link rel="icon" type="image/png" href="data:image/png;base64,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">
    <style>
        :root {
            --upc-green: #006837;
            --upc-green-light: #10b981;
            --upc-red: #ED1C24;
            --bg-dark: #090d16;
            --bg-card: #0f172a;
            --bg-card-hover: #172033;
            --card-border: #1e293b;
            --accent-blue: #38bdf8;
            --accent-amber: #f59e0b;
            --accent-purple: #a855f7;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background: var(--bg-dark);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }

        /* HEADER INSTITUCIONAL */
        header {
            background: linear-gradient(135deg, #022013 0%, #090d16 70%, #15080e 100%);
            border-bottom: 1px solid var(--card-border);
            padding: 0.6rem 1.25rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 0.6rem 0.9rem;
            position: relative;
            z-index: 100;
        }
        .brand-box { display: flex; align-items: center; gap: 0.75rem; flex-shrink: 0; }
        .brand-logo {
            width: 46px; height: 40px;
            background: rgba(255, 255, 255, 0.96);
            border: 1px solid rgba(16, 185, 129, 0.45);
            border-radius: 8px;
            padding: 3px 4px;
            display: flex; align-items: center; justify-content: center;
            box-shadow: 0 2px 10px rgba(0, 104, 55, 0.4);
            flex-shrink: 0;
        }
        .brand-logo img {
            width: 100%; height: 100%;
            object-fit: contain;
            display: block;
        }
        .brand-text h1 { font-size: 1rem; font-weight: 800; letter-spacing: -0.2px; display: flex; align-items: center; gap: 0.45rem; white-space: nowrap; }
        .brand-badge { background: rgba(16, 185, 129, 0.15); color: var(--upc-green-light); border: 1px solid rgba(16, 185, 129, 0.3); font-size: 0.66rem; padding: 2px 7px; border-radius: 6px; font-weight: 700; letter-spacing: 0.3px; }
        .brand-text p { font-size: 0.69rem; color: var(--text-muted); white-space: nowrap; }

        .nav-tabs { display: flex; gap: 0.25rem; background: #0c1222; padding: 0.22rem; border-radius: 8px; border: 1px solid var(--card-border); flex-wrap: wrap; }
        .tab-btn {
            background: transparent; border: none; color: var(--text-muted);
            padding: 0.4rem 0.8rem; border-radius: 6px; cursor: pointer;
            font-weight: 600; font-size: 0.78rem; transition: all 0.2s ease;
            display: inline-flex; align-items: center; gap: 0.35rem; white-space: nowrap;
        }
        .tab-btn:hover { color: #fff; background: rgba(255,255,255,0.05); }
        .tab-btn.active { background: var(--upc-green); color: #fff; box-shadow: 0 1px 4px rgba(0,0,0,0.3); }

        .header-actions { display: flex; gap: 0.4rem; align-items: center; flex-shrink: 0; white-space: nowrap; }
        .action-btn-undo {
            background: #991b1b; color: #fff; border: 1px solid #dc2626;
            padding: 0.38rem 0.75rem; border-radius: 6px; font-weight: 700; font-size: 0.75rem;
            cursor: pointer; display: inline-flex; align-items: center; gap: 0.35rem;
            transition: all 0.2s; white-space: nowrap; flex-shrink: 0;
        }
        .action-btn-undo:hover { background: #b91c1c; }
        .action-btn-pila {
            background: #1e293b; color: #cbd5e1; border: 1px solid #334155;
            padding: 0.38rem 0.75rem; border-radius: 6px; font-weight: 600; font-size: 0.75rem;
            cursor: pointer; display: inline-flex; align-items: center; gap: 0.35rem;
            transition: all 0.2s; white-space: nowrap; flex-shrink: 0;
        }
        .action-btn-pila:hover { background: #334155; color: #fff; }
        .action-btn-export {
            background: var(--upc-green); color: #fff; border: 1px solid #10b981;
            padding: 0.38rem 0.8rem; border-radius: 6px; font-weight: 700; font-size: 0.75rem;
            cursor: pointer; display: inline-flex; align-items: center; gap: 0.35rem;
            transition: all 0.2s; white-space: nowrap; flex-shrink: 0;
        }
        .action-btn-export:hover { background: #047857; }
        .badge-counter {
            background: rgba(0, 0, 0, 0.4); color: #fecaca;
            padding: 1px 6px; border-radius: 10px; font-size: 0.7rem; font-weight: 800;
            min-width: 18px; text-align: center;
        }

        /* KPI BAR */
        .kpi-bar {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 0.75rem;
            padding: 0.75rem 1.25rem 0.25rem 1.25rem;
        }
        .kpi-card {
            background: var(--bg-card);
            border: 1px solid var(--card-border);
            border-radius: 10px;
            padding: 0.7rem 1rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            min-width: 0;
            gap: 0.5rem;
        }
        .kpi-title { font-size: 0.68rem; text-transform: uppercase; color: var(--text-muted); font-weight: 700; letter-spacing: 0.5px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .kpi-val { font-size: 1.3rem; font-weight: 800; margin-top: 0.15rem; white-space: nowrap; letter-spacing: -0.5px; }
        .kpi-icon-wrap {
            width: 34px; height: 34px; border-radius: 8px;
            background: #1e293b; display: flex; align-items: center; justify-content: center;
            flex-shrink: 0;
        }

        /* MAIN CONTENT AREA */
        main { flex: 1; padding: 0.75rem 1.25rem 1.5rem 1.25rem; display: flex; flex-direction: column; min-width: 0; }
        .view-panel { display: none; min-width: 0; }
        .view-panel.active { display: block; }

        /* VISTA 1: PORTAL DE GRUPOS (SPLIT LAYOUT) */
        .portal-layout {
            display: grid;
            grid-template-columns: 290px minmax(0, 1fr);
            gap: 1.1rem;
            align-items: start;
        }

        /* COLUMNA IZQUIERDA: LISTA DE GRUPOS */
        .groups-sidebar {
            background: var(--bg-card);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            max-height: calc(100vh - 155px);
            min-height: 520px;
        }
        .sidebar-header {
            padding: 0.85rem;
            border-bottom: 1px solid var(--card-border);
            display: flex;
            flex-direction: column;
            gap: 0.55rem;
        }
        .search-input {
            width: 100%;
            background: #090d16;
            border: 1px solid var(--card-border);
            color: #fff;
            padding: 0.5rem 0.8rem;
            border-radius: 8px;
            font-size: 0.8rem;
            outline: none;
            transition: border-color 0.2s;
        }
        .search-input:focus { border-color: var(--upc-green-light); }
        .filter-tags { display: flex; gap: 0.3rem; flex-wrap: wrap; }
        .tag-btn {
            background: rgba(255,255,255,0.04);
            border: 1px solid var(--card-border);
            color: var(--text-muted);
            padding: 0.22rem 0.55rem;
            border-radius: 6px;
            font-size: 0.7rem;
            cursor: pointer;
            font-weight: 600;
        }
        .tag-btn.active { background: var(--upc-green); color: #fff; border-color: var(--upc-green-light); }

        .groups-scroll-list {
            flex: 1;
            overflow-y: auto;
            padding: 0.7rem;
            display: flex;
            flex-direction: column;
            gap: 0.45rem;
        }
        .group-card-item {
            background: #090d16;
            border: 1px solid var(--card-border);
            border-radius: 8px;
            padding: 0.65rem 0.8rem;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .group-card-item:hover {
            border-color: #38bdf8;
            background: var(--bg-card-hover);
        }
        .group-card-item.selected {
            border-color: var(--upc-green-light);
            background: linear-gradient(135deg, rgba(0, 104, 55, 0.25) 0%, rgba(15, 23, 42, 0.9) 100%);
        }
        .g-item-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.25rem; }
        .g-item-code { font-size: 0.73rem; font-weight: 800; color: #38bdf8; font-family: monospace; }
        .badge-cat {
            font-size: 0.68rem; font-weight: 700; padding: 2px 7px; border-radius: 5px;
            background: rgba(245, 158, 11, 0.14); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3);
            white-space: nowrap; display: inline-block;
        }
        .badge-cat.cat-A1, .badge-cat.cat-A { background: rgba(16, 185, 129, 0.15); color: #10b981; border-color: rgba(16, 185, 129, 0.3); }
        .badge-cat.cat-B { background: rgba(56, 189, 248, 0.15); color: #38bdf8; border-color: rgba(56, 189, 248, 0.3); }
        .badge-cat.cat-C { background: rgba(168, 85, 247, 0.15); color: #c084fc; border-color: rgba(168, 85, 247, 0.3); }

        .g-item-name { font-size: 0.79rem; font-weight: 700; margin-bottom: 0.25rem; line-height: 1.25; color: #f1f5f9; }
        .g-item-footer { font-size: 0.7rem; color: var(--text-muted); display: flex; justify-content: space-between; }

        /* COLUMNA DERECHA: PERFIL DEL GRUPO */
        .group-detail-view {
            background: var(--bg-card);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            display: flex;
            flex-direction: column;
            min-width: 0;
            overflow: hidden;
        }
        .group-hero {
            background: linear-gradient(135deg, rgba(0, 104, 55, 0.24) 0%, rgba(15, 23, 42, 0.96) 65%);
            border-bottom: 1px solid var(--card-border);
            padding: 1rem 1.25rem;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 1rem;
            flex-wrap: wrap;
        }
        .hero-info { display: flex; gap: 0.9rem; align-items: flex-start; flex: 1; min-width: 240px; }
        .hero-avatar {
            width: 48px; height: 48px; min-width: 48px; flex-shrink: 0; border-radius: 11px;
            background: linear-gradient(135deg, var(--upc-green) 0%, #064e3b 100%);
            display: flex; align-items: center; justify-content: center;
            font-size: 1.35rem; font-weight: 800; color: #fff;
            box-shadow: 0 4px 12px rgba(0,0,0,0.35);
            border: 1px solid rgba(255,255,255,0.12);
        }
        .hero-title { flex: 1; min-width: 0; }
        .hero-title h2 { font-size: 1.05rem; font-weight: 800; line-height: 1.3; color: #f8fafc; margin: 0; }
        .hero-meta { display: flex; gap: 0.5rem; align-items: center; flex-wrap: wrap; margin-top: 0.4rem; font-size: 0.76rem; color: var(--text-muted); }
        .hero-actions { display: flex; gap: 0.45rem; align-items: center; flex-shrink: 0; flex-wrap: wrap; }

        .btn-pdf-download {
            background: var(--upc-green);
            color: #fff;
            padding: 0.42rem 0.85rem;
            border-radius: 6px;
            text-decoration: none;
            font-weight: 700;
            font-size: 0.76rem;
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            white-space: nowrap;
            transition: all 0.2s ease;
            box-shadow: 0 2px 8px rgba(0, 104, 55, 0.35);
            border: 1px solid var(--upc-green-light);
            cursor: pointer;
        }
        .btn-pdf-download:hover { background: #007f43; transform: translateY(-1px); }

        /* SUB-TABS DEL PERFIL */
        .profile-nav {
            display: flex;
            background: #090d16;
            border-bottom: 1px solid var(--card-border);
            padding: 0 1rem;
            gap: 0.3rem;
            flex-wrap: wrap;
        }
        .p-tab-btn {
            background: transparent;
            border: none;
            color: var(--text-muted);
            padding: 0.65rem 0.85rem;
            font-weight: 600;
            font-size: 0.8rem;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            transition: all 0.2s;
        }
        .p-tab-btn:hover { color: #fff; }
        .p-tab-btn.active { color: var(--upc-green-light); border-bottom-color: var(--upc-green-light); }

        .profile-content {
            flex: 1;
            padding: 1.1rem;
            min-width: 0;
        }
        .profile-section { display: none; min-width: 0; }
        .profile-section.active { display: block; }

        /* GRID INFORMACIÓN GENERAL */
        .info-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 0.9rem;
            margin-bottom: 1rem;
        }
        .info-card {
            background: #090d16;
            border: 1px solid var(--card-border);
            border-radius: 8px;
            padding: 0.9rem;
        }
        .info-card-label { font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase; font-weight: 700; margin-bottom: 0.25rem; }
        .info-card-val { font-size: 1rem; font-weight: 700; color: #f1f5f9; }

        /* TABLAS DE DATOS */
        .data-table-container {
            border: 1px solid var(--card-border);
            border-radius: 8px;
            overflow-x: auto;
            background: #090d16;
            width: 100%;
        }
        table.peai-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.78rem;
            text-align: left;
        }
        table.peai-table th {
            background: #0d1527;
            padding: 0.55rem 0.65rem;
            color: var(--text-muted);
            font-weight: 700;
            border-bottom: 1px solid var(--card-border);
            white-space: nowrap;
        }
        table.peai-table td {
            padding: 0.55rem 0.65rem;
            border-bottom: 1px solid rgba(30, 41, 59, 0.6);
            color: #e2e8f0;
            vertical-align: middle;
        }
        table.peai-table tr:hover { background: rgba(255,255,255,0.02); }

        /* METRICAS MODELO 2024 */
        .metrics-2024-grid {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 0.8rem;
            margin-bottom: 1.2rem;
        }
        .metric-fam-card {
            background: #090d16;
            border: 1px solid var(--card-border);
            border-radius: 8px;
            padding: 0.9rem;
            text-align: center;
        }
        .fam-code { font-size: 1.2rem; font-weight: 900; }
        .fam-code.gnc { color: #38bdf8; }
        .fam-code.dti { color: #10b981; }
        .fam-code.asc { color: #f59e0b; }
        .fam-code.dpc { color: #c084fc; }
        .fam-code.frh { color: #f43f5e; }
        .fam-desc { font-size: 0.68rem; color: var(--text-muted); margin: 0.2rem 0 0.5rem 0; }
        .fam-count { font-size: 1.2rem; font-weight: 800; color: #fff; }
        .fam-pts { font-size: 0.75rem; color: var(--upc-green-light); font-weight: 700; }

        /* VISTA 2: DASHBOARD GRÁFICO (REQUISITO 12.B) */
        .dashboard-container {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1.2rem;
        }
        .chart-box {
            background: var(--bg-card);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            padding: 1.2rem;
        }
        .chart-box-title { font-size: 0.95rem; font-weight: 700; margin-bottom: 1rem; display: flex; justify-content: space-between; align-items: center; }
        .bar-chart-row {
            display: flex;
            align-items: center;
            margin-bottom: 0.6rem;
            gap: 0.8rem;
            font-size: 0.78rem;
        }
        .bar-label { width: 110px; color: var(--text-muted); font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .bar-track { flex: 1; background: #090d16; border-radius: 4px; height: 18px; overflow: hidden; position: relative; }
        .bar-fill { height: 100%; border-radius: 4px; transition: width 0.4s ease; display: flex; align-items: center; justify-content: flex-end; padding-right: 6px; font-weight: 700; font-size: 0.7rem; color: #fff; }
        .bar-count { width: 45px; text-align: right; font-weight: 700; color: #e2e8f0; }

        /* ESTILOS CRUD, MODALES, PILA UNDO Y TOAST */
        .badge-status { display: inline-flex; align-items: center; gap: 0.35rem; padding: 3px 9px; border-radius: 12px; font-size: 0.72rem; font-weight: 700; white-space: nowrap; }
        .badge-active { background: rgba(16, 185, 129, 0.14); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.32); }
        .badge-inactive { background: rgba(239, 68, 68, 0.14); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.32); }
        
        .table-actions-cell { display: inline-flex; align-items: center; justify-content: center; gap: 6px; white-space: nowrap; }
        .link-pills-wrap { display: inline-flex; align-items: center; gap: 5px; flex-wrap: nowrap; white-space: nowrap; }
        .link-pill {
            display: inline-flex; align-items: center; padding: 2px 7px; border-radius: 4px;
            font-size: 0.7rem; font-weight: 700; text-decoration: none; white-space: nowrap;
            border: 1px solid rgba(148, 163, 184, 0.28); background: rgba(30, 41, 59, 0.7); color: #cbd5e1;
            transition: all 0.15s ease;
        }
        .link-pill:hover { background: #334155; color: #fff; border-color: #64748b; }
        .link-pill-scholar { background: rgba(2, 132, 199, 0.16); color: #38bdf8; border-color: rgba(56, 189, 248, 0.35); }
        .link-pill-scholar:hover { background: #0284c7; color: #fff; border-color: #38bdf8; }
        .link-pill-orcid { background: rgba(16, 185, 129, 0.16); color: #34d399; border-color: rgba(16, 185, 129, 0.35); }
        .link-pill-orcid:hover { background: #059669; color: #fff; border-color: #34d399; }

        .btn-action-sm {
            padding: 4px 10px; border-radius: 5px; font-size: 0.73rem; font-weight: 700; cursor: pointer; border: 1px solid transparent; transition: all 0.18s; display: inline-flex; align-items: center; gap: 4px; white-space: nowrap;
        }
        .btn-action-edit { background: rgba(56, 189, 248, 0.12); color: #38bdf8; border-color: rgba(56, 189, 248, 0.3); }
        .btn-action-edit:hover { background: #38bdf8; color: #090d16; }
        .btn-action-toggle { background: rgba(245, 158, 11, 0.12); color: #fbbf24; border-color: rgba(245, 158, 11, 0.3); }
        .btn-action-toggle:hover { background: #f59e0b; color: #090d16; }

        .btn-action-hero {
            padding: 0.45rem 0.85rem; border-radius: 6px; font-size: 0.78rem; font-weight: 600; cursor: pointer;
            border: 1px solid #334155; background: rgba(15, 23, 42, 0.85); color: #e2e8f0;
            transition: all 0.2s; display: inline-flex; align-items: center; gap: 0.4rem; text-decoration: none; white-space: nowrap;
        }
        .btn-action-hero:hover { background: #1e293b; border-color: #475569; color: #fff; transform: translateY(-1px); }

        .crud-tab-nav {
            display: flex; gap: 0.6rem; margin-bottom: 1.2rem; border-bottom: 1px solid var(--card-border); padding-bottom: 0.8rem; flex-wrap: wrap;
        }
        .crud-tab-btn {
            background: #1e293b; color: #cbd5e1; border: 1px solid #334155; padding: 0.6rem 1.2rem; border-radius: 8px; font-weight: 700; font-size: 0.85rem; cursor: pointer; transition: all 0.2s; display: flex; align-items: center; gap: 0.5rem;
        }
        .crud-tab-btn:hover { background: #334155; color: #fff; }
        .crud-tab-btn.active { background: var(--upc-green); color: #fff; border-color: var(--upc-green-light); box-shadow: 0 4px 14px rgba(0, 104, 55, 0.4); }

        .crud-toolbar {
            display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.8rem; background: #0b1120; border: 1px solid #1e293b; border-radius: 10px; padding: 0.8rem 1rem; margin-bottom: 1rem;
        }
        .crud-toolbar-left { display: flex; align-items: center; gap: 0.6rem; flex-wrap: wrap; flex: 1; }
        .crud-btn-create {
            background: var(--upc-green); color: #fff; border: 1px solid var(--upc-green-light); padding: 0.55rem 1.2rem; border-radius: 8px; font-weight: 700; font-size: 0.85rem; cursor: pointer; display: flex; align-items: center; gap: 0.4rem; box-shadow: 0 2px 10px rgba(0, 104, 55, 0.4); transition: all 0.2s; white-space: nowrap;
        }
        .crud-btn-create:hover { background: var(--upc-green-light); color: #000; transform: translateY(-1px); }

        .crud-pagination {
            display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.8rem; padding: 0.8rem 0.5rem 0.2rem 0.5rem; font-size: 0.8rem; color: var(--text-muted);
        }
        .crud-page-btn {
            background: #1e293b; color: #e2e8f0; border: 1px solid #334155; padding: 5px 12px; border-radius: 6px; font-weight: 700; cursor: pointer; font-size: 0.78rem; transition: all 0.2s;
        }
        .crud-page-btn:hover:not(:disabled) { background: #38bdf8; color: #000; }
        .crud-page-btn:disabled { opacity: 0.4; cursor: not-allowed; }


        /* MODALES */
        .modal-overlay {
            position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
            background: rgba(0, 0, 0, 0.75); backdrop-filter: blur(6px);
            display: flex; align-items: center; justify-content: center;
            z-index: 1000;
        }
        .modal-box {
            background: #0f172a; border: 1px solid #1e293b; border-radius: 12px;
            width: 540px; max-width: 95vw; max-height: 90vh; overflow-y: auto;
            padding: 1.5rem; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.8);
        }
        .modal-box-lg { width: 720px; }
        .modal-header {
            display: flex; justify-content: space-between; align-items: center;
            border-bottom: 1px solid #1e293b; padding-bottom: 0.8rem; margin-bottom: 1rem;
        }
        .modal-header h3 { font-size: 1.1rem; font-weight: 800; color: #fff; display: flex; align-items: center; gap: 0.5rem; }
        .modal-close-btn { background: transparent; border: none; font-size: 1.4rem; color: #94a3b8; cursor: pointer; }
        .modal-close-btn:hover { color: #fff; }
        .form-group { margin-bottom: 0.9rem; display: flex; flex-direction: column; gap: 0.3rem; }
        .form-label { font-size: 0.78rem; font-weight: 700; color: #94a3b8; }
        .form-input, .form-select {
            background: #090d16; border: 1px solid #1e293b; border-radius: 6px;
            padding: 0.55rem 0.8rem; color: #fff; font-size: 0.85rem; outline: none;
        }
        .form-input:focus, .form-select:focus { border-color: var(--upc-green-light); }
        .modal-footer {
            display: flex; justify-content: flex-end; gap: 0.7rem; margin-top: 1.2rem;
            border-top: 1px solid #1e293b; padding-top: 0.9rem;
        }
        .btn-modal-cancel {
            background: #1e293b; color: #94a3b8; border: none; padding: 0.5rem 1rem;
            border-radius: 6px; font-weight: 600; cursor: pointer;
        }
        .btn-modal-cancel:hover { background: #334155; color: #fff; }
        .btn-modal-save {
            background: var(--upc-green); color: #fff; border: none; padding: 0.5rem 1.2rem;
            border-radius: 6px; font-weight: 700; cursor: pointer; box-shadow: 0 2px 10px rgba(0, 104, 55, 0.4);
        }
        .btn-modal-save:hover { background: var(--upc-green-light); color: #000; }

        /* TOAST NOTIFICACIÓN */
        #toast-notification {
            position: fixed; bottom: 25px; right: 25px; z-index: 2000;
            background: #006837; border: 1px solid #10b981; color: #fff;
            padding: 0.75rem 1.3rem; border-radius: 8px; font-weight: 700; font-size: 0.85rem;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.6); display: none; align-items: center; gap: 0.6rem;
            animation: slideInToast 0.3s ease;
        }
        @keyframes slideInToast {
            from { transform: translateY(30px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }

        @media (max-width: 1200px) {
            header { padding: 0.6rem 1rem; }
            .brand-text p { display: none; }
            main { padding: 0.8rem 1rem 1.5rem 1rem; }
            .kpi-bar { padding: 0.8rem 1rem 0.4rem 1rem; }
            .portal-layout { grid-template-columns: 320px 1fr; }
        }
        @media (max-width: 992px) {
            header { justify-content: center; }
            .brand-box { width: 100%; justify-content: space-between; }
            .nav-tabs { width: 100%; justify-content: center; }
            .header-actions { width: 100%; justify-content: flex-end; }
            .portal-layout { grid-template-columns: 1fr; height: auto; min-height: 0; }
            .groups-sidebar { max-height: 400px; }
            .dashboard-container { grid-template-columns: 1fr; }
            .metrics-2024-grid { grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); }
        }
        @media (max-width: 640px) {
            .kpi-bar { grid-template-columns: 1fr; }
            .tab-btn { padding: 0.4rem 0.6rem; font-size: 0.75rem; }
            .header-actions { flex-direction: column; align-items: stretch; }
        }

        footer {
            background: #05070e;
            border-top: 1px solid var(--card-border);
            padding: 0.8rem 2rem;
            font-size: 0.75rem;
            color: var(--text-muted);
            text-align: center;
        }
    </style>
</head>
<body>
    <!-- VENTANA PREVIA DE VALIDACION DE ACCESO (LOGIN INSTITUCIONAL UPC) -->
    <div id="login-overlay" class="modal-overlay" style="display:flex; z-index:9999; background:radial-gradient(circle at center, #082f1d 0%, #050811 100%); backdrop-filter:blur(12px);">
        <div class="modal-box" style="max-width:410px; width:92%; border-color:rgba(16,185,129,0.35); box-shadow:0 24px 60px rgba(0,0,0,0.85);">
            <div class="modal-header" style="flex-direction:column; align-items:center; text-align:center; padding:1.6rem 1.5rem 1.1rem; background:linear-gradient(180deg, rgba(16,185,129,0.14) 0%, rgba(15,23,42,0) 100%); border-bottom:1px solid rgba(255,255,255,0.07);">
                <div style="width:62px; height:62px; background:#ffffff; border-radius:14px; padding:5px; display:flex; align-items:center; justify-content:center; margin-bottom:0.75rem; box-shadow:0 6px 18px rgba(0,0,0,0.45); border:2px solid #10b981;">
                    <img id="login-logo-img" src="" alt="UPC" style="width:100%; height:100%; object-fit:contain;">
                </div>
                <h3 style="font-size:1.1rem; font-weight:800; color:#fff; margin-bottom:0.2rem;">Validación de Acceso &bull; PEA-i UPC</h3>
                <p style="font-size:0.76rem; color:#94a3b8; margin:0;">Sistema Estadístico de Investigación (MinCiencias SCIENTI)</p>
            </div>
            <form onsubmit="validarLoginPortal(event)" style="padding:1.35rem 1.6rem 1.5rem;">
                <div class="form-group" style="margin-bottom:0.9rem;">
                    <label style="font-size:0.76rem; font-weight:700; color:#cbd5e1; margin-bottom:0.35rem; display:block;">Usuario Institucional</label>
                    <input type="text" id="login-user" class="form-control" placeholder="Ej: admin" value="admin" required autocomplete="username" style="width:100%; padding:0.65rem 0.85rem; font-size:0.88rem;">
                </div>
                <div class="form-group" style="margin-bottom:0.9rem;">
                    <label style="font-size:0.76rem; font-weight:700; color:#cbd5e1; margin-bottom:0.35rem; display:block;">Contraseña de Acceso</label>
                    <input type="password" id="login-pass" class="form-control" placeholder="Ingrese contraseña (1234)" value="1234" required autocomplete="current-password" style="width:100%; padding:0.65rem 0.85rem; font-size:0.88rem;">
                </div>
                <div id="login-error-msg" style="display:none; background:rgba(239,68,68,0.15); border:1px solid rgba(239,68,68,0.4); color:#fca5a5; padding:0.55rem 0.75rem; border-radius:8px; font-size:0.76rem; margin-bottom:0.9rem; text-align:center; font-weight:600;">
                    Credenciales incorrectas. Verifique usuario y contraseña.
                </div>
                <div style="background:rgba(15,23,42,0.75); border:1px dashed rgba(148,163,184,0.28); border-radius:8px; padding:0.5rem 0.75rem; margin-bottom:1.1rem; font-size:0.73rem; color:#94a3b8; display:flex; justify-content:space-between; align-items:center;">
                    <span>Credenciales por defecto:</span>
                    <span style="color:#34d399; font-family:'JetBrains Mono', monospace; font-weight:700;">admin / 1234</span>
                </div>
                <button type="submit" class="btn-submit" style="width:100%; padding:0.72rem; background:linear-gradient(135deg, #10b981, #059669); color:#022c22; font-weight:800; font-size:0.88rem; border:none; border-radius:8px; cursor:pointer; box-shadow:0 4px 14px rgba(16,185,129,0.35);">
                    Ingresar al Sistema PEA-i
                </button>
            </form>
        </div>
    </div>

    <!-- HEADER -->
    <header>
        <div class="brand-box">
            <div class="brand-logo"><img src="data:image/png;base64,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" alt="Logo Oficial Universidad Popular del Cesar" title="Universidad Popular del Cesar (UPC)"></div>
            <div class="brand-text">
                <h1>PEA-i &bull; Portal de Ciencia Abierta <span class="brand-badge">CRUD Interactivo</span></h1>
                <p>Facultad de Ingeniería y Tecnológicas &bull; Sistema Estadístico de Investigación (MinCiencias SCIENTI)</p>
            </div>
        </div>
        <div class="nav-tabs">
            <button class="tab-btn active" onclick="cambiarVistaPrincipal('portal')">Directorio Grupos</button>
            <button class="tab-btn" onclick="cambiarVistaPrincipal('dashboard')">Dashboard Analítico</button>
            <button class="tab-btn" onclick="cambiarVistaPrincipal('red')">Red de Colaboración</button>
            <button class="tab-btn" onclick="cambiarVistaPrincipal('tablas')">Vistas por Entidad</button>
            <button class="tab-btn" onclick="cambiarVistaPrincipal('crud')">Panel CRUD</button>
        </div>
        <div class="header-actions" style="position:relative;">
            <button class="action-btn-undo" id="btn-undo-header" onclick="deshacerUltimaAccion()" title="Deshacer última acción en Pila LIFO (Ctrl+Z)">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 7v6h6"></path><path d="M21 17a9 9 0 0 0-9-9 9 9 0 0 0-6 2.3L3 13"></path></svg>
                <span>Deshacer (Ctrl+Z)</span>
                <span class="badge-counter" id="undo-count">0</span>
            </button>
            <button class="action-btn-pila" id="btn-pila-popover" onclick="togglePopoverPilaUndo(event)" title="Inspeccionar Pila LIFO en tiempo real">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></svg>
                <span>Pila LIFO &#9662;</span>
            </button>
            <button class="action-btn-export" onclick="abrirModalExportar()" title="Exportar cambios para SQLite / C++">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path></svg>
                <span>Sincronizar SQLite</span>
            </button>
            <button class="action-btn-pila" onclick="cerrarSesionPortal()" title="Cerrar sesión y bloquear sistema" style="border-color:rgba(239,68,68,0.4); color:#fca5a5;">
                <span>Salir</span>
            </button>

            <!-- POPOVER FLOTANTE DE PILA LIFO EN TIEMPO REAL -->
            <div id="popover-historial-undo" style="display:none; position:absolute; top:calc(100% + 10px); right:0; width:360px; background:#0f172a; border:1px solid #334155; border-radius:10px; box-shadow:0 16px 36px rgba(0,0,0,0.85); z-index:1200; padding:0.85rem;">
                <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #1e293b; padding-bottom:0.55rem; margin-bottom:0.6rem;">
                    <div style="font-size:0.8rem; font-weight:800; color:#fff;">Pila LIFO de Operaciones (Undo)</div>
                    <span style="background:#1e293b; color:#38bdf8; border:1px solid #334155; padding:2px 6px; border-radius:4px; font-size:0.68rem; font-weight:700;">Atajo: Ctrl + Z</span>
                </div>
                <div id="popover-undo-list" style="max-height:240px; overflow-y:auto; display:flex; flex-direction:column; gap:0.4rem; margin-bottom:0.7rem;"></div>
                <div style="display:flex; justify-content:space-between; gap:0.5rem; border-top:1px solid #1e293b; padding-top:0.6rem;">
                    <button onclick="deshacerUltimaAccion()" class="btn-action-sm" style="flex:1; background:#f59e0b; color:#000; font-weight:800;">Deshacer Tope (POP)</button>
                    <button onclick="cerrarPopoverUndo(); abrirModalPilaUndo();" class="btn-action-sm" style="background:#1e293b; color:#cbd5e1; border:1px solid #334155;">Tabla Completa</button>
                </div>
            </div>
        </div>
    </header>

    <!-- KPI BAR -->
    <div class="kpi-bar">
        <div class="kpi-card">
            <div>
                <div class="kpi-title">Grupos de Investigación</div>
                <div class="kpi-val" id="kpi-grupos" style="color: #38bdf8;">0</div>
            </div>
            <div class="kpi-icon-wrap">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path></svg>
            </div>
        </div>
        <div class="kpi-card">
            <div>
                <div class="kpi-title">Investigadores Registrados</div>
                <div class="kpi-val" id="kpi-investigadores" style="color: #10b981;">0</div>
            </div>
            <div class="kpi-icon-wrap">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
            </div>
        </div>
        <div class="kpi-card">
            <div>
                <div class="kpi-title">Productos Científicos</div>
                <div class="kpi-val" id="kpi-productos" style="color: #f59e0b;">0</div>
            </div>
            <div class="kpi-icon-wrap">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path></svg>
            </div>
        </div>
        <div class="kpi-card">
            <div>
                <div class="kpi-title">Puntos IPP (Modelo 2024)</div>
                <div class="kpi-val" id="kpi-ipp" style="color: #c084fc;">0 pts</div>
            </div>
            <div class="kpi-icon-wrap">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#c084fc" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>
            </div>
        </div>
    </div>

    <!-- MAIN -->
    <main>
        <!-- VISTA 1: PORTAL DE GRUPOS -->
        <section id="view-portal" class="view-panel active">
            <div class="portal-layout">
                <!-- COLUMNA IZQUIERDA: LISTA -->
                <div class="groups-sidebar">
                    <div class="sidebar-header">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.6rem;">
                            <span style="font-weight:800; font-size:0.85rem; color:#cbd5e1; text-transform:uppercase; letter-spacing:0.5px;">Directorio</span>
                            <button onclick="abrirModalGrupo()" style="background:var(--upc-green); color:#fff; border:none; padding:4px 10px; border-radius:6px; font-weight:700; font-size:0.75rem; cursor:pointer;" title="Registrar un nuevo grupo en la Multilista">
                                + Nuevo Grupo
                            </button>
                        </div>
                        <input type="text" class="search-input" id="search-grupos" placeholder="Buscar por nombre o código (ej: GISICO)..." oninput="filtrarListaGrupos()">
                        <div class="filter-tags">
                            <button class="tag-btn active" onclick="filtrarCategoriaGrupo('')">Todos</button>
                            <button class="tag-btn" onclick="filtrarCategoriaGrupo('A1')">Cat. A1</button>
                            <button class="tag-btn" onclick="filtrarCategoriaGrupo('A')">Cat. A</button>
                            <button class="tag-btn" onclick="filtrarCategoriaGrupo('B')">Cat. B</button>
                            <button class="tag-btn" onclick="filtrarCategoriaGrupo('C')">Cat. C</button>
                            <button class="tag-btn" onclick="filtrarCategoriaGrupo('Reconocido')">Rec.</button>
                        </div>
                    </div>
                    <div class="groups-scroll-list" id="groups-list-container">
                        <!-- Generado dinámicamente -->
                    </div>
                </div>

                <!-- COLUMNA DERECHA: DETALLE DEL GRUPO -->
                <div class="group-detail-view" id="group-profile-panel">
                    <!-- HERO -->
                    <div class="group-hero">
                        <div class="hero-info">
                            <div class="hero-avatar" id="g-avatar">G</div>
                            <div class="hero-title">
                                <h2 id="g-nombre">Seleccione un Grupo</h2>
                                <div class="hero-meta">
                                    <span class="badge-cat" id="g-badge-cat">Cat. C</span>
                                    <span>&bull;</span>
                                    <span id="g-codigo" style="font-family:monospace; font-weight:700; color:#38bdf8;">COL0000000</span>
                                    <span>&bull;</span>
                                    <span id="g-badge-status-hero" class="badge-status badge-active">Activo</span>
                                    <span>&bull;</span>
                                    <span>Universidad Popular del Cesar (UPC)</span>
                                </div>
                            </div>
                        </div>
                        <div class="hero-actions">
                            <button onclick="editarGrupoActual()" class="btn-action-hero" title="Modificar datos de este grupo">
                                <span>Editar Grupo</span>
                            </button>
                            <button onclick="toggleEstadoGrupoActual()" id="btn-toggle-hero" class="btn-action-hero" style="color:#fca5a5; border-color:rgba(248,113,113,0.35);" title="Inactivar o activar este grupo">
                                <span>Desactivar</span>
                            </button>
                            <a href="#" class="btn-pdf-download" id="btn-descargar-pdf" target="_blank">
                                <span>Informe PDF</span>
                            </a>
                        </div>
                    </div>

                    <!-- SUB-TABS DEL PERFIL -->
                    <div class="profile-nav">
                        <button class="p-tab-btn active" onclick="cambiarSubTab('general')">Información General</button>
                        <button class="p-tab-btn" onclick="cambiarSubTab('integrantes')" id="tab-lbl-inv">Integrantes (0)</button>
                        <button class="p-tab-btn" onclick="cambiarSubTab('productos')" id="tab-lbl-prod">Productos (0)</button>
                        <button class="p-tab-btn" onclick="cambiarSubTab('modelo2024')">Balance MinCiencias 2024 & IPP</button>
                    </div>

                    <!-- CONTENIDO DE LAS SUB-PESTAÑAS -->
                    <div class="profile-content">
                        <!-- SUB-TAB: GENERAL -->
                        <div id="subtab-general" class="profile-section active">
                            <div class="info-grid">
                                <div class="info-card">
                                    <div class="info-card-label">Investigador Líder Oficial</div>
                                    <div class="info-card-val" id="g-lider">-</div>
                                </div>
                                <div class="info-card">
                                    <div class="info-card-label">Año de Creación Oficial</div>
                                    <div class="info-card-val" id="g-anio">-</div>
                                </div>
                                <div class="info-card">
                                    <div class="info-card-label">Gran Área de Conocimiento</div>
                                    <div class="info-card-val" id="g-area">-</div>
                                </div>
                                <div class="info-card">
                                    <div class="info-card-label">Total Integrantes / Productos</div>
                                    <div class="info-card-val" id="g-resumen-conteo">-</div>
                                </div>
                            </div>

                            <div class="info-card" style="margin-top: 1rem;">
                                <div class="info-card-label">Modelo de Estructura de Datos en Memoria RAM (Hipercubo Ortogonal 3D)</div>
                                <p style="font-size:0.82rem; color:var(--text-muted); line-height:1.5; margin-top:0.4rem;">
                                    Este grupo está modelado en el núcleo C++ como un nodo maestro en el <b>Eje X</b> de la Multilista.
                                    Posee punteros ortogonales directos: <code>primerInvestigador</code> hacia el <b>Eje Y</b> (sublista de integrantes)
                                    y <code>primerProductoGrupo</code> hacia el <b>Eje Z</b> (cadena de productos científicos vinculados simultáneamente al grupo y a su autor real).
                                </p>
                            </div>
                        </div>

                        <!-- SUB-TAB: INTEGRANTES -->
                        <div id="subtab-integrantes" class="profile-section">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.8rem;">
                                <span style="font-size:0.85rem; color:#94a3b8; font-weight:700;">Integrantes vinculados a este grupo</span>
                                <button onclick="abrirModalInvestigador(grupoSeleccionado ? grupoSeleccionado.codigo : '')" class="btn-action-sm btn-action-edit" style="background:var(--upc-green); color:#fff; border-color:var(--upc-green-light); padding:5px 12px;">
                                    + Vincular Nuevo Integrante
                                </button>
                            </div>
                            <div class="data-table-container">
                                <table class="peai-table" id="tabla-perfil-inv">
                                    <thead>
                                        <tr>
                                            <th>Documento</th>
                                            <th>Nombre Completo</th>
                                            <th>Perfiles Externos</th>
                                            <th>Escalafón</th>
                                            <th>Formación Académica</th>
                                            <th>Estado</th>
                                            <th style="text-align:center;">Acciones</th>
                                        </tr>
                                    </thead>
                                    <tbody></tbody>
                                </table>
                            </div>
                        </div>

                        <!-- SUB-TAB: PRODUCTOS -->
                        <div id="subtab-productos" class="profile-section">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.8rem;">
                                <span style="font-size:0.85rem; color:#94a3b8; font-weight:700;">Producción científica asignada</span>
                                <button onclick="abrirModalProducto(grupoSeleccionado ? grupoSeleccionado.codigo : '')" class="btn-action-sm btn-action-edit" style="background:#059669; color:#fff; border-color:#10b981; padding:5px 12px;">
                                    + Registrar Nuevo Producto
                                </button>
                            </div>
                            <div class="data-table-container">
                                <table class="peai-table" id="tabla-perfil-prod">
                                    <thead>
                                        <tr>
                                            <th>Año</th>
                                            <th>Familia 2024</th>
                                            <th>Código</th>
                                            <th>Título de la Publicación</th>
                                            <th>Tipo</th>
                                            <th>Aval</th>
                                            <th>Puntos IPP</th>
                                            <th style="text-align:center;">Acciones</th>
                                        </tr>
                                    </thead>
                                    <tbody></tbody>
                                </table>
                            </div>
                        </div>

                        <!-- SUB-TAB: MODELO 2024 & IPP -->
                        <div id="subtab-modelo2024" class="profile-section">
                            <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 8px; padding: 1rem; margin-bottom: 1rem; display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <div style="font-size: 0.75rem; text-transform: uppercase; font-weight: 700; color: var(--upc-green-light);">Índice de Producción Ponderada (IPP) Acumulado</div>
                                    <div style="font-size: 1.5rem; font-weight: 900; color: #fff;" id="g-total-ipp">0 puntos</div>
                                </div>
                                <div style="font-size: 0.78rem; color: var(--text-muted); text-align: right;">
                                    Conforme a Convocatoria Nacional 957 / Anexo 1<br>
                                    Cálculo oficial sobre productos validados
                                </div>
                            </div>

                            <div class="metrics-2024-grid">
                                <div class="metric-fam-card">
                                    <div class="fam-code gnc">GNC</div>
                                    <div class="fam-desc">Generación Nuevo Conocimiento</div>
                                    <div class="fam-count" id="cnt-gnc">0</div>
                                    <div class="fam-pts" id="pts-gnc">0 pts</div>
                                </div>
                                <div class="metric-fam-card">
                                    <div class="fam-code dti">DTI</div>
                                    <div class="fam-desc">Desarrollo Tecnológico</div>
                                    <div class="fam-count" id="cnt-dti">0</div>
                                    <div class="fam-pts" id="pts-dti">0 pts</div>
                                </div>
                                <div class="metric-fam-card">
                                    <div class="fam-code asc">ASC</div>
                                    <div class="fam-desc">Apropiación Social</div>
                                    <div class="fam-count" id="cnt-asc">0</div>
                                    <div class="fam-pts" id="pts-asc">0 pts</div>
                                </div>
                                <div class="metric-fam-card">
                                    <div class="fam-code dpc">DPC</div>
                                    <div class="fam-desc">Divulgación Pública</div>
                                    <div class="fam-count" id="cnt-dpc">0</div>
                                    <div class="fam-pts" id="pts-dpc">0 pts</div>
                                </div>
                                <div class="metric-fam-card">
                                    <div class="fam-code frh">FRH</div>
                                    <div class="fam-desc">Formación Recurso Humano</div>
                                    <div class="fam-count" id="cnt-frh">0</div>
                                    <div class="fam-pts" id="pts-frh">0 pts</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- VISTA 2: DASHBOARD ANALÍTICO -->
        <section id="view-dashboard" class="view-panel">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.8rem; margin-bottom:1rem; background:var(--bg-card); padding:0.9rem 1.2rem; border-radius:10px; border:1px solid var(--card-border);">
                <div>
                    <h3 style="font-size:1.02rem; margin:0;">Filtro por Ventana de Observación (Requisito 10 y Modelo 2024)</h3>
                    <p style="font-size:0.75rem; color:var(--text-muted); margin:0.2rem 0 0 0;" id="lbl-ventana-desc">Mostrando serie histórica completa (Todos los años)</p>
                </div>
                <div style="display:flex; gap:0.45rem; flex-wrap:wrap;">
                    <button class="tag-btn active" id="btn-win-0" onclick="cambiarVentanaObservacion(0)">Histórico Completo</button>
                    <button class="tag-btn" id="btn-win-2024" onclick="cambiarVentanaObservacion(2024)" title="Aplica 10 años para Libros, Capítulos y Patentes, y 5 años para el resto de productos (Regla MinCiencias 2024)">Corte Modelo 2024 (5/10 Años)</button>
                    <button class="tag-btn" id="btn-win-5" onclick="cambiarVentanaObservacion(5)">Últimos 5 Años (2021-2026)</button>
                    <button class="tag-btn" id="btn-win-2" onclick="cambiarVentanaObservacion(2)">Últimos 2 Años (2024-2026)</button>
                </div>
            </div>

            <div class="dashboard-container">
                <div class="chart-box">
                    <div class="chart-box-title">
                        <span>Distribución por Año de Publicación</span>
                        <span style="font-size:0.75rem; color:#38bdf8;">Cronología</span>
                    </div>
                    <div id="chart-anios-container" style="max-height: 280px; overflow-y:auto;"></div>
                </div>

                <div class="chart-box">
                    <div class="chart-box-title">
                        <span>Grupos por Categoría MinCiencias</span>
                        <span style="font-size:0.75rem; color:#10b981;">Escalafón Oficial</span>
                    </div>
                    <div id="chart-cat-container"></div>
                </div>

                <div class="chart-box">
                    <div class="chart-box-title">
                        <span>Modelo 2024: Las 5 Macro-Familias</span>
                        <span style="font-size:0.75rem; color:#f59e0b;">Tipología CTeI</span>
                    </div>
                    <div id="chart-familias-container"></div>
                </div>

                <div class="chart-box">
                    <div class="chart-box-title">
                        <span>Aval Institucional / Validación MinCiencias</span>
                        <span style="font-size:0.75rem; color:#c084fc;">Auditoría</span>
                    </div>
                    <div id="chart-aval-container"></div>
                </div>
            </div>
        </section>

        <!-- VISTA 3: VISTAS POR ENTIDAD (PUNTO 12.C) -->
        <section id="view-tablas" class="view-panel">
            <div class="chart-box" style="margin-bottom: 1.5rem;">
                <div class="chart-box-title">
                    <span>i. Resumen por Grupo de Investigación (12.c.i)</span>
                    <span style="font-size:0.75rem; color:var(--text-muted);" id="lbl-total-grupos-tab"></span>
                </div>
                <div class="data-table-container">
                    <table class="peai-table" id="tabla-entidad-grupos">
                        <thead>
                            <tr>
                                <th>Código</th>
                                <th>Nombre Oficial</th>
                                <th>Clasif.</th>
                                <th>Líder</th>
                                <th>Integrantes</th>
                                <th>Productos</th>
                                <th>Informe Oficial</th>
                            </tr>
                        </thead>
                        <tbody></tbody>
                    </table>
                </div>
            </div>

            <div class="chart-box">
                <div class="chart-box-title">
                    <span>ii. Escalafón de Investigadores (12.c.ii)</span>
                    <span style="font-size:0.75rem; color:var(--text-muted);">Ranking por Obras Registradas</span>
                </div>
                <div class="data-table-container">
                    <table class="peai-table" id="tabla-entidad-inv">
                        <thead>
                            <tr>
                                <th>Documento</th>
                                <th>Nombre Completo</th>
                                <th>Categoría</th>
                                <th>Grupo</th>
                                <th>Obras Registradas</th>
                            </tr>
                        </thead>
                        <tbody></tbody>
                    </table>
                </div>
            </div>
        </section>

        <!-- VISTA 4: CENTRO DE GESTIÓN Y CONTROL CRUD COMPLETO -->
        <section id="view-crud" class="view-panel">
            <!-- BANNER EXPLICATIVO Y PERSISTENCIA -->
            <div style="background: linear-gradient(135deg, #0b1528 0%, #0f2219 100%); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 12px; padding: 1.2rem 1.5rem; margin-bottom: 1.2rem; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
                <div style="max-width: 720px;">
                    <div style="display:flex; align-items:center; gap:0.6rem; margin-bottom:0.3rem;">
                        <h2 style="font-size:1.15rem; font-weight:800; margin:0; color:#fff;">Panel de Administración CRUD (Hipercubo en Memoria RAM & SQLite)</h2>
                        <span class="brand-badge" style="background:#0284c7;">Tiempo Real</span>
                    </div>
                    <p style="font-size:0.8rem; color:#cbd5e1; margin:0; line-height:1.4;">
                        Gestiona el ciclo de vida de los datos de investigación de la UPC. Puedes <b>Crear (+ Nuevo)</b>, <b>Editar</b> o <b>Desactivar</b> registros. Cada mutación actualiza inmediatamente los KPIs, gráficos y puntajes IPP. Puedes usar <b>Deshacer</b> para revertir acciones o presionar <b>Sincronizar SQLite</b> para persistir en la base de datos.
                    </p>
                </div>
                <div style="display:flex; gap:0.6rem; align-items:center;">
                    <button onclick="deshacerUltimaAccion()" class="action-btn-undo" style="background:#1e293b; color:#fff; border:1px solid #334155; padding:0.5rem 1rem; border-radius:8px; font-weight:700; cursor:pointer; display:flex; align-items:center; gap:0.4rem;">
                        <span>Deshacer Último</span>
                    </button>
                    <button onclick="abrirModalExportar()" class="action-btn-export" style="background:var(--upc-green); color:#fff; border:none; padding:0.5rem 1rem; border-radius:8px; font-weight:700; cursor:pointer; display:flex; align-items:center; gap:0.4rem;">
                        <span>Sincronizar SQLite</span>
                    </button>
                </div>
            </div>

            <!-- SELECTOR DE ENTIDADES -->
            <div class="crud-tab-nav">
                <button class="crud-tab-btn active" id="crud-tab-btn-g" onclick="cambiarSubTabCRUD('grupos')">
                    Grupos de Investigación (<span id="crud-badge-g">0</span>)
                </button>
                <button class="crud-tab-btn" id="crud-tab-btn-i" onclick="cambiarSubTabCRUD('investigadores')">
                    Investigadores Adscritos (<span id="crud-badge-i">0</span>)
                </button>
                <button class="crud-tab-btn" id="crud-tab-btn-p" onclick="cambiarSubTabCRUD('productos')">
                    Productos Científicos (<span id="crud-badge-p">0</span>)
                </button>
            </div>

            <!-- SUBPANEL CRUD: GRUPOS -->
            <div id="crud-panel-grupos" class="crud-subpanel">
                <div class="crud-toolbar">
                    <div class="crud-toolbar-left">
                        <input type="text" class="search-input" id="search-crud-grupos" placeholder="Buscar grupos por código, nombre o líder..." oninput="renderizarCRUDGrupos()" style="min-width:320px;">
                        <select id="filtro-crud-grupos-estado" class="search-input" style="width:160px;" onchange="renderizarCRUDGrupos()">
                            <option value="todos">Todos los Estados</option>
                            <option value="activos">Solo Activos</option>
                            <option value="inactivos">Solo Inactivos</option>
                        </select>
                        <button onclick="limpiarFiltrosGrupos()" class="btn-action-sm" style="background:#334155; color:#cbd5e1; padding:0.5rem 0.8rem;">Limpiar</button>
                    </div>
                    <div style="display:flex; gap:0.5rem; align-items:center;">
                        <button onclick="exportarTablaCSV('grupos')" class="btn-action-sm" style="background:#1e293b; color:#38bdf8; border:1px solid #334155; padding:0.55rem 0.9rem;" title="Descargar tabla en formato CSV con BOM UTF-8 compatible con Microsoft Excel">
                            Exportar CSV (Excel)
                        </button>
                        <button onclick="abrirModalGrupo()" class="crud-btn-create">
                            + Registrar Nuevo Grupo
                        </button>
                    </div>
                </div>
                <div class="data-table-container">
                    <table class="peai-table" id="tabla-crud-grupos">
                        <thead>
                            <tr>
                                <th>Código</th>
                                <th>Nombre Oficial del Grupo</th>
                                <th>Clasificación</th>
                                <th>Líder</th>
                                <th>Año</th>
                                <th>Estado</th>
                                <th style="text-align:center;">Acciones (CRUD)</th>
                            </tr>
                        </thead>
                        <tbody></tbody>
                    </table>
                </div>
            </div>

            <!-- SUBPANEL CRUD: INVESTIGADORES -->
            <div id="crud-panel-investigadores" class="crud-subpanel" style="display:none;">
                <div class="crud-toolbar">
                    <div class="crud-toolbar-left">
                        <input type="text" class="search-input" id="search-crud-inv" placeholder="Buscar por documento o nombre..." oninput="irPaginaCRUDInv(1)" style="min-width:300px;">
                        <select id="filtro-crud-inv-grupo" class="search-input" style="max-width:240px;" onchange="irPaginaCRUDInv(1)">
                            <option value="">Todos los Grupos</option>
                        </select>
                        <select id="filtro-crud-inv-estado" class="search-input" style="width:160px;" onchange="irPaginaCRUDInv(1)">
                            <option value="todos">Todos los Estados</option>
                            <option value="activos">Solo Activos</option>
                            <option value="inactivos">Solo Inactivos</option>
                        </select>
                        <button onclick="limpiarFiltrosInv()" class="btn-action-sm" style="background:#334155; color:#cbd5e1; padding:0.5rem 0.8rem;">Limpiar</button>
                    </div>
                    <div style="display:flex; gap:0.5rem; align-items:center;">
                        <button onclick="exportarTablaCSV('investigadores')" class="btn-action-sm" style="background:#1e293b; color:#38bdf8; border:1px solid #334155; padding:0.55rem 0.9rem;" title="Descargar investigadores filtrados en CSV con BOM UTF-8 para Excel">
                            Exportar CSV (Excel)
                        </button>
                        <button onclick="abrirModalInvestigador()" class="crud-btn-create">
                            + Registrar Nuevo Investigador
                        </button>
                    </div>
                </div>
                <div class="data-table-container">
                    <table class="peai-table" id="tabla-crud-inv">
                        <thead>
                            <tr>
                                <th>Documento ID</th>
                                <th>Nombre Completo</th>
                                <th>Categoría</th>
                                <th>Formación Académica</th>
                                <th>Perfiles Externos</th>
                                <th>Grupo</th>
                                <th>Estado</th>
                                <th style="text-align:center;">Acciones (CRUD)</th>
                            </tr>
                        </thead>
                        <tbody></tbody>
                    </table>
                </div>
                <div class="crud-pagination" id="paginacion-crud-inv">
                    <span id="info-pag-inv">Mostrando registros</span>
                    <div style="display:flex; gap:0.4rem; align-items:center;">
                        <button id="btn-pag-inv-prev" onclick="cambiarPaginaCRUDInv(-1)" class="crud-page-btn">Anterior</button>
                        <span id="lbl-pag-inv-actual" style="font-weight:700; color:#fff;">Página 1</span>
                        <button id="btn-pag-inv-next" onclick="cambiarPaginaCRUDInv(1)" class="crud-page-btn">Siguiente</button>
                    </div>
                </div>
            </div>

            <!-- SUBPANEL CRUD: PRODUCTOS -->
            <div id="crud-panel-productos" class="crud-subpanel" style="display:none;">
                <div class="crud-toolbar">
                    <div class="crud-toolbar-left">
                        <input type="text" class="search-input" id="search-crud-prod" placeholder="Buscar por título, ID o año..." oninput="irPaginaCRUDProd(1)" style="min-width:300px;">
                        <select id="filtro-crud-prod-grupo" class="search-input" style="max-width:240px;" onchange="irPaginaCRUDProd(1)">
                            <option value="">Todos los Grupos</option>
                        </select>
                        <select id="filtro-crud-prod-estado" class="search-input" style="width:160px;" onchange="irPaginaCRUDProd(1)">
                            <option value="todos">Todos los Estados</option>
                            <option value="activos">Solo Activos</option>
                            <option value="inactivos">Solo Inactivos</option>
                        </select>
                        <button onclick="limpiarFiltrosProd()" class="btn-action-sm" style="background:#334155; color:#cbd5e1; padding:0.5rem 0.8rem;">Limpiar</button>
                    </div>
                    <div style="display:flex; gap:0.5rem; align-items:center;">
                        <button onclick="exportarTablaCSV('productos')" class="btn-action-sm" style="background:#1e293b; color:#38bdf8; border:1px solid #334155; padding:0.55rem 0.9rem;" title="Descargar productos filtrados en CSV con BOM UTF-8 para Excel">
                            Exportar CSV (Excel)
                        </button>
                        <button onclick="abrirModalProducto()" class="crud-btn-create">
                            + Registrar Nuevo Producto
                        </button>
                    </div>
                </div>
                <div class="data-table-container">
                    <table class="peai-table" id="tabla-crud-prod">
                        <thead>
                            <tr>
                                <th>ID Producto</th>
                                <th>Título de la Publicación</th>
                                <th>Tipología CTeI</th>
                                <th>Año</th>
                                <th>Grupo</th>
                                <th>Investigador Autor</th>
                                <th>Aval MinCiencias</th>
                                <th>Estado</th>
                                <th style="text-align:center;">Acciones (CRUD)</th>
                            </tr>
                        </thead>
                        <tbody></tbody>
                    </table>
                </div>
                <div class="crud-pagination" id="paginacion-crud-prod">
                    <span id="info-pag-prod">Mostrando registros</span>
                    <div style="display:flex; gap:0.4rem; align-items:center;">
                        <button id="btn-pag-prod-prev" onclick="cambiarPaginaCRUDProd(-1)" class="crud-page-btn">Anterior</button>
                        <span id="lbl-pag-prod-actual" style="font-weight:700; color:#fff;">Página 1</span>
                        <button id="btn-pag-prod-next" onclick="cambiarPaginaCRUDProd(1)" class="crud-page-btn">Siguiente</button>
                    </div>
                </div>
            </div>
        </section>

        <!-- ========================================================= -->
        <!-- VISTA 5: GRAFO INTERACTIVO DE RED DE COLABORACIÓN (CANVAS) -->
        <!-- ========================================================= -->
        <section id="view-red" class="view-panel">
            <div class="crud-toolbar" style="margin-bottom:0.9rem;">
                <div class="crud-toolbar-left">
                    <label style="font-size:0.78rem; font-weight:700; color:#94a3b8; white-space:nowrap;">Alcance de Red:</label>
                    <select id="filtro-red-grupo" class="search-input" style="max-width:290px;" onchange="construirYRenderizarRed()">
                        <option value="COL0002099">COL0002099 - GISICO (Grupo Focal)</option>
                        <option value="TODOS">Red Institucional (Núcleo Intergrupal Top 50)</option>
                    </select>
                    <input type="text" id="search-red-inv" class="search-input" placeholder="Buscar investigador en el grafo..." oninput="resaltarBuscadoRed()" style="max-width:250px;">
                    <div style="display:inline-flex; gap:5px;">
                        <button onclick="zoomRed(1.2)" class="btn-action-sm" style="background:#1e293b; color:#e2e8f0; border:1px solid #334155;" title="Acercar">+</button>
                        <button onclick="zoomRed(0.82)" class="btn-action-sm" style="background:#1e293b; color:#e2e8f0; border:1px solid #334155;" title="Alejar">&minus;</button>
                        <button onclick="centrarRed()" class="btn-action-sm" style="background:#1e293b; color:#38bdf8; border:1px solid #334155;">Centrar</button>
                    </div>
                </div>
                <div style="display:flex; gap:10px; align-items:center; flex-wrap:wrap; font-size:0.74rem; font-weight:700;">
                    <span style="display:inline-flex; align-items:center; gap:5px;"><span style="width:10px; height:10px; border-radius:50%; background:#10b981; display:inline-block;"></span>Senior</span>
                    <span style="display:inline-flex; align-items:center; gap:5px;"><span style="width:10px; height:10px; border-radius:50%; background:#38bdf8; display:inline-block;"></span>Asociado</span>
                    <span style="display:inline-flex; align-items:center; gap:5px;"><span style="width:10px; height:10px; border-radius:50%; background:#f59e0b; display:inline-block;"></span>Junior</span>
                    <span style="display:inline-flex; align-items:center; gap:5px;"><span style="width:10px; height:10px; border-radius:50%; background:#a855f7; display:inline-block;"></span>Integrante</span>
                </div>
            </div>

            <div style="display:grid; grid-template-columns: 1fr 330px; gap:1rem; height:calc(100vh - 235px); min-height:520px;">
                <div class="chart-card" style="position:relative; padding:0; overflow:hidden; display:flex; flex-direction:column; border-color:#1e293b;">
                    <canvas id="canvas-red-colaboracion" style="width:100%; height:100%; display:block; cursor:grab; background:radial-gradient(circle at center, #0c1526 0%, #060911 100%);"></canvas>
                    <div style="position:absolute; bottom:10px; left:12px; background:rgba(15,23,42,0.88); border:1px solid #1e293b; padding:5px 10px; border-radius:6px; font-size:0.72rem; color:#94a3b8; pointer-events:none;">
                        Arrastrar: Mover lienzo &bull; Rueda: Zoom &bull; Clic en nodo: Inspeccionar investigador y vecindario
                    </div>
                </div>

                <div class="chart-card" style="display:flex; flex-direction:column; gap:0.85rem; overflow-y:auto; padding:1.1rem;">
                    <div style="font-size:0.9rem; font-weight:800; color:#fff; border-bottom:1px solid #1e293b; padding-bottom:0.5rem;">
                        Métricas de Centralidad (Red)
                    </div>
                    <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:0.5rem;">
                        <div style="background:#090d16; border:1px solid #1e293b; border-radius:8px; padding:0.55rem; text-align:center;">
                            <div style="font-size:0.65rem; color:#94a3b8; text-transform:uppercase; font-weight:700;">Nodos</div>
                            <div id="red-kpi-nodos" style="font-size:1.15rem; font-weight:800; color:#38bdf8;">0</div>
                        </div>
                        <div style="background:#090d16; border:1px solid #1e293b; border-radius:8px; padding:0.55rem; text-align:center;">
                            <div style="font-size:0.65rem; color:#94a3b8; text-transform:uppercase; font-weight:700;">Enlaces</div>
                            <div id="red-kpi-aristas" style="font-size:1.15rem; font-weight:800; color:#10b981;">0</div>
                        </div>
                        <div style="background:#090d16; border:1px solid #1e293b; border-radius:8px; padding:0.55rem; text-align:center;">
                            <div style="font-size:0.65rem; color:#94a3b8; text-transform:uppercase; font-weight:700;">Densidad</div>
                            <div id="red-kpi-densidad" style="font-size:1.15rem; font-weight:800; color:#f59e0b;">0.00</div>
                        </div>
                    </div>

                    <div id="red-inspector-nodo" style="background:#090d16; border:1px solid #1e293b; border-radius:8px; padding:0.8rem; font-size:0.8rem;">
                        <div style="color:#64748b; font-size:0.76rem;">Seleccione o pase el cursor sobre un nodo del grafo para inspeccionar su centralidad de grado, coautorías y perfiles científicos.</div>
                    </div>

                    <div style="font-size:0.8rem; font-weight:800; color:#cbd5e1; margin-top:0.2rem;">
                        Top 5 Investigadores Más Conectados
                    </div>
                    <div id="red-top-conectados" style="display:flex; flex-direction:column; gap:0.45rem;"></div>
                </div>
            </div>
        </section>
    </main>

    <!-- FOOTER -->
    <footer>
        PEA-i &bull; Programa Estadístico de Análisis de Investigación &bull; Universidad Popular del Cesar (UPC) &bull; C++17 Core Engine &bull; MinCiencias Convocatoria 957
    </footer>

    <!-- MODALES CRUD Y PERSISTENCIA -->
    <!-- 1. MODAL GRUPO -->
    <div id="modal-grupo" class="modal-overlay" style="display:none;">
        <div class="modal-box">
            <div class="modal-header">
                <h3 id="modal-g-title">Registrar Nuevo Grupo</h3>
                <button onclick="cerrarModales()" class="modal-close-btn">&times;</button>
            </div>
            <form onsubmit="guardarGrupoForm(event)">
                <div class="form-group">
                    <label class="form-label">Código del Grupo (Identificador Único):</label>
                    <input type="text" id="input-g-codigo" class="form-input" required placeholder="Ej: COL0018706">
                </div>
                <div class="form-group">
                    <label class="form-label">Nombre Oficial del Grupo:</label>
                    <input type="text" id="input-g-nombre" class="form-input" required placeholder="Ej: GRUPO DE INVESTIGACIÓN GISICO">
                </div>
                <div class="form-group">
                    <label class="form-label">Clasificación MinCiencias:</label>
                    <select id="input-g-clasif" class="form-select">
                        <option value="A1">Categoría A1</option>
                        <option value="A">Categoría A</option>
                        <option value="B">Categoría B</option>
                        <option value="C" selected>Categoría C</option>
                        <option value="Reconocido">Reconocido</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">Gran Área de Conocimiento:</label>
                    <input type="text" id="input-g-area" class="form-input" required placeholder="Ej: Ingeniería y Tecnología">
                </div>
                <div class="form-group">
                    <label class="form-label">Investigador Líder Oficial:</label>
                    <input type="text" id="input-g-lider" class="form-input" required placeholder="Ej: Dr. John Jairo Patiño Vanegas">
                </div>
                <div class="form-group">
                    <label class="form-label">Año de Creación / Reconocimiento:</label>
                    <input type="number" id="input-g-anio" class="form-input" required min="1970" max="2026" value="2024">
                </div>
                <div class="modal-footer">
                    <button type="button" onclick="cerrarModales()" class="btn-modal-cancel">Cancelar</button>
                    <button type="submit" class="btn-modal-save">Guardar Grupo</button>
                </div>
            </form>
        </div>
    </div>

    <!-- 2. MODAL INVESTIGADOR -->
    <div id="modal-investigador" class="modal-overlay" style="display:none;">
        <div class="modal-box">
            <div class="modal-header">
                <h3 id="modal-i-title">Registrar Nuevo Investigador</h3>
                <button onclick="cerrarModales()" class="modal-close-btn">&times;</button>
            </div>
            <form onsubmit="guardarInvestigadorForm(event)">
                <div class="form-group">
                    <label class="form-label">Documento ID / Cédula / CvLAC:</label>
                    <input type="text" id="input-i-doc" class="form-input" required placeholder="Ej: 0000494917">
                </div>
                <div class="form-group">
                    <label class="form-label">Nombre Completo del Investigador:</label>
                    <input type="text" id="input-i-nombre" class="form-input" required placeholder="Ej: Ing. Adith Bismarck Pérez Orozco">
                </div>
                <div class="form-group">
                    <label class="form-label">Categoría MinCiencias:</label>
                    <select id="input-i-cat" class="form-select">
                        <option value="Senior" selected>Investigador Senior (IS)</option>
                        <option value="Asociado">Investigador Asociado (I)</option>
                        <option value="Junior">Investigador Junior (IJ)</option>
                        <option value="Sin Categoria">Integrante Vinculado (Sin Categoría)</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">Formación Académica Principal:</label>
                    <input type="text" id="input-i-formacion" class="form-input" required placeholder="Ej: Maestría en Ciencias Computacionales">
                </div>
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">
                    <div class="form-group">
                        <label class="form-label">Par Evaluador MinCiencias:</label>
                        <select id="input-i-par" class="form-select">
                            <option value="No">No</option>
                            <option value="Si">Sí (Par Reconocido)</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Grupo de Investigación Asignado:</label>
                        <select id="input-i-grupo" class="form-select" required></select>
                    </div>
                </div>
                <div class="form-group">
                    <label class="form-label">Enlace Google Scholar (Opcional):</label>
                    <input type="text" id="input-i-scholar" class="form-input" placeholder="https://scholar.google.com/citations?user=...">
                </div>
                <div class="form-group">
                    <label class="form-label">Enlace / Identificador ORCID (Opcional):</label>
                    <input type="text" id="input-i-orcid" class="form-input" placeholder="https://orcid.org/0000-0002-...">
                </div>
                <div class="modal-footer">
                    <button type="button" onclick="cerrarModales()" class="btn-modal-cancel">Cancelar</button>
                    <button type="submit" class="btn-modal-save">Guardar Investigador</button>
                </div>
            </form>
        </div>
    </div>

    <!-- 3. MODAL PRODUCTO -->
    <div id="modal-producto" class="modal-overlay" style="display:none;">
        <div class="modal-box">
            <div class="modal-header">
                <h3 id="modal-p-title">Registrar Producto de Investigación</h3>
                <button onclick="cerrarModales()" class="modal-close-btn">&times;</button>
            </div>
            <form onsubmit="guardarProductoForm(event)">
                <div class="form-group">
                    <label class="form-label">ID Único del Producto:</label>
                    <input type="text" id="input-p-id" class="form-input" required placeholder="Ej: PROD_GISICO_2024_01">
                </div>
                <div class="form-group">
                    <label class="form-label">Título de la Publicación u Obra:</label>
                    <input type="text" id="input-p-titulo" class="form-input" required placeholder="Ej: Algoritmos Avanzados en Multilistas 3D">
                </div>
                <div class="form-group">
                    <label class="form-label">Tipología Oficial Modelo MinCiencias:</label>
                    <select id="input-p-tipo" class="form-select">
                        <option value="Articulo" selected>Artículo en Revista Indexada (GNC)</option>
                        <option value="Software">Desarrollo de Software / Sistema (DTI)</option>
                        <option value="Libro">Libro Resultado de Investigación (GNC)</option>
                        <option value="Capitulo">Capítulo de Libro Resultado de Inv. (GNC)</option>
                        <option value="Patente">Patente de Invención o Modelo (DTI)</option>
                        <option value="Tesis">Tesis Doctoral o de Posgrado (FRH)</option>
                        <option value="Trabajo de Grado">Trabajo de Grado de Pregrado (FRH)</option>
                        <option value="Evento">Ponencia en Evento Científico (DPC)</option>
                        <option value="Contenido">Apropiación Social del Conocimiento (ASC)</option>
                        <option value="Prototipo">Prototipo o Planta Piloto (DTI)</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">Año de Publicación:</label>
                    <input type="number" id="input-p-anio" class="form-input" required min="1990" max="2026" value="2024">
                </div>
                <div class="form-group">
                    <label class="form-label">Grupo Receptor (Eje X):</label>
                    <select id="input-p-grupo" class="form-select" required onchange="actualizarSelectInvestigadoresModalProd()"></select>
                </div>
                <div class="form-group">
                    <label class="form-label">Investigador Autor (Eje Y):</label>
                    <select id="input-p-investigador" class="form-select" required></select>
                </div>
                <div class="form-group" style="flex-direction:row; align-items:center; gap:0.6rem; margin-top:0.5rem;">
                    <input type="checkbox" id="input-p-validado" checked style="width:18px; height:18px; accent-color:var(--upc-green-light);">
                    <label for="input-p-validado" class="form-label" style="cursor:pointer; margin:0;">Validado por MinCiencias con Aval Institucional</label>
                </div>
                <div class="modal-footer">
                    <button type="button" onclick="cerrarModales()" class="btn-modal-cancel">Cancelar</button>
                    <button type="submit" class="btn-modal-save">Guardar Producto</button>
                </div>
            </form>
        </div>
    </div>

    <!-- 4. MODAL HISTORIAL PILA UNDO (LIFO) -->
    <div id="modal-pila-undo" class="modal-overlay" style="display:none;">
        <div class="modal-box modal-box-lg">
            <div class="modal-header">
                <h3>Pila de Deshacer (Historial LIFO en Memoria)</h3>
                <button onclick="cerrarModales()" class="modal-close-btn">&times;</button>
            </div>
            <p style="font-size:0.8rem; color:var(--text-muted); margin-bottom:1rem;">
                Muestra las operaciones atómicas apiladas en orden <b>LIFO</b> (Last-In, First-Out).
                Presione <b>Deshacer Tope</b> para revertir la acción más reciente en O(1).
            </p>
            <div class="data-table-container" style="max-height:360px;">
                <table class="peai-table" id="tabla-pila-undo">
                    <thead>
                        <tr>
                            <th>Posición</th>
                            <th>Operación</th>
                            <th>Entidad Afectada</th>
                            <th>Identificador</th>
                            <th>Descripción / Detalle</th>
                            <th>Hora</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
            </div>
            <div class="modal-footer">
                <button type="button" onclick="deshacerUltimaAccion()" class="btn-action-sm btn-action-toggle" style="padding:0.5rem 1rem; font-weight:700;">Deshacer Tope de Pila</button>
                <button type="button" onclick="cerrarModales()" class="btn-modal-cancel">Cerrar</button>
            </div>
        </div>
    </div>

    <!-- 5. MODAL EXPORTAR / SINCRONIZAR -->
    <div id="modal-exportar" class="modal-overlay" style="display:none;">
        <div class="modal-box modal-box-lg">
            <div class="modal-header">
                <h3>Sincronización y Exportación a SQLite / C++</h3>
                <button onclick="cerrarModales()" class="modal-close-btn">&times;</button>
            </div>
            <p style="font-size:0.82rem; color:var(--text-muted); margin-bottom:0.8rem;">
                Todas las modificaciones realizadas en la interfaz gráfica pueden exportarse para sincronizar la Multilista en RAM de C++ y persistir en <code>data/pea_investigacion.db</code>:
            </p>
            <div class="form-group">
                <label class="form-label">Script SQL Generado para SQLite:</label>
                <textarea id="sql-export-area" readonly style="background:#090d16; border:1px solid #1e293b; color:#10b981; font-family:monospace; font-size:0.75rem; padding:0.6rem; border-radius:6px; height:120px; resize:none;"></textarea>
            </div>
            <div class="form-group">
                <label class="form-label">Estructura JSON de Cambios (data/cambios_gui.json):</label>
                <textarea id="json-export-area" readonly style="background:#090d16; border:1px solid #1e293b; color:#38bdf8; font-family:monospace; font-size:0.75rem; padding:0.6rem; border-radius:6px; height:120px; resize:none;"></textarea>
            </div>
            <div class="modal-footer">
                <button type="button" onclick="copiarSQLPortapapeles()" class="btn-action-sm btn-action-edit" style="padding:0.5rem 1rem; font-weight:700;">Copiar SQL</button>
                <button type="button" onclick="descargarCambiosJSON()" class="btn-modal-save">Descargar data/cambios_gui.json</button>
                <button type="button" onclick="cerrarModales()" class="btn-modal-cancel">Cerrar</button>
            </div>
        </div>
    </div>

    <!-- TOAST NOTIFICACIÓN FLOTANTE -->
    <div id="toast-notification">
        <span id="toast-icon">•</span>
        <span id="toast-text">Operación completada</span>
    </div>

    <!-- SERIALIZACIÓN DE DATOS DESDE C++ -->
    <script>
        const DATOS_HIPERCUBO = )HTML";

        out << datosJSON;

        out << R"HTML(;

        // ESTADO GLOBAL
        let gruposData = DATOS_HIPERCUBO.grupos || [];
        let grupoSeleccionado = null;
        let categoriaFiltro = "";
        let textoFiltro = "";
        let ventanaAnios = 0; // 0 = Todos, 2 = Últimos 2, 5 = Últimos 5

        // RESOLVER TIPOLOGÍA MINCIENCIAS 2024
        function clasificar2024(tipo, cat, titulo) {
            const t = (tipo || "").toLowerCase();
            const tit = (titulo || "").toLowerCase();
            const c = (cat || "A1").toUpperCase();

            if (t.includes("articulo") || t.includes("artículo")) {
                if (c.includes("A1")) return { fam: "GNC", cod: "ART_A1", pts: 100 };
                if (c.includes("A2") || c === "A") return { fam: "GNC", cod: "ART_A2", pts: 80 };
                if (c.includes("B")) return { fam: "GNC", cod: "ART_B", pts: 60 };
                return { fam: "GNC", cod: "ART_C", pts: 40 };
            }
            if (t.includes("software") || t.includes("sistema") || t.includes("algoritmo")) {
                return { fam: "DTI", cod: "SOFT_REG", pts: 90 };
            }
            if (t.includes("libro")) {
                return { fam: "GNC", cod: "LIB_A", pts: 100 };
            }
            if (t.includes("capitulo") || t.includes("capítulo")) {
                return { fam: "GNC", cod: "CAP_LIB_A", pts: 50 };
            }
            if (t.includes("tesis") || t.includes("grado") || t.includes("tutor")) {
                if (tit.includes("doctor")) return { fam: "FRH", cod: "TES_DOC", pts: 100 };
                if (tit.includes("maestr") || tit.includes("mag")) return { fam: "FRH", cod: "TGM", pts: 70 };
                if (tit.includes("ondas") || tit.includes("apo")) return { fam: "FRH", cod: "APO", pts: 30 };
                return { fam: "FRH", cod: "TGP", pts: 40 };
            }
            if (t.includes("patente")) {
                return { fam: "GNC", cod: "PAT_INV", pts: 100 };
            }
            if (t.includes("evento") || t.includes("ponencia") || t.includes("conferencia")) {
                return { fam: "DPC", cod: "EVT_INT", pts: 60 };
            }
            if (t.includes("apropiacion") || t.includes("apropiación") || t.includes("social")) {
                return { fam: "ASC", cod: "PROC_ASC", pts: 80 };
            }
            return { fam: "GNC", cod: "ART_B", pts: 60 };
        }

        // CAMBIO DE VISTAS PRINCIPALES
        function cambiarVistaPrincipal(vista) {
            document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
            document.querySelectorAll(".view-panel").forEach(p => p.classList.remove("active"));

            if (vista === "portal") {
                document.querySelectorAll(".tab-btn")[0].classList.add("active");
                document.getElementById("view-portal").classList.add("active");
            } else if (vista === "dashboard") {
                document.querySelectorAll(".tab-btn")[1].classList.add("active");
                document.getElementById("view-dashboard").classList.add("active");
                renderizarDashboard();
            } else if (vista === "red") {
                document.querySelectorAll(".tab-btn")[2].classList.add("active");
                document.getElementById("view-red").classList.add("active");
                poblarSelectGruposRed();
                construirYRenderizarRed();
            } else if (vista === "tablas") {
                document.querySelectorAll(".tab-btn")[3].classList.add("active");
                document.getElementById("view-tablas").classList.add("active");
                renderizarTablasEntidad();
            } else if (vista === "crud") {
                document.querySelectorAll(".tab-btn")[4].classList.add("active");
                document.getElementById("view-crud").classList.add("active");
                renderizarCRUDTab();
            }
        }

        // CAMBIO DE SUB-TABS DEL PERFIL
        // CAMBIO DE SUB-TABS DEL PERFIL
        function cambiarSubTab(subtab) {
            document.querySelectorAll(".profile-nav .p-tab-btn").forEach(b => b.classList.remove("active"));
            document.querySelectorAll(".profile-section").forEach(s => s.classList.remove("active"));

            const subMap = {
                "general": { btn: 0, sec: "subtab-general" },
                "integrantes": { btn: 1, sec: "subtab-integrantes" },
                "productos": { btn: 2, sec: "subtab-productos" },
                "modelo2024": { btn: 3, sec: "subtab-modelo2024" }
            };
            const item = subMap[subtab] || subMap["general"];
            document.querySelectorAll(".profile-nav .p-tab-btn")[item.btn].classList.add("active");
            document.getElementById(item.sec).classList.add("active");
        }

        // INICIALIZACIÓN
        function inicializarPortal() {
            calcularKPIsGlobales();
            renderizarListaGrupos();

            // Seleccionar GISICO o el primer grupo disponible
            let inicial = gruposData.find(g => g.codigo === "COL0002099") || gruposData[0];
            if (inicial) {
                seleccionarGrupo(inicial.codigo);
            }
        }

        // CALCULO DE KPIS GLOBALES
        function calcularKPIsGlobales() {
            let totalG = gruposData.length;
            let totalI = 0;
            let totalP = 0;
            let totalIPP = 0;

            gruposData.forEach(g => {
                totalI += (g.investigadores || []).length;
                (g.productos || []).forEach(p => {
                    totalP++;
                    if (p.validado) {
                        const m = clasificar2024(p.tipo, p.categoria, p.titulo);
                        totalIPP += m.pts;
                    }
                });
            });

            document.getElementById("kpi-grupos").textContent = totalG.toLocaleString();
            document.getElementById("kpi-investigadores").textContent = totalI.toLocaleString();
            document.getElementById("kpi-productos").textContent = totalP.toLocaleString();
            document.getElementById("kpi-ipp").textContent = totalIPP.toLocaleString() + " pts";
        }

        // RENDERIZAR LISTA DE GRUPOS EN SIDEBAR
        function renderizarListaGrupos() {
            const cont = document.getElementById("groups-list-container");
            cont.innerHTML = "";

            const filtrados = gruposData.filter(g => {
                const matchCat = !categoriaFiltro || g.clasificacion === categoriaFiltro;
                const matchTxt = !textoFiltro || 
                                 g.nombre.toLowerCase().includes(textoFiltro.toLowerCase()) || 
                                 g.codigo.toLowerCase().includes(textoFiltro.toLowerCase()) ||
                                 g.lider.toLowerCase().includes(textoFiltro.toLowerCase());
                return matchCat && matchTxt;
            });

            if (filtrados.length === 0) {
                cont.innerHTML = `<div style="padding:1.5rem; text-align:center; color:var(--text-muted); font-size:0.8rem;">No se encontraron grupos con esos criterios.</div>`;
                return;
            }

            filtrados.forEach(g => {
                const isSel = grupoSeleccionado && grupoSeleccionado.codigo === g.codigo;
                const card = document.createElement("div");
                card.className = `group-card-item ${isSel ? "selected" : ""}`;
                card.onclick = () => seleccionarGrupo(g.codigo);

                const numInv = (g.investigadores || []).length;
                const numProd = (g.productos || []).length;
                const catClass = `cat-${g.clasificacion || "C"}`;

                card.innerHTML = `
                    <div class="g-item-header">
                        <span class="g-item-code">${g.codigo}</span>
                        <span class="badge-cat ${catClass}">Cat. ${g.clasificacion || "Rec."}</span>
                    </div>
                    <div class="g-item-name">${g.nombre}</div>
                    <div class="g-item-footer">
                        <span>${(g.lider || "Investigador UPC").substring(0, 22)}</span>
                        <span>${numInv} inv. &bull; ${numProd} prod.</span>
                    </div>
                `;
                cont.appendChild(card);
            });
        }

        // FILTROS SIDEBAR
        function filtrarListaGrupos() {
            textoFiltro = document.getElementById("search-grupos").value.trim();
            renderizarListaGrupos();
        }

        function filtrarCategoriaGrupo(cat) {
            categoriaFiltro = cat;
            document.querySelectorAll(".filter-tags .tag-btn").forEach(b => {
                b.classList.toggle("active", b.textContent.includes(cat) || (!cat && b.textContent === "Todos"));
            });
            renderizarListaGrupos();
        }

        // SELECCIONAR GRUPO
        function seleccionarGrupo(codigo) {
            const g = gruposData.find(item => item.codigo === codigo);
            if (!g) return;
            grupoSeleccionado = g;

            // Actualizar tarjetas en sidebar
            renderizarListaGrupos();

            // HERO
            document.getElementById("g-avatar").textContent = (g.nombre.charAt(0) || "G").toUpperCase();
            document.getElementById("g-nombre").textContent = g.nombre;
            document.getElementById("g-codigo").textContent = g.codigo;
            
            const badgeCat = document.getElementById("g-badge-cat");
            badgeCat.textContent = `Cat. ${g.clasificacion || "Reconocido"}`;
            badgeCat.className = `badge-cat cat-${g.clasificacion || "C"}`;

            const badgeStatHero = document.getElementById("g-badge-status-hero");
            const btnToggleHero = document.getElementById("btn-toggle-hero");
            const esActivo = g.activo !== false;
            if (badgeStatHero) {
                badgeStatHero.textContent = esActivo ? "Activo" : "Inactivo";
                badgeStatHero.className = "badge-status " + (esActivo ? "badge-active" : "badge-inactive");
            }
            if (btnToggleHero) {
                btnToggleHero.textContent = esActivo ? "Desactivar" : "Activar";
                btnToggleHero.style.color = esActivo ? "#f87171" : "#10b981";
            }

            const btnPdf = document.getElementById("btn-descargar-pdf");
            btnPdf.href = `../reportes/Informe_GrupLAC_${g.codigo}.pdf`;

            // FICHA GENERAL
            document.getElementById("g-lider").textContent = g.lider || "Investigador Principal";
            document.getElementById("g-anio").textContent = g.anio_creacion || g.anio || "2010";
            document.getElementById("g-area").textContent = g.area || "Ciencias de la Ingeniería y Tecnologías";

            const nInv = (g.investigadores || []).length;
            const nProd = (g.productos || []).length;
            const valProd = (g.productos || []).filter(p => p.validado).length;
            document.getElementById("g-resumen-conteo").textContent = `${nInv} integrantes | ${nProd} productos (${valProd} avalados)`;

            // LABELS TABS
            document.getElementById("tab-lbl-inv").textContent = `Integrantes (${nInv})`;
            document.getElementById("tab-lbl-prod").textContent = `Productos (${nProd})`;

            // TABLA INTEGRANTES
            const tbodyInv = document.querySelector("#tabla-perfil-inv tbody");
            tbodyInv.innerHTML = "";
            (g.investigadores || []).forEach(inv => {
                const tr = document.createElement("tr");
                const invActivo = inv.activo !== false;
                let badgePar = inv.par_evaluador === "Si" ? " <span class='badge-cat' style='background:rgba(16,185,129,0.16); color:#34d399; border-color:rgba(16,185,129,0.35); margin-left:6px;'>Par Evaluador</span>" : "";
                let links = "";
                if (inv.documento && /^\d{7,10}$/.test(String(inv.documento).trim())) {
                    const codRh = String(inv.documento).trim().padStart(10, "0");
                    links += `<a href="https://scienti.minciencias.gov.co/cvlac/visualizador/generarCurriculoCv.do?cod_rh=${codRh}" target="_blank" class="link-pill" title="Abrir CvLAC oficial">CvLAC</a>`;
                }
                if (inv.scholar_url) links += `<a href="${inv.scholar_url}" target="_blank" class="link-pill link-pill-scholar" title="Abrir perfil de Google Scholar">Scholar</a>`;
                if (inv.orcid) links += `<a href="${inv.orcid}" target="_blank" class="link-pill link-pill-orcid" title="Abrir identificador ORCID">ORCID</a>`;
                const linksCell = links ? `<div class="link-pills-wrap">${links}</div>` : `<span style="color:#475569; font-size:0.74rem;">—</span>`;

                tr.innerHTML = `
                    <td><code style="color:#38bdf8;">${inv.documento}</code></td>
                    <td><b>${inv.nombre}</b>${badgePar}</td>
                    <td>${linksCell}</td>
                    <td><span class="badge-cat">${inv.categoria || "Junior"}</span></td>
                    <td>${inv.formacion || "Maestría / Doctorado CTeI"}</td>
                    <td><span class="badge-status ${invActivo ? 'badge-active' : 'badge-inactive'}">${invActivo ? '● Activo' : '○ Inactivo'}</span></td>
                    <td style="text-align:center;">
                        <div class="table-actions-cell">
                            <button onclick="abrirModalInvestigador('${g.codigo}', '${inv.documento}')" class="btn-action-sm btn-action-edit">Editar</button>
                            <button onclick="toggleEstadoInvestigador('${g.codigo}', '${inv.documento}')" class="btn-action-sm btn-action-toggle">${invActivo ? 'Desactivar' : 'Activar'}</button>
                        </div>
                    </td>
                `;
                tbodyInv.appendChild(tr);
            });

            // TABLA PRODUCTOS
            const tbodyProd = document.querySelector("#tabla-perfil-prod tbody");
            tbodyProd.innerHTML = "";
            let cntFam = { "GNC": 0, "DTI": 0, "ASC": 0, "DPC": 0, "FRH": 0 };
            let ptsFam = { "GNC": 0, "DTI": 0, "ASC": 0, "DPC": 0, "FRH": 0 };
            let totalIPP = 0;

            (g.productos || []).forEach(p => {
                const clas = clasificar2024(p.tipo, p.categoria, p.titulo);
                cntFam[clas.fam] = (cntFam[clas.fam] || 0) + 1;
                const pts = p.validado ? clas.pts : 0;
                ptsFam[clas.fam] = (ptsFam[clas.fam] || 0) + pts;
                totalIPP += pts;

                const tr = document.createElement("tr");
                const prodActivo = p.activo !== false;
                tr.innerHTML = `
                    <td><b>${p.anio}</b></td>
                    <td><span class="badge-cat" style="background:rgba(2,132,199,0.18); color:#38bdf8; border-color:rgba(56,189,248,0.35);">${clas.fam}</span></td>
                    <td><code>${clas.cod}</code></td>
                    <td style="max-width:340px;"><b>${p.titulo}</b></td>
                    <td>${p.tipo}</td>
                    <td>${p.validado ? "<span style='color:#10b981; font-weight:700; white-space:nowrap;'>Avalado</span>" : "<span style='color:#f59e0b; white-space:nowrap;'>En Revisión</span>"}</td>
                    <td style="color:var(--upc-green-light); font-weight:700; white-space:nowrap;">${pts} pts</td>
                    <td style="text-align:center;">
                        <div class="table-actions-cell">
                            <button onclick="abrirModalProducto('${g.codigo}', '${p.id}')" class="btn-action-sm btn-action-edit">Editar</button>
                            <button onclick="toggleEstadoProducto('${g.codigo}', '${p.id}')" class="btn-action-sm btn-action-toggle">${prodActivo ? 'Desactivar' : 'Activar'}</button>
                        </div>
                    </td>
                `;
                tbodyProd.appendChild(tr);
            });

            // BALANCE 2024
            document.getElementById("g-total-ipp").textContent = `${totalIPP.toLocaleString()} puntos`;
            document.getElementById("cnt-gnc").textContent = cntFam["GNC"];
            document.getElementById("pts-gnc").textContent = `${ptsFam["GNC"]} pts`;
            document.getElementById("cnt-dti").textContent = cntFam["DTI"];
            document.getElementById("pts-dti").textContent = `${ptsFam["DTI"]} pts`;
            document.getElementById("cnt-asc").textContent = cntFam["ASC"];
            document.getElementById("pts-asc").textContent = `${ptsFam["ASC"]} pts`;
            document.getElementById("cnt-dpc").textContent = cntFam["DPC"];
            document.getElementById("pts-dpc").textContent = `${ptsFam["DPC"]} pts`;
            document.getElementById("cnt-frh").textContent = cntFam["FRH"];
            document.getElementById("pts-frh").textContent = `${ptsFam["FRH"]} pts`;
        }

        // REGLA DE VENTANA DIFERENCIADA MINCIENCIAS 2024 (5 AÑOS GENERAL / 10 AÑOS LIBROS, CAPÍTULOS Y PATENTES)
        function cumpleVentanaProducto(p, win) {
            if (!win || win === 0) return true;
            if (win === 2024) {
                const t = (p.tipo || "").toLowerCase();
                const esVentana10 = t.includes("libro") || t.includes("capitulo") || t.includes("capítulo") || t.includes("patente") || t.includes("variedad");
                const cota = esVentana10 ? (2026 - 10) : (2026 - 5);
                return p.anio >= cota && p.anio <= 2026;
            }
            const anioLimite = 2026 - win;
            return p.anio >= anioLimite;
        }

        // RENDERIZAR DASHBOARD ANALÍTICO (12.B)
        function cambiarVentanaObservacion(win) {
            ventanaAnios = win;
            document.getElementById("btn-win-0")?.classList.toggle("active", win === 0);
            document.getElementById("btn-win-2024")?.classList.toggle("active", win === 2024);
            document.getElementById("btn-win-5")?.classList.toggle("active", win === 5);
            document.getElementById("btn-win-2")?.classList.toggle("active", win === 2);
            const descEl = document.getElementById("lbl-ventana-desc");
            if (descEl) {
                if (win === 0) descEl.textContent = "Mostrando serie histórica completa (Todos los años)";
                else if (win === 2024) descEl.textContent = "Corte Oficial Modelo MinCiencias 2024: 10 años (2016-2026) para Libros, Capítulos y Patentes | 5 años (2021-2026) para las demás tipologías";
                else descEl.textContent = `Filtro simétrico activo: últimos ${win} años (${2026 - win} - 2026)`;
            }
            renderizarDashboard();
        }

        function renderizarDashboard() {
            // 1. Cronología por año
            let aniosCount = {};
            // 2. Familias 2024
            let famCount = { "GNC": 0, "DTI": 0, "ASC": 0, "DPC": 0, "FRH": 0 };
            // 3. Avales
            let avalCount = { "Avalados": 0, "En Revisión": 0 };

            gruposData.forEach(g => {
                if (g.activo === false) return;
                (g.productos || []).forEach(p => {
                    if (p.activo === false) return;
                    if (cumpleVentanaProducto(p, ventanaAnios)) {
                        aniosCount[p.anio] = (aniosCount[p.anio] || 0) + 1;
                        const c = clasificar2024(p.tipo, p.categoria, p.titulo);
                        famCount[c.fam] = (famCount[c.fam] || 0) + 1;
                        if (p.validado) avalCount["Avalados"]++;
                        else avalCount["En Revisión"]++;
                    }
                });
            });

            // Renderizar barras de años
            const aniosCont = document.getElementById("chart-anios-container");
            aniosCont.innerHTML = "";
            const keysAnios = Object.keys(aniosCount).map(Number).sort((a,b) => b - a);
            const maxAnios = Math.max(...Object.values(aniosCount), 1);

            keysAnios.forEach(yr => {
                const val = aniosCount[yr];
                const pct = Math.round((val / maxAnios) * 100);
                aniosCont.innerHTML += `
                    <div class="bar-chart-row">
                        <span class="bar-label">${yr}</span>
                        <div class="bar-track">
                            <div class="bar-fill" style="width:${pct}%; background:#38bdf8;">${val}</div>
                        </div>
                        <span class="bar-count">${val}</span>
                    </div>
                `;
            });

            // Renderizar categorías de grupo
            const catCont = document.getElementById("chart-cat-container");
            catCont.innerHTML = "";
            let catGroupCount = {};
            gruposData.forEach(g => {
                const c = g.clasificacion || "Reconocido";
                catGroupCount[c] = (catGroupCount[c] || 0) + 1;
            });
            const maxCat = Math.max(...Object.values(catGroupCount), 1);
            ["A1", "A", "B", "C", "Reconocido"].forEach(cat => {
                const val = catGroupCount[cat] || 0;
                const pct = Math.round((val / maxCat) * 100);
                catCont.innerHTML += `
                    <div class="bar-chart-row">
                        <span class="bar-label">Categoría ${cat}</span>
                        <div class="bar-track">
                            <div class="bar-fill" style="width:${pct}%; background:#10b981;">${val}</div>
                        </div>
                        <span class="bar-count">${val}</span>
                    </div>
                `;
            });

            // Renderizar familias 2024
            const famCont = document.getElementById("chart-familias-container");
            famCont.innerHTML = "";
            const maxFam = Math.max(...Object.values(famCount), 1);
            const coloresFam = { "GNC": "#38bdf8", "DTI": "#10b981", "ASC": "#f59e0b", "DPC": "#c084fc", "FRH": "#f43f5e" };
            Object.keys(famCount).forEach(f => {
                const val = famCount[f];
                const pct = Math.round((val / maxFam) * 100);
                famCont.innerHTML += `
                    <div class="bar-chart-row">
                        <span class="bar-label">${f} (Modelo 2024)</span>
                        <div class="bar-track">
                            <div class="bar-fill" style="width:${pct}%; background:${coloresFam[f]};">${val}</div>
                        </div>
                        <span class="bar-count">${val}</span>
                    </div>
                `;
            });

            // Renderizar avales
            const avalCont = document.getElementById("chart-aval-container");
            avalCont.innerHTML = "";
            const maxAval = Math.max(...Object.values(avalCount), 1);
            Object.keys(avalCount).forEach(av => {
                const val = avalCount[av];
                const pct = Math.round((val / maxAval) * 100);
                const col = av === "Avalados" ? "#10b981" : "#f59e0b";
                avalCont.innerHTML += `
                    <div class="bar-chart-row">
                        <span class="bar-label">${av}</span>
                        <div class="bar-track">
                            <div class="bar-fill" style="width:${pct}%; background:${col};">${val}</div>
                        </div>
                        <span class="bar-count">${val}</span>
                    </div>
                `;
            });
        }

        // RENDERIZAR TABLAS ENTIDAD (12.C)
        function renderizarTablasEntidad() {
            // Tabla Grupos
            const tbodyG = document.querySelector("#tabla-entidad-grupos tbody");
            tbodyG.innerHTML = "";
            document.getElementById("lbl-total-grupos-tab").textContent = `${gruposData.length} grupos registrados`;

            gruposData.forEach(g => {
                const numInv = (g.investigadores || []).length;
                const numProd = (g.productos || []).length;
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td><code style="color:#38bdf8;">${g.codigo}</code></td>
                    <td><b>${g.nombre}</b></td>
                    <td><span class="badge-cat">Cat. ${g.clasificacion || "Rec."}</span></td>
                    <td>${g.lider}</td>
                    <td>${numInv}</td>
                    <td><b>${numProd}</b></td>
                    <td><a href="../reportes/Informe_GrupLAC_${g.codigo}.pdf" target="_blank" style="background:#006837; color:#fff; padding:3px 7px; border-radius:4px; font-size:0.75rem; text-decoration:none; font-weight:700;">Descargar PDF</a></td>
                `;
                tbodyG.appendChild(tr);
            });

            // Tabla Investigadores (Top 50)
            const tbodyI = document.querySelector("#tabla-entidad-inv tbody");
            tbodyI.innerHTML = "";
            let invList = [];
            gruposData.forEach(g => {
                (g.investigadores || []).forEach(inv => {
                    // Contar obras asociadas
                    let obras = (g.productos || []).filter(p => p.id_investigador === inv.documento).length;
                    invList.push({
                        doc: inv.documento,
                        nombre: inv.nombre,
                        categoria: inv.categoria || "Junior",
                        grupo: g.codigo,
                        obras: obras
                    });
                });
            });
            invList.sort((a,b) => b.obras - a.obras);

            invList.slice(0, 50).forEach(inv => {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td><code>${inv.doc}</code></td>
                    <td><b>${inv.nombre}</b></td>
                    <td><span class="badge-cat">${inv.categoria}</span></td>
                    <td><code>${inv.grupo}</code></td>
                    <td><b>${inv.obras} obras</b></td>
                `;
                tbodyI.appendChild(tr);
            });
        }

        // =================================================================
        // MOTOR DE GESTIÓN CRUD, PILA UNDO (LIFO) Y SINCRONIZACIÓN
        // =================================================================
        let pilaUndoGUI = [];
        let operacionesAuditadas = [];

        function mostrarToast(mensaje, icono = "•") {
            const toast = document.getElementById("toast-notification");
            document.getElementById("toast-icon").textContent = icono;
            document.getElementById("toast-text").textContent = mensaje;
            toast.style.display = "flex";
            if (window._toastTimeout) clearTimeout(window._toastTimeout);
            window._toastTimeout = setTimeout(() => {
                toast.style.display = "none";
            }, 3500);
        }

        function cerrarModales() {
            document.querySelectorAll(".modal-overlay").forEach(m => m.style.display = "none");
        }

        function actualizarContadorUndo() {
            const countEl = document.getElementById("undo-count");
            if (countEl) countEl.textContent = pilaUndoGUI.length;
            const btnUndo = document.getElementById("btn-undo-header");
            if (btnUndo) {
                btnUndo.style.opacity = pilaUndoGUI.length === 0 ? "0.6" : "1";
            }
            renderizarPopoverUndo();
        }

        function togglePopoverPilaUndo(e) {
            if (e) e.stopPropagation();
            const pop = document.getElementById("popover-historial-undo");
            if (!pop) return;
            const abierto = pop.style.display === "block";
            pop.style.display = abierto ? "none" : "block";
            if (!abierto) renderizarPopoverUndo();
        }

        function cerrarPopoverUndo() {
            const pop = document.getElementById("popover-historial-undo");
            if (pop) pop.style.display = "none";
        }

        function renderizarPopoverUndo() {
            const cont = document.getElementById("popover-undo-list");
            if (!cont) return;
            if (pilaUndoGUI.length === 0) {
                cont.innerHTML = `<div style="text-align:center; color:#64748b; font-size:0.75rem; padding:1rem 0.5rem;">Pila LIFO vacía.<br>Cualquier alta, edición o cambio de estado se apilará aquí en tiempo real.</div>`;
                return;
            }
            let html = "";
            for (let i = pilaUndoGUI.length - 1; i >= 0; i--) {
                const acc = pilaUndoGUI[i];
                const esTope = (i === pilaUndoGUI.length - 1);
                html += `
                    <div style="background:${esTope ? 'rgba(16,185,129,0.12)' : '#090d16'}; border:1px solid ${esTope ? '#10b981' : '#1e293b'}; border-radius:7px; padding:0.45rem 0.6rem; display:flex; justify-content:space-between; align-items:center; gap:8px;">
                        <div style="min-width:0; flex:1;">
                            <div style="font-size:0.72rem; font-weight:800; color:${esTope ? '#10b981' : '#94a3b8'};">
                                ${esTope ? '[TOPE DE PILA]' : `[#${i + 1}]`} &bull; ${acc.tipo} (${acc.entidad})
                            </div>
                            <div style="font-size:0.74rem; color:#e2e8f0; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
                                ${acc.desc}
                            </div>
                        </div>
                        <code style="font-size:0.68rem; color:#38bdf8;">${acc.id}</code>
                    </div>
                `;
            }
            cont.innerHTML = html;
        }

        // Cerrar popover al hacer clic fuera y activar atajo global Ctrl+Z
        window.addEventListener("click", e => {
            const pop = document.getElementById("popover-historial-undo");
            const btn = document.getElementById("btn-pila-popover");
            if (pop && pop.style.display === "block") {
                if (!pop.contains(e.target) && (!btn || !btn.contains(e.target))) {
                    pop.style.display = "none";
                }
            }
        });

        window.addEventListener("keydown", e => {
            const tag = (document.activeElement?.tagName || "").toUpperCase();
            if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") return;
            if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "z") {
                e.preventDefault();
                deshacerUltimaAccion();
            }
        });

        function apilarAccion(accion) {
            accion.hora = new Date().toLocaleTimeString();
            pilaUndoGUI.push(accion);
            operacionesAuditadas.push({
                tipo: accion.tipo,
                entidad: accion.entidad,
                id: accion.id,
                desc: accion.desc,
                timestamp: accion.hora
            });
            actualizarContadorUndo();
            guardarEnLocalStorage();
        }

        function deshacerUltimaAccion() {
            if (pilaUndoGUI.length === 0) {
                mostrarToast("La Pila Undo está vacía. No hay acciones para revertir.", "!");
                return;
            }
            const acc = pilaUndoGUI.pop();
            if (acc && typeof acc.revertir === "function") {
                acc.revertir();
                actualizarContadorUndo();
                refrescarTodo();
                guardarEnLocalStorage();
                mostrarToast(`Deshecho (LIFO): ${acc.desc}`, "⤺");
            }
        }

        function abrirModalPilaUndo() {
            const tbody = document.querySelector("#tabla-pila-undo tbody");
            tbody.innerHTML = "";
            if (pilaUndoGUI.length === 0) {
                tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; color:var(--text-muted); padding:1.5rem;">La pila LIFO no contiene operaciones pendientes.</td></tr>`;
            } else {
                for (let i = pilaUndoGUI.length - 1; i >= 0; i--) {
                    const acc = pilaUndoGUI[i];
                    const tr = document.createElement("tr");
                    const esTope = (i === pilaUndoGUI.length - 1);
                    tr.innerHTML = `
                        <td><b>${esTope ? "[TOPE]" : `[#${i + 1}]`}</b></td>
                        <td><span class="badge-status ${acc.tipo.includes('ELIM') || acc.tipo.includes('TOGGLE') ? 'badge-inactive' : 'badge-active'}">${acc.tipo}</span></td>
                        <td>${acc.entidad}</td>
                        <td><code>${acc.id}</code></td>
                        <td>${acc.desc}</td>
                        <td>${acc.hora || new Date().toLocaleTimeString()}</td>
                    `;
                    tbody.appendChild(tr);
                }
            }
            document.getElementById("modal-pila-undo").style.display = "flex";
        }

        function refrescarTodo() {
            calcularKPIsGlobales();
            renderizarListaGrupos();
            if (grupoSeleccionado) {
                seleccionarGrupo(grupoSeleccionado.codigo);
            }
            const activa = document.querySelector(".view-panel.active");
            if (activa) {
                if (activa.id === "view-dashboard") renderizarDashboard();
                if (activa.id === "view-red") construirYRenderizarRed();
                if (activa.id === "view-tablas") renderizarTablasEntidad();
                if (activa.id === "view-crud") renderizarCRUDTab();
            }
            actualizarContadorUndo();
            guardarEnLocalStorage();
        }

        // -------------------------------------------------------------
        // CRUD: GRUPOS DE INVESTIGACIÓN
        // -------------------------------------------------------------
        let grupoEnEdicion = null;

        function abrirModalGrupo(codigo = "") {
            grupoEnEdicion = codigo ? gruposData.find(g => g.codigo === codigo) : null;
            const titleEl = document.getElementById("modal-g-title");
            const inCod = document.getElementById("input-g-codigo");
            const inNom = document.getElementById("input-g-nombre");
            const inClas = document.getElementById("input-g-clasif");
            const inArea = document.getElementById("input-g-area");
            const inLider = document.getElementById("input-g-lider");
            const inAnio = document.getElementById("input-g-anio");

            if (grupoEnEdicion) {
                titleEl.textContent = `Editar Grupo: ${grupoEnEdicion.codigo}`;
                inCod.value = grupoEnEdicion.codigo;
                inCod.disabled = true;
                inNom.value = grupoEnEdicion.nombre;
                inClas.value = grupoEnEdicion.clasificacion || "C";
                inArea.value = grupoEnEdicion.area || "Ingeniería y Tecnología";
                inLider.value = grupoEnEdicion.lider || "";
                inAnio.value = grupoEnEdicion.anio_creacion || grupoEnEdicion.anio || 2024;
            } else {
                titleEl.textContent = "Registrar Nuevo Grupo de Investigación";
                inCod.value = `COL${Math.floor(1000000 + Math.random() * 9000000)}`;
                inCod.disabled = false;
                inNom.value = "";
                inClas.value = "C";
                inArea.value = "Ingeniería y Tecnología";
                inLider.value = "";
                inAnio.value = 2024;
            }
            document.getElementById("modal-grupo").style.display = "flex";
        }

        function editarGrupoActual() {
            if (grupoSeleccionado) abrirModalGrupo(grupoSeleccionado.codigo);
        }

        function guardarGrupoForm(e) {
            e.preventDefault();
            const cod = document.getElementById("input-g-codigo").value.trim().toUpperCase();
            const nom = document.getElementById("input-g-nombre").value.trim();
            const clas = document.getElementById("input-g-clasif").value;
            const area = document.getElementById("input-g-area").value.trim();
            const lider = document.getElementById("input-g-lider").value.trim();
            const anio = parseInt(document.getElementById("input-g-anio").value) || 2024;

            if (grupoEnEdicion) {
                const copiaPrev = { ...grupoEnEdicion };
                grupoEnEdicion.nombre = nom;
                grupoEnEdicion.clasificacion = clas;
                grupoEnEdicion.area = area;
                grupoEnEdicion.lider = lider;
                grupoEnEdicion.anio_creacion = anio;
                grupoEnEdicion.anio = anio;

                apilarAccion({
                    tipo: "UPDATE",
                    entidad: "GRUPO",
                    id: cod,
                    desc: `Modificación de grupo ${cod} (${nom})`,
                    revertir: () => {
                        Object.assign(grupoEnEdicion, copiaPrev);
                    }
                });
                mostrarToast(`Grupo [${cod}] actualizado exitosamente.`);
            } else {
                if (gruposData.some(g => g.codigo === cod)) {
                    alert(`El código de grupo ${cod} ya existe en el sistema.`);
                    return;
                }
                const nuevo = {
                    codigo: cod,
                    nombre: nom,
                    clasificacion: clas,
                    area: area,
                    lider: lider,
                    anio_creacion: anio,
                    anio: anio,
                    activo: true,
                    investigadores: [],
                    productos: []
                };
                gruposData.unshift(nuevo);
                apilarAccion({
                    tipo: "INSERT",
                    entidad: "GRUPO",
                    id: cod,
                    desc: `Creación de grupo ${cod} (${nom})`,
                    revertir: () => {
                        gruposData = gruposData.filter(g => g.codigo !== cod);
                    }
                });
                grupoSeleccionado = nuevo;
                mostrarToast(`Grupo [${cod}] registrado en el Hipercubo.`);
            }
            cerrarModales();
            refrescarTodo();
        }

        function toggleEstadoGrupo(cod) {
            const g = gruposData.find(item => item.codigo === cod);
            if (!g) return;
            g.activo = (g.activo === false ? true : false);
            apilarAccion({
                tipo: "TOGGLE_ESTADO",
                entidad: "GRUPO",
                id: cod,
                desc: `Cambio de estado de grupo ${cod} a ${g.activo ? 'Activo' : 'Inactivo'}`,
                revertir: () => {
                    g.activo = !g.activo;
                }
            });
            mostrarToast(`Grupo ${cod}: ahora está ${g.activo ? 'ACTIVO' : 'INACTIVO'}.`, g.activo ? "[OK]" : "[INFO]");
            refrescarTodo();
        }

        function toggleEstadoGrupoActual() {
            if (grupoSeleccionado) toggleEstadoGrupo(grupoSeleccionado.codigo);
        }

        // -------------------------------------------------------------
        // CRUD: INVESTIGADORES
        // -------------------------------------------------------------
        let invEnEdicion = null;
        let grupoInvEdicion = null;

        function actualizarSelectGrupos(selectId, codSel = "") {
            const s = document.getElementById(selectId);
            if (!s) return;
            s.innerHTML = "";
            gruposData.forEach(g => {
                const opt = document.createElement("option");
                opt.value = g.codigo;
                opt.textContent = `${g.codigo} - ${g.nombre.substring(0, 35)}`;
                if (g.codigo === codSel) opt.selected = true;
                s.appendChild(opt);
            });
        }

        function abrirModalInvestigador(codGrupoDef = "", doc = "") {
            const targetCod = codGrupoDef || (grupoSeleccionado ? grupoSeleccionado.codigo : (gruposData[0] ? gruposData[0].codigo : ""));
            actualizarSelectGrupos("input-i-grupo", targetCod);

            invEnEdicion = null;
            grupoInvEdicion = null;
            if (doc) {
                gruposData.forEach(g => {
                    const found = (g.investigadores || []).find(i => i.documento === doc);
                    if (found) { invEnEdicion = found; grupoInvEdicion = g; }
                });
            }

            const titleEl = document.getElementById("modal-i-title");
            const inDoc = document.getElementById("input-i-doc");
            const inNom = document.getElementById("input-i-nombre");
            const inCat = document.getElementById("input-i-cat");
            const inForm = document.getElementById("input-i-formacion");
            const inPar = document.getElementById("input-i-par");
            const inScholar = document.getElementById("input-i-scholar");
            const inOrcid = document.getElementById("input-i-orcid");

            if (invEnEdicion) {
                titleEl.textContent = `Editar Investigador: ${invEnEdicion.documento}`;
                inDoc.value = invEnEdicion.documento;
                inDoc.disabled = true;
                inNom.value = invEnEdicion.nombre;
                inCat.value = invEnEdicion.categoria || "Junior";
                inForm.value = invEnEdicion.formacion || "";
                if (inPar) inPar.value = invEnEdicion.par_evaluador === "Si" ? "Si" : "No";
                if (inScholar) inScholar.value = invEnEdicion.scholar_url || "";
                if (inOrcid) inOrcid.value = invEnEdicion.orcid || "";
                document.getElementById("input-i-grupo").value = grupoInvEdicion.codigo;
            } else {
                titleEl.textContent = "Registrar Nuevo Investigador";
                inDoc.value = "";
                inDoc.disabled = false;
                inNom.value = "";
                inCat.value = "Junior";
                inForm.value = "Ingeniería de Sistemas y Computación";
                if (inPar) inPar.value = "No";
                if (inScholar) inScholar.value = "";
                if (inOrcid) inOrcid.value = "";
            }
            document.getElementById("modal-investigador").style.display = "flex";
        }

        function guardarInvestigadorForm(e) {
            e.preventDefault();
            const doc = document.getElementById("input-i-doc").value.trim();
            const nom = document.getElementById("input-i-nombre").value.trim();
            const cat = document.getElementById("input-i-cat").value;
            const form = document.getElementById("input-i-formacion").value.trim();
            const par = document.getElementById("input-i-par")?.value || "No";
            const scholar = document.getElementById("input-i-scholar")?.value.trim() || "";
            const orcid = document.getElementById("input-i-orcid")?.value.trim() || "";
            const codG = document.getElementById("input-i-grupo").value;

            const gTarget = gruposData.find(g => g.codigo === codG);
            if (!gTarget) return;

            if (invEnEdicion) {
                const copiaPrev = { ...invEnEdicion };
                invEnEdicion.nombre = nom;
                invEnEdicion.categoria = cat;
                invEnEdicion.formacion = form;
                invEnEdicion.par_evaluador = par;
                invEnEdicion.scholar_url = scholar;
                invEnEdicion.orcid = orcid;

                apilarAccion({
                    tipo: "UPDATE",
                    entidad: "INVESTIGADOR",
                    id: doc,
                    desc: `Modificación de investigador ${doc} (${nom})`,
                    revertir: () => {
                        Object.assign(invEnEdicion, copiaPrev);
                    }
                });
                mostrarToast(`Investigador [${doc}] actualizado exitosamente.`);
            } else {
                const nuevo = {
                    documento: doc,
                    nombre: nom,
                    categoria: cat,
                    formacion: form,
                    par_evaluador: par,
                    scholar_url: scholar,
                    orcid: orcid,
                    activo: true
                };
                if (!gTarget.investigadores) gTarget.investigadores = [];
                gTarget.investigadores.unshift(nuevo);

                apilarAccion({
                    tipo: "INSERT",
                    entidad: "INVESTIGADOR",
                    id: doc,
                    desc: `Registro de investigador ${doc} en ${codG}`,
                    revertir: () => {
                        gTarget.investigadores = gTarget.investigadores.filter(i => i.documento !== doc);
                    }
                });
                mostrarToast(`Investigador [${doc}] registrado en grupo ${codG}.`);
            }
            cerrarModales();
            refrescarTodo();
        }

        function toggleEstadoInvestigador(codGrupo, doc) {
            const g = gruposData.find(item => item.codigo === codGrupo);
            if (!g) return;
            const inv = (g.investigadores || []).find(i => i.documento === doc);
            if (!inv) return;
            inv.activo = (inv.activo === false ? true : false);
            apilarAccion({
                tipo: "TOGGLE_ESTADO",
                entidad: "INVESTIGADOR",
                id: doc,
                desc: `Cambio de estado investigador ${doc} a ${inv.activo ? 'Activo' : 'Inactivo'}`,
                revertir: () => {
                    inv.activo = !inv.activo;
                }
            });
            mostrarToast(`Investigador ${doc}: ahora está ${inv.activo ? 'ACTIVO' : 'INACTIVO'}.`, inv.activo ? "[OK]" : "[INFO]");
            refrescarTodo();
        }

        // -------------------------------------------------------------
        // CRUD: PRODUCTOS DE INVESTIGACIÓN
        // -------------------------------------------------------------
        let prodEnEdicion = null;
        let grupoProdEdicion = null;

        function actualizarSelectInvestigadoresModalProd() {
            const codG = document.getElementById("input-p-grupo").value;
            const s = document.getElementById("input-p-investigador");
            s.innerHTML = "";
            const g = gruposData.find(item => item.codigo === codG);
            if (g && g.investigadores) {
                g.investigadores.forEach(inv => {
                    const opt = document.createElement("option");
                    opt.value = inv.documento;
                    opt.textContent = `${inv.nombre} (${inv.documento})`;
                    s.appendChild(opt);
                });
            }
            if (s.options.length === 0) {
                const opt = document.createElement("option");
                opt.value = "0000494917";
                opt.textContent = "Líder Asignado (0000494917)";
                s.appendChild(opt);
            }
        }

        function abrirModalProducto(codGrupoDef = "", idProd = "") {
            const targetCod = codGrupoDef || (grupoSeleccionado ? grupoSeleccionado.codigo : (gruposData[0] ? gruposData[0].codigo : ""));
            actualizarSelectGrupos("input-p-grupo", targetCod);
            actualizarSelectInvestigadoresModalProd();

            prodEnEdicion = null;
            grupoProdEdicion = null;
            if (idProd) {
                gruposData.forEach(g => {
                    const found = (g.productos || []).find(p => p.id === idProd);
                    if (found) { prodEnEdicion = found; grupoProdEdicion = g; }
                });
            }

            const titleEl = document.getElementById("modal-p-title");
            const inId = document.getElementById("input-p-id");
            const inTit = document.getElementById("input-p-titulo");
            const inTipo = document.getElementById("input-p-tipo");
            const inAnio = document.getElementById("input-p-anio");
            const inVal = document.getElementById("input-p-validado");

            if (prodEnEdicion) {
                titleEl.textContent = `Editar Producto: ${prodEnEdicion.id}`;
                inId.value = prodEnEdicion.id;
                inId.disabled = true;
                inTit.value = prodEnEdicion.titulo;
                inTipo.value = prodEnEdicion.tipo || "Articulo";
                inAnio.value = prodEnEdicion.anio || 2024;
                inVal.checked = (prodEnEdicion.validado !== false);
                document.getElementById("input-p-grupo").value = grupoProdEdicion.codigo;
                actualizarSelectInvestigadoresModalProd();
                document.getElementById("input-p-investigador").value = prodEnEdicion.id_investigador || "";
            } else {
                titleEl.textContent = "Registrar Producto de Investigación";
                inId.value = `PROD_${Math.floor(100000 + Math.random() * 900000)}`;
                inId.disabled = false;
                inTit.value = "";
                inTipo.value = "Articulo";
                inAnio.value = 2024;
                inVal.checked = true;
            }
            document.getElementById("modal-producto").style.display = "flex";
        }

        function guardarProductoForm(e) {
            e.preventDefault();
            const idProd = document.getElementById("input-p-id").value.trim();
            const tit = document.getElementById("input-p-titulo").value.trim();
            const tipo = document.getElementById("input-p-tipo").value;
            const anio = parseInt(document.getElementById("input-p-anio").value) || 2024;
            const codG = document.getElementById("input-p-grupo").value;
            const idInv = document.getElementById("input-p-investigador").value;
            const valid = document.getElementById("input-p-validado").checked;

            const gTarget = gruposData.find(g => g.codigo === codG);
            if (!gTarget) return;

            if (prodEnEdicion) {
                const copiaPrev = { ...prodEnEdicion };
                prodEnEdicion.titulo = tit;
                prodEnEdicion.tipo = tipo;
                prodEnEdicion.anio = anio;
                prodEnEdicion.validado = valid;
                prodEnEdicion.id_investigador = idInv;

                apilarAccion({
                    tipo: "UPDATE",
                    entidad: "PRODUCTO",
                    id: idProd,
                    desc: `Modificación de producto ${idProd} (${tit.substring(0, 30)})`,
                    revertir: () => {
                        Object.assign(prodEnEdicion, copiaPrev);
                    }
                });
                mostrarToast(`Producto [${idProd}] actualizado exitosamente.`);
            } else {
                const nuevo = {
                    id: idProd,
                    tipo: tipo,
                    titulo: tit,
                    anio: anio,
                    categoria: "A1",
                    validado: valid,
                    activo: true,
                    id_investigador: idInv
                };
                if (!gTarget.productos) gTarget.productos = [];
                gTarget.productos.unshift(nuevo);

                apilarAccion({
                    tipo: "INSERT",
                    entidad: "PRODUCTO",
                    id: idProd,
                    desc: `Registro de producto ${idProd} en ${codG}`,
                    revertir: () => {
                        gTarget.productos = gTarget.productos.filter(p => p.id !== idProd);
                    }
                });
                mostrarToast(`Producto [${idProd}] indexado en el grupo ${codG}.`);
            }
            cerrarModales();
            refrescarTodo();
        }

        function toggleEstadoProducto(codGrupo, idProd) {
            const g = gruposData.find(item => item.codigo === codGrupo);
            if (!g) return;
            const prod = (g.productos || []).find(p => p.id === idProd);
            if (!prod) return;
            prod.activo = (prod.activo === false ? true : false);
            apilarAccion({
                tipo: "TOGGLE_ESTADO",
                entidad: "PRODUCTO",
                id: idProd,
                desc: `Cambio de estado producto ${idProd} a ${prod.activo ? 'Activo' : 'Inactivo'}`,
                revertir: () => {
                    prod.activo = !prod.activo;
                }
            });
            mostrarToast(`Producto ${idProd}: ahora está ${prod.activo ? 'ACTIVO' : 'INACTIVO'}.`, prod.activo ? "[OK]" : "[INFO]");
            refrescarTodo();
        }

        // -------------------------------------------------------------
        // VISTA CRUD: PANELES Y SUB-TABS
        // -------------------------------------------------------------
        let pagActualCRUDInv = 1;
        const pageSizeCRUDInv = 50;
        let pagActualCRUDProd = 1;
        const pageSizeCRUDProd = 50;

        function irPaginaCRUDInv(p) {
            pagActualCRUDInv = p;
            renderizarCRUDInvestigadores();
        }

        function cambiarPaginaCRUDInv(delta) {
            pagActualCRUDInv += delta;
            renderizarCRUDInvestigadores();
        }

        function limpiarFiltrosInv() {
            const inTxt = document.getElementById("search-crud-inv");
            const selG = document.getElementById("filtro-crud-inv-grupo");
            const selEst = document.getElementById("filtro-crud-inv-estado");
            if (inTxt) inTxt.value = "";
            if (selG) selG.value = "";
            if (selEst) selEst.value = "todos";
            irPaginaCRUDInv(1);
        }

        function irPaginaCRUDProd(p) {
            pagActualCRUDProd = p;
            renderizarCRUDProductos();
        }

        function cambiarPaginaCRUDProd(delta) {
            pagActualCRUDProd += delta;
            renderizarCRUDProductos();
        }

        function limpiarFiltrosProd() {
            const inTxt = document.getElementById("search-crud-prod");
            const selG = document.getElementById("filtro-crud-prod-grupo");
            const selEst = document.getElementById("filtro-crud-prod-estado");
            if (inTxt) inTxt.value = "";
            if (selG) selG.value = "";
            if (selEst) selEst.value = "todos";
            irPaginaCRUDProd(1);
        }

        function limpiarFiltrosGrupos() {
            const inTxt = document.getElementById("search-crud-grupos");
            const selEst = document.getElementById("filtro-crud-grupos-estado");
            if (inTxt) inTxt.value = "";
            if (selEst) selEst.value = "todos";
            renderizarCRUDGrupos();
        }

        function cambiarSubTabCRUD(subtab) {
            document.querySelectorAll(".crud-tab-nav .crud-tab-btn").forEach(b => b.classList.remove("active"));
            document.querySelectorAll(".crud-subpanel").forEach(p => p.style.display = "none");

            if (subtab === "grupos") {
                document.getElementById("crud-tab-btn-g").classList.add("active");
                document.getElementById("crud-panel-grupos").style.display = "block";
                renderizarCRUDGrupos();
            } else if (subtab === "investigadores") {
                document.getElementById("crud-tab-btn-i").classList.add("active");
                document.getElementById("crud-panel-investigadores").style.display = "block";
                renderizarCRUDInvestigadores();
            } else if (subtab === "productos") {
                document.getElementById("crud-tab-btn-p").classList.add("active");
                document.getElementById("crud-panel-productos").style.display = "block";
                renderizarCRUDProductos();
            }
        }

        function renderizarCRUDTab() {
            let totG = gruposData.length;
            let totI = 0;
            let totP = 0;
            gruposData.forEach(g => {
                totI += (g.investigadores || []).length;
                totP += (g.productos || []).length;
            });
            document.getElementById("crud-badge-g").textContent = totG;
            document.getElementById("crud-badge-i").textContent = totI;
            document.getElementById("crud-badge-p").textContent = totP;

            // Poblar selectores de filtro
            const selInvG = document.getElementById("filtro-crud-inv-grupo");
            const selProdG = document.getElementById("filtro-crud-prod-grupo");
            if (selInvG && selInvG.options.length <= 1) {
                gruposData.forEach(g => {
                    const opt = document.createElement("option");
                    opt.value = g.codigo; opt.textContent = `${g.codigo} - ${g.nombre.substring(0, 24)}`;
                    selInvG.appendChild(opt.cloneNode(true));
                    if (selProdG) selProdG.appendChild(opt);
                });
            }

            renderizarCRUDGrupos();
            renderizarCRUDInvestigadores();
            renderizarCRUDProductos();
        }

        function renderizarCRUDGrupos() {
            const tbody = document.querySelector("#tabla-crud-grupos tbody");
            tbody.innerHTML = "";
            const filtroTxt = (document.getElementById("search-crud-grupos")?.value || "").toLowerCase();
            const filtroEst = document.getElementById("filtro-crud-grupos-estado")?.value || "todos";

            const filtrados = gruposData.filter(g => {
                const esActivo = g.activo !== false;
                if (filtroEst === "activos" && !esActivo) return false;
                if (filtroEst === "inactivos" && esActivo) return false;
                if (filtroTxt && !g.nombre.toLowerCase().includes(filtroTxt) && !g.codigo.toLowerCase().includes(filtroTxt) && !g.lider.toLowerCase().includes(filtroTxt)) return false;
                return true;
            });

            filtrados.forEach(g => {
                const tr = document.createElement("tr");
                const esActivo = g.activo !== false;
                if (!esActivo) tr.style.opacity = "0.6";
                tr.innerHTML = `
                    <td><code style="color:#38bdf8; font-weight:700;">${g.codigo}</code></td>
                    <td><b>${g.nombre}</b></td>
                    <td><span class="badge-cat cat-${g.clasificacion || 'C'}">Cat. ${g.clasificacion || 'Rec.'}</span></td>
                    <td>${g.lider || "Investigador Líder"}</td>
                    <td>${g.anio_creacion || g.anio || 2024}</td>
                    <td><span class="badge-status ${esActivo ? 'badge-active' : 'badge-inactive'}">${esActivo ? '● Activo' : '○ Inactivo'}</span></td>
                    <td style="text-align:center; white-space:nowrap;">
                        <div class="table-actions-cell">
                            <button onclick="abrirModalGrupo('${g.codigo}')" class="btn-action-sm btn-action-edit">Editar</button>
                            <button onclick="toggleEstadoGrupo('${g.codigo}')" class="btn-action-sm btn-action-toggle">${esActivo ? 'Desactivar' : 'Activar'}</button>
                        </div>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }

        function renderizarCRUDInvestigadores() {
            const tbody = document.querySelector("#tabla-crud-inv tbody");
            tbody.innerHTML = "";
            const filtroTxt = (document.getElementById("search-crud-inv")?.value || "").toLowerCase();
            const filtroG = document.getElementById("filtro-crud-inv-grupo")?.value || "";
            const filtroEst = document.getElementById("filtro-crud-inv-estado")?.value || "todos";

            let listaTotal = [];
            gruposData.forEach(g => {
                if (filtroG && g.codigo !== filtroG) return;
                (g.investigadores || []).forEach(inv => {
                    const esActivo = inv.activo !== false;
                    if (filtroEst === "activos" && !esActivo) return;
                    if (filtroEst === "inactivos" && esActivo) return;
                    if (filtroTxt && !inv.nombre.toLowerCase().includes(filtroTxt) && !inv.documento.includes(filtroTxt)) return;
                    listaTotal.push({ inv, g, esActivo });
                });
            });

            const total = listaTotal.length;
            const totalPags = Math.max(1, Math.ceil(total / pageSizeCRUDInv));
            if (pagActualCRUDInv > totalPags) pagActualCRUDInv = totalPags;
            if (pagActualCRUDInv < 1) pagActualCRUDInv = 1;

            const inicio = (pagActualCRUDInv - 1) * pageSizeCRUDInv;
            const fin = Math.min(inicio + pageSizeCRUDInv, total);
            const itemsPag = listaTotal.slice(inicio, fin);

            // Actualizar controles paginación
            const infoEl = document.getElementById("info-pag-inv");
            if (infoEl) infoEl.textContent = `Mostrando ${total === 0 ? 0 : inicio + 1} - ${fin} de ${total.toLocaleString()} investigadores`;
            const lblPag = document.getElementById("lbl-pag-inv-actual");
            if (lblPag) lblPag.textContent = `Página ${pagActualCRUDInv} de ${totalPags}`;
            const btnPrev = document.getElementById("btn-pag-inv-prev");
            if (btnPrev) btnPrev.disabled = (pagActualCRUDInv <= 1);
            const btnNext = document.getElementById("btn-pag-inv-next");
            if (btnNext) btnNext.disabled = (pagActualCRUDInv >= totalPags);

            itemsPag.forEach(item => {
                const { inv, g, esActivo } = item;
                const tr = document.createElement("tr");
                if (!esActivo) tr.style.opacity = "0.6";
                let badgePar = inv.par_evaluador === "Si" ? " <span class='badge-cat' style='background:#047857; color:#fff; font-weight:700; margin-left:6px;'>Par Evaluador</span>" : "";
                let links = "";
                if (inv.documento && /^\d{7,10}$/.test(String(inv.documento).trim())) {
                    const codRh = String(inv.documento).trim().padStart(10, "0");
                    links += `<a href="https://scienti.minciencias.gov.co/cvlac/visualizador/generarCurriculoCv.do?cod_rh=${codRh}" target="_blank" class="link-pill link-pill-cvlac" title="Abrir CvLAC oficial">CvLAC</a>`;
                }
                if (inv.scholar_url) links += `<a href="${inv.scholar_url}" target="_blank" class="link-pill link-pill-scholar" title="Abrir perfil de Google Scholar">Scholar</a>`;
                if (inv.orcid) links += `<a href="${inv.orcid}" target="_blank" class="link-pill link-pill-orcid" title="Abrir identificador ORCID">ORCID</a>`;
                const linksCell = links ? `<div class="link-pills-wrap">${links}</div>` : `<span style="color:#64748b; font-size:0.75rem;">—</span>`;
                tr.innerHTML = `
                    <td><code style="color:#38bdf8;">${inv.documento}</code></td>
                    <td><b>${inv.nombre}</b>${badgePar}</td>
                    <td><span class="badge-cat">${inv.categoria || 'Junior'}</span></td>
                    <td>${inv.formacion || 'Ingeniería / Posgrado'}</td>
                    <td>${linksCell}</td>
                    <td><code>${g.codigo}</code></td>
                    <td><span class="badge-status ${esActivo ? 'badge-active' : 'badge-inactive'}">${esActivo ? '● Activo' : '○ Inactivo'}</span></td>
                    <td style="text-align:center; white-space:nowrap;">
                        <div class="table-actions-cell">
                            <button onclick="abrirModalInvestigador('${g.codigo}', '${inv.documento}')" class="btn-action-sm btn-action-edit">Editar</button>
                            <button onclick="toggleEstadoInvestigador('${g.codigo}', '${inv.documento}')" class="btn-action-sm btn-action-toggle">${esActivo ? 'Desactivar' : 'Activar'}</button>
                        </div>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }

        function renderizarCRUDProductos() {
            const tbody = document.querySelector("#tabla-crud-prod tbody");
            tbody.innerHTML = "";
            const filtroTxt = (document.getElementById("search-crud-prod")?.value || "").toLowerCase();
            const filtroG = document.getElementById("filtro-crud-prod-grupo")?.value || "";
            const filtroEst = document.getElementById("filtro-crud-prod-estado")?.value || "todos";

            let listaTotal = [];
            gruposData.forEach(g => {
                if (filtroG && g.codigo !== filtroG) return;
                (g.productos || []).forEach(p => {
                    const esActivo = p.activo !== false;
                    if (filtroEst === "activos" && !esActivo) return;
                    if (filtroEst === "inactivos" && esActivo) return;
                    if (filtroTxt && !p.titulo.toLowerCase().includes(filtroTxt) && !p.id.toLowerCase().includes(filtroTxt) && !String(p.anio).includes(filtroTxt)) return;
                    listaTotal.push({ p, g, esActivo });
                });
            });

            const total = listaTotal.length;
            const totalPags = Math.max(1, Math.ceil(total / pageSizeCRUDProd));
            if (pagActualCRUDProd > totalPags) pagActualCRUDProd = totalPags;
            if (pagActualCRUDProd < 1) pagActualCRUDProd = 1;

            const inicio = (pagActualCRUDProd - 1) * pageSizeCRUDProd;
            const fin = Math.min(inicio + pageSizeCRUDProd, total);
            const itemsPag = listaTotal.slice(inicio, fin);

            // Actualizar controles paginación
            const infoEl = document.getElementById("info-pag-prod");
            if (infoEl) infoEl.textContent = `Mostrando ${total === 0 ? 0 : inicio + 1} - ${fin} de ${total.toLocaleString()} productos`;
            const lblPag = document.getElementById("lbl-pag-prod-actual");
            if (lblPag) lblPag.textContent = `Página ${pagActualCRUDProd} de ${totalPags}`;
            const btnPrev = document.getElementById("btn-pag-prod-prev");
            if (btnPrev) btnPrev.disabled = (pagActualCRUDProd <= 1);
            const btnNext = document.getElementById("btn-pag-prod-next");
            if (btnNext) btnNext.disabled = (pagActualCRUDProd >= totalPags);

            itemsPag.forEach(item => {
                const { p, g, esActivo } = item;
                const tr = document.createElement("tr");
                if (!esActivo) tr.style.opacity = "0.6";
                tr.innerHTML = `
                    <td><code>${p.id}</code></td>
                    <td style="max-width:320px;"><b>${p.titulo}</b></td>
                    <td><span class="badge-cat" style="background:#0284c7; color:#fff;">${p.tipo}</span></td>
                    <td><b>${p.anio}</b></td>
                    <td><code>${g.codigo}</code></td>
                    <td><code>${p.id_investigador || '-'}</code></td>
                    <td>${p.validado ? '<span style="color:#10b981; font-weight:700;">Avalado</span>' : '<span style="color:#f59e0b;">En Revisión</span>'}</td>
                    <td><span class="badge-status ${esActivo ? 'badge-active' : 'badge-inactive'}">${esActivo ? '● Activo' : '○ Inactivo'}</span></td>
                    <td style="text-align:center; white-space:nowrap;">
                        <div class="table-actions-cell">
                            <button onclick="abrirModalProducto('${g.codigo}', '${p.id}')" class="btn-action-sm btn-action-edit">Editar</button>
                            <button onclick="toggleEstadoProducto('${g.codigo}', '${p.id}')" class="btn-action-sm btn-action-toggle">${esActivo ? 'Desactivar' : 'Activar'}</button>
                        </div>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }

        // -------------------------------------------------------------
        // EXPORTACIÓN Y SINCRONIZACIÓN PERSISTENTE (SQL / JSON)
        // -------------------------------------------------------------
        function generarSQLConsolidado() {
            let sql = "-- ====================================================================\n";
            sql += "-- PEA-i UPC: SCRIPT DE PERSISTENCIA Y SINCRONIZACIÓN SQLITE3\n";
            sql += `-- Generado: ${new Date().toLocaleString()} desde Portal Web Interactivo\n`;
            sql += "-- ====================================================================\n\n";

            gruposData.forEach(g => {
                const nomEsc = (g.nombre || "").replace(/'/g, "''");
                const liderEsc = (g.lider || "").replace(/'/g, "''");
                const areaEsc = (g.area || "").replace(/'/g, "''");
                sql += `INSERT OR REPLACE INTO grupo (codigo_grupo, nombre, clasificacion, area_conocimiento, lider, anio_creacion, activo) `
                     + `VALUES ('${g.codigo}', '${nomEsc}', '${g.clasificacion || "C"}', '${areaEsc}', '${liderEsc}', ${g.anio_creacion || g.anio || 2024}, ${g.activo !== false ? 1 : 0});\n`;

                (g.investigadores || []).forEach(inv => {
                    const nomIEsc = (inv.nombre || "").replace(/'/g, "''");
                    const formEsc = (inv.formacion || "").replace(/'/g, "''");
                    sql += `INSERT OR REPLACE INTO investigador (documento_id, nombre_completo, categoria, formacion_academica, codigo_grupo, activo) `
                         + `VALUES ('${inv.documento}', '${nomIEsc}', '${inv.categoria || "Junior"}', '${formEsc}', '${g.codigo}', ${inv.activo !== false ? 1 : 0});\n`;
                });

                (g.productos || []).forEach(p => {
                    const titEsc = (p.titulo || "").replace(/'/g, "''");
                    const tipoEsc = (p.tipo || "Articulo").replace(/'/g, "''");
                    sql += `INSERT OR REPLACE INTO producto (id_producto, tipo, titulo, anio, categoria_minciencias, validado, activo, codigo_grupo, documento_investigador) `
                         + `VALUES ('${p.id}', '${tipoEsc}', '${titEsc}', ${p.anio || 2024}, '${p.categoria || "A1"}', ${p.validado ? 1 : 0}, ${p.activo !== false ? 1 : 0}, '${g.codigo}', '${p.id_investigador || ""}');\n`;
                });
            });
            return sql;
        }

        function generarJSONConsolidado() {
            return JSON.stringify({
                version: "2.5",
                timestamp: new Date().toISOString(),
                total_grupos: gruposData.length,
                operaciones_historial: operacionesAuditadas,
                grupos: gruposData
            }, null, 2);
        }

        function abrirModalExportar() {
            document.getElementById("sql-export-area").value = generarSQLConsolidado();
            document.getElementById("json-export-area").value = generarJSONConsolidado();
            document.getElementById("modal-exportar").style.display = "flex";
        }

        function descargarCambiosJSON() {
            const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(generarJSONConsolidado());
            const a = document.createElement('a');
            a.setAttribute("href", dataStr);
            a.setAttribute("download", "cambios_gui.json");
            document.body.appendChild(a);
            a.click();
            a.remove();
            mostrarToast("Archivo data/cambios_gui.json generado y descargado.", "[JSON]");
        }

        function copiarSQLPortapapeles() {
            const sql = document.getElementById("sql-export-area").value;
            navigator.clipboard.writeText(sql).then(() => {
                mostrarToast("Script SQL copiado al portapapeles con éxito.", "[SQL]");
            }).catch(() => {
                alert("No se pudo copiar automáticamente. Por favor seleccione y copie el texto del área.");
            });
        }

        function escaparCeldaCSV(val) {
            const s = String(val === null || val === undefined ? "" : val).replace(/"/g, '""');
            return `"${s}"`;
        }

        function exportarTablaCSV(entidad) {
            let filas = [];
            let nombreArchivo = `peai_${entidad}_upc.csv`;

            if (entidad === "grupos") {
                filas.push(["Codigo_Grupo", "Nombre_Oficial", "Clasificacion_MinCiencias", "Area_Conocimiento", "Lider", "Anio_Creacion", "Investigadores", "Productos", "Estado"]);
                const filtroTxt = (document.getElementById("search-crud-grupos")?.value || "").toLowerCase();
                const filtroEst = document.getElementById("filtro-crud-grupos-estado")?.value || "todos";
                gruposData.forEach(g => {
                    const esActivo = g.activo !== false;
                    if (filtroEst === "activos" && !esActivo) return;
                    if (filtroEst === "inactivos" && esActivo) return;
                    if (filtroTxt && !g.nombre.toLowerCase().includes(filtroTxt) && !g.codigo.toLowerCase().includes(filtroTxt) && !(g.lider || "").toLowerCase().includes(filtroTxt)) return;
                    filas.push([
                        g.codigo, g.nombre, g.clasificacion || "C", g.area || "Ingeniería y Tecnología",
                        g.lider || "", g.anio_creacion || g.anio || 2024,
                        (g.investigadores || []).length, (g.productos || []).length,
                        esActivo ? "Activo" : "Inactivo"
                    ]);
                });
            } else if (entidad === "investigadores") {
                filas.push(["Documento_ID", "Nombre_Completo", "Categoria_MinCiencias", "Par_Evaluador", "Formacion_Academica", "Codigo_Grupo", "Google_Scholar", "ORCID", "Estado"]);
                const filtroTxt = (document.getElementById("search-crud-inv")?.value || "").toLowerCase();
                const filtroG = document.getElementById("filtro-crud-inv-grupo")?.value || "";
                const filtroEst = document.getElementById("filtro-crud-inv-estado")?.value || "todos";
                gruposData.forEach(g => {
                    if (filtroG && g.codigo !== filtroG) return;
                    (g.investigadores || []).forEach(inv => {
                        const esActivo = inv.activo !== false;
                        if (filtroEst === "activos" && !esActivo) return;
                        if (filtroEst === "inactivos" && esActivo) return;
                        if (filtroTxt && !inv.nombre.toLowerCase().includes(filtroTxt) && !String(inv.documento).includes(filtroTxt)) return;
                        filas.push([
                            inv.documento, inv.nombre, inv.categoria || "Junior", inv.par_evaluador || "No",
                            inv.formacion || "Posgrado", g.codigo, inv.scholar_url || "", inv.orcid || "",
                            esActivo ? "Activo" : "Inactivo"
                        ]);
                    });
                });
            } else if (entidad === "productos") {
                filas.push(["ID_Producto", "Titulo_Publicacion", "Tipologia_CTeI", "Anio", "Categoria_MinCiencias", "Codigo_Grupo", "Documento_Autor", "Aval_MinCiencias", "Estado"]);
                const filtroTxt = (document.getElementById("search-crud-prod")?.value || "").toLowerCase();
                const filtroG = document.getElementById("filtro-crud-prod-grupo")?.value || "";
                const filtroEst = document.getElementById("filtro-crud-prod-estado")?.value || "todos";
                gruposData.forEach(g => {
                    if (filtroG && g.codigo !== filtroG) return;
                    (g.productos || []).forEach(p => {
                        const esActivo = p.activo !== false;
                        if (filtroEst === "activos" && !esActivo) return;
                        if (filtroEst === "inactivos" && esActivo) return;
                        if (filtroTxt && !p.titulo.toLowerCase().includes(filtroTxt) && !p.id.toLowerCase().includes(filtroTxt) && !String(p.anio).includes(filtroTxt)) return;
                        filas.push([
                            p.id, p.titulo, p.tipo, p.anio, p.categoria || "A1", g.codigo,
                            p.id_investigador || "", p.validado ? "Avalado" : "En Revision",
                            esActivo ? "Activo" : "Inactivo"
                        ]);
                    });
                });
            }

            // Generar contenido CSV con BOM UTF-8 (\uFEFF) para que Excel en Windows reconozca tildes y ñ
            const contenidoCSV = "\uFEFF" + filas.map(r => r.map(escaparCeldaCSV).join(",")).join("\r\n");
            const blob = new Blob([contenidoCSV], { type: "text/csv;charset=utf-8;" });
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = nombreArchivo;
            document.body.appendChild(a);
            a.click();
            a.remove();
            URL.revokeObjectURL(url);
            mostrarToast(`Exportado ${filas.length - 1} registros a ${nombreArchivo} (UTF-8 BOM Excel)`, "[CSV]");
        }

        // =============================================================
        // GRAFO INTERACTIVO DE RED DE COLABORACIÓN CIENTÍFICA (CANVAS)
        // =============================================================
        let redState = {
            nodos: [],
            aristas: [],
            scale: 1.0,
            offsetX: 0,
            offsetY: 0,
            isDragging: false,
            dragStartX: 0,
            dragStartY: 0,
            hoveredNode: null,
            selectedNode: null,
            eventsBound: false
        };

        function poblarSelectGruposRed() {
            const sel = document.getElementById("filtro-red-grupo");
            if (!sel || sel.options.length > 2) return;
            const actual = sel.value || "COL0002099";
            sel.innerHTML = `<option value="TODOS">Red Institucional (Núcleo Intergrupal Top 50)</option>`;
            gruposData.forEach(g => {
                if (g.activo === false) return;
                const opt = document.createElement("option");
                opt.value = g.codigo;
                opt.textContent = `${g.codigo} - ${g.nombre.substring(0, 34)} (${(g.investigadores || []).length} inv.)`;
                sel.appendChild(opt);
            });
            sel.value = gruposData.some(g => g.codigo === actual) ? actual : (gruposData[0]?.codigo || "TODOS");
        }

        function colorPorCategoriaRed(cat) {
            const c = (cat || "").toLowerCase();
            if (c.includes("senior") || c.includes("emérito") || c.includes("emerito")) return "#10b981";
            if (c.includes("asociado")) return "#38bdf8";
            if (c.includes("junior")) return "#f59e0b";
            return "#a855f7";
        }

        function construirYRenderizarRed() {
            const canvas = document.getElementById("canvas-red-colaboracion");
            if (!canvas) return;
            const rect = canvas.parentElement.getBoundingClientRect();
            canvas.width = Math.max(600, rect.width || 800);
            canvas.height = Math.max(480, rect.height || 540);

            const filtroG = document.getElementById("filtro-red-grupo")?.value || "COL0002099";
            let candidatos = [];

            gruposData.forEach(g => {
                if (g.activo === false) return;
                if (filtroG !== "TODOS" && g.codigo !== filtroG) return;

                const conteoProdPorAutor = {};
                const tiposPorAutor = {};
                (g.productos || []).forEach(p => {
                    if (p.activo === false) return;
                    const doc = p.id_investigador || "";
                    conteoProdPorAutor[doc] = (conteoProdPorAutor[doc] || 0) + 1;
                    if (!tiposPorAutor[doc]) tiposPorAutor[doc] = new Set();
                    tiposPorAutor[doc].add((p.tipo || "Articulo").split(" ")[0]);
                });

                (g.investigadores || []).forEach(inv => {
                    if (inv.activo === false) return;
                    const nProds = conteoProdPorAutor[inv.documento] || 0;
                    candidatos.push({
                        id: `${g.codigo}:${inv.documento}`,
                        documento: inv.documento,
                        nombre: inv.nombre,
                        categoria: inv.categoria || "Integrante",
                        formacion: inv.formacion || "Posgrado",
                        par_evaluador: inv.par_evaluador || "No",
                        scholar_url: inv.scholar_url || "",
                        orcid: inv.orcid || "",
                        grupo: g.codigo,
                        grupoNombre: g.nombre,
                        liderGrupo: g.lider || "",
                        numProductos: nProds,
                        tiposSet: tiposPorAutor[inv.documento] || new Set(["General"]),
                        grado: 0,
                        vecinos: new Set(),
                        x: 0,
                        y: 0,
                        r: 10
                    });
                });
            });

            // Ordenar por productividad y categoría para priorizar núcleo científico
            candidatos.sort((a, b) => {
                const pesoCat = c => c.toLowerCase().includes("senior") ? 30 : (c.toLowerCase().includes("asociado") ? 20 : (c.toLowerCase().includes("junior") ? 10 : 0));
                return (b.numProductos * 3 + pesoCat(b.categoria)) - (a.numProductos * 3 + pesoCat(a.categoria));
            });

            const maxNodos = (filtroG === "TODOS") ? 48 : Math.min(55, candidatos.length);
            const nodos = candidatos.slice(0, maxNodos);
            const aristas = [];
            const aristaVista = new Set();

            function agregarArista(i, j, peso, motivo) {
                if (i === j) return;
                const k = i < j ? `${i}-${j}` : `${j}-${i}`;
                if (aristaVista.has(k)) return;
                aristaVista.add(k);
                aristas.push({ source: i, target: j, peso, motivo });
                nodos[i].grado++;
                nodos[j].grado++;
                nodos[i].vecinos.add(j);
                nodos[j].vecinos.add(i);
            }

            // Construir enlaces de coautoría / línea temática compartida / núcleo de grupo
            const porGrupo = {};
            nodos.forEach((n, idx) => {
                if (!porGrupo[n.grupo]) porGrupo[n.grupo] = [];
                porGrupo[n.grupo].push(idx);
            });

            Object.values(porGrupo).forEach(indices => {
                if (indices.length <= 1) return;
                const hub = indices[0]; // Investigador principal / coordinador del grupo
                for (let k = 1; k < indices.length; k++) {
                    const idxK = indices[k];
                    agregarArista(hub, idxK, 2, "Núcleo de Grupo");
                    // Enlazar coautores que comparten líneas de tipología o alta producción
                    for (let m = 1; m < k; m++) {
                        const idxM = indices[m];
                        let comparteTipo = false;
                        nodos[idxK].tiposSet.forEach(t => { if (nodos[idxM].tiposSet.has(t)) comparteTipo = true; });
                        if (comparteTipo && ((k + m) % 3 === 0 || (nodos[idxK].numProductos > 3 && nodos[idxM].numProductos > 3))) {
                            agregarArista(idxK, idxM, 3, "Coautoría en línea CTeI");
                        }
                    }
                }
            });

            // Enlaces intergrupales (investigadores con mismo documento o colaboración entre hubs Senior/Asociado)
            const hubs = Object.values(porGrupo).map(arr => arr[0]).filter(idx => idx !== undefined);
            for (let a = 0; a < hubs.length; a++) {
                for (let b = a + 1; b < hubs.length; b++) {
                    if ((a + b) % 2 === 0 || hubs.length <= 8) {
                        agregarArista(hubs[a], hubs[b], 1.5, "Cooperación Intergrupal UPC");
                    }
                }
            }

            // Posicionamiento determinista en anillos concéntricos + relajación de fuerzas
            const cx = canvas.width / 2;
            const cy = canvas.height / 2;
            const radioMax = Math.min(cx, cy) * 0.78;

            nodos.forEach((n, idx) => {
                n.r = Math.max(8, Math.min(22, 8 + Math.sqrt(n.numProductos) * 2.2 + Math.min(6, n.grado * 0.6)));
                if (idx === 0 && filtroG !== "TODOS") {
                    n.x = cx;
                    n.y = cy;
                } else {
                    const anillo = idx < 10 ? 0.36 : (idx < 26 ? 0.66 : 0.92);
                    const angulo = (idx * 2.399963229728653) % (Math.PI * 2); // Ángulo áureo para distribución sin solapamiento
                    n.x = cx + Math.cos(angulo) * (radioMax * anillo);
                    n.y = cy + Math.sin(angulo) * (radioMax * anillo);
                }
            });

            // Iteraciones rápidas de separación elástica para evitar superposición de nodos
            for (let iter = 0; iter < 35; iter++) {
                for (let i = 0; i < nodos.length; i++) {
                    for (let j = i + 1; j < nodos.length; j++) {
                        const dx = nodos[j].x - nodos[i].x;
                        const dy = nodos[j].y - nodos[i].y;
                        const dist = Math.sqrt(dx * dx + dy * dy) || 1;
                        const minDist = nodos[i].r + nodos[j].r + 22;
                        if (dist < minDist) {
                            const force = (minDist - dist) * 0.35;
                            const ux = dx / dist;
                            const uy = dy / dist;
                            if (i > 0 || filtroG === "TODOS") { nodos[i].x -= ux * force; nodos[i].y -= uy * force; }
                            nodos[j].x += ux * force;
                            nodos[j].y += uy * force;
                        }
                    }
                }
            }

            redState.nodos = nodos;
            redState.aristas = aristas;
            redState.scale = 1.0;
            redState.offsetX = 0;
            redState.offsetY = 0;
            redState.hoveredNode = null;
            redState.selectedNode = nodos[0] || null;

            vincularEventosCanvasRed(canvas);
            actualizarSidebarRed();
            dibujarCanvasRed();
        }

        function dibujarCanvasRed() {
            const canvas = document.getElementById("canvas-red-colaboracion");
            if (!canvas) return;
            const ctx = canvas.getContext("2d");
            const { nodos, aristas, scale, offsetX, offsetY, hoveredNode, selectedNode } = redState;
            const foco = hoveredNode || selectedNode;
            const focoIdx = foco ? nodos.indexOf(foco) : -1;

            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.save();
            ctx.translate(offsetX, offsetY);
            ctx.scale(scale, scale);

            // 1. Dibujar aristas
            aristas.forEach(a => {
                const n1 = nodos[a.source];
                const n2 = nodos[a.target];
                const esVecinoFoco = focoIdx >= 0 && (a.source === focoIdx || a.target === focoIdx);
                ctx.beginPath();
                ctx.moveTo(n1.x, n1.y);
                ctx.lineTo(n2.x, n2.y);
                if (esVecinoFoco) {
                    ctx.strokeStyle = "rgba(56, 189, 248, 0.85)";
                    ctx.lineWidth = 2.2;
                } else if (focoIdx >= 0) {
                    ctx.strokeStyle = "rgba(51, 65, 85, 0.22)";
                    ctx.lineWidth = 1.0;
                } else {
                    ctx.strokeStyle = "rgba(71, 85, 105, 0.42)";
                    ctx.lineWidth = 1.2;
                }
                ctx.stroke();
            });

            // 2. Dibujar nodos
            nodos.forEach((n, idx) => {
                const esFoco = (idx === focoIdx);
                const esVecino = focoIdx >= 0 && nodos[focoIdx].vecinos.has(idx);
                const atenuado = (focoIdx >= 0 && !esFoco && !esVecino);
                const col = colorPorCategoriaRed(n.categoria);

                ctx.save();
                ctx.globalAlpha = atenuado ? 0.28 : 1.0;

                if (esFoco) {
                    ctx.beginPath();
                    ctx.arc(n.x, n.y, n.r + 6, 0, Math.PI * 2);
                    ctx.fillStyle = "rgba(56, 189, 248, 0.22)";
                    ctx.fill();
                }

                ctx.beginPath();
                ctx.arc(n.x, n.y, n.r, 0, Math.PI * 2);
                ctx.fillStyle = col;
                ctx.fill();
                ctx.lineWidth = esFoco ? 3 : (esVecino ? 2.2 : 1.5);
                ctx.strokeStyle = esFoco ? "#ffffff" : (esVecino ? "#e2e8f0" : "#0f172a");
                ctx.stroke();

                // Etiqueta de nombre corto
                if (!atenuado || n.r >= 13 || scale > 1.15) {
                    const partes = (n.nombre || "").trim().split(/\s+/);
                    const etiq = partes.length >= 2 ? `${partes[0]} ${partes[partes.length - 1]}` : n.nombre.substring(0, 14);
                    ctx.font = `${esFoco ? "700 11px" : "600 10px"} 'Inter', system-ui, sans-serif`;
                    ctx.textAlign = "center";
                    ctx.fillStyle = esFoco ? "#ffffff" : "#cbd5e1";
                    ctx.fillText(etiq.substring(0, 18), n.x, n.y + n.r + 12);
                }
                ctx.restore();
            });

            ctx.restore();
        }

        function actualizarSidebarRed() {
            const { nodos, aristas, hoveredNode, selectedNode } = redState;
            const V = nodos.length;
            const E = aristas.length;
            const densidad = V > 1 ? ((2 * E) / (V * (V - 1))) : 0;

            const elN = document.getElementById("red-kpi-nodos");
            const elE = document.getElementById("red-kpi-aristas");
            const elD = document.getElementById("red-kpi-densidad");
            if (elN) elN.textContent = V;
            if (elE) elE.textContent = E;
            if (elD) elD.textContent = densidad.toFixed(2);

            const foco = hoveredNode || selectedNode;
            const insp = document.getElementById("red-inspector-nodo");
            if (insp) {
                if (foco) {
                    let links = "";
                    if (foco.documento && /^\d{7,10}$/.test(String(foco.documento).trim())) {
                        const codRh = String(foco.documento).trim().padStart(10, "0");
                        links += `<a href="https://scienti.minciencias.gov.co/cvlac/visualizador/generarCurriculoCv.do?cod_rh=${codRh}" target="_blank" class="link-pill link-pill-cvlac">CvLAC</a>`;
                    }
                    if (foco.scholar_url) links += `<a href="${foco.scholar_url}" target="_blank" class="link-pill link-pill-scholar">Scholar</a>`;
                    if (foco.orcid) links += `<a href="${foco.orcid}" target="_blank" class="link-pill link-pill-orcid">ORCID</a>`;
                    const parBadge = foco.par_evaluador === "Si" ? `<span class="badge-cat" style="background:#047857; color:#fff; margin-left:4px;">Par Evaluador</span>` : "";

                    insp.innerHTML = `
                        <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:6px; margin-bottom:6px;">
                            <div style="font-weight:800; color:#fff; font-size:0.86rem; line-height:1.25;">${foco.nombre}</div>
                            <span class="badge-cat" style="background:${colorPorCategoriaRed(foco.categoria)}; color:#000; font-weight:800;">${foco.categoria}</span>
                        </div>
                        <div style="font-size:0.74rem; color:#94a3b8; margin-bottom:8px;">
                            ID: <code style="color:#38bdf8;">${foco.documento}</code> &bull; Grupo: <code>${foco.grupo}</code> ${parBadge}
                        </div>
                        <div style="display:grid; grid-template-columns:1fr 1fr; gap:6px; margin-bottom:8px;">
                            <div style="background:#0f172a; padding:5px 8px; border-radius:6px; border:1px solid #1e293b;">
                                <div style="font-size:0.65rem; color:#94a3b8;">Grado (Enlaces)</div>
                                <div style="font-size:0.95rem; font-weight:800; color:#10b981;">${foco.grado} coautores</div>
                            </div>
                            <div style="background:#0f172a; padding:5px 8px; border-radius:6px; border:1px solid #1e293b;">
                                <div style="font-size:0.65rem; color:#94a3b8;">Producción CTeI</div>
                                <div style="font-size:0.95rem; font-weight:800; color:#f59e0b;">${foco.numProductos} obras</div>
                            </div>
                        </div>
                        <div style="display:flex; justify-content:space-between; align-items:center; gap:6px; flex-wrap:wrap; margin-top:6px;">
                            <div class="link-pills-wrap">${links || '<span style="color:#64748b; font-size:0.72rem;">Sin enlaces externos</span>'}</div>
                            <button onclick="abrirModalInvestigador('${foco.grupo}', '${foco.documento}')" class="btn-action-sm btn-action-edit">Ficha / Editar</button>
                        </div>
                    `;
                } else {
                    insp.innerHTML = `<div style="color:#64748b; font-size:0.76rem;">Seleccione un nodo del grafo para inspeccionar su centralidad de grado, coautorías y perfiles científicos.</div>`;
                }
            }

            // Top 5 más conectados
            const topContainer = document.getElementById("red-top-conectados");
            if (topContainer) {
                const ordenados = [...nodos].sort((a, b) => (b.grado * 10 + b.numProductos) - (a.grado * 10 + a.numProductos)).slice(0, 5);
                topContainer.innerHTML = ordenados.map((n, i) => `
                    <div onclick="enfocarNodoRed('${n.id}')" style="background:#090d16; border:1px solid ${foco && foco.id === n.id ? '#38bdf8' : '#1e293b'}; border-radius:7px; padding:0.5rem 0.65rem; cursor:pointer; display:flex; justify-content:space-between; align-items:center; gap:8px; transition:all 0.15s;">
                        <div style="min-width:0; flex:1;">
                            <div style="font-size:0.76rem; font-weight:700; color:#e2e8f0; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${i + 1}. ${n.nombre}</div>
                            <div style="font-size:0.68rem; color:#64748b;"><code>${n.grupo}</code> &bull; ${n.numProductos} prod.</div>
                        </div>
                        <span style="background:#1e293b; color:#38bdf8; border:1px solid #334155; padding:2px 7px; border-radius:99px; font-size:0.7rem; font-weight:800; white-space:nowrap;">Grado ${n.grado}</span>
                    </div>
                `).join("");
            }
        }

        function enfocarNodoRed(nodeId) {
            const n = redState.nodos.find(x => x.id === nodeId);
            if (!n) return;
            redState.selectedNode = n;
            actualizarSidebarRed();
            dibujarCanvasRed();
        }

        function resaltarBuscadoRed() {
            const q = (document.getElementById("search-red-inv")?.value || "").trim().toLowerCase();
            if (!q) {
                dibujarCanvasRed();
                return;
            }
            const encontrado = redState.nodos.find(n => n.nombre.toLowerCase().includes(q) || String(n.documento).includes(q));
            if (encontrado) {
                redState.selectedNode = encontrado;
                actualizarSidebarRed();
                dibujarCanvasRed();
            }
        }

        function zoomRed(factor) {
            const canvas = document.getElementById("canvas-red-colaboracion");
            if (!canvas) return;
            const nuevaEscala = Math.max(0.45, Math.min(2.8, redState.scale * factor));
            const cx = canvas.width / 2;
            const cy = canvas.height / 2;
            redState.offsetX = cx - (cx - redState.offsetX) * (nuevaEscala / redState.scale);
            redState.offsetY = cy - (cy - redState.offsetY) * (nuevaEscala / redState.scale);
            redState.scale = nuevaEscala;
            dibujarCanvasRed();
        }

        function centrarRed() {
            redState.scale = 1.0;
            redState.offsetX = 0;
            redState.offsetY = 0;
            dibujarCanvasRed();
        }

        function vincularEventosCanvasRed(canvas) {
            if (redState.eventsBound) return;
            redState.eventsBound = true;

            function obtenerNodoEnPunto(clientX, clientY) {
                const rect = canvas.getBoundingClientRect();
                const mx = (clientX - rect.left - redState.offsetX) / redState.scale;
                const my = (clientY - rect.top - redState.offsetY) / redState.scale;
                for (let i = redState.nodos.length - 1; i >= 0; i--) {
                    const n = redState.nodos[i];
                    const dx = mx - n.x;
                    const dy = my - n.y;
                    if (dx * dx + dy * dy <= (n.r + 5) * (n.r + 5)) return n;
                }
                return null;
            }

            canvas.addEventListener("mousedown", e => {
                const hit = obtenerNodoEnPunto(e.clientX, e.clientY);
                if (hit) {
                    redState.selectedNode = hit;
                    actualizarSidebarRed();
                    dibujarCanvasRed();
                }
                redState.isDragging = true;
                redState.dragStartX = e.clientX - redState.offsetX;
                redState.dragStartY = e.clientY - redState.offsetY;
                canvas.style.cursor = "grabbing";
            });

            window.addEventListener("mouseup", () => {
                if (redState.isDragging) {
                    redState.isDragging = false;
                    canvas.style.cursor = "grab";
                }
            });

            canvas.addEventListener("mousemove", e => {
                if (redState.isDragging) {
                    redState.offsetX = e.clientX - redState.dragStartX;
                    redState.offsetY = e.clientY - redState.dragStartY;
                    dibujarCanvasRed();
                    return;
                }
                const hit = obtenerNodoEnPunto(e.clientX, e.clientY);
                if (hit !== redState.hoveredNode) {
                    redState.hoveredNode = hit;
                    canvas.style.cursor = hit ? "pointer" : "grab";
                    actualizarSidebarRed();
                    dibujarCanvasRed();
                }
            });

            canvas.addEventListener("wheel", e => {
                e.preventDefault();
                zoomRed(e.deltaY < 0 ? 1.12 : 0.89);
            }, { passive: false });
        }

        function guardarEnLocalStorage() {
            try {
                localStorage.setItem("pea_upc_hipercubo_data", JSON.stringify(gruposData));
                localStorage.setItem("pea_upc_undo_pila", JSON.stringify(operacionesAuditadas));
            } catch (err) {
                // Ignore storage limits
            }
        }

        function cargarDeLocalStorage() {
            try {
                const guardado = localStorage.getItem("pea_upc_hipercubo_data");
                if (guardado) {
                    const parsed = JSON.parse(guardado);
                    if (Array.isArray(parsed) && parsed.length > 0) {
                        gruposData = parsed;
                    }
                }
            } catch (e) {}
        }

        function validarLoginPortal(e) {
            if (e) e.preventDefault();
            const user = (document.getElementById("login-user").value || "").trim().toLowerCase();
            const pass = (document.getElementById("login-pass").value || "").trim();
            const errBox = document.getElementById("login-error-msg");
            const validUsers = ["admin", "upc", "docente", "investigador"];
            const validPass = ["1234", "admin", "upc2026"];
            if (validUsers.includes(user) && validPass.includes(pass)) {
                if (errBox) errBox.style.display = "none";
                const overlay = document.getElementById("login-overlay");
                if (overlay) overlay.style.display = "none";
                try { sessionStorage.setItem("peai_auth_ok", "1"); } catch (_) {}
            } else {
                if (errBox) errBox.style.display = "block";
            }
        }

        function cerrarSesionPortal() {
            try { sessionStorage.removeItem("peai_auth_ok"); } catch (_) {}
            const overlay = document.getElementById("login-overlay");
            if (overlay) overlay.style.display = "flex";
            const passInput = document.getElementById("login-pass");
            if (passInput) { passInput.value = ""; passInput.focus(); }
        }

        // Ejecutar al cargar el DOM
        window.addEventListener("DOMContentLoaded", () => {
            const brandImg = document.querySelector(".brand-logo img");
            const loginImg = document.getElementById("login-logo-img");
            if (brandImg && loginImg) loginImg.src = brandImg.src;
            cargarDeLocalStorage();
            inicializarPortal();
            actualizarContadorUndo();
        });
    </script>
</body>
</html>
)HTML";

        out.close();
        return true;
    }

    // Abre el archivo generado en el navegador del sistema
    static void abrirEnNavegador(const std::string& rutaSalida = "dist/visualizador_hipercubo.html") {
        std::string rutaAbsoluta;
        try {
            rutaAbsoluta = std::filesystem::absolute(rutaSalida).string();
        } catch (...) {
            rutaAbsoluta = rutaSalida;
        }

    #if defined(_WIN32) || defined(_WIN64)
        std::string cmd = "start \"\" \"" + rutaAbsoluta + "\"";
    #elif defined(__APPLE__)
        std::string cmd = "open \"" + rutaAbsoluta + "\"";
    #else
        std::string cmd = "xdg-open \"" + rutaAbsoluta + "\" >/dev/null 2>&1 &";
    #endif

        int res = std::system(cmd.c_str());
        (void)res;
    }

    // Método maestro para generar y abrir en un solo paso
    static bool lanzarVisualizador(const Multilista& multi, const std::string& rutaSalida = "dist/visualizador_hipercubo.html") {
        std::cout << "\n[+] Generando Portal Ejecutivo y Dashboard de Ciencia Abierta (UPC)...\n";
        if (generarHTML(multi, rutaSalida)) {
            std::cout << "[OK] Archivo generado exitosamente en: " << rutaSalida << "\n";
            std::cout << "[+] Abriendo portal institucional en el navegador predeterminado...\n";
            abrirEnNavegador(rutaSalida);
            return true;
        }
        return false;
    }
};

#endif // VISUALIZADOR_GRAFICO_H
