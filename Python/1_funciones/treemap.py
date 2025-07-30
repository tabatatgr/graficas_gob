from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib import font_manager
import squarify 
import pandas as pd
import random

from funciones import limpiar_svg_con_scour 
from funciones import get_text_color_for_bg 
from funciones import exportar_grafica

import textwrap
def wrap_text(text, ax, fig, max_width, fontsize, fontweight):
    if ' ' not in text:
        return text
    for width in range(len(text), 1, -1):
        candidate = '\n'.join(textwrap.wrap(text, width=width, break_long_words=False))
        t = ax.text(0, 0, candidate, fontsize=fontsize, fontweight=fontweight)
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        bbox = t.get_window_extent(renderer=renderer)
        inv = ax.transData.inverted()
        bbox_data = inv.transform(bbox)
        text_width = bbox_data[1][0] - bbox_data[0][0]
        t.remove()
        if text_width <= max_width:
            return candidate
    # Fuerza una palabra por línea si nada cabe
    candidate = '\n'.join(textwrap.wrap(text, width=1, break_long_words=False))
    return candidate


# Función para ajustar el tamaño de fuente para que el texto no se salga del rectángulo
def ajustar_fontsize(ax, fig, texto, max_width, base_size, fontweight):
    fontsize = base_size
    t = ax.text(0, 0, texto, fontsize=fontsize, fontweight=fontweight)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    bbox = t.get_window_extent(renderer=renderer)
    inv = ax.transData.inverted()
    bbox_data = inv.transform(bbox)
    text_width = bbox_data[1][0] - bbox_data[0][0]
    t.remove()
    while text_width > max_width and fontsize > 6:
        fontsize -= 1
        t = ax.text(0, 0, texto, fontsize=fontsize, fontweight=fontweight)
        fig.canvas.draw()
        bbox = t.get_window_extent(renderer=renderer)
        bbox_data = inv.transform(bbox)
        text_width = bbox_data[1][0] - bbox_data[0][0]
        t.remove()
    return fontsize

# def calcular_fontsize(area, base, ajusta_tam_letra):
#     base = base * ajusta_tam_letra  
#     if area > 0.08:
#         return base
#     elif area > 0.06:
#         return int(base * 20 / 26)
#     elif area > 0.04:
#         return int(base * 18 / 26)
#     elif area > 0.02:
#         return int(base * 14 / 26)
#     elif area > 0.01:
#         return int(base * 11 / 26)
#     elif area > 0.005:
#         return int(base * 9 / 26)
#     else:
#         return int(base * 5 / 26)

# def calcular_fontsize(area, base, ajusta_tam_letra):
#     base = base * ajusta_tam_letra  
#     if area > 0.08:
#         return base
#     elif area > 0.06:
#         return int(base * 20 / 26)
#     elif area > 0.04:
#         return int(base * 18 / 26)
#     elif area > 0.03:
#         return int(base * 16 / 26)
#     elif area > 0.02:
#         return int(base * 14 / 26)
#     elif area > 0.015:
#         return int(base * 12 / 26)
#     elif area > 0.01:
#         return int(base * 11 / 26)
#     elif area > 0.008:
#         return int(base * 10 / 26)
#     elif area > 0.006:
#         return int(base * 9 / 26)
#     elif area > 0.005:
#         return int(base * 8 / 26)
#     elif area > 0.004:
#         return int(base * 7 / 26)
#     elif area > 0.003:
#         return int(base * 6 / 26)
#     elif area > 0.002:
#         return int(base * 5 / 26)
#     elif area > 0.0015:
#         return int(base * 4 / 26)
#     elif area > 0.001:
#         return int(base * 3 / 26)
#     elif area > 0.0007:
#         return int(base * 2.5 / 26)
#     elif area > 0.0005:
#         return int(base * 2 / 26)
#     elif area > 0.0003:
#         return int(base * 1.5 / 26)
#     elif area > 0.0001:
#         return int(base * 1 / 26)
#     else:
#         return int(base * 0.7 / 26)

def calcular_fontsize(area, base, ajusta_tam_letra):
    base = base * ajusta_tam_letra  
    if area > 0.08:
        return base
    elif area > 0.06:
        return int(base * 20 / 26)
    elif area > 0.04:
        return int(base * 24 / 26)  
    elif area > 0.03:
        return int(base * 16 / 26)
    elif area > 0.02:
        return int(base * 14 / 26)
    elif area > 0.015:
        return int(base * 12 / 26)
    elif area > 0.01:
        return int(base * 11 / 26)
    elif area > 0.008:
        return int(base * 10 / 26)
    elif area > 0.006:
        return int(base * 9 / 26)
    elif area > 0.005:
        return int(base * 4.5 / 26)  
    elif area > 0.003:
        return int(base * 5 / 26)
    elif area > 0.002:
        return int(base * 4 / 26)
    elif area > 0.0015:
        return int(base * 3 / 26)
    elif area > 0.001:
        return int(base * 2.2 / 26)
    elif area > 0.0007:
        return int(base * 1.5 / 26)
    elif area > 0.0005:
        return int(base * 1.1 / 26)
    elif area > 0.0003:
        return int(base * 0.8 / 26)
    elif area > 0.00015:
        return int(base * 0.6 / 26)
    elif area > 0.00007:
        return int(base * 0.45 / 26)
    else:
        return int(base * 0.3 / 26)
    

def treemap(victimas_por_entidad, 
            nombre=None, 
            area_min=0.001, 
            tipo_letra='Montserrat',
            fontsize_etiqueta=26, 
            fontsize_valor=26, 
            fontsize_porcentaje=26,
            paleta_colores=None,
            porce_parentesis=False,
            ancho_fig=16,        
            alto_fig=10, 
            color_borde_rec="white",
            ancho_borde_rec=1,
            ajusta_sep_valor=0.18,
            ajusta_tam_letra=1.0,
            ajusta_posY_texto=0.5,
            ):

    # Configuración de fuentes y colores
    font_config = {
        'family': tipo_letra,
        'etiquetas': {'size': fontsize_etiqueta, 'weight': 'bold', 'color': '#ffffff'},
        'valor': {'size': fontsize_valor, 'weight': 'bold', 'color': '#ffffff'},
        'porcentaje': {'size': fontsize_porcentaje, 'weight': 'medium', 'color': '#ffffff'}
    }

   # Configuración para que el texto en SVG sea editable.
    plt.rcParams['svg.fonttype'] = 'none'
    # Carga de fuentes personalizadas desde la carpeta de fuentes.
    font_dirs = [Path("../0_fonts")]
    font_files = font_manager.findSystemFonts(fontpaths=font_dirs)
    for font_file in font_files:
        font_manager.fontManager.addfont(font_file)
    plt.rc('font', family=tipo_letra)  # Aplica la fuente a toda la gráfica


    # Asegurar que todos los valores sean numéricos tipo float
    victimas_por_entidad['NUMERO DE VICTIMAS'] = pd.to_numeric(
        victimas_por_entidad['NUMERO DE VICTIMAS'], errors='coerce'
    ).fillna(0).astype(float)

    # Ordenar y calcular porcentaje
    df = victimas_por_entidad.sort_values(by='NUMERO DE VICTIMAS', ascending=False).copy()
    total_nacional = df['NUMERO DE VICTIMAS'].sum()
    df['Porcentaje'] = (df['NUMERO DE VICTIMAS'] / total_nacional * 100).round(1)

    # --- Colores por paleta_colores ---
    n = len(df)
    if paleta_colores is None:
        paleta_colores = ['#10302C', '#4C6A67', '#9B2247', '#9D792A', '#D5B162', '#767676']
    colores = list(paleta_colores[:n])  # Usa solo los colores dados, sin repetir
    if len(colores) < n:
        # Si faltan colores, agrega aleatorios
        for _ in range(n - len(colores)):
            color_rand = "#{:06x}".format(random.randint(0, 0xFFFFFF))
            colores.append(color_rand)

    # Configurar la figura
    plt.rc('font', family=font_config['family'])
    fig, ax = plt.subplots(figsize=(ancho_fig, alto_fig), dpi=300)
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    ax.axis('off')  # <-- Oculta los ejes y los números

    # rectangulos
    sizes = df['NUMERO DE VICTIMAS'].tolist()
    rectangles = squarify.normalize_sizes(sizes, 1, 1)
    rectangles = squarify.squarify(rectangles, 0, 0, 1, 1)

    for rect, (_, row), color in zip(rectangles, df.iterrows(), colores):
        x, y, dx, dy = rect['x'], rect['y'], rect['dx'], rect['dy']

        ax.add_patch(plt.Rectangle(
            (x, y), dx, dy,
            facecolor=color,
            edgecolor=color_borde_rec,
            linewidth=ancho_borde_rec  
        ))

        area = dx * dy

        if area > area_min:
            entidad = row['ENTIDAD FEDERATIVA']
            entidad_mod = entidad

            # Ajuste de tamaño de fuente siempre proporcional al área
            fontsize_et = calcular_fontsize(area, fontsize_etiqueta, ajusta_tam_letra)
            fontsize_val = calcular_fontsize(area, fontsize_valor, ajusta_tam_letra)
            fontsize_pct = calcular_fontsize(area, fontsize_porcentaje, ajusta_tam_letra)

            # --- DEBUG: Imprime área, tamaño de letra y etiqueta ---
            print(f"[DEBUG] Área: {area:.6f} | Etiqueta: '{entidad_mod}' | FontSize: {fontsize_et}")


            x_text = x + dx * 0.04
            y_text = y + dy * 0.55
            y_text2 = y_text - dy * ajusta_sep_valor  # <-- usa el nuevo argumento
            y_text3 = y_text2 - dy * ajusta_sep_valor  # <-- usa el nuevo argumento

            color_texto = get_text_color_for_bg(color)

            max_text_width = dx * 0.92
            max_valor_width = dx * 0.92

            # 1. Primer wrap y ajuste de tamaño
            entidad_mod_wrapped = wrap_text(entidad_mod, ax, fig, max_text_width, fontsize_et, font_config['etiquetas']['weight'])
            fontsize_et_ajustado = ajustar_fontsize(ax, fig, entidad_mod_wrapped, max_text_width, fontsize_et, font_config['etiquetas']['weight'])

            valor_y_porcentaje = f"{int(row['NUMERO DE VICTIMAS']):,} ({row['Porcentaje']}%)"
            valor_y_porcentaje_wrapped = wrap_text(valor_y_porcentaje, ax, fig, max_valor_width, fontsize_val, font_config['valor']['weight'])
            fontsize_val_ajustado = ajustar_fontsize(ax, fig, valor_y_porcentaje_wrapped, max_valor_width, fontsize_val, font_config['valor']['weight'])

            # 2. Usa el tamaño más pequeño para ambos textos
            fontsize_final = min(fontsize_et_ajustado, fontsize_val_ajustado)

            # 3. Vuelve a aplicar wrap_text con el tamaño final
            entidad_mod_wrapped_final = wrap_text(entidad_mod, ax, fig, max_text_width, fontsize_final, font_config['etiquetas']['weight'])
            valor_y_porcentaje_wrapped_final = wrap_text(valor_y_porcentaje, ax, fig, max_valor_width, fontsize_final, font_config['valor']['weight'])

            # Dibuja la etiqueta y obtiene el objeto de texto
            text_obj = ax.text(
                x + dx/2,
                y + dy * ajusta_posY_texto,  # <--- usa el nuevo argumento para ajustar la posición vertical
                entidad_mod_wrapped_final,
                ha='center',
                va='center',
                fontsize=fontsize_final,
                fontweight=font_config['etiquetas']['weight'],
                color=color_texto,
                zorder=10,
            )

            # Calcula la posición real de la parte inferior del texto de la etiqueta
            fig.canvas.draw()
            renderer = fig.canvas.get_renderer()
            bbox = text_obj.get_window_extent(renderer=renderer)
            inv = ax.transData.inverted()
            bbox_data = inv.transform(bbox)
            etiqueta_bottom = bbox_data[0][1]  # y mínimo (parte inferior del texto)

            # Calcula la posición del valor justo debajo de la última línea de la etiqueta
            y_valor = etiqueta_bottom - dy * ajusta_sep_valor

            # Dibuja el valor y porcentaje debajo de la etiqueta
            ax.text(
                x + dx/2,
                y_valor,
                valor_y_porcentaje_wrapped_final,
                ha='center',
                va='top',
                fontsize=fontsize_final,
                fontweight=font_config['valor']['weight'],
                color=color_texto,
                zorder=10,
            )


    # # Dibuja el borde externo del treemap
    ax.add_patch(
        plt.Rectangle(
            (0, 0), 1, 1,
            fill=False,
            edgecolor=color_borde_rec,
            linewidth=ancho_borde_rec,
            zorder=20,
            clip_on=False  
        )
    )
    plt.tight_layout()

    exportar_grafica(nombre or "treemap", limpiar_svg_con_scour)
    plt.show()