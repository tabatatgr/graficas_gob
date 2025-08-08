from pathlib import Path
from adjustText import adjust_text
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.font_manager as font_manager
import subprocess
import pandas as pd
import os

from funciones import limpiar_svg_con_scour, formato_fechas

def multilineal(
    df_long, 
    nombre_df="multilineal",
    font='Arial',
    tipografia=None,
    margen=0.7,
    orientacion_etiqu_ejeX=None,  
    ancho_fig=None,
    alto_fig=None,
    sustituir_etiquetas_ejeY=None,
    y_limits=None,
    variable_x_size=24,
    variable_x_weight='semibold',
    variable_x_color='#767676',
    variable_y_size=24,
    variable_y_weight='medium',
    variable_y_color='#767676',
    capsula_valor_size=12,
    capsula_valor_weight='medium',
    capsula_valor_color='#ffffff',
    leyenda_size=20,
    leyenda_weight='medium',
    leyenda_color='#767676',
    leyenda_final=False,
    leyenda=False,
    ncol_leyenda=None, 
    ajusta_pos_leyenda_final=0.0,
    ajusta_pos_tag_final=0.0, 
    ajusta_sep_tag_final=0.0, 
    decimales_capsu=0,
    puntos=True,
    sin_tag=2,
    arrowprops=dict(arrowstyle='-', color='gray', lw=0.5),
    force_text=(150, 150),
    expand_points=(150, 150),
    expand_text=(150, 150),
    only_move={'points': 'y', 'text': 'y'},
    autoalign='y',
    lim=1000,
    tag_final=True,
    tag_max=True,
    paleta_colores=None,
    pos_leyenda=(0.5, 1.2), 
    muestra_etiquetas=None,
):
    # Validar columnas
    if df_long.shape[1] != 3:
        raise ValueError("El DataFrame debe tener exactamente 3 columnas: fecha, variable y valor (en ese orden).")

    # Asignar nombres automáticos
    columna_fecha = df_long.columns[0]
    columna_variable = df_long.columns[1]
    columna_valor = df_long.columns[2]

    font_config = {
        'family': font,
        'variable_x': {'size': variable_x_size, 'weight': variable_x_weight, 'color': variable_x_color},
        'variable_y': {'size': variable_y_size, 'weight': variable_y_weight, 'color': variable_y_color},
        'capsula_valor': {'size': capsula_valor_size, 'weight': capsula_valor_weight, 'color': capsula_valor_color},
        'leyenda': {'size': leyenda_size, 'weight': leyenda_weight, 'color': leyenda_color}
    }

    plt.rcParams['svg.fonttype'] = 'none'
    font_dirs = [Path("../0_fonts")]
    font_files = font_manager.findSystemFonts(fontpaths=font_dirs)
    for font_file in font_files:
        font_manager.fontManager.addfont(font_file)

    # --- Ajuste de tamaño de figura ---
    if ancho_fig is not None and alto_fig is not None:
        fig, ax = plt.subplots(figsize=(ancho_fig, alto_fig))
    else:
        ancho_px = 1480
        alto_px = 520
        dpi = 100
        ancho_in = ancho_px / dpi
        alto_in = alto_px / dpi
        fig, ax = plt.subplots(figsize=(ancho_in, alto_in), dpi=dpi)

    variables = df_long[columna_variable].unique()
    if paleta_colores is not None:
        colores_asignados = paleta_colores
    else:
        colores_asignados = ["#006157", "#767676", "#671435", "#9B2247", "#9D792A", "#D5B162"]
    color_map = {var: colores_asignados[i % len(colores_asignados)] for i, var in enumerate(variables)}

    # Graficar todas las líneas y puntos primero
    for i, var in enumerate(variables):
        datos = df_long[df_long[columna_variable] == var]
        ax.plot(
            datos[columna_fecha],
            datos[columna_valor],
            label=var,
            color=color_map[var],
            linewidth=2
        )
        if puntos:
            ax.scatter(
                datos[columna_fecha],
                datos[columna_valor],
                color=color_map[var],
                s=40,
                zorder=3
            )

    # Calcular la escala global para el offset de etiquetas
    escala = df_long[columna_valor].max() - df_long[columna_valor].min()

    # Calcular la coordenada X máxima global para alinear todas las etiquetas finales
    if tag_final == 'derecha':
        x_final_global = df_long[columna_fecha].max()

    all_texts = []
    tag_final_texts = []  # Para guardar referencias a las etiquetas finales
    for i, var in enumerate(variables):
        datos = df_long[df_long[columna_variable] == var].reset_index(drop=True)
        total_puntos = len(datos)
        max_index = datos[columna_valor].idxmax()
        color = color_map[var]
        bbox_props = dict(
            boxstyle="round,pad=0.25,rounding_size=0.99", 
            fc=color,
            ec='#ffffff', 
            lw=margen, 
            alpha=1.0
        )
        espacio = "\u00A0"
        va = 'bottom'
        escala = df_long[columna_valor].max() - df_long[columna_valor].min()
        offset = abs(escala) * 0.03 if escala else 10
        for j, row in datos.iterrows():
            # Si muestra_etiquetas está definido, solo mostrar en esos índices
            if muestra_etiquetas is not None:
                mostrar_etiqueta = j in muestra_etiquetas
            else:
                mostrar_etiqueta = (total_puntos - j - 1) % (sin_tag + 1) == 0

            tiene_etiqueta = mostrar_etiqueta
            es_ultimo = (j == total_puntos - 1) and (tag_final is True)
            es_maximo = (j == max_index) and tag_max
            if (tiene_etiqueta or es_ultimo or es_maximo) and not (tag_final == 'derecha' and j == total_puntos - 1):
                valor_capsula = f"{row[columna_valor]:,.{decimales_capsu}f}"
                all_texts.append(
                    plt.text(
                        row[columna_fecha],
                        row[columna_valor] + offset,
                        f"{espacio*1}{valor_capsula}{espacio*1}",
                        fontsize=font_config['capsula_valor']['size'],
                        color=font_config['capsula_valor']['color'],
                        weight=font_config['capsula_valor']['weight'],
                        ha='center',
                        va=va,
                        bbox=bbox_props,
                        fontname=font_config['family']
                    )
                )
        # Etiqueta final a la derecha, alineada para todas las líneas
        if tag_final == 'derecha':
            y_final = datos[columna_valor].iloc[-1]
            valor_capsula = f"{y_final:,.{decimales_capsu}f}"
            desplazamiento_tag = 0.2 + ajusta_pos_tag_final  # Usa el argumento para ajustar
            if pd.api.types.is_numeric_dtype(df_long[columna_fecha]):
                x_pos = x_final_global + desplazamiento_tag
            else:
                x_pos = x_final_global
            txt_tag = plt.text(
                x_pos,
                y_final,
                f"{espacio*1}{valor_capsula}{espacio*1}",
                fontsize=font_config['capsula_valor']['size'],
                color=font_config['capsula_valor']['color'],
                weight=font_config['capsula_valor']['weight'],
                ha='left',
                va='center',
                bbox=bbox_props,
                fontname=font_config['family']
                )
            all_texts.append(txt_tag)
            tag_final_texts.append(txt_tag)

    # Ajusta todas las etiquetas juntas
    adjust_text(
        all_texts,
        arrowprops=arrowprops,
        force_text=force_text,
        expand_points=expand_points,
        expand_text=expand_text,
        only_move=only_move,
        autoalign=autoalign,
        lim=lim,
    )

    # Si tag_final == 'derecha', forzar alineación X de las etiquetas finales
    if tag_final == 'derecha':
        for txt in tag_final_texts:
            pos = txt.get_position()
            # Solo sumar desplazamiento si el eje X es numérico
            if pd.api.types.is_numeric_dtype(df_long[columna_fecha]):
                txt.set_position((x_final_global + desplazamiento_tag, pos[1]))
            else:
                txt.set_position((x_final_global, pos[1]))

    # Si tag_final == 'derecha' y leyenda_final, extraer las coordenadas Y ajustadas
    if tag_final == 'derecha' and leyenda_final:
        y_coords = [txt.get_position()[1] for txt in tag_final_texts]
    else:
        y_coords = None

    # Etiquetas y formato para el eje x (acepta fechas o enteros)
    valores_x = df_long[columna_fecha].unique()
    if pd.api.types.is_integer_dtype(df_long[columna_fecha]):
        etiquetas_x = [str(x) for x in valores_x]
    else:
        etiquetas_x = formato_fechas(valores_x)

    # Determinar rotación según orientacion_etiqu_ejeX
    if orientacion_etiqu_ejeX == "vertical":
        rotation = 90
    elif orientacion_etiqu_ejeX == "diagonal":
        rotation = 45
    else:  # 'horizontal' o None
        rotation = 0

    # Aplicar límites del eje y si se especifican
    if y_limits is not None:
        ax.set_ylim(y_limits)

    # Etiquetas y formato para el eje y
    if sustituir_etiquetas_ejeY is not None:
        min_tick = ax.get_ylim()[0]
        max_tick = ax.get_ylim()[1]
        n_etiquetas = len(sustituir_etiquetas_ejeY)
        def y_formatter(x, _):
            idx = int(round((x - min_tick) / (max_tick - min_tick) * (n_etiquetas - 1)))
            if 0 <= idx < n_etiquetas:
                return sustituir_etiquetas_ejeY[idx]
            return ""
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(y_formatter))
    else:
        # Mostrar decimales solo si el rango es menor a 1, si no, mostrar enteros
        y_min, y_max = ax.get_ylim()
        if abs(y_max - y_min) < 1:
            ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.2f}"))
        else:
            ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))

    plt.xticks(
        ticks=valores_x,
        labels=etiquetas_x,
        rotation=rotation,
        fontsize=font_config['variable_x']['size'],
        weight=font_config['variable_x']['weight'],
        color=font_config['variable_x']['color'],
        fontname=font_config['family']  
    )
    plt.yticks(
        fontsize=font_config['variable_y']['size'],
        weight=font_config['variable_y']['weight'],
        color=font_config['variable_y']['color'],
        fontname=font_config['family'] 
    )

    if leyenda_final:
        leyenda_texts = []
        for i, var in enumerate(variables):
            datos = df_long[df_long[columna_variable] == var]
            x_final = datos[columna_fecha].iloc[-1]
            # Si tag_final es 'derecha' y leyenda_final, usar el mismo Y que la etiqueta final ajustada
            if tag_final == 'derecha' and y_coords is not None:
                y_final = y_coords[i]
                # Aplica el ajuste horizontal aquí
                x_final_ajustado = x_final + ajusta_pos_leyenda_final if pd.api.types.is_numeric_dtype(df_long[columna_fecha]) else x_final
            else:
                y_final = datos[columna_valor].iloc[-1]
                x_final_ajustado = x_final + ajusta_pos_leyenda_final if pd.api.types.is_numeric_dtype(df_long[columna_fecha]) else x_final
            leyenda_texts.append(
                ax.text(
                    x_final_ajustado, y_final,
                    f"  {var}",
                    color=color_map[var],
                    fontsize=font_config['leyenda']['size'],
                    fontweight=font_config['leyenda']['weight'],
                    va='center',
                    ha='left',
                    fontname=font_config['family']
                )
        )
        # Primero ajustar solo en Y
        adjust_text(
            leyenda_texts,
            ax=ax,
            only_move={'points': 'y', 'text': 'y'},
            autoalign='y',
            lim=1000,
            arrowprops=None
        )
        # Luego aplicar el desplazamiento horizontal
        for txt in tag_final_texts:
            pos = txt.get_position()
            # Solo sumar desplazamiento si el eje X es numérico
            if pd.api.types.is_numeric_dtype(df_long[columna_fecha]):
                txt.set_position((x_final_global + desplazamiento_tag, pos[1]))
            else:
                txt.set_position((x_final_global, pos[1]))
    if leyenda:
        leg = ax.legend(
            loc='upper center',
            bbox_to_anchor=pos_leyenda,
            ncol=ncol_leyenda if ncol_leyenda is not None else len(variables),
            frameon=False,
            prop={
                'size': font_config['leyenda']['size'],
                'weight': font_config['leyenda']['weight'],
                'family': font_config['family']
            }
        )
        for text in leg.get_texts():
            text.set_color(font_config['leyenda']['color'])  
            
    # Ajuste manual de separación vertical entre etiquetas finales (mayores arriba, menores abajo)
    if ajusta_sep_tag_final != 0.0 and len(tag_final_texts) > 1:
        posiciones = [txt.get_position() for txt in tag_final_texts]
        orden = sorted(range(len(posiciones)), key=lambda i: -posiciones[i][1])  # mayor Y arriba
        posiciones_ordenadas = [posiciones[i] for i in orden]
        textos_ordenados = [tag_final_texts[i] for i in orden]
        x_vals = [x for x, y in posiciones_ordenadas]
        y_centro = sum([y for x, y in posiciones_ordenadas]) / len(posiciones_ordenadas)
        for i, txt in enumerate(textos_ordenados):
            # Invertir el desplazamiento para que el primero (mayor) quede arriba
            nuevo_y = y_centro - ajusta_sep_tag_final * (i - (len(textos_ordenados)-1)/2)
            txt.set_position((x_vals[i], nuevo_y))

    # Leyenda tradicional si leyenda=True (independiente de leyenda_final)
    if leyenda:
        leg = ax.legend(
            loc='upper center',
            bbox_to_anchor=pos_leyenda,  # <-- Usar el nuevo argumento aquí
            ncol=ncol_leyenda if ncol_leyenda is not None else len(variables),
            frameon=False,
            prop={
                'size': font_config['leyenda']['size'],
                'weight': font_config['leyenda']['weight'],
                'family': font_config['family']
            }
        ) 

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_linewidth(1.5)
    ax.grid(axis='y', linestyle='-', color='#000000', alpha=0.2, linewidth=0.75)
    ax.yaxis.set_ticks_position('left')

    # --- GUARDADO Y VISUALIZACIÓN ---
    os.makedirs("output", exist_ok=True)
    plt.tight_layout()

    base_path = f"output/{nombre_df}"
    original_svg_path = f"{base_path}.svg"
    scour_svg_path = f"{base_path}_scour.svg"
    plt.savefig(original_svg_path, format='svg', bbox_inches='tight', dpi=300)
    plt.savefig(f"{base_path}.png", format='png', bbox_inches='tight', dpi=300)

    try:
        limpiar_svg_con_scour(original_svg_path, scour_svg_path)
        os.remove(original_svg_path)
    except Exception as e:
        print(f"Error al optimizar o eliminar el SVG: {e}")

    plt.show()