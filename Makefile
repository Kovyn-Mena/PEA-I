# =====================================================================
# Makefile — PEA-i (Programa Estadístico de Análisis de Investigación)
# Universidad Popular del Cesar — Estructura de Datos
# =====================================================================

ifeq ($(OS),Windows_NT)
    TARGET = pea_cpp.exe
    PYTHON = python
    CXX = g++
    CC = gcc
    CXXFLAGS = -std=c++17 -Wall -Wextra -Isrc/cpp/include
    # Usa sqlite3 amalgamado si existe (compilado como C puro, luego linkeado)
    ifneq ($(wildcard src/cpp/sqlite3.c),)
        SQLITE_OBJ = src/cpp/sqlite3_amalg.o
        LDFLAGS = -static-libgcc -static-libstdc++
    else
        SQLITE_OBJ =
        LDFLAGS = -lsqlite3 -static-libgcc -static-libstdc++
    endif
    ifneq ($(wildcard C:/msys64/ucrt64/bin/g++.exe),)
        CXX = C:/msys64/ucrt64/bin/g++.exe
        CC = C:/msys64/ucrt64/bin/gcc.exe
        CXXFLAGS += -IC:/msys64/ucrt64/include
        LDFLAGS += -LC:/msys64/ucrt64/lib
    endif
else
    TARGET = pea_cpp
    PYTHON = python3
    CXX = g++
    CC = gcc
    CXXFLAGS = -std=c++17 -Wall -Wextra -Isrc/cpp/include
    # En Linux usar sqlite3 del sistema (más simple y ya instalado)
    SQLITE_OBJ =
    LDFLAGS = -lsqlite3
endif

SRC = src/cpp/main.cpp

# Regla por defecto: compilar el binario principal
all: $(TARGET)

$(TARGET): $(SRC) $(wildcard src/cpp/include/*.h) $(SQLITE_OBJ)
	@echo "[C++] Compilando $(TARGET)..."
	$(CXX) $(CXXFLAGS) $(SRC) $(SQLITE_OBJ) -o $(TARGET) $(LDFLAGS)
	@echo "[OK] Compilación exitosa: ./$(TARGET)"

# Compilar sqlite3.c como C puro (necesario para el amalgamado — void* no es C++)
src/cpp/sqlite3_amalg.o: src/cpp/sqlite3.c
	@echo "[C]   Compilando sqlite3 amalgamado como C..."
	$(CC) -O2 -c src/cpp/sqlite3.c -o src/cpp/sqlite3_amalg.o

# Ejecutar el programa en consola C++
run: run-cpp

run-cpp: $(TARGET)
	./$(TARGET)

# Ejecutar el programa en consola Python
run-py:
	$(PYTHON) Taller2_AB_PO_XX.py

# Ejecutar el modo visualizador gráfico (C++ GUI)
gui: $(TARGET)
	./$(TARGET) --gui

run-gui: gui

# Ejecutar el dashboard gráfico (Python GUI - HTML5 & 3 Vistas)
gui-py:
	$(PYTHON) Taller2_AB_PO_XX.py --gui

run-gui-py: gui-py

# Ejecutar la suite completa de pruebas unitarias (C++ y Python)
test:
	@echo "--- Ejecutando pruebas unitarias C++ ---"
	$(CXX) $(CXXFLAGS) src/cpp/test_tda.cpp -o src/cpp/test_tda
	./src/cpp/test_tda
	@echo "\n--- Ejecutando pruebas unitarias Python ---"
	$(PYTHON) src/python/test_tda.py

# Generar diagramas y documento Word formal de especificación técnica
docs:
	$(PYTHON) docs/generate_diagrams.py
	$(PYTHON) docs/generate_word_doc.py
	@echo "[OK] Documentación y diagramas generados exitosamente."

# Ejecutar auditoría complementaria en Rust (Punto 14.f)
audit-rust:
	@if command -v cargo >/dev/null 2>&1; then \
		cargo run --manifest-path src/rust/Cargo.toml; \
	else \
		echo "[INFO] Compilador Rust (cargo) no detectado en el PATH."; \
		echo "[INFO] Los archivos fuente se encuentran en src/rust/ para revisión y compilación con 'cargo run'."; \
	fi

# Limpiar ejecutables y temporales
clean:
	rm -f $(TARGET) pea_cpp pea_cpp.exe src/cpp/test_tda src/cpp/test_tda.exe src/cpp/test_sqlite Taller2_EstructuraDatos_GrupoXX.zip
	rm -f dist/dashboard_python.html
	find . -name "__pycache__" -type d -not -path "./.git/*" -exec rm -rf {} + 2>/dev/null; true
	@echo "[OK] Archivos temporales eliminados."

# Ejecutar verificación cruzada de equivalencia C++17 vs Python
verify: $(TARGET)
	$(PYTHON) Taller2_AB_PO_XX.py --verify

# Empaquetar entrega final en archivo ZIP para envío al docente (adithperez@unicesar.edu.co)
package: clean docs
	@$(PYTHON) scripts/package_zip.py

.PHONY: all run run-cpp run-py gui run-gui gui-py run-gui-py test verify docs audit-rust clean package


