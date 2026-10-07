@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul
cd /d "%~dp0"
title PEA-i - Sistema de Analisis de Investigacion UPC (Windows)

:MENU
cls
echo ===============================================================================
echo   PEA-i: Programa Estadistico de Analisis de Investigacion (UPC)
echo   Universidad Popular del Cesar - Facultad de Ingenieria y Tecnologicas
echo   Asignatura: Estructura de Datos (Taller 2) ^| Semestre 2026-I
echo   Docente: Ing. Adith Bismarck Perez Orozco
echo   Estudiante: Kovyn B. Mena
echo ===============================================================================
echo.
echo   Seleccione una opcion de ejecucion:
echo.
echo   [1] Consola Interactiva Python (Recomendado - Abre al instante sin compilar)
echo   [2] Interfaz Grafica de Escritorio Tkinter (Python GUI --gui)
echo   [3] Portal Web Interactivo del Hipercubo y CRUD (HTML5 Offline)
echo   [4] Compilar y Ejecutar en C++17 (Autodetecta MSYS2, MinGW, Code::Blocks)
echo   [5] Ejecutar Pruebas Unitarias de Estructuras de Datos (TDAs)
echo   [6] Abrir Documentacion Tecnica Oficial Word (.docx)
echo   [0] Salir
echo.
echo ===============================================================================
set "OPC="
set /p OPC="Ingrese el numero de la opcion [0-6]: "

if "%OPC%"=="1" goto RUN_PY_CONSOLE
if "%OPC%"=="2" goto RUN_PY_GUI
if "%OPC%"=="3" goto RUN_WEB
if "%OPC%"=="4" goto RUN_CPP
if "%OPC%"=="5" goto RUN_TESTS
if "%OPC%"=="6" goto OPEN_DOCX
if "%OPC%"=="0" exit /b 0

echo [!] Opcion no valida. Intente nuevamente.
timeout /t 2 >nul
goto MENU

:: ==============================================================================
:: DETECCION REAL DE PYTHON (Evita el alias fantasma de Microsoft Store)
:: ==============================================================================
:DETECT_PYTHON
set "PYCMD="

python --version >nul 2>&1
if !ERRORLEVEL! equ 0 (
    set "PYCMD=python"
    exit /b 0
)

py -3 --version >nul 2>&1
if !ERRORLEVEL! equ 0 (
    set "PYCMD=py -3"
    exit /b 0
)

if exist "C:\msys64\ucrt64\bin\python.exe" (
    set "PYCMD=C:\msys64\ucrt64\bin\python.exe"
    exit /b 0
)
if exist "C:\msys64\mingw64\bin\python.exe" (
    set "PYCMD=C:\msys64\mingw64\bin\python.exe"
    exit /b 0
)

for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python3*") do (
    if exist "%%D\python.exe" (
        set "PYCMD=%%D\python.exe"
        exit /b 0
    )
)
for /d %%D in ("C:\Program Files\Python3*") do (
    if exist "%%D\python.exe" (
        set "PYCMD=%%D\python.exe"
        exit /b 0
    )
)

echo.
echo [!] ERROR: No se detecto una instalacion funcional de Python 3 en Windows.
echo     Instale Python 3 desde https://www.python.org/downloads/ marcando
echo     la casilla "Add python.exe to PATH", o use la opcion [3] Portal Web.
echo.
exit /b 1

:RUN_PY_CONSOLE
cls
call :DETECT_PYTHON
if !ERRORLEVEL! neq 0 (
    pause
    goto MENU
)
echo [OK] Python detectado: !PYCMD!
echo [+] Iniciando Consola Interactiva PEA-i...
echo.
if "!PYCMD!"=="py -3" (
    py -3 Taller2_AB_PO_XX.py
) else (
    "!PYCMD!" Taller2_AB_PO_XX.py
)
pause
goto MENU

:RUN_PY_GUI
cls
call :DETECT_PYTHON
if !ERRORLEVEL! neq 0 (
    pause
    goto MENU
)
echo [OK] Python detectado: !PYCMD!
echo [+] Iniciando Interfaz Grafica Nativa Tkinter (--gui)...
echo.
if "!PYCMD!"=="py -3" (
    py -3 Taller2_AB_PO_XX.py --gui
) else (
    "!PYCMD!" Taller2_AB_PO_XX.py --gui
)
pause
goto MENU

:RUN_WEB
cls
if exist "dist\visualizador_hipercubo.html" (
    echo [+] Abriendo Portal Web Interactivo del Hipercubo en su navegador...
    start "" "dist\visualizador_hipercubo.html"
    echo [OK] Portal abierto en el navegador predeterminado.
) else (
    echo [!] No se encontro dist\visualizador_hipercubo.html
)
pause
goto MENU

:RUN_CPP
cls
echo ===============================================================================
echo   PEA-i: Compilacion y Ejecucion en C++17 (Windows)
echo ===============================================================================
echo.
if exist "pea_cpp.exe" (
    echo [i] Se encontro pea_cpp.exe ya compilado.
    echo   [1] Ejecutar pea_cpp.exe directamente
    echo   [2] Recompilar desde el codigo fuente C++17
    set "RECOMP=1"
    set /p RECOMP="Seleccione [1-2, Enter=1]: "
    if "!RECOMP!"=="1" goto EXEC_CPP_BIN
)

set "CXX_BIN="
set "CXX_INC="
set "CXX_LIB="

if exist "C:\msys64\ucrt64\bin\g++.exe" (
    set "CXX_BIN=C:\msys64\ucrt64\bin\g++.exe"
    set "CXX_INC=-IC:/msys64/ucrt64/include"
    set "CXX_LIB=-LC:/msys64/ucrt64/lib"
    set "PATH=C:\msys64\ucrt64\bin;!PATH!"
    goto COMPILE_CPP
)
if exist "C:\msys64\mingw64\bin\g++.exe" (
    set "CXX_BIN=C:\msys64\mingw64\bin\g++.exe"
    set "CXX_INC=-IC:/msys64/mingw64/include"
    set "CXX_LIB=-LC:/msys64/mingw64/lib"
    set "PATH=C:\msys64\mingw64\bin;!PATH!"
    goto COMPILE_CPP
)
g++ --version >nul 2>&1
if !ERRORLEVEL! equ 0 (
    set "CXX_BIN=g++"
    goto COMPILE_CPP
)
if exist "C:\Program Files\CodeBlocks\MinGW\bin\g++.exe" (
    set "CXX_BIN=C:\Program Files\CodeBlocks\MinGW\bin\g++.exe"
    goto COMPILE_CPP
)
if exist "C:\MinGW\bin\g++.exe" (
    set "CXX_BIN=C:\MinGW\bin\g++.exe"
    goto COMPILE_CPP
)

echo [!] No se detecto compilador g++ con soporte SQLite3 en este equipo.
echo     Puede usar la opcion [1] Consola Python o [3] Portal Web sin compilar.
pause
goto MENU

:COMPILE_CPP
echo [+] Compilando con: "!CXX_BIN!"
"!CXX_BIN!" -std=c++17 -Wall -Wextra -Isrc/cpp/include !CXX_INC! src/cpp/main.cpp -o pea_cpp.exe !CXX_LIB! -lsqlite3 -static-libgcc -static-libstdc++
if !ERRORLEVEL! neq 0 (
    echo.
    echo [!] Error al compilar C++ (verifique que libsqlite3-dev este instalado en MinGW/MSYS2).
    pause
    goto MENU
)
echo [OK] Compilacion exitosa: pea_cpp.exe

:EXEC_CPP_BIN
echo.
pea_cpp.exe
pause
goto MENU

:RUN_TESTS
cls
call :DETECT_PYTHON
if !ERRORLEVEL! equ 0 (
    echo [+] Ejecutando suite de pruebas unitarias Python...
    if "!PYCMD!"=="py -3" (
        py -3 src\python\test_tda.py
    ) else (
        "!PYCMD!" src\python\test_tda.py
    )
)
pause
goto MENU

:OPEN_DOCX
cls
if exist "Documentacion_Tecnica_GrupoXX.docx" (
    echo [+] Abriendo Documentacion_Tecnica_GrupoXX.docx...
    start "" "Documentacion_Tecnica_GrupoXX.docx"
) else (
    echo [!] No se encontro Documentacion_Tecnica_GrupoXX.docx
)
pause
goto MENU
