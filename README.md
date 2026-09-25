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

## 🛠️ Instrucciones de Compilación y Ejecución Directa

### 1. Ejecución en C++ (Persona A)

#### Opción A (Rápida con Makefile):
* **Compilar y Ejecutar:**
  ```bash
  make run
  ```
* **Solo Compilar:**
  ```bash
  make
  ./pea_cpp
  ```
* **Ejecutar Suite de Pruebas Unitarias:**
  ```bash
  make test
  ```
* **Limpiar binarios:**
  ```bash
  make clean
  ```

#### Opción B (Compilación directa con g++):
```bash
g++ -std=c++17 -Wall -Isrc/cpp/include Taller2_AB_PO_XX.cpp -lsqlite3 -o Taller2_AB_PO_XX
./Taller2_AB_PO_XX
```

---

### 2. Ejecución en Python (Persona B)
* **Requisitos:**
  ```bash
  pip install -r requirements.txt
  ```

#### Opción A (Rápida con Makefile):
* **Ejecutar la consola interactiva Python:**
  ```bash
  make run-py
  ```

#### Opción B (Ejecución directa del entregable):
```bash
python3 Taller2_AB_PO_XX.py
```

* **Ejecutar pruebas unitarias de TDAs:**
  ```bash
  python3 src/python/test_tda.py
  # O ejecutar todas las pruebas (C++ y Python) juntas:
  make test
  ```

---

## 👥 Equipo de Trabajo
* **Persona A (Lead C++):** Estructuras TDA C++, persistencia SQLite, filtros y tablas de consola.
* **Persona B (Lead Python):** Estructuras TDA Python, módulo de ingesta (Scraping, PDF, CSV), persistencia y Dashboard Tkinter.
* **Persona C (Documentación y Video):** Redacción técnica (SPEC, HU, Casos de Uso), presentación y edición del video.
