# =====================================================================
# Makefile — PEA-i (Programa Estadístico de Análisis de Investigación)
# Universidad Popular del Cesar — Estructura de Datos
# =====================================================================

CXX = g++
CXXFLAGS = -std=c++17 -Wall -Wextra -Isrc/cpp/include
LDFLAGS = -lsqlite3

TARGET = pea_cpp
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
	python3 Taller2_AB_PO_XX.py

# Ejecutar el modo visualizador gráfico (C++ GUI)
gui: $(TARGET)
	./$(TARGET) --gui

run-gui: gui

# Ejecutar el dashboard gráfico (Python GUI - Matplotlib & 3 Vistas)
gui-py:
	python3 Taller2_AB_PO_XX.py --gui

run-gui-py: gui-py

# Ejecutar la suite completa de pruebas unitarias (C++ y Python)
test:
	@echo "--- Ejecutando pruebas unitarias C++ ---"
	$(CXX) $(CXXFLAGS) src/cpp/test_tda.cpp -o src/cpp/test_tda
	./src/cpp/test_tda
	@echo "\n--- Ejecutando pruebas unitarias Python ---"
	python3 src/python/test_tda.py

# Generar diagramas y documento Word formal de especificación técnica
docs:
	python3 docs/generate_diagrams.py
	python3 docs/generate_word_doc.py
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
	rm -f $(TARGET) src/cpp/test_tda src/cpp/test_sqlite
	@echo "[OK] Archivos temporales eliminados."

.PHONY: all run run-cpp run-py gui run-gui gui-py run-gui-py test docs audit-rust clean
