@echo off
chcp 65001 >nul
title PEA-i — Sistema de Analisis de Investigacion UPC (Windows)

:MENU
cls
echo ===============================================================================
echo   PEA-i: Programa Estadistico de Analisis de Investigacion (UPC)
echo   Universidad Popular del Cesar — Facultad de Ingenieria y Tecnologicas
echo   Asignatura: Estructura de Datos (Taller 2) | Semestre 2026-I
echo   Docente: Ing. Adith Bismarck Perez Orozco
echo   Estudiante: Kovyn B. Mena
echo ===============================================================================
echo.
echo   Bienvenido al lanzador principal para Windows.
echo   Por favor seleccione una opcion para ejecutar:
echo.
echo   [1] Ejecutar Consola Autonoma (Recomendado - Abre al instante sin compilar)
echo   [2] Compilar y Ejecutar en C++17 (Autodetecta g++, MSYS2, Code::Blocks)
echo   [3] Abrir Portal Web Ejecutivo (Visualizador del Hipercubo en navegador)
echo   [4] Ver Documento Tecnico Oficial Word (.docx)
echo   [5] Ver Informe PDF Oficial de Investigacion (GISICO)
echo   [6] Ejecutar Pruebas Unitarias de Estructuras de Datos (TDAs)
echo   [0] Salir
echo.
echo ===============================================================================
set /p OPC="Ingrese el numero de la opcion [0-6]: "

if "%OPC%"=="1" goto RUN_PY
if "%OPC%"=="2" goto RUN_CPP
if "%OPC%"=="3" goto RUN_WEB
if "%OPC%"=="4" goto OPEN_DOCX
if "%OPC%"=="5" goto OPEN_PDF
if "%OPC%"=="6" goto RUN_TESTS
if "%OPC%"=="0" exit /b 0

echo [!] Opcion no valida. Intente nuevamente.
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
    echo [i] Abriendo Documentacion Tecnica Word...
    start Documentacion_Tecnica_GrupoXX.docx
) else (
    echo [!] No se encontro el archivo Documentacion_Tecnica_GrupoXX.docx
)
pause
goto MENU

:OPEN_PDF
cls
if exist "reportes\Informe_GrupLAC_COL0002099.pdf" (
    echo [i] Abriendo Informe Oficial PDF de GISICO...
    start reportes\Informe_GrupLAC_COL0002099.pdf
) else (
    echo [!] No se encontro el informe PDF en reportes\
)
pause
goto MENU

:RUN_TESTS
cls
echo ===============================================================================
echo   Ejecucion de Pruebas Unitarias de Estructuras de Datos (TDAs)
echo ===============================================================================
where python >nul 2>&1
if %ERRORLEVEL% equ 0 (
    python src\python\test_tda.py
) else (
    where py >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        py src\python\test_tda.py
    ) else (
        if exist "C:\msys64\ucrt64\bin\python.exe" (
            C:\msys64\ucrt64\bin\python.exe src\python\test_tda.py
        ) else (
            echo [!] Se requiere Python para ejecutar el test runner.
        )
    )
)
echo.
pause
goto MENU
