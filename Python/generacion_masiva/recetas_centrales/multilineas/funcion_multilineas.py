import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.font_manager as font_manager
import subprocess
import os


def ajusta_etiquetas(
    dataframe, 
    columnas, 
    colores, 
    columna_x, 
    sin_tag=2, 
    max=True, 
    fontsize=16, 
    fontname=None,
    fontweight=None,
    fontcolor=None,
    escala=None
):
    """
    Devuelve la lista de textos a etiquetar, pero NO llama a adjust_text.
    """
    texts = []
    for col, color in zip(columnas, colores):
        total_puntos = len(dataframe)
        max_index = dataframe[col].idxmax() if max else None
        for i, row in dataframe.iterrows():
            tiene_etiqueta = (total_puntos - i - 1) % (sin_tag + 1) == 0 or i == total_puntos - 1 or (max and i == max_index)
            if tiene_etiqueta:
                bbox_props = dict(boxstyle="round,pad=0.25,rounding_size=0.99", fc=color, ec="none", alpha=1.0)
                espacio = "\u00A0"
                va = 'bottom' if i % 2 == 0 else 'top'
                offset = escala if va == 'bottom' else -escala
                texts.append(
                    plt.text(
                        row[columna_x], 
                        row[col] + offset,
                        f"{espacio*1}{int(row[col]):,}{espacio*1}",
                        fontsize=fontsize, 
                        color=fontcolor if fontcolor else "white",
                        weight=fontweight,
                        ha='center', 
                        va=va, 
                        bbox=bbox_props,
                        fontname=fontname
                    )
                )
    return texts

def generar_multilineas(df, **kwargs):
    """
    Genera una gráfica de multilineas usando matplotlib que produce PNG y SVG
    
    Args:
        df: DataFrame con los datos (debe estar en formato long)
        **kwargs: Parámetros de configuración que pueden incluir:
            - columna_fecha: Nombre de la columna con fechas (default: 'Fecha')
            - columna_variable: Nombre de la columna con variables (default: 'Variable')
            - columna_valor: Nombre de la columna con valores (default: 'Valor')
            - nombre_archivo: Nombre del archivo de salida (default: 'multilineas')
            - font: Fuente a usar (default: 'Arial')
            - margen: Margen para las etiquetas (default: 0.7)
            - sin_tag: Frecuencia de etiquetas (default: 2)
            - config: Configuración adicional
    """
    try:
        # Verificar que adjustText esté disponible
        try:
            from adjustText import adjust_text
        except ImportError:
            print("Advertencia: adjustText no está disponible. Las etiquetas pueden solaparse.")
            adjust_text = None
        
        # Extraer parámetros con valores por defecto
        columna_fecha = kwargs.get('columna_fecha', 'Fecha')
        columna_variable = kwargs.get('columna_variable', 'Variable')
        columna_valor = kwargs.get('columna_valor', 'Valor')
        nombre_archivo = kwargs.get('nombre_archivo', kwargs.get('nombre', 'multilineas'))
        font = kwargs.get('font', 'Arial')
        margen = kwargs.get('margen', 0.7)
        sin_tag = kwargs.get('sin_tag', 2)
        config = kwargs.get('config', {})
        
        # Verificar que las columnas especificadas existan en el DataFrame
        if columna_fecha not in df.columns:
            raise ValueError(f"La columna '{columna_fecha}' no existe en el DataFrame.")
        if columna_variable not in df.columns:
            raise ValueError(f"La columna '{columna_variable}' no existe en el DataFrame.")
        if columna_valor not in df.columns:
            raise ValueError(f"La columna '{columna_valor}' no existe en el DataFrame.")
        
        # Configuración de fuentes
        font_config = {
            'family': font,
            'variable_x': {'size': 24, 'weight': 'semibold', 'color': '#767676'},
            'variable_y': {'size': 24, 'weight': 'medium', 'color': '#767676'},
            'capsula_valor': {'size': 12, 'weight': 'medium', 'color': '#ffffff'},
            'leyenda': {'size': 20, 'weight': 'medium', 'color': '#767676'}
        }

        # Configurar matplotlib
        plt.rcParams['svg.fonttype'] = 'none'
        font_dirs = [Path("../0_fonts")]
        font_files = font_manager.findSystemFonts(fontpaths=font_dirs)
        for font_file in font_files:
            font_manager.fontManager.addfont(font_file)

        # Configurar tamaño de figura
        ancho_px = 1480
        alto_px = 520
        dpi = 100
        ancho_in = ancho_px / dpi
        alto_in = alto_px / dpi

        fig, ax = plt.subplots(figsize=(ancho_in, alto_in), dpi=dpi)

        # Colores asignados
        colores_asignados = ["#006157", "#767676", "#671435", "#9B2247", "#9D792A", "#D5B162"]
        variables = df[columna_variable].unique()
        color_map = {var: colores_asignados[i % len(colores_asignados)] for i, var in enumerate(variables)}

        # Graficar todas las líneas y puntos primero
        for i, var in enumerate(variables):
            datos = df[df[columna_variable] == var]
            ax.plot(
                datos[columna_fecha],
                datos[columna_valor],
                label=var,
                color=color_map[var],
                linewidth=2
            )
            ax.scatter(
                datos[columna_fecha],
                datos[columna_valor],
                color=color_map[var],
                s=40,
                zorder=3
            )

        # Calcular la escala global para el offset de etiquetas
        escala = df[columna_valor].max() - df[columna_valor].min()

        # Agregar las etiquetas
        all_texts = []
        for i, var in enumerate(variables):
            datos = df[df[columna_variable] == var].reset_index(drop=True)
            total_puntos = len(datos)
            max_index = datos[columna_valor].idxmax()
            color = color_map[var]
            for j, row in datos.iterrows():
                tiene_etiqueta = (total_puntos - j - 1) % (sin_tag + 1) == 0 or j == total_puntos - 1 or j == max_index
                if tiene_etiqueta:
                    bbox_props = dict(
                        boxstyle="round,pad=0.25,rounding_size=0.99", 
                        fc=color,
                        ec='#ffffff', 
                        lw=margen, 
                        alpha=1.0
                    )
                    espacio = "\u00A0"
                    va = 'bottom'
                    offset = abs(escala) * 0.03 if escala else 10
                    all_texts.append(
                        plt.text(
                            row[columna_fecha],
                            row[columna_valor] + offset,
                            f"{espacio*1}{int(row[columna_valor]):,}{espacio*1}",
                            fontsize=font_config['capsula_valor']['size'],
                            color=font_config['capsula_valor']['color'],
                            weight=font_config['capsula_valor']['weight'],
                            ha='center',
                            va=va,
                            bbox=bbox_props,
                            fontname=font_config['family']
                        )
                    )

        # Ajustar todas las etiquetas juntas si adjustText está disponible
        if adjust_text and all_texts:
            adjust_text(
                all_texts,
                arrowprops=dict(arrowstyle='-', color='gray', lw=0.5),
                force_text=(150, 150),
                expand_points=(150, 150),
                expand_text=(150, 150),
                only_move={'points': 'y', 'text': 'y'},
                autoalign='y',
                lim=1000,
            )

        # Configurar etiquetas y formato
        plt.xticks(
            rotation=45,
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
        
        # Configurar leyenda
        leg = ax.legend(
            loc='upper center',
            bbox_to_anchor=(0.5, 1.2),
            ncol=len(variables),
            frameon=False,
            prop={
                'size': font_config['leyenda']['size'],
                'weight': font_config['leyenda']['weight'],
                'family': font_config['family']
            }
        )
        
        # Aplicar color manualmente a los textos de la leyenda
        for text in leg.get_texts():
            text.set_color(font_config['leyenda']['color'])
        
        # Configurar bordes
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_linewidth(1.5)
        
        # Configurar grid
        ax.grid(axis='y', linestyle='-', color='#000000', alpha=0.2, linewidth=0.75)
        ax.grid(axis='x', linestyle='-', color='#000000', alpha=0.2, linewidth=0.75)
        
        # Configurar formato de números
        ax.yaxis.set_ticks_position('left')
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))

        nombre_df = nombre_archivo or "multilineas"

        # --- 9. GUARDADO Y VISUALIZACIÓN ---
        output_dir = kwargs.get('output_dir', 'output')
        os.makedirs(output_dir, exist_ok=True)

        # Ajustar márgenes (idéntico a barras)
        left_margin = 0.15
        right_margin = 0.95
        bottom_margin = 0.2
        top_margin = 0.95
        plt.subplots_adjust(left=left_margin, right=right_margin, top=top_margin, bottom=bottom_margin)

        nombre_archivo_svg = f"{nombre_df}.svg"
        ruta_temporal = os.path.join(output_dir, nombre_archivo_svg)
        plt.savefig(ruta_temporal, format='svg', dpi=300, transparent=True)

        # Aplicar el flujo de exportación
        try:
            from svg_cleanup.flujo_exportacion import exportar_grafica
            archivo_final = exportar_grafica(ruta_temporal, nombre_df, output_dir)
            # Limpiar archivo temporal
            if archivo_final and os.path.exists(ruta_temporal):
                os.remove(ruta_temporal)
        except ImportError:
            print("Nota: Módulo de exportación no disponible. Se guardará el SVG sin optimizar.")
        except Exception as e:
            print(f"Advertencia: Error en el flujo de exportación: {e}")

        plt.close(fig)  # Cerrar la figura para liberar memoria
        print(f"Gráfica de multilineas guardada como: {ruta_temporal}")
        return ruta_temporal
        
    except Exception as e:
        print(f"Error al generar gráfica de multilineas: {e}")
        return None
