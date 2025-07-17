# Workflow de Colaboración y Generación de Gráficas

## Descripción General

Este sistema implementa un flujo de trabajo completo para que cualquier integrante del equipo pueda generar, editar y entregar visualizaciones de forma ordenada y reproducible.

## Componentes del Sistema

### 1. **workflow_colaborativo.py**
Script principal que coordina todo el flujo de trabajo colaborativo.

### 2. **inicializador_proyecto.py**
Crea la estructura de carpetas y archivos necesarios para cada proyecto.

### 3. **grafico_cli.py**
Interfaz CLI para generación masiva de gráficas con recetas YAML.

### 4. **generador_catalogo.py**
Genera catálogos Excel con información técnica de cada proyecto.

### 5. **svg_cleanup/**
Módulo para optimización automática de SVG para Figma.

### 6. **recetas_centrales/**
Repositorio de recetas YAML centralizadas y versionadas.

## Flujo de Trabajo Completo

### 1. Clonar el entorno base
```bash
git clone [repositorio]
cd graficas_gob/Python/generacion_masiva
```

### 2. Crear un nuevo proyecto
```bash
python workflow_colaborativo.py crear nombre_proyecto --descripcion "Descripción del proyecto"
```

### 3. Ejecutar workflow completo
```bash
python workflow_colaborativo.py workflow nombre_proyecto --datos archivo1.csv archivo2.xlsx --descripcion "Descripción"
```

### 4. Para proyectos existentes

#### Generar gráficas
```bash
python workflow_colaborativo.py generar proyectos/nombre_proyecto
```

#### Generar catálogo
```bash
python workflow_colaborativo.py catalogo proyectos/nombre_proyecto
```

#### Listar proyectos
```bash
python workflow_colaborativo.py listar
```

## Estructura de Proyecto

Cada proyecto se organiza con la siguiente estructura:

```
proyectos/
└── nombre_proyecto/
    ├── input/                  # Archivos de datos de entrada
    │   ├── datos_ejemplo.csv
    │   └── otros_datos.xlsx
    ├── output/                 # Gráficas generadas
    │   ├── grafica1.svg
    │   └── grafica2.svg
    ├── recetas/                # Recetas YAML del proyecto
    │   ├── barras_ejemplo.yaml
    │   └── linea_ejemplo.yaml
    ├── temp/                   # Archivos temporales
    ├── docs/                   # Documentación del proyecto
    ├── config_proyecto.yaml    # Configuración del proyecto
    ├── generar_graficas.py     # Script local para generar gráficas
    ├── generar_catalogo.py     # Script local para generar catálogo
    ├── resumen.xlsx            # Catálogo técnico del proyecto
    └── README.md               # Documentación del proyecto
```

## Pasos Detallados del Workflow

### Paso 1: Inicialización del Proyecto
- Crea la estructura de carpetas
- Copia recetas centrales
- Genera archivos de configuración
- Crea scripts personalizados del proyecto

### Paso 2: Preparación de Datos
- Copia archivos de datos a `input/`
- Valida formatos de datos
- Genera datos de ejemplo si es necesario

### Paso 3: Configuración de Recetas
- Lista recetas disponibles
- Permite seleccionar recetas específicas
- Valida configuración de recetas

### Paso 4: Generación de Gráficas
- Procesa todas las recetas con los datos
- Genera archivos SVG optimizados
- Aplica estilos corporativos

### Paso 5: Optimización SVG
- Aplica limpieza automática de SVG
- Asigna IDs semánticos
- Optimiza para importación en Figma

### Paso 6: Generación de Catálogo
- Crea archivo Excel con información técnica
- Incluye rutas a archivos
- Documenta parámetros usados

### Paso 7: Verificación de Calidad
- Verifica archivos generados
- Calcula métricas de calidad
- Reporta errores encontrados

## Uso del Sistema

### Crear un nuevo proyecto completo
```bash
python workflow_colaborativo.py workflow "Proyecto Q1 2025" \
    --datos input/ventas.csv input/presupuesto.xlsx \
    --descripcion "Análisis de ventas Q1 2025"
```

### Trabajar con proyecto existente
```bash
# Generar gráficas actualizadas
python workflow_colaborativo.py generar proyectos/proyecto_q1_2025

# Actualizar catálogo
python workflow_colaborativo.py catalogo proyectos/proyecto_q1_2025
```

### Listar todos los proyectos
```bash
python workflow_colaborativo.py listar
```

## Archivos Importantes

### config_proyecto.yaml
Configuración específica de cada proyecto:
```yaml
proyecto:
  nombre: "Proyecto Q1 2025"
  fecha_creacion: "2025-01-16 10:30:00"
  descripcion: "Análisis de ventas Q1 2025"
  
configuracion_graficas:
  formato_salida: "svg"
  optimizacion_svg: true
  generar_catalogo: true
```

### resumen.xlsx
Catálogo técnico con hojas:
- **Resumen Proyecto**: Información general
- **Catálogo Gráficas**: Detalles de cada gráfica
- **Datos Entrada**: Información de archivos de datos
- **Metadatos**: Métricas del proyecto

## Recetas Centrales

Las recetas están centralizadas en `recetas_centrales/` y incluyen:

### barras_ejemplo.yaml
```yaml
tipo_grafico: "barras_verticales"
descripcion: "Gráfica de barras verticales básica"
parametros:
  nombre: "barras_ejemplo"
  titulo: "Ejemplo de Barras Verticales"
  columna_categoria: "Categoria"
  columna_valor: "Valor"
```

### linea_ejemplo.yaml
```yaml
tipo_grafico: "linea"
descripcion: "Gráfica de línea simple"
parametros:
  nombre: "linea_ejemplo"
  titulo: "Ejemplo de Línea Temporal"
  columna_x: "Mes"
  columna_y: "Valor"
```

## Integración con Figma

Los archivos SVG generados están optimizados para Figma:
- **IDs semánticos**: `titulo-ventas-2024`, `barra-enero`, `etiqueta-valor`
- **Estructura limpia**: Grupos organizados jerárquicamente
- **Metadatos mínimos**: Archivos ligeros y rápidos
- **Figma-ready**: Procesamiento específico para importación

## Mantenimiento del Sistema

### Actualizar recetas centrales
```bash
# Actualizar desde repositorio central
git pull origin main

# Sincronizar recetas en proyecto existente
cp recetas_centrales/*.yaml proyectos/mi_proyecto/recetas/
```

### Backup de proyectos
```bash
# Respaldar todos los proyectos
tar -czf backup_proyectos.tar.gz proyectos/
```

### Limpieza de archivos temporales
```bash
# Limpiar archivos temporales de todos los proyectos
find proyectos/ -name "temp" -type d -exec rm -rf {} +
```

## Troubleshooting

### Error: "No se encontraron archivos de datos"
- Verificar que los archivos estén en `input/`
- Comprobar formatos soportados: `.csv`, `.xlsx`, `.xls`

### Error: "Receta no encontrada"
- Verificar que la receta esté en `recetas/`
- Comprobar sintaxis YAML
- Validar que el tipo de gráfico sea soportado

### Error: "SVG no optimizado"
- Verificar instalación de SVGO: `npm install -g svgo`
- Verificar instalación de Scour: `pip install scour`
- Comprobar permisos de archivos

## Mejores Prácticas

### Para el Equipo
1. **No modificar recetas centrales** sin coordinación
2. **Usar nombres descriptivos** para proyectos
3. **Mantener datos organizados** en `input/`
4. **Revisar el catálogo Excel** antes de editar
5. **Documentar cambios** en el README del proyecto

### Para Administradores
1. **Versionar recetas centrales** en Git
2. **Hacer backup regular** de proyectos
3. **Monitorear uso de espacio** en disco
4. **Actualizar herramientas** regularmente
5. **Mantener documentación** actualizada

## Soporte

Para problemas técnicos:
1. Revisar logs de error
2. Verificar dependencias instaladas
3. Consultar documentación de componentes
4. Reportar bugs con información detallada

---
*Documentación generada automáticamente - Última actualización: 2025-01-16*
