# helpers_barras.py – Mapa de helpers y flujo modular

## ¿Qué hace cada helper?

- **formato_fechas**: Da formato legible a fechas para etiquetas de eje.
- **get_text_color_for_bg**: Elige color de texto óptimo según fondo.
- **procesar_espaciado**: Calcula parámetros de espaciado y tamaño de barras/figura.
- **cargar_fuentes**: Carga fuentes personalizadas para matplotlib.
- **unir_barras**: Une categorías especiales (izquierda/derecha) en la gráfica.
- **preparar_datos_barras**: Procesa y transforma el DataFrame de entrada, aplica orden, etiquetas, unión, etc.
- **graficar_barras**: Dibuja la gráfica de barras en matplotlib según los datos y configuración.
- **guardar_y_exportar_svg**: (Nuevo) Guarda la figura en SVG y aplica el flujo de exportación/optimización.

## Flujo de la función `barras`

1. **procesar_espaciado**: Ajusta dimensiones y espaciado según kwargs y parámetros.
2. **cargar_fuentes**: Prepara las fuentes necesarias.
3. **preparar_datos_barras**: Convierte el DataFrame y parámetros en un diccionario de datos listo para graficar.
4. **graficar_barras**: Genera la figura y ejes matplotlib.
5. **guardar_y_exportar_svg**: Guarda y exporta el SVG optimizado.
6. **plt.show()**: Muestra la gráfica en pantalla.

## Parámetros obligatorios y opcionales

- **Obligatorio**:
  - `df_wide`: DataFrame de entrada (formato ancho, categorías en filas, series en columnas).

- **Opcionales** (con valor por defecto):
  - `nombre`, `font`, `fontsize_barra`, `fontsize_valor_total`, `bar_height`, `bar_height_override`, `aumenta_ancho_fig`, `aumenta_alto_fig`, `orientacion`, `aumenta_sep_leyenda`, `valor_barra`, `valor_total`, `porcentaje_barra`, `porcentaje_divergente`, `porcentaje_total`, `porcentaje_total_inicio`, `ordenar_por`, `orden`, `quitar_capsula`, `area_min`, `espacio_inicio`, `paleta_colores`, `color_valor_barra`, `agregar_datos`, `asignar_etiquetas`, `grillas`, `leyenda`, `posicion_leyenda`, `union_izquierda`, `union_derecha`, `separar_por_total`, `y_limits`, `nombre_eje_x`, `nombre_eje_y`, `resaltar_etiquetas`, `sustituir_etiquetas`, `porcentaje_abajo`, `orientacion_etiqueta_x`, `altura_min`, `ejeY_negativo_a_positivo`, `capsulas_cero`, `ncol_leyenda`, `output_dir`, `desplazamiento_capsula`, `**kwargs`.

---
