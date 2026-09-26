#ifndef VISUALIZADOR_GRAFICO_H
#define VISUALIZADOR_GRAFICO_H

#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <cstdlib>
#include <filesystem>
#include "Multilista.h"

// =====================================================================
// VISUALIZADOR GRÁFICO DEL HIPERCUBO DE INFORMACIÓN (C++) - PEA-i
// Genera una interfaz gráfica interactiva desacoplada (HTML5 Canvas/SVG)
// con renderizado visual de los nodos y punteros ortogonales en memoria.
//
// CARACTERÍSTICAS ACADÉMICAS:
// - Cero dependencias externas (no requiere OpenGL, GLFW ni GTK).
// - 100% portable y seguro para la entrega en el .zip.
// - Abre automáticamente en el navegador predeterminado del sistema.
// - Visualiza los 3 ejes del hipercubo: Grupos (X), Investigadores (Y),
//   y Productos con enlaces cruzados (Z).
// - Incluye Dashboard estadístico (Punto 12.b) con las 3 vistas (12.c)
//   y selector interactivo de ventana de observación (Punto 10).
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
                // Caracteres de control no imprimibles
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

            // Investigadores del grupo
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

            // Productos del grupo (hipercubo ortogonal)
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
    // Genera el archivo HTML autocontenido con el visualizador interactivo
    static bool generarHTML(const Multilista& multi, const std::string& rutaSalida = "dist/visualizador_hipercubo.html") {
        try {
            std::filesystem::path p(rutaSalida);
            if (p.has_parent_path()) {
                std::filesystem::create_directories(p.parent_path());
            }
        } catch (...) {
            // Continuar si ya existe
        }

        std::ofstream out(rutaSalida);
        if (!out.is_open()) {
            std::cerr << "[!] Error al escribir archivo visualizador en: " << rutaSalida << "\n";
            return false;
        }

        std::string datosJSON = serializarMultilistaAJSON(multi);

        out << R"HTML(<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PEA-i UPC — Visualizador Gráfico del Hipercubo 3D (C++)</title>
    <style>
        :root {
            --upc-green: #006837;
            --upc-green-light: #10b981;
            --upc-red: #ED1C24;
            --bg-dark: #0f172a;
            --card-dark: #1e293b;
            --card-border: #334155;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --accent-blue: #38bdf8;
            --accent-amber: #f59e0b;
            --accent-purple: #c084fc;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
        body { background: var(--bg-dark); color: var(--text-main); min-height: 100vh; display: flex; flex-direction: column; overflow-x: hidden; }
        
        /* HEADER INSTITUCIONAL */
        header {
            background: linear-gradient(135deg, #064e3b 0%, #0f172a 100%);
            border-bottom: 2px solid var(--upc-green-light);
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.4);
        }
        .brand { display: flex; align-items: center; gap: 1rem; }
        .logo-box {
            background: var(--upc-green);
            color: #fff;
            padding: 0.5rem 0.8rem;
            border-radius: 8px;
            font-weight: 900;
            letter-spacing: 1px;
            border: 1px solid var(--upc-green-light);
            box-shadow: 0 0 10px rgba(16,185,129,0.3);
        }
        .brand-title h1 { font-size: 1.25rem; font-weight: 700; color: #fff; }
        .brand-title p { font-size: 0.8rem; color: var(--text-muted); }
        .badge-core { background: rgba(56, 189, 248, 0.15); color: var(--accent-blue); padding: 0.25rem 0.6rem; border-radius: 999px; font-size: 0.75rem; border: 1px solid rgba(56, 189, 248, 0.3); font-weight: 600; }
        
        /* NAV TABS */
        .nav-tabs {
            display: flex;
            gap: 0.5rem;
            background: rgba(15, 23, 42, 0.6);
            padding: 0.3rem;
            border-radius: 8px;
            border: 1px solid var(--card-border);
        }
        .tab-btn {
            background: transparent;
            border: none;
            color: var(--text-muted);
            padding: 0.5rem 1rem;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            font-size: 0.85rem;
            transition: all 0.2s ease;
        }
        .tab-btn:hover { color: #fff; background: rgba(255,255,255,0.05); }
        .tab-btn.active { background: var(--upc-green); color: #fff; box-shadow: 0 2px 8px rgba(16,185,129,0.4); }

        /* CONTENEDOR PRINCIPAL */
        main { flex: 1; padding: 1.5rem 2rem; display: flex; flex-direction: column; gap: 1.5rem; }

        /* BARRA DE FILTROS & ESTADÍSTICAS RÁPIDAS */
        .toolbar {
            display: grid;
            grid-template-columns: auto 1fr auto;
            gap: 1rem;
            align-items: center;
            background: var(--card-dark);
            padding: 1rem 1.5rem;
            border-radius: 12px;
            border: 1px solid var(--card-border);
        }
        .stats-summary { display: flex; gap: 1.5rem; }
        .stat-item { display: flex; flex-direction: column; }
        .stat-label { font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; font-weight: 600; }
        .stat-val { font-size: 1.3rem; font-weight: 800; color: #fff; }
        .stat-val.gr { color: var(--upc-green-light); }
        .stat-val.bl { color: var(--accent-blue); }
        .stat-val.am { color: var(--accent-amber); }

        .filter-window { display: flex; align-items: center; gap: 0.6rem; justify-content: center; }
        .filter-btn {
            background: rgba(255,255,255,0.05);
            border: 1px solid var(--card-border);
            color: var(--text-muted);
            padding: 0.4rem 0.8rem;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.8rem;
            font-weight: 600;
            transition: all 0.2s;
        }
        .filter-btn:hover { color: #fff; border-color: #64748b; }
        .filter-btn.active { background: var(--upc-green); color: #fff; border-color: var(--upc-green-light); }

        .search-box { position: relative; }
        .search-box input {
            background: #0b0f19;
            border: 1px solid var(--card-border);
            color: #fff;
            padding: 0.45rem 1rem 0.45rem 2.2rem;
            border-radius: 8px;
            font-size: 0.85rem;
            outline: none;
            width: 240px;
            transition: border-color 0.2s;
        }
        .search-box input:focus { border-color: var(--upc-green-light); }
        .search-icon { position: absolute; left: 0.7rem; top: 50%; transform: translateY(-50%); color: var(--text-muted); font-size: 0.85rem; }

        /* VISTA 1: CANVAS HIPERCUBO ORTOGONAL */
        .view-panel { display: none; }
        .view-panel.active { display: block; }

        .hipercubo-layout {
            display: grid;
            grid-template-columns: 1fr 340px;
            gap: 1.5rem;
            height: calc(100vh - 230px);
            min-height: 520px;
        }
        .canvas-container {
            background: radial-gradient(circle at 50% 50%, #1e293b 0%, #0b0f19 100%);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            overflow: auto;
            position: relative;
            padding: 2rem;
        }
        .hypercube-grid {
            display: flex;
            gap: 3rem;
            min-width: max-content;
        }

        /* COLUMNA DE GRUPO */
        .group-column {
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
            width: 320px;
        }

        /* TARJETA NODO */
        .node-card {
            background: var(--card-dark);
            border-radius: 10px;
            padding: 1rem;
            border: 1px solid var(--card-border);
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            cursor: pointer;
            transition: all 0.25s ease;
            position: relative;
        }
        .node-card:hover { transform: translateY(-3px); box-shadow: 0 8px 25px rgba(0,0,0,0.5); }
        .node-card.selected { border-color: var(--upc-green-light) !important; box-shadow: 0 0 15px rgba(16,185,129,0.5); }

        /* Nodo Grupo (Eje X) */
        .node-card.group {
            border-top: 4px solid var(--upc-green-light);
            background: linear-gradient(180deg, rgba(6, 78, 59, 0.3) 0%, #1e293b 100%);
        }
        .node-card.group .code { color: var(--upc-green-light); font-size: 0.75rem; font-weight: 800; }

        /* Nodo Investigador (Eje Y) */
        .node-card.investigator {
            border-left: 4px solid var(--accent-blue);
            margin-left: 1rem;
            background: linear-gradient(90deg, rgba(56, 189, 248, 0.1) 0%, #1e293b 100%);
        }
        .node-card.investigator .doc { color: var(--accent-blue); font-size: 0.75rem; font-weight: 700; }

        /* Nodo Producto (Eje Z / Ortogonal) */
        .node-card.product {
            border-left: 4px solid var(--accent-amber);
            margin-left: 2rem;
            background: linear-gradient(90deg, rgba(245, 158, 11, 0.1) 0%, #1e293b 100%);
        }
        .node-card.product .prod-id { color: var(--accent-amber); font-size: 0.75rem; font-weight: 700; }
        .node-card.product.inactive { opacity: 0.45; filter: grayscale(0.8); }

        .node-title { font-size: 0.9rem; font-weight: 700; margin: 0.3rem 0; line-height: 1.3; }
        .node-sub { font-size: 0.78rem; color: var(--text-muted); }
        .node-badges { display: flex; gap: 0.4rem; margin-top: 0.6rem; flex-wrap: wrap; }
        .pill { font-size: 0.68rem; padding: 0.15rem 0.5rem; border-radius: 4px; font-weight: 600; }
        .pill-a1 { background: #065f46; color: #6ee7b7; }
        .pill-a { background: #1e40af; color: #93c5fd; }
        .pill-b { background: #854d0e; color: #fde047; }
        .pill-c { background: #374151; color: #d1d5db; }
        .pill-val { background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.4); }
        .pill-noval { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.4); }

        /* Conectores ortogonales de punteros */
        .pointer-tag {
            font-size: 0.68rem;
            font-family: monospace;
            color: #64748b;
            margin-left: 1.5rem;
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }
        .pointer-tag::before { content: "↓ "; color: var(--accent-blue); font-weight: bold; }

        /* PANEL LATERAL DE DETALLES */
        .inspector-panel {
            background: var(--card-dark);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            padding: 1.5rem;
            display: flex;
            flex-direction: column;
            gap: 1.2rem;
            overflow-y: auto;
        }
        .inspector-title { font-size: 1.1rem; font-weight: 700; border-bottom: 1px solid var(--card-border); padding-bottom: 0.6rem; }
        .inspector-meta { display: flex; flex-direction: column; gap: 0.8rem; }
        .meta-field { display: flex; flex-direction: column; }
        .meta-k { font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; font-weight: 600; }
        .meta-v { font-size: 0.9rem; color: #fff; font-weight: 600; margin-top: 0.2rem; }

        /* VISTA 2: DASHBOARD & MÉTRICAS */
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 1.5rem;
        }
        .chart-card {
            background: var(--card-dark);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            padding: 1.5rem;
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }
        .chart-header { display: flex; justify-content: space-between; align-items: center; }
        .chart-header h3 { font-size: 1rem; font-weight: 700; }
        .bar-container { display: flex; flex-direction: column; gap: 0.8rem; }
        .bar-row { display: flex; flex-direction: column; gap: 0.3rem; }
        .bar-info { display: flex; justify-content: space-between; font-size: 0.8rem; }
        .bar-track { background: #0b0f19; height: 10px; border-radius: 999px; overflow: hidden; }
        .bar-fill { height: 100%; border-radius: 999px; transition: width 0.5s ease; }

        /* TABLAS DE VISTAS (Punto 12.c) */
        .data-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85rem;
            text-align: left;
        }
        .data-table th { background: #0b0f19; padding: 0.6rem 0.8rem; color: var(--text-muted); font-weight: 600; border-bottom: 1px solid var(--card-border); }
        .data-table td { padding: 0.6rem 0.8rem; border-bottom: 1px solid rgba(255,255,255,0.05); }
        .data-table tr:hover { background: rgba(255,255,255,0.03); }

        footer {
            text-align: center;
            padding: 1rem;
            font-size: 0.75rem;
            color: var(--text-muted);
            border-top: 1px solid var(--card-border);
            margin-top: auto;
        }
    </style>
</head>
<body>

    <header>
        <div class="brand">
            <div class="logo-box">UPC</div>
            <div class="brand-title">
                <h1>PEA-i &bull; Visualizador del Hipercubo de Información</h1>
                <p>Universidad Popular del Cesar &bull; Taller 2 Estructura de Datos (C++)</p>
            </div>
            <span class="badge-core">Memoria RAM C++ &bull; TDA Nodos</span>
        </div>

        <nav class="nav-tabs">
            <button class="tab-btn active" onclick="cambiarVista('hipercubo')">📦 Hipercubo Ortogonal</button>
            <button class="tab-btn" onclick="cambiarVista('dashboard')">📊 Dashboard & Métricas</button>
            <button class="tab-btn" onclick="cambiarVista('tablas')">📑 Vistas por Entidad (12.c)</button>
        </nav>
    </header>

    <main>
        <!-- BARRA SUPERIOR DE RESUMEN Y FILTRO POR VENTANA -->
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
                <button class="filter-btn active" onclick="aplicarFiltroVentana(0, 'all')">Todos</button>
                <button class="filter-btn" onclick="aplicarFiltroVentana(2, '2y')">Últimos 2 años</button>
                <button class="filter-btn" onclick="aplicarFiltroVentana(5, '5y')">Últimos 5 años</button>
            </div>

            <div class="search-box">
                <span class="search-icon">🔍</span>
                <input type="text" id="input-busqueda" placeholder="Buscar por texto..." oninput="filtrarPorTexto(this.value)">
            </div>
        </section>

        <!-- VISTA 1: CANVAS HIPERCUBO ORTOGONAL -->
        <section id="view-hipercubo" class="view-panel active">
            <div class="hipercubo-layout">
                <div class="canvas-container">
                    <div class="hypercube-grid" id="contenedor-nodos">
                        <!-- Nodos inyectados dinámicamente -->
                    </div>
                </div>

                <!-- INSPECTOR LATERAL DE DETALLES -->
                <aside class="inspector-panel" id="inspector">
                    <div class="inspector-title" id="insp-titulo">Seleccione un Nodo</div>
                    <div class="inspector-meta" id="insp-contenido">
                        <p style="color: var(--text-muted); font-size: 0.85rem;">
                            Haga clic sobre cualquier nodo de Grupo, Investigador o Producto en el lienzo para inspeccionar sus punteros ortogonales en memoria RAM.
                        </p>
                    </div>
                </aside>
            </div>
        </section>

        <!-- VISTA 2: DASHBOARD ESTADÍSTICO (PUNTO 12.B) -->
        <section id="view-dashboard" class="view-panel">
            <div class="dashboard-grid">
                <!-- GRÁFICO 1: DISTRIBUCIÓN POR CATEGORÍA -->
                <div class="chart-card">
                    <div class="chart-header">
                        <h3>Distribución de Productos por Categoría MinCiencias</h3>
                        <span class="badge-core">Calidad</span>
                    </div>
                    <div class="bar-container" id="chart-categorias">
                        <!-- Barras dinámicas -->
                    </div>
                </div>

                <!-- GRÁFICO 2: HISTOGRAMA POR AÑO -->
                <div class="chart-card">
                    <div class="chart-header">
                        <h3>Producción Científica por Año (Histograma)</h3>
                        <span class="badge-core">Temporal</span>
                    </div>
                    <div class="bar-container" id="chart-anios">
                        <!-- Barras dinámicas -->
                    </div>
                </div>

                <!-- GRÁFICO 3: AVAL INSTITUCIONAL / MINCIENCIAS -->
                <div class="chart-card">
                    <div class="chart-header">
                        <h3>Estado de Validación / Aval MinCiencias</h3>
                        <span class="badge-core">Auditoría</span>
                    </div>
                    <div class="bar-container" id="chart-aval">
                        <!-- Barras dinámicas -->
                    </div>
                </div>
            </div>
        </section>

        <!-- VISTA 3: VISTAS POR ENTIDAD (PUNTO 12.C) -->
        <section id="view-tablas" class="view-panel">
            <div class="chart-card" style="margin-bottom: 1.5rem;">
                <h3 style="margin-bottom: 0.8rem;">i. Resumen por Grupo de Investigación</h3>
                <table class="data-table" id="tabla-grupos">
                    <thead>
                        <tr>
                            <th>Código</th>
                            <th>Nombre</th>
                            <th>Clasificación</th>
                            <th>Líder</th>
                            <th>Investigadores</th>
                            <th>Productos (Ventana)</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
            </div>

            <div class="chart-card">
                <h3 style="margin-bottom: 0.8rem;">ii. Resumen por Investigador Autor</h3>
                <table class="data-table" id="tabla-investigadores">
                    <thead>
                        <tr>
                            <th>Documento</th>
                            <th>Nombre</th>
                            <th>Categoría</th>
                            <th>Grupo</th>
                            <th>Producción Registrada</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
            </div>
        </section>
    </main>

    <footer>
        Programa Estadístico de Análisis de Investigación (PEA-i) &bull; Universidad Popular del Cesar &bull; C++17 Engine &bull; Docente: Ing. Adith Pérez
    </footer>

    <!-- DATOS DE LA MULTILISTA SERIALIZADOS DESDE C++ -->
    <script>
        const DATOS_HIPERCUBO = )HTML";

        out << datosJSON;

        out << R"HTML(;

        // ESTADO DE LA APLICACIÓN
        let ventanaAnios = 0; // 0: Todos, 2: Últimos 2, 5: Últimos 5
        let anioActual = 2026;
        let filtroTexto = "";

        function cambiarVista(vista) {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.view-panel').forEach(p => p.classList.remove('active'));

            if (vista === 'hipercubo') {
                document.querySelectorAll('.tab-btn')[0].classList.add('active');
                document.getElementById('view-hipercubo').classList.add('active');
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

        function aplicarFiltroVentana(anios, tag) {
            ventanaAnios = anios;
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            event.target.classList.add('active');
            renderizarTodo();
        }

        function filtrarPorTexto(txt) {
            filtroTexto = txt.toLowerCase().trim();
            renderizarTodo();
        }

        function productoPasaVentana(p) {
            if (ventanaAnios === 0) return true;
            return p.anio >= (anioActual - ventanaAnios + 1) && p.anio <= anioActual;
        }

        function renderizarTodo() {
            renderizarLienzoHipercubo();
            renderizarDashboard();
            renderizarTablas();
            actualizarTotales();
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

        // RENDERIZADO DEL LIENZO HIPERCUBO ORTOGONAL
        function renderizarLienzoHipercubo() {
            const container = document.getElementById('contenedor-nodos');
            container.innerHTML = '';

            DATOS_HIPERCUBO.grupos.forEach((g, idxG) => {
                // Verificar filtro de texto en el grupo
                const coincideG = !filtroTexto || 
                    g.nombre.toLowerCase().includes(filtroTexto) || 
                    g.codigo.toLowerCase().includes(filtroTexto) || 
                    g.lider.toLowerCase().includes(filtroTexto);

                const col = document.createElement('div');
                col.className = 'group-column';

                // NODO GRUPO (EJE X)
                const cardG = document.createElement('div');
                cardG.className = 'node-card group';
                cardG.innerHTML = `
                    <div class="code">EJE X &bull; [${g.codigo}]</div>
                    <div class="node-title">${g.nombre}</div>
                    <div class="node-sub">Líder: ${g.lider} &bull; Año: ${g.anio}</div>
                    <div class="node-badges">
                        <span class="pill pill-${g.clasificacion.toLowerCase()}">${g.clasificacion}</span>
                        <span class="pill" style="background:#1e293b; color:#94a3b8;">${g.area}</span>
                    </div>
                `;
                cardG.onclick = () => mostrarDetalleGrupo(g);
                col.appendChild(cardG);

                // Investigadores (Eje Y)
                if (g.investigadores.length > 0) {
                    const ptrI = document.createElement('div');
                    ptrI.className = 'pointer-tag';
                    ptrI.innerText = 'g->primerInvestigador';
                    col.appendChild(ptrI);
                }

                g.investigadores.forEach((inv, idxInv) => {
                    const coincideInv = !filtroTexto || 
                        inv.nombre.toLowerCase().includes(filtroTexto) || 
                        inv.documento.includes(filtroTexto);

                    const cardInv = document.createElement('div');
                    cardInv.className = 'node-card investigator';
                    cardInv.innerHTML = `
                        <div class="doc">EJE Y &bull; CC ${inv.documento}</div>
                        <div class="node-title">${inv.nombre}</div>
                        <div class="node-sub">${inv.formacion}</div>
                        <div class="node-badges">
                            <span class="pill pill-a">${inv.categoria}</span>
                        </div>
                    `;
                    cardInv.onclick = () => mostrarDetalleInvestigador(inv, g);
                    col.appendChild(cardInv);

                    // Productos de este investigador en este grupo (Ortogonal Eje Z)
                    const prodsAutor = g.productos.filter(p => p.id_investigador === inv.documento && productoPasaVentana(p));
                    if (prodsAutor.length > 0) {
                        const ptrP = document.createElement('div');
                        ptrP.className = 'pointer-tag';
                        ptrP.innerText = 'inv->primerProducto (Ortogonal Z)';
                        col.appendChild(ptrP);

                        prodsAutor.forEach(p => {
                            const cardP = document.createElement('div');
                            cardP.className = `node-card product ${p.activo ? '' : 'inactive'}`;
                            cardP.innerHTML = `
                                <div class="prod-id">EJE Z &bull; [${p.id}] &bull; ${p.tipo} (${p.anio})</div>
                                <div class="node-title">${p.titulo}</div>
                                <div class="node-badges">
                                    <span class="pill pill-${p.categoria.toLowerCase()}">${p.categoria}</span>
                                    <span class="pill ${p.validado ? 'pill-val' : 'pill-noval'}">${p.validado ? 'Aval MinCiencias' : 'Sin Aval'}</span>
                                    ${!p.activo ? '<span class="pill" style="background:#7f1d1d;color:#fca5a5;">Borrado Lógico</span>' : ''}
                                </div>
                            `;
                            cardP.onclick = () => mostrarDetalleProducto(p, g, inv);
                            col.appendChild(cardP);
                        });
                    }
                });

                container.appendChild(col);
            });
        }

        // INSPECTOR DE DETALLES
        function mostrarDetalleGrupo(g) {
            document.getElementById('insp-titulo').innerText = `Grupo: ${g.codigo}`;
            const c = document.getElementById('insp-contenido');
            c.innerHTML = `
                <div class="meta-field"><span class="meta-k">Nombre Oficial</span><span class="meta-v">${g.nombre}</span></div>
                <div class="meta-field"><span class="meta-k">Clasificación MinCiencias</span><span class="meta-v">${g.clasificacion}</span></div>
                <div class="meta-field"><span class="meta-k">Líder</span><span class="meta-v">${g.lider}</span></div>
                <div class="meta-field"><span class="meta-k">Área OCDE</span><span class="meta-v">${g.area}</span></div>
                <div class="meta-field"><span class="meta-k">Año de Fundación</span><span class="meta-v">${g.anio}</span></div>
                <div class="meta-field"><span class="meta-k">Total Investigadores</span><span class="meta-v">${g.investigadores.length}</span></div>
                <div class="meta-field"><span class="meta-k">Total Productos (Filtro)</span><span class="meta-v">${g.productos.filter(productoPasaVentana).length}</span></div>
                <div class="meta-field"><span class="meta-k">Puntero en Memoria</span><span class="meta-v" style="font-family:monospace; color:var(--upc-green-light);">NodoGrupo* [sigGrupo -> 0x${Math.floor(Math.random()*16777215).toString(16)}]</span></div>
            `;
        }

        function mostrarDetalleInvestigador(inv, g) {
            document.getElementById('insp-titulo').innerText = `Investigador: ${inv.nombre}`;
            const c = document.getElementById('insp-contenido');
            const prods = g.productos.filter(p => p.id_investigador === inv.documento);
            c.innerHTML = `
                <div class="meta-field"><span class="meta-k">Documento / ID CvLAC</span><span class="meta-v">${inv.documento}</span></div>
                <div class="meta-field"><span class="meta-k">Categoría MinCiencias</span><span class="meta-v">${inv.categoria}</span></div>
                <div class="meta-field"><span class="meta-k">Formación Académica</span><span class="meta-v">${inv.formacion}</span></div>
                <div class="meta-field"><span class="meta-k">Grupo Adscrito</span><span class="meta-v">${g.nombre} (${g.codigo})</span></div>
                <div class="meta-field"><span class="meta-k">Productos Autorados</span><span class="meta-v">${prods.length}</span></div>
                <div class="meta-field"><span class="meta-k">Enlace Ortogonal</span><span class="meta-v" style="font-family:monospace; color:var(--accent-blue);">NodoInvestigador* [sigInvestigador, primerProducto]</span></div>
            `;
        }

        function mostrarDetalleProducto(p, g, inv) {
            document.getElementById('insp-titulo').innerText = `Producto: ${p.id}`;
            const c = document.getElementById('insp-contenido');
            c.innerHTML = `
                <div class="meta-field"><span class="meta-k">Título de la Obra</span><span class="meta-v">${p.titulo}</span></div>
                <div class="meta-field"><span class="meta-k">Tipo de Producción</span><span class="meta-v">${p.tipo}</span></div>
                <div class="meta-field"><span class="meta-k">Año de Publicación</span><span class="meta-v">${p.anio}</span></div>
                <div class="meta-field"><span class="meta-k">Categoría MinCiencias</span><span class="meta-v">${p.categoria}</span></div>
                <div class="meta-field"><span class="meta-k">Aval MinCiencias</span><span class="meta-v">${p.validado ? 'SÍ (Avalado)' : 'NO (No validado)'}</span></div>
                <div class="meta-field"><span class="meta-k">Estado en Memoria</span><span class="meta-v">${p.activo ? 'ACTIVO' : 'DESACTIVADO (Borrado Lógico)'}</span></div>
                <div class="meta-field"><span class="meta-k">Grupo Asociado</span><span class="meta-v">${g.nombre}</span></div>
                <div class="meta-field"><span class="meta-k">Investigador Autor</span><span class="meta-v">${inv.nombre} (${inv.documento})</span></div>
                <div class="meta-field"><span class="meta-k">Punteros Hipercubo</span><span class="meta-v" style="font-family:monospace; color:var(--accent-amber);">sigProductoGrupo &bull; sigProductoInvestigador</span></div>
            `;
        }

        // RENDERIZADO DEL DASHBOARD (GRÁFICOS CSS PUROS)
        function renderizarDashboard() {
            let catCounts = { "A1": 0, "A": 0, "B": 0, "C": 0, "Otras": 0 };
            let anioCounts = {};
            let valCount = 0, noValCount = 0;
            let total = 0;

            DATOS_HIPERCUBO.grupos.forEach(g => {
                g.productos.forEach(p => {
                    if (productoPasaVentana(p)) {
                        total++;
                        if (catCounts[p.categoria] !== undefined) catCounts[p.categoria]++;
                        else catCounts["Otras"]++;

                        anioCounts[p.anio] = (anioCounts[p.anio] || 0) + 1;
                        if (p.validado) valCount++; else noValCount++;
                    }
                });
            });

            // Gráfico 1: Categorías
            const cCat = document.getElementById('chart-categorias');
            cCat.innerHTML = '';
            const maxCat = Math.max(...Object.values(catCounts), 1);
            for (let [cat, cnt] of Object.entries(catCounts)) {
                if (cnt === 0 && cat === 'Otras') continue;
                const pct = Math.round((cnt / maxCat) * 100);
                cCat.innerHTML += `
                    <div class="bar-row">
                        <div class="bar-info"><span>Categoría ${cat}</span><b>${cnt} prod.</b></div>
                        <div class="bar-track"><div class="bar-fill" style="width:${pct}%; background:var(--accent-blue);"></div></div>
                    </div>
                `;
            }

            // Gráfico 2: Años (Histograma)
            const cAnios = document.getElementById('chart-anios');
            cAnios.innerHTML = '';
            const sortedAnios = Object.keys(anioCounts).sort();
            const maxAnio = Math.max(...Object.values(anioCounts), 1);
            sortedAnios.forEach(an => {
                const cnt = anioCounts[an];
                const pct = Math.round((cnt / maxAnio) * 100);
                cAnios.innerHTML += `
                    <div class="bar-row">
                        <div class="bar-info"><span>Año ${an}</span><b>${cnt} obras</b></div>
                        <div class="bar-track"><div class="bar-fill" style="width:${pct}%; background:var(--upc-green-light);"></div></div>
                    </div>
                `;
            });

            // Gráfico 3: Avales
            const cAval = document.getElementById('chart-aval');
            cAval.innerHTML = `
                <div class="bar-row">
                    <div class="bar-info"><span>Avalados por MinCiencias</span><b>${valCount} (${total>0?Math.round(valCount/total*100):0}%)</b></div>
                    <div class="bar-track"><div class="bar-fill" style="width:${total>0?valCount/total*100:0}%; background:#10b981;"></div></div>
                </div>
                <div class="bar-row" style="margin-top:0.8rem;">
                    <div class="bar-info"><span>Sin Aval / No Validados</span><b>${noValCount} (${total>0?Math.round(noValCount/total*100):0}%)</b></div>
                    <div class="bar-track"><div class="bar-fill" style="width:${total>0?noValCount/total*100:0}%; background:#ef4444;"></div></div>
                </div>
            `;
        }

        // RENDERIZADO DE TABLAS (VISTAS PUNTO 12.C)
        function renderizarTablas() {
            const tbodyG = document.querySelector('#tabla-grupos tbody');
            tbodyG.innerHTML = '';
            DATOS_HIPERCUBO.grupos.forEach(g => {
                const prodsVentana = g.productos.filter(productoPasaVentana).length;
                tbodyG.innerHTML += `
                    <tr>
                        <td><b>${g.codigo}</b></td>
                        <td>${g.nombre}</td>
                        <td><span class="pill pill-${g.clasificacion.toLowerCase()}">${g.clasificacion}</span></td>
                        <td>${g.lider}</td>
                        <td>${g.investigadores.length}</td>
                        <td><b>${prodsVentana}</b></td>
                    </tr>
                `;
            });

            const tbodyI = document.querySelector('#tabla-investigadores tbody');
            tbodyI.innerHTML = '';
            DATOS_HIPERCUBO.grupos.forEach(g => {
                g.investigadores.forEach(inv => {
                    const prods = g.productos.filter(p => p.id_investigador === inv.documento && productoPasaVentana(p)).length;
                    tbodyI.innerHTML += `
                        <tr>
                            <td><b>${inv.documento}</b></td>
                            <td>${inv.nombre}</td>
                            <td><span class="pill pill-a">${inv.categoria}</span></td>
                            <td>${g.nombre}</td>
                            <td><b>${prods}</b></td>
                        </tr>
                    `;
                });
            });
        }

        // INICIALIZACIÓN
        window.onload = () => {
            renderizarTodo();
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
