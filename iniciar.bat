@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul
cd /d "%~dp0"
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
:: CHEQUEO DE DEPENDENCIAS (no fatal: pylib/ vendored cubre requests, bs4,
:: pypdf y reportlab; solo avisa y ofrece pip install -r requirements.txt)
:: ==============================================================================
:CHECK_DEPS
if "!PYCMD!"=="py -3" (
    py -3 -c "import requests, bs4, pypdf, reportlab" >nul 2>&1
) else (
    "!PYCMD!" -c "import requests, bs4, pypdf, reportlab" >nul 2>&1
)
if !ERRORLEVEL! neq 0 (
    echo.
    echo [i] Faltan librerias Python (requests/bs4/pypdf/reportlab).
    echo     El proyecto incluye bundle local pylib/ que cubre lo esencial.
    echo     Si algo falla, instale con: pip install -r requirements.txt
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
echo   [4] Compilar y Ejecutar en C++17 (Autodetecta MSYS2, MinGW, Code::Blocks)
echo   [5] Ejecutar Pruebas Unitarias de Estructuras de Datos (TDAs)
echo   [6] Abrir Documentacion Tecnica Oficial Word (.docx)
echo   [7] Empaquetar Entrega Formal en ZIP (Limpio para envio al docente)
echo   [8] Ingesta Masiva UPC - Todos los grupos (66) con CvLAC
echo   [0] Salir
echo.
echo ===============================================================================
set "OPC="
set /p OPC="Ingrese el numero de la opcion [0-8]: "

if "%OPC%"=="1" goto RUN_PY_CONSOLE
if "%OPC%"=="2" goto RUN_PY_GUI
if "%OPC%"=="3" goto RUN_WEB
if "%OPC%"=="4" goto RUN_CPP
if "%OPC%"=="5" goto RUN_TESTS
if "%OPC%"=="6" goto OPEN_DOCX
if "%OPC%"=="7" goto RUN_PACKAGE
if "%OPC%"=="8" goto RUN_INGESTA
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
    "!PYCMD!" -c "import webbrowser, sys; webbrowser.open('file:///' + sys.argv[1].replace(chr(92), '/').replace(' ', '%%20'))" "!HTML_PATH!" >nul 2>&1
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
            start "" %%B "file:///!HTML_PATH!"
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
echo     Si se abre en Bloc de Notas, copia esta ruta en tu navegador:
echo     file:///!HTML_PATH!
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

echo [!] No se detecto compilador g++ en este equipo.
echo     Opciones sin compilar: [1] Consola Python  [3] Portal Web
echo     Para compilar C++: instale MSYS2 desde https://www.msys2.org/
echo     y ejecute en la terminal MSYS2:
echo       pacman -S mingw-w64-ucrt-x86_64-gcc
echo.
echo Presione cualquier tecla para volver al menu...
pause >nul
goto MENU

:COMPILE_CPP
echo [+] Compilador detectado: "!CXX_BIN!"
echo.

:: Verificar si existe el amalgamado sqlite3.c (compilacion portable sin -lsqlite3)
if exist "src\cpp\sqlite3.c" (
    echo [+] Usando SQLite3 amalgamado incluido (portable, sin dependencias externas)
    echo [+] Compilando sqlite3.c como C...
    :: sqlite3.c DEBE compilarse como C puro (no C++), luego linkearse con el binario C++
    set "CC_BIN=!CXX_BIN:.exe=!"
    set "CC_BIN=!CC_BIN:g++=gcc!"
    if not exist "!CC_BIN!.exe" set "CC_BIN=gcc"
    "!CC_BIN!" -O2 !CXX_INC! -c src/cpp/sqlite3.c -o src/cpp/sqlite3_amalg.o
    if !ERRORLEVEL! neq 0 (
        echo [!] No se pudo compilar sqlite3.c con gcc. Intentando con -lsqlite3...
        goto COMPILE_CPP_NOSQLITE
    )
    echo [+] Compilando y linkeando C++17...
    "!CXX_BIN!" -std=c++17 -Wall -Wextra -Isrc/cpp/include !CXX_INC! ^
        src/cpp/main.cpp src/cpp/sqlite3_amalg.o ^
        -o pea_cpp.exe !CXX_LIB! ^
        -static-libgcc -static-libstdc++
    del /q src\cpp\sqlite3_amalg.o >nul 2>&1
    goto COMPILE_CPP_DONE
)

:COMPILE_CPP_NOSQLITE
    echo [i] src\cpp\sqlite3.c no encontrado — intentando con -lsqlite3 del sistema
    echo [+] Compilando...
    "!CXX_BIN!" -std=c++17 -Wall -Wextra -Isrc/cpp/include !CXX_INC! ^
        src/cpp/main.cpp ^
        -o pea_cpp.exe !CXX_LIB! ^
        -lsqlite3 -static-libgcc -static-libstdc++

:COMPILE_CPP_DONE

if !ERRORLEVEL! neq 0 (
    echo.
    echo [!] Error de compilacion C++. Posibles causas:
    echo     1. Falta src\cpp\sqlite3.c (amalgamado SQLite3)
    echo        Descargue de: https://www.sqlite.org/download.html
    echo        (archivo "sqlite-amalgamation-XXXXXXX.zip", copie sqlite3.c y sqlite3.h
    echo        a la carpeta src\cpp\)
    echo     2. El compilador no soporta C++17 (actualice MinGW/MSYS2)
    echo     3. Rutas con espacios o permisos insuficientes
    echo.
    echo     Alternativas sin compilar: [1] Consola Python  [3] Portal Web
    echo.
    echo Presione cualquier tecla para volver al menu...
    pause >nul
    goto MENU
)
echo [OK] Compilacion exitosa: pea_cpp.exe

:EXEC_CPP_BIN
echo.
echo [+] Ejecutando pea_cpp.exe...
echo.
pea_cpp.exe
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
call :DETECT_PYTHON
if !ERRORLEVEL! equ 0 (
    echo [+] Ejecutando suite de pruebas unitarias Python...
    echo.
    if "!PYCMD!"=="py -3" (
        py -3 src\python\test_tda.py
    ) else (
        "!PYCMD!" src\python\test_tda.py
    )
) else (
    echo [i] Python no detectado: se omiten tests Python.
)
echo.
echo [+] Buscando compilador C++ para pruebas de TDAs en C++...
g++ --version >nul 2>&1
if !ERRORLEVEL! equ 0 (
    echo [+] Compilando y ejecutando tests C++...
    if exist "src\cpp\sqlite3.c" (
        g++ -std=c++17 -Wall -Wextra -Isrc\cpp\include src\cpp\test_tda.cpp src\cpp\sqlite3.c -o src\cpp\test_tda.exe -static-libgcc -static-libstdc++
    ) else (
        g++ -std=c++17 -Wall -Wextra -Isrc\cpp\include src\cpp\test_tda.cpp -o src\cpp\test_tda.exe -lsqlite3
    )
    if !ERRORLEVEL! equ 0 (
        src\cpp\test_tda.exe
        del /q src\cpp\test_tda.exe >nul 2>&1
    ) else (
        echo [!] No se pudo compilar tests C++.
        echo     Si falta sqlite3: descargue el amalgamado de sqlite.org y
        echo     coloque sqlite3.c y sqlite3.h en src\cpp\
    )
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
:: FIN — Salida limpia (red de seguridad: nunca se cierra sin que el usuario vea)
:: ==============================================================================
:FIN
echo.
echo   Hasta luego. — PEA-i Sistema de Analisis de Investigacion UPC
echo.
pause >nul
exit /b 0
