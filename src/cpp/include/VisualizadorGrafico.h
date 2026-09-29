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
// PEA-i: VISUALIZADOR GRÁFICO INTERACTIVO DEL HIPERCUBO 3D Y DASHBOARD
// Universidad Popular del Cesar — Estructura de Datos (2026-I)
// =====================================================================
// Arquitectura Zero-Dependencies:
// - Genera un archivo HTML5 autónomo con Canvas 3D isométrico/orbital.
// - Renderiza los 3 ejes ortogonales:
//     • Eje X: Grupos de Investigación (Verde Institucional UPC #006837)
//     • Eje Y: Investigadores Autores (Rojo Institucional UPC #ED1C24 / Cyan)
//     • Eje Z: Productos Científicos y Línea Temporal (Ámbar / Púrpura)
// - Control de cámara 3D: Rotación orbital por arrastre y Zoom con rueda.
// - Explorador jerárquico por tarjetas y vista de tablas por entidad (12.c).
// - Dashboard estadístico con histograma temporal y filtros por ventana (Punto 10).
// - Abre automáticamente con el navegador del sistema operativo.
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
    <title>PEA-i UPC — Visualizador 3D del Hipercubo y Dashboard</title>
    <style>
        :root {
            --upc-green: #006837;
            --upc-green-light: #10b981;
            --upc-red: #ED1C24;
            --bg-dark: #080c16;
            --bg-card: #0f172a;
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
            overflow-x: hidden;
        }

        /* HEADER INSTITUCIONAL */
        header {
            background: linear-gradient(135deg, #022c19 0%, #080c16 60%, #1e1014 100%);
            border-bottom: 2px solid var(--upc-green);
            padding: 0.8rem 2rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            position: sticky;
            top: 0;
            z-index: 100;
            backdrop-filter: blur(8px);
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
        .brand-text h1 { font-size: 1.25rem; font-weight: 800; letter-spacing: -0.5px; }
        .brand-text p { font-size: 0.78rem; color: var(--text-muted); }

        .nav-tabs { display: flex; gap: 0.4rem; background: rgba(15, 23, 42, 0.8); padding: 0.3rem; border-radius: 8px; border: 1px solid var(--card-border); }
        .tab-btn {
            background: transparent; border: none; color: var(--text-muted);
            padding: 0.45rem 1rem; border-radius: 6px; cursor: pointer;
            font-weight: 600; font-size: 0.82rem; transition: all 0.2s ease;
        }
        .tab-btn:hover { color: #fff; background: rgba(255,255,255,0.06); }
        .tab-btn.active { background: var(--upc-green); color: #fff; box-shadow: 0 2px 10px rgba(16, 185, 129, 0.4); }

        /* CONTENIDO PRINCIPAL */
        main { flex: 1; padding: 1.2rem 2rem; display: flex; flex-direction: column; gap: 1rem; }

        /* TOOLBAR SUPERIOR */
        .toolbar {
            display: grid;
            grid-template-columns: auto 1fr auto;
            gap: 1.5rem;
            align-items: center;
            background: var(--bg-card);
            padding: 0.8rem 1.4rem;
            border-radius: 12px;
            border: 1px solid var(--card-border);
        }
        .stats-summary { display: flex; gap: 1.8rem; }
        .stat-item { display: flex; flex-direction: column; }
        .stat-label { font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px; }
        .stat-val { font-size: 1.35rem; font-weight: 800; }
        .stat-val.gr { color: var(--upc-green-light); }
        .stat-val.bl { color: var(--accent-blue); }
        .stat-val.am { color: var(--accent-amber); }

        .filter-window { display: flex; align-items: center; gap: 0.5rem; justify-content: center; }
        .filter-btn {
            background: rgba(255,255,255,0.04);
            border: 1px solid var(--card-border);
            color: var(--text-muted);
            padding: 0.35rem 0.8rem;
            border-radius: 6px; cursor: pointer;
            font-size: 0.8rem; font-weight: 600; transition: all 0.2s;
        }
        .filter-btn:hover { color: #fff; border-color: #64748b; }
        .filter-btn.active { background: var(--upc-green); color: #fff; border-color: var(--upc-green-light); }

        .search-box { position: relative; }
        .search-box input {
            background: #080c16; border: 1px solid var(--card-border);
            color: #fff; padding: 0.45rem 1rem 0.45rem 2.2rem;
            border-radius: 8px; font-size: 0.82rem; outline: none; width: 260px;
            transition: border-color 0.2s;
        }
        .search-box input:focus { border-color: var(--upc-green-light); }
        .search-icon { position: absolute; left: 0.75rem; top: 50%; transform: translateY(-50%); color: var(--text-muted); font-size: 0.85rem; }

        /* VISTAS */
        .view-panel { display: none; }
        .view-panel.active { display: block; }

        /* VISTA 1: HIPERCUBO 3D Y EXPLORADOR */
        .hipercubo-subnav {
            display: flex; gap: 0.8rem; align-items: center; justify-content: space-between;
            margin-bottom: 0.8rem;
        }
        .subnav-btn-group { display: flex; gap: 0.4rem; }
        .sub-btn {
            background: var(--bg-card); border: 1px solid var(--card-border);
            color: var(--text-muted); padding: 0.35rem 0.9rem; border-radius: 6px;
            font-size: 0.8rem; font-weight: 600; cursor: pointer;
        }
        .sub-btn.active { background: #1e293b; color: #fff; border-color: #38bdf8; }

        .hipercubo-layout {
            display: grid;
            grid-template-columns: 1fr 340px;
            gap: 1.2rem;
            height: calc(100vh - 220px);
            min-height: 540px;
        }

        /* LIENZO 3D (CANVAS) */
        .canvas-container {
            background: radial-gradient(circle at 50% 50%, #111827 0%, #05070e 100%);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            position: relative;
            overflow: hidden;
            display: flex; flex-direction: column;
        }
        #canvas3d { width: 100%; height: 100%; cursor: grab; }
        #canvas3d:active { cursor: grabbing; }

        .canvas-hud {
            position: absolute; bottom: 1rem; left: 1rem;
            background: rgba(15, 23, 42, 0.85); backdrop-filter: blur(6px);
            border: 1px solid var(--card-border); border-radius: 8px;
            padding: 0.6rem 0.9rem; font-size: 0.75rem; color: var(--text-muted);
            pointer-events: none;
        }
        .canvas-controls {
            position: absolute; top: 1rem; right: 1rem;
            display: flex; gap: 0.4rem;
        }
        .hud-btn {
            background: rgba(15, 23, 42, 0.9); border: 1px solid var(--card-border);
            color: #fff; padding: 0.4rem 0.7rem; border-radius: 6px; font-size: 0.75rem;
            cursor: pointer; transition: background 0.2s;
        }
        .hud-btn:hover { background: #1e293b; }

        /* VISTA ARQUITECTURAL / JERÁRQUICA */
        .hierarchy-container {
            display: grid;
            grid-template-columns: 300px 1fr;
            gap: 1rem;
            height: 100%;
            overflow: hidden;
        }
        .investigators-list-col {
            background: var(--bg-card);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            overflow-y: auto;
            padding: 0.8rem;
            display: flex; flex-direction: column; gap: 0.5rem;
        }
        .inv-item-card {
            background: #080c16;
            border: 1px solid var(--card-border);
            border-radius: 8px;
            padding: 0.7rem 0.9rem;
            cursor: pointer;
            transition: all 0.2s;
        }
        .inv-item-card:hover { border-color: var(--accent-blue); background: #0f172a; }
        .inv-item-card.active { border-color: var(--upc-green-light); background: #022c19; }
        .inv-item-name { font-weight: 700; font-size: 0.85rem; margin-bottom: 0.2rem; }
        .inv-item-meta { font-size: 0.72rem; color: var(--text-muted); display: flex; justify-content: space-between; }

        .products-grid-col {
            background: var(--bg-card);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            padding: 1rem;
            overflow-y: auto;
            display: flex; flex-direction: column; gap: 0.8rem;
        }
        .products-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 0.8rem;
        }
        .prod-card {
            background: #080c16; border: 1px solid var(--card-border);
            border-radius: 8px; padding: 0.8rem; cursor: pointer;
            display: flex; flex-direction: column; justify-content: space-between;
            transition: all 0.2s;
        }
        .prod-card:hover { border-color: var(--accent-amber); transform: translateY(-2px); }
        .prod-card-title { font-weight: 600; font-size: 0.82rem; line-height: 1.3; margin-bottom: 0.6rem; color: #fff; }
        .prod-card-tags { display: flex; flex-wrap: wrap; gap: 0.4rem; font-size: 0.7rem; }

        /* INSPECTOR LATERAL */
        .inspector-panel {
            background: var(--bg-card);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            padding: 1.2rem;
            display: flex; flex-direction: column; gap: 1rem;
            overflow-y: auto;
        }
        .inspector-title { font-size: 1rem; font-weight: 700; border-bottom: 1px solid var(--card-border); padding-bottom: 0.6rem; }
        .meta-field { display: flex; flex-direction: column; gap: 0.2rem; margin-bottom: 0.7rem; }
        .meta-k { font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase; font-weight: 700; }
        .meta-v { font-size: 0.85rem; color: #fff; word-break: break-word; }
        .ptr-box {
            background: #080c16; border: 1px solid #1e293b; border-radius: 6px;
            padding: 0.5rem 0.7rem; font-family: monospace; font-size: 0.75rem;
            color: var(--upc-green-light); margin-top: 0.4rem;
        }

        /* PILLS Y BADGES */
        .pill { padding: 0.2rem 0.5rem; border-radius: 4px; font-weight: 700; font-size: 0.68rem; text-transform: uppercase; }
        .pill-a1 { background: #064e3b; color: #6ee7b7; border: 1px solid #10b981; }
        .pill-a { background: #1e3a8a; color: #93c5fd; border: 1px solid #3b82f6; }
        .pill-b { background: #78350f; color: #fde68a; border: 1px solid #f59e0b; }
        .pill-c { background: #581c87; color: #e9d5ff; border: 1px solid #a855f7; }
        .pill-val { background: #022c19; color: #34d399; }
        .pill-noval { background: #3f1d1d; color: #f87171; }

        /* DASHBOARD GRID */
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
            gap: 1.2rem;
        }
        .chart-card {
            background: var(--bg-card);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            padding: 1.2rem;
            display: flex; flex-direction: column; gap: 1rem;
        }
        .chart-header { display: flex; justify-content: space-between; align-items: center; }
        .chart-header h3 { font-size: 0.95rem; font-weight: 700; }
        .bar-container { display: flex; flex-direction: column; gap: 0.6rem; }
        .bar-row { display: flex; flex-direction: column; gap: 0.2rem; }
        .bar-info { display: flex; justify-content: space-between; font-size: 0.75rem; color: var(--text-muted); }
        .bar-track { height: 10px; background: #080c16; border-radius: 5px; overflow: hidden; }
        .bar-fill { height: 100%; border-radius: 5px; transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1); }

        /* TABLAS POR ENTIDAD */
        .data-table {
            width: 100%; border-collapse: collapse; font-size: 0.8rem;
        }
        .data-table th, .data-table td {
            padding: 0.6rem 0.8rem; text-align: left; border-bottom: 1px solid var(--card-border);
        }
        .data-table th { background: #080c16; color: var(--text-muted); font-size: 0.72rem; text-transform: uppercase; }
        .data-table tr:hover { background: rgba(255,255,255,0.03); cursor: pointer; }

        .pagination-bar {
            display: flex; justify-content: space-between; align-items: center;
            padding-top: 0.8rem; font-size: 0.8rem; color: var(--text-muted);
        }
        .page-btns { display: flex; gap: 0.4rem; }

        footer {
            border-top: 1px solid var(--card-border); padding: 0.8rem 2rem;
            font-size: 0.75rem; color: var(--text-muted); text-align: center;
        }
    </style>
</head>
<body>
    <header>
        <div class="brand-box">
            <div class="brand-logo">UPC</div>
            <div class="brand-text">
                <h1>PEA-i &bull; Analítica de Investigación MinCiencias</h1>
                <p>Hipercubo Ortogonal 3D &bull; Estructura de Datos &bull; Ing. Adith Pérez</p>
            </div>
        </div>

        <nav class="nav-tabs">
            <button class="tab-btn active" onclick="cambiarVista('hipercubo')">📦 Hipercubo 3D</button>
            <button class="tab-btn" onclick="cambiarVista('dashboard')">📊 Dashboard & Métricas</button>
            <button class="tab-btn" onclick="cambiarVista('tablas')">📑 Vistas por Entidad (12.c)</button>
        </nav>
    </header>

    <main>
        <!-- BARRA SUPERIOR DE FILTROS & ESTADÍSTICAS -->
        <section class="toolbar">
            <div class="stats-summary">
                <div class="stat-item">
                    <span class="stat-label">Grupos (Eje X)</span>
                    <span class="stat-val gr" id="lbl-total-grupos">0</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Investigadores (Eje Y)</span>
                    <span class="stat-val bl" id="lbl-total-inv">0</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Productos (Eje Z)</span>
                    <span class="stat-val am" id="lbl-total-prod">0</span>
                </div>
            </div>

            <!-- FILTRO DE VENTANA DE OBSERVACIÓN (PUNTO 10) -->
            <div class="filter-window">
                <span class="stat-label" style="margin-right: 0.4rem;">Ventana de Años:</span>
                <button class="filter-btn active" onclick="aplicarFiltroVentana(0, this)">Todos</button>
                <button class="filter-btn" onclick="aplicarFiltroVentana(2, this)">Últimos 2 años</button>
                <button class="filter-btn" onclick="aplicarFiltroVentana(5, this)">Últimos 5 años</button>
            </div>

            <div class="search-box">
                <span class="search-icon">🔍</span>
                <input type="text" id="input-busqueda" placeholder="Buscar por título, autor o ID..." oninput="filtrarPorTexto(this.value)">
            </div>
        </section>

        <!-- VISTA 1: HIPERCUBO ORTOGONAL -->
        <section id="view-hipercubo" class="view-panel active">
            <div class="hipercubo-subnav">
                <div class="subnav-btn-group">
                    <button class="sub-btn active" id="btn-sub-3d" onclick="cambiarSubvistaHipercubo('3d')">🌐 Vista Espacial 3D (Canvas)</button>
                    <button class="sub-btn" id="btn-sub-hier" onclick="cambiarSubvistaHipercubo('hier')">🗂️ Explorador de Nodos & Mosaico</button>
                </div>
                <span style="font-size: 0.75rem; color: var(--text-muted);">Arrastre el ratón para rotar el hipercubo en 3D &bull; Rueda para Zoom</span>
            </div>

            <div class="hipercubo-layout">
                <!-- CONTENEDOR 3D -->
                <div class="canvas-container" id="subview-3d">
                    <canvas id="canvas3d"></canvas>
                    <div class="canvas-hud">
                        <div><b>Ejes Ortogonales en RAM:</b></div>
                        <div><span style="color:var(--upc-green-light)">■ Eje X:</span> Grupos (Horizontal)</div>
                        <div><span style="color:var(--accent-blue)">■ Eje Y:</span> Investigadores (Vertical)</div>
                        <div><span style="color:var(--accent-amber)">■ Eje Z:</span> Productos & Línea Temporal</div>
                    </div>
                    <div class="canvas-controls">
                        <button class="hud-btn" onclick="reiniciarCamara3D()">🔄 Reset Vista</button>
                    </div>
                </div>

                <!-- CONTENEDOR JERÁRQUICO -->
                <div class="hierarchy-container" id="subview-hier" style="display: none;">
                    <div class="investigators-list-col" id="col-investigadores">
                        <!-- Investigadores inyectados dinámicamente -->
                    </div>
                    <div class="products-grid-col">
                        <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid var(--card-border); padding-bottom:0.5rem;">
                            <h3 id="hier-prod-header" style="font-size: 0.95rem; font-weight: 700;">Producción Científica</h3>
                            <span id="hier-prod-count" style="font-size: 0.8rem; color: var(--accent-amber);">0 productos</span>
                        </div>
                        <div class="products-grid" id="contenedor-mosaico">
                            <!-- Productos inyectados dinámicamente -->
                        </div>
                    </div>
                </div>

                <!-- INSPECTOR LATERAL DE DETALLES -->
                <aside class="inspector-panel" id="inspector">
                    <div class="inspector-title" id="insp-titulo">Inspector de Memoria</div>
                    <div id="insp-contenido">
                        <p style="color: var(--text-muted); font-size: 0.85rem; line-height: 1.4;">
                            Haga clic sobre cualquier nodo en el lienzo 3D o en el explorador para inspeccionar sus punteros ortogonales en memoria RAM.
                        </p>
                    </div>
                </aside>
            </div>
        </section>

        <!-- VISTA 2: DASHBOARD ESTADÍSTICO (PUNTO 12.B) -->
        <section id="view-dashboard" class="view-panel">
            <div class="dashboard-grid">
                <!-- GRÁFICO 1: CATEGORÍAS MINCIENCIAS -->
                <div class="chart-card">
                    <div class="chart-header">
                        <h3>Categorías MinCiencias (A1, A, B, C)</h3>
                        <span class="pill pill-a1">Calidad</span>
                    </div>
                    <div class="bar-container" id="chart-categorias"></div>
                </div>

                <!-- GRÁFICO 2: HISTOGRAMA POR AÑO -->
                <div class="chart-card">
                    <div class="chart-header">
                        <h3>Producción Científica por Año (Histograma)</h3>
                        <span class="pill pill-b">Línea Temporal</span>
                    </div>
                    <div class="bar-container" id="chart-anios"></div>
                </div>

                <!-- GRÁFICO 3: AVAL MINCIENCIAS -->
                <div class="chart-card">
                    <div class="chart-header">
                        <h3>Aval Institucional / MinCiencias</h3>
                        <span class="pill pill-val">Auditoría</span>
                    </div>
                    <div class="bar-container" id="chart-aval"></div>
                </div>

                <!-- GRÁFICO 4: TIPOS DE PRODUCTO -->
                <div class="chart-card">
                    <div class="chart-header">
                        <h3>Tipología de Obras Registradas</h3>
                        <span class="pill pill-a">Tipología</span>
                    </div>
                    <div class="bar-container" id="chart-tipos"></div>
                </div>
            </div>
        </section>

        <!-- VISTA 3: VISTAS POR ENTIDAD (PUNTO 12.C) -->
        <section id="view-tablas" class="view-panel">
            <div class="chart-card" style="margin-bottom: 1.2rem;">
                <h3 style="margin-bottom: 0.6rem;">i. Resumen por Grupo de Investigación (12.c.i)</h3>
                <table class="data-table" id="tabla-grupos">
                    <thead>
                        <tr>
                            <th>Código</th>
                            <th>Nombre Oficial</th>
                            <th>Clasif.</th>
                            <th>Líder</th>
                            <th>Investigadores</th>
                            <th>Total Obras</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
            </div>

            <div class="chart-card" style="margin-bottom: 1.2rem;">
                <h3 style="margin-bottom: 0.6rem;">ii. Resumen por Investigador Autor (12.c.ii)</h3>
                <table class="data-table" id="tabla-investigadores">
                    <thead>
                        <tr>
                            <th>Documento</th>
                            <th>Nombre Completo</th>
                            <th>Categoría</th>
                            <th>Formación</th>
                            <th>Obras Registradas</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
            </div>

            <div class="chart-card">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.6rem;">
                    <h3>iii. Listado Exhaustivo de Productos Científicos (12.c.iii)</h3>
                    <span id="tab-prod-count" style="font-size:0.8rem; color:var(--text-muted);">Paginado</span>
                </div>
                <table class="data-table" id="tabla-productos">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Tipo</th>
                            <th>Título de la Publicación</th>
                            <th>Año</th>
                            <th>Cat.</th>
                            <th>Aval</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
                <div class="pagination-bar">
                    <span id="lbl-pag-prod">Página 1 de 1</span>
                    <div class="page-btns">
                        <button class="filter-btn" onclick="paginarTablaProd(-1)">◀ Anterior</button>
                        <button class="filter-btn" onclick="paginarTablaProd(1)">Siguiente ▶</button>
                    </div>
                </div>
            </div>
        </section>
    </main>

    <footer>
        PEA-i &bull; Programa Estadístico de Análisis de Investigación &bull; Universidad Popular del Cesar &bull; C++17 Multi-Engine &bull; MinCiencias SCIENTI
    </footer>

    <!-- SERIALIZACIÓN DE DATOS DESDE C++ -->
    <script>
        const DATOS_HIPERCUBO = )HTML";

        out << datosJSON;

        out << R"HTML(;

        // ESTADO GLOBAL
        let ventanaAnios = 0; // 0: Todos, 2: Últimos 2, 5: Últimos 5
        let anioActual = 2026;
        let filtroTexto = "";
        let invSeleccionadoDoc = null;
        let subvistaActual = '3d';
        let pagProdActual = 0;
        const PRODS_POR_PAG = 15;

        // CAMBIO DE PESTAÑAS PRINCIPALES
        function cambiarVista(vista) {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.view-panel').forEach(p => p.classList.remove('active'));

            if (vista === 'hipercubo') {
                document.querySelectorAll('.tab-btn')[0].classList.add('active');
                document.getElementById('view-hipercubo').classList.add('active');
                if (subvistaActual === '3d') dibujarEscena3D();
            } else if (vista === 'dashboard') {
                document.querySelectorAll('.tab-btn')[1].classList.add('active');
                document.getElementById('view-dashboard').classList.add('active');
                renderizarDashboard();
            } else {
                document.querySelectorAll('.tab-btn')[2].classList.add('active');
                document.getElementById('view-tablas').classList.add('active');
                renderizarTablas();
            }
        }

        function cambiarSubvistaHipercubo(sub) {
            subvistaActual = sub;
            document.getElementById('btn-sub-3d').classList.toggle('active', sub === '3d');
            document.getElementById('btn-sub-hier').classList.toggle('active', sub === 'hier');
            document.getElementById('subview-3d').style.display = (sub === '3d') ? 'flex' : 'none';
            document.getElementById('subview-hier').style.display = (sub === 'hier') ? 'grid' : 'none';

            if (sub === '3d') {
                dibujarEscena3D();
            } else {
                renderizarExploradorJerarquico();
            }
        }

        function aplicarFiltroVentana(anios, btn) {
            ventanaAnios = anios;
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            if (btn) btn.classList.add('active');
            renderizarTodo();
        }

        function filtrarPorTexto(txt) {
            filtroTexto = txt.toLowerCase().trim();
            pagProdActual = 0;
            renderizarTodo();
        }

        function productoPasaVentana(p) {
            if (ventanaAnios === 0) return true;
            return p.anio >= (anioActual - ventanaAnios + 1) && p.anio <= anioActual;
        }

        function renderizarTodo() {
            actualizarTotales();
            if (subvistaActual === '3d') dibujarEscena3D();
            renderizarExploradorJerarquico();
            renderizarDashboard();
            renderizarTablas();
        }

        function actualizarTotales() {
            let totalG = DATOS_HIPERCUBO.grupos.length;
            let totalI = 0;
            let totalP = 0;

            DATOS_HIPERCUBO.grupos.forEach(g => {
                totalI += g.investigadores.length;
                g.productos.forEach(p => {
                    if (productoPasaVentana(p)) totalP++;
                });
            });

            document.getElementById('lbl-total-grupos').innerText = totalG;
            document.getElementById('lbl-total-inv').innerText = totalI;
            document.getElementById('lbl-total-prod').innerText = totalP;
        }

        // =====================================================================
        // MOTOR GRÁFICO 3D EN CANVAS HTML5 (HIPERCUBO ORTOGONAL)
        // =====================================================================
        const canvas = document.getElementById('canvas3d');
        const ctx = canvas.getContext('2d');

        let rotX = 0.45;
        let rotY = -0.55;
        let zoom = 1.0;
        let isDragging = false;
        let lastMouseX = 0, lastMouseY = 0;
        let nodos3D = []; // Para detección de clic

        function redimensionarCanvas() {
            const rect = canvas.parentElement.getBoundingClientRect();
            canvas.width = rect.width;
            canvas.height = rect.height;
            dibujarEscena3D();
        }
        window.addEventListener('resize', redimensionarCanvas);

        canvas.addEventListener('mousedown', (e) => {
            isDragging = true;
            lastMouseX = e.clientX;
            lastMouseY = e.clientY;
        });
        window.addEventListener('mouseup', () => isDragging = false);
        window.addEventListener('mousemove', (e) => {
            if (!isDragging) return;
            const dx = e.clientX - lastMouseX;
            const dy = e.clientY - lastMouseY;
            rotY += dx * 0.008;
            rotX += dy * 0.008;
            lastMouseX = e.clientX;
            lastMouseY = e.clientY;
            dibujarEscena3D();
        });

        canvas.addEventListener('wheel', (e) => {
            e.preventDefault();
            zoom += e.deltaY * -0.001;
            zoom = Math.max(0.4, Math.min(2.5, zoom));
            dibujarEscena3D();
        });

        canvas.addEventListener('click', (e) => {
            const rect = canvas.getBoundingClientRect();
            const mouseX = e.clientX - rect.left;
            const mouseY = e.clientY - rect.top;

            let nodoSeleccionado = null;
            let minDist = 18;

            nodos3D.forEach(n => {
                const dist = Math.hypot(n.screenX - mouseX, n.screenY - mouseY);
                if (dist < minDist) {
                    minDist = dist;
                    nodoSeleccionado = n;
                }
            });

            if (nodoSeleccionado) {
                if (nodoSeleccionado.tipo === 'G') mostrarDetalleGrupo(nodoSeleccionado.ref);
                else if (nodoSeleccionado.tipo === 'I') mostrarDetalleInvestigador(nodoSeleccionado.ref, nodoSeleccionado.grupo);
                else if (nodoSeleccionado.tipo === 'P') mostrarDetalleProducto(nodoSeleccionado.ref, nodoSeleccionado.grupo);
            }
        });

        function reiniciarCamara3D() {
            rotX = 0.45;
            rotY = -0.55;
            zoom = 1.0;
            dibujarEscena3D();
        }

        // Proyección 3D a 2D
        function proyectar3D(x, y, z, cx, cy) {
            // Rotación Y
            let x1 = x * Math.cos(rotY) + z * Math.sin(rotY);
            let z1 = -x * Math.sin(rotY) + z * Math.cos(rotY);

            // Rotación X
            let y2 = y * Math.cos(rotX) - z1 * Math.sin(rotX);
            let z2 = y * Math.sin(rotX) + z1 * Math.cos(rotX);

            const scale = 280 * zoom / (z2 + 650);
            return {
                x: cx + x1 * scale,
                y: cy + y2 * scale,
                z: z2,
                visible: (z2 + 650) > 10
            };
        }

        function dibujarEscena3D() {
            if (!canvas.width || !canvas.height) return;
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            nodos3D = [];

            const cx = canvas.width / 2;
            const cy = canvas.height / 2;

            // 1. Dibujar Ejes Coordenados del Hipercubo
            const orig = proyectar3D(0, 0, 0, cx, cy);
            const pX = proyectar3D(220, 0, 0, cx, cy);
            const pY = proyectar3D(0, 220, 0, cx, cy);
            const pZ = proyectar3D(0, 0, 220, cx, cy);

            ctx.lineWidth = 1.5;
            // Eje X (Grupos)
            ctx.strokeStyle = '#10b981';
            ctx.beginPath(); ctx.moveTo(orig.x, orig.y); ctx.lineTo(pX.x, pX.y); ctx.stroke();
            ctx.fillStyle = '#10b981'; ctx.fillText('Eje X: Grupos', pX.x + 5, pX.y);

            // Eje Y (Investigadores)
            ctx.strokeStyle = '#38bdf8';
            ctx.beginPath(); ctx.moveTo(orig.x, orig.y); ctx.lineTo(pY.x, pY.y); ctx.stroke();
            ctx.fillStyle = '#38bdf8'; ctx.fillText('Eje Y: Investigadores', pY.x + 5, pY.y);

            // Eje Z (Productos)
            ctx.strokeStyle = '#f59e0b';
            ctx.beginPath(); ctx.moveTo(orig.x, orig.y); ctx.lineTo(pZ.x, pZ.y); ctx.stroke();
            ctx.fillStyle = '#f59e0b'; ctx.fillText('Eje Z: Obras & Años', pZ.x + 5, pZ.y);

            // 2. Posicionar y Renderizar Nodos de la Multilista
            DATOS_HIPERCUBO.grupos.forEach((g, idxG) => {
                const posX = -120 + idxG * 180;
                const posG = proyectar3D(posX, -120, -100, cx, cy);

                // Nodo Grupo (Verde UPC)
                ctx.fillStyle = '#006837';
                ctx.strokeStyle = '#10b981';
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.arc(posG.x, posG.y, 14 * zoom, 0, Math.PI * 2);
                ctx.fill(); ctx.stroke();
                ctx.fillStyle = '#fff';
                ctx.font = 'bold 11px sans-serif';
                ctx.fillText(g.codigo, posG.x - 18, posG.y - 18);

                nodos3D.push({ screenX: posG.x, screenY: posG.y, tipo: 'G', ref: g });

                // Investigadores del Grupo (Eje Y)
                g.investigadores.forEach((inv, idxI) => {
                    const posY = -60 + idxI * 32;
                    const posI = proyectar3D(posX, posY, -40, cx, cy);

                    // Línea ortogonal Grupo -> Investigador
                    ctx.strokeStyle = 'rgba(56, 189, 248, 0.4)';
                    ctx.lineWidth = 1;
                    ctx.beginPath(); ctx.moveTo(posG.x, posG.y); ctx.lineTo(posI.x, posI.y); ctx.stroke();

                    // Nodo Investigador
                    ctx.fillStyle = '#0284c7';
                    ctx.beginPath();
                    ctx.arc(posI.x, posI.y, 8 * zoom, 0, Math.PI * 2);
                    ctx.fill();

                    nodos3D.push({ screenX: posI.x, screenY: posI.y, tipo: 'I', ref: inv, grupo: g });

                    // Productos de este Investigador (Eje Z)
                    const prodsAutor = g.productos.filter(p => p.id_investigador === inv.documento && productoPasaVentana(p));
                    prodsAutor.slice(0, 15).forEach((p, idxP) => {
                        const posZ = 0 + idxP * 24;
                        const posP = proyectar3D(posX + (idxP % 2 ? 15 : -15), posY, posZ, cx, cy);

                        // Enlace Ortogonal Investigador -> Producto (Z)
                        ctx.strokeStyle = 'rgba(245, 158, 11, 0.3)';
                        ctx.beginPath(); ctx.moveTo(posI.x, posI.y); ctx.lineTo(posP.x, posP.y); ctx.stroke();

                        // Nodo Producto
                        ctx.fillStyle = p.validado ? '#f59e0b' : '#ef4444';
                        ctx.beginPath();
                        ctx.arc(posP.x, posP.y, 4 * zoom, 0, Math.PI * 2);
                        ctx.fill();

                        nodos3D.push({ screenX: posP.x, screenY: posP.y, tipo: 'P', ref: p, grupo: g });
                    });
                });
            });
        }

        // =====================================================================
        // EXPLORADOR JERÁRQUICO (SUBVISTA 2 DEL HIPERCUBO)
        // =====================================================================
        function renderizarExploradorJerarquico() {
            const colInv = document.getElementById('col-investigadores');
            const contMosaico = document.getElementById('contenedor-mosaico');
            colInv.innerHTML = '';
            contMosaico.innerHTML = '';

            let todosLosProds = [];

            DATOS_HIPERCUBO.grupos.forEach(g => {
                g.productos.forEach(p => {
                    if (productoPasaVentana(p)) todosLosProds.push({ prod: p, grupo: g });
                });

                // Header de Grupo
                const gHeader = document.createElement('div');
                gHeader.style.padding = '0.4rem 0';
                gHeader.style.fontWeight = '800';
                gHeader.style.fontSize = '0.8rem';
                gHeader.style.color = 'var(--upc-green-light)';
                gHeader.innerText = `GRUPO: ${g.codigo} (${g.productos.length} obras)`;
                colInv.appendChild(gHeader);

                // Tarjeta 'Todos los miembros'
                const cardAll = document.createElement('div');
                cardAll.className = `inv-item-card ${invSeleccionadoDoc === null ? 'active' : ''}`;
                cardAll.innerHTML = `
                    <div class="inv-item-name">Todos los Investigadores</div>
                    <div class="inv-item-meta"><span>Producción consolidada</span><b>${g.productos.filter(productoPasaVentana).length}</b></div>
                `;
                cardAll.onclick = () => { invSeleccionadoDoc = null; renderizarExploradorJerarquico(); };
                colInv.appendChild(cardAll);

                g.investigadores.forEach(inv => {
                    const cant = g.productos.filter(p => p.id_investigador === inv.documento && productoPasaVentana(p)).length;
                    const cardInv = document.createElement('div');
                    cardInv.className = `inv-item-card ${invSeleccionadoDoc === inv.documento ? 'active' : ''}`;
                    cardInv.innerHTML = `
                        <div class="inv-item-name">${inv.nombre}</div>
                        <div class="inv-item-meta"><span>${inv.categoria}</span><b>${cant} obras</b></div>
                    `;
                    cardInv.onclick = () => {
                        invSeleccionadoDoc = inv.documento;
                        mostrarDetalleInvestigador(inv, g);
                        renderizarExploradorJerarquico();
                    };
                    colInv.appendChild(cardInv);
                });
            });

            // Filtrar productos a mostrar
            let prodsMostrar = todosLosProds.filter(item => {
                if (invSeleccionadoDoc && item.prod.id_investigador !== invSeleccionadoDoc) return false;
                if (filtroTexto) {
                    const txt = (item.prod.titulo + " " + item.prod.id + " " + item.prod.tipo).toLowerCase();
                    if (!txt.includes(filtroTexto)) return false;
                }
                return true;
            });

            document.getElementById('hier-prod-count').innerText = `${prodsMostrar.length} productos`;

            prodsMostrar.forEach(item => {
                const p = item.prod;
                const cardP = document.createElement('div');
                cardP.className = 'prod-card';
                cardP.innerHTML = `
                    <div class="prod-card-title">${p.titulo}</div>
                    <div class="prod-card-tags">
                        <span class="pill pill-${p.categoria.toLowerCase()}">${p.categoria}</span>
                        <span class="pill" style="background:#1e293b; color:#94a3b8;">${p.tipo} &bull; ${p.anio}</span>
                        <span class="pill ${p.validado ? 'pill-val' : 'pill-noval'}">${p.validado ? 'Avalado' : 'Sin Aval'}</span>
                    </div>
                `;
                cardP.onclick = () => mostrarDetalleProducto(p, item.grupo);
                contMosaico.appendChild(cardP);
            });
        }

        // =====================================================================
        // INSPECTOR LATERAL DE DETALLES
        // =====================================================================
        function mostrarDetalleGrupo(g) {
            document.getElementById('insp-titulo').innerText = `Grupo: ${g.codigo}`;
            const c = document.getElementById('insp-contenido');
            c.innerHTML = `
                <div class="meta-field"><span class="meta-k">Nombre Oficial</span><span class="meta-v">${g.nombre}</span></div>
                <div class="meta-field"><span class="meta-k">Clasificación</span><span class="meta-v">${g.clasificacion}</span></div>
                <div class="meta-field"><span class="meta-k">Líder</span><span class="meta-v">${g.lider}</span></div>
                <div class="meta-field"><span class="meta-k">Área OCDE</span><span class="meta-v">${g.area}</span></div>
                <div class="meta-field"><span class="meta-k">Año de Fundación</span><span class="meta-v">${g.anio}</span></div>
                <div class="meta-field"><span class="meta-k">Investigadores</span><span class="meta-v">${g.investigadores.length}</span></div>
                <div class="meta-field"><span class="meta-k">Producción (Filtro)</span><span class="meta-v">${g.productos.filter(productoPasaVentana).length} obras</span></div>
                <div class="ptr-box">NodoGrupo* &bull; sigGrupo -> 0x0<br>primerInvestigador -> 0x7ffd10a<br>primerProducto -> 0x7ffd22b</div>
            `;
        }

        function mostrarDetalleInvestigador(inv, g) {
            document.getElementById('insp-titulo').innerText = `Investigador: ${inv.nombre}`;
            const c = document.getElementById('insp-contenido');
            const cant = g.productos.filter(p => p.id_investigador === inv.documento).length;
            c.innerHTML = `
                <div class="meta-field"><span class="meta-k">Documento / CvLAC</span><span class="meta-v">${inv.documento}</span></div>
                <div class="meta-field"><span class="meta-k">Categoría MinCiencias</span><span class="meta-v">${inv.categoria}</span></div>
                <div class="meta-field"><span class="meta-k">Formación Académica</span><span class="meta-v">${inv.formacion}</span></div>
                <div class="meta-field"><span class="meta-k">Grupo Adscrito</span><span class="meta-v">${g.nombre}</span></div>
                <div class="meta-field"><span class="meta-k">Obras Autoradas</span><span class="meta-v">${cant} registradas</span></div>
                <div class="ptr-box">NodoInvestigador* [sigInvestigador]<br>primerProducto (Ortogonal Z)</div>
            `;
        }

        function mostrarDetalleProducto(p, g) {
            document.getElementById('insp-titulo').innerText = `Obra: ${p.id}`;
            const c = document.getElementById('insp-contenido');
            c.innerHTML = `
                <div class="meta-field"><span class="meta-k">Título</span><span class="meta-v">${p.titulo}</span></div>
                <div class="meta-field"><span class="meta-k">Tipo de Producción</span><span class="meta-v">${p.tipo}</span></div>
                <div class="meta-field"><span class="meta-k">Año de Publicación</span><span class="meta-v">${p.anio}</span></div>
                <div class="meta-field"><span class="meta-k">Categoría</span><span class="meta-v">${p.categoria}</span></div>
                <div class="meta-field"><span class="meta-k">Aval MinCiencias</span><span class="meta-v">${p.validado ? 'SÍ (Aval Institucional)' : 'NO (Sin validar)'}</span></div>
                <div class="meta-field"><span class="meta-k">Grupo Asociado</span><span class="meta-v">${g.nombre}</span></div>
                <div class="meta-field"><span class="meta-k">Autor (ID)</span><span class="meta-v">${p.id_investigador}</span></div>
                <div class="ptr-box">NodoProducto*<br>sigProductoGrupo &bull; sigProductoInvestigador</div>
            `;
        }

        // =====================================================================
        // DASHBOARD ESTADÍSTICO
        // =====================================================================
        function renderizarDashboard() {
            let catCounts = { "A1": 0, "A": 0, "B": 0, "C": 0, "Otras": 0 };
            let anioCounts = {};
            let tipoCounts = {};
            let valCount = 0, noValCount = 0;
            let total = 0;

            DATOS_HIPERCUBO.grupos.forEach(g => {
                g.productos.forEach(p => {
                    if (productoPasaVentana(p)) {
                        total++;
                        if (catCounts[p.categoria] !== undefined) catCounts[p.categoria]++;
                        else catCounts["Otras"]++;

                        anioCounts[p.anio] = (anioCounts[p.anio] || 0) + 1;
                        tipoCounts[p.tipo] = (tipoCounts[p.tipo] || 0) + 1;

                        if (p.validado) valCount++; else noValCount++;
                    }
                });
            });

            // 1. Gráfico Categorías
            const cCat = document.getElementById('chart-categorias');
            cCat.innerHTML = '';
            for (let [cat, cnt] of Object.entries(catCounts)) {
                if (cnt === 0 && cat === 'Otras') continue;
                const pct = total > 0 ? Math.round((cnt / total) * 100) : 0;
                cCat.innerHTML += `
                    <div class="bar-row">
                        <div class="bar-info"><span>Categoría ${cat}</span><b>${cnt} (${pct}%)</b></div>
                        <div class="bar-track"><div class="bar-fill" style="width:${pct}%; background:var(--accent-blue);"></div></div>
                    </div>
                `;
            }

            // 2. Gráfico Años (Histograma Temporal)
            const cAnios = document.getElementById('chart-anios');
            cAnios.innerHTML = '';
            const sortedAnios = Object.keys(anioCounts).sort().reverse();
            const maxAnio = Math.max(...Object.values(anioCounts), 1);
            sortedAnios.slice(0, 12).forEach(an => {
                const cnt = anioCounts[an];
                const pct = Math.round((cnt / maxAnio) * 100);
                const enVentana = (ventanaAnios === 0) || (an >= anioActual - ventanaAnios + 1);
                cAnios.innerHTML += `
                    <div class="bar-row">
                        <div class="bar-info"><span>Año ${an}</span><b>${cnt} obras</b></div>
                        <div class="bar-track"><div class="bar-fill" style="width:${pct}%; background:${enVentana ? 'var(--upc-green-light)' : '#475569'};"></div></div>
                    </div>
                `;
            });

            // 3. Avales
            const cAval = document.getElementById('chart-aval');
            const pctVal = total > 0 ? Math.round((valCount / total) * 100) : 0;
            const pctNoVal = total > 0 ? Math.round((noValCount / total) * 100) : 0;
            cAval.innerHTML = `
                <div class="bar-row">
                    <div class="bar-info"><span>Avalados por MinCiencias</span><b>${valCount} (${pctVal}%)</b></div>
                    <div class="bar-track"><div class="bar-fill" style="width:${pctVal}%; background:var(--upc-green-light);"></div></div>
                </div>
                <div class="bar-row" style="margin-top:0.6rem;">
                    <div class="bar-info"><span>Sin Aval / No Validados</span><b>${noValCount} (${pctNoVal}%)</b></div>
                    <div class="bar-track"><div class="bar-fill" style="width:${pctNoVal}%; background:var(--upc-red);"></div></div>
                </div>
            `;

            // 4. Tipologías
            const cTipos = document.getElementById('chart-tipos');
            cTipos.innerHTML = '';
            for (let [tipo, cnt] of Object.entries(tipoCounts)) {
                const pct = total > 0 ? Math.round((cnt / total) * 100) : 0;
                cTipos.innerHTML += `
                    <div class="bar-row">
                        <div class="bar-info"><span>${tipo}</span><b>${cnt} (${pct}%)</b></div>
                        <div class="bar-track"><div class="bar-fill" style="width:${pct}%; background:var(--accent-purple);"></div></div>
                    </div>
                `;
            }
        }

        // =====================================================================
        // VISTAS POR ENTIDAD (PUNTO 12.C)
        // =====================================================================
        function renderizarTablas() {
            // 1. Grupos
            const tbodyG = document.querySelector('#tabla-grupos tbody');
            tbodyG.innerHTML = '';
            DATOS_HIPERCUBO.grupos.forEach(g => {
                const prods = g.productos.filter(productoPasaVentana).length;
                tbodyG.innerHTML += `
                    <tr onclick="mostrarDetalleGrupo(DATOS_HIPERCUBO.grupos[0])">
                        <td><b>${g.codigo}</b></td>
                        <td>${g.nombre}</td>
                        <td><span class="pill pill-${g.clasificacion.toLowerCase()}">${g.clasificacion}</span></td>
                        <td>${g.lider}</td>
                        <td>${g.investigadores.length}</td>
                        <td><b>${prods}</b></td>
                    </tr>
                `;
            });

            // 2. Investigadores
            const tbodyI = document.querySelector('#tabla-investigadores tbody');
            tbodyI.innerHTML = '';
            DATOS_HIPERCUBO.grupos.forEach(g => {
                g.investigadores.forEach(inv => {
                    const prods = g.productos.filter(p => p.id_investigador === inv.documento && productoPasaVentana(p)).length;
                    tbodyI.innerHTML += `
                        <tr onclick="mostrarDetalleInvestigador(DATOS_HIPERCUBO.grupos[0].investigadores.find(i=>i.documento==='${inv.documento}'), DATOS_HIPERCUBO.grupos[0])">
                            <td><code>${inv.documento}</code></td>
                            <td><b>${inv.nombre}</b></td>
                            <td>${inv.categoria}</td>
                            <td>${inv.formacion}</td>
                            <td><b>${prods}</b></td>
                        </tr>
                    `;
                });
            });

            // 3. Productos (Paginado)
            renderizarTablaProductosPaginada();
        }

        function renderizarTablaProductosPaginada() {
            const tbodyP = document.querySelector('#tabla-productos tbody');
            tbodyP.innerHTML = '';

            let todos = [];
            DATOS_HIPERCUBO.grupos.forEach(g => {
                g.productos.forEach(p => {
                    if (productoPasaVentana(p)) {
                        if (!filtroTexto || p.titulo.toLowerCase().includes(filtroTexto) || p.id.toLowerCase().includes(filtroTexto)) {
                            todos.push({ prod: p, grupo: g });
                        }
                    }
                });
            });

            const total = todos.length;
            const totalPags = Math.max(1, Math.ceil(total / PRODS_POR_PAG));
            if (pagProdActual >= totalPags) pagProdActual = totalPags - 1;

            const inicio = pagProdActual * PRODS_POR_PAG;
            const fin = Math.min(inicio + PRODS_POR_PAG, total);

            document.getElementById('lbl-pag-prod').innerText = `Página ${pagProdActual + 1} de ${totalPags} (Total: ${total} obras)`;

            todos.slice(inicio, fin).forEach(item => {
                const p = item.prod;
                tbodyP.innerHTML += `
                    <tr onclick="mostrarDetalleProducto(DATOS_HIPERCUBO.grupos[0].productos.find(x=>x.id==='${p.id}'), DATOS_HIPERCUBO.grupos[0])">
                        <td><code>${p.id}</code></td>
                        <td>${p.tipo}</td>
                        <td>${p.titulo}</td>
                        <td>${p.anio}</td>
                        <td><span class="pill pill-${p.categoria.toLowerCase()}">${p.categoria}</span></td>
                        <td><span class="pill ${p.validado ? 'pill-val' : 'pill-noval'}">${p.validado ? 'Aval' : 'Sin Aval'}</span></td>
                    </tr>
                `;
            });
        }

        function paginarTablaProd(delta) {
            pagProdActual += delta;
            if (pagProdActual < 0) pagProdActual = 0;
            renderizarTablaProductosPaginada();
        }

        // INICIALIZACIÓN
        window.onload = () => {
            renderizarTodo();
            redimensionarCanvas();
        };
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
        std::cout << "\n[+] Generando Visualizador Gráfico del Hipercubo 3D desde la Multilista en RAM...\n";
        if (generarHTML(multi, rutaSalida)) {
            std::cout << "[OK] Archivo generado exitosamente en: " << rutaSalida << "\n";
            std::cout << "[+] Abriendo interfaz gráfica en el navegador predeterminado...\n";
            abrirEnNavegador(rutaSalida);
            return true;
        }
        return false;
    }
};

#endif // VISUALIZADOR_GRAFICO_H
