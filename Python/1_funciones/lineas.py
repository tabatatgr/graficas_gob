from pathlib import Path
from adjustText import adjust_text
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.font_manager as font_manager
import subprocess
import pandas as pd
import os

from funciones import limpiar_svg_con_scour 
from funciones import formato_fechas
from funciones import mostrar_guardar_figura

def lineas(
# --- DATOS Y ESTRUCTURA ---
df,                            # DataFrame de entrada (formato largo: fecha, variable, valor)
puntos=True,                   # Mostrar puntos en la línea (bool: True/False)
escalonada=False,              # Graficar líneas escalonadas (bool: True/False)
lineas_verticales=None,        # Lista de dicts con líneas verticales a agregar (None o [{'x':..., 'color':..., ...}, ...])
ancho_linea=2,                 # Grosor de las líneas principales (int o float)

# --- GRÁFICA GENERAL --- 
nombre="lineas",               # Nombre base para archivos de salida (str)
tipo_letra='Montserrat',       # Tipo de letra para todo el texto (str, ej: 'Montserrat', 'Arial')
paleta_colores=None,           # Lista de colores para las líneas (None o [str, ...])
ancho_fig=None,                # Ancho de la figura en pulgadas (None o float)
alto_fig=None,                 # Alto de la figura en pulgadas (None o float)
margen=False,                  # Mostrar todos los bordes del gráfico (bool: True/False)
margen_color='black',          # Color de los bordes del gráfico (str, ej: 'black', '#123456')
margen_ancho=1.5,              # Grosor de los bordes del gráfico (float)
marcas_ejes=True,              # Mostrar marcas (ticks) en los ejes (bool: True/False)
mostrar_fig=True,              # Mostrar la figura al terminar (bool: True/False)
guardar_fig=True,              # Guardar la figura al terminar (bool: True/False)

# --- CÁPSULAS O TAGS ---
muestra_etiquetas=None,        # Índices de puntos donde mostrar etiquetas (None o list[int])
weight_borde_capsu=0.7,        # Grosor del borde de las cápsulas (float)
capsula_valor_size=12,         # Tamaño de letra para valores en cápsulas (int)
capsula_valor_weight='medium', # Grosor de letra en cápsulas (str: 'normal', 'medium', 'bold', etc.)
capsula_valor_color='#ffffff', # Color de letra en cápsulas (str)
ajusta_pos_tag_final=0.0,      # Ajuste horizontal de etiquetas finales (float)
ajusta_sep_tag_final=0.0,      # Ajuste vertical entre etiquetas finales (float)
ajusta_pos_capsu=0.0,          # Ajuste vertical de cápsulas (float)
decimales_capsu=0,             # Número de decimales en valores de cápsulas (int)
tag_final=True,                # Mostrar etiqueta final en cada línea (bool: True/False o 'derecha')
tag_max=True,                  # Mostrar etiqueta en el valor máximo de cada línea (bool: True/False)
tag_especifico=None,           # Lista de valores X donde mostrar etiquetas específicas (None o list)
rounding_size=0.99,            # Redondez de las cápsulas (float, 0 a 1)
sin_tag=2,                     # Espaciado entre etiquetas automáticas (int)

# --- FUNCIÓN: ADJUST_TEXT ---
arrowprops=dict(arrowstyle='-', color='gray', lw=0.5), # Propiedades de flechas para etiquetas (dict)
force_text=(150, 150),         # Fuerza de ajuste de texto (tuple: (int, int))
expand_points=(150, 150),      # Expansión de puntos para ajuste (tuple: (int, int))
expand_text=(150, 150),        # Expansión de texto para ajuste (tuple: (int, int))
only_move={'points': 'y', 'text': 'y'}, # Restricción de movimiento en ajuste (dict)
autoalign='y',                 # Tipo de alineación automática ('y', 'x', 'xy', None)
lim=1000,                      # Número máximo de iteraciones para ajuste (int)

# --- LEYENDA ---
tam_letra_leyenda=20,          # Tamaño de letra para la leyenda (int)
weight_letra_leyenda='medium', # Grosor de letra para la leyenda (str)
color_letra_leyenda='#767676', # Color de letra para la leyenda (str)
leyenda_final=False,           # Mostrar leyenda final alineada a la derecha (bool: True/False)
leyenda=False,                 # Mostrar leyenda tradicional (bool: True/False)
ncol_leyenda=None,             # Número de columnas en la leyenda (None o int)
pos_leyenda=(0.5, 1.2),        # Posición de la leyenda tradicional (tuple: (float, float))
ajusta_pos_leyenda_final=0.0,  # Ajuste horizontal de leyenda final (float)

# --- EJE X ---
tam_letra_ejeX=24,             # Tamaño de letra para etiquetas eje X (int)
weight_letra_ejeX='semibold',  # Grosor de letra para etiquetas eje X (str)
color_letra_ejeX='#767676',    # Color de letra para etiquetas eje X (str)
orientacion_etiqu_ejeX=None,   # Orientación de etiquetas eje X (None, 'horizontal', 'vertical', 'diagonal')
modalidad_fechas=None,         # Formato de fechas en eje X (None o str, ej: 'año', 'mes', etc.)

# --- EJE Y ---
sustituir_etiquetas_ejeY=None, # Lista para sustituir etiquetas del eje Y (None o list[str])
y_limits=None,                 # Límites del eje Y (None o tuple: (min, max))
reducir_ticks_y=False,         # Reducir número de ticks en eje Y (bool: True/False)
tam_letra_ejeY=24,             # Tamaño de letra para etiquetas eje Y (int)
weight_letra_ejeY='medium',    # Grosor de letra para etiquetas eje Y (str)
color_letra_ejeY='#767676',    # Color de letra para etiquetas eje Y (str)

):
    # Validar columnas
    if df.shape[1] != 3:
        raise ValueError("El DataFrame debe tener exactamente 3 columnas: fecha, variable y valor (en ese orden).")

    # Asignar nombres automáticos
    columna_fecha = df.columns[0]
    columna_variable = df.columns[1]
    columna_valor = df.columns[2]

    font_config = {
        'family': tipo_letra,
        'variable_x': {'size': tam_letra_ejeX, 'weight': weight_letra_ejeX, 'color': color_letra_ejeX},
        'variable_y': {'size': tam_letra_ejeY, 'weight': weight_letra_ejeY, 'color': color_letra_ejeY},
        'capsula_valor': {'size': capsula_valor_size, 'weight': capsula_valor_weight, 'color': capsula_valor_color},
        'leyenda': {'size': tam_letra_leyenda, 'weight': weight_letra_leyenda, 'color': color_letra_leyenda}
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

    variables = df[columna_variable].unique()
    if paleta_colores is not None:
        colores_asignados = paleta_colores
    else:
        colores_asignados = ["#006157", "#767676", "#671435", "#9B2247", "#9D792A", "#D5B162"]
    color_map = {var: colores_asignados[i % len(colores_asignados)] for i, var in enumerate(variables)}

    # Graficar todas las líneas y puntos primero
    for i, var in enumerate(variables):
        datos = df[df[columna_variable] == var]
        if escalonada:
            ax.step(
                datos[columna_fecha],
                datos[columna_valor],
                label=var,
                color=color_map[var],
                linewidth=ancho_linea,
                where='mid'
            )
        else:
            ax.plot(
                datos[columna_fecha],
                datos[columna_valor],
                label=var,
                color=color_map[var],
                linewidth=ancho_linea
            )
        if puntos:
            ax.scatter(
                datos[columna_fecha],
                datos[columna_valor],
                color=color_map[var],
                s=40,
                zorder=3
            )

    # ...después de graficar las líneas y puntos...
    y_max = df[columna_valor].max()
    y_min = df[columna_valor].min()
    espacio_extra = abs(y_max - y_min) * 0.24  # 15% de espacio extra arriba
    ax.set_ylim(y_min - 0.5*espacio_extra, y_max + espacio_extra)

    # Calcular la escala global para el offset de etiquetas
    escala = df[columna_valor].max() - df[columna_valor].min()

    # Calcular la coordenada X máxima global para alinear todas las etiquetas finales
    if tag_final == 'derecha':
        x_final_global = df[columna_fecha].max()

    all_texts = []
    tag_final_texts = []  # Para guardar referencias a las etiquetas finales
    for i, var in enumerate(variables):
        datos = df[df[columna_variable] == var].reset_index(drop=True)
        total_puntos = len(datos)
        max_index = datos[columna_valor].idxmax()
        color = color_map[var]
        bbox_props = dict(
            boxstyle=f"round,pad=0.25,rounding_size={rounding_size}",
            fc=color,
            ec='#ffffff', 
            lw=weight_borde_capsu, 
            alpha=1.0
        )
        espacio = "\u00A0"
        va = 'bottom'
        escala = df[columna_valor].max() - df[columna_valor].min()
        offset = abs(escala) * 0.03 if escala else 10
        for j, row in datos.iterrows():
            # --- NUEVO: Mostrar tag si el valor de X está en tag_especifico ---
            if tag_especifico is not None and row[columna_fecha] in tag_especifico:
                mostrar_etiqueta = True
            else:
                # Si muestra_etiquetas está definido, solo mostrar en esos índices
                if muestra_etiquetas is not None:
                    mostrar_etiqueta = j in muestra_etiquetas
                else:
                    mostrar_etiqueta = (total_puntos - j - 1) % (sin_tag + 1) == 0

            tiene_etiqueta = mostrar_etiqueta
            es_ultimo = (j == total_puntos - 1) and (tag_final is True)
            es_maximo = (j == max_index) and tag_max
            # --- NUEVO: tag_especifico tiene mayor jerarquía ---
            if tag_especifico is not None and row[columna_fecha] in tag_especifico:
                mostrar_tag = True
            else:
                mostrar_tag = (tiene_etiqueta or es_ultimo or es_maximo) and not (tag_final == 'derecha' and j == total_puntos - 1)

            if mostrar_tag:
                # Si es el máximo, aumenta el offset para evitar que se encime
                offset_actual = offset
                if es_maximo:
                    offset_actual += abs(escala) * 0.0  

                # Formato inteligente de decimales
                valor_num = row[columna_valor]
                if decimales_capsu > 0:
                    valor_capsula = f"{valor_num:.{decimales_capsu}f}".rstrip('0').rstrip('.')
                else:
                    valor_capsula = f"{int(valor_num)}"

                all_texts.append(
                    plt.text(
                        row[columna_fecha],
                        row[columna_valor] + offset_actual + ajusta_pos_capsu,
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
            if pd.api.types.is_numeric_dtype(df[columna_fecha]):
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
            if pd.api.types.is_numeric_dtype(df[columna_fecha]):
                txt.set_position((x_final_global + desplazamiento_tag, pos[1]))
            else:
                txt.set_position((x_final_global, pos[1]))

    # Si tag_final == 'derecha' y leyenda_final, extraer las coordenadas Y ajustadas
    if tag_final == 'derecha' and leyenda_final:
        y_coords = [txt.get_position()[1] for txt in tag_final_texts]
    else:
        y_coords = None

     # Etiquetas y formato para el eje x (acepta fechas o enteros)
    valores_x = df[columna_fecha].unique()
    if pd.api.types.is_integer_dtype(df[columna_fecha]):
        etiquetas_x = [str(x) for x in valores_x]
    else:
        etiquetas_x = formato_fechas(valores_x, modalidad=modalidad_fechas)  

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

    # Reducir el número de ticks en el eje Y si se solicita, priorizando enteros
    if reducir_ticks_y:
        ax.yaxis.set_major_locator(mticker.MaxNLocator(nbins=5, prune='both', integer=True))

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
            ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:g}"))

    # --- Graficar líneas verticales ---
    if lineas_verticales is not None:
        for linea in lineas_verticales:
            ax.axvline(
                x=linea.get('x', 0),
                color=linea.get('color', '#DC8F12'),
                linewidth=linea.get('linewidth', 2),
                linestyle=linea.get('linestyle', '--'),
                alpha=linea.get('alpha', 1),
                zorder=linea.get('zorder', 0)
            )

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

    # --- Mostrar u ocultar las marcas de los ejes (ticks) ---
    if not marcas_ejes:
        ax.tick_params(axis='x', which='both', length=0)
        ax.tick_params(axis='y', which='both', length=0)


    if leyenda_final:
        leyenda_texts = []
        for i, var in enumerate(variables):
            datos = df[df[columna_variable] == var]
            x_final = datos[columna_fecha].iloc[-1]
            # Si tag_final es 'derecha' y leyenda_final, usar el mismo Y que la etiqueta final ajustada
            if tag_final == 'derecha' and y_coords is not None:
                y_final = y_coords[i]
                # Aplica el ajuste horizontal aquí
                x_final_ajustado = x_final + ajusta_pos_leyenda_final if pd.api.types.is_numeric_dtype(df[columna_fecha]) else x_final
            else:
                y_final = datos[columna_valor].iloc[-1]
                x_final_ajustado = x_final + ajusta_pos_leyenda_final if pd.api.types.is_numeric_dtype(df[columna_fecha]) else x_final
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
            if pd.api.types.is_numeric_dtype(df[columna_fecha]):
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

    if margen:
        for spine in ['top', 'right', 'left', 'bottom']:
            ax.spines[spine].set_visible(True)
            ax.spines[spine].set_linewidth(margen_ancho)
            ax.spines[spine].set_color(margen_color)
    else:
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_linewidth(margen_ancho)
        ax.spines['bottom'].set_color(margen_color)


    ax.grid(axis='y', linestyle='-', color='#000000', alpha=0.2, linewidth=0.75)
    ax.yaxis.set_ticks_position('left')

    return mostrar_guardar_figura(fig, ax, nombre, guardar_fig, mostrar_fig, limpiar_svg_con_scour)