# PEA-i — Programa Estadístico de Análisis de Investigación
**Universidad Popular del Cesar (UPC) — Facultad de Ingeniería y Tecnológicas**  
**Asignatura:** Estructura de Datos (Taller 2) | **Semestre:** 2026-I  
**Docente:** Ing. Adith Bismarck Pérez Orozco  
**Estudiante:** Kovyn B. Mena (`kbmena@unicesar.edu.co`)  
**Documento Técnico Word:** [`Documentacion_Tecnica_GrupoXX.docx`](Documentacion_Tecnica_GrupoXX.docx) | **Paquete ZIP:** `Taller2_EstructuraDatos_GrupoXX.zip`

---

## 📌 Descripción General del Sistema

**PEA-i** es un sistema computacional integral de analítica científica diseñado para gestionar, auditar, catalogar y evaluar la producción investigativa de la Universidad Popular del Cesar conforme al modelo oficial **SCIENTI (GrupLAC y CvLAC de MinCiencias)** y a la taxonomía vigente del **Modelo de Medición MinCiencias 2024 (Convocatoria 957 / Anexo 1)**.

El sistema implementa dos soluciones complementarias y coordinadas (**C++17** y **Python**):
1. **Consola Primero (Filosofía Académica):** Operación 100% autónoma en consola para sustentación y evaluación del examen parcial, gobernada por **Estructuras de Datos Basadas en Punteros (TDAs puros)** sin contenedores automáticos de alto nivel (`std::vector`, `std::map`, etc.).
2. **Hipercubo de Información Multidimensional:** Modelado en memoria RAM mediante una **Multilista Ortogonal 3D** de enlaces cruzados entre Grupos (Eje X), Investigadores (Eje Y) y Productos (Eje Z).
3. **Persistencia Relacional SQLite3:** Contrato unificado bajo esquema ACID con soporte WAL (`data/pea_investigacion.db`).
4. **Portal Ejecutivo de Ciencia Abierta:** Interfaz web visual zero-dependency generada nativamente en C++ (`dist/visualizador_hipercubo.html`) y generador de informes PDF oficiales en ReportLab.

---

## 🏛️ Modelo Oficial MinCiencias 2024 & Taxonomía Científica

El sistema incorpora las **5 Macro-familias** oficiales y **15 tipologías** científicas con cálculo del **Índice de Producción Ponderada (IPP)**:

* **1. GNC (Generación de Nuevo Conocimiento):** Artículos indexados A1, A2, B, C; Libros de investigación; Capítulos de libro; Patentes de invención.
* **2. DTI (Desarrollo Tecnológico e Innovación):** Software registrado DNDA, Prototipos industriales, Diseños industriales, Regulaciones y normas técnicas, Informes técnicos de investigación.
* **3. ASC (Apropiación Social del Conocimiento):** Procesos de innovación social y ciencia participativa, Contenidos digitales y audiovisuales.
* **4. DPC (Divulgación Pública de la Ciencia):** Ponencias y participación en eventos científicos, Documentos de trabajo institucional (*Working Papers*), Talleres de difusión CTeI.
* **5. FRH (Formación de Recurso Humano):** Tesis de doctorado, Trabajos de grado de maestría y pregrado, Jurados evaluadores de tesis, Cursos de corta duración dictados, Acompañamiento Programa Ondas (`APO`).

---

## ⚡ Motor de Ingesta, Scraping y Hojas de Vida CvLAC

* **Detección Fidedigna de Aval Institucional (`chulo_1.jpg`)**: El motor de scraping analiza directamente el DOM de GrupLAC detectando la marca `chulo_1.jpg` (avalado oficialmente en la convocatoria) vs `chulo_0.jpg` (pendiente / sin aval). En GISICO (`COL0002099`), clasifica con exactitud matemática **168 productos validados** y **162 sin aval**.
* **Perfiles Curriculares Enriquecidos (`PerfilInvestigador`)**: Extrae y vincula la condición de **Par Evaluador MinCiencias**, enlace directo a **Google Scholar**, código internacional persistente **ORCID** y máximo nivel educativo.
* **Respaldo Offline para Sustentación (`data/snapshots/`)**: 90 archivos HTML oficiales (85 CvLAC + 5 GrupLAC) organizados con búsqueda recursiva nativa (`os.walk`), permitiendo demostraciones instantáneas en **0.08 segundos** sin depender de la red institucional.
* **Dataset Institucional UPC:** 62 grupos de investigación de la UPC, 362 investigadores y 3,351 productos científicos reales.

---

## 🧱 Las Estructuras de Datos Académicas Puras (RAM)

| TDA Implementado | Disciplina | Función en el Sistema PEA-i |
| :--- | :---: | :--- |
| **Multilista Ortogonal 3D** | Nodos con doble enlace cruzado | Modela el Hipercubo tridimensional. Conecta simultáneamente cada producto al grupo y al autor sin redundancia de memoria, ahorrando más del 99.8% de memoria frente a una matriz tridimensional tradicional. |
| **Pila (Stack)** | LIFO (*Last-In, First-Out*) | Módulo **Deshacer (Undo)**. Almacena las operaciones de inserción, modificación o borrado lógico en $O(1)$ para revertir el estado previo instantáneamente. |
| **Cola (Queue)** | FIFO (*First-In, First-Out*) | Motor de **Ingesta por Lotes**. Encola solicitudes de Web Scraping (GrupLAC/CvLAC), PDF y CSV, garantizando procesamiento en estricto orden de llegada en $O(1)$. |

---

## 📂 Estructura del Repositorio

```text
.
├── Makefile                           # Automatización integral (make, test, package, docs)
├── README.md                          # Guía ejecutiva y técnica del proyecto
├── integrantes.txt                    # Datos de autoría y acreditación académica
├── Documentacion_Tecnica_GrupoXX.docx # Especificación formal oficial en formato Word
├── Taller2_AB_PO_XX.cpp               # Punto de entrada C++ unificado
├── Taller2_AB_PO_XX.py                # Punto de entrada Python unificado
├── data/
│   ├── schema.sql                     # Contrato relacional DDL (Grupos, Investigadores, Productos, PerfilInvestigador)
│   ├── pea_investigacion.db           # Base de datos SQLite3 con 3,351 productos UPC
│   ├── catalogo_minciencias_2024.json # Catálogo maestro con ponderaciones e IPP
│   └── snapshots/                     # 90 snapshots oficiales GrupLAC y CvLAC para contingencia offline
├── docs/
│   ├── SPEC_TECNICO.md                # Especificación técnica exhaustiva (HU, Variables, Diagramas)
│   ├── GUIA_VIDEO_EXPLICATIVO.md      # Guion y guía palabra por palabra para la grabación del video (5.0)
│   ├── FEEDBACK_COMPANERO_PEA_I.md    # Auditoría comparativa y mejoras de arquitectura
│   └── generate_word_doc.py           # Generador automático del documento técnico Word (.docx)
├── reportes/
│   ├── Informe_GrupLAC_COL0002099.pdf # Reporte oficial PDF generado para GISICO
│   └── Informe_GrupLAC_COL0043834.pdf # Reporte oficial PDF generado para AITICE
├── scripts/
│   └── package_zip.py                 # Empaquetador automático para entrega limpia en ZIP
└── src/
    ├── cpp/                           # Solución C++17 Modular
    │   ├── include/                   # TDAs puros (Nodo, Multilista, Pila, Cola, Catalogo2024, GestorSQLite)
    │   ├── main.cpp                   # Consola interactiva C++
    │   └── test_tda.cpp               # Test runner unitario en C++
    └── python/                        # Solución Python Modular
        ├── structures/                # TDAs en clases Python (Multilista, Pila, Cola, Nodos)
        ├── core/                      # Ingesta (chulo_1, CvLAC, CSV, PDF), SQLite, ReportLab y Catálogo 2024
        ├── console.py                 # Consola interactiva Python
        └── test_tda.py                # Test runner unitario en Python
```

---

## 🛠️ Guía Rápida de Comandos (Makefile)

Todas las tareas están automatizadas mediante el archivo `Makefile`:

### 1. Compilación y Ejecución
```bash
# Compilar la aplicación C++:
make

# Ejecutar la consola C++:
make run

# Ejecutar la consola interactiva Python:
make run-py

# Abrir el Portal Ejecutivo Web y Dashboard de Ciencia Abierta:
make gui
# O directamente:
./pea_cpp --gui
```

### 2. Pruebas Unitarias Automatizadas
```bash
# Ejecuta la suite de verificación completa (100% de TDAs en C++ y Python):
make test
```

### 3. Generación de Documentación y Reportes
```bash
# Genera diagramas arquitectónicos y el documento Word oficial:
make docs
```

### 4. Empaquetado de Entrega Formal
```bash
# Limpia temporales, compila, genera documentación y ensambla el ZIP final:
make package
# Genera: Taller2_EstructuraDatos_GrupoXX.zip (Listo para enviar a adithperez@unicesar.edu.co)
```

---

## 👥 Acreditación Académica
* **Estudiante / Desarrollador:** Kovyn B. Mena (`kbmena@unicesar.edu.co`)
* **Asignatura:** Estructura de Datos — Grupo 01
* **Docente Evaluador:** Ing. Adith Bismarck Pérez Orozco
* **Universidad Popular del Cesar (UPC) — 2026**
