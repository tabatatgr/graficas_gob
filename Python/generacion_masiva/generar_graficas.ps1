# Script PowerShell para generación masiva de gráficas
# Uso: .\generar_graficas.ps1 [parámetros]

param(
    [string]$RecetasDir = "recetas",
    [string]$DatosFile = "conteos_por_dependencia.xlsx",
    [string]$OutputDir = "output_cli",
    [string]$RecetaUnica = "",
    [string]$PythonCmd = "python",
    [switch]$Help,
    [string[]]$ArgsExtra = @()
)

# Función para mostrar ayuda
function Show-Help {
    Write-Host ""
    Write-Host "Sistema de Generación Masiva de Gráficas" -ForegroundColor Green
    Write-Host "===========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Uso: .\generar_graficas.ps1 [parámetros]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Parámetros:" -ForegroundColor Cyan
    Write-Host "  -RecetasDir <directorio>    Directorio con archivos YAML (por defecto: recetas)"
    Write-Host "  -DatosFile <archivo>        Archivo de datos Excel/CSV (por defecto: conteos_por_dependencia.xlsx)"
    Write-Host "  -OutputDir <directorio>     Directorio de salida (por defecto: output_cli)"
    Write-Host "  -RecetaUnica <archivo>      Procesar solo una receta específica"
    Write-Host "  -PythonCmd <comando>        Comando Python a usar (por defecto: python)"
    Write-Host "  -Help                       Mostrar esta ayuda"
    Write-Host "  -ArgsExtra <args>           Argumentos adicionales para el CLI"
    Write-Host ""
    Write-Host "Ejemplos:" -ForegroundColor Cyan
    Write-Host "  .\generar_graficas.ps1"
    Write-Host "  .\generar_graficas.ps1 -RecetasDir 'mis_recetas' -OutputDir 'resultados'"
    Write-Host "  .\generar_graficas.ps1 -RecetaUnica 'general.yaml'"
    Write-Host "  .\generar_graficas.ps1 -ArgsExtra '--fontsize_barra','10','--bar_height','0.8'"
    Write-Host ""
}

# Mostrar ayuda si se solicita
if ($Help) {
    Show-Help
    exit 0
}

# Función para verificar si un comando existe
function Test-Command {
    param([string]$Command)
    try {
        & $Command --version | Out-Null
        return $true
    } catch {
        return $false
    }
}

# Función para verificar archivos y directorios
function Test-Prerequisites {
    $errors = @()
    
    # Verificar Python
    if (-not (Test-Command $PythonCmd)) {
        $errors += "Python no está disponible con el comando '$PythonCmd'"
    }
    
    # Verificar CLI
    if (-not (Test-Path "grafico_cli.py")) {
        $errors += "No se encontró el archivo grafico_cli.py"
    }
    
    # Verificar directorio de recetas
    if (-not (Test-Path $RecetasDir)) {
        $errors += "No se encontró el directorio de recetas '$RecetasDir'"
    }
    
    # Verificar archivo de datos
    if (-not (Test-Path $DatosFile)) {
        $errors += "No se encontró el archivo de datos '$DatosFile'"
    }
    
    return $errors
}

# Función principal
function Main {
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Sistema de Generación Masiva de Gráficas" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    
    # Mostrar configuración
    Write-Host "Configuración:" -ForegroundColor Cyan
    Write-Host "- Directorio de recetas: $RecetasDir" -ForegroundColor White
    Write-Host "- Archivo de datos: $DatosFile" -ForegroundColor White
    Write-Host "- Directorio de salida: $OutputDir" -ForegroundColor White
    Write-Host "- Comando Python: $PythonCmd" -ForegroundColor White
    if ($RecetaUnica) {
        Write-Host "- Receta única: $RecetaUnica" -ForegroundColor White
    }
    Write-Host ""
    
    # Verificar prerequisitos
    $errors = Test-Prerequisites
    if ($errors.Count -gt 0) {
        Write-Host "Errores encontrados:" -ForegroundColor Red
        foreach ($error in $errors) {
            Write-Host "  - $error" -ForegroundColor Red
        }
        exit 1
    }
    
    # Construir comando
    $command = @($PythonCmd, "grafico_cli.py")
    $command += @("--recetas-dir", $RecetasDir)
    $command += @("--datos", $DatosFile)
    $command += @("--output", $OutputDir)
    
    if ($RecetaUnica) {
        $command += @("--receta-unica", $RecetaUnica)
    }
    
    if ($ArgsExtra.Count -gt 0) {
        $command += $ArgsExtra
    }
    
    # Mostrar comando a ejecutar
    Write-Host "Ejecutando:" -ForegroundColor Yellow
    Write-Host "  $($command -join ' ')" -ForegroundColor Gray
    Write-Host ""
    
    # Ejecutar comando
    try {
        & $command[0] $command[1..($command.Length-1)]
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "¡Generación completada exitosamente!" -ForegroundColor Green
            Write-Host "Los archivos se guardaron en: $OutputDir" -ForegroundColor Green
            
            # Mostrar resumen de archivos generados
            if (Test-Path $OutputDir) {
                $svgFiles = Get-ChildItem -Path $OutputDir -Filter "*.svg" | Measure-Object
                $pngFiles = Get-ChildItem -Path $OutputDir -Filter "*.png" | Measure-Object
                
                Write-Host ""
                Write-Host "Archivos generados:" -ForegroundColor Cyan
                Write-Host "  - SVG: $($svgFiles.Count)" -ForegroundColor White
                Write-Host "  - PNG: $($pngFiles.Count)" -ForegroundColor White
            }
        } else {
            Write-Host ""
            Write-Host "Error durante la ejecución (código: $LASTEXITCODE)" -ForegroundColor Red
            Write-Host "Verifica los logs anteriores para más detalles." -ForegroundColor Red
            exit $LASTEXITCODE
        }
    } catch {
        Write-Host ""
        Write-Host "Error ejecutando el comando:" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
        exit 1
    }
}

# Ejecutar función principal
Main
