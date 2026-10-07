# Directivas y Reglas del Proyecto (PEA-i / Taller 2 Estructuras de Datos)

## 🧠 Sincronización Obligatoria con Obsidian
1. **Bóveda Oficial:** La documentación viva del proyecto reside en `documentacion-obsidian/PEA-I/`.
2. **Consultar antes de actuar:** Leer las notas relevantes de la bóveda antes de proponer cambios estructurales o refactors en C++ / Python.
3. **Registro Continuo de Bitácora:**
   - Cada sesión de desarrollo, corrección de errores, refactor o feature debe quedar registrada en `documentacion-obsidian/PEA-I/060 - Bitácora de Cambios y Registro de Errores Lógicos.md`.
   - Especificar archivos tocados, causa raíz de bugs y verificación de compilación / pruebas.
4. **Mantenimiento del Hub e Interconexión:**
   - Si se añade un concepto, módulo o requerimiento nuevo, crear su nota `NNN - Nombre.md` y enlazarla en `000 - PEA-i Hub Principal.md`.
   - Utilizar sintaxis Markdown de Obsidian: enlaces `[[Nota]]`, etiquetas `#tag` y diagramas `mermaid`.
5. **Estándares de Código:**
   - C++: C++17, monolito único `Taller2_*.cpp`, `-Wall -Wextra`, cero warnings, manejo estricto de memoria para TDAs (Pila LIFO, Cola FIFO, Multilistas Ortogonales 3D) y persistencia SQLite.
   - Python: Ingesta/Scraping modular `Taller2_*.py`, compatibilidad UTF-8, scripts de inicialización y soporte CLI.
