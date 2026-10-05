# =====================================================================
# Makefile — PEA-i (Programa Estadístico de Análisis de Investigación)
# Universidad Popular del Cesar — Estructura de Datos
# =====================================================================

ifeq ($(OS),Windows_NT)
    TARGET = pea_cpp.exe
    PYTHON = python
    CXX = g++
    CXXFLAGS = -std=c++17 -Wall -Wextra -Isrc/cpp/include
    LDFLAGS = -lsqlite3
    ifneq ($(wildcard C:/msys64/ucrt64/bin/g++.exe),)
        CXX = C:/msys64/ucrt64/bin/g++.exe
        CXXFLAGS += -IC:/msys64/ucrt64/include
        LDFLAGS += -LC:/msys64/ucrt64/lib -static-libgcc -static-libstdc++
    endif
else
    TARGET = pea_cpp
    PYTHON = python3
    CXX = g++
    CXXFLAGS = -std=c++17 -Wall -Wextra -Isrc/cpp/include
    LDFLAGS = -lsqlite3
endif

SRC = src/cpp/main.cpp

# Regla por defecto: compilar el binario principal
all: $(TARGET)

$(TARGET): $(SRC) $(wildcard src/cpp/include/*.h)
	@echo "[C++] Compilando $(TARGET)..."
	$(CXX) $(CXXFLAGS) $(SRC) -o $(TARGET) $(LDFLAGS)
	@echo "[OK] Compilación exitosa: ./$(TARGET)"

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

# Ejecutar el dashboard gráfico (Python GUI - Matplotlib & 3 Vistas)
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
	rm -f $(TARGET) pea_cpp pea_cpp.exe src/cpp/test_tda src/cpp/test_sqlite Taller2_EstructuraDatos_GrupoXX.zip
	@echo "[OK] Archivos temporales eliminados."

# Empaquetar entrega final en archivo ZIP para envío al docente (adithperez@unicesar.edu.co)
package: clean docs
	@$(PYTHON) scripts/package_zip.py

.PHONY: all run run-cpp run-py gui run-gui gui-py run-gui-py test docs audit-rust clean package


