/*
 * UNIVERSIDAD POPULAR DEL CESAR (UPC)
 * FACULTAD DE INGENIERÍA Y TECNOLÓGICAS — INGENIERÍA DE SISTEMAS
 * ASIGNATURA: ESTRUCTURA DE DATOS (2026-I)
 * DOCENTE: ING. ADITH PÉREZ
 * 
 * PROYECTO: PEA-i — Programa Estadístico de Análisis de Investigación
 * TALLER 2 — ENTREGABLE EN C++ (ARCHIVO ÚNICO AUTOCONTENIDO)
 * 
 * AUTORES: Kovyn Mena & Equipo
 * ARCHIVO: Taller2_KM_PO_XX.cpp
 */

#include <iostream>
#include <string>
#include <sstream>
#include <iomanip>
#include <cstdlib>
#include <cstdio>
#include <ctime>
#include <vector>
#include <sqlite3.h>

#ifdef _WIN32
  #include <windows.h>
  #include <conio.h>
#else
  #include <termios.h>
  #include <unistd.h>
#endif

using namespace std;

// ============================================================================
// FUNCIONES DE UTILIDAD DE PLATAFORMA (TECLADO & CONSOLA)
// ============================================================================

void inicializarTerminal() {
#ifdef _WIN32
    SetConsoleOutputCP(65001); // Activar UTF-8 en terminal Windows
    SetConsoleCP(65001);
#endif
}

void limpiarPantalla() {
#ifdef _WIN32
    system("cls");
#else
    system("clear");
#endif
}

char leerTecla() {
#ifdef _WIN32
    return (char)_getch();
#else
    struct termios oldt, newt;
    char ch;
    tcgetattr(STDIN_FILENO, &oldt);
    newt = oldt;
    newt.c_lflag &= ~(ICANON | ECHO);
    tcsetattr(STDIN_FILENO, TCSANOW, &newt);
    ch = getchar();
    tcsetattr(STDIN_FILENO, TCSANOW, &oldt);
    return ch;
#endif
}

void pausar() {
    cout << "\nPresione cualquier tecla para continuar...";
    leerTecla();
    cout << endl;
}

// Pausa con ENTER confirmado (para mensajes de flujo de carga).
void pausarEnter(const string& msg = "Presione ENTER para continuar...") {
    cout << "\n" << msg;
    string s;
    getline(cin, s);
}

// ============================================================================
// RENDER TABULAR (tablas <= 80 col, truncar "...", headers ASCII)
// ============================================================================

// ============================================================================
// RENDER CON BORDES ASCII (S26): filas | a | b |, marcos +---+ / +===+.
// Mide ANCHO VISUAL (tildes/� = 1 columna) para que nada se descuadre.
// Solo presentacion: no toca TDAs, datos ni logica.
// ============================================================================

// Ancho en columnas de pantalla: ASCII=1, continuacion UTF-8=0, resto=1.
static size_t anchoVisual(const string& s) {
    size_t w = 0;
    for (size_t i = 0; i < s.size(); i++) {
        unsigned char b = static_cast<unsigned char>(s[i]);
        if ((b & 0xC0) == 0x80) continue; // byte de continuacion: no suma
        w++;
    }
    return w;
}

// Trunca por ancho visual sin partir un caracter multibyte.
static string truncarVisual(const string& s, size_t maxVis) {
    size_t w = 0, n = 0;
    while (n < s.size() && w < maxVis) {
        unsigned char b = static_cast<unsigned char>(s[n]);
        size_t len = 1;
        if ((b & 0x80) == 0) len = 1;
        else if ((b & 0xE0) == 0xC0) len = 2;
        else if ((b & 0xF0) == 0xE0) len = 3;
        else if ((b & 0xF8) == 0xF0) len = 4;
        if (w + 1 > maxVis) break;
        w++;
        n += len;
        if (n > s.size()) { n = s.size(); break; }
    }
    return s.substr(0, n);
}

// Red de seguridad S30: el � residual (U+FFFD) se muestra como '?'
// para no descuadrar ni romper la consola cp1252. Los datos en BD/RAM no se tocan.
static string sinRaros(const string& s) {
    string o; o.reserve(s.size());
    for (size_t i = 0; i < s.size();) {
        unsigned char b = static_cast<unsigned char>(s[i]);
        if (b == 0xEF && i + 2 < s.size() && (unsigned char)s[i+1] == 0xBF && (unsigned char)s[i+2] == 0xBD) { o += '?'; i += 3; }
        else { o += s[i]; i++; }
    }
    return o;
}

// Contenido de celda con 1 espacio a cada lado: " texto ".
static string celdaV(const string& s, size_t ancho) {
    string t = sinRaros(s);
    if (ancho <= 3) t = truncarVisual(t, ancho);
    else if (anchoVisual(t) > ancho) t = truncarVisual(t, ancho - 3) + "...";
    size_t falta = (ancho > anchoVisual(t)) ? (ancho - anchoVisual(t)) : 0;
    return " " + t + string(falta + 1, ' ');
}

// Marco: +-----+-----+ ('-' datos, '=' cabecera).
static string bordeTabla(const vector<size_t>& anchos, char relleno) {
    string b = "+";
    for (size_t i = 0; i < anchos.size(); i++) b += string(anchos[i] + 2, relleno) + "+";
    return b;
}

// Fila de datos: | a | b |.
static string filaTabla(const vector<string>& celdas, const vector<size_t>& anchos) {
    string f = "|";
    for (size_t i = 0; i < celdas.size() && i < anchos.size(); i++) f += celdaV(celdas[i], anchos[i]) + "|";
    return f;
}

// Titulo a todo el ancho de la tabla.
static string tituloTabla(const string& s, const vector<size_t>& anchos) {
    size_t tot = 0;
    for (size_t i = 0; i < anchos.size(); i++) tot += anchos[i];
    if (!anchos.empty()) tot += 3 * (anchos.size() - 1);
    return "|" + celdaV(s, tot) + "|";
}

// ============================================================================
// ESTRUCTURAS DE DATOS Dinámicas Basadas en Nodos Puros (TDAs)
// ============================================================================

// 1. NODO PRODUCTO DE INVESTIGACIÓN (Doble enlace ortogonal)
struct NodoProducto {
    int id_producto;
    string titulo;
    string tipo_producto;     // Artículo, Libro, Software, Patente
    string categoria;         // A1, A, B, C, Reconocido
    string estado_validacion; // Validado, Pendiente, Rechazado
    int anio_publicacion;
    string codigo_grupo_fk;
    string cod_rh_investigador_fk;
    bool activo;               // true: Activo, false: Borrado lógico

    NodoProducto* sigProductoGrupo;        // Eje 1: Navegación por Grupo
    NodoProducto* sigProductoInvestigador; // Eje 2: Navegación por Investigador

    NodoProducto(int id, string tit, string tipo, string cat, string val, int anio, string grp, string inv)
        : id_producto(id), titulo(tit), tipo_producto(tipo), categoria(cat),
          estado_validacion(val), anio_publicacion(anio), codigo_grupo_fk(grp),
          cod_rh_investigador_fk(inv), activo(true),
          sigProductoGrupo(nullptr), sigProductoInvestigador(nullptr) {}
};

// 2. NODO INVESTIGADOR
struct NodoInvestigador {
    string cod_rh;
    string nombre_completo;
    string correo;
    string categoria_minciencias; // Emergente, Junior, Asociado, Senior, Ínclito
    string cvlac_url;
    bool activo;

    NodoInvestigador* sigInvestigador; // Lista simple de investigadores
    NodoProducto* primProducto;        // Lista ortogonal de sus productos

    NodoInvestigador(string rh, string nom, string mail, string cat, string url)
        : cod_rh(rh), nombre_completo(nom), correo(mail), categoria_minciencias(cat),
          cvlac_url(url), activo(true), sigInvestigador(nullptr), primProducto(nullptr) {}
};

// 3. NODO GRUPO DE INVESTIGACIÓN
struct NodoGrupo {
    string codigo_grupo;
    string nombre;
    string lider;
    string plan_investigacion;
    string lineas_estrategicas;
    bool activo;

    NodoGrupo* sigGrupo;                 // Eje Horizontal: Siguiente Grupo
    NodoInvestigador* primInvestigador;  // Eje Vertical: Lista de Investigadores adscritos
    NodoProducto* primProducto;          // Eje 3D: Lista de Productos asociados al grupo

    NodoGrupo(string cod, string nom, string lid, string plan, string lineas)
        : codigo_grupo(cod), nombre(nom), lider(lid), plan_investigacion(plan),
          lineas_estrategicas(lineas), activo(true),
          sigGrupo(nullptr), primInvestigador(nullptr), primProducto(nullptr) {}
};

// 4. NODO ACCIÓN (Para Pila LIFO - Undo)
struct NodoAccion {
    int id_accion;
    string tipo_operacion;  // CREAR, EDITAR, DESACTIVAR, ELIMINAR
    string entidad_afectada; // GRUPO, INVESTIGADOR, PRODUCTO
    string datos_json;      // Respaldo de datos anteriores
    NodoAccion* sigAccion;

    NodoAccion(int id, string op, string ent, string json)
        : id_accion(id), tipo_operacion(op), entidad_afectada(ent), datos_json(json), sigAccion(nullptr) {}
};

// 5. NODO TAREA (Para Cola FIFO - Ingesta)
struct NodoTarea {
    string tipo_origen; // URL_SCIENTI, CSV, PDF
    string ruta_o_url;
    NodoTarea* sigTarea;

    NodoTarea(string tipo, string ruta)
        : tipo_origen(tipo), ruta_o_url(ruta), sigTarea(nullptr) {}
};

// ============================================================================
// CLASE PILA LIFO (DESHACER - UNDO)
// ============================================================================

class PilaUndo {
private:
    NodoAccion* top;
    int contador;

public:
    PilaUndo() : top(nullptr), contador(0) {}

    ~PilaUndo() {
        limpiar();
    }

    void apilar(string op, string ent, string json) {
        contador++;
        NodoAccion* nuevo = new NodoAccion(contador, op, ent, json);
        nuevo->sigAccion = top;
        top = nuevo;
    }

    bool desapilar(string &op, string &ent, string &json) {
        if (estaVacia()) return false;
        NodoAccion* temp = top;
        op = temp->tipo_operacion;
        ent = temp->entidad_afectada;
        json = temp->datos_json;
        top = top->sigAccion;
        delete temp;
        return true;
    }

    bool estaVacia() const {
        return top == nullptr;
    }

    // CREACION demostrable: reinicia la estructura a estado vacio inicial.
    void crearVacia() { limpiar(); }

    int tamano() const {
        int n = 0;
        NodoAccion* c = top;
        while (c != nullptr) { n++; c = c->sigAccion; }
        return n;
    }

    // CONSULTA no destructiva del tope (para sustentacion punto B).
    bool verTope(string &op, string &ent, string &json) const {
        if (estaVacia()) return false;
        op = top->tipo_operacion;
        ent = top->entidad_afectada;
        json = top->datos_json;
        return true;
    }

    void listar() const {
        cout << "--- Pila Undo (LIFO, tope primero) [" << tamano() << " acciones] ---\n";
        NodoAccion* c = top;
        while (c != nullptr) {
            cout << " #" << c->id_accion << " " << c->tipo_operacion << "/" << c->entidad_afectada << endl;
            c = c->sigAccion;
        }
        if (estaVacia()) cout << " (vacia)\n";
    }

    void limpiar() {
        while (top != nullptr) {
            NodoAccion* temp = top;
            top = top->sigAccion;
            delete temp;
        }
        contador = 0;
    }
};

// ============================================================================
// CLASE COLA FIFO (INGESTA SECUENCIAL)
// ============================================================================

class ColaIngesta {
private:
    NodoTarea* frente;
    NodoTarea* finalCola;

public:
    ColaIngesta() : frente(nullptr), finalCola(nullptr) {}

    ~ColaIngesta() {
        limpiar();
    }

    void encolar(string tipo, string ruta) {
        NodoTarea* nuevo = new NodoTarea(tipo, ruta);
        if (finalCola == nullptr) {
            frente = finalCola = nuevo;
        } else {
            finalCola->sigTarea = nuevo;
            finalCola = nuevo;
        }
    }

    bool desencolar(string &tipo, string &ruta) {
        if (estaVacia()) return false;
        NodoTarea* temp = frente;
        tipo = temp->tipo_origen;
        ruta = temp->ruta_o_url;
        frente = frente->sigTarea;
        if (frente == nullptr) finalCola = nullptr;
        delete temp;
        return true;
    }

    bool estaVacia() const {
        return frente == nullptr;
    }

    // CREACION demostrable: reinicia la cola a estado vacio inicial.
    void crearVacia() { limpiar(); }

    int tamano() const {
        int n = 0;
        NodoTarea* c = frente;
        while (c != nullptr) { n++; c = c->sigTarea; }
        return n;
    }

    // CONSULTA no destructiva del frente (sin desencolar).
    bool verFrente(string &tipo, string &ruta) const {
        if (estaVacia()) return false;
        tipo = frente->tipo_origen;
        ruta = frente->ruta_o_url;
        return true;
    }

    void listarPendientes() const {
        cout << "--- Cola Ingesta (FIFO, frente primero) [" << tamano() << " tareas] ---\n";
        NodoTarea* c = frente;
        int i = 1;
        while (c != nullptr) {
            cout << " " << i << ". [" << c->tipo_origen << "] " << c->ruta_o_url << endl;
            c = c->sigTarea;
            i++;
        }
        if (estaVacia()) cout << " (vacia)\n";
    }

    void limpiar() {
        while (frente != nullptr) {
            NodoTarea* temp = frente;
            frente = frente->sigTarea;
            delete temp;
        }
        finalCola = nullptr;
    }
};

// ============================================================================
// CLASE MULTILISTA ORTOGONAL 3D (HIPERCUBO EN RAM)
// ============================================================================

class MultilistaOrtogonal {
private:
    NodoGrupo* cabeceraGrupos;

public:
    MultilistaOrtogonal() : cabeceraGrupos(nullptr) {}

    ~MultilistaOrtogonal() {
        limpiar();
    }

    NodoGrupo* getCabeceraGrupos() const { return cabeceraGrupos; }

    // CREACION demostrable: deja el hipercubo en estado vacio inicial.
    // La LISTA simple es el bloque base: cada eje (sigGrupo, sigInvestigador,
    // sigProductoGrupo) es una lista enlazada simple; la MULTILISTA las cruza.
    void crearVacia() { limpiar(); }

    // POLITICA DE PROPIEDAD (evita double-free / leaks, ver BUG-03):
    // - Cada NodoProducto tiene UN solo propietario para delete: el eje del GRUPO.
    // - El eje del INVESTIGADOR solo desenlaza (nunca hace delete).
    // - Eliminar un producto = desenlazar de ambos ejes + un unico delete.
    // - Eliminar investigador/grupo en cascada reutiliza esa primitiva.

    // --- MÉTODOS DE BÚSQUEDA ---
    NodoGrupo* buscarGrupo(const string& codigo) {
        NodoGrupo* actual = cabeceraGrupos;
        while (actual != nullptr) {
            if (actual->codigo_grupo == codigo && actual->activo) return actual;
            actual = actual->sigGrupo;
        }
        return nullptr;
    }

    NodoGrupo* buscarGrupoIncluyeInactivos(const string& codigo) {
        NodoGrupo* actual = cabeceraGrupos;
        while (actual != nullptr) {
            if (actual->codigo_grupo == codigo) return actual;
            actual = actual->sigGrupo;
        }
        return nullptr;
    }

    // Busca investigador DENTRO de un grupo (respeta adscripcion N:M).
    NodoInvestigador* buscarInvestigadorEnGrupo(NodoGrupo* g, const string& cod_rh, bool soloActivos = true) {
        if (g == nullptr) return nullptr;
        NodoInvestigador* inv = g->primInvestigador;
        while (inv != nullptr) {
            if (inv->cod_rh == cod_rh && (!soloActivos || inv->activo)) return inv;
            inv = inv->sigInvestigador;
        }
        return nullptr;
    }

    NodoInvestigador* buscarInvestigador(const string& cod_rh) {
        NodoGrupo* g = cabeceraGrupos;
        while (g != nullptr) {
            NodoInvestigador* inv = buscarInvestigadorEnGrupo(g, cod_rh, true);
            if (inv != nullptr) return inv;
            g = g->sigGrupo;
        }
        return nullptr;
    }

    NodoInvestigador* buscarInvestigadorIncluyeInactivos(const string& cod_rh, string* outGrupo = nullptr) {
        NodoGrupo* g = cabeceraGrupos;
        while (g != nullptr) {
            NodoInvestigador* inv = buscarInvestigadorEnGrupo(g, cod_rh, false);
            if (inv != nullptr) {
                if (outGrupo != nullptr) *outGrupo = g->codigo_grupo;
                return inv;
            }
            g = g->sigGrupo;
        }
        return nullptr;
    }

    NodoProducto* buscarProducto(int id_prod) {
        NodoGrupo* g = cabeceraGrupos;
        while (g != nullptr) {
            NodoProducto* p = g->primProducto;
            while (p != nullptr) {
                if (p->id_producto == id_prod && p->activo) return p;
                p = p->sigProductoGrupo;
            }
            g = g->sigGrupo;
        }
        return nullptr;
    }

    NodoProducto* buscarProductoIncluyeInactivos(int id_prod) {
        NodoGrupo* g = cabeceraGrupos;
        while (g != nullptr) {
            NodoProducto* p = g->primProducto;
            while (p != nullptr) {
                if (p->id_producto == id_prod) return p;
                p = p->sigProductoGrupo;
            }
            g = g->sigGrupo;
        }
        return nullptr;
    }

    int maxIdProducto() const {
        int mx = 0;
        NodoGrupo* g = cabeceraGrupos;
        while (g != nullptr) {
            NodoProducto* p = g->primProducto;
            while (p != nullptr) {
                if (p->id_producto > mx) mx = p->id_producto;
                p = p->sigProductoGrupo;
            }
            g = g->sigGrupo;
        }
        return mx;
    }

    // --- MÉTODOS DE INSERCIÓN ---
    bool insertarGrupo(string cod, string nom, string lid, string plan, string lineas) {
        if (buscarGrupoIncluyeInactivos(cod) != nullptr) return false; // codigo duplicado
        NodoGrupo* nuevo = new NodoGrupo(cod, nom, lid, plan, lineas);
        nuevo->sigGrupo = cabeceraGrupos;
        cabeceraGrupos = nuevo;
        return true;
    }

    bool insertarInvestigador(string cod_grupo, string rh, string nom, string mail, string cat, string url) {
        NodoGrupo* g = buscarGrupoIncluyeInactivos(cod_grupo);
        if (g == nullptr) return false;
        // Ya adscrito a ESTE grupo (se permite el mismo rh en OTRO grupo: N:M por copias)
        if (buscarInvestigadorEnGrupo(g, rh, false) != nullptr) return false;

        NodoInvestigador* nuevo = new NodoInvestigador(rh, nom, mail, cat, url);
        nuevo->sigInvestigador = g->primInvestigador;
        g->primInvestigador = nuevo;
        return true;
    }

    // Exige adscripcion: el investigador debe estar adscrito al grupo destino.
    bool insertarProducto(int id, string tit, string tipo, string cat, string val, int anio, string cod_grupo, string cod_rh) {
        NodoGrupo* g = buscarGrupo(cod_grupo);
        if (g == nullptr) return false;
        NodoInvestigador* inv = buscarInvestigadorEnGrupo(g, cod_rh, true);
        if (inv == nullptr) return false; // no adscrito a este grupo
        if (buscarProductoIncluyeInactivos(id) != nullptr) return false; // id duplicado

        NodoProducto* nuevo = new NodoProducto(id, tit, tipo, cat, val, anio, cod_grupo, cod_rh);

        // 1. Enlazar en el eje del Grupo (eje propietario)
        nuevo->sigProductoGrupo = g->primProducto;
        g->primProducto = nuevo;

        // 2. Enlazar en el eje del Investigador (eje no propietario)
        nuevo->sigProductoInvestigador = inv->primProducto;
        inv->primProducto = nuevo;

        return true;
    }

    // --- EDICIÓN (modificación punto 9 y 11) ---
    bool editarGrupo(const string& cod, const string& nom, const string& lid, const string& plan, const string& lineas) {
        NodoGrupo* g = buscarGrupo(cod);
        if (g == nullptr) return false;
        if (!nom.empty()) g->nombre = nom;
        if (!lid.empty()) g->lider = lid;
        if (!plan.empty()) g->plan_investigacion = plan;
        if (!lineas.empty()) g->lineas_estrategicas = lineas;
        return true;
    }

    bool editarInvestigador(const string& cod_rh, const string& nom, const string& mail, const string& cat, const string& url) {
        bool tocado = false;
        NodoGrupo* g = cabeceraGrupos;
        while (g != nullptr) {
            NodoInvestigador* inv = buscarInvestigadorEnGrupo(g, cod_rh, true);
            if (inv != nullptr) {
                if (!nom.empty()) inv->nombre_completo = nom;
                if (!mail.empty()) inv->correo = mail;
                if (!cat.empty()) inv->categoria_minciencias = cat;
                if (!url.empty()) inv->cvlac_url = url;
                tocado = true;
            }
            g = g->sigGrupo;
        }
        return tocado;
    }

    bool editarProducto(int id, const string& tit, const string& tipo, const string& cat, const string& val, int anio /*-1=no cambia*/) {
        NodoProducto* p = buscarProducto(id);
        if (p == nullptr) return false;
        if (!tit.empty()) p->titulo = tit;
        if (!tipo.empty()) p->tipo_producto = tipo;
        if (!cat.empty()) p->categoria = cat;
        if (!val.empty()) p->estado_validacion = val;
        if (anio > 0) p->anio_publicacion = anio;
        return true;
    }

    // --- BORRADO LÓGICO / REACTIVACIÓN ---
    bool desactivarGrupo(const string& cod) {
        NodoGrupo* g = buscarGrupo(cod);
        if (g == nullptr) return false;
        g->activo = false;
        return true;
    }
    bool reactivarGrupo(const string& cod) {
        NodoGrupo* g = buscarGrupoIncluyeInactivos(cod);
        if (g == nullptr || g->activo) return false;
        g->activo = true;
        return true;
    }
    bool desactivarInvestigador(const string& cod_rh) {
        bool tocado = false;
        NodoGrupo* g = cabeceraGrupos;
        while (g != nullptr) {
            NodoInvestigador* inv = buscarInvestigadorEnGrupo(g, cod_rh, true);
            if (inv != nullptr) { inv->activo = false; tocado = true; }
            g = g->sigGrupo;
        }
        return tocado;
    }
    bool reactivarInvestigador(const string& cod_rh) {
        bool tocado = false;
        NodoGrupo* g = cabeceraGrupos;
        while (g != nullptr) {
            NodoInvestigador* inv = buscarInvestigadorEnGrupo(g, cod_rh, false);
            if (inv != nullptr && !inv->activo) { inv->activo = true; tocado = true; }
            g = g->sigGrupo;
        }
        return tocado;
    }
    bool desactivarProducto(int id_prod) {
        NodoProducto* p = buscarProducto(id_prod);
        if (p == nullptr) return false;
        p->activo = false;
        return true;
    }
    bool reactivarProducto(int id_prod) {
        NodoProducto* p = buscarProductoIncluyeInactivos(id_prod);
        if (p == nullptr || p->activo) return false;
        p->activo = true;
        return true;
    }

    // --- ELIMINACIÓN FÍSICA (con desenlace en ambos ejes, un solo delete) ---
    static void desenlazarProductoDeInvestigador(NodoInvestigador* inv, NodoProducto* target) {
        if (inv == nullptr || target == nullptr) return;
        NodoProducto* prev = nullptr;
        NodoProducto* cur = inv->primProducto;
        while (cur != nullptr) {
            if (cur == target) {
                if (prev == nullptr) inv->primProducto = cur->sigProductoInvestigador;
                else prev->sigProductoInvestigador = cur->sigProductoInvestigador;
                cur->sigProductoInvestigador = nullptr;
                return;
            }
            prev = cur;
            cur = cur->sigProductoInvestigador;
        }
    }

    // Elimina un producto: lo desenlaza del grupo y de su investigador y hace UN delete.
    bool eliminarProductoFisico(int id_prod) {
        NodoGrupo* g = cabeceraGrupos;
        while (g != nullptr) {
            NodoProducto* prev = nullptr;
            NodoProducto* cur = g->primProducto;
            while (cur != nullptr) {
                if (cur->id_producto == id_prod) {
                    // 1. Desenlazar del eje investigador (sin delete)
                    NodoGrupo* gi = cabeceraGrupos;
                    while (gi != nullptr) {
                        NodoInvestigador* inv = buscarInvestigadorEnGrupo(gi, cur->cod_rh_investigador_fk, false);
                        if (inv != nullptr) desenlazarProductoDeInvestigador(inv, cur);
                        gi = gi->sigGrupo;
                    }
                    // 2. Desenlazar del eje grupo y liberar (único owner)
                    if (prev == nullptr) g->primProducto = cur->sigProductoGrupo;
                    else prev->sigProductoGrupo = cur->sigProductoGrupo;
                    cur->sigProductoGrupo = nullptr;
                    delete cur;
                    return true;
                }
                prev = cur;
                cur = cur->sigProductoGrupo;
            }
            g = g->sigGrupo;
        }
        return false;
    }

    // Elimina al investigador de UN grupo (solo esa adscripción). En cascada elimina
    // sus productos de ese grupo usando eliminarProductoFisico.
    bool eliminarInvestigadorDeGrupo(const string& cod_grupo, const string& cod_rh) {
        NodoGrupo* g = buscarGrupoIncluyeInactivos(cod_grupo);
        if (g == nullptr) return false;
        NodoInvestigador* inv = buscarInvestigadorEnGrupo(g, cod_rh, false);
        if (inv == nullptr) return false;
        // 1. Productos de este investigador en este grupo
        vector<int> ids;
        NodoProducto* p = inv->primProducto;
        while (p != nullptr) {
            if (p->codigo_grupo_fk == cod_grupo) ids.push_back(p->id_producto);
            p = p->sigProductoInvestigador;
        }
        for (size_t i = 0; i < ids.size(); i++) eliminarProductoFisico(ids[i]);
        // 2. Desenlazar nodo investigador y liberar
        NodoInvestigador* prev = nullptr;
        NodoInvestigador* cur = g->primInvestigador;
        while (cur != nullptr) {
            if (cur == inv) {
                if (prev == nullptr) g->primInvestigador = cur->sigInvestigador;
                else prev->sigInvestigador = cur->sigInvestigador;
                delete cur;
                return true;
            }
            prev = cur;
            cur = cur->sigInvestigador;
        }
        return false;
    }

    // Elimina un grupo en cascada: productos, adscripciones y nodo grupo.
    bool eliminarGrupoFisico(const string& cod) {
        // 1. Eliminar todos sus productos (cada uno desenlaza ambos ejes)
        NodoGrupo* g = buscarGrupoIncluyeInactivos(cod);
        if (g == nullptr) return false;
        while (g->primProducto != nullptr) {
            eliminarProductoFisico(g->primProducto->id_producto);
        }
        // 2. Liberar nodos investigador de este grupo (ya sin productos)
        NodoInvestigador* inv = g->primInvestigador;
        while (inv != nullptr) {
            NodoInvestigador* t = inv;
            inv = inv->sigInvestigador;
            delete t;
        }
        g->primInvestigador = nullptr;
        // 3. Desenlazar y liberar nodo grupo
        NodoGrupo* prev = nullptr;
        NodoGrupo* cur = cabeceraGrupos;
        while (cur != nullptr) {
            if (cur == g) {
                if (prev == nullptr) cabeceraGrupos = cur->sigGrupo;
                else prev->sigGrupo = cur->sigGrupo;
                delete cur;
                return true;
            }
            prev = cur;
            cur = cur->sigGrupo;
        }
        return false;
    }

    // --- CONSULTAS Y TABLAS ESTADÍSTICAS ---
    void listarGrupos() const {
        // Sin codigos a la vista: numero + nombre + lider (los codigos quedan internos).
        // Tablas anchas (~109): ensanchar la terminal para verlas sin cortes.
        const vector<size_t> W = {3, 64, 32};
        cout << "\n" << bordeTabla(W, '=') << "\n";
        cout << tituloTabla("LISTADO DE GRUPOS DE INVESTIGACION", W) << "\n";
        cout << bordeTabla(W, '=') << "\n";
        cout << filaTabla({"No.", "GRUPO", "LIDER"}, W) << "\n";
        cout << bordeTabla(W, '-') << "\n";
        NodoGrupo* g = cabeceraGrupos;
        int count = 0;
        while (g != nullptr) {
            if (g->activo) {
                count++;
                vector<string> f;
                f.push_back(to_string(count));
                f.push_back(g->nombre);
                f.push_back(g->lider);
                cout << filaTabla(f, W) << "\n";
            }
            g = g->sigGrupo;
        }
        cout << bordeTabla(W, '-') << "\n";
        cout << "Total Grupos Activos: " << count << endl;
    }

    void listarProductosPorVentanaAnios(int anioInicio, int anioFin) const {
        // Tablas anchas (~110). Headers ASCII.
        const vector<size_t> W = {5, 50, 11, 5, 6, 14};
        cout << "\n" << bordeTabla(W, '=') << "\n";
        cout << tituloTabla("FILTRO PRODUCCION CIENTIFICA", W) << "\n";
        cout << tituloTabla("Ventana: " + to_string(anioInicio) + " - " + to_string(anioFin), W) << "\n";
        cout << bordeTabla(W, '=') << "\n";
        cout << filaTabla({"ID", "TITULO", "TIPO", "CAT", "ANIO", "GRUPO"}, W) << "\n";
        cout << bordeTabla(W, '-') << "\n";

        NodoGrupo* g = cabeceraGrupos;
        int count = 0;
        while (g != nullptr) {
            if (g->activo) {
                NodoProducto* p = g->primProducto;
                while (p != nullptr) {
                    if (p->activo && p->anio_publicacion >= anioInicio && p->anio_publicacion <= anioFin) {
                        vector<string> f;
                        f.push_back(to_string(p->id_producto));
                        f.push_back(p->titulo);
                        f.push_back(p->tipo_producto);
                        f.push_back(p->categoria);
                        f.push_back(to_string(p->anio_publicacion));
                        f.push_back(etiquetaGrupo(p->codigo_grupo_fk));
                        cout << filaTabla(f, W) << "\n";
                        count++;
                    }
                    p = p->sigProductoGrupo;
                }
            }
            g = g->sigGrupo;
        }
        cout << bordeTabla(W, '-') << "\n";
        cout << "Total Productos Encontrados: " << count << endl;
    }

    void generarResumenEstadistico() const {
        // Tablas anchas (~99).
        const vector<size_t> W = {22, 70};
        cout << "\n" << bordeTabla(W, '=') << "\n";
        cout << tituloTabla("RESUMEN ESTADISTICO DESCRIPTIVO (12.a)", W) << "\n";
        cout << bordeTabla(W, '=') << "\n";

        NodoGrupo* g = cabeceraGrupos;
        while (g != nullptr) {
            if (g->activo) {
                int totalProd = 0, catA1 = 0, catA = 0, catB = 0, catC = 0;
                int totalInv = 0;

                // Contar investigadores
                NodoInvestigador* inv = g->primInvestigador;
                while (inv != nullptr) {
                    if (inv->activo) totalInv++;
                    inv = inv->sigInvestigador;
                }

                // Contar productos y categorías
                NodoProducto* p = g->primProducto;
                while (p != nullptr) {
                    if (p->activo) {
                        totalProd++;
                        if (p->categoria == "A1") catA1++;
                        else if (p->categoria == "A") catA++;
                        else if (p->categoria == "B") catB++;
                        else if (p->categoria == "C") catC++;
                    }
                    p = p->sigProductoGrupo;
                }

                cout << tituloTabla("[GRUPO] " + g->nombre, W) << "\n";
                cout << filaTabla({"Lider:", g->lider}, W) << "\n";
                cout << filaTabla({"Investigadores:", to_string(totalInv)}, W) << "\n";
                cout << filaTabla({"Produccion total:", to_string(totalProd)}, W) << "\n";
                cout << filaTabla({"Categorias:", "A1:" + to_string(catA1) + " A:" + to_string(catA) +
                              " B:" + to_string(catB) + " C:" + to_string(catC)}, W) << "\n";
                cout << bordeTabla(W, '-') << "\n";
            }
            g = g->sigGrupo;
        }
    }

    void listarInvestigadores(bool incluirInactivos = false) const {
        // Tablas anchas (~91). Headers ASCII.
        const vector<size_t> W = {12, 44, 14, 8};
        cout << "\n" << bordeTabla(W, '=') << "\n";
        cout << tituloTabla("LISTADO DE INVESTIGADORES (por grupo)", W) << "\n";
        cout << bordeTabla(W, '=') << "\n";
        NodoGrupo* g = cabeceraGrupos;
        int count = 0;
        while (g != nullptr) {
            if (g->activo) {
                cout << tituloTabla("Grupo: " + g->nombre, W) << "\n";
                cout << filaTabla({"COD_RH", "NOMBRE", "CATEGORIA", "ESTADO"}, W) << "\n";
                cout << bordeTabla(W, '-') << "\n";
                NodoInvestigador* inv = g->primInvestigador;
                while (inv != nullptr) {
                    if (inv->activo || incluirInactivos) {
                        vector<string> f;
                        f.push_back(inv->cod_rh);
                        f.push_back(inv->nombre_completo);
                        f.push_back(inv->categoria_minciencias);
                        f.push_back(inv->activo ? "ACTIVO" : "INACTIVO");
                        cout << filaTabla(f, W) << "\n";
                        count++;
                    }
                    inv = inv->sigInvestigador;
                }
            }
            g = g->sigGrupo;
        }
        cout << bordeTabla(W, '-') << "\nTotal: " << count << endl;
    }

    // Enlista SOLO los investigadores del grupo indicado (el usuario lo elige por numero antes).
    void listarInvestigadoresDeGrupo(const string& cod, bool incluirInactivos = false) const {
        NodoGrupo* g = cabeceraGrupos;
        while (g != nullptr && g->codigo_grupo != cod) g = g->sigGrupo;
        if (g == nullptr) { cout << "[ERROR] Grupo no encontrado.\n"; return; }
        const vector<size_t> W = {12, 44, 14, 8};
        cout << "\n" << bordeTabla(W, '=') << "\n";
        cout << tituloTabla("INVESTIGADORES DE: " + g->nombre, W) << "\n";
        cout << bordeTabla(W, '=') << "\n";
        cout << filaTabla({"COD_RH", "NOMBRE", "CATEGORIA", "ESTADO"}, W) << "\n";
        cout << bordeTabla(W, '-') << "\n";
        int count = 0;
        NodoInvestigador* inv = g->primInvestigador;
        while (inv != nullptr) {
            if (inv->activo || incluirInactivos) {
                vector<string> f;
                f.push_back(inv->cod_rh);
                f.push_back(inv->nombre_completo);
                f.push_back(inv->categoria_minciencias);
                f.push_back(inv->activo ? "ACTIVO" : "INACTIVO");
                cout << filaTabla(f, W) << "\n";
                count++;
            }
            inv = inv->sigInvestigador;
        }
        cout << bordeTabla(W, '-') << "\nTotal: " << count << endl;
    }

    // Etiqueta corta del grupo para tablas (sigla -XXX- o nombre). Sin codigos a la vista.
    string etiquetaGrupo(const string& cod) const {
        NodoGrupo* g = cabeceraGrupos;
        while (g != nullptr) {
            if (g->codigo_grupo == cod) {
                const string& n = g->nombre;
                if (!n.empty() && n[n.size() - 1] == '-') {
                    size_t fin = n.size() - 1;
                    size_t ini = fin;
                    while (ini > 0 && ((n[ini-1] >= 'A' && n[ini-1] <= 'Z') || (n[ini-1] >= '0' && n[ini-1] <= '9'))) ini--;
                    if (ini > 0 && n[ini-1] == '-' && (fin - ini) >= 2 && (fin - ini) <= 12) {
                        string sig;
                        for (size_t k = ini; k < fin; k++) sig += n[k];
                        return sig;
                    }
                }
                return n;
            }
            g = g->sigGrupo;
        }
        return cod;
    }

    void listarProductos(bool incluirInactivos = false) const {
        // Tablas anchas (~111). Headers ASCII.
        const vector<size_t> W = {5, 34, 11, 5, 11, 6, 4, 10};
        cout << "\n" << bordeTabla(W, '=') << "\n";
        cout << tituloTabla("LISTADO DE PRODUCTOS (por grupo)", W) << "\n";
        cout << bordeTabla(W, '=') << "\n";
        cout << filaTabla({"ID", "TITULO", "TIPO", "CAT", "VALID", "ANIO", "EST", "GRUPO"}, W) << "\n";
        cout << bordeTabla(W, '-') << "\n";
        NodoGrupo* g = cabeceraGrupos;
        int count = 0;
        while (g != nullptr) {
            NodoProducto* p = g->primProducto;
            while (p != nullptr) {
                if (p->activo || incluirInactivos) {
                    vector<string> f;
                    f.push_back(to_string(p->id_producto));
                    f.push_back(p->titulo);
                    f.push_back(p->tipo_producto);
                    f.push_back(p->categoria);
                    f.push_back(p->estado_validacion);
                    f.push_back(to_string(p->anio_publicacion));
                    f.push_back(p->activo ? "ACT" : "INA");
                    f.push_back(etiquetaGrupo(p->codigo_grupo_fk));
                    cout << filaTabla(f, W) << "\n";
                    count++;
                }
                p = p->sigProductoGrupo;
            }
            g = g->sigGrupo;
        }
        cout << bordeTabla(W, '-') << "\nTotal: " << count << endl;
    }

    // Enlista SOLO los productos del grupo indicado (el usuario lo elige por numero antes).
    void listarProductosDeGrupo(const string& cod, bool incluirInactivos = false) const {
        NodoGrupo* g = cabeceraGrupos;
        while (g != nullptr && g->codigo_grupo != cod) g = g->sigGrupo;
        if (g == nullptr) { cout << "[ERROR] Grupo no encontrado.\n"; return; }
        const vector<size_t> W = {5, 44, 11, 5, 11, 6, 4};
        cout << "\n" << bordeTabla(W, '=') << "\n";
        cout << tituloTabla("PRODUCTOS DE: " + g->nombre, W) << "\n";
        cout << bordeTabla(W, '=') << "\n";
        cout << filaTabla({"ID", "TITULO", "TIPO", "CAT", "VALID", "ANIO", "EST"}, W) << "\n";
        cout << bordeTabla(W, '-') << "\n";
        int count = 0;
        NodoProducto* p = g->primProducto;
        while (p != nullptr) {
            if (p->activo || incluirInactivos) {
                vector<string> f;
                f.push_back(to_string(p->id_producto));
                f.push_back(p->titulo);
                f.push_back(p->tipo_producto);
                f.push_back(p->categoria);
                f.push_back(p->estado_validacion);
                f.push_back(to_string(p->anio_publicacion));
                f.push_back(p->activo ? "ACT" : "INA");
                cout << filaTabla(f, W) << "\n";
                count++;
            }
            p = p->sigProductoGrupo;
        }
        cout << bordeTabla(W, '-') << "\nTotal: " << count << endl;
    }

    void verDetalleGrupo(const string& cod) const {
        NodoGrupo* g = cabeceraGrupos;
        while (g != nullptr && g->codigo_grupo != cod) g = g->sigGrupo;
        if (g == nullptr) { cout << "[ERROR] Grupo no encontrado.\n"; return; }
        cout << "\n=== GRUPO [" << g->codigo_grupo << "] " << g->nombre << " ===\n";
        cout << "Lider: " << g->lider << "\nPlan: " << g->plan_investigacion
             << "\nLineas: " << g->lineas_estrategicas
             << "\nEstado: " << (g->activo ? "ACTIVO" : "INACTIVO") << "\n";
        cout << "--- Integrantes ---\n";
        NodoInvestigador* inv = g->primInvestigador;
        while (inv != nullptr) {
            cout << " * [" << inv->cod_rh << "] " << inv->nombre_completo << " (" << inv->categoria_minciencias << ")"
                 << (inv->activo ? "" : " INACTIVO") << endl;
            inv = inv->sigInvestigador;
        }
        cout << "--- Productos ---\n";
        NodoProducto* p = g->primProducto;
        while (p != nullptr) {
            cout << " * (" << p->id_producto << ") " << p->titulo << " [" << p->categoria << "/" << p->estado_validacion << "/" << p->anio_publicacion << "]"
                 << (p->activo ? "" : " INACTIVO") << endl;
            p = p->sigProductoGrupo;
        }
    }

    void verDetalleInvestigador(const string& rh) const {
        bool hallado = false;
        NodoGrupo* g = cabeceraGrupos;
        while (g != nullptr) {
            NodoInvestigador* inv = g->primInvestigador;
            while (inv != nullptr) {
                if (inv->cod_rh == rh) {
                    if (!hallado) {
                        cout << "\n=== INVESTIGADOR [" << inv->cod_rh << "] " << inv->nombre_completo << " ===\n";
                        cout << "Correo: " << inv->correo << "\nCategoria: " << inv->categoria_minciencias
                             << "\nCvLAC: " << inv->cvlac_url << endl;
                        hallado = true;
                    }
                    cout << " Adscrito a [" << g->codigo_grupo << "] " << g->nombre
                         << (inv->activo ? "" : " (INACTIVO en este grupo)") << endl;
                    NodoProducto* p = inv->primProducto;
                    while (p != nullptr) {
                        cout << "   - (" << p->id_producto << ") " << p->titulo << " [" << p->anio_publicacion << "]" << endl;
                        p = p->sigProductoInvestigador;
                    }
                }
                inv = inv->sigInvestigador;
            }
            g = g->sigGrupo;
        }
        if (!hallado) cout << "[ERROR] Investigador no encontrado.\n";
    }

    void verDetalleProducto(int id) const {
        NodoGrupo* g = cabeceraGrupos;
        while (g != nullptr) {
            NodoProducto* p = g->primProducto;
            while (p != nullptr) {
                if (p->id_producto == id) {
                    cout << "\n=== PRODUCTO (" << p->id_producto << ") ===\nTitulo: " << p->titulo
                         << "\nTipo: " << p->tipo_producto << "\nCategoria: " << p->categoria
                         << "\nValidacion: " << p->estado_validacion << "\nAnio: " << p->anio_publicacion
                         << "\nGrupo: " << p->codigo_grupo_fk << "\nInvestigador: " << p->cod_rh_investigador_fk
                         << "\nEstado: " << (p->activo ? "ACTIVO" : "INACTIVO") << endl;
                    return;
                }
                p = p->sigProductoGrupo;
            }
            g = g->sigGrupo;
        }
        cout << "[ERROR] Producto no encontrado.\n";
    }

    void limpiar() {
        NodoGrupo* g = cabeceraGrupos;
        while (g != nullptr) {
            // Liberar Investigadores (sus listas de productos solo desenlazan, no liberan)
            NodoInvestigador* inv = g->primInvestigador;
            while (inv != nullptr) {
                NodoInvestigador* tempInv = inv;
                inv = inv->sigInvestigador;
                tempInv->primProducto = nullptr; // evitar colgantes
                delete tempInv;
            }
            // Liberar Productos: unico owner es el eje del grupo
            NodoProducto* p = g->primProducto;
            while (p != nullptr) {
                NodoProducto* tempP = p;
                p = p->sigProductoGrupo;
                delete tempP;
            }
            NodoGrupo* tempG = g;
            g = g->sigGrupo;
            delete tempG;
        }
        cabeceraGrupos = nullptr;
    }
};

// ============================================================================
// GESTOR DE PERSISTENCIA SQLITE (SQLite3 C-API)
// ============================================================================

class GestorSQLite {
private:
    sqlite3* db;
    string dbPath;

public:
    GestorSQLite(string path) : db(nullptr), dbPath(path) {}

    ~GestorSQLite() {
        desconectar();
    }

    bool conectar() {
        int rc = sqlite3_open(dbPath.c_str(), &db);
        if (rc != SQLITE_OK) {
            cerr << "[ERROR SQLITE] No se pudo abrir la BD: " << sqlite3_errmsg(db) << endl;
            return false;
        }
        // Activar modo WAL y busy timeout para concurrencia (Blindaje BUG-01)
        sqlite3_exec(db, "PRAGMA journal_mode=WAL;", nullptr, nullptr, nullptr);
        sqlite3_exec(db, "PRAGMA busy_timeout=5000;", nullptr, nullptr, nullptr);
        sqlite3_exec(db, "PRAGMA foreign_keys=ON;", nullptr, nullptr, nullptr);
        return true;
    }

    void desconectar() {
        if (db != nullptr) {
            sqlite3_close(db);
            db = nullptr;
        }
    }

    static string colText(sqlite3_stmt* s, int c) {
        const unsigned char* t = sqlite3_column_text(s, c);
        return t ? (const char*)t : "";
    }

    bool cargarEnMultilista(MultilistaOrtogonal& multilista) {
        if (db == nullptr) return false;
        multilista.limpiar();

        // 1. Grupos (incluye inactivos; la RAM conserva el flag)
        sqlite3_stmt* stmtG;
        const char* sqlG = "SELECT codigo_grupo, nombre, lider, plan_investigacion, lineas_estrategicas, estado FROM Grupos;";
        if (sqlite3_prepare_v2(db, sqlG, -1, &stmtG, nullptr) == SQLITE_OK) {
            while (sqlite3_step(stmtG) == SQLITE_ROW) {
                multilista.insertarGrupo(colText(stmtG,0), colText(stmtG,1), colText(stmtG,2), colText(stmtG,3), colText(stmtG,4));
                if (sqlite3_column_int(stmtG, 5) == 0)
                    multilista.desactivarGrupo(colText(stmtG,0));
            }
            sqlite3_finalize(stmtG);
        }

        // 2. Investigadores via junction N:M (FIX C-2: sin duplicar en todos los grupos)
        sqlite3_stmt* stmtI;
        const char* sqlI = "SELECT gi.codigo_grupo_fk, i.cod_rh, i.nombre_completo, i.correo, i.categoria_minciencias, i.cvlac_url, i.estado "
                           "FROM grupo_investigador gi JOIN Investigadores i ON i.cod_rh = gi.cod_rh_fk;";
        if (sqlite3_prepare_v2(db, sqlI, -1, &stmtI, nullptr) == SQLITE_OK) {
            while (sqlite3_step(stmtI) == SQLITE_ROW) {
                string grp = colText(stmtI, 0);
                string rh = colText(stmtI, 1);
                multilista.insertarInvestigador(grp, rh, colText(stmtI,2), colText(stmtI,3), colText(stmtI,4), colText(stmtI,5));
                if (sqlite3_column_int(stmtI, 6) == 0)
                    multilista.desactivarInvestigador(rh);
            }
            sqlite3_finalize(stmtI);
        }

        // 3. Productos (incluye inactivos)
        sqlite3_stmt* stmtP;
        // S30: orden cronologico descendente (lo nuevo primero) en TODAS las vistas que usan esta carga.
        const char* sqlP = "SELECT id_producto, titulo, tipo_producto, categoria, estado_validacion, anio_publicacion, codigo_grupo_fk, cod_rh_investigador_fk, estado FROM Productos ORDER BY anio_publicacion DESC;";
        if (sqlite3_prepare_v2(db, sqlP, -1, &stmtP, nullptr) == SQLITE_OK) {
            while (sqlite3_step(stmtP) == SQLITE_ROW) {
                int id = sqlite3_column_int(stmtP, 0);
                int est = sqlite3_column_int(stmtP, 8);
                multilista.insertarProducto(id, colText(stmtP,1), colText(stmtP,2), colText(stmtP,3), colText(stmtP,4),
                                            sqlite3_column_int(stmtP,5), colText(stmtP,6), colText(stmtP,7));
                if (est == 0) {
                    NodoProducto* p = multilista.buscarProductoIncluyeInactivos(id);
                    if (p != nullptr) p->activo = false;
                }
            }
            sqlite3_finalize(stmtP);
        }
        return true;
    }

    // ---- Altas ----
    bool guardarNuevoGrupo(const string& cod, const string& nom, const string& lid, const string& plan, const string& lineas) {
        if (db == nullptr) return false;
        const char* sql = "INSERT OR IGNORE INTO Grupos (codigo_grupo, nombre, lider, plan_investigacion, lineas_estrategicas, estado) VALUES (?,?,?,?,?,1);";
        sqlite3_stmt* st;
        if (sqlite3_prepare_v2(db, sql, -1, &st, nullptr) != SQLITE_OK) return false;
        sqlite3_bind_text(st,1,cod.c_str(),-1,SQLITE_TRANSIENT);
        sqlite3_bind_text(st,2,nom.c_str(),-1,SQLITE_TRANSIENT);
        sqlite3_bind_text(st,3,lid.c_str(),-1,SQLITE_TRANSIENT);
        sqlite3_bind_text(st,4,plan.c_str(),-1,SQLITE_TRANSIENT);
        sqlite3_bind_text(st,5,lineas.c_str(),-1,SQLITE_TRANSIENT);
        bool ok = (sqlite3_step(st) == SQLITE_DONE && sqlite3_changes(db) > 0);
        sqlite3_finalize(st);
        return ok;
    }
    bool guardarNuevoInvestigador(const string& rh, const string& nom, const string& mail, const string& cat, const string& url) {
        if (db == nullptr) return false;
        const char* sql = "INSERT OR IGNORE INTO Investigadores (cod_rh, nombre_completo, correo, categoria_minciencias, cvlac_url, estado) VALUES (?,?,?,?,?,1);";
        sqlite3_stmt* st;
        if (sqlite3_prepare_v2(db, sql, -1, &st, nullptr) != SQLITE_OK) return false;
        sqlite3_bind_text(st,1,rh.c_str(),-1,SQLITE_TRANSIENT);
        sqlite3_bind_text(st,2,nom.c_str(),-1,SQLITE_TRANSIENT);
        sqlite3_bind_text(st,3,mail.c_str(),-1,SQLITE_TRANSIENT);
        sqlite3_bind_text(st,4,cat.c_str(),-1,SQLITE_TRANSIENT);
        sqlite3_bind_text(st,5,url.c_str(),-1,SQLITE_TRANSIENT);
        bool ok = (sqlite3_step(st) == SQLITE_DONE);
        sqlite3_finalize(st);
        return ok;
    }
    bool guardarAdscripcion(const string& codGrupo, const string& rh) {
        if (db == nullptr) return false;
        const char* sql = "INSERT OR IGNORE INTO grupo_investigador (codigo_grupo_fk, cod_rh_fk) VALUES (?,?);";
        sqlite3_stmt* st;
        if (sqlite3_prepare_v2(db, sql, -1, &st, nullptr) != SQLITE_OK) return false;
        sqlite3_bind_text(st,1,codGrupo.c_str(),-1,SQLITE_TRANSIENT);
        sqlite3_bind_text(st,2,rh.c_str(),-1,SQLITE_TRANSIENT);
        bool ok = (sqlite3_step(st) == SQLITE_DONE);
        sqlite3_finalize(st);
        return ok;
    }
    // Devuelve el id real (last_insert_rowid) para sincronizar RAM<->BD (FIX C-4).
    long long guardarNuevoProducto(const string& tit, const string& tipo, const string& cat, const string& val, int anio, const string& grp, const string& inv) {
        if (db == nullptr) return -1;
        const char* sql = "INSERT INTO Productos (titulo, tipo_producto, categoria, estado_validacion, anio_publicacion, codigo_grupo_fk, cod_rh_investigador_fk, estado) VALUES (?,?,?,?,?,?,?,1);";
        sqlite3_stmt* st;
        if (sqlite3_prepare_v2(db, sql, -1, &st, nullptr) != SQLITE_OK) return -1;
        sqlite3_bind_text(st,1,tit.c_str(),-1,SQLITE_TRANSIENT);
        sqlite3_bind_text(st,2,tipo.c_str(),-1,SQLITE_TRANSIENT);
        sqlite3_bind_text(st,3,cat.c_str(),-1,SQLITE_TRANSIENT);
        sqlite3_bind_text(st,4,val.c_str(),-1,SQLITE_TRANSIENT);
        sqlite3_bind_int(st,5,anio);
        sqlite3_bind_text(st,6,grp.c_str(),-1,SQLITE_TRANSIENT);
        sqlite3_bind_text(st,7,inv.c_str(),-1,SQLITE_TRANSIENT);
        bool ok = (sqlite3_step(st) == SQLITE_DONE);
        sqlite3_finalize(st);
        return ok ? sqlite3_last_insert_rowid(db) : -1;
    }
    // ---- Actualizaciones ----
    bool actualizarGrupo(const string& cod, const string& nom, const string& lid, const string& plan, const string& lineas) {
        if (db == nullptr) return false;
        const char* sql = "UPDATE Grupos SET nombre=?, lider=?, plan_investigacion=?, lineas_estrategicas=? WHERE codigo_grupo=?;";
        sqlite3_stmt* st;
        if (sqlite3_prepare_v2(db, sql, -1, &st, nullptr) != SQLITE_OK) return false;
        sqlite3_bind_text(st,1,nom.c_str(),-1,SQLITE_TRANSIENT);
        sqlite3_bind_text(st,2,lid.c_str(),-1,SQLITE_TRANSIENT);
        sqlite3_bind_text(st,3,plan.c_str(),-1,SQLITE_TRANSIENT);
        sqlite3_bind_text(st,4,lineas.c_str(),-1,SQLITE_TRANSIENT);
        sqlite3_bind_text(st,5,cod.c_str(),-1,SQLITE_TRANSIENT);
        bool ok = (sqlite3_step(st) == SQLITE_DONE);
        sqlite3_finalize(st);
        return ok;
    }
    bool actualizarInvestigador(const string& rh, const string& nom, const string& mail, const string& cat, const string& url) {
        if (db == nullptr) return false;
        const char* sql = "UPDATE Investigadores SET nombre_completo=?, correo=?, categoria_minciencias=?, cvlac_url=? WHERE cod_rh=?;";
        sqlite3_stmt* st;
        if (sqlite3_prepare_v2(db, sql, -1, &st, nullptr) != SQLITE_OK) return false;
        sqlite3_bind_text(st,1,nom.c_str(),-1,SQLITE_TRANSIENT);
        sqlite3_bind_text(st,2,mail.c_str(),-1,SQLITE_TRANSIENT);
        sqlite3_bind_text(st,3,cat.c_str(),-1,SQLITE_TRANSIENT);
        sqlite3_bind_text(st,4,url.c_str(),-1,SQLITE_TRANSIENT);
        sqlite3_bind_text(st,5,rh.c_str(),-1,SQLITE_TRANSIENT);
        bool ok = (sqlite3_step(st) == SQLITE_DONE);
        sqlite3_finalize(st);
        return ok;
    }
    bool actualizarProducto(int id, const string& tit, const string& tipo, const string& cat, const string& val, int anio) {
        if (db == nullptr) return false;
        const char* sql = "UPDATE Productos SET titulo=?, tipo_producto=?, categoria=?, estado_validacion=?, anio_publicacion=? WHERE id_producto=?;";
        sqlite3_stmt* st;
        if (sqlite3_prepare_v2(db, sql, -1, &st, nullptr) != SQLITE_OK) return false;
        sqlite3_bind_text(st,1,tit.c_str(),-1,SQLITE_TRANSIENT);
        sqlite3_bind_text(st,2,tipo.c_str(),-1,SQLITE_TRANSIENT);
        sqlite3_bind_text(st,3,cat.c_str(),-1,SQLITE_TRANSIENT);
        sqlite3_bind_text(st,4,val.c_str(),-1,SQLITE_TRANSIENT);
        sqlite3_bind_int(st,5,anio);
        sqlite3_bind_int(st,6,id);
        bool ok = (sqlite3_step(st) == SQLITE_DONE);
        sqlite3_finalize(st);
        return ok;
    }
    bool setEstado(const string& tabla, const string& colId, const string& idTxt, int estado) {
        if (db == nullptr) return false;
        string sql = "UPDATE " + tabla + " SET estado=" + (estado ? "1" : "0") + " WHERE " + colId + "=?;";
        sqlite3_stmt* st;
        if (sqlite3_prepare_v2(db, sql.c_str(), -1, &st, nullptr) != SQLITE_OK) return false;
        if (colId == "id_producto") sqlite3_bind_int(st, 1, atoi(idTxt.c_str()));
        else sqlite3_bind_text(st, 1, idTxt.c_str(), -1, SQLITE_TRANSIENT);
        bool ok = (sqlite3_step(st) == SQLITE_DONE);
        sqlite3_finalize(st);
        return ok;
    }
    // ---- Bajas físicas ----
    bool eliminarProductoDB(int id) {
        if (db == nullptr) return false;
        const char* sql = "DELETE FROM Productos WHERE id_producto=?;";
        sqlite3_stmt* st;
        if (sqlite3_prepare_v2(db, sql, -1, &st, nullptr) != SQLITE_OK) return false;
        sqlite3_bind_int(st, 1, id);
        bool ok = (sqlite3_step(st) == SQLITE_DONE);
        sqlite3_finalize(st);
        return ok;
    }
    bool eliminarAdscripcionDB(const string& codGrupo, const string& rh) {
        if (db == nullptr) return false;
        const char* sql = "DELETE FROM grupo_investigador WHERE codigo_grupo_fk=? AND cod_rh_fk=?;";
        sqlite3_stmt* st;
        if (sqlite3_prepare_v2(db, sql, -1, &st, nullptr) != SQLITE_OK) return false;
        sqlite3_bind_text(st,1,codGrupo.c_str(),-1,SQLITE_TRANSIENT);
        sqlite3_bind_text(st,2,rh.c_str(),-1,SQLITE_TRANSIENT);
        bool ok = (sqlite3_step(st) == SQLITE_DONE);
        sqlite3_finalize(st);
        // Si ya no le quedan grupos, borrar la fila del investigador (evita huerfanos)
        const char* sql2 = "DELETE FROM Investigadores WHERE cod_rh=? AND NOT EXISTS (SELECT 1 FROM grupo_investigador WHERE cod_rh_fk=?);";
        sqlite3_stmt* st2;
        if (sqlite3_prepare_v2(db, sql2, -1, &st2, nullptr) == SQLITE_OK) {
            sqlite3_bind_text(st2,1,rh.c_str(),-1,SQLITE_TRANSIENT);
            sqlite3_bind_text(st2,2,rh.c_str(),-1,SQLITE_TRANSIENT);
            sqlite3_step(st2);
            sqlite3_finalize(st2);
        }
        return ok;
    }
    // Reinserta un producto con ID explicito (para Undo de ELIMINAR).
    bool guardarProductoConId(int id, const string& tit, const string& tipo, const string& cat, const string& val, int anio, const string& grp, const string& inv, int estado = 1) {
        if (db == nullptr) return false;
        const char* sql = "INSERT OR IGNORE INTO Productos (id_producto, titulo, tipo_producto, categoria, estado_validacion, anio_publicacion, codigo_grupo_fk, cod_rh_investigador_fk, estado) VALUES (?,?,?,?,?,?,?,?,?);";
        sqlite3_stmt* st;
        if (sqlite3_prepare_v2(db, sql, -1, &st, nullptr) != SQLITE_OK) return false;
        sqlite3_bind_int(st,1,id);
        sqlite3_bind_text(st,2,tit.c_str(),-1,SQLITE_TRANSIENT);
        sqlite3_bind_text(st,3,tipo.c_str(),-1,SQLITE_TRANSIENT);
        sqlite3_bind_text(st,4,cat.c_str(),-1,SQLITE_TRANSIENT);
        sqlite3_bind_text(st,5,val.c_str(),-1,SQLITE_TRANSIENT);
        sqlite3_bind_int(st,6,anio);
        sqlite3_bind_text(st,7,grp.c_str(),-1,SQLITE_TRANSIENT);
        sqlite3_bind_text(st,8,inv.c_str(),-1,SQLITE_TRANSIENT);
        sqlite3_bind_int(st,9,estado);
        bool ok = (sqlite3_step(st) == SQLITE_DONE);
        sqlite3_finalize(st);
        return ok;
    }
    bool registrarAccion(const string& tipo, const string& entidad, const string& json) {
        if (db == nullptr) return false;
        const char* sql = "INSERT INTO HistorialAcciones (tipo_operacion, entidad_afectada, json_datos) VALUES (?,?,?);";
        sqlite3_stmt* st;
        if (sqlite3_prepare_v2(db, sql, -1, &st, nullptr) != SQLITE_OK) return false;
        sqlite3_bind_text(st,1,tipo.c_str(),-1,SQLITE_TRANSIENT);
        sqlite3_bind_text(st,2,entidad.c_str(),-1,SQLITE_TRANSIENT);
        sqlite3_bind_text(st,3,json.c_str(),-1,SQLITE_TRANSIENT);
        bool ok = (sqlite3_step(st) == SQLITE_DONE);
        sqlite3_finalize(st);
        return ok;
    }
    int contarHistorial() {
        if (db == nullptr) return -1;
        sqlite3_stmt* st;
        if (sqlite3_prepare_v2(db, "SELECT COUNT(*) FROM HistorialAcciones;", -1, &st, nullptr) != SQLITE_OK) return -1;
        int n = -1;
        if (sqlite3_step(st) == SQLITE_ROW) n = sqlite3_column_int(st, 0);
        sqlite3_finalize(st);
        return n;
    }
    bool eliminarGrupoDB(const string& cod) {
        if (db == nullptr) return false;
        const char* sql = "DELETE FROM Grupos WHERE codigo_grupo=?;"; // CASCADE borra adscripciones y productos
        sqlite3_stmt* st;
        if (sqlite3_prepare_v2(db, sql, -1, &st, nullptr) != SQLITE_OK) return false;
        sqlite3_bind_text(st,1,cod.c_str(),-1,SQLITE_TRANSIENT);
        bool ok = (sqlite3_step(st) == SQLITE_DONE);
        sqlite3_finalize(st);
        // Limpieza de investigadores que quedaron sin grupo
        sqlite3_exec(db, "DELETE FROM Investigadores WHERE NOT EXISTS (SELECT 1 FROM grupo_investigador WHERE cod_rh_fk=Investigadores.cod_rh);", nullptr, nullptr, nullptr);
        return ok;
    }
};

// ============================================================================
// PUENTE DE INTEROPERABILIDAD CLI (popen C++ ↔ Python)
// ============================================================================

class GestorInterop {
public:
    static bool ejecutarScriptPython(string argumentos) {
        cout << "\n[INTEROP] Invocando script Python con argumentos: " << argumentos << "...\n";
        
        // PYTHONIOENCODING=utf-8: la tuberia hereda la consola cp1252 y los
        // � de SCIENTI tumbarian el script (BUG-10). El .py tambien se blinda solo.
        string envPy = "set PYTHONIOENCODING=utf-8&& ";
        // Detectar comando python adecuado
        string comando = envPy + "C:\\msys64\\ucrt64\\bin\\python.exe Taller2_KM_PO_XX.py " + argumentos;

        FILE* pipe = popen(comando.c_str(), "r");
        if (!pipe) {
            // Intentar comando genérico si el de msys64 no está
            comando = envPy + "python Taller2_KM_PO_XX.py " + argumentos;
            pipe = popen(comando.c_str(), "r");
            if (!pipe) {
                cerr << "[ERROR INTEROP] No se pudo ejecutar la tubería popen.\n";
                return false;
            }
        }

        char buffer[256];
        while (fgets(buffer, sizeof(buffer), pipe) != nullptr) {
            cout << "  [PYTHON] " << buffer;
        }

        int exitCode = pclose(pipe);
        cout << "[INTEROP] Proceso Python finalizado con código: " << exitCode << endl;
        return (exitCode == 0);
    }

    // Ejecuta el script y devuelve su salida para parsearla (buscador por nombre).
    static string salidaPython(const string& argumentos) {
        string comando = "set PYTHONIOENCODING=utf-8&& C:\\msys64\\ucrt64\\bin\\python.exe Taller2_KM_PO_XX.py " + argumentos;
        string out;
        FILE* pipe = popen(comando.c_str(), "r");
        if (!pipe) return out;
        char buffer[512];
        while (fgets(buffer, sizeof(buffer), pipe) != nullptr) out += buffer;
        pclose(pipe);
        return out;
    }

    static vector<string> partir(const string& s, char sep) {
        vector<string> v;
        string cur;
        for (size_t i = 0; i < s.size(); i++) {
            if (s[i] == sep) { v.push_back(cur); cur.clear(); }
            else if (s[i] != '\r' && s[i] != '\n') cur += s[i];
        }
        v.push_back(cur);
        return v;
    }
};

struct CandidatoGrupo {
    string nro, nombre, col, lider, inst, cat;
};

// ============================================================================
// APLICACIÓN CONSOLA AUTÓNOMA UX
// ============================================================================

class ConsolaApp {
private:
    MultilistaOrtogonal multilista;
    PilaUndo pilaUndo;
    ColaIngesta colaIngesta;
    GestorSQLite gestorBD;

public:
    ConsolaApp() : gestorBD("data/pea_investigacion.db") {}

    void iniciar() {
        inicializarTerminal();
        gestorBD.conectar();

        limpiarPantalla();
        cout << "======================================================================\n";
        cout << "  PEA-i — PROGRAMA ESTADÍSTICO DE ANÁLISIS DE INVESTIGACIÓN (UPC)     \n";
        cout << "======================================================================\n";
        cout << "  Estructura de Datos 2026-I | Docente: Ing. Adith Pérez              \n";
        cout << "----------------------------------------------------------------------\n";

        // PRIMERO: desea cargar un grupo (por NOMBRE desde SCIENTI) o seguir con lo actual.
        char resp = '\0';
        while (resp != 's' && resp != 'n') {
            string r = leerTexto("Desea cargar algun grupo de investigacion de la universidad popular del cesar? (si/no) + ENTER: ", false);
            string t = "";
            for (size_t i = 0; i < r.size(); i++) {
                char c = r[i];
                if (c >= 'A' && c <= 'Z') c = (char)(c + ('a' - 'A'));
                if (c != ' ' && c != '\t') t += c;
            }
            if (t == "si" || t == "s" || t == "sí") resp = 's';
            else if (t == "no" || t == "n") resp = 'n';
            else cout << "[AVISO] Responda si o no y pulse ENTER.\n";
        }

        if (resp == 's') {
            // Buscador por NOMBRE: verifica en SCIENTI, permite escoger universidad y carga.
            menuBuscarGrupo();
            menuPrincipal();
            return;
        }

        // "no": continua con los datos actuales (Nota 10).
        cout << "----------------------------------------------------------------------\n";
        cout << " [NOTA 10] Elija la modalidad de arranque inicial:\n";
        cout << " 1. Precargar datos de la Universidad desde SQLite (data/pea_investigacion.db)\n";
        cout << " 2. Iniciar con estructuras vacías en memoria RAM (Ejecutar sin datos)\n";
        cout << "----------------------------------------------------------------------\n";
        char opt = '\0';
        while (opt != '1' && opt != '2') {
            opt = leerOpcion(" Seleccione una opcion [1-2] + ENTER: ");
            if (opt != '1' && opt != '2') cout << "[AVISO] Opcion invalida. Escriba 1 o 2 y pulse ENTER.\n";
        }

        if (opt == '1') {
            cout << "[INFO] Precargando Hipercubo 3D desde SQLite...\n";
            gestorBD.cargarEnMultilista(multilista);
        } else {
            crearSistemaVacio("arranque Nota 10 sin datos");
        }

        pausar();
        menuPrincipal();
    }

    // Flujo reutilizable de carga por grupo (misma logica del arranque).
    // Verifica existencia ("Grupo no existente") y universidad ("universidad no encontrada").
    void flujoCargaGrupoUPC() {
        string nro = leerTexto(" nro GrupLAC (ENTER = GISICO 00000000002099): ", true);
        if (nro.empty()) nro = "00000000002099";
        string univ = leerTexto(" Universidad (ENTER = sin filtro): ", true);
        cout << "\n[Cargando datos...]\n";
        colaIngesta.encolar("URL_SCIENTI", "nro=" + nro);
        string args = "--scrape-grupo \"" + nro + "\"";
        if (!univ.empty()) args += " --universidad \"" + univ + "\"";
        GestorInterop::ejecutarScriptPython(args);
        cout << "\n[RECARGA] Sincronizando Hipercubo 3D en RAM desde SQLite...\n";
        gestorBD.cargarEnMultilista(multilista);
        cout << "\n[Datos cargados con exito.]\n";
        pausarEnter("Presione ENTER para continuar...");
    }

    static string leerLinea(const string& prompt) {
        cout << prompt;
        string s;
        getline(cin, s);
        return s;
    }

    // --- Entrada con ENTER confirmado (los menus NO avanzan con getch) ---
    static string recortar(const string& s) {
        size_t a = 0;
        while (a < s.size() && (s[a] == ' ' || s[a] == '\t' || s[a] == '\r')) a++;
        size_t b = s.size();
        while (b > a && (s[b - 1] == ' ' || s[b - 1] == '\t' || s[b - 1] == '\r')) b--;
        return s.substr(a, b - a);
    }

    // Lee la opcion del menu: exige escribir + pulsar ENTER. '\0' = ENTER vacio.
    static char leerOpcion(const string& prompt) {
        cout << prompt;
        string s;
        getline(cin, s);
        s = recortar(s);
        if (s.empty()) return '\0';
        return s[0];
    }

    // --- Validadores por tipo de dato (puntos 6/9: categoria y validacion) ---
    static bool esCategoriaValida(const string& v) {
        return v == "A1" || v == "A" || v == "B" || v == "C" || v == "Reconocido";
    }
    static bool esValidacionValida(const string& v) {
        return v == "Validado" || v == "Pendiente" || v == "Rechazado";
    }
    static bool esTipoValido(const string& v) {
        return v == "Articulo" || v == "Libro" || v == "Software" || v == "Patente" ||
               v == "Capitulo"; // capitulos GrupLAC: valor propio, no Libro (S28)
    }
    static bool esCategoriaInvValida(const string& v) {
        return v == "Emergente" || v == "Junior" || v == "Asociado" || v == "Senior" ||
               v == "No categorizado"; // estado real consultado en CvLAC (S17)
    }
    static bool esCorreoValido(const string& v) {
        size_t a = v.find('@');
        return a != string::npos && a > 0 && a + 1 < v.size() && v.find('.', a) != string::npos;
    }
    static bool esAnioValido(int a) { return a >= 1900 && a <= 2026; }

    // Lee entero con ENTER confirmado; repite hasta valido (nunca deja basura en cin).
    // permitirVacio=true: ENTER vacio devuelve 'defecto' (usado en edicion = conservar).
    static int leerEntero(const string& prompt, int minV, int maxV, bool permitirVacio, int defecto, bool* fueVacio = nullptr) {
        while (true) {
            cout << prompt;
            string s;
            getline(cin, s);
            s = recortar(s);
            if (s.empty()) {
                if (permitirVacio) { if (fueVacio) *fueVacio = true; return defecto; }
                cout << "[AVISO] Valor requerido. Intente de nuevo.\n";
                continue;
            }
            char* fin = nullptr;
            long v = strtol(s.c_str(), &fin, 10);
            if (fin == nullptr || *fin != '\0') {
                cout << "[AVISO] Debe ser un numero entero. Intente de nuevo.\n";
                continue;
            }
            if (v < minV || v > maxV) {
                cout << "[AVISO] Fuera de rango [" << minV << "-" << maxV << "]. Intente de nuevo.\n";
                continue;
            }
            if (fueVacio) *fueVacio = false;
            return (int)v;
        }
    }

    // Lee texto con ENTER confirmado. permitirVacio=true: ENTER = conservar (devuelve "").
    typedef bool (*ValidadorTxt)(const string&);
    static string leerTextoVal(const string& prompt, bool permitirVacio, ValidadorTxt v, const string& ayuda) {
        while (true) {
            cout << prompt;
            string s;
            getline(cin, s);
            s = recortar(s);
            if (s.empty()) {
                if (permitirVacio) return ""; // ENTER = no cambiar, nunca se guarda vacio
                cout << "[AVISO] Valor requerido (no vacio). Intente de nuevo.\n";
                continue;
            }
            if (v != nullptr && !v(s)) {
                cout << "[AVISO] Valor invalido. " << ayuda << " Intente de nuevo."
                     << (permitirVacio ? " (ENTER = conservar)" : "") << "\n";
                continue;
            }
            return s;
        }
    }
    static string leerTexto(const string& prompt, bool permitirVacio) {
        return leerTextoVal(prompt, permitirVacio, nullptr, "");
    }
    // Atajos por dato (edicion: permitirVacio=true => ENTER conserva; creacion: false => obliga).
    static string leerCategoria(bool permitirVacio) {
        return leerTextoVal(" Categoria (A1/A/B/C/Reconocido): ", permitirVacio, esCategoriaValida, "Opciones: A1/A/B/C/Reconocido.");
    }
    static string leerValidacion(bool permitirVacio) {
        return leerTextoVal(" Validacion (Validado/Pendiente/Rechazado): ", permitirVacio, esValidacionValida, "Opciones: Validado/Pendiente/Rechazado.");
    }
    static string leerTipoProd(bool permitirVacio) {
        return leerTextoVal(" Tipo (Articulo/Libro/Software/Patente/Capitulo): ", permitirVacio, esTipoValido, "Opciones: Articulo/Libro/Software/Patente/Capitulo (sin tilde).");
    }
    static string leerCorreo(bool permitirVacio) {
        return leerTextoVal(" Correo: ", permitirVacio, esCorreoValido, "Debe contener @ y dominio (ej. x@unicesar.edu.co).");
    }
    static string leerCatInvestigador(bool permitirVacio) {
        return leerTextoVal(" Categoria (Emergente/Junior/Asociado/Senior/No categorizado): ", permitirVacio, esCategoriaInvValida, "Opciones: Emergente/Junior/Asociado/Senior/No categorizado.");
    }
    static vector<string> splitSEP(const string& s) {
        vector<string> out;
        string cur;
        for (size_t i = 0; i < s.size(); i++) {
            if (s[i] == '\x1F') { out.push_back(cur); cur.clear(); }
            else cur += s[i];
        }
        out.push_back(cur);
        return out;
    }
    static string joinSEP(const vector<string>& v) {
        string s;
        for (size_t i = 0; i < v.size(); i++) {
            if (i) s += '\x1F';
            s += v[i];
        }
        return s;
    }

    // INCLUSION con persistencia doble: Pila RAM + tabla HistorialAcciones (Fase A3).
    void apilarConPersistencia(const string& op, const string& ent, const string& json) {
        pilaUndo.apilar(op, ent, json);
        gestorBD.registrarAccion(op, ent, json);
    }

    // CREACION demostrable del sistema completo (Fase A1 + Nota 10).
    void crearSistemaVacio(const string& motivo) {
        multilista.crearVacia();
        pilaUndo.crearVacia();
        colaIngesta.crearVacia();
        cout << "[CREACION] Sistema vacio inicializado (" << motivo << ").\n";
        cout << " Multilista/Hipercubo + Pila Undo + Cola Ingesta creadas vacias.\n";
    }

    // B1: demostracion 7 operaciones x 4 TDAs con datos de prueba.
    // B2: aclara que la LISTA simple es la base de la MULTILISTA.
    void demoTDAs() {
        limpiarPantalla();
        cout << "======================================================================\n";
        cout << " DEMOSTRACION 7 OPERACIONES x 4 TDAs (puntos B + 8/9 del taller)\n";
        cout << " NOTA: la LISTA enlazada simple es el bloque base: cada eje del\n";
        cout << " hipercubo (sigGrupo, sigInvestigador, sigProductoGrupo) ES una lista\n";
        cout << " simple; la MULTILISTA las cruza en 3D. Pila=LIFO Undo, Cola=FIFO ingesta.\n";
        cout << "======================================================================\n";
        // 1. CREACION
        crearSistemaVacio("demo 7x4");
        cout << "[1/7 CREACION] OK: multilista=" << (multilista.getCabeceraGrupos() == nullptr ? "vacia" : "NO-vacia")
             << " pila=" << pilaUndo.tamano() << " cola=" << colaIngesta.tamano() << endl;
        // 2. INCLUSION
        multilista.insertarGrupo("DEMO01", "Grupo Demo", "Lider Demo", "Plan demo", "Linea demo");
        multilista.insertarInvestigador("DEMO01", "DEMO0001", "Inv Demo", "demo@unicesar.edu.co", "Junior", "http://demo");
        multilista.insertarProducto(90001, "Producto demo 7x4", "Articulo", "B", "Pendiente", 2025, "DEMO01", "DEMO0001");
        pilaUndo.apilar("CREAR", "PRODUCTO", "90001"); // demo RAM sola, no contamina Historial
        colaIngesta.encolar("DEMO", "demo/origen");
        cout << "[2/7 INCLUSION] OK: grupo+investigador+producto demo + 1 pila + 1 cola.\n";
        // 3. CONSULTA (no destructiva)
        {
            string op, ent, js;
            bool okTop = pilaUndo.verTope(op, ent, js);
            string tt, rt;
            bool okFr = colaIngesta.verFrente(tt, rt);
            cout << "[3/7 CONSULTA] verTope=" << (okTop ? op + "/" + ent : "vacio")
                 << " verFrente=" << (okFr ? tt : "vacio") << " | Listados:" << endl;
            multilista.listarGrupos();
            pilaUndo.listar();
            colaIngesta.listarPendientes();
        }
        // 4. MODIFICACION
        multilista.editarProducto(90001, "", "", "A", "Validado", -1);
        cout << "[4/7 MODIFICACION] OK: producto 90001 categoria=B->A, validacion->Validado.\n";
        // 5. DESACTIVACION (logica)
        multilista.desactivarProducto(90001);
        cout << "[5/7 DESACTIVACION] OK: producto 90001 activo=false (sigue en RAM).\n";
        multilista.reactivarProducto(90001);
        cout << "        Reactivado para continuar la demo.\n";
        // 6. ELIMINACION (fisica + LIFO/FIFO)
        {
            string t, r;
            colaIngesta.desencolar(t, r);
            multilista.eliminarProductoFisico(90001);
            cout << "[6/7 ELIMINACION] OK: producto demo eliminado (1 delete), cola desencolada (" << t << ").\n";
        }
        // 7. PERSISTENCIA
        gestorBD.guardarNuevoGrupo("DEMO01", "Grupo Demo", "Lider Demo", "Plan demo", "Linea demo");
        gestorBD.registrarAccion("DEMO", "TDAS", "demo-7x4-ok");
        cout << "[7/7 PERSISTENCIA] OK: grupo DEMO01 + accion DEMO en SQLite (ver HistorialAcciones).\n";
        cout << "Historial en BD: " << gestorBD.contarHistorial() << " filas.\n";
        // Limpieza demo para no contaminar datos reales
        multilista.eliminarGrupoFisico("DEMO01");
        gestorBD.eliminarGrupoDB("DEMO01");
        cout << "Demo limpiada (grupo DEMO01 eliminado de RAM y BD).\n";
        pausar();
    }

    void ejecutarUndo() {
        string op, ent, js;
        if (!pilaUndo.desapilar(op, ent, js)) {
            cout << "\n[UNDO] No hay acciones pendientes por deshacer en la Pila.\n";
            return;
        }
        vector<string> f = splitSEP(js);
        if (op == "CREAR" && ent == "GRUPO" && f.size() >= 1) {
            multilista.eliminarGrupoFisico(f[0]);
            gestorBD.eliminarGrupoDB(f[0]);
            cout << "[UNDO] Creacion de grupo " << f[0] << " revertida (eliminado).\n";
        } else if (op == "CREAR" && ent == "INVESTIGADOR" && f.size() >= 2) {
            multilista.eliminarInvestigadorDeGrupo(f[0], f[1]);
            gestorBD.eliminarAdscripcionDB(f[0], f[1]);
            cout << "[UNDO] Creacion de investigador " << f[1] << " revertida.\n";
        } else if (op == "CREAR" && ent == "PRODUCTO" && f.size() >= 1) {
            int id = atoi(f[0].c_str());
            multilista.eliminarProductoFisico(id);
            gestorBD.eliminarProductoDB(id);
            cout << "[UNDO] Creacion de producto " << id << " revertida (eliminado).\n";
        } else if (op == "DESACTIVAR" && ent == "GRUPO" && f.size() >= 1) {
            multilista.reactivarGrupo(f[0]);
            gestorBD.setEstado("Grupos", "codigo_grupo", f[0], 1);
            cout << "[UNDO] Grupo " << f[0] << " reactivado.\n";
        } else if (op == "DESACTIVAR" && ent == "INVESTIGADOR" && f.size() >= 1) {
            multilista.reactivarInvestigador(f[0]);
            gestorBD.setEstado("Investigadores", "cod_rh", f[0], 1);
            cout << "[UNDO] Investigador " << f[0] << " reactivado.\n";
        } else if (op == "DESACTIVAR" && ent == "PRODUCTO" && f.size() >= 1) {
            int id = atoi(f[0].c_str());
            multilista.reactivarProducto(id);
            gestorBD.setEstado("Productos", "id_producto", f[0], 1);
            cout << "[UNDO] Producto " << id << " reactivado.\n";
        } else if (op == "EDITAR" && ent == "GRUPO" && f.size() >= 5) {
            multilista.editarGrupo(f[0], f[1], f[2], f[3], f[4]);
            gestorBD.actualizarGrupo(f[0], f[1], f[2], f[3], f[4]);
            cout << "[UNDO] Edicion de grupo " << f[0] << " revertida.\n";
        } else if (op == "EDITAR" && ent == "INVESTIGADOR" && f.size() >= 5) {
            multilista.editarInvestigador(f[0], f[1], f[2], f[3], f[4]);
            gestorBD.actualizarInvestigador(f[0], f[1], f[2], f[3], f[4]);
            cout << "[UNDO] Edicion de investigador " << f[0] << " revertida.\n";
        } else if (op == "EDITAR" && ent == "PRODUCTO" && f.size() >= 6) {
            int id = atoi(f[0].c_str());
            int anio = atoi(f[5].c_str());
            multilista.editarProducto(id, f[1], f[2], f[3], f[4], anio);
            gestorBD.actualizarProducto(id, f[1], f[2], f[3], f[4], anio);
            cout << "[UNDO] Edicion de producto " << id << " revertida.\n";
        } else if (op == "ELIMINAR" && ent == "PRODUCTO" && f.size() >= 7) {
            int id = atoi(f[0].c_str());
            int anio = atoi(f[5].c_str());
            multilista.insertarProducto(id, f[1], f[2], f[3], f[4], anio, f[6], f[7].size() > 0 ? f[7] : "");
            gestorBD.guardarProductoConId(id, f[1], f[2], f[3], f[4], anio, f[6], f[7]);
            cout << "[UNDO] Producto " << id << " restaurado.\n";
        } else {
            cout << "[UNDO] Accion " << op << "/" << ent << " no reversible automaticamente (haga recarga desde BD).\n";
        }
    }

    void menuPrincipal() {
        char opcion;
        do {
            limpiarPantalla();
            cout << "======================================================================\n";
            cout << "                     PEA-i — MENÚ PRINCIPAL (C++)                     \n";
            cout << "======================================================================\n";
            cout << " 1. Gestionar Grupos de Investigación (CRUD completo)\n";
            cout << " 2. Gestionar Investigadores (CRUD + adscripcion N:M)\n";
            cout << " 3. Gestionar Productos (CRUD + categoria/validacion)\n";
            cout << " 4. Filtrar Producción por Ventana de Años (Últimos 2, 5 años)\n";
            cout << " 5. Ver Resumen Estadístico Descriptivo (Tablas & Números - Punto 12.a)\n";
            cout << " 6. Deshacer última acción (Pila Undo - LIFO)\n";
            cout << " 7. Descargar / Ingestar Datos SCIENTI (Cola FIFO & Python Scraping)\n";
            cout << " 8. Lanzar Dashboard Gráfico Tkinter + Matplotlib (Puntos 12.b, 12.c - Interop)\n";
            cout << " 9. Demostracion 7 ops x 4 TDAs (creacion/inclusion/consulta/...)\n";
            cout << " 0. Salir del Programa\n";
            cout << " NOTA: LISTA simple = bloque base (cada eje ES una lista); la MULTILISTA las cruza.\n";
            cout << "======================================================================\n";

            opcion = leerOpcion(" Seleccione una opcion [0-9] + ENTER: ");

            switch (opcion) {
                case '1':
                    menuGrupos();
                    break;

                case '2':
                    menuInvestigadores();
                    break;

                case '3':
                    menuProductos();
                    break;

                case '4': {
                    limpiarPantalla();
                    cout << "--- FILTRO DE VENTANA DE OBSERVACIÓN DE AÑOS ---\n";
                    cout << " 1. Últimos 2 años (2024 - 2026)\n";
                    cout << " 2. Últimos 5 años (2021 - 2026)\n";
                    cout << " 3. Rango personalizado\n";
                    char fOpt = leerOpcion(" Seleccione opcion + ENTER: ");

                    if (fOpt == '1') multilista.listarProductosPorVentanaAnios(2024, 2026);
                    else if (fOpt == '2') multilista.listarProductosPorVentanaAnios(2021, 2026);
                    else if (fOpt == '3') {
                        int aIni = leerEntero(" Ingrese anio inicial [1900-2026]: ", 1900, 2026, false, 0);
                        int aFin = leerEntero(" Ingrese anio final [1900-2026]: ", 1900, 2026, false, 0);
                        if (aIni > aFin) { cout << "[AVISO] Rango invertido, se intercambian.\n"; int t = aIni; aIni = aFin; aFin = t; }
                        multilista.listarProductosPorVentanaAnios(aIni, aFin);
                    } else cout << "[AVISO] Opcion invalida.\n";
                    pausar();
                    break;
                }

                case '5':
                    limpiarPantalla();
                    multilista.generarResumenEstadistico();
                    pausar();
                    break;

                case '6': {
                    limpiarPantalla();
                    ejecutarUndo();
                    pausar();
                    break;
                }

                case '7': {
                    limpiarPantalla();
                    cout << "--- INGESTA DE DATOS DE INVESTIGACIÓN (COLA FIFO) ---\n";
                    cout << " 1. Descargar desde URL Oficial MinCiencias SCIENTI (Scraping)\n";
                    cout << " 2. Ingestar desde archivo CSV (data/muestra_upc.csv)\n";
                    cout << " 3. Ingestar desde dataset de respaldo offline (--offline)\n";
                    cout << " 4. Extraer grupo UPC por nro GrupLAC (sistema N-grupos)\n";
                    cout << " 5. Buscar grupo por NOMBRE en SCIENTI (elige universidad y carga)\n";
                    char iOpt = leerOpcion(" Seleccione opcion + ENTER: ");

                    if (iOpt == '1') {
                        string url = leerTexto(" Ingrese URL de GrupLAC / CvLAC: ", false);
                        colaIngesta.encolar("URL_SCIENTI", url);
                        GestorInterop::ejecutarScriptPython("--scrape-url \"" + url + "\"");
                    } else if (iOpt == '4') {
                        flujoCargaGrupoUPC();
                    } else if (iOpt == '5') {
                        menuBuscarGrupo();
                    } else if (iOpt == '2') {
                        colaIngesta.encolar("CSV", "data/muestra_upc.csv");
                        GestorInterop::ejecutarScriptPython("--ingesta-archivo \"data/muestra_upc.csv\"");
                    } else if (iOpt == '3') {
                        colaIngesta.encolar("OFFLINE", "data/dataset_respaldo.csv");
                        GestorInterop::ejecutarScriptPython("--offline");
                    }
                    
                    // Recargar memoria desde SQLite tras la ingesta
                    cout << "\n[RECARGA] Sincronizando Hipercubo 3D en RAM desde SQLite...\n";
                    gestorBD.cargarEnMultilista(multilista);
                    pausar();
                    break;
                }

                case '8':
                    limpiarPantalla();
                    cout << "[INTEROP] Lanzando Dashboard Gráfico en Python (Tkinter + Matplotlib)...\n";
                    GestorInterop::ejecutarScriptPython("--gui");
                    gestorBD.cargarEnMultilista(multilista);
                    pausar();
                    break;

                case '9':
                    demoTDAs();
                    break;

                case '0':
                    cout << "\nGracias por utilizar el sistema PEA-i de la Universidad Popular del Cesar.\n";
                    break;

                default:
                    cout << "\nOpción inválida. Intente de nuevo.\n";
                    pausar();
                    break;
            }
        } while (opcion != '0');
    }

    // Buscador por nombre: SCIENTI -> candidatos (nro + universidad) -> elige -> carga.
    // Si no hay coincidencias: grupo no existente. Si hay varias universidades: el usuario escoge.
    void menuBuscarGrupo() {
        limpiarPantalla();
        cout << "--- BUSCAR GRUPO POR NOMBRE EN SCIENTI ---\n";
        string q = leerTexto(" Nombre a buscar (ej. GISICO): ", false);
        cout << "\n[Buscando en SCIENTI...]\n";
        string out = GestorInterop::salidaPython("--buscar-grupo \"" + q + "\"");
        vector<CandidatoGrupo> cands;
        {
            string cur;
            for (size_t i = 0; i <= out.size(); i++) {
                if (i == out.size() || out[i] == '\n') {
                    if (cur.size() > 5 && cur.substr(0, 5) == "CAND|") {
                        vector<string> f = GestorInterop::partir(cur, '|');
                        if (f.size() >= 8) {
                            CandidatoGrupo c;
                            c.nro = f[2]; c.nombre = f[3]; c.col = f[4];
                            c.lider = f[5]; c.inst = f[6]; c.cat = f[7];
                            cands.push_back(c);
                        }
                    }
                    cur.clear();
                } else if (out[i] != '\r') cur += out[i];
            }
        }
        if (cands.empty()) {
            cout << "[AVISO] Grupo no existente (sin coincidencias para \"" << q << "\").\n";
            cout << "Sugerencia: indexe mas instituciones con --grupos-institucion (hoy: las ya indexadas).\n";
            pausar();
            return;
        }
        cout << "\nCoincidencias (escoja por numero; 0 cancela):\n";
        {
            const vector<size_t> W = {3, 60, 36};
            cout << bordeTabla(W, '=') << "\n";
            cout << filaTabla({"No.", "GRUPO", "UNIVERSIDAD"}, W) << "\n";
            cout << bordeTabla(W, '-') << "\n";
            for (size_t i = 0; i < cands.size(); i++) {
                vector<string> f;
                f.push_back(to_string(i + 1));
                f.push_back(cands[i].nombre);
                f.push_back(cands[i].inst);
                cout << filaTabla(f, W) << "\n";
            }
            cout << bordeTabla(W, '-') << "\n";
        }
        int pick = leerEntero(" Opcion [0-" + to_string(cands.size()) + "]: ", 0, (int)cands.size(), false, 0);
        if (pick == 0) { cout << "[CANCELADO].\n"; pausar(); return; }
        CandidatoGrupo elegido = cands[(size_t)pick - 1];
        cout << "\n[Cargando datos de " << elegido.nombre.substr(0, 40) << " / " << elegido.inst.substr(0, 30) << "...]\n";
        colaIngesta.encolar("URL_SCIENTI", "nro=" + elegido.nro);
        string args = "--scrape-grupo \"" + elegido.nro + "\"";
        if (!elegido.inst.empty()) args += " --universidad \"" + elegido.inst + "\"";
        GestorInterop::ejecutarScriptPython(args);
        cout << "\n[RECARGA] Sincronizando Hipercubo 3D en RAM desde SQLite...\n";
        gestorBD.cargarEnMultilista(multilista);
        cout << "\n[Datos cargados con exito.]\n";
        pausarEnter("Presione ENTER para continuar...");
    }

    // Muestra los grupos por NUMERO (sin codigos) y devuelve el codigo interno elegido.
    // Devuelve "" si cancela (0) o no hay grupos.
    string elegirGrupo(const string& titulo) {
        vector<string> cods;
        vector<string> noms;
        NodoGrupo* g = multilista.getCabeceraGrupos();
        while (g != nullptr) {
            cods.push_back(g->codigo_grupo);
            noms.push_back(g->nombre + (g->activo ? "" : " (INACTIVO)"));
            g = g->sigGrupo;
        }
        if (cods.empty()) { cout << "[AVISO] No hay grupos en el sistema.\n"; return ""; }
        const vector<size_t> W = {3, 80};
        cout << bordeTabla(W, '=') << "\n";
        cout << tituloTabla(titulo, W) << "\n";
        cout << bordeTabla(W, '=') << "\n";
        cout << filaTabla({"No.", "GRUPO"}, W) << "\n";
        cout << bordeTabla(W, '-') << "\n";
        for (size_t i = 0; i < cods.size(); i++) {
            vector<string> f;
            f.push_back(to_string(i + 1));
            f.push_back(noms[i]);
            cout << filaTabla(f, W) << "\n";
        }
        cout << bordeTabla(W, '-') << "\n";
        int pick = leerEntero(" Seleccione el grupo [0 = cancelar]: ", 0, (int)cods.size(), false, 0);
        if (pick == 0) return "";
        return cods[(size_t)pick - 1];
    }

    void menuGrupos() {
        char opt;
        do {
            limpiarPantalla();
            cout << "--- GESTION DE GRUPOS (CRUD) ---\n";
            cout << " 1. Listar grupos\n 2. Ver detalle de grupo\n 3. Crear grupo\n 4. Editar grupo\n";
            cout << " 5. Desactivar grupo (logico)\n 6. Reactivar grupo\n 7. Eliminar grupo (fisico, cascada)\n 0. Volver\n";
            opt = leerOpcion("Seleccione + ENTER: ");
            if (opt == '1') { multilista.listarGrupos(); pausar(); }
            else if (opt == '2') {
                string c = elegirGrupo("Seleccione el grupo a consultar");
                if (c.empty()) { cout << "[CANCELADO].\n"; pausar(); }
                else { multilista.verDetalleGrupo(c); pausar(); }
            }
            else if (opt == '3') {
                string cod = leerTexto(" Codigo (ej. COL0000004): ", false);
                string nom = leerTexto(" Nombre (ej. GINTE): ", false);
                string lid = leerTexto(" Lider: ", false);
                string plan = leerTexto(" Plan de investigacion: ", false);
                string lin = leerTexto(" Lineas estrategicas: ", false);
                if (multilista.insertarGrupo(cod, nom, lid, plan, lin)) {
                    gestorBD.guardarNuevoGrupo(cod, nom, lid, plan, lin);
                    apilarConPersistencia("CREAR", "GRUPO", cod);
                    cout << "[EXITO] Grupo creado en RAM y SQLite.\n";
                } else cout << "[ERROR] Codigo duplicado.\n";
                pausar();
            } else if (opt == '4') {
                string cod = elegirGrupo("Seleccione el grupo a editar");
                if (cod.empty()) { cout << "[CANCELADO].\n"; pausar(); continue; }
                NodoGrupo* g = multilista.buscarGrupo(cod);
                if (g == nullptr) { cout << "[ERROR] No existe o inactivo.\n"; pausar(); continue; }
                string oldNom = g->nombre, oldLid = g->lider, oldPlan = g->plan_investigacion, oldLin = g->lineas_estrategicas;
                cout << "(ENTER vacio = conservar el valor actual)\n";
                string nom = leerTexto(" Nuevo nombre [" + oldNom + "]: ", true);
                string lid = leerTexto(" Nuevo lider [" + oldLid + "]: ", true);
                string plan = leerTexto(" Nuevo plan: ", true);
                string lin = leerTexto(" Nuevas lineas: ", true);
                if (multilista.editarGrupo(cod, nom, lid, plan, lin)) {
                    NodoGrupo* g2 = multilista.buscarGrupo(cod);
                    gestorBD.actualizarGrupo(cod, g2->nombre, g2->lider, g2->plan_investigacion, g2->lineas_estrategicas);
                    apilarConPersistencia("EDITAR", "GRUPO", joinSEP(vector<string>{cod, oldNom, oldLid, oldPlan, oldLin}));
                    cout << "[EXITO] Grupo actualizado.\n";
                }
                pausar();
            } else if (opt == '5') {
                string cod = elegirGrupo("Seleccione el grupo a desactivar");
                if (cod.empty()) { cout << "[CANCELADO].\n"; pausar(); continue; }
                if (multilista.desactivarGrupo(cod)) {
                    gestorBD.setEstado("Grupos", "codigo_grupo", cod, 0);
                    apilarConPersistencia("DESACTIVAR", "GRUPO", cod);
                    cout << "[EXITO] Grupo desactivado.\n";
                } else cout << "[ERROR] No encontrado.\n";
                pausar();
            } else if (opt == '6') {
                string cod = elegirGrupo("Seleccione el grupo a reactivar");
                if (cod.empty()) { cout << "[CANCELADO].\n"; pausar(); continue; }
                if (multilista.reactivarGrupo(cod)) {
                    gestorBD.setEstado("Grupos", "codigo_grupo", cod, 1);
                    cout << "[EXITO] Grupo reactivado.\n";
                } else cout << "[ERROR] No encontrado o ya activo.\n";
                pausar();
            } else if (opt == '7') {
                string cod = elegirGrupo("Seleccione el grupo a ELIMINAR (cascada)");
                if (cod.empty()) { cout << "[CANCELADO].\n"; pausar(); continue; }
                string conf = leerTexto(" Escriba SI para confirmar: ", false);
                if (conf == "SI" && multilista.eliminarGrupoFisico(cod)) {
                    gestorBD.eliminarGrupoDB(cod);
                    cout << "[EXITO] Grupo eliminado en cascada (RAM + BD).\n";
                } else cout << "[CANCELADO] No se elimino.\n";
                pausar();
            } else if (opt != '0' && opt != '\0') { cout << "[AVISO] Opcion invalida.\n"; pausar(); }
        } while (opt != '0');
    }

    void menuInvestigadores() {
        char opt;
        do {
            limpiarPantalla();
            cout << "--- GESTION DE INVESTIGADORES (CRUD + adscripcion N:M) ---\n";
            cout << " 1. Listar investigadores\n 2. Ver detalle\n 3. Crear + adscribir a grupo\n 4. Adscribir existente a otro grupo\n";
            cout << " 5. Editar datos personales\n 6. Desactivar\n 7. Reactivar\n 8. Eliminar de un grupo (fisico)\n 0. Volver\n";
            opt = leerOpcion("Seleccione + ENTER: ");
            if (opt == '1') {
                string grp = elegirGrupo("Seleccione el grupo del cual desea enlistar sus investigadores");
                if (grp.empty()) { cout << "[CANCELADO].\n"; pausar(); }
                else { multilista.listarInvestigadoresDeGrupo(grp); pausar(); }
            }
            else if (opt == '2') { string rh = leerTexto(" cod_rh: ", false); multilista.verDetalleInvestigador(rh); pausar(); }
            else if (opt == '3') {
                string grp = elegirGrupo("Seleccione el grupo destino");
                if (grp.empty()) { cout << "[CANCELADO].\n"; pausar(); continue; }
                string rh = leerTexto(" cod_rh (ej. 0000123456): ", false);
                string nom = leerTexto(" Nombre completo: ", false);
                string mail = leerCorreo(false);
                string cat = leerCatInvestigador(false);
                string url = leerTexto(" URL CvLAC: ", false);
                if (multilista.buscarGrupoIncluyeInactivos(grp) == nullptr) { cout << "[ERROR] Grupo no existe.\n"; pausar(); continue; }
                // Si el investigador ya existe globalmente, reutilizar sus datos para la adscripcion
                NodoInvestigador* gex = multilista.buscarInvestigador(rh);
                string fNom = nom, fMail = mail, fCat = cat, fUrl = url;
                if (gex != nullptr) { fNom = gex->nombre_completo; fMail = gex->correo; fCat = gex->categoria_minciencias; fUrl = gex->cvlac_url; }
                if (multilista.insertarInvestigador(grp, rh, fNom, fMail, fCat, fUrl)) {
                    gestorBD.guardarNuevoInvestigador(rh, fNom, fMail, fCat, fUrl);
                    gestorBD.guardarAdscripcion(grp, rh);
                    apilarConPersistencia("CREAR", "INVESTIGADOR", joinSEP(vector<string>{grp, rh}));
                    cout << "[EXITO] Investigador adscrito a " << grp << ".\n";
                } else cout << "[ERROR] Ya adscrito o grupo invalido.\n";
                pausar();
            } else if (opt == '4') {
                string grp = elegirGrupo("Seleccione el grupo destino");
                if (grp.empty()) { cout << "[CANCELADO].\n"; pausar(); continue; }
                string rh = leerTexto(" cod_rh existente: ", false);
                NodoInvestigador* gex = multilista.buscarInvestigador(rh);
                if (gex == nullptr) { cout << "[ERROR] Ese rh no existe. Use opcion 3.\n"; pausar(); continue; }
                if (multilista.insertarInvestigador(grp, rh, gex->nombre_completo, gex->correo, gex->categoria_minciencias, gex->cvlac_url)) {
                    gestorBD.guardarAdscripcion(grp, rh);
                    apilarConPersistencia("CREAR", "INVESTIGADOR", joinSEP(vector<string>{grp, rh}));
                    cout << "[EXITO] Adscripcion N:M creada.\n";
                } else cout << "[ERROR] Ya adscrito o grupo invalido.\n";
                pausar();
            } else if (opt == '5') {
                string rh = leerTexto(" cod_rh a editar: ", false);
                NodoInvestigador* inv = multilista.buscarInvestigador(rh);
                if (inv == nullptr) { cout << "[ERROR] No existe.\n"; pausar(); continue; }
                string oN = inv->nombre_completo, oM = inv->correo, oC = inv->categoria_minciencias, oU = inv->cvlac_url;
                cout << "(ENTER vacio = conservar el valor actual)\n";
                string nom = leerTexto(" Nombre [" + oN + "]: ", true);
                string mail = leerCorreo(true);
                string cat = leerCatInvestigador(true);
                string url = leerTexto(" CvLAC (ENTER = conservar): ", true);
                if (multilista.editarInvestigador(rh, nom, mail, cat, url)) {
                    NodoInvestigador* n2 = multilista.buscarInvestigador(rh);
                    gestorBD.actualizarInvestigador(rh, n2->nombre_completo, n2->correo, n2->categoria_minciencias, n2->cvlac_url);
                    apilarConPersistencia("EDITAR", "INVESTIGADOR", joinSEP(vector<string>{rh, oN, oM, oC, oU}));
                    cout << "[EXITO] Actualizado en todos sus grupos.\n";
                }
                pausar();
            } else if (opt == '6') {
                string rh = leerTexto(" cod_rh a desactivar: ", false);
                if (multilista.desactivarInvestigador(rh)) {
                    gestorBD.setEstado("Investigadores", "cod_rh", rh, 0);
                    apilarConPersistencia("DESACTIVAR", "INVESTIGADOR", rh);
                    cout << "[EXITO] Desactivado.\n";
                } else cout << "[ERROR] No encontrado.\n";
                pausar();
            } else if (opt == '7') {
                string rh = leerTexto(" cod_rh a reactivar: ", false);
                if (multilista.reactivarInvestigador(rh)) {
                    gestorBD.setEstado("Investigadores", "cod_rh", rh, 1);
                    cout << "[EXITO] Reactivado.\n";
                } else cout << "[ERROR] No encontrado o ya activo.\n";
                pausar();
            } else if (opt == '8') {
                string grp = elegirGrupo("Seleccione el grupo");
                if (grp.empty()) { cout << "[CANCELADO].\n"; pausar(); continue; }
                string rh = leerTexto(" cod_rh: ", false);
                string conf = leerTexto(" Escriba SI para confirmar: ", false);
                if (conf == "SI" && multilista.eliminarInvestigadorDeGrupo(grp, rh)) {
                    gestorBD.eliminarAdscripcionDB(grp, rh);
                    cout << "[EXITO] Adscripcion eliminada (sus productos de ese grupo tambien).\n";
                } else cout << "[CANCELADO].\n";
                pausar();
            } else if (opt != '0' && opt != '\0') { cout << "[AVISO] Opcion invalida.\n"; pausar(); }
        } while (opt != '0');
    }

    void menuProductos() {
        char opt;
        do {
            limpiarPantalla();
            cout << "--- GESTION DE PRODUCTOS (CRUD + categoria/validacion) ---\n";
            cout << " 1. Listar productos\n 2. Ver detalle\n 3. Crear producto (ID automatico)\n 4. Editar (categoria/validacion)\n";
            cout << " 5. Desactivar (logico)\n 6. Reactivar\n 7. Eliminar fisico\n 0. Volver\n";
            opt = leerOpcion("Seleccione + ENTER: ");
            if (opt == '1') {
                string grp = elegirGrupo("Seleccione el grupo del cual desea enlistar sus productos");
                if (grp.empty()) { cout << "[CANCELADO].\n"; pausar(); }
                else { multilista.listarProductosDeGrupo(grp); pausar(); }
            }
            else if (opt == '2') {
                int id = leerEntero(" ID: ", 1, 2000000000, false, 0);
                multilista.verDetalleProducto(id); pausar();
            } else if (opt == '3') {
                string tit = leerTexto(" Titulo: ", false);
                string tipo = leerTipoProd(false);
                string cat = leerCategoria(false);
                string val = leerValidacion(false);
                int anio = leerEntero(" Anio [1900-2026]: ", 1900, 2026, false, 0);
                string grp = elegirGrupo("Seleccione el grupo del producto");
                if (grp.empty()) { cout << "[CANCELADO].\n"; pausar(); continue; }
                string inv = leerTexto(" cod_rh (debe estar adscrito al grupo): ", false);
                long long newId = gestorBD.guardarNuevoProducto(tit, tipo, cat, val, anio, grp, inv);
                if (newId <= 0) { cout << "[ERROR BD] FK invalida o BD bloqueada.\n"; pausar(); continue; }
                if (multilista.insertarProducto((int)newId, tit, tipo, cat, val, anio, grp, inv)) {
                    apilarConPersistencia("CREAR", "PRODUCTO", to_string(newId));
                    cout << "[EXITO] Producto " << newId << " creado en RAM y SQLite.\n";
                } else {
                    gestorBD.eliminarProductoDB((int)newId); // rollback: la RAM rechazo (no adscrito/duplicado)
                    cout << "[ERROR] Investigador no adscrito a ese grupo. Rollback en BD.\n";
                }
                pausar();
            } else if (opt == '4') {
                int id = leerEntero(" ID a editar: ", 1, 2000000000, false, 0);
                NodoProducto* p = multilista.buscarProducto(id);
                if (p == nullptr) { cout << "[ERROR] No existe.\n"; pausar(); continue; }
                string oT = p->titulo, oTi = p->tipo_producto, oC = p->categoria, oV = p->estado_validacion;
                int oA = p->anio_publicacion;
                cout << "(ENTER vacio = conservar el valor actual; cada dato se valida)\n";
                string tit = leerTexto(" Titulo (ENTER = conservar): ", true);
                string tipo = leerTipoProd(true);
                string cat = leerCategoria(true);
                string val = leerValidacion(true);
                bool anioVacio = false;
                int anio = leerEntero(" Anio [" + to_string(oA) + "] (ENTER = conservar): ", 1900, 2026, true, oA, &anioVacio);
                if (multilista.editarProducto(id, tit, tipo, cat, val, anioVacio ? -1 : anio)) {
                    NodoProducto* p2 = multilista.buscarProducto(id);
                    gestorBD.actualizarProducto(id, p2->titulo, p2->tipo_producto, p2->categoria, p2->estado_validacion, p2->anio_publicacion);
                    apilarConPersistencia("EDITAR", "PRODUCTO", joinSEP(vector<string>{to_string(id), oT, oTi, oC, oV, to_string(oA)}));
                    cout << "[EXITO] Producto actualizado.\n";
                }
                pausar();
            } else if (opt == '5') {
                int id = leerEntero(" ID a desactivar: ", 1, 2000000000, false, 0);
                if (multilista.desactivarProducto(id)) {
                    gestorBD.setEstado("Productos", "id_producto", to_string(id), 0);
                    apilarConPersistencia("DESACTIVAR", "PRODUCTO", to_string(id));
                    cout << "[EXITO] Desactivado.\n";
                } else cout << "[ERROR] No encontrado.\n";
                pausar();
            } else if (opt == '6') {
                int id = leerEntero(" ID a reactivar: ", 1, 2000000000, false, 0);
                if (multilista.reactivarProducto(id)) {
                    gestorBD.setEstado("Productos", "id_producto", to_string(id), 1);
                    cout << "[EXITO] Reactivado.\n";
                } else cout << "[ERROR] No encontrado o ya activo.\n";
                pausar();
            } else if (opt == '7') {
                int id = leerEntero(" ID a ELIMINAR: ", 1, 2000000000, false, 0);
                NodoProducto* p = multilista.buscarProductoIncluyeInactivos(id);
                if (p == nullptr) { cout << "[ERROR] No existe.\n"; pausar(); continue; }
                string snap = joinSEP(vector<string>{to_string(p->id_producto), p->titulo, p->tipo_producto, p->categoria, p->estado_validacion, to_string(p->anio_publicacion), p->codigo_grupo_fk, p->cod_rh_investigador_fk});
                string conf = leerTexto(" Escriba SI para confirmar: ", false);
                if (conf == "SI" && multilista.eliminarProductoFisico(id)) {
                    gestorBD.eliminarProductoDB(id);
                    apilarConPersistencia("ELIMINAR", "PRODUCTO", snap);
                    cout << "[EXITO] Eliminado fisico (RAM + BD).\n";
                } else cout << "[CANCELADO].\n";
                pausar();
            } else if (opt != '0' && opt != '\0') { cout << "[AVISO] Opcion invalida.\n"; pausar(); }
        } while (opt != '0');
    }
};

// ============================================================================
// FUNCIÓN PRINCIPAL MAIN
// ============================================================================

int main() {
    ConsolaApp app;
    app.iniciar();
    return 0;
}
