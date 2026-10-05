@echo off
chcp 65001 >nul
title PEA-i — Programa Estadistico de Analisis de Investigacion (UPC)
echo ===============================================================================
echo   PEA-i: Programa Estadistico de Analisis de Investigacion - UPC
echo   Asignatura: Estructura de Datos (Taller 2) - Semestre 2026-I
echo ===============================================================================
echo.
echo [1/2] Verificando entorno de Python en su equipo...

set "PYCMD="

:: 1. Verificar comando en PATH
where python >nul 2>&1 && set "PYCMD=python" && goto RUN
where py >nul 2>&1 && set "PYCMD=py" && goto RUN
where python3 >nul 2>&1 && set "PYCMD=python3" && goto RUN

:: 2. Verificar rutas de MSYS2 (UCRT64 / MINGW64)
if exist "C:\msys64\ucrt64\bin\python.exe" set "PYCMD=C:\msys64\ucrt64\bin\python.exe" && goto RUN
if exist "C:\msys64\mingw64\bin\python.exe" set "PYCMD=C:\msys64\mingw64\bin\python.exe" && goto RUN

:: 3. Verificar instalaciones estandar de usuario (AppData)
for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python3*") do (
    if exist "%%D\python.exe" (
        set "PYCMD=%%D\python.exe"
        goto RUN
    )
)

:: 4. Verificar Program Files
for /d %%D in ("C:\Program Files\Python3*") do (
    if exist "%%D\python.exe" (
        set "PYCMD=%%D\python.exe"
        goto RUN
    )
)
for /d %%D in ("C:\Program Files (x86)\Python3*") do (
    if exist "%%D\python.exe" (
        set "PYCMD=%%D\python.exe"
        goto RUN
    )
)

:: 5. Verificar WindowsApps
if exist "%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe" (
    set "PYCMD=%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe"
    goto RUN
)

:: Si no se encontro Python
echo [!] ERROR: No se encontro Python instalado en este equipo con Windows.
echo.
echo Para solucionarlo:
echo   1. Descargue Python 3 desde: https://www.python.org/downloads/
echo   2. Durante la instalacion, asegurese de marcar la casilla:
echo      "Add python.exe to PATH"
echo   3. Vuelva a ejecutar este archivo.
echo.
echo Presione una tecla para salir...
pause >nul
exit /b 1

:RUN
echo [OK] Python detectado: %PYCMD%
echo [2/2] Iniciando PEA-i (Consola Interactiva UPC)...
echo.
"%PYCMD%" Taller2_AB_PO_XX.py
if %ERRORLEVEL% neq 0 (
    echo.
    echo [i] La aplicacion finalizo con codigo %ERRORLEVEL%.
    pause
)
