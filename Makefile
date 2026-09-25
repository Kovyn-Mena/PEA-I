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

# Ejecutar el programa en consola
run: $(TARGET)
	./$(TARGET)

# Ejecutar la suite completa de pruebas unitarias (C++ y Python)
test:
	@echo "--- Ejecutando pruebas unitarias C++ ---"
	$(CXX) $(CXXFLAGS) src/cpp/test_tda.cpp -o src/cpp/test_tda
	./src/cpp/test_tda
	@echo "\n--- Ejecutando pruebas unitarias Python ---"
	python3 src/python/test_tda.py

# Limpiar ejecutables y temporales
clean:
	rm -f $(TARGET) src/cpp/test_tda src/cpp/test_sqlite
	@echo "[OK] Archivos temporales eliminados."

.PHONY: all run test clean
