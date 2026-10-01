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

                json << "        {\n";
                json << "          \"documento\": \"" << escaparJSON(inv->documento_id) << "\",\n";
                json << "          \"nombre\": \"" << escaparJSON(inv->nombre_completo) << "\",\n";
                json << "          \"categoria\": \"" << escaparJSON(inv->categoria) << "\",\n";
                json << "          \"formacion\": \"" << escaparJSON(inv->formacion_academica) << "\",\n";
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
            background: linear-gradient(135deg, #022c19 0%, #090d16 65%, #18090d 100%);
            border-bottom: 2px solid var(--upc-green);
            padding: 0.9rem 2rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            position: sticky;
            top: 0;
            z-index: 100;
            backdrop-filter: blur(10px);
        }
        .brand-box { display: flex; align-items: center; gap: 1rem; }
        .brand-logo {
            width: 44px; height: 44px;
            background: linear-gradient(135deg, var(--upc-green) 50%, var(--upc-red) 50%);
            border-radius: 10px;
            display: flex; align-items: center; justify-content: center;
            font-weight: 900; font-size: 1.1rem; color: #fff;
            box-shadow: 0 4px 14px rgba(0, 104, 55, 0.4);
        }
        .brand-text h1 { font-size: 1.2rem; font-weight: 800; letter-spacing: -0.3px; display: flex; align-items: center; gap: 0.5rem; }
        .brand-badge { background: rgba(16, 185, 129, 0.2); color: var(--upc-green-light); font-size: 0.7rem; padding: 2px 7px; border-radius: 12px; font-weight: 700; }
        .brand-text p { font-size: 0.78rem; color: var(--text-muted); }

        .nav-tabs { display: flex; gap: 0.4rem; background: rgba(15, 23, 42, 0.85); padding: 0.3rem; border-radius: 8px; border: 1px solid var(--card-border); }
        .tab-btn {
            background: transparent; border: none; color: var(--text-muted);
            padding: 0.5rem 1.1rem; border-radius: 6px; cursor: pointer;
            font-weight: 600; font-size: 0.84rem; transition: all 0.2s ease;
            display: flex; align-items: center; gap: 0.4rem;
        }
        .tab-btn:hover { color: #fff; background: rgba(255,255,255,0.06); }
        .tab-btn.active { background: var(--upc-green); color: #fff; box-shadow: 0 2px 10px rgba(16, 185, 129, 0.4); }

        /* KPI BAR */
        .kpi-bar {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1rem;
            padding: 1.2rem 2rem 0.5rem 2rem;
        }
        .kpi-card {
            background: var(--bg-card);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            padding: 1rem 1.2rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .kpi-title { font-size: 0.75rem; text-transform: uppercase; color: var(--text-muted); font-weight: 700; letter-spacing: 0.5px; }
        .kpi-val { font-size: 1.6rem; font-weight: 800; margin-top: 0.2rem; }

        /* MAIN CONTENT AREA */
        main { flex: 1; padding: 1rem 2rem 2rem 2rem; display: flex; flex-direction: column; }
        .view-panel { display: none; }
        .view-panel.active { display: block; }

        /* VISTA 1: PORTAL DE GRUPOS (SPLIT LAYOUT) */
        .portal-layout {
            display: grid;
            grid-template-columns: 360px 1fr;
            gap: 1.5rem;
            height: calc(100vh - 210px);
            min-height: 600px;
        }

        /* COLUMNA IZQUIERDA: LISTA DE GRUPOS */
        .groups-sidebar {
            background: var(--bg-card);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        .sidebar-header {
            padding: 1rem;
            border-bottom: 1px solid var(--card-border);
            display: flex;
            flex-direction: column;
            gap: 0.6rem;
        }
        .search-input {
            width: 100%;
            background: #090d16;
            border: 1px solid var(--card-border);
            color: #fff;
            padding: 0.55rem 0.9rem;
            border-radius: 8px;
            font-size: 0.82rem;
            outline: none;
            transition: border-color 0.2s;
        }
        .search-input:focus { border-color: var(--upc-green-light); }
        .filter-tags { display: flex; gap: 0.3rem; flex-wrap: wrap; }
        .tag-btn {
            background: rgba(255,255,255,0.04);
            border: 1px solid var(--card-border);
            color: var(--text-muted);
            padding: 0.25rem 0.6rem;
            border-radius: 6px;
            font-size: 0.72rem;
            cursor: pointer;
            font-weight: 600;
        }
        .tag-btn.active { background: var(--upc-green); color: #fff; border-color: var(--upc-green-light); }

        .groups-scroll-list {
            flex: 1;
            overflow-y: auto;
            padding: 0.8rem;
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }
        .group-card-item {
            background: #090d16;
            border: 1px solid var(--card-border);
            border-radius: 8px;
            padding: 0.75rem 0.9rem;
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
        .g-item-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem; }
        .g-item-code { font-size: 0.75rem; font-weight: 800; color: #38bdf8; font-family: monospace; }
        .badge-cat {
            font-size: 0.68rem; font-weight: 700; padding: 2px 6px; border-radius: 4px;
            background: rgba(245, 158, 11, 0.15); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.3);
        }
        .badge-cat.cat-A1, .badge-cat.cat-A { background: rgba(16, 185, 129, 0.15); color: #10b981; border-color: rgba(16, 185, 129, 0.3); }
        .badge-cat.cat-B { background: rgba(56, 189, 248, 0.15); color: #38bdf8; border-color: rgba(56, 189, 248, 0.3); }
        .badge-cat.cat-C { background: rgba(168, 85, 247, 0.15); color: #c084fc; border-color: rgba(168, 85, 247, 0.3); }

        .g-item-name { font-size: 0.82rem; font-weight: 700; margin-bottom: 0.3rem; line-height: 1.25; color: #f1f5f9; }
        .g-item-footer { font-size: 0.72rem; color: var(--text-muted); display: flex; justify-content: space-between; }

        /* COLUMNA DERECHA: PERFIL DEL GRUPO */
        .group-detail-view {
            background: var(--bg-card);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        .group-hero {
            background: linear-gradient(135deg, rgba(0, 104, 55, 0.3) 0%, rgba(15, 23, 42, 0.95) 70%);
            border-bottom: 1px solid var(--card-border);
            padding: 1.4rem 1.6rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .hero-info { display: flex; gap: 1.2rem; align-items: center; }
        .hero-avatar {
            width: 58px; height: 58px; border-radius: 12px;
            background: linear-gradient(135deg, var(--upc-green) 0%, #064e3b 100%);
            display: flex; align-items: center; justify-content: center;
            font-size: 1.6rem; font-weight: 800; color: #fff;
            box-shadow: 0 4px 15px rgba(0,0,0,0.4);
            border: 1px solid rgba(255,255,255,0.1);
        }
        .hero-title h2 { font-size: 1.25rem; font-weight: 800; line-height: 1.3; }
        .hero-meta { display: flex; gap: 0.8rem; align-items: center; margin-top: 0.4rem; font-size: 0.78rem; color: var(--text-muted); }

        .btn-pdf-download {
            background: var(--upc-green);
            color: #fff;
            padding: 0.65rem 1.2rem;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 700;
            font-size: 0.82rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            transition: all 0.2s ease;
            box-shadow: 0 4px 12px rgba(0, 104, 55, 0.4);
            border: none;
            cursor: pointer;
        }
        .btn-pdf-download:hover { background: #007f43; transform: translateY(-1px); }

        /* SUB-TABS DEL PERFIL */
        .profile-nav {
            display: flex;
            background: #090d16;
            border-bottom: 1px solid var(--card-border);
            padding: 0 1.2rem;
            gap: 0.4rem;
        }
        .p-tab-btn {
            background: transparent;
            border: none;
            color: var(--text-muted);
            padding: 0.75rem 1rem;
            font-weight: 600;
            font-size: 0.82rem;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            transition: all 0.2s;
        }
        .p-tab-btn:hover { color: #fff; }
        .p-tab-btn.active { color: var(--upc-green-light); border-bottom-color: var(--upc-green-light); }

        .profile-content {
            flex: 1;
            overflow-y: auto;
            padding: 1.4rem;
        }
        .profile-section { display: none; }
        .profile-section.active { display: block; }

        /* GRID INFORMACIÓN GENERAL */
        .info-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1rem;
            margin-bottom: 1.2rem;
        }
        .info-card {
            background: #090d16;
            border: 1px solid var(--card-border);
            border-radius: 8px;
            padding: 1rem;
        }
        .info-card-label { font-size: 0.72rem; color: var(--text-muted); text-transform: uppercase; font-weight: 700; margin-bottom: 0.3rem; }
        .info-card-val { font-size: 1.05rem; font-weight: 700; color: #f1f5f9; }

        /* TABLAS DE DATOS */
        .data-table-container {
            border: 1px solid var(--card-border);
            border-radius: 8px;
            overflow: hidden;
            background: #090d16;
        }
        table.peai-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.8rem;
            text-align: left;
        }
        table.peai-table th {
            background: #0d1527;
            padding: 0.65rem 0.9rem;
            color: var(--text-muted);
            font-weight: 700;
            border-bottom: 1px solid var(--card-border);
        }
        table.peai-table td {
            padding: 0.65rem 0.9rem;
            border-bottom: 1px solid rgba(30, 41, 59, 0.6);
            color: #e2e8f0;
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
    <!-- HEADER -->
    <header>
        <div class="brand-box">
            <div class="brand-logo">UPC</div>
            <div class="brand-text">
                <h1>PEA-i &bull; Portal de Ciencia Abierta <span class="brand-badge">v2.4 Oficial</span></h1>
                <p>Facultad de Ingeniería y Tecnológicas &bull; Sistema Estadístico de Investigación (MinCiencias SCIENTI)</p>
            </div>
        </div>
        <div class="nav-tabs">
            <button class="tab-btn active" onclick="cambiarVistaPrincipal('portal')">🏛️ Directorio de Grupos</button>
            <button class="tab-btn" onclick="cambiarVistaPrincipal('dashboard')">📊 Dashboard Analítico (12.b)</button>
            <button class="tab-btn" onclick="cambiarVistaPrincipal('tablas')">📑 Vistas por Entidad (12.c)</button>
        </div>
    </header>

    <!-- KPI BAR -->
    <div class="kpi-bar">
        <div class="kpi-card">
            <div>
                <div class="kpi-title">Grupos de Investigación</div>
                <div class="kpi-val" id="kpi-grupos" style="color: #38bdf8;">0</div>
            </div>
            <div style="font-size: 1.8rem; opacity: 0.6;">🏢</div>
        </div>
        <div class="kpi-card">
            <div>
                <div class="kpi-title">Investigadores Registrados</div>
                <div class="kpi-val" id="kpi-investigadores" style="color: #10b981;">0</div>
            </div>
            <div style="font-size: 1.8rem; opacity: 0.6;">👨‍🔬</div>
        </div>
        <div class="kpi-card">
            <div>
                <div class="kpi-title">Productos Científicos</div>
                <div class="kpi-val" id="kpi-productos" style="color: #f59e0b;">0</div>
            </div>
            <div style="font-size: 1.8rem; opacity: 0.6;">📚</div>
        </div>
        <div class="kpi-card">
            <div>
                <div class="kpi-title">Puntos IPP (Modelo 2024)</div>
                <div class="kpi-val" id="kpi-ipp" style="color: #c084fc;">0 pts</div>
            </div>
            <div style="font-size: 1.8rem; opacity: 0.6;">🏆</div>
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
                        <input type="text" class="search-input" id="search-grupos" placeholder="🔍 Buscar por nombre o código (ej: GISICO)..." oninput="filtrarListaGrupos()">
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
                                    <span>Universidad Popular del Cesar (UPC)</span>
                                </div>
                            </div>
                        </div>
                        <a href="#" class="btn-pdf-download" id="btn-descargar-pdf" target="_blank">
                            <span>📄</span> Descargar Informe PDF
                        </a>
                    </div>

                    <!-- SUB-TABS DEL PERFIL -->
                    <div class="profile-nav">
                        <button class="p-tab-btn active" onclick="cambiarSubTab('general')">📋 Información General</button>
                        <button class="p-tab-btn" onclick="cambiarSubTab('integrantes')" id="tab-lbl-inv">👥 Integrantes (0)</button>
                        <button class="p-tab-btn" onclick="cambiarSubTab('productos')" id="tab-lbl-prod">📚 Productos (0)</button>
                        <button class="p-tab-btn" onclick="cambiarSubTab('modelo2024')">🎯 Balance MinCiencias 2024 & IPP</button>
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
                            <div class="data-table-container">
                                <table class="peai-table" id="tabla-perfil-inv">
                                    <thead>
                                        <tr>
                                            <th>Documento / CvLAC</th>
                                            <th>Nombre Completo</th>
                                            <th>Escalafón MinCiencias</th>
                                            <th>Formación Académica</th>
                                            <th>Estado</th>
                                        </tr>
                                    </thead>
                                    <tbody></tbody>
                                </table>
                            </div>
                        </div>

                        <!-- SUB-TAB: PRODUCTOS -->
                        <div id="subtab-productos" class="profile-section">
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
                                        </tr>
                                    </thead>
                                    <tbody></tbody>
                                </table>
                            </div>
                        </div>

                        <!-- SUB-TAB: MODELO 2024 -->
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
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem; background:var(--bg-card); padding:0.8rem 1.2rem; border-radius:10px; border:1px solid var(--card-border);">
                <div>
                    <h3 style="font-size:1.05rem;">Filtro por Ventana de Observación (Requisito 10)</h3>
                    <p style="font-size:0.75rem; color:var(--text-muted);">Calcule las métricas institucionales según el marco de años de la convocatoria</p>
                </div>
                <div style="display:flex; gap:0.4rem;">
                    <button class="tag-btn active" id="btn-win-0" onclick="cambiarVentanaObservacion(0)">Todos los Años</button>
                    <button class="tag-btn" id="btn-win-5" onclick="cambiarVentanaObservacion(5)">Últimos 5 Años (2021-2026)</button>
                    <button class="tag-btn" id="btn-win-2" onclick="cambiarVentanaObservacion(2)">Últimos 2 Años (2024-2026)</button>
                </div>
            </div>

            <div class="dashboard-container">
                <div class="chart-box">
                    <div class="chart-box-title">
                        <span>📊 Distribución por Año de Publicación</span>
                        <span style="font-size:0.75rem; color:#38bdf8;">Cronología</span>
                    </div>
                    <div id="chart-anios-container" style="max-height: 280px; overflow-y:auto;"></div>
                </div>

                <div class="chart-box">
                    <div class="chart-box-title">
                        <span>🏛️ Grupos por Categoría MinCiencias</span>
                        <span style="font-size:0.75rem; color:#10b981;">Escalafón Oficial</span>
                    </div>
                    <div id="chart-cat-container"></div>
                </div>

                <div class="chart-box">
                    <div class="chart-box-title">
                        <span>🎯 Modelo 2024: Las 5 Macro-Familias</span>
                        <span style="font-size:0.75rem; color:#f59e0b;">Tipología CTeI</span>
                    </div>
                    <div id="chart-familias-container"></div>
                </div>

                <div class="chart-box">
                    <div class="chart-box-title">
                        <span>✅ Aval Institucional / Validación MinCiencias</span>
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
                    <span>🏢 i. Resumen por Grupo de Investigación (12.c.i)</span>
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
                    <span>👨‍🔬 ii. Escalafón de Investigadores (12.c.ii)</span>
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
    </main>

    <!-- FOOTER -->
    <footer>
        PEA-i &bull; Programa Estadístico de Análisis de Investigación &bull; Universidad Popular del Cesar (UPC) &bull; C++17 Core Engine &bull; MinCiencias Convocatoria 957
    </footer>

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
            } else if (vista === "tablas") {
                document.querySelectorAll(".tab-btn")[2].classList.add("active");
                document.getElementById("view-tablas").classList.add("active");
                renderizarTablasEntidad();
            }
        }

        // CAMBIO DE SUB-TABS DEL PERFIL
        function cambiarSubTab(subtab) {
            document.querySelectorAll(".p-tab-btn").forEach(b => b.classList.remove("active"));
            document.querySelectorAll(".profile-section").forEach(s => s.classList.remove("active"));

            const subMap = {
                "general": { btn: 0, sec: "subtab-general" },
                "integrantes": { btn: 1, sec: "subtab-integrantes" },
                "productos": { btn: 2, sec: "subtab-productos" },
                "modelo2024": { btn: 3, sec: "subtab-modelo2024" }
            };
            const item = subMap[subtab] || subMap["general"];
            document.querySelectorAll(".p-tab-btn")[item.btn].classList.add("active");
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
                        <span>👤 ${(g.lider || "Investigador UPC").substring(0, 22)}</span>
                        <span>👥 ${numInv} &bull; 📚 ${numProd}</span>
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
            document.getElementById("tab-lbl-inv").textContent = `👥 Integrantes (${nInv})`;
            document.getElementById("tab-lbl-prod").textContent = `📚 Productos (${nProd})`;

            // TABLA INTEGRANTES
            const tbodyInv = document.querySelector("#tabla-perfil-inv tbody");
            tbodyInv.innerHTML = "";
            (g.investigadores || []).forEach(inv => {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td><code style="color:#38bdf8;">${inv.documento}</code></td>
                    <td><b>${inv.nombre}</b></td>
                    <td><span class="badge-cat">${inv.categoria || "Junior"}</span></td>
                    <td>${inv.formacion || "Maestría / Doctorado CTeI"}</td>
                    <td>${inv.activo ? "<span style='color:#10b981;'>● Activo</span>" : "<span style='color:#94a3b8;'>Inactivo</span>"}</td>
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
                tr.innerHTML = `
                    <td><b>${p.anio}</b></td>
                    <td><span class="badge-cat" style="background:#0284c7; color:#fff;">${clas.fam}</span></td>
                    <td><code>${clas.cod}</code></td>
                    <td style="max-width:380px;">${p.titulo}</td>
                    <td>${p.tipo}</td>
                    <td>${p.validado ? "<span style='color:#10b981; font-weight:700;'>Avalado</span>" : "<span style='color:#f59e0b;'>En Revisión</span>"}</td>
                    <td style="color:var(--upc-green-light); font-weight:700;">${pts} pts</td>
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

        // RENDERIZAR DASHBOARD ANALÍTICO (12.B)
        function cambiarVentanaObservacion(win) {
            ventanaAnios = win;
            document.getElementById("btn-win-0").classList.toggle("active", win === 0);
            document.getElementById("btn-win-5").classList.toggle("active", win === 5);
            document.getElementById("btn-win-2").classList.toggle("active", win === 2);
            renderizarDashboard();
        }

        function renderizarDashboard() {
            const anioLimite = ventanaAnios > 0 ? (2026 - ventanaAnios) : 0;

            // 1. Cronología por año
            let aniosCount = {};
            // 2. Familias 2024
            let famCount = { "GNC": 0, "DTI": 0, "ASC": 0, "DPC": 0, "FRH": 0 };
            // 3. Avales
            let avalCount = { "Avalados": 0, "En Revisión": 0 };

            gruposData.forEach(g => {
                (g.productos || []).forEach(p => {
                    if (p.anio >= anioLimite) {
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
                    <td><a href="../reportes/Informe_GrupLAC_${g.codigo}.pdf" target="_blank" style="background:#006837; color:#fff; padding:3px 7px; border-radius:4px; font-size:0.75rem; text-decoration:none; font-weight:700;">📄 Descargar PDF</a></td>
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

        // Ejecutar al cargar el DOM
        window.addEventListener("DOMContentLoaded", inicializarPortal);
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
