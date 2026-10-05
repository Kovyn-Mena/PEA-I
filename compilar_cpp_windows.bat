@echo off
chcp 65001 >nul
title PEA-i — Compilador y Ejecutor C++ (Windows)
echo ===============================================================================
echo   PEA-i: Compilación y Ejecución en C++17 (Windows)
echo   Universidad Popular del Cesar — Estructura de Datos
echo ===============================================================================
echo.

set CXX_BIN=
set CXX_INC=
set CXX_LIB=

:: 1. Verificar si ya existe el ejecutable pea_cpp.exe compilado previamente
if exist "pea_cpp.exe" (
    echo [i] Se encontró un binario 'pea_cpp.exe' previamente compilado.
    echo.
    echo   [1] Ejecutar directamente pea_cpp.exe
    echo   [2] Recompilar desde el código fuente C++
    echo.
    set /p RECOMP="Seleccione una opción [1-2, Enter=1]: "
    if "%RECOMP%"=="2" goto BUSCAR_COMPILADOR
    goto EJECUTAR_BINARIO
)

:BUSCAR_COMPILADOR
echo [1/3] Detectando compilador C++ (g++) en su sistema Windows...

:: 1. Probar g++ en PATH
where g++ >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set CXX_BIN=g++
    echo [OK] Se detectó g++ en el PATH del sistema.
    goto COMPILAR
)

:: 2. Probar MSYS2 UCRT64 (Configuración estándar UPC / Damián)
if exist "C:\msys64\ucrt64\bin\g++.exe" (
    set CXX_BIN=C:\msys64\ucrt64\bin\g++.exe
    set CXX_INC=-IC:/msys64/ucrt64/include
    set CXX_LIB=-LC:/msys64/ucrt64/lib
    echo [OK] Se detectó MSYS2 UCRT64 en C:\msys64\ucrt64.
    goto COMPILAR
)

:: 3. Probar MSYS2 MINGW64
if exist "C:\msys64\mingw64\bin\g++.exe" (
    set CXX_BIN=C:\msys64\mingw64\bin\g++.exe
    set CXX_INC=-IC:/msys64/mingw64/include
    set CXX_LIB=-LC:/msys64/mingw64/lib
    echo [OK] Se detectó MSYS2 MINGW64 en C:\msys64\mingw64.
    goto COMPILAR
)

:: 4. Probar Code::Blocks
if exist "C:\Program Files\CodeBlocks\MinGW\bin\g++.exe" (
    set CXX_BIN="C:\Program Files\CodeBlocks\MinGW\bin\g++.exe"
    echo [OK] Se detectó MinGW de Code::Blocks (64-bit).
    goto COMPILAR
)
if exist "C:\Program Files (x86)\CodeBlocks\MinGW\bin\g++.exe" (
    set CXX_BIN="C:\Program Files (x86)\CodeBlocks\MinGW\bin\g++.exe"
    echo [OK] Se detectó MinGW de Code::Blocks (32-bit).
    goto COMPILAR
)

:: 5. Probar Dev-C++
if exist "C:\Program Files (x86)\Dev-Cpp\MinGW64\bin\g++.exe" (
    set CXX_BIN="C:\Program Files (x86)\Dev-Cpp\MinGW64\bin\g++.exe"
    echo [OK] Se detectó MinGW64 de Dev-C++.
    goto COMPILAR
)

:: 6. Probar MinGW estándar
if exist "C:\MinGW\bin\g++.exe" (
    set CXX_BIN=C:\MinGW\bin\g++.exe
    echo [OK] Se detectó MinGW en C:\MinGW.
    goto COMPILAR
)

:: Si no se encontró ningún compilador:
echo.
echo [!] AVISO: No se encontró ningún compilador g++ instalado en las rutas estándar.
echo.
echo No te preocupes: PEA-i cuenta con una versión idéntica en Python que ejecuta
echo exactamente las mismas estructuras de datos (Multilista 3D, Pila Undo, Cola)
echo y accede a los 3,351 productos de investigación sin necesidad de compilar nada.
echo.
echo ¿Deseas iniciar la aplicación ahora mismo usando Python? [S/N]
set /p USAR_PY="> "
if /i "%USAR_PY%"=="S" (
    call ejecutar_windows.bat
    exit /b 0
)
echo.
echo Si deseas compilar en C++ manualmente, instala MSYS2 o MinGW con SQLite3.
pause
exit /b 1

:COMPILAR
echo [2/3] Compilando pea_cpp.exe con soporte C++17 y SQLite3...
echo Ejecutando: %CXX_BIN% -std=c++17 -Wall -Isrc/cpp/include %CXX_INC% src/cpp/main.cpp -o pea_cpp.exe %CXX_LIB% -lsqlite3 -static-libgcc -static-libstdc++
%CXX_BIN% -std=c++17 -Wall -Wextra -Isrc/cpp/include %CXX_INC% src/cpp/main.cpp -o pea_cpp.exe %CXX_LIB% -lsqlite3 -static-libgcc -static-libstdc++

if %ERRORLEVEL% neq 0 (
    echo.
    echo [!] ERROR: La compilación de C++ no se pudo completar.
    echo     Causa común: Falta la librería SQLite3 de desarrollo en tu MinGW.
    echo.
    echo En MSYS2 puedes instalarla con:
    echo     pacman -S mingw-w64-ucrt-x86_64-sqlite3
    echo.
    echo ¿Deseas abrir la versión de Python que funciona de inmediato sin compilar? [S/N]
    set /p USAR_PY="> "
    if /i "%USAR_PY%"=="S" (
        call ejecutar_windows.bat
        exit /b 0
    )
    pause
    exit /b 1
)

echo [OK] Compilación exitosa: pea_cpp.exe generado correctamente.
echo.

:EJECUTAR_BINARIO
echo [3/3] Iniciando Consola C++ PEA-i (UPC)...
echo ===============================================================================
echo.
pea_cpp.exe
if %ERRORLEVEL% neq 0 (
    echo.
    echo [i] La aplicación C++ finalizó con código %ERRORLEVEL%.
    pause
)
