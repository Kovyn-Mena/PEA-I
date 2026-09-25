# Guía Maestra de Desarrollo y Colaboración — PEA-i (Taller 2)
**Universidad Popular del Cesar (UPC) — Facultad de Ingeniería y Tecnológicas**  
**Asignatura:** Estructura de Datos | **Semestre:** 2026-I | **Docente:** Ing. Adith Pérez  
**Meta:** 5.0 / 5.0 (Requerimientos Base + Todos los Complementos)

---

## 📌 1. Visión General del Proyecto

El **PEA-i** (Programa Estadístico de Análisis de Investigación) gestiona, analiza y visualiza la producción científica de la UPC siguiendo los estándares del modelo **SCIENTI (MinCiencias)**.

El taller exige **dos implementaciones coordinadas (C++ y Python)** que modelan la información en un **Hipercubo de Información** tridimensional mediante **estructuras de datos puras basadas en Nodos (Lista Enlazada, Multilista, Pila y Cola)** sin usar estructuras nativas automáticas.

### Entregables Exigidos por el Profesor:
1. `Taller2_AB_PO_XX.cpp` (Archivo de entrega principal en C++).
2. `Taller2_AB_PO_XX.py` (Archivo de entrega principal en Python).
3. `data/pea_investigacion.db` (Base de datos SQLite con datos reales).
4. `Documentacion_Tecnica_GrupoXX.docx` (Word con SPEC, Historias de Usuario, Casos de Uso y Diagramas).
5. `integrantes.txt` (Identificación del equipo).
6. **Video de Sustentación en YouTube (~10 min):** Los 3 integrantes visibles en cámara todo el tiempo e identidad institucional UPC.

---

## 🚀 2. Estado Actual del Repositorio (Lo que YA está 100% listo)

| Componente | Estado | Descripción |
| :--- | :---: | :--- |
| **Fase 0: Esquema y Contrato SQLite** |  Listo | Tablas `Grupos`, `Investigadores`, `Productos`, claves foráneas, datos semilla en `data/schema.sql` y `data/init_db.py`. |
| **Fase 1: TDAs Académicos Puros (C++)** |  Listo | `NodoGrupo`, `NodoInvestigador`, `NodoProducto` con punteros ortogonales en [Nodo.h](file:///home/kovyn/Documentos/Taller%202%20estructura/src/cpp/include/Nodo.h), [Multilista.h](file:///home/kovyn/Documentos/Taller%202%20estructura/src/cpp/include/Multilista.h), [Pila.h](file:///home/kovyn/Documentos/Taller%202%20estructura/src/cpp/include/Pila.h) (Undo) y [Cola.h](file:///home/kovyn/Documentos/Taller%202%20estructura/src/cpp/include/Cola.h) (Ingesta). |
| **Fase 1: TDAs Académicos Puros (Python)** |  Listo | Clases equivalentes en `src/python/structures/` probadas con assertions al 100%. |
| **Fase 2: Consola Autónoma C++** |  Listo | Menú con lectura instantánea de teclas (`getch`), borrado de pantalla multiplataforma, protección de `Ctrl+C`, CRUD completo, Pila Undo, filtro de años y persistencia SQLite. |
| **Fase 2: Consola Autónoma Python** |  Listo | Mismo menú interactivo con paridad 100% a C++ en [src/python/console.py](file:///home/kovyn/Documentos/Taller%202%20estructura/src/python/console.py) y persistencia en [src/python/core/db.py](file:///home/kovyn/Documentos/Taller%202%20estructura/src/python/core/db.py). |
| **Makefile de Automatización** |  Listo | Comandos de 1 sola línea para compilar, probar y ejecutar ambos lenguajes. |

---

## 🛡️ 3. Reglas de Oro (Para NO romper el código existente)

1. **NO modificar `data/schema.sql` ni la estructura de las tablas:** Es el contrato sagrado entre C++ y Python. Cualquier cambio en columnas o nombres rompería la compatibilidad.
2. **NO reemplazar las estructuras TDA por listas/diccionarios nativos:** Toda la información en memoria RAM debe residir en la `Multilista` creada con nodos. Esto es lo que evalúa el profesor.
3. **Consola Primero:** La consola debe seguir corriendo al 100% de manera autónoma. La interfaz gráfica (GUI) que se desarrolle debe ser una capa externa que se active mediante un argumento opcional (`--gui`).
4. **NUNCA hacer commit directo a `main` ni a `dev`:** Siempre trabajar en ramas de funcionalidad (`feature/...`) y subir cambios mediante Pull Request (PR).

---

## 👥 4. División de Roles y Asignación de Tareas

```
                   +--------------------------------------------+
                   |        REPOSITORIO GITHUB (PEA-i)          |
                   +---------------------+----------------------+
                                         |
               +-------------------------+-------------------------+
               |                                                   |
   [PERSONA A - C++ Lead]                               [PERSONA B - Python Lead]
   - Mantenimiento Core C++                             - Módulo de Ingesta Masiva (Fase 3)
   - Interoperabilidad popen (Fase 4)                   - Dashboard GUI Tkinter (Fase 5)
   - Pruebas y Revisión de PRs                          - Pruebas cruzadas y PRs
               |                                                   |
               +-------------------------+-------------------------+
                                         |
                               [PERSONA C - Video/Doc]
                               - Redacción Word formal (Casos de Uso, HU, DER)
                               - Diapositivas institucionales UPC
                               - Estructura y edición del Video (10 min)
```

---

## 💻 5. Tareas Pendientes para PERSONA B (Python Lead)

### 🎯 Tarea 1: Módulo de Ingesta Masiva (Fase 3)
* **Rama asignada:** `feature/ingesta-datos`
* **Archivo a crear:** `src/python/core/ingesta.py`
* **Librerías a usar:** `requests`, `beautifulsoup4`, `pypdf`, `csv` (todas en `requirements.txt`).
* **Requerimientos exactos del Taller (Punto 7):**
  1. **Web Scraping GrupLAC:** Descargar y parsear datos desde la URL oficial de MinCiencias dada en el taller:  
     `https://scienti.minciencias.gov.co/gruplac/jsp/visualiza/visualizagr.jsp?nro=00000000002099`  
     *Extraer:* Nombre del grupo, líder, integrantes de la tabla de recursos humanos y lista de productos.
  2. **Web Scraping CvLAC:** Descargar datos del investigador desde:  
     `https://scienti.minciencias.gov.co/cvlac/visualizador/generarCurriculoCv.do?cod_rh=0000494917`
  3. **Lector de CSV:** Leer archivos tabulares estructurados (como `data/muestra_upc.csv`).
  4. **Lector de PDF:** Extraer texto y tablas de informes en formato PDF (como `data/muestra_upc.pdf`) usando `pypdf`.
  5. **Uso de la Cola (TDA FIFO):**  
     Las fuentes a procesar deben agregarse a la `Cola` de ingesta (`cola.encolar(tipo, ruta)`). El procesador las atiende secuencialmente (`cola.desencolar()`), extrae los registros e invoca `GestorPersistencia.guardar_en_bd()` o los inserta en la base de datos SQLite.

### 🎯 Tarea 2: Dashboard Visual e Interactivo (Fase 5)
* **Rama asignada:** `feature/python-gui`
* **Archivo a crear:** `src/python/gui.py`
* **Librerías a usar:** `tkinter` (nativo de Python) y `matplotlib`.
* **Requerimientos exactos del Taller (Puntos 12.b y 14.c):**
  1. Crear una ventana limpia con pestañas (*Grupos*, *Investigadores*, *Productos*, *Estadísticas*).
  2. Incrustar gráficos de `matplotlib`:
     * Gráfico de barras de productos por categoría (A1, A, B, C).
     * Histograma o distribución de producción por año.
  3. Selector de ventana de observación (últimos 2 años, últimos 5 años, rango libre) que actualice los gráficos dinámicamente en pantalla.
  4. La GUI debe leer los datos desde `GestorPersistencia.cargar_desde_bd()`.

---

## 🔄 6. Flujo de Trabajo en Git (Guía Paso a Paso para Persona B)

### Paso 1: Clonar el Repositorio y Configurar Entorno
```bash
# 1. Clonar el repositorio
git clone https://github.com/Kovyn-Mena/PEA-I.git
cd PEA-I

# 2. Instalar dependencias de Python
pip install -r requirements.txt
```

### Paso 2: Cambiarse a la Rama de Trabajo
```bash
# Descargar todas las ramas remotas
git fetch origin

# Pasarse a la rama de ingesta para empezar a desarrollar
git checkout feature/ingesta-datos
```

### Paso 3: Probar que todo funcione antes de programar
```bash
# Ejecutar las pruebas unitarias
make test

# Probar la consola actual de Python
make run-py
```

### Paso 4: Realizar Cambios y Commits Pequeños
Hacer commits descriptivos siguiendo la convención:
```bash
# Ejemplo tras implementar el parser de CSV:
git add src/python/core/ingesta.py
git commit -m "feat(ingesta): implementar lector de archivos CSV y encolamiento en Cola TDA"

# Ejemplo tras implementar el Web Scraper de GrupLAC:
git add src/python/core/ingesta.py
git commit -m "feat(ingesta): implementar web scraper con BeautifulSoup para URLs GrupLAC"
```

### Paso 5: Subir Cambios a GitHub y Crear Pull Request (PR)
```bash
# Subir la rama a GitHub
git push origin feature/ingesta-datos
```
* Ir a la página del repositorio en GitHub: `https://github.com/Kovyn-Mena/PEA-I`.
* Crear un **Pull Request (PR)** desde `feature/ingesta-datos` **hacia la rama `dev`** (¡NUNCA directo a `main`!).
* Persona A revisa el PR, prueba el código y hace el `Merge`.

---

## 🛠️ 7. Atajos Rápidos del Makefile

| Comando | Acción |
| :--- | :--- |
| `make` o `make run-cpp` | Compila y ejecuta la aplicación de consola C++ |
| `make run-py` | Ejecuta la aplicación de consola Python |
| `make test` | Ejecuta todas las pruebas unitarias de TDAs (C++ y Python) |
| `make clean` | Elimina binarios compilados y archivos temporales |

---

## 🎬 8. Guion y Reglas para el Video de Sustentación (Persona C y Todo el Equipo)

* **Duración:** Alrededor de **10 minutos**.
* **Identidad Institucional:** Usar portada, diapositivas y colores oficiales de la **Universidad Popular del Cesar (UPC)**.
* **Cámaras Activas:** **Los 3 integrantes deben ser visibles en video TODO el tiempo** (usar Zoom, Google Meet o Teams con las 3 cámaras fijas en pantalla compartida).
* **Distribución del Guion:**
  * **Minuto 0:00 - 2:00 (Persona C):** Presentación institucional, introducción a MinCiencias SCIENTI, explicación teórica del Hipercubo y justificación de los 4 TDAs.
  * **Minuto 2:00 - 5:30 (Persona A):** Demostración C++ (pregunta de inicio, CRUD en consola, demostración de la Pila Undo en vivo, tablas de resumen y filtro de años).
  * **Minuto 5:30 - 8:30 (Persona B):** Demostración Python (demostración del Web Scraper procesando URL en vivo, lectura de PDF/CSV con la Cola, persistencia compartida en SQLite y Dashboard gráfico de barras e histogramas).
  * **Minuto 8:30 - 10:00 (Persona C / Todos):** Conclusiones, verificación del repositorio GitHub (ramas y PRs) y cierre.
