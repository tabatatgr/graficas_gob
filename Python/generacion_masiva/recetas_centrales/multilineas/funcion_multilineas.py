
import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.font_manager as font_manager
import subprocess
import os
from .helpers_multilineas import ajusta_etiquetas


def _validar_columnas_multilineas(df, columna_fecha, columna_serie, columna_valor):
    if columna_fecha not in df.columns:
        raise ValueError(f"La columna '{columna_fecha}' no existe en el DataFrame.")
    if columna_serie not in df.columns:
        raise ValueError(f"La columna '{columna_serie}' no existe en el DataFrame.")
    if columna_valor not in df.columns:
        raise ValueError(f"La columna '{columna_valor}' no existe en el DataFrame.")

def _configurar_fuentes_multilineas(font):
    font_config = {
        'family': font,
        'variable_x': {'size': 24, 'weight': 'semibold', 'color': '#767676'},
        'variable_y': {'size': 24, 'weight': 'medium', 'color': '#767676'},
        'capsula_valor': {'size': 12, 'weight': 'medium', 'color': '#ffffff'},
        'leyenda': {'size': 20, 'weight': 'medium'}  # color se asignará por serie
    }
    plt.rcParams['svg.fonttype'] = 'none'
    font_dirs = [Path("../0_fonts")]
    font_files = font_manager.findSystemFonts(fontpaths=font_dirs)
    for font_file in font_files:
        font_manager.fontManager.addfont(font_file)
    return font_config

def _configurar_figura_multilineas():
    ancho_px = 1480
    alto_px = 520
    dpi = 100
    ancho_in = ancho_px / dpi
    alto_in = alto_px / dpi
    fig, ax = plt.subplots(figsize=(ancho_in, alto_in), dpi=dpi)
    return fig, ax

def _asignar_colores_multilineas(series):
    colores_asignados = ["#006157", "#767676", "#671435", "#9B2247", "#9D792A", "#D5B162"]
    color_map = {serie: colores_asignados[i % len(colores_asignados)] for i, serie in enumerate(series)}
    return color_map

def _graficar_multilineas(ax, df, columna_fecha, columna_serie, columna_valor, color_map):
    series = df[columna_serie].unique()
    for serie in series:
        datos = df[df[columna_serie] == serie]
        ax.plot(
            datos[columna_fecha],
            datos[columna_valor],
            label=serie,
            color=color_map[serie],
            linewidth=2
        )
        ax.scatter(
            datos[columna_fecha],
            datos[columna_valor],
            color=color_map[serie],
            s=40,
            zorder=3
        )

def _agregar_etiquetas_multilineas(ax, df, columna_fecha, columna_serie, columna_valor, color_map, font_config, borde_capsula, sin_tag, escala):
    # Usa el helper genérico para etiquetas
    all_texts = []
    series = df[columna_serie].unique()
    for serie in series:
        datos = df[df[columna_serie] == serie].reset_index(drop=True)
        all_texts.extend(
            ajusta_etiquetas(
                datos,
                columnas=[columna_valor],
                colores=[color_map[serie]],
                columna_x=columna_fecha,
                sin_tag=sin_tag,
                max=True,
                fontsize=font_config['capsula_valor']['size'],
                fontname=font_config['family'],
                fontweight=font_config['capsula_valor']['weight'],
                fontcolor=font_config['capsula_valor']['color'],
                escala=abs(escala) * 0.03 if escala else 10
            )
        )
    return all_texts

def _ajustar_etiquetas_multilineas(adjust_text, all_texts):
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

def _configurar_leyenda_multilineas(ax, series, font_config, color_map):
    leg = ax.legend(
        loc='upper center',
        bbox_to_anchor=(0.5, 1.2),
        ncol=len(series),
        frameon=False,
        prop={
            'size': font_config['leyenda']['size'],
            'weight': font_config['leyenda']['weight'],
            'family': font_config['family']
        }
    )
    for text, serie in zip(leg.get_texts(), series):
        text.set_color(color_map[serie])

def _configurar_ejes_multilineas(ax, font_config):
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
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_linewidth(1.5)
    ax.grid(axis='y', linestyle='-', color='#000000', alpha=0.2, linewidth=0.75)
    ax.grid(axis='x', linestyle='-', color='#000000', alpha=0.2, linewidth=0.75)
    ax.yaxis.set_ticks_position('left')
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))

def _guardar_y_exportar_multilineas(fig, nombre_df, output_dir):
    left_margin = 0.15
    right_margin = 0.95
    bottom_margin = 0.2
    top_margin = 0.95
    plt.subplots_adjust(left=left_margin, right=right_margin, top=top_margin, bottom=bottom_margin)
    nombre_archivo_svg = f"{nombre_df}.svg"
    ruta_temporal = os.path.join(output_dir, nombre_archivo_svg)
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
    print(f"Gráfica de multilineas guardada como: {ruta_temporal}")
    return ruta_temporal

def generar_multilineas(df, **kwargs):
    """
    Genera una gráfica de multilineas usando matplotlib que produce PNG y SVG.
    Si no se especifican columnas, las infiere automáticamente del DataFrame.
    """
    try:
        try:
            from adjustText import adjust_text
        except ImportError:
            print("Advertencia: adjustText no está disponible. Las etiquetas pueden solaparse.")
            adjust_text = None

        # Inferencia automática de columnas si no se pasan explícitamente
        def inferir_columnas(df):
            # Heurística: buscar nombres comunes y tipos
            posibles_fechas = [c for c in df.columns if c.lower() in ['fecha', 'periodo', 'period', 'date']]
            posibles_series = [c for c in df.columns if c.lower() in ['variable', 'serie', 'categoria', 'categoría', 'grupo', 'entidad', 'serie', 'serie_nombre']]
            posibles_valores = [c for c in df.columns if df[c].dtype.kind in 'fi' and c.lower() not in posibles_fechas + posibles_series]
            columna_fecha = posibles_fechas[0] if posibles_fechas else df.columns[0]
            columna_serie = posibles_series[0] if posibles_series else df.columns[1]
            columna_valor = posibles_valores[0] if posibles_valores else df.columns[-1]
            return columna_fecha, columna_serie, columna_valor

        columna_fecha = kwargs.get('columna_fecha')
        columna_serie = kwargs.get('columna_serie', kwargs.get('columna_variable'))
        columna_valor = kwargs.get('columna_valor')
        if not (columna_fecha and columna_serie and columna_valor):
            inf_fecha, inf_serie, inf_valor = inferir_columnas(df)
            columna_fecha = columna_fecha or inf_fecha
            columna_serie = columna_serie or inf_serie
            columna_valor = columna_valor or inf_valor

        nombre_archivo = kwargs.get('nombre_archivo', kwargs.get('nombre', 'multilineas'))
        font = kwargs.get('font', 'Arial')
        borde_capsula = kwargs.get('borde_capsula', kwargs.get('margen', 0.7))
        sin_tag = kwargs.get('sin_tag', 2)
        output_dir = kwargs.get('output_dir', 'output')
        _validar_columnas_multilineas(df, columna_fecha, columna_serie, columna_valor)
        font_config = _configurar_fuentes_multilineas(font)
        fig, ax = _configurar_figura_multilineas()
        series = df[columna_serie].unique()
        color_map = _asignar_colores_multilineas(series)
        _graficar_multilineas(ax, df, columna_fecha, columna_serie, columna_valor, color_map)
        escala = df[columna_valor].max() - df[columna_valor].min()
        all_texts = _agregar_etiquetas_multilineas(
            ax, df, columna_fecha, columna_serie, columna_valor, color_map, font_config, borde_capsula, sin_tag, escala
        )
        _ajustar_etiquetas_multilineas(adjust_text, all_texts)
        _configurar_leyenda_multilineas(ax, series, font_config, color_map)
        _configurar_ejes_multilineas(ax, font_config)
        nombre_df = nombre_archivo or "multilineas"
        os.makedirs(output_dir, exist_ok=True)
        ruta_svg = _guardar_y_exportar_multilineas(fig, nombre_df, output_dir)
        # Exportar también a PNG
        nombre_archivo_png = f"{nombre_df}.png"
        ruta_png = os.path.join(output_dir, nombre_archivo_png)
        fig.savefig(ruta_png, format='png', dpi=300, transparent=True)
        print(f"Gráfica de multilineas guardada como: {ruta_png}")
        return {'svg': ruta_svg, 'png': ruta_png}
    except Exception as e:
        print(f"Error al generar gráfica de multilineas: {e}")
        return None
