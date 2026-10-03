@echo off
set PATH=C:\msys64\ucrt64\bin;%PATH%
echo [1/2] Inicializando Base de Datos SQLite...
C:\msys64\ucrt64\bin\python.exe data\init_db.py
echo [2/2] Compilando Taller2_KM_PO_XX.cpp...
C:\msys64\ucrt64\bin\g++.exe -std=c++17 -Wall -Wextra -g Taller2_KM_PO_XX.cpp -o pea_cpp.exe -I C:\msys64\ucrt64\include -L C:\msys64\ucrt64\lib -lsqlite3 -static-libgcc -static-libstdc++
if errorlevel 1 (
    echo [ERROR] Fallo la compilacion.
    pause
    exit /b 1
)
echo [EXITO] Compilacion correcta. Ejecutando pea_cpp.exe...
pea_cpp.exe
