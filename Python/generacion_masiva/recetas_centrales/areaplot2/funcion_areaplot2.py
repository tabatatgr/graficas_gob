# Función para gráficas de área (areaplot2)
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager
from pathlib import Path
import matplotlib.ticker as mticker
import subprocess
import os

def obtener_indices_a_omitir(
    df,
    columnas,
    incluir_min=False,
    incluir_max=False,
    omitir_antes_del_max=False
):
    """Obtiene los índices de puntos a omitir en las etiquetas"""
    indices_a_omitir = set()

    for col in columnas:
        if pd.api.types.is_numeric_dtype(df[col]):
            if omitir_antes_del_max:
                idx_max = df[col].idxmax()
                pos = df.index.get_loc(idx_max)
                if pos > 0:
                    idx_antes = df.index[pos - 1]
                    indices_a_omitir.add(idx_antes)

            if not incluir_max:
                indices_a_omitir.add(df[col].idxmax())
            if not incluir_min:
                indices_a_omitir.add(df[col].idxmin())

    return list(indices_a_omitir)

def ajusta_etiquetas_apiladas_manual(
    dataframe, columnas, colores, columna_x, sin_tag=1, etiquetar_max=True, 
    bbox_props=None, fontsize=12, separacion=40, indices_a_omitir=None
):
    """
    Ajusta las etiquetas de los puntos en una gráfica apilada, colocándolas por encima del punto más alto
    y apilándolas verticalmente en orden correcto.
    """
    plt.rcParams['svg.fonttype'] = 'none'
    font_dirs = [Path("../0_fonts")]
    font_files = font_manager.findSystemFonts(fontpaths=font_dirs)
    for font_file in font_files:
        font_manager.fontManager.addfont(font_file)
    
    if indices_a_omitir is None:
        indices_a_omitir = set()
    else:
        indices_a_omitir = set(indices_a_omitir)
        
    # Calcular la altura acumulada máxima en cada punto X
    acumulado = dataframe[columnas].cumsum(axis=1)
    y_max_global = acumulado.max(axis=1)

    # Diccionario para guardar la posición Y más alta ocupada en cada X
    y_max_por_x = {}

    for col, color in zip(columnas, colores):
        total_puntos = len(dataframe)
        max_index = dataframe[col].idxmax() if etiquetar_max else None

        for i, row in dataframe.iterrows():
            x_pos = row[columna_x]
            tiene_etiqueta = (
                (total_puntos - i - 1) % (sin_tag + 1) == 0
                or i == total_puntos - 1
                or (etiquetar_max and i == max_index)
            )

            if (
                i not in indices_a_omitir and (
                    (total_puntos - i - 1) % (sin_tag + 1) == 0
                    or i == total_puntos - 1
                    or (etiquetar_max and i == max_index)
                )
            ):
                
                if tiene_etiqueta:
                    # Obtener el valor específico de esta serie en este punto
                    valor_actual = acumulado[col][i]
                    
                    # Altura base: usar el valor acumulado de esta serie
                    y_base = valor_actual
                    
                    # Si ya hay una etiqueta en esta X, mantener la altura base
                    if x_pos in y_max_por_x:
                        y_etiqueta = y_base
                    else:
                        y_etiqueta = y_base
                    
                    # Actualizar la altura máxima registrada para esta X
                    y_max_por_x[x_pos] = y_etiqueta

                    # Configurar el fondo de la etiqueta
                    if i != 1 and i != total_puntos - 1:  # Puntos intermedios
                        bbox_props_intermedio = dict(boxstyle="round,pad=0.15,rounding_size=0.8", fc="white", ec="gray", alpha=1.0, linewidth=1.5)
                        texto_color = color
                    else:  # Puntos máximos o finales
                        bbox_props_intermedio = bbox_props or dict(boxstyle="round,pad=0.15,rounding_size=0.8", fc=color, ec="none", alpha=1.0, linewidth=1.5)
                        texto_color = "white"
                    
                    # Añadir la etiqueta
                    texto_capsula = f"{int(row[col]):,}".center(10)

                    # Ya no modificamos la posición x de las fechas finales
                    x_pos_mod = x_pos

                    plt.text(
                        x_pos_mod,
                        y_etiqueta,
                        texto_capsula,
                        fontsize=fontsize,
                        color=texto_color,
                        ha='center',
                        va='bottom',
                        bbox=bbox_props_intermedio
                    )

def areaplot2(
    df, 
    columna_fecha,
    nombre="areaplot2",
    font='Arial',
    ancho_px=1480,
    alto_px=520,
    dpi=100,
    paleta_colores=None,
    mostrar_etiquetas=True,
    sin_tag=1,
    etiquetar_max=True,
    incluir_min=True,
    incluir_max=True,
    omitir_antes_del_max=True,
    separacion_etiquetas=1100,
    margen_y=0.5,
    rotacion_x=45,
    mostrar_grid_x=True,
    mostrar_grid_y=True,
    alpha=0.8,
    usar_flujo_svg=False,    # ← Optimización SVG para Figma
    **kwargs
):
    """
    Genera una gráfica de área (area plot) a partir de un DataFrame.

    Args:
        df (pd.DataFrame): DataFrame que contiene los datos a graficar.
        columna_fecha (str): Nombre de la columna que se usará como eje X.
        nombre (str): Nombre del archivo de salida
        font (str): Fuente a utilizar
        ancho_px (int): Ancho en píxeles
        alto_px (int): Alto en píxeles
        dpi (int): Resolución
        paleta_colores (list): Lista de colores personalizados
        mostrar_etiquetas (bool): Si mostrar etiquetas en los puntos
        sin_tag (int): Puntos sin etiqueta entre etiquetas
        etiquetar_max (bool): Si etiquetar el valor máximo de cada columna
        incluir_min (bool): Si incluir el mínimo en las etiquetas
        incluir_max (bool): Si incluir el máximo en las etiquetas
        omitir_antes_del_max (bool): Si omitir el punto antes del máximo
        separacion_etiquetas (int): Separación vertical entre etiquetas
        margen_y (float): Margen superior del eje Y (como porcentaje)
        rotacion_x (int): Rotación de las etiquetas del eje X
        mostrar_grid_x (bool): Si mostrar grilla en X
        mostrar_grid_y (bool): Si mostrar grilla en Y
        alpha (float): Transparencia del área
    """
    
    # Configuración de la fuente
    font_config = {
        'family': font,
        'titulo': {'size': 36, 'weight': 'medium', 'color': '#000000'},
        'eje_y': {'size': 24, 'weight': 'medium', 'color': '#000000'},
        'eje_x': {'size': 24, 'weight': 'medium', 'color': '#000000'},
        'etiquetas_eje_y': {'size': 24, 'weight': 'medium', 'color': '#767676'},
        'etiquetas_eje_x': {'size': 24, 'weight': 'semibold', 'color': '#767676'},
        'capsula_valor': {'size': 9, 'weight': 'medium', 'color': '#10302C'},
        'capsula_max': {'size': 12, 'weight': 'medium', 'color': 'white'},
        'porcentaje': {'size': 10, 'weight': 'medium', 'color': '#4C6A67'},
        'leyenda': {'size': 20, 'weight': 'medium', 'color': '#767676'}
    }

    plt.rcParams['svg.fonttype'] = 'none'
    font_dirs = [Path("../0_fonts")]
    font_files = font_manager.findSystemFonts(fontpaths=font_dirs)
    for font_file in font_files:
        font_manager.fontManager.addfont(font_file)
    
    # Verificar que la columna especificada exista
    if columna_fecha not in df.columns:
        raise ValueError(f"La columna '{columna_fecha}' no existe en el DataFrame.")
    
    # Obtener las columnas a graficar (excluyendo la columna de fecha)
    columnas_a_graficar = [col for col in df.columns if col != columna_fecha]
    
    # Configurar el tamaño de la figura
    ancho_in = ancho_px / dpi
    alto_in = alto_px / dpi
    
    # Crear la figura
    fig, ax = plt.subplots(figsize=(ancho_in, alto_in), dpi=dpi)
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)
    
    # Obtener los colores
    colores_asignados = paleta_colores or [
        "#006157", "#767676", "#671435", "#9B2247", "#9D792A", "#D5B162"
    ]
    
    # Graficar el área para cada columna
    ax.stackplot(
        df[columna_fecha],
        [df[col] for col in columnas_a_graficar],
        labels=columnas_a_graficar,
        colors=colores_asignados[:len(columnas_a_graficar)],
        alpha=alpha
    )

    # Configurar etiquetas y título
    ax.set_xlabel(columna_fecha, fontdict=font_config['etiquetas_eje_x'])
    ax.set_ylabel("Valores", fontdict=font_config['etiquetas_eje_y'])

    # Configurar etiquetas de ejes
    plt.xticks(rotation=rotacion_x, fontsize=font_config['eje_x']['size'], color=font_config['eje_x']['color'])
    plt.yticks(fontsize=font_config['eje_y']['size'], color=font_config['eje_y']['color'])
    
    # Posicionar la leyenda
    ax.legend(
        loc='upper center',
        bbox_to_anchor=(0.5, 1.1),
        ncol=len(columnas_a_graficar),
        frameon=False,
        prop=font_manager.FontProperties(
            family=font_config['family'],
            size=font_config['leyenda']['size'],
            weight=font_config['leyenda']['weight']
        )
    )

    # Configurar ejes
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(True)
    ax.spines['bottom'].set_linewidth(2)

    # Formatear números del eje Y
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))

    # Configurar grillas
    if mostrar_grid_y:
        ax.grid(axis='y', linestyle='-', color='#000000', alpha=0.2, linewidth=0.75)
    if mostrar_grid_x:
        ax.grid(axis='x', linestyle='-', color='#000000', alpha=0.2, linewidth=0.75)

    # Agregar etiquetas si se especifica
    if mostrar_etiquetas:
        indices_a_omitir = obtener_indices_a_omitir(
            df, columnas_a_graficar, 
            incluir_max=incluir_max, 
            incluir_min=incluir_min,
            omitir_antes_del_max=omitir_antes_del_max
        )
        
        ajusta_etiquetas_apiladas_manual(
            dataframe=df,
            columnas=columnas_a_graficar,
            colores=colores_asignados,
            columna_x=columna_fecha,
            sin_tag=sin_tag,
            etiquetar_max=etiquetar_max,
            fontsize=font_config['capsula_valor']['size'],
            separacion=separacion_etiquetas,
            indices_a_omitir=indices_a_omitir
        )

        # Ajustar límites del eje Y con margen
        y_max = df[columnas_a_graficar].sum(axis=1).max()
        margen = y_max * margen_y
        ax.set_ylim(0, y_max + margen)

    plt.tight_layout()

    # --- GUARDADO Y VISUALIZACIÓN ---
    os.makedirs("output", exist_ok=True)
    output_path = os.path.join("output", f"{nombre}.svg")
    
    # Guardar la gráfica - el CLI se encargará de la limpieza SVG
    plt.savefig(output_path, format="svg", bbox_inches='tight', dpi=dpi, transparent=True)
    plt.show()
