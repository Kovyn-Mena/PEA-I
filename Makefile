# Makefile del proyecto PEA-i (Universidad Popular del Cesar)
CXX = C:/msys64/ucrt64/bin/g++.exe
PYTHON = C:/msys64/ucrt64/bin/python.exe
CXXFLAGS = -std=c++17 -Wall -Wextra -g
LIBS = -lsqlite3

all: init-db build-cpp

init-db:
	$(PYTHON) data/init_db.py

build-cpp:
	$(CXX) $(CXXFLAGS) -IC:/msys64/ucrt64/include Taller2_KM_PO_XX.cpp -o pea_cpp.exe -LC:/msys64/ucrt64/lib $(LIBS) -static-libgcc -static-libstdc++

run-cpp: build-cpp
	./pea_cpp.exe

run-py:
	$(PYTHON) Taller2_KM_PO_XX.py

gui-py:
	$(PYTHON) Taller2_KM_PO_XX.py --gui

test:
	$(PYTHON) data/init_db.py
	$(CXX) $(CXXFLAGS) -IC:/msys64/ucrt64/include Taller2_KM_PO_XX.cpp -o pea_cpp.exe -LC:/msys64/ucrt64/lib $(LIBS)

clean:
	rm -f pea_cpp.exe *.o
