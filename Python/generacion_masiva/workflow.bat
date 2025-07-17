@echo off
REM Script batch para facilitar el uso del workflow de gráficas en Windows

setlocal enabledelayedexpansion

REM Configuración
set PYTHON_CMD=python
set SCRIPT_DIR=%~dp0
set WORKFLOW_SCRIPT=%SCRIPT_DIR%workflow_colaborativo.py

REM Función para mostrar ayuda
if "%1"=="help" goto :help
if "%1"=="/?" goto :help
if "%1"=="" goto :help

REM Función para crear nuevo proyecto
if "%1"=="crear" (
    if "%2"=="" (
        echo Error: Especifica el nombre del proyecto
        echo Uso: %0 crear nombre_proyecto [descripcion]
        exit /b 1
    )
    
    set PROYECTO_NOMBRE=%2
    set DESCRIPCION=%3
    
    echo Creando proyecto: !PROYECTO_NOMBRE!
    if not "!DESCRIPCION!"=="" (
        %PYTHON_CMD% "%WORKFLOW_SCRIPT%" crear "!PROYECTO_NOMBRE!" --descripcion "!DESCRIPCION!"
    ) else (
        %PYTHON_CMD% "%WORKFLOW_SCRIPT%" crear "!PROYECTO_NOMBRE!"
    )
    
    if !errorlevel! equ 0 (
        echo.
        echo ✓ Proyecto creado exitosamente
        echo.
        echo Próximos pasos:
        echo 1. Colocar archivos de datos en proyectos/!PROYECTO_NOMBRE!/input/
        echo 2. Ejecutar: %0 generar !PROYECTO_NOMBRE!
        echo 3. Revisar catálogo: %0 catalogo !PROYECTO_NOMBRE!
    )
    
    exit /b !errorlevel!
)

REM Función para workflow completo
if "%1"=="workflow" (
    if "%2"=="" (
        echo Error: Especifica el nombre del proyecto
        echo Uso: %0 workflow nombre_proyecto archivo_datos [descripcion]
        exit /b 1
    )
    
    if "%3"=="" (
        echo Error: Especifica el archivo de datos
        echo Uso: %0 workflow nombre_proyecto archivo_datos [descripcion]
        exit /b 1
    )
    
    set PROYECTO_NOMBRE=%2
    set ARCHIVO_DATOS=%3
    set DESCRIPCION=%4
    
    echo Ejecutando workflow completo para: !PROYECTO_NOMBRE!
    echo Archivo de datos: !ARCHIVO_DATOS!
    
    if not "!DESCRIPCION!"=="" (
        %PYTHON_CMD% "%WORKFLOW_SCRIPT%" workflow "!PROYECTO_NOMBRE!" --datos "!ARCHIVO_DATOS!" --descripcion "!DESCRIPCION!"
    ) else (
        %PYTHON_CMD% "%WORKFLOW_SCRIPT%" workflow "!PROYECTO_NOMBRE!" --datos "!ARCHIVO_DATOS!"
    )
    
    exit /b !errorlevel!
)

REM Función para generar gráficas
if "%1"=="generar" (
    if "%2"=="" (
        echo Error: Especifica el nombre del proyecto
        echo Uso: %0 generar nombre_proyecto
        exit /b 1
    )
    
    set PROYECTO_NOMBRE=%2
    set PROYECTO_DIR=proyectos\!PROYECTO_NOMBRE!
    
    if not exist "!PROYECTO_DIR!" (
        echo Error: Proyecto no encontrado: !PROYECTO_DIR!
        exit /b 1
    )
    
    echo Generando gráficas para: !PROYECTO_NOMBRE!
    %PYTHON_CMD% "%WORKFLOW_SCRIPT%" generar "!PROYECTO_DIR!"
    
    exit /b !errorlevel!
)

REM Función para generar catálogo
if "%1"=="catalogo" (
    if "%2"=="" (
        echo Error: Especifica el nombre del proyecto
        echo Uso: %0 catalogo nombre_proyecto
        exit /b 1
    )
    
    set PROYECTO_NOMBRE=%2
    set PROYECTO_DIR=proyectos\!PROYECTO_NOMBRE!
    
    if not exist "!PROYECTO_DIR!" (
        echo Error: Proyecto no encontrado: !PROYECTO_DIR!
        exit /b 1
    )
    
    echo Generando catálogo para: !PROYECTO_NOMBRE!
    %PYTHON_CMD% "%WORKFLOW_SCRIPT%" catalogo "!PROYECTO_DIR!"
    
    exit /b !errorlevel!
)

REM Función para listar proyectos
if "%1"=="listar" (
    echo Listando proyectos disponibles...
    %PYTHON_CMD% "%WORKFLOW_SCRIPT%" listar
    exit /b !errorlevel!
)

REM Función para abrir proyecto
if "%1"=="abrir" (
    if "%2"=="" (
        echo Error: Especifica el nombre del proyecto
        echo Uso: %0 abrir nombre_proyecto
        exit /b 1
    )
    
    set PROYECTO_NOMBRE=%2
    set PROYECTO_DIR=proyectos\!PROYECTO_NOMBRE!
    
    if not exist "!PROYECTO_DIR!" (
        echo Error: Proyecto no encontrado: !PROYECTO_DIR!
        exit /b 1
    )
    
    echo Abriendo proyecto: !PROYECTO_NOMBRE!
    explorer "!PROYECTO_DIR!"
    exit /b 0
)

REM Si no se reconoce el comando
echo Error: Comando no reconocido: %1
echo Usa '%0 help' para ver comandos disponibles
exit /b 1

:help
echo.
echo ==========================================
echo   WORKFLOW DE GRÁFICAS - SISTEMA CLI
echo ==========================================
echo.
echo Comandos disponibles:
echo.
echo   %0 crear PROYECTO [DESCRIPCION]
echo     Crea un nuevo proyecto con la estructura completa
echo.
echo   %0 workflow PROYECTO ARCHIVO_DATOS [DESCRIPCION]
echo     Ejecuta el workflow completo (crear + generar + catalogo)
echo.
echo   %0 generar PROYECTO
echo     Genera gráficas para un proyecto existente
echo.
echo   %0 catalogo PROYECTO
echo     Genera catálogo Excel para un proyecto existente
echo.
echo   %0 listar
echo     Lista todos los proyectos disponibles
echo.
echo   %0 abrir PROYECTO
echo     Abre la carpeta del proyecto en el explorador
echo.
echo   %0 help
echo     Muestra esta ayuda
echo.
echo Ejemplos:
echo.
echo   %0 crear "Ventas Q1 2025" "Análisis de ventas del primer trimestre"
echo   %0 workflow "Ventas Q1 2025" datos.csv "Análisis de ventas"
echo   %0 generar "Ventas Q1 2025"
echo   %0 catalogo "Ventas Q1 2025"
echo   %0 listar
echo   %0 abrir "Ventas Q1 2025"
echo.
echo ==========================================
goto :eof
