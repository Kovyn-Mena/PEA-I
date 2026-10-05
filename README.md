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

## 🚀 Guía de Ejecución Rápida y Multiplataforma

> [!IMPORTANT]
> **¿Por qué a tu compañero o amigo no le abría el programa?**
> 1. **Si usa Windows:** El archivo `pea_cpp` es un ejecutable binario de **Linux (ELF 64-bit)**. En Windows, hacer doble clic en `pea_cpp` muestra el error *"Esta aplicación no se puede ejecutar en este equipo"* o no hace nada. Además, el comando `make` no viene instalado por defecto en la consola de Windows.
> 2. **Solución Inmediata para Windows:** Usar la versión en **Python** (que no requiere compilar absolutamente nada) o hacer doble clic en el lanzador automático `ejecutar_windows.bat`.
> 3. **Si usa Linux:** Si descargó el código comprimido en ZIP, el archivo ejecutable puede haber perdido los permisos de ejecución (`chmod +x pea_cpp`) o puede faltar la librería SQLite3 de desarrollo (`sudo apt install libsqlite3-dev`).

---

### 💻 1. Ejecución en Windows (Para Compañeros y Docente)

En Windows tienes scripts automatizados de un solo clic que resuelven todo sin configuraciones complejas:

#### 🌟 Opción 1: Lanzador Maestro con Menú Interactivo (¡El Más Recomendado!)
Simplemente haz **doble clic** sobre:
```text
INICIAR_WINDOWS.bat
```
Se abrirá un menú interactivo en la consola de Windows donde puedes elegir con un número:
* `[1]` Ejecutar Consola en Python (Abre al instante sin compilar nada).
* `[2]` Compilar y Ejecutar en C++ (Detecta automáticamente tu compilador y genera `pea_cpp.exe`).
* `[3]` Abrir Portal Web Ejecutivo (Visualizador del Hipercubo en Edge/Chrome).
* `[4]` Ver Documentación Técnica Oficial Word (`.docx`).
* `[5]` Ver Informe PDF Oficial de Investigación (GISICO).
* `[6]` Ejecutar Pruebas Unitarias de Estructuras (TDAs).

#### ⚙️ Opción 2: Compilar y Ejecutar en C++ en Windows
Si deseas ejecutar específicamente la versión en **C++** en Windows:
1. Haz doble clic sobre:
   ```text
   compilar_cpp_windows.bat
   ```
2. El script buscará automáticamente si tienes instalado:
   * **MSYS2 UCRT64** (`C:\msys64\ucrt64\bin\g++.exe` — configuración estándar de la UPC).
   * **MSYS2 MINGW64** (`C:\msys64\mingw64\bin\g++.exe`).
   * **Code::Blocks** (`C:\Program Files\CodeBlocks\MinGW\bin\g++.exe`).
   * **Dev-C++** (`C:\Program Files (x86)\Dev-Cpp\MinGW64\bin\g++.exe`).
   * O cualquier **g++** en el `PATH` del sistema.
3. Compilará `pea_cpp.exe` y lo iniciará de inmediato.
4. *Si no tienes ningún compilador C++ instalado*, el script te avisará cordialmente y te ofrecerá iniciar la versión de Python que tiene exactamente los mismos TDAs y la misma base de datos sin compilar nada.

#### ⚡ Opción 3: Ejecución Inmediata en Python (Doble Clic Directo)
Si solo quieres abrir la consola interactiva sin compilar C++:
* Haz doble clic sobre:
  ```text
  ejecutar_windows.bat
  ```
* O por terminal (CMD / PowerShell):
  ```powershell
  python Taller2_AB_PO_XX.py
  ```

#### 🌐 Opción 4: Portal Web Ejecutivo (Visualizador Gráfico del Hipercubo)
Para ver la interfaz gráfica moderna con tarjetas, estadísticas interactivas, filtrado por macro-familias y perfiles curriculares CvLAC enriquecidos con enlaces y fotos:
* Haz doble clic directo sobre:
  ```text
  dist/visualizador_hipercubo.html
  ```
  *(Es 100% autocontenido y funciona offline en Google Chrome, Microsoft Edge o Mozilla Firefox sin necesidad de servidores web ni dependencias externas).*

---

### 🐧 2. Ejecución en Linux (Ubuntu, Debian, Linux Mint, Fedora, Arch)

En Linux puedes utilizar tanto la solución nativa de alto rendimiento en **C++17** como la solución en **Python 3**.

#### Requisitos Previos en Linux (Se instalan una única vez):
```bash
sudo apt update
sudo apt install -y build-essential libsqlite3-dev python3 python3-pip
```

#### Modo C++17 (Nativo con TDAs Puros y Punteros):
```bash
# 1. Compilar todo el proyecto:
make

# 2. Ejecutar la consola interactiva C++:
make run
# O directamente:
./pea_cpp
```

#### Modo Python 3:
```bash
# Ejecutar la consola interactiva en Python:
make run-py
# O directamente:
python3 Taller2_AB_PO_XX.py
```

#### Abrir el Portal Web Ejecutivo desde la terminal de Linux:
```bash
make gui
# O también:
./pea_cpp --gui
```

---

### 🍎 3. Ejecución en macOS

En macOS, la forma más rápida y directa es a través de Python 3:
```bash
python3 Taller2_AB_PO_XX.py
```
O para compilar la versión C++ utilizando Homebrew:
```bash
brew install sqlite3
clang++ -std=c++17 -I$(brew --prefix sqlite3)/include -L$(brew --prefix sqlite3)/lib src/cpp/main.cpp -lsqlite3 -o pea_mac
./pea_mac
```

---

### 🔧 Solución de Problemas Frecuentes (FAQ / Troubleshooting)

| Mensaje de Error o Situación | Causa | Solución Paso a Paso |
| :--- | :--- | :--- |
| **"Esta aplicación no se puede ejecutar en este equipo"** (Windows) | Se intentó hacer doble clic en `pea_cpp` (que es un binario compilado para Linux). | Ejecuta `ejecutar_windows.bat` o abre la terminal y escribe `python Taller2_AB_PO_XX.py`. |
| **`'make' no se reconoce como un comando interno o externo`** (Windows) | Windows CMD/PowerShell no incluye la utilidad `make` de Linux por defecto. | En Windows no necesitas `make`. Ejecuta `python Taller2_AB_PO_XX.py` o abre `dist/visualizador_hipercubo.html`. |
| **`bash: ./pea_cpp: Permiso denegado`** (`Permission denied` en Linux) | El archivo descargado o descomprimido perdió los permisos de ejecución en Linux. | Ejecuta en terminal: `chmod +x pea_cpp` y vuelve a correr `./pea_cpp`. |
| **`fatal error: sqlite3.h: No such file or directory`** o `cannot find -lsqlite3` | Falta la cabecera de desarrollo de SQLite3 en el sistema Linux. | Instala la librería con: `sudo apt install libsqlite3-dev`. |
| **`error: externally-managed-environment`** al usar `pip` en Linux moderno | Protección PEP 668 en Ubuntu 23+/Debian 12+ para proteger el sistema operativo. | Crea un entorno virtual:<br>`python3 -m venv .venv`<br>`source .venv/bin/activate`<br>`pip install -r requirements.txt` |
| **`ModuleNotFoundError: No module named 'requests'` o `'bs4'`** | Faltan las librerías opcionales de scraping web en vivo. | Ejecuta `pip install -r requirements.txt`. *(Nota: La consola, la multilista, los 3,351 productos y las consultas funcionan aún sin estas librerías).* |
| **¿Cómo ver los reportes PDF oficiales generados?** | Los documentos oficiales se encuentran en la carpeta `reportes/`. | Abre `reportes/Informe_GrupLAC_COL0002099.pdf` en cualquier visor de PDF del sistema. |

---

## 🛠️ Automatización con Makefile (Desarrollo y Evaluación en Linux)

Para usuarios y docentes en entornos Linux/Unix, todas las tareas del ciclo de vida del software están completamente automatizadas:

```bash
make          # Compila el ejecutable nativo C++ (pea_cpp)
make run      # Ejecuta la consola interactiva en C++
make run-py   # Ejecuta la consola interactiva en Python
make gui      # Abre el Portal Ejecutivo y Dashboard Web de Ciencia Abierta
make test     # Ejecuta la suite de pruebas unitarias (100% C++ y Python)
make docs     # Genera el documento técnico oficial en Word (.docx)
make package  # Limpia, prueba, compila y empaqueta el ZIP de entrega final
make clean    # Limpia archivos objeto y binarios temporales
```

---

## 👥 Acreditación Académica
* **Estudiante / Desarrollador:** Kovyn B. Mena (`kbmena@unicesar.edu.co`)
* **Asignatura:** Estructura de Datos — Grupo 01
* **Docente Evaluador:** Ing. Adith Bismarck Pérez Orozco
* **Universidad Popular del Cesar (UPC) — 2026**
