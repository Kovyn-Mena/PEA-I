@echo off
chcp 65001 >nul
title PEA-i — Sistema de Análisis de Investigación UPC (Windows)

:MENU
cls
echo ===============================================================================
echo   PEA-i: Programa Estadístico de Análisis de Investigación (UPC)
echo   Universidad Popular del Cesar — Facultad de Ingeniería y Tecnológicas
echo   Asignatura: Estructura de Datos (Taller 2) | Semestre 2026-I
echo   Docente: Ing. Adith Bismarck Pérez Orozco
echo   Estudiante: Kovyn B. Mena
echo ===============================================================================
echo.
echo   Bienvenido al lanzador principal para Windows.
echo   Por favor seleccione una opción para ejecutar:
echo.
echo   [1] Ejecutar Consola Autónoma (Recomendado - Abre al instante sin compilar)
echo   [2] Compilar y Ejecutar en C++17 (Autodetecta g++, MSYS2, Code::Blocks)
echo   [3] Abrir Portal Web Ejecutivo (Visualizador del Hipercubo en navegador)
echo   [4] Ver Documento Técnico Oficial Word (.docx)
echo   [5] Ver Informe PDF Oficial de Investigación (GISICO)
echo   [6] Ejecutar Pruebas Unitarias de Estructuras de Datos (TDAs)
echo   [0] Salir
echo.
echo ===============================================================================
set /p OPC="Ingrese el número de la opción [0-6]: "

if "%OPC%"=="1" goto RUN_PY
if "%OPC%"=="2" goto RUN_CPP
if "%OPC%"=="3" goto RUN_WEB
if "%OPC%"=="4" goto OPEN_DOCX
if "%OPC%"=="5" goto OPEN_PDF
if "%OPC%"=="6" goto RUN_TESTS
if "%OPC%"=="0" exit /b 0

echo [!] Opción no válida. Intente nuevamente.
timeout /t 2 >nul
goto MENU

:RUN_PY
cls
call ejecutar_windows.bat
goto MENU

:RUN_CPP
cls
call compilar_cpp_windows.bat
goto MENU

:RUN_WEB
cls
echo [i] Abriendo el Portal Web Ejecutivo del Hipercubo en su navegador...
start dist\visualizador_hipercubo.html
echo [OK] Abierto exitosamente.
pause
goto MENU

:OPEN_DOCX
cls
if exist "Documentacion_Tecnica_GrupoXX.docx" (
    echo [i] Abriendo Documentación Técnica Word...
    start Documentacion_Tecnica_GrupoXX.docx
) else (
    echo [!] No se encontró el archivo Documentacion_Tecnica_GrupoXX.docx
)
pause
goto MENU

:OPEN_PDF
cls
if exist "reportes\Informe_GrupLAC_COL0002099.pdf" (
    echo [i] Abriendo Informe Oficial PDF de GISICO...
    start reportes\Informe_GrupLAC_COL0002099.pdf
) else (
    echo [!] No se encontró el informe PDF en reportes\
)
pause
goto MENU

:RUN_TESTS
cls
echo ===============================================================================
echo   Ejecución de Pruebas Unitarias de Estructuras de Datos (TDAs)
echo ===============================================================================
where python >nul 2>&1
if %ERRORLEVEL% equ 0 (
    python src\python\test_tda.py
) else (
    where py >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        py src\python\test_tda.py
    ) else (
        echo [!] Se requiere Python para ejecutar el test runner.
    )
)
echo.
pause
goto MENU
