# Guía Maestra de Desarrollo, Arquitectura y Colaboración — PEA-i (Taller 2)
**Universidad Popular del Cesar (UPC) — Facultad de Ingeniería y Tecnológicas**  
**Programa:** Ingeniería de Sistemas | **Asignatura:** Estructura de Datos (2026-I)  
**Docente:** Ing. Adith Pérez | **Meta de Evaluación:** 5.0 / 5.0  

---

## 📌 1. Visión General del Proyecto

El **PEA-i** (Programa Estadístico de Análisis de Investigación) es una plataforma diseñada para gestionar, analizar, auditar y visualizar la producción científica de la Universidad Popular del Cesar siguiendo el modelo nacional **SCIENTI de MinCiencias**.

El taller exige el desarrollo de **dos soluciones de software coordinadas (una en C++ y otra en Python)** que compartan los mismos datos y modelen la información mediante un **Hipercubo de Información** tridimensional implementado con **Estructuras de Datos Académicas Puras basadas en Nodos** (sin contenedores automáticos de biblioteca estándar).

---

## 🏛️ 2. Lo que se ha Desarrollado Hasta Ahora y el PORQUÉ de Cada Decisión

Se han completado integralmente las **Fases 0, 1 y 2** en ambos lenguajes, garantizando una base arquitectónica robusta, libre de errores y con paridad total:

### 🔹 Fase 0: Contrato Relacional y Persistencia Base (SQLite)
* **Archivos:** `data/schema.sql`, `data/init_db.py`, `data/pea_investigacion.db`, `data/muestra_upc.csv`.
* **¿Qué se hizo?:** Se definió el esquema relacional con 4 tablas (`Grupos`, `Investigadores`, `Productos`, `HistorialAcciones`) con integridad referencial (`ON DELETE CASCADE`), y un script de inicialización con datos reales de la UPC (grupos GIDSE, GISI, BIOTEC; perfiles reales como el del docente Adith Pérez y productos científicos indexados).
* **¿Por qué esta decisión?:**
  1. *Interoperabilidad sin servidores:* SQLite es un motor embebido en un único archivo (`.db`) que tanto C++ (`libsqlite3`) como Python (`sqlite3`) leen y escriben nativamente sin requerir instalar MySQL o PostgreSQL ni configurar puertos de red.
  2. *Contrato Sagrado:* La base de datos actúa como la **única fuente de la verdad**, garantizando que lo que crea o modifica C++ sea visto de inmediato por Python y viceversa.
  3. *Datos Semilla Reales:* Contar desde el día 1 con datos reales de la UPC permite probar consultas, filtros y estadísticas sin tener que tipear datos ficticios manualmente.

---

### 🔹 Fase 1: TDAs Académicos Puros (C++ y Python)
* **Archivos C++:** `src/cpp/include/Nodo.h`, `Multilista.h`, `Pila.h`, `Cola.h`.
* **Archivos Python:** `src/python/structures/nodos.py`, `multilista.py`, `pila.py`, `cola.py`.
* **Pruebas:** `src/cpp/test_tda.cpp` y `src/python/test_tda.py` (ejecutables con `make test`).
* **¿Qué se hizo?:** Se implementaron desde cero las 4 estructuras exigidas por el docente utilizando únicamente apuntadores/referencias de memoria entre nodos:
  1. **Multilista Ortogonal (Hipercubo 3D):** Nodos con doble enlace ortogonal. `NodoGrupo` apunta horizontalmente al siguiente grupo y verticalmente a su lista de investigadores y productos. A su vez, `NodoProducto` está enlazado simultáneamente al grupo (`sigProductoGrupo`) y al investigador autor (`sigProductoInvestigador`).
  2. **Pila (Stack - LIFO):** Estructura basada en nodos con puntero `siguiente` para el historial de cambios y la función **Deshacer (Undo)**.
  3. **Cola (Queue - FIFO):** Estructura basada en nodos con punteros `frente` y `final` para la ingesta secuencial de datos por lotes.
* **¿Por qué esta decisión?:**
  1. *Exigencia Estricta del Docente:* En Estructura de Datos está terminantemente prohibido usar colecciones de alto nivel como `std::vector`, `std::list` o listas/diccionarios de Python para almacenar las entidades. La evaluación depende de dominar el manejo explícito de punteros y memoria dinámica.
  2. *Eficiencia del Hipercubo:* El modelo multidimensional tradicional en matrices densas desperdiciaría gigabytes de memoria en casillas vacías (matriz dispersa). La Multilista Ortogonal solo consume memoria para las relaciones que realmente existen ($O(1)$ en enlaces cruzados) sin duplicar entidades.

---

### 🔹 Fase 2: Consolas Autónomas Interactivas (C++ y Python)
* **Archivos C++:** `src/cpp/include/ConsolaApp.h`, `src/cpp/main.cpp`, `Taller2_AB_PO_XX.cpp`.
* **Archivos Python:** `src/python/console.py`, `src/python/main.py`, `Taller2_AB_PO_XX.py`.
* **¿Qué se hizo?:**
  1. **Inicio Flexible (Punto 10 del Taller):** Al arrancar, pregunta si se desea precargar la base de datos SQLite en la Multilista o iniciar con estructuras vacías en memoria RAM.
  2. **CRUD Completo:** Creación, consulta detallada, edición de campos, desactivación (borrado lógico) y eliminación física definitiva para Grupos, Investigadores y Productos.
  3. **Deshacer (Undo) con Pila:** Permite revertir la última acción destructiva o modificación recuperando el estado anterior en $O(1)$.
  4. **Filtro de Ventana de Observación (Punto 10):** Permite filtrar dinámicamente la producción científica por los últimos 2 años, últimos 5 años o cualquier rango arbitrario.
  5. **Resumen Estadístico Descriptivo en Consola (Punto 12.a):** Tablas de indicadores por grupo e investigador.
  6. **Búsqueda Inteligente y Ejemplos Aleatorios:** En las consultas de detalle ya no es obligatorio conocerse ni copiar de memoria los códigos largos. Al escribir parte del nombre (ej. `gidse`, `adith`, `hipercubo`) el sistema lo localiza automáticamente; y si simplemente se presiona **ENTER** en blanco, el sistema selecciona y despliega un ejemplo real al azar.
  7. **Experiencia de Usuario en Terminal (UX):**
     * *Lectura instantánea de tecla (`getch`):* Los menús y pausas responden inmediatamente al presionar una tecla (1, 2, 0, etc.) sin obligar al usuario a presionar ENTER adicional.
     * *Borrado de pantalla automático:* Limpieza fluida entre transiciones de menú (`cls` en Windows, secuencias ANSI en Linux/Mac).
     * *Opción estandarizada de retorno:* Siempre la opción `0` permite regresar al menú anterior o cancelar una operación.
     * *Protección de Copia con Ctrl+C:* Evita que el usuario cierre el programa por accidente al presionar `Ctrl+C` en lugar de `Ctrl+Shift+C` en la terminal.
* **¿Por qué esta decisión?:**
  * La consola es el núcleo que evaluará el docente en el examen parcial de código. Debe ser 100% autónoma, a prueba de fallos y no depender de ninguna ventana gráfica para funcionar.

---

## 👥 3. División de Trabajo y Sincronización del Equipo

Para lograr una nota de **5.0 / 5.0**, el trabajo se organiza en dos roles complementarios para que el avance sea paralelo sin pisarse el código:

```
                      +---------------------------------------+
                      |       REPOSITORIO GITHUB (PEA-i)      |
                      +-------------------+-------------------+
                                          |
                +-------------------------+-------------------------+
                |                                                   |
    [PERSONA A - Lead C++ / Core]                       [PERSONA B - Lead Python / Ingesta / GUI]
    (Kovyn - Linux CachyOS)                             (Compañero - Windows)
    * Mantenimiento de la Multilista C++                * Fase 3: Ingesta Masiva (Scraping/PDF/CSV)
    * Fase 4: Interoperabilidad C++ <-> Python          * Fase 5: Dashboard Gráfico Tkinter
    * Revisión de PRs y Merges a 'dev'                  * Pruebas en Windows y apertura de PRs
```

### ¿Qué estará haciendo Persona A (Kovyn) y por qué?
1. **Fase 4 — Interoperabilidad entre C++ y Python (Punto 14.d para 5.0):**
   * *¿Qué hará?:* Implementará llamadas desde C++ hacia módulos de Python usando tuberías estándar del sistema (`popen()` / `exec`).
   * *¿Por qué?:* Permite que la consola en C++ pueda solicitarle a Python que ejecute el Web Scraper de MinCiencias o que abra el Dashboard gráfico sin duplicar motores de interfaz gráfica pesados en C++.
2. **Revisión, Integración y Pruebas Cruzadas:**
   * Garantizar que las ramas de Persona B se integren limpiamente a `dev` sin conflictos.

### ¿Qué estará haciendo Persona B (Compañero) y por qué?
Persona B se enfocará en las **Fases 3 y 5 en Python**, donde el lenguaje ofrece las mejores herramientas del mercado:

#### 🎯 Tarea 1: Módulo de Ingesta Masiva (Fase 3)
* **Rama Git:** `feature/ingesta-datos`
* **Archivo:** `src/python/core/ingesta.py`
* **¿Por qué existe esta fase?:** El Punto 7 del taller exige que el sistema no solo reciba datos por teclado, sino que sea capaz de descargar y procesar información automáticamente de 3 fuentes distintas:
  1. **Web Scraping GrupLAC:** Descargar el HTML de un grupo desde la URL oficial de MinCiencias dada por el docente:
     `https://scienti.minciencias.gov.co/gruplac/jsp/visualiza/visualizagr.jsp?nro=00000000002099`  
     *Extraer:* Nombre del grupo, líder, integrantes y tabla de productos.
  2. **Web Scraping CvLAC:** Descargar el currículo del investigador desde la URL oficial dada por el docente:
     `https://scienti.minciencias.gov.co/cvlac/visualizador/generarCurriculoCv.do?cod_rh=0000494917`  
     *Extraer:* Nombre, categoría del investigador y sus publicaciones.
  3. **Lector de Archivos CSV y PDF:**
     * Archivos CSV: Leer archivos tabulares estructurados (como `data/muestra_upc.csv`).
     * Archivos PDF: Extraer texto estructurado de reportes PDF usando la librería `pypdf`.
  4. **Uso Obligatorio de la Cola TDA (FIFO):**
     * Cada fuente o URL a procesar se añade a la `Cola` (`cola.encolar(tipo, origen)`).
     * El procesador consume de la cola (`cola.desencolar()`), extrae los registros y los guarda en la base de datos SQLite con `GestorPersistencia`.

#### 🎯 Tarea 2: Dashboard Gráfico Interactivo (Fase 5)
* **Rama Git:** `feature/python-gui`
* **Archivo:** `src/python/gui.py` (ejecutable opcional mediante bandera `--gui`).
* **¿Por qué existe esta fase?:** El Punto 12.b del taller exige explícitamente:
  > *"En Python el programa mostrará un DASHBOARD con la información estadística, histogramas y diagramas de barras. Ejemplo: https://sistemainvestigacion.uniminuto.edu/PGrupos/Ver/141"*
* **Qué debe incluir:**
  1. Ventana construida en **Tkinter** (nativo de Python, sin dependencias complejas).
  2. Gráficos interactivos de **Matplotlib** incrustados en la interfaz:
     * Gráfico de barras: Distribución de productos por categoría (`A1`, `A`, `B`, `C`).
     * Histograma: Producción científica por año.
  3. Control interactivo de ventana de observación (selector de años: últimos 2 años, últimos 5 años, rango personalizado) que actualice los gráficos dinámicamente.

---

## 💻 4. Guía de Configuración en Windows (Para Persona B)

Dado que Persona A trabaja en **Linux (CachyOS)** y Persona B trabajará en **Windows**, el proyecto ya fue programado y blindado para ser 100% multiplataforma. Sigue estos pasos para dejar tu entorno listo en Windows:

### 1. Herramientas a Descargar e Instalar en Windows
1. **Git para Windows:** Descargar desde [git-scm.com](https://git-scm.com/).
   * Durante la instalación, en la opción de finales de línea (*Line Ending Conversion*), selecciona:
     `Checkout Windows-style, commit Unix-style line endings` (o ejecuta `git config --global core.autocrlf true`).
2. **Python 3.10 o superior:** Descargar desde [python.org](https://www.python.org/).
   * ⚠️ **IMPORTANTE:** En la primera pantalla del instalador, marcar la casilla **"Add python.exe to PATH"**.
3. **Compilador C++ (MinGW-w64):**
   * Opción recomendada sencilla: [WinLibs](https://winlibs.com/) o [w64devkit](https://github.com/skeeto/w64devkit/releases) (descomprimir y agregar la carpeta `bin` al PATH de Windows).
   * Opcional: También puedes usar **WSL2 (Windows Subsystem for Linux)** o **MSYS2**.
4. **Editor de Código:** [Visual Studio Code](https://code.visualstudio.com/).
   * Extensiones sugeridas en VS Code: *Python*, *C/C++*, y *SQLite Viewer* (para explorar visualmente `data/pea_investigacion.db`).
5. **DB Browser for SQLite (Opcional, muy útil):** [sqlitebrowser.org](https://sqlitebrowser.org/) para ver las tablas y datos con interfaz visual.

---

### 2. Clonar el Repositorio y Configurar Dependencias en Windows
Abre **Git Bash**, **PowerShell** o la terminal de VS Code y ejecuta:

```bash
# 1. Clonar el proyecto
git clone https://github.com/Kovyn-Mena/PEA-I.git
cd PEA-I

# 2. Instalar las librerías de Python requeridas
pip install -r requirements.txt
```

---

### 3. Comandos de Ejecución y Pruebas en Windows

Si tienes instalado `make` (en Git Bash o MSYS2), los comandos son idénticos:
```bash
make test      # Ejecuta todas las pruebas unitarias (C++ y Python)
make run-py    # Ejecuta la consola interactiva en Python
make run-cpp   # Compila y ejecuta la consola C++
```

Si ejecutas directamente desde **CMD** o **PowerShell** de Windows sin `make`:
* **Probar consola Python:**
  ```cmd
  python Taller2_AB_PO_XX.py
  ```
* **Correr pruebas de Python:**
  ```cmd
  python src/python/test_tda.py
  ```
* **Compilar y correr C++ (con MinGW):**
  ```cmd
  g++ -std=c++17 -Wall -Wextra -Isrc/cpp/include src/cpp/main.cpp -o pea_cpp.exe -lsqlite3
  pea_cpp.exe
  ```

> 💡 **Nota sobre Windows y Caracteres Especiales:** El código ya incluye la instrucción automática `chcp 65001` y el manejo de códigos de tecla extendidos de Windows (`msvcrt` y `conio.h`), de modo que tildes, símbolos y flechas funcionarán de inmediato sin romper la consola.

---

## 🔗 5. Enlaces Oficiales del Taller (PDF del Docente) y Recursos de Desarrollo

Para facilitar el desarrollo de la ingesta y la GUI, aquí están los enlaces y referencias exactas extraídas del taller del profesor:

### 🌐 Enlaces Oficiales de Prueba (MinCiencias SCIENTI)
* **Portal SCIENTI de MinCiencias:**  
  [https://minciencias.gov.co/scienti](https://minciencias.gov.co/scienti)
* **URL GrupLAC de prueba obligatoria (Grupo GIDSE UPC):**  
  [https://scienti.minciencias.gov.co/gruplac/jsp/visualiza/visualizagr.jsp?nro=00000000002099](https://scienti.minciencias.gov.co/gruplac/jsp/visualiza/visualizagr.jsp?nro=00000000002099)
* **URL CvLAC de prueba obligatoria (Perfil docente Adith Pérez):**  
  [https://scienti.minciencias.gov.co/cvlac/visualizador/generarCurriculoCv.do?cod_rh=0000494917](https://scienti.minciencias.gov.co/cvlac/visualizador/generarCurriculoCv.do?cod_rh=0000494917)
* **Ejemplo oficial de referencia para el Dashboard (Uniminuto):**  
  [https://sistemainvestigacion.uniminuto.edu/PGrupos/Ver/141](https://sistemainvestigacion.uniminuto.edu/PGrupos/Ver/141)

### 📦 Librerías de Python Utilizadas
Todas están especificadas en `requirements.txt`:
* `requests`: Para descargas HTTP de las páginas de GrupLAC y CvLAC.
* `beautifulsoup4`: Para parsear el HTML y extraer tablas y textos del scraping.
* `pypdf`: Para leer y procesar texto de archivos PDF de investigación.
* `matplotlib`: Para generar gráficos de barras, histogramas y visualizaciones estadísticas.
* Librerías nativas estándar utilizadas: `sqlite3`, `tkinter`, `csv`, `os`, `sys`, `json`.

### 🎨 Identidad Institucional de la UPC (Para el Dashboard y Documentos)
* **Color Verde Institucional:** `#006837`
* **Color Rojo Institucional:** `#ED1C24`
* **Color Blanco / Fondo:** `#FFFFFF` y `#F4F6F9`
* **Tipografías recomendadas:** `Segoe UI`, `Arial`, `Helvetica`

---

## 🌿 6. Flujo de Trabajo en Git (Guía Paso a Paso para Persona B)

Para mantener el repositorio impecable y profesional:

1. **Descargar ramas remotas actualizadas:**
   ```bash
   git fetch origin
   ```
2. **Cambiarse a la rama asignada (ejemplo para Ingesta):**
   ```bash
   git checkout feature/ingesta-datos
   ```
3. **Programar y hacer commits pequeños y claros:**
   ```bash
   git add src/python/core/ingesta.py
   git commit -m "feat(ingesta): implementar parser HTML con BeautifulSoup para GrupLAC"
   ```
4. **Subir los cambios a GitHub:**
   ```bash
   git push origin feature/ingesta-datos
   ```
5. **Crear Pull Request en GitHub:**
   * Entra a [github.com/Kovyn-Mena/PEA-I](https://github.com/Kovyn-Mena/PEA-I).
   * Crea un **Pull Request (PR)** desde `feature/ingesta-datos` **hacia la rama `dev`** (nunca directo a `main`).
   * Persona A revisará el PR, validará que las pruebas pasen y hará el Merge a `dev`.

---

## 🛡️ 7. Reglas de Oro para Todo el Equipo

1. **No tocar `data/schema.sql`:** La base de datos es el contrato común. Si se cambia un nombre de columna, se rompería C++ o Python.
2. **No usar estructuras nativas para almacenar el hipercubo:** La información en RAM **siempre** debe residir en los nodos de la `Multilista`.
3. **La consola nunca debe dejar de funcionar:** Cualquier nueva funcionalidad gráfica o de ingesta debe integrarse como un módulo modular complementario sin alterar la autonomía de la consola.
4. **Validar antes de hacer commit:** Correr siempre `make test` (o `python src/python/test_tda.py`) antes de subir cambios.
