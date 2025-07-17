# Sistema de Generación Masiva de Gráficas

## Descripción General

Este sistema permite generar gráficas de forma masiva usando recetas YAML y una interfaz de línea de comandos (CLI). Está diseñado para facilitar la producción en lote de visualizaciones manteniendo consistencia en estilos corporativos.

## Componentes del Sistema

### 1. **grafico_cli.py**
Interfaz de línea de comandos principal que coordina todo el proceso de generación.

### 2. **funcion_barras.py**
Módulo que contiene la función de generación de gráficas de barras

### 3. **estilos_globales.py**
Configuración centralizada de estilos corporativos y paletas de colores.

### 4. **recetas/** (directorio)
Contiene archivos YAML que definen cada gráfica a generar.

### 5. **generar_graficas.bat**
Script batch para Windows que simplifica el uso del CLI.

## Uso Básico

### Generación de todas las gráficas

```bash
# Usando Python directamente
python grafico_cli.py --recetas-dir recetas --datos.xlsx --output output_cli

# Usando el script batch (Windows)
generar_graficas.bat
```

### Generación de una sola gráfica

```bash
# Usando Python directamente
python grafico_cli.py --recetas-dir recetas --datos conteos_por_dependencia.xlsx --output output_cli --receta-unica general.yaml

# Usando el script batch (Windows)
generar_graficas.bat --receta-unica general.yaml
```

### Parámetros adicionales en línea de comandos

```bash
# Ajustar parámetros específicos sin modificar el YAML
python grafico_cli.py --recetas-dir recetas --datos.xlsx --output output_cli --kwargs fontsize_barra=10 bar_height=0.8

# También funciona con argumentos libres
python grafico_cli.py --recetas-dir recetas --datos.xlsx --output output_cli --fontsize_barra 10 --bar_height 0.8
```

## Estructura de Recetas YAML

### Ejemplo básico de receta

```yaml
# Tipo de gráfica a generar
tipo_grafico: barras_verticales

# Configuración de procesamiento de datos
datos:
  filtros:
    - columna: indicadora
      valor: "General"
      operador: "=="
  
  columnas:
    - Año
    - Acumulado anterior
    - Desaparecidos del periodo
    - Localizados de años anteriores
    - Localizados del periodo
    - Sin año de localización
  
  transformaciones:
    - columna: Localizados de años anteriores
      operacion: negativo
    - columna: Localizados del periodo
      operacion: negativo

# Parámetros específicos de la gráfica
parametros:
  nombre: "dataframe_General"
  bar_height: 0.65
  font: "Montserrat"
  fontsize_barra: 7
  fontsize_valor_total: 15
  valor_barra: true
  valor_total: true
  porcentaje_barra: true
  paleta_colores:
    - "#114a44"
    - "#739489"
    - "#3d5c93"
    - "#7393b3"
    - "#6B5B95"

# Elementos a excluir (opcional)
exclusiones:
  - "leyenda"
  - "grillas"
```

### Secciones de una receta

#### 1. **tipo_grafico**
Especifica qué función de gráfica usar. Actualmente soporta:
- `barras_verticales`

#### 2. **datos** (opcional)
Configuración para procesamiento de datos:

- **filtros**: Lista de filtros a aplicar
  - `columna`: Nombre de la columna
  - `valor`: Valor a filtrar
  - `operador`: Tipo de operación (`==`, `!=`, `in`)

- **columnas**: Lista de columnas a mantener en el DataFrame

- **transformaciones**: Lista de transformaciones a aplicar
  - `columna`: Nombre de la columna
  - `operacion`: Tipo de transformación (`negativo`, `absoluto`, `agregar_ceros`)

#### 3. **parametros**
Todos los parámetros que acepta la función de gráfica. Algunos importantes:

- `nombre`: Nombre base para los archivos de salida
- `font`: Fuente tipográfica
- `fontsize_barra`: Tamaño de fuente para valores en barras
- `fontsize_valor_total`: Tamaño de fuente para valores totales
- `paleta_colores`: Lista de colores hexadecimales
- `bar_height`: Ancho de las barras
- `valor_barra`: Mostrar valores dentro de las barras
- `valor_total`: Mostrar valores totales
- `porcentaje_barra`: Mostrar porcentajes en barras
- `leyenda`: Mostrar leyenda
- `agregar_datos`: Datos adicionales para agregar al DataFrame

#### 4. **exclusiones** (opcional)
Lista de parámetros a excluir del procesamiento.

## Ejemplos de Uso

### Caso 1: Generación básica

```bash
# Generar todas las gráficas definidas en el directorio recetas/
python grafico_cli.py --recetas-dir recetas --datos datos.xlsx --output graficas_finales
```

### Caso 2: Ajuste puntual sin modificar YAML

```bash
# Cambiar el tamaño de fuente para todas las recetas
python grafico_cli.py --recetas-dir recetas --datos datos.xlsx --output graficas_finales --fontsize_barra 12
```

### Caso 3: Generación con múltiples parámetros libres

```bash
# Ajustar varios parámetros simultáneamente
python grafico_cli.py --recetas-dir recetas --datos datos.xlsx --output graficas_finales --bar_height 0.8 --fontsize_barra 10 --fontsize_valor_total 18
```

### Caso 4: Procesamiento de receta individual

```bash
# Procesar solo la receta específica
python grafico_cli.py --recetas-dir recetas --datos datos.xlsx --output graficas_finales --receta-unica mujeres.yaml
```

### Caso 5: Uso con script batch (Windows)

```batch
# Uso básico
generar_graficas.bat

# Con parámetros personalizados
generar_graficas.bat --recetas recetas_especiales --output resultados_2024

# Solo una receta
generar_graficas.bat --receta-unica general.yaml
```

## Control de Calidad

El sistema incluye verificaciones automáticas:

1. **Validación de recetas**: Estructura YAML correcta
2. **Validación de datos**: Archivos de datos accesibles
3. **Verificación de salida**: Archivos generados correctamente
4. **Reporte de errores**: Logs detallados de problemas

### Ejemplo de salida del sistema

```
Cargando datos desde: conteos_por_dependencia.xlsx
Datos cargados: 42 filas, 7 columnas
Encontradas 7 recetas

Procesando: general.yaml
✓ Gráfica generada: dataframe_General

Procesando: mujeres.yaml
✓ Gráfica generada: dataframe_Mujeres

=== Resumen ===
Gráficas exitosas: 6
Gráficas fallidas: 1
Total procesadas: 7

=== Control de Calidad ===
Archivos SVG generados: 6
Archivos PNG generados: 6
✓ Todos los archivos tienen contenido
```

## Ventajas del Sistema

1. **Escalabilidad**: Genera múltiples gráficas en una sola ejecución
2. **Flexibilidad**: Parámetros libres para ajustes puntuales
3. **Consistencia**: Estilos corporativos centralizados
4. **Versionado**: Recetas YAML versionables en repositorios
5. **Automatización**: Integrable en pipelines de CI/CD
6. **Mantenibilidad**: Código modular y reutilizable

## Extensión del Sistema

Para agregar nuevos tipos de gráficas:

1. Crear la función de gráfica en un módulo separado
2. Importarla en `grafico_cli.py`
3. Agregarla al diccionario `self.tipos_grafico`
4. Crear recetas YAML para el nuevo tipo

Ejemplo:
```python
# En grafico_cli.py
from mi_modulo import funcion_scatter

class GraficoCLI:
    def __init__(self):
        self.tipos_grafico = {
            'barras_verticales': barras_verticales,
            'scatter': funcion_scatter,  # Nueva función
        }
```

## Notas Técnicas

- El sistema utiliza pandas para procesamiento de datos
- Matplotlib para generación de gráficas
- PyYAML para lectura de recetas
- Soporte para archivos Excel (.xlsx) y CSV
- Generación automática de archivos SVG y PNG
- Optimización SVG opcional con scour y svgo
