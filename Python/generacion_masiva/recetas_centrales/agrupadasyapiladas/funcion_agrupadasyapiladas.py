# Función para gráficas de barras agrupadas y apiladas
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager
from pathlib import Path
import matplotlib.ticker as mticker
import os

def agrupadasyapiladas(
    dataframes, 
    nombre="grafica_agrupadasyapiladas",
    font='Arial',
    barra_valor=True, 
    porcentaje=True, 
    capsula_max=True,
    ancho_px=3200,
    alto_px=520,
    dpi=100,
    paleta_colores=None,
    columna_grupo='Categoria',
    columna_subgrupo='Mes',
    columna_valor='Valor',
    excluir_total=False,
    output_dir="output",
    usar_flujo_svg=True,  # Por defecto, limpieza SVG avanzada para Figma
    mostrar_grafica=False,
    **kwargs
):
    """
    Genera una gráfica de barras apiladas agrupadas para múltiples DataFrames.

    Args:
        dataframes (list of pd.DataFrame): Lista de DataFrames con los datos de los grupos de subgrupos apilados.
        font_size (int): Tamaño de la fuente para los elementos de la gráfica.
    """

    font_config = configurar_fuente_agrupadasyapiladas(font)
    grupos, subgrupos_list = configurar_datos_agrupadasyapiladas(dataframes, columna_grupo, columna_subgrupo)
    colores_por_grupo = asignar_colores_agrupadasyapiladas(subgrupos_list, paleta_colores)
    fig, ax, x_pos, posiciones_centrales = crear_figura_agrupadasyapiladas(grupos, colores_por_grupo, ancho_px, alto_px, dpi)
    dibujar_barras_agrupadasyapiladas(
        ax, dataframes, colores_por_grupo, x_pos, grupos, barra_valor, capsula_max, font_config,
        columna_grupo, columna_subgrupo, columna_valor
    )
    configurar_leyenda_agrupadasyapiladas(ax, font_config, len(dataframes))
    configurar_estilos_agrupadasyapiladas(ax, font_config, posiciones_centrales, grupos)
    guardar_y_exportar_agrupadasyapiladas(fig, output_dir, nombre, dpi, mostrar=mostrar_grafica, usar_flujo_svg=usar_flujo_svg)

# --- HELPERS MODULARIZADOS ---
def configurar_fuente_agrupadasyapiladas(font):
    font_config = {
        'family': font,
        'titulo': {'size': 36, 'weight': 'medium', 'color': '#000000'},
        'eje_y': {'size': 18, 'weight': 'medium', 'color': '#000000'},
        'eje_x': {'size': 18, 'weight': 'medium', 'color': '#000000'},
        'etiquetas_eje_y': {'size': 24, 'weight': 'medium', 'color': '#767676'},
        'etiquetas_eje_x': {'size': 24, 'weight': 'semibold', 'color': '#767676'},
        'barra_valor': {'size': 9, 'weight': 'medium', 'color': '#10302C'},
        'capsula_max': {'size': 12, 'weight': 'medium', 'color': 'white'},
        'porcentaje': {'size': 10, 'weight': 'medium', 'color': '#4C6A67'},
        'leyenda': {'size': 14, 'weight': 'medium', 'color': '#767676'}
    }
    plt.rcParams['svg.fonttype'] = 'none'
    font_dirs = [Path("../0_fonts")]
    font_files = font_manager.findSystemFonts(fontpaths=font_dirs)
    for font_file in font_files:
        font_manager.fontManager.addfont(font_file)
    return font_config

def configurar_datos_agrupadasyapiladas(dataframes, columna_grupo, columna_subgrupo):
    grupos = dataframes[0][columna_grupo].unique().tolist()
    subgrupos_list = [df[columna_subgrupo].unique().tolist() for df in dataframes]
    return grupos, subgrupos_list

def asignar_colores_agrupadasyapiladas(subgrupos_list, paleta_colores=None):
    if paleta_colores is None:
        lista_colores = ["#006157", "#767676", "#671435", "#9B2247", "#9D792A", "#D5B162", "#10302C", "#E6D194", "#018477", "#FF6666", "#00008B", "#854991"]
    else:
        lista_colores = paleta_colores
    colores_por_grupo = []
    color_index = 0
    for subgrupos in subgrupos_list:
        colores_por_grupo.append(lista_colores[color_index:color_index + len(subgrupos)])
        color_index += len(subgrupos)
    return colores_por_grupo

def crear_figura_agrupadasyapiladas(grupos, colores_por_grupo, ancho_px, alto_px, dpi):
    ancho_barra = 0.2
    espacio_entre_barras = 0.05
    ancho_grupo = len(colores_por_grupo) * (ancho_barra + espacio_entre_barras)
    desplazamiento_inicial = -ancho_grupo / 2
    ancho_in = ancho_px / dpi
    alto_in = alto_px / dpi
    fig, ax = plt.subplots(figsize=(ancho_in, alto_in), dpi=dpi)
    x_pos = np.arange(len(grupos))
    posiciones_centrales = [i + desplazamiento_inicial + (len(colores_por_grupo) // 2) * ancho_barra for i in x_pos]
    return fig, ax, x_pos, posiciones_centrales

def dibujar_barras_agrupadasyapiladas(ax, dataframes, colores_por_grupo, x_pos, grupos, barra_valor, capsula_max, font_config, columna_grupo, columna_subgrupo, columna_valor):
    ancho_barra = 0.2
    espacio_entre_barras = 0.05
    desplazamiento_inicial = -len(dataframes) * (ancho_barra + espacio_entre_barras) / 2
    for df, colores, offset in zip(dataframes, colores_por_grupo, range(len(dataframes))):
        bottom = np.zeros(len(grupos))
        total_grupo = (
            df.groupby(columna_grupo)[columna_valor].sum()
            .reindex(grupos)
            .values
        )
        subgrupos = df[columna_subgrupo].unique().tolist()
        for subgrupo, color in zip(subgrupos, colores):
            valores = df[df[columna_subgrupo] == subgrupo].sort_values(columna_grupo)[columna_valor].values
            if len(valores) < len(grupos):
                valores = np.pad(valores, (0, len(grupos) - len(valores)), 'constant')
            posicion_barra = x_pos + desplazamiento_inicial + offset * ancho_barra
            ax.bar(
                posicion_barra,
                valores,
                width=ancho_barra,
                bottom=bottom,
                color=color,
                label=subgrupo,
                zorder=3
            )
            for i, valor in enumerate(valores):
                porcentaje = (valor / total_grupo[i]) * 100 if total_grupo[i] != 0 else 0
                if barra_valor:
                    ax.text(
                        posicion_barra[i],
                        bottom[i] + valor / 2,
                        f"{int(valor):,} ({porcentaje:.1f}%)" if porcentaje else f"{int(valor):,}",
                        ha='center',
                        va='center',
                        fontsize=font_config['barra_valor']['size'],
                        fontweight=font_config['barra_valor']['weight'],
                        color='white' if porcentaje > 10 else 'black'
                    )
            bottom += np.array(valores)
        if capsula_max:
            factor_separacion = max(bottom) * 0.05
            for i, total in enumerate(bottom):
                ax.text(
                    posicion_barra[i],
                    total + factor_separacion,
                    f"{int(total):,}",
                    ha="center",
                    va="bottom",
                    fontsize=font_config['capsula_max']['size'],
                    fontweight=font_config['capsula_max']['weight'],
                    color=colores[1] if len(colores) > 1 else 'black',
                    bbox=dict(boxstyle="round,pad=0.35,rounding_size=0.99", fc="white", ec=colores[0], alpha=1.0)
                )

def configurar_leyenda_agrupadasyapiladas(ax, font_config, n_dataframes):
    ax.legend(
        loc='upper center',
        bbox_to_anchor=(0.5, 1.5),
        frameon=False,
        prop={'size': font_config['leyenda']['size'], 'weight': font_config['leyenda']['weight']},
        ncol=max(1, n_dataframes),
    )

def configurar_estilos_agrupadasyapiladas(ax, font_config, posiciones_centrales, grupos):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(True)
    ax.spines['bottom'].set_linewidth(2)
    ax.grid(axis='y', linestyle='-', color='#000000', alpha=0.2, linewidth=0.75)
    import matplotlib.ticker as mticker
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.tick_params(axis='y', labelsize=font_config['eje_y']['size'], labelcolor=font_config['eje_y']['color'])
    ax.yaxis.label.set_size(font_config['eje_y']['size'])
    ax.yaxis.label.set_weight(font_config['eje_y']['weight'])
    ax.yaxis.label.set_color(font_config['eje_y']['color'])
    ax.set_xticks(posiciones_centrales)
    ax.set_xticklabels(grupos, fontsize=font_config['eje_x']['size'],
                    fontweight=font_config['eje_x']['weight'],
                    color=font_config['eje_x']['color'])
    ax.set_ylabel('Valores', fontsize=font_config['etiquetas_eje_y']['size'], fontweight=font_config['etiquetas_eje_y']['weight'], color=font_config['etiquetas_eje_y']['color'])
    plt.tight_layout()

def guardar_y_exportar_agrupadasyapiladas(fig, output_dir, nombre, dpi, mostrar=False, usar_flujo_svg=True):
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{nombre}.svg")
    plt.savefig(output_path, format="svg", bbox_inches='tight', dpi=dpi)
    if mostrar:
        plt.show()
    # Si se solicita el flujo SVG avanzado, ejecutarlo
    if usar_flujo_svg:
        try:
            from Python.generacion_masiva.svg_cleanup.flujo_exportacion import exportar_grafica
        except ImportError:
            try:
                from svg_cleanup.flujo_exportacion import exportar_grafica
            except ImportError:
                print("No se pudo importar el flujo de exportación SVG avanzado.")
                return
        resultado = exportar_grafica(output_path, nombre, output_dir)
        if resultado:
            print(f"SVG optimizado para Figma: {resultado}")
        else:
            print("Error en el flujo de exportación SVG avanzado.")