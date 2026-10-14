@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul
cd /d "%~dp0"
set "PEAI_PYLIB=%~dp0pylib"
set "PYTHONDONTWRITEBYTECODE=1"
if exist "src\cpp\sqlite3_amalg.o" del /q "src\cpp\sqlite3_amalg.o" >nul 2>&1
if exist "src\cpp\test_tda.exe" del /q "src\cpp\test_tda.exe" >nul 2>&1
title PEA-i - Sistema de Analisis de Investigacion UPC (Windows)
goto MENU

:: ==============================================================================
:: SUBRUTINAS — se definen ANTES del :MENU para que goto MENU las salte
:: ==============================================================================

:: ==============================================================================
:: DETECCION REAL DE PYTHON (Evita el alias fantasma de Microsoft Store)
:: Usa -c "print('ok')" en lugar de --version: el alias del Store retorna
:: ERRORLEVEL 0 con --version pero falla al intentar ejecutar cualquier script.
:: ==============================================================================
:DETECT_PYTHON
set "PYCMD="

python -c "print('ok')" >nul 2>&1
if !ERRORLEVEL! equ 0 (
    set "PYCMD=python"
    exit /b 0
)

py -3 -c "print('ok')" >nul 2>&1
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
echo [!] ERROR: No se detecto Python 3 funcional en este equipo.
echo     El alias de Microsoft Store no es suficiente.
echo     Instale Python 3 desde https://www.python.org/downloads/
echo     marcando la casilla "Add python.exe to PATH".
echo     Mientras tanto puede usar la opcion [3] Portal Web (no requiere Python).
echo.
exit /b 1

:: ==============================================================================
:: DETECCION SILENCIOSA DE PYTHON (sin mensajes — para uso interno en RUN_WEB)
:: ==============================================================================
:DETECT_PYTHON_SILENCIOSO
set "PYCMD="
python -c "print('ok')" >nul 2>&1
if !ERRORLEVEL! equ 0 ( set "PYCMD=python" & exit /b 0 )
py -3 -c "print('ok')" >nul 2>&1
if !ERRORLEVEL! equ 0 ( set "PYCMD=py -3" & exit /b 0 )
if exist "C:\msys64\ucrt64\bin\python.exe" (
    set "PYCMD=C:\msys64\ucrt64\bin\python.exe" & exit /b 0
)
if exist "C:\msys64\mingw64\bin\python.exe" (
    set "PYCMD=C:\msys64\mingw64\bin\python.exe" & exit /b 0
)
for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python3*") do (
    if exist "%%D\python.exe" ( set "PYCMD=%%D\python.exe" & exit /b 0 )
)
for /d %%D in ("C:\Program Files\Python3*") do (
    if exist "%%D\python.exe" ( set "PYCMD=%%D\python.exe" & exit /b 0 )
)
exit /b 1

:: ==============================================================================
:: DETECCION DE COMPILADOR C++ (prioriza instalaciones conocidas y completas)
:: ==============================================================================
:DETECT_CPP
set "CXX_BIN="
set "CC_BIN="
set "CXX_INC="
set "CXX_LIB="

if exist "C:\msys64\ucrt64\bin\g++.exe" (
    set "CXX_BIN=C:\msys64\ucrt64\bin\g++.exe"
    set "CC_BIN=C:\msys64\ucrt64\bin\gcc.exe"
    set "CXX_INC=-IC:/msys64/ucrt64/include"
    set "CXX_LIB=-LC:/msys64/ucrt64/lib"
    set "PATH=C:\msys64\ucrt64\bin;%PATH%"
    exit /b 0
)
if exist "C:\msys64\mingw64\bin\g++.exe" (
    set "CXX_BIN=C:\msys64\mingw64\bin\g++.exe"
    set "CC_BIN=C:\msys64\mingw64\bin\gcc.exe"
    set "CXX_INC=-IC:/msys64/mingw64/include"
    set "CXX_LIB=-LC:/msys64/mingw64/lib"
    set "PATH=C:\msys64\mingw64\bin;%PATH%"
    exit /b 0
)
if exist "C:\Program Files\CodeBlocks\MinGW\bin\g++.exe" (
    set "CXX_BIN=C:\Program Files\CodeBlocks\MinGW\bin\g++.exe"
    set "CC_BIN=C:\Program Files\CodeBlocks\MinGW\bin\gcc.exe"
    exit /b 0
)
if exist "C:\Program Files (x86)\Dev-Cpp\MinGW64\bin\g++.exe" (
    set "CXX_BIN=C:\Program Files (x86)\Dev-Cpp\MinGW64\bin\g++.exe"
    set "CC_BIN=C:\Program Files (x86)\Dev-Cpp\MinGW64\bin\gcc.exe"
    exit /b 0
)
if exist "C:\MinGW\bin\g++.exe" (
    set "CXX_BIN=C:\MinGW\bin\g++.exe"
    set "CC_BIN=C:\MinGW\bin\gcc.exe"
    exit /b 0
)
g++ --version >nul 2>&1
if !ERRORLEVEL! equ 0 (
    set "CXX_BIN=g++"
    set "CC_BIN=gcc"
    exit /b 0
)
exit /b 1

:: ==============================================================================
:: CHEQUEO DE DEPENDENCIAS (no fatal; avisa si las funciones avanzadas no
:: encuentran sus dependencias completas en el Python elegido o en pylib/)
:: ==============================================================================
:CHECK_DEPS
if "!PYCMD!"=="py -3" (
    py -3 -c "import os,sys; sys.path.insert(0, os.environ['PEAI_PYLIB']); import requests, bs4, pypdf, reportlab" >nul 2>&1
) else (
    "!PYCMD!" -c "import os,sys; sys.path.insert(0, os.environ['PEAI_PYLIB']); import requests, bs4, pypdf, reportlab" >nul 2>&1
)
if !ERRORLEVEL! neq 0 (
    echo.
    echo [i] Dependencias Python ausentes o incompletas (requests/bs4/pypdf/reportlab).
    echo     Para habilitar scraping e informes PDF, ejecute:
    if "!PYCMD!"=="py -3" (
        echo     py -3 -m pip install -r requirements.txt
    ) else (
        echo     "!PYCMD!" -m pip install -r requirements.txt
    )
    echo.
)
exit /b 0

:: ==============================================================================
:: MENU PRINCIPAL
:: ==============================================================================
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
echo   [2] Dashboard Grafico Interactivo Python (HTML5 + 3 Vistas --gui)
echo   [3] Portal Web Interactivo del Hipercubo y CRUD (HTML5 Offline)
echo   [4] Compilar y Ejecutar en C++17 (Autodetecta MSYS2, MinGW, Code::Blocks, Dev-C++)
echo   [5] Ejecutar Pruebas Unitarias de Estructuras de Datos (TDAs)
echo   [6] Abrir Documentacion Tecnica Oficial Word (.docx)
echo   [7] Empaquetar Entrega Formal en ZIP (Limpio para envio al docente)
echo   [8] Ingesta Masiva UPC - Todos los grupos (66) con CvLAC
echo   [9] Diagnostico del sistema (reporte para soporte)
echo   [0] Salir
echo.
echo ===============================================================================
set "OPC="
set /p OPC="Ingrese el numero de la opcion [0-9]: "
if errorlevel 1 goto FIN

if "%OPC%"=="1" goto RUN_PY_CONSOLE
if "%OPC%"=="2" goto RUN_PY_GUI
if "%OPC%"=="3" goto RUN_WEB
if "%OPC%"=="4" goto RUN_CPP
if "%OPC%"=="5" goto RUN_TESTS
if "%OPC%"=="6" goto OPEN_DOCX
if "%OPC%"=="7" goto RUN_PACKAGE
if "%OPC%"=="8" goto RUN_INGESTA
if "%OPC%"=="9" goto RUN_DIAGNOSTICO
if "%OPC%"=="0" goto FIN

echo [!] Opcion no valida. Intente nuevamente.
timeout /t 2 >nul
goto MENU

:: ==============================================================================
:: [1] CONSOLA INTERACTIVA PYTHON
:: ==============================================================================
:RUN_PY_CONSOLE
cls
echo [*] Verificando Python...
call :DETECT_PYTHON
if !ERRORLEVEL! neq 0 (
    echo Presione cualquier tecla para volver al menu...
    pause >nul
    goto MENU
)
echo [OK] Python detectado: !PYCMD!
call :CHECK_DEPS
echo [+] Iniciando Consola Interactiva PEA-i...
echo.
if "!PYCMD!"=="py -3" (
    py -3 Taller2_AB_PO_XX.py
) else (
    "!PYCMD!" Taller2_AB_PO_XX.py
)
echo.
echo Presione cualquier tecla para volver al menu...
pause >nul
goto MENU

:: ==============================================================================
:: [2] DASHBOARD GRAFICO PYTHON (--gui)
:: ==============================================================================
:RUN_PY_GUI
cls
echo [*] Verificando Python...
call :DETECT_PYTHON
if !ERRORLEVEL! neq 0 (
    echo Presione cualquier tecla para volver al menu...
    pause >nul
    goto MENU
)
echo [OK] Python detectado: !PYCMD!
call :CHECK_DEPS
echo [+] Iniciando Dashboard Grafico Interactivo Python (--gui)...
echo.
if "!PYCMD!"=="py -3" (
    py -3 Taller2_AB_PO_XX.py --gui
) else (
    "!PYCMD!" Taller2_AB_PO_XX.py --gui
)
echo.
echo Presione cualquier tecla para volver al menu...
pause >nul
goto MENU

:: ==============================================================================
:: [3] PORTAL WEB HTML5 OFFLINE
:: Usa rundll32 url.dll,FileProtocolHandler para forzar apertura en navegador
:: (evita que Windows abra el .html en Bloc de Notas o WordPad).
:: Fallbacks: Python webbrowser, navegadores conocidos, start clasico.
:: ==============================================================================
:RUN_WEB
cls
echo [+] Abriendo Portal Web Interactivo del Hipercubo...
if not exist "dist\visualizador_hipercubo.html" (
    echo.
    echo [!] No se encontro dist\visualizador_hipercubo.html
    echo     Verifique que extrajiste el ZIP completamente en una carpeta
    echo     y que la carpeta dist\ existe junto a este archivo iniciar.bat.
    echo.
    echo Presione cualquier tecla para volver al menu...
    pause >nul
    goto MENU
)

:: Ruta absoluta necesaria para rundll32 y llamadas a navegadores
set "HTML_PATH=%~dp0dist\visualizador_hipercubo.html"

:: Intento 1: Python webbrowser (mas confiable y multiplataforma)
call :DETECT_PYTHON_SILENCIOSO
if defined PYCMD (
    if "!PYCMD!"=="py -3" (
        py -3 -c "import pathlib,sys,webbrowser; sys.exit(0 if webbrowser.open(pathlib.Path(sys.argv[1]).as_uri()) else 1)" "!HTML_PATH!" >nul 2>&1
    ) else (
        "!PYCMD!" -c "import pathlib,sys,webbrowser; sys.exit(0 if webbrowser.open(pathlib.Path(sys.argv[1]).as_uri()) else 1)" "!HTML_PATH!" >nul 2>&1
    )
    if !ERRORLEVEL! equ 0 (
        echo [OK] Portal abierto en el navegador via Python webbrowser.
        echo.
        echo Presione cualquier tecla para volver al menu...
        pause >nul
        goto MENU
    )
)

:: Intento 2: rundll32 FileProtocolHandler — abre el manejador de protocolo
:: file:// de Windows, que siempre usa el navegador (no el editor de texto)
rundll32 url.dll,FileProtocolHandler "!HTML_PATH!"
if !ERRORLEVEL! equ 0 (
    echo [OK] Portal abierto con rundll32.
    echo.
    echo Presione cualquier tecla para volver al menu...
    pause >nul
    goto MENU
)

:: Intento 3: navegadores conocidos directamente
set "ABIERTO=0"
for %%B in (
    "%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"
    "%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"
    "%ProgramFiles%\Google\Chrome\Application\chrome.exe"
    "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
    "%ProgramFiles%\Mozilla Firefox\firefox.exe"
    "%ProgramFiles%\BraveSoftware\Brave-Browser\Application\brave.exe"
) do (
    if !ABIERTO! equ 0 (
        if exist %%B (
            start "" %%B "!HTML_PATH!"
            set "ABIERTO=1"
            echo [OK] Portal abierto con %%~B
        )
    )
)
if !ABIERTO! equ 1 (
    echo.
    echo Presione cualquier tecla para volver al menu...
    pause >nul
    goto MENU
)

:: Fallback final: start clasico con instrucciones manuales
echo [!] No se encontro un navegador conocido. Intentando apertura directa...
echo     Si no se abre, copia esta ruta en tu navegador:
echo     !HTML_PATH!
echo.
start "" "!HTML_PATH!"
echo Presione cualquier tecla para volver al menu...
pause >nul
goto MENU

:: ==============================================================================
:: [4] COMPILAR Y EJECUTAR C++17
:: Usa sqlite3.c amalgamado incluido en src/cpp/ — no requiere libsqlite3
:: instalado en MSYS2/MinGW. Si no existe el amalgamado, informa como instalarlo.
:: ==============================================================================
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
    echo.
    set "RECOMP=1"
    set /p RECOMP="Seleccione [1-2, Enter=1]: "
    if errorlevel 1 goto FIN
    if "!RECOMP!"=="1" goto EXEC_CPP_BIN
)

call :DETECT_CPP
if !ERRORLEVEL! neq 0 goto CPP_COMPILER_MISSING

echo [+] Compilador detectado: "!CXX_BIN!"
echo.
set "CPP_BUILD=%TEMP%\pea_i_cpp_%RANDOM%_%RANDOM%.exe"
set "SQLITE_OBJ=%TEMP%\pea_i_sqlite_%RANDOM%_%RANDOM%.o"

if exist "src\cpp\sqlite3.c" (
    echo [+] Usando SQLite3 amalgamado incluido.
    echo [+] Compilando SQLite3 como C...
    "!CC_BIN!" -O2 !CXX_INC! -c "src\cpp\sqlite3.c" -o "!SQLITE_OBJ!"
    set "BUILD_STATUS=!ERRORLEVEL!"
    if not "!BUILD_STATUS!"=="0" goto CPP_BUILD_FAILED

    echo [+] Compilando y enlazando C++17...
    "!CXX_BIN!" -std=c++17 -Wall -Wextra -Isrc/cpp/include !CXX_INC! ^
        "src/cpp/main.cpp" "!SQLITE_OBJ!" -o "!CPP_BUILD!" !CXX_LIB! ^
        -static-libgcc -static-libstdc++
    set "BUILD_STATUS=!ERRORLEVEL!"
) else (
    echo [+] Compilando con SQLite del sistema...
    "!CXX_BIN!" -std=c++17 -Wall -Wextra -Isrc/cpp/include !CXX_INC! ^
        "src/cpp/main.cpp" -o "!CPP_BUILD!" !CXX_LIB! ^
        -lsqlite3 -static-libgcc -static-libstdc++
    set "BUILD_STATUS=!ERRORLEVEL!"
)

if exist "!SQLITE_OBJ!" del /q "!SQLITE_OBJ!" >nul 2>&1
if not "!BUILD_STATUS!"=="0" goto CPP_BUILD_FAILED
move /y "!CPP_BUILD!" "%~dp0pea_cpp.exe" >nul
if !ERRORLEVEL! neq 0 goto CPP_BUILD_FAILED
echo [OK] Compilacion exitosa: pea_cpp.exe
goto EXEC_CPP_BIN

:CPP_COMPILER_MISSING
echo [!] No se detecto compilador g++ en este equipo.
echo     Opciones sin compilar: [1] Consola Python  [3] Portal Web
echo     Para compilar C++: instale MSYS2 desde https://www.msys2.org/
echo     y ejecute en la terminal MSYS2:
echo       pacman -S mingw-w64-ucrt-x86_64-gcc
echo.
echo Presione cualquier tecla para volver al menu...
pause >nul
goto MENU

:CPP_BUILD_FAILED
if exist "!SQLITE_OBJ!" del /q "!SQLITE_OBJ!" >nul 2>&1
if exist "!CPP_BUILD!" del /q "!CPP_BUILD!" >nul 2>&1
echo.
echo [!] Error de compilacion C++. Posibles causas:
echo     1. Error del compilador o falta de permisos para escribir temporales.
echo     2. El compilador no soporta C++17 (actualice MinGW/MSYS2).
echo     3. Si falta sqlite3.c, instale SQLite3 de desarrollo para enlazar -lsqlite3.
echo.
echo     Alternativas sin compilar: [1] Consola Python  [3] Portal Web
echo.
echo Presione cualquier tecla para volver al menu...
pause >nul
goto MENU

:EXEC_CPP_BIN
echo.
echo [+] Ejecutando pea_cpp.exe...
echo.
"%~dp0pea_cpp.exe"
echo.
echo Presione cualquier tecla para volver al menu...
pause >nul
goto MENU

:: ==============================================================================
:: [5] PRUEBAS UNITARIAS TDAs (Python + C++)
:: ==============================================================================
:RUN_TESTS
cls
echo ===============================================================================
echo   PEA-i: Pruebas Unitarias de Estructuras de Datos
echo ===============================================================================
echo.
call :DETECT_PYTHON_SILENCIOSO
if defined PYCMD (
    echo [+] Ejecutando suite de pruebas unitarias Python...
    echo.
    if "!PYCMD!"=="py -3" (
        py -3 src\python\test_tda.py
    ) else (
        "!PYCMD!" src\python\test_tda.py
    )
    set "TEST_STATUS=!ERRORLEVEL!"
    if not "!TEST_STATUS!"=="0" echo [!] Las pruebas Python terminaron con errores.
) else (
    echo [i] Python no detectado: se omiten tests Python.
)
echo.
echo [+] Buscando compilador C++ para pruebas de TDAs en C++...
call :DETECT_CPP
if !ERRORLEVEL! equ 0 (
    echo [+] Compilando y ejecutando tests C++...
    set "TEST_BIN=%TEMP%\pea_i_test_tda_%RANDOM%_%RANDOM%.exe"
    "!CXX_BIN!" -std=c++17 -Wall -Wextra -Isrc\cpp\include ^
        "src\cpp\test_tda.cpp" -o "!TEST_BIN!" -static-libgcc -static-libstdc++
    set "TEST_STATUS=!ERRORLEVEL!"
    if "!TEST_STATUS!"=="0" (
        "!TEST_BIN!"
        set "TEST_STATUS=!ERRORLEVEL!"
    ) else (
        echo [!] No se pudo compilar tests C++.
    )
    if exist "!TEST_BIN!" del /q "!TEST_BIN!" >nul 2>&1
    if not "!TEST_STATUS!"=="0" echo [!] Las pruebas C++ terminaron con errores.
) else (
    echo [i] g++ no detectado: se omiten tests C++.
)
echo.
echo Presione cualquier tecla para volver al menu...
pause >nul
goto MENU

:: ==============================================================================
:: [6] ABRIR DOCUMENTACION TECNICA (.docx)
:: ==============================================================================
:OPEN_DOCX
cls
if exist "Documentacion_Tecnica_GrupoXX.docx" (
    echo [+] Abriendo Documentacion_Tecnica_GrupoXX.docx...
    start "" "Documentacion_Tecnica_GrupoXX.docx"
) else (
    echo [!] No se encontro Documentacion_Tecnica_GrupoXX.docx
)
echo.
echo Presione cualquier tecla para volver al menu...
pause >nul
goto MENU

:: ==============================================================================
:: [7] EMPAQUETAR ENTREGA EN ZIP
:: ==============================================================================
:RUN_PACKAGE
cls
echo [*] Verificando Python...
call :DETECT_PYTHON
if !ERRORLEVEL! neq 0 (
    echo Presione cualquier tecla para volver al menu...
    pause >nul
    goto MENU
)
echo [OK] Python detectado: !PYCMD!
echo [+] Creando archivo de entrega ZIP limpio...
echo.
if "!PYCMD!"=="py -3" (
    py -3 scripts\package_zip.py
) else (
    "!PYCMD!" scripts\package_zip.py
)
echo.
echo Presione cualquier tecla para volver al menu...
pause >nul
goto MENU

:: ==============================================================================
:: [8] INGESTA MASIVA UPC (66 grupos con CvLAC)
:: ==============================================================================
:RUN_INGESTA
cls
echo [*] Verificando Python...
call :DETECT_PYTHON
if !ERRORLEVEL! neq 0 (
    echo Presione cualquier tecla para volver al menu...
    pause >nul
    goto MENU
)
call :CHECK_DEPS
echo ===============================================================================
echo   PEA-i: Ingesta Masiva UPC - 66 grupos con hojas de vida CvLAC
echo ===============================================================================
echo.
echo   [1] Rapida offline (snapshots locales, sin CvLAC) --auto-ingest --sin-cvlac
echo   [2] Completa en vivo (red MinCiencias + CvLAC, 1-2 horas) --auto-ingest --con-red
echo   [3] Completa forzada (reprocesa todo) --auto-ingest --con-red --forzar
echo   [0] Volver al menu
echo.
set "ING="
set /p ING="Seleccione [0-3]: "
if errorlevel 1 goto FIN
if "%ING%"=="1" goto INGESTA_RAPIDA
if "%ING%"=="2" goto INGESTA_FULL
if "%ING%"=="3" goto INGESTA_FORZADA
goto MENU

:INGESTA_RAPIDA
echo [+] Ingesta rapida offline...
if "!PYCMD!"=="py -3" (
    py -3 Taller2_AB_PO_XX.py --auto-ingest --sin-cvlac
) else (
    "!PYCMD!" Taller2_AB_PO_XX.py --auto-ingest --sin-cvlac
)
echo.
echo Presione cualquier tecla para volver al menu...
pause >nul
goto MENU

:INGESTA_FULL
echo [+] Ingesta completa en vivo (puede tardar 1-2 horas, no cierre la ventana)...
if "!PYCMD!"=="py -3" (
    py -3 Taller2_AB_PO_XX.py --auto-ingest --con-red
) else (
    "!PYCMD!" Taller2_AB_PO_XX.py --auto-ingest --con-red
)
echo.
echo Presione cualquier tecla para volver al menu...
pause >nul
goto MENU

:INGESTA_FORZADA
echo [+] Ingesta completa forzada en vivo...
if "!PYCMD!"=="py -3" (
    py -3 Taller2_AB_PO_XX.py --auto-ingest --con-red --forzar
) else (
    "!PYCMD!" Taller2_AB_PO_XX.py --auto-ingest --con-red --forzar
)
echo.
echo Presione cualquier tecla para volver al menu...
pause >nul
goto MENU

:: ==============================================================================
:: [9] DIAGNOSTICO DEL SISTEMA (reporte copiable para soporte)
:: ==============================================================================
:RUN_DIAGNOSTICO
cls
call :DETECT_PYTHON
if !ERRORLEVEL! neq 0 (
    pause
    goto MENU
)
echo [+] Ejecutando diagnostico del sistema...
echo     (copie el reporte si necesita soporte)
echo.
if "!PYCMD!"=="py -3" (
    py -3 Taller2_AB_PO_XX.py --diagnostico
) else (
    "!PYCMD!" Taller2_AB_PO_XX.py --diagnostico
)
echo.
echo Presione cualquier tecla para volver al menu...
pause >nul
goto MENU

:: ==============================================================================
:: FIN — Salida limpia (red de seguridad: nunca se cierra sin que el usuario vea)
:: ==============================================================================
:FIN
echo.
echo   Hasta luego. — PEA-i Sistema de Analisis de Investigacion UPC
echo.
pause >nul
exit /b 0
