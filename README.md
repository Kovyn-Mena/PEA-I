# PEA-i — Programa Estadístico de Análisis de Investigación
**Universidad Popular del Cesar (UPC) — Facultad de Ingeniería y Tecnológicas**  
**Asignatura:** Estructura de Datos (Taller 2)  
**Semestre:** 2026-I  

## 📌 Descripción del Proyecto
PEA-i es una solución de software desarrollada en dos implementaciones independientes y coordinadas (**C++** y **Python**) para la gestión, análisis estadístico y visualización de la información de investigación científica (SCIENTI - MinCiencias) de la Universidad Popular del Cesar.

El sistema modela la información en un **Hipercubo de información multidimensional** implementado mediante **Estructuras de Datos basadas en Nodos (Listas Enlazadas, Multilistas, Pila y Cola)** sin depender de estructuras mágicas de alto nivel, permitiendo una defensa académica impecable y un funcionamiento 100% autónomo por consola.

---

## 📂 Estructura del Repositorio
```text
.
├── data/
│   ├── schema.sql             # Contrato de base de datos relacional SQLite
│   ├── init_db.py             # Script de inicialización y verificación de BD
│   ├── muestra_upc.csv        # Dataset de prueba local (CSV)
│   └── muestra_upc.pdf        # Documento PDF de prueba local
├── docs/
│   ├── spec-inicial.md        # Especificación técnica, variables E/S y TDA
│   └── architecture.md        # Diagrama de arquitectura y flujo C++ <-> Python
├── src/
│   ├── cpp/                   # Solución en C++ (Persona A)
│   │   ├── include/           # Definiciones de TDA (Nodos, Listas, Pila, Cola)
│   │   ├── core/              # Lógica de negocio y persistencia SQLite
│   │   └── main.cpp           # Consola interactiva C++
│   └── python/                # Solución en Python (Persona B)
│       ├── structures/        # TDAs basados en clases y nodos enlazados
│       ├── core/              # Ingesta (Scraping, PDF, CSV) y SQLite
│       ├── console.py         # Consola interactiva Python
│       └── gui.py             # Dashboard visual Tkinter / Matplotlib
├── integrantes.txt            # Datos de los estudiantes
└── README.md
```

---

## 🛠️ Requisitos de Compilación y Ejecución

### C++
* Compilador `g++` con soporte C++17.
* Librería SQLite3 de desarrollo (`libsqlite3-dev`).
* Compilación:
  ```bash
  g++ -std=c++17 -Wall src/cpp/test_sqlite.cpp -lsqlite3 -o src/cpp/test_sqlite
  ```

### Python
* Python 3.10+
* Módulos necesarios para ingesta y gráficos:
  ```bash
  pip install requests beautifulsoup4 pypdf matplotlib
  ```

---

## 👥 Equipo de Trabajo
* **Persona A (Lead C++):** Estructuras TDA C++, persistencia SQLite, filtros y tablas de consola.
* **Persona B (Lead Python):** Estructuras TDA Python, módulo de ingesta (Scraping, PDF, CSV), persistencia y Dashboard Tkinter.
* **Persona C (Documentación y Video):** Redacción técnica (SPEC, HU, Casos de Uso), presentación y edición del video.
