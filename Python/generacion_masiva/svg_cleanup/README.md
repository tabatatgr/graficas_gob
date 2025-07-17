# Flujo de Exportación de Gráficas para Figma

## Descripción General

Este flujo permite convertir visualizaciones generadas automáticamente en gráficos listos para ser editados visualmente en herramientas como Figma, manteniendo la estructura semántica de los elementos y optimizando el archivo para su uso en diseño.

## Proceso Completo

### 1. Generación Inicial
La visualización se genera mediante código (Python) y se exporta en formato SVG. En esta etapa el archivo contiene los elementos estructurales básicos (`<g>`, `<path>`, `<text>`, etc.) pero sin nombres identificables en las capas.

### 2. Optimización SVGO
Se aplica primero la optimización básica con SVGO:
- Elimina atributos redundantes
- Normaliza estilos
- Reduce el tamaño del archivo
- Limpia elementos innecesarios

### 3. Limpieza Scour
Después se aplica la limpieza profunda con Scour:
- Refina la limpieza a nivel de XML
- Elimina metadatos innecesarios
- Ajusta formatos numéricos
- Asegura una salida mínima y coherente

### 4. Asignación Semántica de Capas
**Después de la optimización**, se asignan identificadores (`id`) descriptivos a los elementos clave:

- **Ejes**: `axis-x-1`, `axis-y-1`
- **Barras**: `bar-1`, `bar-2`, `bar-3`
- **Líneas de datos**: `line-1`, `line-plot`
- **Etiquetas**: `label-1`, `label-2`, `tick-3`
- **Áreas**: `area-1`, `area-2`
- **Grupos**: `bars-group`, `labels-group`, `axes-group`

El nombrado se basa en la posición, tipo de elemento y atributos presentes, facilitando su identificación posterior. La jerarquía de grupos (`<g>`) se conserva para mantener la estructura lógica de la visualización.

**¿Por qué la semántica va al final?** 
- Si se agregan IDs semánticos antes de SVGO/Scour, estos pueden ser eliminados o modificados
- Es más eficiente optimizar primero el archivo "sucio" y luego agregar la semántica al archivo ya limpio
- Garantiza que los IDs semánticos persistan en el archivo final

### 5. Compatibilidad con Figma
- Elimina comentarios XML problemáticos
- Asegura que el viewBox esté presente
- Limpia atributos no compatibles con Figma
- Normaliza espacios y formato

### 6. Edición Visual
El archivo SVG optimizado se importa en Figma. Gracias al etiquetado semántico, cada capa aparece claramente identificada en la interfaz de diseño, permitiendo:

- Cambio de tipografías
- Aplicación de colores institucionales
- Ajuste de espaciado
- Adición de anotaciones gráficas
- Modificaciones visuales sin ambigüedad

### 7. Exportación Final
Una vez completada la edición visual, el archivo puede exportarse en el formato requerido (SVG, PDF, PNG de alta resolución) para su integración en reportes, presentaciones, sitios web o redes sociales.

## Uso

### Uso Básico
```python
from svg_cleanup.flujo_exportacion import exportar_grafica

# Exportar una gráfica
resultado = exportar_grafica("mi_grafica.svg", "mi_grafica", "output")
```

### Uso con Wrapper Semántico
```python
from semantic_wrapper import aplicar_flujo_semantico

# Aplicar a cualquier función de gráfico
resultado = aplicar_flujo_semantico(funcion_barras, datos, nombre="mi_grafica")
```

### Uso desde Línea de Comandos
```bash
python svg_cleanup/flujo_exportacion.py mi_grafica.svg mi_grafica output
```

## Requisitos

- **SVGO**: `npm install -g svgo`
- **Scour**: `pip install scour`

## Archivos de Salida

Para cada gráfica procesada se genera:
- `nombre_figma.svg`: Archivo final optimizado para Figma

Los archivos intermedios se eliminan automáticamente para mantener limpio el directorio de salida.

## Ventajas

1. **Flujo unificado**: Un solo script maneja todo el proceso
2. **Etiquetado semántico**: Capas identificables en Figma
3. **Optimización inteligente**: Conserva estructura mientras optimiza
4. **Compatibilidad garantizada**: Probado específicamente con Figma
5. **Automatización completa**: Integrable en flujos de trabajo
6. **Limpieza automática**: No deja archivos temporales
