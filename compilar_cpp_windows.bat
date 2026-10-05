@echo off
chcp 65001 >nul
title PEA-i — Compilador y Ejecutor C++ (Windows)
echo ===============================================================================
echo   PEA-i: Compilacion y Ejecucion en C++17 (Windows)
echo   Universidad Popular del Cesar — Estructura de Datos
echo ===============================================================================
echo.

set "CXX_BIN="
set "CXX_INC="
set "CXX_LIB="

if exist "pea_cpp.exe" (
    echo [i] Se encontro un binario pea_cpp.exe previamente compilado.
    echo.
    echo   [1] Ejecutar directamente pea_cpp.exe
    echo   [2] Recompilar desde el codigo fuente C++
    echo.
    set /p RECOMP="Seleccione una opcion [1-2, Enter=1]: "
    if "%RECOMP%"=="2" goto BUSCAR_COMPILADOR
    goto EJECUTAR_BINARIO
)

:BUSCAR_COMPILADOR
echo [1/3] Detectando compilador C++ (g++) en su sistema Windows...

:: 1. Probar MSYS2 UCRT64 (Configuracion estandar UPC / Damian)
if exist "C:\msys64\ucrt64\bin\g++.exe" (
    set "CXX_BIN=C:\msys64\ucrt64\bin\g++.exe"
    set "CXX_INC=-IC:/msys64/ucrt64/include"
    set "CXX_LIB=-LC:/msys64/ucrt64/lib"
    echo [OK] Se detecto MSYS2 UCRT64 en C:\msys64\ucrt64.
    goto COMPILAR
)

:: 2. Probar MSYS2 MINGW64
if exist "C:\msys64\mingw64\bin\g++.exe" (
    set "CXX_BIN=C:\msys64\mingw64\bin\g++.exe"
    set "CXX_INC=-IC:/msys64/mingw64/include"
    set "CXX_LIB=-LC:/msys64/mingw64/lib"
    echo [OK] Se detecto MSYS2 MINGW64 en C:\msys64\mingw64.
    goto COMPILAR
)

:: 3. Probar g++ en PATH
where g++ >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "CXX_BIN=g++"
    echo [OK] Se detecto g++ en el PATH del sistema.
    goto COMPILAR
)

:: 4. Probar Code::Blocks
if exist "C:\Program Files\CodeBlocks\MinGW\bin\g++.exe" (
    set "CXX_BIN=C:\Program Files\CodeBlocks\MinGW\bin\g++.exe"
    echo [OK] Se detecto MinGW de Code::Blocks (64-bit).
    goto COMPILAR
)
if exist "C:\Program Files (x86)\CodeBlocks\MinGW\bin\g++.exe" (
    set "CXX_BIN=C:\Program Files (x86)\CodeBlocks\MinGW\bin\g++.exe"
    echo [OK] Se detecto MinGW de Code::Blocks (32-bit).
    goto COMPILAR
)

:: 5. Probar Dev-C++
if exist "C:\Program Files (x86)\Dev-Cpp\MinGW64\bin\g++.exe" (
    set "CXX_BIN=C:\Program Files (x86)\Dev-Cpp\MinGW64\bin\g++.exe"
    echo [OK] Se detecto MinGW64 de Dev-C++.
    goto COMPILAR
)

:: 6. Probar MinGW estandar
if exist "C:\MinGW\bin\g++.exe" (
    set "CXX_BIN=C:\MinGW\bin\g++.exe"
    echo [OK] Se detecto MinGW en C:\MinGW.
    goto COMPILAR
)

echo.
echo [!] AVISO: No se detecto ningun compilador g++ instalado en las rutas estandar.
echo.
echo PEA-i cuenta con una version autonoma en Python que ejecuta
echo exactamente las mismas estructuras de datos (Multilista 3D, Pila Undo, Cola)
echo y accede a los 3,351 productos de investigacion sin compilar nada.
echo.
echo Desea iniciar la aplicacion ahora mismo usando Python? [S/N]
set /p USAR_PY="> "
if /i "%USAR_PY%"=="S" (
    call ejecutar_windows.bat
    exit /b 0
)
pause
exit /b 1

:COMPILAR
echo [2/3] Compilando pea_cpp.exe con soporte C++17 y SQLite3...
"%CXX_BIN%" -std=c++17 -Wall -Wextra -Isrc/cpp/include %CXX_INC% src/cpp/main.cpp -o pea_cpp.exe %CXX_LIB% -lsqlite3 -static-libgcc -static-libstdc++

if %ERRORLEVEL% neq 0 (
    echo.
    echo [!] ERROR: La compilacion de C++ fallo.
    echo     Causa comun: Falta la libreria SQLite3 en su compilador MinGW.
    echo.
    echo Desea abrir la version de Python que funciona de inmediato sin compilar? [S/N]
    set /p USAR_PY="> "
    if /i "%USAR_PY%"=="S" (
        call ejecutar_windows.bat
        exit /b 0
    )
    pause
    exit /b 1
)

echo [OK] Compilacion exitosa: pea_cpp.exe generado correctamente.
echo.

:EJECUTAR_BINARIO
echo [3/3] Iniciando Consola C++ PEA-i (UPC)...
echo ===============================================================================
echo.
pea_cpp.exe
if %ERRORLEVEL% neq 0 (
    echo.
    echo [i] La aplicacion C++ finalizo con codigo %ERRORLEVEL%.
    pause
)
