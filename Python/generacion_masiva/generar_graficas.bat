@echo off
REM Script batch para generar gráficas usando el sistema CLI
REM Uso: generar_graficas.bat [opciones]

setlocal enabledelayedexpansion

REM Configuración por defecto
set RECETAS_DIR=recetas
set DATOS_FILE=conteos_por_dependencia.xlsx
set OUTPUT_DIR=output_cli
set PYTHON_CMD=python

REM Verificar si Python está disponible
%PYTHON_CMD% --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python no está disponible en el PATH
    echo Por favor, instala Python o agrégalo al PATH del sistema
    exit /b 1
)

REM Verificar si el archivo CLI existe
if not exist "grafico_cli.py" (
    echo Error: No se encontró el archivo grafico_cli.py
    echo Asegúrate de estar en el directorio correcto
    exit /b 1
)

REM Mostrar ayuda si se solicita
if "%1"=="--help" goto :help
if "%1"=="-h" goto :help
if "%1"=="/?" goto :help

REM Procesar argumentos
:parse_args
if "%1"=="" goto :execute
if "%1"=="--recetas" (
    set RECETAS_DIR=%2
    shift
    shift
    goto :parse_args
)
if "%1"=="--datos" (
    set DATOS_FILE=%2
    shift
    shift
    goto :parse_args
)
if "%1"=="--output" (
    set OUTPUT_DIR=%2
    shift
    shift
    goto :parse_args
)
if "%1"=="--receta-unica" (
    set RECETA_UNICA=%2
    shift
    shift
    goto :parse_args
)
REM Para argumentos adicionales, los conservamos
set ARGS_EXTRA=%ARGS_EXTRA% %1
shift
goto :parse_args

:execute
echo ========================================
echo Sistema de Generación Masiva de Gráficas
echo ========================================
echo.
echo Configuración:
echo - Directorio de recetas: %RECETAS_DIR%
echo - Archivo de datos: %DATOS_FILE%
echo - Directorio de salida: %OUTPUT_DIR%
if defined RECETA_UNICA echo - Receta única: %RECETA_UNICA%
echo.

REM Verificar que existe el directorio de recetas
if not exist "%RECETAS_DIR%" (
    echo Error: No se encontró el directorio de recetas '%RECETAS_DIR%'
    exit /b 1
)

REM Verificar que existe el archivo de datos
if not exist "%DATOS_FILE%" (
    echo Error: No se encontró el archivo de datos '%DATOS_FILE%'
    exit /b 1
)

REM Crear comando Python
set PYTHON_COMMAND=%PYTHON_CMD% grafico_cli.py --recetas-dir "%RECETAS_DIR%" --datos "%DATOS_FILE%" --output "%OUTPUT_DIR%"

if defined RECETA_UNICA (
    set PYTHON_COMMAND=%PYTHON_COMMAND% --receta-unica "%RECETA_UNICA%"
)

if defined ARGS_EXTRA (
    set PYTHON_COMMAND=%PYTHON_COMMAND% %ARGS_EXTRA%
)

echo Ejecutando: %PYTHON_COMMAND%
echo.

REM Ejecutar el comando
%PYTHON_COMMAND%

if errorlevel 1 (
    echo.
    echo Error durante la ejecución. Verifica los logs anteriores.
    exit /b 1
) else (
    echo.
    echo ¡Generación completada exitosamente!
    echo Los archivos se guardaron en: %OUTPUT_DIR%
)

goto :end

:help
echo.
echo Sistema de Generación Masiva de Gráficas
echo.
echo Uso: generar_graficas.bat [opciones]
echo.
echo Opciones:
echo   --recetas DIR       Directorio con archivos YAML de recetas (por defecto: recetas)
echo   --datos ARCHIVO     Archivo de datos Excel/CSV (por defecto: conteos_por_dependencia.xlsx)
echo   --output DIR        Directorio de salida (por defecto: output_cli)
echo   --receta-unica YAML Procesar solo una receta específica
echo   --help, -h, /?      Mostrar esta ayuda
echo.
echo Ejemplos:
echo   generar_graficas.bat
echo   generar_graficas.bat --recetas mis_recetas --output resultados
echo   generar_graficas.bat --receta-unica general.yaml
echo   generar_graficas.bat --kwargs fontsize_barra=10 bar_height=0.8
echo.
echo Parámetros adicionales se pasan directamente al CLI de Python.

:end
endlocal
