# 🎬 Guía Definitiva y Guion para el Video Explicativo — Sistema PEA-i
**Universidad Popular del Cesar (UPC) — Facultad de Ingeniería y Tecnológicas**  
**Asignatura:** Estructura de Datos (2026-I) | **Docente:** Ing. Adith Bismarck Pérez Orozco  
**Estudiante:** Kovyn B. Mena (`kbmena@unicesar.edu.co`) | **Objetivo:** Calificación 5.0 / 5.0  

---

## 💡 Consejo de Oro Inicial (Mentalidad para el Video)
No te preocupes por haber utilizado herramientas de Inteligencia Artificial para construir el proyecto. Lo que el profesor evalúa en el video **no es si escribiste cada línea a mano en un bloc de notas**, sino que **comprendas y domines la teoría de Estructuras de Datos**:
1. ¿Qué es un nodo y qué punteros tiene?
2. ¿Por qué es un Hipercubo ortogonal y no una lista plana?
3. ¿Cómo funciona la Pila (LIFO) para el Undo?
4. ¿Cómo funciona la Cola (FIFO) para la Ingesta?
5. ¿Cuál es la diferencia entre memoria RAM y persistencia SQLite?

Si explicas esos 5 puntos con seguridad siguiendo este guion, tu nota será un **5.0 rotundo**.

---

## ⏱️ Estructura del Video (8 a 10 Minutos Recomendados)

```
00:00 - 01:15  |  1. Presentación e Introducción del Proyecto
01:15 - 03:30  |  2. El Corazón Teórico: Nodos y Multilista Ortogonal (Código)
03:30 - 05:00  |  3. Estructuras Auxiliares: TDA Pila (Undo) y TDA Cola (Ingesta)
05:00 - 07:00  |  4. Demostración en Vivo en Consola C++ (CRUD, Filtros, Undo)
07:00 - 08:30  |  5. Demostración del Portal Ejecutivo Web & Reportes PDF
08:30 - 09:30  |  6. Pruebas Unitarias (Testing Automatizado) y Conclusión
```

---

## 📜 Guion Paso a Paso (Palabra por Palabra)

### Minuto 0:00 – 01:15 | Introducción y Contexto del Problema
*(Pantalla: Terminal limpia con el comando listo o carátula de la presentación).*

> *"Cordial saludo, profesor Adith Pérez y compañeros. Mi nombre es Kovyn Mena, estudiante de Ingeniería de Sistemas de la Universidad Popular del Cesar. En este video presento la solución integral al Taller 2 de Estructura de Datos: el sistema PEA-i (Programa Estadístico de Análisis de Investigación).*
> 
> *El objetivo principal del sistema es auditar, catalogar y evaluar la producción científica institucional siguiendo los lineamientos oficiales de MinCiencias (GrupLAC y CvLAC) y la taxonomía del nuevo Modelo 2024.*
> 
> *Para resolver el problema con máxima eficiencia computacional, implementamos una solución basada en 'Consola Primero' en C++17 puro y Python, utilizando un Hipercubo de Información tridimensional modelado mediante una Multilista Ortogonal en memoria RAM, respaldada por un TDA Pila para la función Deshacer, un TDA Cola para la ingesta ordenada de datos, y persistencia relacional en SQLite."*

---

### Minuto 01:15 – 03:30 | El Corazón Teórico: La Multilista Ortogonal
*(Pantalla: Abre en VS Code el archivo `src/cpp/include/Nodo.h` y luego `Multilista.h`).*

> *"Pasemos a revisar las estructuras de datos fundamentales.*
> 
> *El enunciado del taller nos plantea un Hipercubo de información. En memoria RAM, esto se traduce conceptualmente en tres dimensiones:*
> - *Eje X: Los Grupos de Investigación.*
> - *Eje Y: Los Investigadores adscritos a cada grupo.*
> - *Eje Z: Los Productos científicos generados.*
> 
> *(Señala en `Nodo.h` las líneas 14 a 36):*
> *Aquí en `Nodo.h` podemos observar la definición pura de los nodos:*
> 1. *`NodoGrupo`: Contiene los datos del grupo (código, nombre, líder, clasificación) y dos punteros clave: `sigGrupo` para avanzar al siguiente grupo en el Eje X, y `primerInvestigador` para descender al Eje Y.*
> 2. *`NodoInvestigador`: Contiene la información del docente o investigador (cédula, nombre, categoría MinCiencias) y dos punteros: `sigInvestigador` y `primerProducto` para conectar con el Eje Z.*
> 3. *Y el punto más importante de la ortogonalidad está en `NodoProducto`: cada producto científico tiene DOS punteros siguientes simultáneos:*
>    - *`sigProductoGrupo`: Para recorrer todos los productos de un grupo.*
>    - *`sigProductoInvestigador`: Para recorrer solo los productos de ese autor específico.*
> 
> *Esto es lo que convierte a la estructura en una **Multilista Ortogonal**: una sola instancia física del producto en memoria RAM pertenece al mismo tiempo a la sublista del grupo y a la sublista del investigador, sin duplicar memoria y permitiendo navegaciones cruzadas en tiempo $O(1)$ de salto de puntero.*
> 
> *(Abre `src/cpp/include/Multilista.h` y muestra `insertarProducto`):*
> *En `Multilista.h`, método `insertarProducto`, vemos exactamente cómo se realiza el doble enlace ortogonal conectando `nuevo->sigProductoGrupo` y `nuevo->sigProductoInvestigador`."*

---

### Minuto 03:30 – 05:00 | Estructuras Auxiliares: Pila y Cola
*(Pantalla: Abre `src/cpp/include/Pila.h` y `src/cpp/include/Cola.h`).*

> *"Para complementar el sistema, diseñamos dos estructuras de datos lineales puras desde cero, sin utilizar las librerías estándar `std::stack` ni `std::queue`:*
> 
> 1. *TDA Pila (Stack LIFO - `src/cpp/include/Pila.h`):*
>    *Implementada con un puntero `cima`. Se utiliza para el historial de transacciones y la funcionalidad **Deshacer (Undo)**. Cada vez que creamos, modificamos o desactivamos un registro, apilamos la acción previa en tiempo $O(1)$. Cuando el usuario presiona la opción 'Deshacer', hacemos un `pop()` y revertimos el estado anterior inmediatamente.*
> 
> 2. *TDA Cola (Queue FIFO - `src/cpp/include/Cola.h`):*
>    *Implementada con punteros `primero` y `ultimo`. Se encarga de la **Ingesta de Datos**. Cuando se envían solicitudes de Web Scraping de URLs de GrupLAC o rutas de archivos PDF y CSV, se encolan para procesarse de manera estrictamente secuencial y ordenada en tiempo $O(1)$ de inserción y extracción."*

---

### Minuto 05:00 – 07:00 | Demostración en Vivo en Consola C++
*(Pantalla: Abre la terminal en pantalla completa).*

**Comando a ejecutar:**
```bash
./pea_cpp
```

> *"Vamos a ejecutar la aplicación en C++.*
> 
> *(En el menú de inicio selecciona la opción `[1]` para cargar desde SQLite):*
> *Al iniciar con la opción 1, el `GestorSQLite` lee la persistencia en disco y traslada todos los nodos a la memoria RAM. Como vemos, tenemos en RAM 62 grupos, 362 investigadores y 3,351 productos científicos reales de la Universidad Popular del Cesar.*
> 
> *(Entra a la opción `1. Gestión de Grupos` y luego `3. Consultar Detalle de un Grupo`):*
> *Aquí tenemos la consulta del Hipercubo con búsqueda inteligente. Si escribo `gisico` o presiono directamente **ENTER**, el sistema localiza el grupo:*
> - *Podemos ver al grupo GISICO (`COL0002099`), su líder el docente John Jairo Patiño Vanegas, sus investigadores adscritos como el profesor Adith Pérez, y la lista completa de productos vinculados.*
> 
> *(Regresa al menú principal con `0`, entra a `5. Resumen Estadístico y Filtro`):*
> *Aquí cumplimos el **Punto 10 del taller**: podemos filtrar la producción por ventana de observación, por ejemplo los últimos 2 años o los últimos 5 años, evaluando dinámicamente la producción vigente según las convocatorias de MinCiencias.*
> 
> *(Demuestra la Pila Undo):*
> *Ahora entremos a `1. Gestión de Grupos` -> `5. Desactivar Grupo`. Desactivemos un grupo para hacer un borrado lógico. Vemos que su estado cambia a `[INACT]`. Si regresamos al Menú Principal y presionamos la opción `4. Deshacer última acción`, la Pila extrae la operación y reactiva el grupo de forma inmediata."*

---

### Minuto 07:00 – 08:30 | Portal Ejecutivo Web & Reportes Oficiales PDF
*(Pantalla: Terminal y navegador web).*

**Comando a ejecutar:**
```bash
./pea_cpp --gui
```

> *"Ahora veamos la capa de visualización e interoperabilidad.*
> 
> *Cumpliendo con el requerimiento del Dashboard analítico (Punto 12.b), implementamos una arquitectura 'Zero-Dependencies'. Al ejecutar `./pea_cpp --gui`, C++ toma la Multilista en memoria RAM, serializa la información y genera de forma instantánea este **Portal Ejecutivo de Ciencia Abierta** en HTML5 y CSS moderno dark mode.*
> 
> *(Muestra el navegador):*
> 1. *En el panel lateral izquierdo podemos buscar cualquier grupo de la UPC o filtrarlo por categorías MinCiencias (A1, A, B, C, Reconocidos).*
> 2. *Al seleccionar un grupo (por ejemplo GISICO), vemos su ficha técnica institucional y un botón directo que dice **'📄 Descargar Informe PDF'**.*
> 3. *Si hacemos clic en él, se abre el reporte oficial en PDF que generamos con ReportLab con los colores institucionales verde y rojo de la UPC, balance del Modelo MinCiencias 2024 (calculando el Índice de Producción Ponderada IPP en las 5 macro-familias: GNC, DTI, ASC, DPC y FRH).*
> 4. *En el Dashboard general tenemos el histograma cronológico de publicaciones desde 1996 hasta 2026, la distribución de categorías y los indicadores de aval institucional."*

---

### Minuto 08:30 – 09:30 | Testing Automatizado y Conclusión
*(Pantalla: Terminal).*

**Comando a ejecutar:**
```bash
make test
```

> *"Para garantizar la confiabilidad absoluta y la rigurosidad académica, el proyecto incluye una suite de pruebas unitarias automatizadas tanto para C++ como para Python.*
> 
> *(Ejecuta `make test`):*
> *Al ejecutar `make test`, el compilador g++ corre el ejecutable de pruebas verificando la Multilista ortogonal, los conteos de nodos, la Pila LIFO y la Cola FIFO. Inmediatamente después, Python ejecuta su suite espejo para comprobar la paridad estructural.*
> 
> *Todo el proyecto está empaquetado y listo para su entrega formal mediante la regla `make package`, que genera un archivo ZIP limpio de 2.5 MB.*
> 
> *Con esto concluyo la sustentación. Muchas gracias por su atención."*

---

## 🎯 Preguntas Típicas del Docente y Cómo Responderlas

| Pregunta del Docente | Respuesta Correcta y Segura |
| :--- | :--- |
| **¿Por qué esto se llama Hipercubo si en pantalla vemos una lista?** | *"Porque el término 'Hipercubo' hace referencia a la estructura multidimensional en memoria RAM. Es un espacio tridimensional definido por Grupos ($X$), Investigadores ($Y$) y Productos ($Z$). Cada producto tiene dos punteros simultáneos (`sigProductoGrupo` y `sigProductoInvestigador`) que cruzan las dimensiones ortogonalmente."* |
| **¿Por qué usaron SQLite si la materia es Estructura de Datos y punteros?** | *"SQLite se utiliza exclusivamente como persistencia en frío (almacenamiento en disco) para no perder los datos al cerrar la consola. Pero en cuanto el programa arranca, todos los datos se cargan en nodos enlazados con punteros dinámicos (`new` / `delete`). Todas las operaciones de CRUD, búsqueda, filtros y estadísticas se ejecutan en RAM sobre la Multilista."* |
| **¿Qué ventaja tiene el borrado lógico sobre el borrado físico?** | *"El borrado lógico (`activo = false`) preserva la trazabilidad histórica de MinCiencias: el registro sigue existiendo para auditorías pero se excluye de los cálculos vigentes. El borrado físico (`delete`), en cambio, reconecta los punteros ortogonales para evitar fugas de memoria (`memory leaks`)."* |
| **¿Dónde se evidencia la interoperabilidad entre C++ y Python?** | *"En dos puntos: 1) Comparten la misma base de datos relacional SQLite con esquemas idénticos. 2) La consola en C++ utiliza tuberías de procesos (`popen` en `GestorInterop.h`) para invocar el motor de Web Scraping de Python y el generador de reportes PDF de ReportLab."* |
| **¿Qué es el IPP del Modelo 2024?** | *"Es el Índice de Producción Ponderada exigido en el Anexo 1 de la Convocatoria 957 de MinCiencias. Pondera las 5 familias (GNC, DTI, ASC, DPC, FRH) asignando pesos relativos (ej. 100 pts a patentes y artículos A1, 90 pts a software con registro DNDA, 70 pts a tesis de maestría) para evaluar el impacto real del grupo."* |
