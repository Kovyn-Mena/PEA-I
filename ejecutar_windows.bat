@echo off
chcp 65001 >nul
title PEA-i — Programa Estadístico de Análisis de Investigación (UPC)
echo ===============================================================================
echo   PEA-i: Programa Estadístico de Análisis de Investigación (UPC)
echo   Asignatura: Estructura de Datos (Taller 2) - Semestre 2026-I
echo ===============================================================================
echo.
echo [1/2] Verificando entorno de Python en su equipo...

where python >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set PYCMD=python
    goto RUN
)

where py >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set PYCMD=py
    goto RUN
)

where python3 >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set PYCMD=python3
    goto RUN
)

echo [!] ERROR: No se encontró Python instalado en este equipo con Windows.
echo.
echo Para solucionarlo:
echo   1. Descargue Python 3 desde: https://www.python.org/downloads/
echo   2. Durante la instalación, MARQUE la casilla:
echo      "Add python.exe to PATH" (Agregar Python al PATH del sistema).
echo   3. Vuelva a ejecutar este archivo (ejecutar_windows.bat).
echo.
echo Presione cualquier tecla para salir...
pause >nul
exit /b 1

:RUN
echo [OK] Python detectado correctamente.
echo [2/2] Iniciando PEA-i (Consola Interactiva UPC)...
echo.
%PYCMD% Taller2_AB_PO_XX.py
if %ERRORLEVEL% neq 0 (
    echo.
    echo [i] La aplicación finalizó con código de salida %ERRORLEVEL%.
    pause
)
