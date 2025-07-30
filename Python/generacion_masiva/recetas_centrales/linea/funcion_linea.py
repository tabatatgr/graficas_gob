from pathlib import Path
import pandas as pd
import matplotlib.transforms as mtrans
from matplotlib.text import TextPath
from matplotlib.patches import PathPatch
import matplotlib.pyplot as plt
from matplotlib.dates import date2num
import matplotlib.font_manager as font_manager

import os

def curly_at_fechas(x, y, width, height, ax=None, color="k"):
    """
    Dibuja una llave '{' o '}' en cualquier lugar del gráfico.

    Parámetros:
    - x: Coordenada X (puede ser una fecha o un valor numérico).
    - y: Coordenada Y.
    - width: Ancho de la llave.
    - height: Altura de la llave.
    - ax: Eje de Matplotlib donde se dibujará la llave (opcional).
    - color: Color del símbolo de la llave (por defecto es negro).
    """
    if not ax:
        ax = plt.gca()
    # Si x es una fecha, convertirla a un valor numérico
    if isinstance(x, pd.Timestamp):
        x = date2num(x)
    # Crear el símbolo de la llave con una fuente explícita
    tp = TextPath((0, 0), "}", size=1, prop=dict(family="DejaVu Sans"))
    # Escalar y trasladar la llave
    trans = (
        mtrans.Affine2D().scale(width, height) +
        mtrans.Affine2D().translate(x, y) +
        ax.transData
    )
    # Crear y añadir el PathPatch al eje con el color especificado
    pp = PathPatch(tp, lw=0, fc=color, transform=trans)
    ax.add_artist(pp)


def _configurar_fuentes(font='Montserrat'):
    font_config = {
        'family': font,
        'variable_x': {'size': 24, 'weight': 'semibold', 'color': '#767676'},
        'variable_y': {'size': 24, 'weight': 'medium', 'color': '#767676'},
        'capsula': {'size': 18, 'weight': 'medium', 'color': 'white'},
    }
    plt.rcParams['svg.fonttype'] = 'none'
    font_dirs = [Path("../0_fonts")]
    font_files = font_manager.findSystemFonts(fontpaths=font_dirs)
    for font_file in font_files:
        font_manager.fontManager.addfont(font_file)
    return font_config

def _validar_columnas(df, columna_fecha, columna_grafica, columna_linea):
    if columna_fecha not in df.columns:
        raise ValueError(f"La columna '{columna_fecha}' no existe en el DataFrame.")
    if columna_grafica not in df.columns:
        raise ValueError(f"La columna '{columna_grafica}' no existe en el DataFrame.")
    if columna_linea not in df.columns:
        raise ValueError(f"La columna '{columna_linea}' no existe en el DataFrame.")

def _configurar_figura():
    ancho_px = 1480
    alto_px = 520
    dpi = 100
    ancho_in = ancho_px / dpi
    alto_in = alto_px / dpi
    fig, ax = plt.subplots(figsize=(ancho_in, alto_in), dpi=dpi)
    return fig, ax

def _graficar_linea(df, ax, columna_fecha, columna_grafica, columna_linea, font_config):
    color_area = '#d4dce9'
    color_linea = '#2f5597'
    color_linea_punteada = '#c00000'
    ax.fill_between(
        df[columna_fecha],
        df[columna_grafica],
        color=color_area,
        alpha=1.,
    )
    ax.plot(
        df[columna_fecha],
        df[columna_grafica],
        color=color_linea,
        linewidth=2
    )
    ax.plot(
        df[columna_fecha],
        df[columna_linea],
        color=color_linea_punteada,
        linestyle='--',
        linewidth=2
    )
    ax.tick_params(axis='x', labelsize=font_config['variable_x']['size'], labelcolor=font_config['variable_x']['color'])
    ax.tick_params(axis='y', labelsize=font_config['variable_y']['size'], labelcolor=font_config['variable_y']['color'])
    ax.spines['bottom'].set_position(('data', 0))
    plt.xticks(rotation=90, fontname=font_config['family'], fontsize=font_config['variable_x']['size'], color=font_config['variable_x']['color'], weight=font_config['variable_x']['weight'])
    plt.yticks(fontname=font_config['family'], fontsize=font_config['variable_y']['size'], color=font_config['variable_y']['color'], weight=font_config['variable_y']['weight'])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(True)
    ax.spines['bottom'].set_linewidth(2)
    ax.grid(axis='y', linestyle='-', color='#000000', alpha=0.2, linewidth=0.75)
    ax.grid(axis='x', linestyle='-', color='#000000', alpha=0.2, linewidth=0.75)

def _agregar_llave_capsula(df, ax, columna_fecha, columna_grafica, columna_linea, font_config):
    x_pos = df[columna_fecha].iloc[-1]
    y_pos_gra = df[columna_grafica].iloc[-1]
    y_pos_lin = df[columna_linea].iloc[-1]
    if y_pos_gra > y_pos_lin:
        y_pos_min = y_pos_lin
        y_pos_max = y_pos_gra
    else:
        y_pos_min = y_pos_gra
        y_pos_max = y_pos_lin
    altura = y_pos_max - y_pos_min
    x_min, x_max = ax.get_xlim()
    y_min, y_max = ax.get_ylim()
    factor_ancho = 0.04 * (x_max - x_min)
    factor_alto = 0.05 * (y_max - y_min)
    curly_at_fechas(x_pos, y_pos_min+0.2*factor_alto, width=factor_ancho, height=altura+factor_alto, ax=ax, color="#af0b19")
    diferencia = round(y_pos_gra - y_pos_lin)
    color_capsula = "#af0b19"
    bbox_props = dict(boxstyle="round,pad=0.25,rounding_size=0.99", fc=color_capsula, ec="none", alpha=1.0)
    x_pos_numeric = date2num(x_pos)
    ax.text(
        x_pos_numeric + 1.8 * factor_ancho,
        y_pos_min + altura / 2.5,
        diferencia,
        color=font_config['capsula']['color'],
        fontsize=font_config['capsula']['size'],
        fontweight=font_config['capsula']['weight'],
        fontname=font_config['family'],
        bbox=bbox_props,
        ha="center",
        va="center"
    )

def _guardar_y_exportar(fig, nombre_df, output_dir):
    left_margin = 0.15
    right_margin = 0.95
    bottom_margin = 0.2
    top_margin = 0.95
    plt.subplots_adjust(left=left_margin, right=right_margin, top=top_margin, bottom=bottom_margin)
    nombre_archivo = f"{nombre_df}.svg"
    ruta_temporal = os.path.join(output_dir, nombre_archivo)
    plt.savefig(ruta_temporal, format='svg', dpi=300, transparent=True)
    try:
        from svg_cleanup.flujo_exportacion import exportar_grafica
        archivo_final = exportar_grafica(ruta_temporal, nombre_df, output_dir)
        if archivo_final and os.path.exists(ruta_temporal):
            os.remove(ruta_temporal)
    except ImportError:
        print("Nota: Módulo de exportación no disponible. Se guardará el SVG sin optimizar.")
    except Exception as e:
        print(f"Advertencia: Error en el flujo de exportación: {e}")
    plt.close(fig)
    print(f"Gráfica guardada como: {ruta_temporal}")
    return ruta_temporal

def _inferir_columna(df, posibles):
    for col in df.columns:
        if col.lower() in posibles:
            return col
    return None

def linea_diferencia_capsula(df, **kwargs):
    """
    Genera una gráfica de línea con diferencia y cápsula opcional.
    Si no se especifican columnas, se infieren automáticamente por nombre.
    """
    try:
        posibles_fechas = {'fecha', 'date', 'periodo', 'period', 'año', 'anio', 'year'}
        posibles_grafica = {'valor', 'valores', 'value', 'grafica', 'y', 'principal'}
        posibles_linea = {'referencia', 'linea', 'line', 'comparacion', 'comparación', 'ref', 'y2'}

        columna_fecha = kwargs.get('columna_fecha') or _inferir_columna(df, posibles_fechas)
        columna_grafica = kwargs.get('columna_grafica') or _inferir_columna(df, posibles_grafica)
        columna_linea = kwargs.get('columna_linea') or _inferir_columna(df, posibles_linea)
        nombre_archivo = kwargs.get('nombre_archivo', kwargs.get('nombre', 'linea'))
        output_dir = kwargs.get('output_dir', 'output')
        font = kwargs.get('font', 'Montserrat')
        agregar_capsula = kwargs.get('agregar_capsula', True)
        if not columna_fecha or not columna_grafica or not columna_linea:
            raise ValueError("No se pudieron inferir las columnas automáticamente. Especifica columna_fecha, columna_grafica y columna_linea.")
        _validar_columnas(df, columna_fecha, columna_grafica, columna_linea)
        if df[columna_fecha].dtype == 'object':
            df[columna_fecha] = pd.to_datetime(df[columna_fecha])
        font_config = _configurar_fuentes(font)
        nombre_df = nombre_archivo or "linea"
        fig, ax = _configurar_figura()
        _graficar_linea(df, ax, columna_fecha, columna_grafica, columna_linea, font_config)
        if agregar_capsula:
            _agregar_llave_capsula(df, ax, columna_fecha, columna_grafica, columna_linea, font_config)
        os.makedirs(output_dir, exist_ok=True)
        ruta = _guardar_y_exportar(fig, nombre_df, output_dir)
        return ruta
    except Exception as e:
        print(f"Error al generar gráfica de línea: {e}")
        return None
