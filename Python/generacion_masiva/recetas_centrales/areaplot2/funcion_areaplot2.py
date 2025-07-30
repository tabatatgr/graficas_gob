
# --- IMPORTS NECESARIOS ---
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager
from pathlib import Path
import os
import matplotlib.ticker as mticker

# --- HELPERS MODULARIZADOS ---
def configurar_fuente_areaplot2(font):
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
    return font_config

def obtener_columnas_a_graficar(df, columna_fecha):
    if columna_fecha not in df.columns:
        raise ValueError(f"La columna '{columna_fecha}' no existe en el DataFrame.")
    return [col for col in df.columns if col != columna_fecha]

def crear_figura_areaplot2(ancho_px, alto_px, dpi):
    ancho_in = ancho_px / dpi
    alto_in = alto_px / dpi
    fig, ax = plt.subplots(figsize=(ancho_in, alto_in), dpi=dpi)
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)
    return fig, ax

def asignar_colores_areaplot2(paleta_colores, n):
    if paleta_colores is not None:
        return paleta_colores[:n]
    return ["#006157", "#767676", "#671435", "#9B2247", "#9D792A", "#D5B162"][:n]

def graficar_area_apilada_areaplot2(ax, df, columna_fecha, columnas_a_graficar, colores_asignados, alpha):
    ax.stackplot(
        df[columna_fecha],
        [df[col] for col in columnas_a_graficar],
        labels=columnas_a_graficar,
        colors=colores_asignados,
        alpha=alpha
    )

def configurar_ejes_areaplot2(ax, columna_fecha, font_config):
    ax.set_xlabel(columna_fecha, fontdict=font_config['etiquetas_eje_x'])
    ax.set_ylabel("Valores", fontdict=font_config['etiquetas_eje_y'])

def configurar_ticks_areaplot2(ax, font_config, rotacion_x):
    plt.xticks(rotation=rotacion_x, fontsize=font_config['eje_x']['size'], color=font_config['eje_x']['color'])
    plt.yticks(fontsize=font_config['eje_y']['size'], color=font_config['eje_y']['color'])

def configurar_leyenda_areaplot2(ax, columnas_a_graficar, font_config):
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

def configurar_estilos_areaplot2(ax):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(True)
    ax.spines['bottom'].set_linewidth(2)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))

def configurar_grillas_areaplot2(ax, mostrar_grid_x, mostrar_grid_y):
    if mostrar_grid_y:
        ax.grid(axis='y', linestyle='-', color='#000000', alpha=0.2, linewidth=0.75)
    if mostrar_grid_x:
        ax.grid(axis='x', linestyle='-', color='#000000', alpha=0.2, linewidth=0.75)

def guardar_y_exportar_areaplot2(fig, nombre, dpi, mostrar=False, usar_flujo_svg=False):
    os.makedirs("output", exist_ok=True)
    output_path = os.path.join("output", f"{nombre}.svg")
    plt.savefig(output_path, format="svg", bbox_inches='tight', dpi=dpi, transparent=True)
    if mostrar:
        plt.show()
    # Si se solicita el flujo SVG avanzado, ejecutarlo
    if usar_flujo_svg:
        try:
            from Python.generacion_masiva.svg_cleanup.flujo_exportacion import exportar_grafica
        except ImportError:
            try:
                from ..svg_cleanup.flujo_exportacion import exportar_grafica
            except ImportError:
                print("No se pudo importar el flujo de exportación SVG avanzado.")
                return
        resultado = exportar_grafica(output_path, nombre, "output")
        if resultado:
            print(f"SVG optimizado para Figma: {resultado}")
        else:
            print("Error en el flujo de exportación SVG avanzado.")

def obtener_indices_a_omitir(
    df,
    columnas,
    incluir_min=False,
    incluir_max=False,
    omitir_antes_del_max=False
):
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
    plt.rcParams['svg.fonttype'] = 'none'
    font_dirs = [Path("../0_fonts")]
    font_files = font_manager.findSystemFonts(fontpaths=font_dirs)
    for font_file in font_files:
        font_manager.fontManager.addfont(font_file)
    if indices_a_omitir is None:
        indices_a_omitir = set()
    else:
        indices_a_omitir = set(indices_a_omitir)
    acumulado = dataframe[columnas].cumsum(axis=1)
    y_max_global = acumulado.max(axis=1)
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
                i not in indices_a_omitir and tiene_etiqueta
            ):
                valor_actual = acumulado[col][i]
                y_base = valor_actual
                if x_pos in y_max_por_x:
                    y_etiqueta = y_base
                else:
                    y_etiqueta = y_base
                y_max_por_x[x_pos] = y_etiqueta
                if i != 1 and i != total_puntos - 1:
                    bbox_props_intermedio = dict(boxstyle="round,pad=0.15,rounding_size=0.8", fc="white", ec="gray", alpha=1.0, linewidth=1.5)
                    texto_color = color
                else:
                    bbox_props_intermedio = bbox_props or dict(boxstyle="round,pad=0.15,rounding_size=0.8", fc=color, ec="none", alpha=1.0, linewidth=1.5)
                    texto_color = "white"
                texto_capsula = f"{int(row[col]):,}".center(10)
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

# --- FUNCIÓN PRINCIPAL ---
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
    usar_flujo_svg=True,    # Si True, aplica limpieza SVG avanzada para Figma
    mostrar_grafica=False,   # Si True, muestra la ventana interactiva
    **kwargs
):
    font_config = configurar_fuente_areaplot2(font)
    columnas_a_graficar = obtener_columnas_a_graficar(df, columna_fecha)
    fig, ax = crear_figura_areaplot2(ancho_px, alto_px, dpi)
    colores_asignados = asignar_colores_areaplot2(paleta_colores, len(columnas_a_graficar))
    graficar_area_apilada_areaplot2(ax, df, columna_fecha, columnas_a_graficar, colores_asignados, alpha)
    configurar_ejes_areaplot2(ax, columna_fecha, font_config)
    configurar_ticks_areaplot2(ax, font_config, rotacion_x)
    configurar_leyenda_areaplot2(ax, columnas_a_graficar, font_config)
    configurar_estilos_areaplot2(ax)
    configurar_grillas_areaplot2(ax, mostrar_grid_x, mostrar_grid_y)
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
        y_max = df[columnas_a_graficar].sum(axis=1).max()
        margen = y_max * margen_y
        ax.set_ylim(0, y_max + margen)
    plt.tight_layout()
    guardar_y_exportar_areaplot2(fig, nombre, dpi, mostrar=mostrar_grafica, usar_flujo_svg=usar_flujo_svg)

