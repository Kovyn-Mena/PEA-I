# 📋 Auditoría y Feedback Técnico — Proyecto PEA-i (Taller 2)

---

## 1. Apreciación Inicial del Trabajo Realizado

Primero que todo, **felicitaciones por el trabajo de ingeniería inversa y scraping que hiciste en la rama de ingesta**:
* La extracción de la **Hoja de Vida de CvLAC** (par evaluador, Google Scholar, ORCID, formación y experiencia) en la tabla `perfil_investigador` está excelente.
* La detección del **aval institucional con `chulo_1.jpg`** para marcar productos como `Validado` resuelve de forma muy inteligente un vacío de datos.
* El mapeo del **código institucional 947 de la UPC con los 66 grupos** y el sistema de caché en archivos ZIP para no saturar MinCiencias demuestran un nivel técnico muy alto.
* La bitácora en Obsidian (`060 - Bitácora de Cambios`) es sumamente rigurosa y ordenada.

Sin embargo, al contrastar el estado actual del repositorio con la **Guía del Taller 2 y la Rúbrica Oficial del profesor Adith Pérez**, existen **varios puntos críticos faltantes** que nos pueden costar la nota máxima (5.0) si no los completamos antes de la entrega final y el video explicativo.

A continuación te detallo **qué falta exactamente, por qué es obligatorio y cómo resolverlo**:

---

## 2. Matriz de Cumplimiento Frente a la Rúbrica Oficial

| # | Requisito del Taller (Guía Oficial) | Estado en tu repo | Impacto / Riesgo |
|:--:|---|:---:|---|
| **1-4** | Gestión de Grupos, Investigadores, Productos y Detalles | ✅ **Completado** | Excelente en C++. |
| **5** | Documento "Modelo" MinCiencias 2024 e IPP | ❌ **No Implementado** | **Alto**. Declarado como "documento faltante". El profesor evaluará el cálculo de pesos e IPP. |
| **6-7** | Variables E/S, Web Scraping y persistencia SQLite | ✅ **Completado** | Sólido y verificado. |
| **8** | Solución en Estructuras Puras de Datos (TDAs) | 🟡 **Parcial (Solo C++)** | **Crítico**. No existen clases TDA en Python. |
| **9-11** | CRUD, Filtros por año (2/5 años) y Edición | ✅ **Completado** | Operativo en la consola C++. |
| **12.a** | Salidas tabulares por consola | ✅ **Completado** | Tablas formateadas con bordes ASCII. |
| **12.b** | Dashboard Analítico Gráfico (Estilo UNIMINUTO) | ❌ **0% Implementado** | **Crítico**. La bandera `--gui` no abre interfaz gráfica. |
| **12.c** | Vistas específicas por entidad (Grupos, Investigadores, Productos) | ❌ **0% Implementado** | Falta la capa visual de tablas interactivas. |
| **13-14** | Suite de Pruebas Automatizadas y Documentación Formal | ❌ **Incompleto** | Falta suite de asserts y el `.docx` oficial. |

---

## 🔍 3. Detalle de lo que Falta y Por Qué es Obligatorio

### 🚨 1. Solución de Estructuras Puras (TDA) en Python (Punto 8 y 13)
* **Lo que pasa actualmente:**  
  Tu archivo `Taller2_KM_PO_XX.py` es un script procedural de scraping y carga a SQLite (1,725 líneas). **No contiene ninguna clase de estructura de datos**. No hay clase `Multilista`, ni `Pila`, ni `Cola`, ni `NodoProducto`, ni `NodoInvestigador`, ni consola interactiva en Python.
* **Por qué el profesor lo va a exigir:**  
  La guía del taller y el examen parcial exigen **dos implementaciones coordinadas pero autónomas**: una en C++ y otra en Python. Si el docente ejecuta Python y ve que solo es un scraper sin menús ni estructuras enlazadas en RAM, la nota de la parte de Python se cae a 0.
* **Solución requerida:**  
  Python debe tener su propio paquete de estructuras puras (`Nodo`, `Multilista` con punteros ortogonales, `Pila` para Undo y `Cola` para ingesta) y una consola interactiva análoga a la de C++.

---

### 🚨 2. Interfaz Gráfica / Dashboard Analítico (Puntos 12.b, 12.c y 14.c)
* **Lo que pasa actualmente:**  
  En `Taller2_KM_PO_XX.py` la bandera `--gui` dice literalmente:
  ```python
  # Modos: (1) consola (pendiente Fase 2) | (2) --gui (pendiente Fase 5)
  ```
  Si se ejecuta `python3 Taller2_KM_PO_XX.py --gui`, solo imprime el texto de ayuda por consola. No se abre ninguna ventana ni gráfico.
* **Por qué el profesor lo va a exigir:**  
  El Punto 12 del taller dice textualmente:
  > *"Diseñe una interfaz amigable (Dashboard)... donde se presenten gráficos (histogramas, barras) para el balance de investigación institucional... y vistas por entidad."*  
  Sin GUI, la calificación máxima según la rúbrica queda topada en **4.0**, impidiendo el 5.0.
* **Solución requerida:**  
  Se requiere un Dashboard visual operativo. Puede ser mediante Tkinter/Matplotlib o un Portal Ejecutivo HTML5/CSS moderno que se abra automáticamente en el navegador con `./pea_cpp --gui`.

---

### 3. El Modelo MinCiencias 2024 y el Cálculo de IPP (Punto 5)
* **Lo que pasa actualmente:**  
  En el archivo `MODELO_FALTANTE_Punto5.md` escribiste:
  > *"El enunciado remite a 'el siguiente documento: Modelo', pero dicho documento no fue suministrado... Para no bloquear los puntos 1–4 y 6, se adopta el modelo estándar SCIENTI GrupLAC/CvLAC".*
* **Por qué esto es un error frente al profesor Adith:**  
  El profesor no se refería a un archivo adjunto que olvidó subir; se refería al **"Modelo de Medición de Grupos de Investigación e Investigadores de MinCiencias vigente (Convocatoria 957 / Anexo 1)"**.  
  Este modelo define las **5 Macro-Familias oficiales**:
  1. **GNC:** Generación de Nuevo Conocimiento (Artículos A1-C, Libros, Patentes).
  2. **DTI:** Desarrollo Tecnológico e Innovación (Software DNDA, Prototipos).
  3. **ASC:** Apropiación Social del Conocimiento.
  4. **DPC:** Divulgación Pública de la Ciencia.
  5. **FRH:** Formación de Recurso Humano (Tesis de maestría, doctorado, asesorías Ondas).  
  Y exige el cálculo del **IPP (Índice de Producción Ponderada)**, asignando puntajes relativos (ej. 100 pts a Patentes y Artículos A1, 90 pts a Software, 70 pts a Tesis de Maestría).
* **Solución requerida:**  
  Eliminar el documento de "modelo faltante" e incorporar la resolución de categorías del Modelo 2024 y el cálculo del balance de puntos IPP por grupo.

---

###4. Portabilidad del `Makefile` (Rutas C:/msys64 Hardcodeadas)
* **Lo que pasa actualmente:**  
  En el `Makefile` tienes escrito:
  ```makefile
  CXX = C:/msys64/ucrt64/bin/g++.exe
  PYTHON = C:/msys64/ucrt64/bin/python.exe
  ```
* **Por qué es un problema grave:**  
  Esas son rutas absolutas de tu disco duro local en Windows con MSYS2. Si el profesor (o cualquier compañero en Linux o Mac) clona el repositorio y escribe `make`, la terminal arroja:
  ```text
  make: C:/msys64/ucrt64/bin/g++.exe: No such file or directory
  ```
* **Solución requerida:**  
  Usar variables estándar multiplataforma:
  ```makefile
  CXX ?= g++
  PYTHON ?= python3
  ```
  Permitiendo que funcione en Linux, macOS o Windows sin modificar el archivo.

---

###  5. Suite de Pruebas Unitarias Automatizadas de TDAs (Punto 13)
* **Lo que pasa actualmente:**  
  En tu `Makefile`, la regla `make test` solo hace esto:
  ```makefile
  test:
      $(PYTHON) data/init_db.py
      $(CXX) $(CXXFLAGS) Taller2_KM_PO_XX.cpp ...
  ```
  Es decir, solo re-inicializa la base de datos y recompila. No corre ningún test unitario real.
* **Por qué el profesor lo va a exigir:**  
  El docente evaluará si los punteros de la Multilista ortogonal, el comportamiento LIFO de la Pila y el FIFO de la Cola están blindados. Se debe demostrar con `assert` que al insertar, eliminar o desactivar nodos, los conteos y punteros de memoria no quedan huérfanos.
* **Solución requerida:**  
  Crear suites de pruebas unitarias automatizadas (`test_tda.cpp` y `test_tda.py`) que ejecuten pruebas de estrés sobre los TDAs puros y verifiquen $O(1)$ en operaciones críticas.

---

###  6. Informes Oficiales en PDF y Documento Word (`.docx`)
* **Lo que pasa actualmente:**  
  * Solo cuentas con `data/muestra_upc.pdf` (un PDF de entrada con dos filas de ejemplo generado con fpdf2).
  * No hay generador de informes ejecutivos institucionales en PDF para los grupos.
  * Tienes las notas en Obsidian, pero no está generado el archivo formal `Documentacion_Tecnica_GrupoXX.docx` que pide el docente con diagramas de casos de uso y arquitectura.
* **Por qué es obligatorio:**  
  El taller pide la generación de reportes formales de producción y la entrega de la especificación técnica en formato Word editable junto al código fuente.

---

### 📦 7. Estructura y Modularidad (Monolito vs. Módulos)
* **Lo que pasa actualmente:**  
  * `Taller2_KM_PO_XX.cpp` tiene **2,639 líneas** en un solo archivo.
  * `Taller2_KM_PO_XX.py` tiene **1,725 líneas** en un solo archivo.
  * El directorio `pylib/` contiene carpetas completas de pip (`requests`, `beautifulsoup4`, etc.) committeadas en Git.
* **Riesgo para el video explicativo:**  
  En el video explicativo de 8–10 minutos que debemos grabar para el profesor, abrir un archivo de 2,600 líneas hace muy difícil explicar los nodos con claridad. Es mucho más pedagógico y académico tener los TDAs separados en cabeceras limpias (`Nodo.h`, `Multilista.h`, `Pila.h`, `Cola.h`), donde cada archivo tiene entre 80 y 150 líneas bien comentadas.

---

## 🚀 4. Propuesta de Solución y Coordinación

Para que el grupo asegure el **5.0 / 5.0** sin retrabajar ni desgastarnos:

1. **Unificar lo mejor de ambos lados:**
   - De tu desarrollo: podemos mantener tu lógica de **extracción de la hoja de vida CvLAC** (par evaluador, Scholar, ORCID) y la detección de `chulo_1.jpg`.
   - De la solución completa que ya tengo estructurada y probada: podemos tomar **la solución completa de TDAs en Python**, **el Portal Ejecutivo / Dashboard gráfico**, **el Catálogo y cálculo del Modelo MinCiencias 2024**, **la suite de testing automatizada (`make test`)** y **el generador de informes PDF oficiales**.

2. **Empaquetado Limpio:**
   - Asegurarnos de que el ZIP final pese ~2.5 MB, compile con un simple `make` en cualquier sistema operativo y contenga el documento técnico Word (`.docx`) listo para radicar.
