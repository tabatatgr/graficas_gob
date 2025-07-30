import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from pathlib import Path
from matplotlib import font_manager
import subprocess
import os


def _validar_columnas_lineas(df, columna_entidad, columna_fecha, columna_valor):
    if columna_entidad not in df.columns:
        raise ValueError(f"La columna '{columna_entidad}' no existe en el DataFrame.")
    if columna_fecha not in df.columns:
        raise ValueError(f"La columna '{columna_fecha}' no existe en el DataFrame.")
    if columna_valor not in df.columns:
        raise ValueError(f"La columna '{columna_valor}' no existe en el DataFrame.")

def _configurar_fuentes_lineas():
    plt.rcParams['svg.fonttype'] = 'none'
    font_dirs = [Path("../0_fonts")]
    font_files = font_manager.findSystemFonts(fontpaths=font_dirs)
    for font_file in font_files:
        font_manager.fontManager.addfont(font_file)

def _configurar_figura_lineas():
    fig, ax = plt.subplots(figsize=(12, 4))
    return fig, ax

def _graficar_lineas(ax, df, columna_entidad, columna_fecha, columna_valor, entidad_destacada, color_destacado, color_otras, alpha_otras):
    # Permitir múltiples entidades destacadas
    if isinstance(entidad_destacada, str):
        entidades_destacadas = [entidad_destacada]
    else:
        entidades_destacadas = list(entidad_destacada) if entidad_destacada is not None else []
    for name, group in df.groupby(columna_entidad):
        alpha = 1 if name in entidades_destacadas else alpha_otras
        color = color_destacado if name in entidades_destacadas else color_otras
        ax.plot(group[columna_fecha], group[columna_valor],
               label=name if name in entidades_destacadas else "",
               alpha=alpha, color=color, linewidth=1.5)

def _configurar_ejes_lineas(ax, df, columna_fecha, columna_valor, intervalo_etiquetas=1):
    years = sorted(df[columna_fecha].unique())
    years_ticks = years[::intervalo_etiquetas] if intervalo_etiquetas > 1 else years
    ax.set_xticks(years_ticks)
    ax.set_xticklabels(years_ticks, rotation=0, ha='right', fontweight='bold')
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    y_min, y_max = df[columna_valor].min(), df[columna_valor].max()
    ax.set_yticks(np.linspace(y_min, y_max, num=5))
    ax.tick_params(axis='x', which='both', bottom=False, top=False)
    ax.tick_params(axis='y', which='both', left=False, right=False)
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(True)
    plt.tight_layout()

def _guardar_y_exportar_lineas(fig, nombre_df, output_dir):
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
    print(f"Gráfica de líneas de tendencia guardada como: {ruta_temporal}")
    return ruta_temporal

def generar_lineas_tendencia(df, **kwargs):
    """
    Genera una gráfica de líneas de tendencia usando matplotlib que produce PNG y SVG
    """
    try:
        columna_entidad = kwargs.get('columna_entidad', 'entity_name')
        columna_fecha = kwargs.get('columna_fecha', 'data_year')
        columna_valor = kwargs.get('columna_valor', 'data_value')
        nombre_archivo = kwargs.get('nombre_archivo', kwargs.get('nombre', 'lineas_tendencia'))
        entidad_destacada = kwargs.get('entidad_destacada', 'México')
        color_destacado = kwargs.get('color_destacado', '#8B0000')
        color_otras = kwargs.get('color_otras', '#10302C')
        alpha_otras = kwargs.get('alpha_otras', 0.3)
        intervalo_etiquetas = kwargs.get('intervalo_etiquetas', 1)
        output_dir = kwargs.get('output_dir', 'output')
        _validar_columnas_lineas(df, columna_entidad, columna_fecha, columna_valor)
        _configurar_fuentes_lineas()
        nombre_df = nombre_archivo or "lineas_tendencia"
        fig, ax = _configurar_figura_lineas()
        _graficar_lineas(ax, df, columna_entidad, columna_fecha, columna_valor, entidad_destacada, color_destacado, color_otras, alpha_otras)
        _configurar_ejes_lineas(ax, df, columna_fecha, columna_valor, intervalo_etiquetas)
        os.makedirs(output_dir, exist_ok=True)
        ruta = _guardar_y_exportar_lineas(fig, nombre_df, output_dir)
        return ruta
    except Exception as e:
        print(f"Error al generar gráfica de líneas de tendencia: {e}")
        return None
