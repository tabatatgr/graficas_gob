if porcentaje_barra or valor_barra:
    porcentaje_valor = (valor[y_pos] / total_general) * 100
    texto = ""
    if valor_barra:
        texto += f"{valor[y_pos]:,.0f}"
    if porcentaje_barra:
        if valor_barra:
            texto += f" ({porcentaje_valor:.1f}%)"
        else:
            texto += f"{porcentaje_valor:.1f}%"

    # Crear un texto temporal en (0, 0) para medir su ancho
    temp_text = ax.text(0, 0, texto,
                        fontsize=font_config['porcentaje']['size'],
                        fontfamily=font_config['family'],
                        fontweight=font_config['porcentaje']['weight'],
                        va='center', ha='center')
    
    # Forzar el renderizado
    fig.canvas.draw()
    
    # Obtener el ancho en unidades de datos
    bbox = temp_text.get_window_extent()
    bbox_data = ax.transData.inverted().transform_bbox(bbox)
    texto_width = bbox_data.width
    
    # Eliminar el texto temporal
    temp_text.remove()

    # Añadir un margen del 10% para evitar bordes
    if texto_width < valor[y_pos] * 0.9:
        ax.text(left + valor[y_pos] / 2, y_pos, texto,
                va='center', ha='center',
                fontsize=font_config['porcentaje']['size'],
                fontfamily=font_config['family'],
                fontweight=font_config['porcentaje']['weight'],
                color='white')