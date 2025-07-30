"""
Función modular para la generación de gráficas treemap.
Esta función genera gráficas treemap en formato PNG y SVG optimizado.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager
import squarify
import pandas as pd
from pathlib import Path
import os


def _configurar_fuentes_treemap(kwargs):
    ZORDER_TEXTO = kwargs.get('zorder_texto', 10)
    font_config = {
        'family': kwargs.get('font', 'Montserrat'),
        'etiquetas': {
            'size': kwargs.get('fontsize_etiqueta', 26),
            'weight': 'bold',
            'color': '#ffffff',
            'zorder': ZORDER_TEXTO
        },
        'valor': {
            'size': kwargs.get('fontsize_valor', 26),
            'weight': 'bold',
            'color': '#ffffff',
            'zorder': ZORDER_TEXTO
        },
        'porcentaje': {
            'size': kwargs.get('fontsize_porcentaje', 26),
            'weight': 'medium',
            'color': '#ffffff',
            'zorder': ZORDER_TEXTO
        }
    }
    plt.rcParams['svg.fonttype'] = 'none'
    font_paths = [
        Path("Python/0_fonts"),
        Path("../0_fonts"),
        Path("0_fonts"),
        Path("../../0_fonts")
    ]
    font_dir = next((d for d in font_paths if d.exists()), None)
    if font_dir:
        font_files = font_manager.findSystemFonts(fontpaths=[font_dir])
        for font_file in font_files:
            font_manager.fontManager.addfont(font_file)
    return font_config

def _inferir_columnas_treemap(df, kwargs):
    col_etiqueta = kwargs.get('columna_etiqueta')
    col_valor = kwargs.get('columna_valor')
    if not col_etiqueta:
        # Heurística: buscar nombres comunes
        posibles = [c for c in df.columns if c.lower() in ['entidad federativa', 'entidad', 'categoria', 'categoría', 'grupo', 'nombre', 'label']]
        col_etiqueta = posibles[0] if posibles else df.columns[0]
    if not col_valor:
        posibles = [c for c in df.columns if df[c].dtype.kind in 'fi']
        col_valor = posibles[0] if posibles else df.columns[-1]
    return col_etiqueta, col_valor

def _asignar_colores_treemap(df, col_valor, colores=None):
    if colores and isinstance(colores, list) and len(colores) >= 2:
        color_max, color_otros = colores[0], colores[1]
    else:
        color_max, color_otros = '#10302C', '#4C6A67'
    max_valor = df[col_valor].max()
    return [color_max if val == max_valor else color_otros for val in df[col_valor]]

def _configurar_figura_treemap(font_family):
    plt.rc('font', family=font_family)
    fig, ax = plt.subplots(figsize=(16, 10), dpi=300)
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    return fig, ax

def _calcular_fontsize(area, base):
    if area > 0.08:
        return base
    elif area > 0.06:
        return int(base * 20 / 26)
    elif area > 0.04:
        return int(base * 18 / 26)
    elif area > 0.02:
        return int(base * 14 / 26)
    elif area > 0.01:
        return int(base * 11 / 26)
    elif area > 0.005:
        return int(base * 9 / 26)
    else:
        return int(base * 5 / 26)

def _dibujar_treemap(ax, df, rectangles, colores, col_etiqueta, col_valor, font_config, area_min):
    # ADVERTENCIA: Si los nombres de entidad son muy largos, el texto puede desbordar el rectángulo.
    # Considera recortar o ajustar manualmente si tienes casos extremos.
    for rect, (_, row), color in zip(rectangles, df.iterrows(), colores):
        x, y, dx, dy = rect['x'], rect['y'], rect['dx'], rect['dy']
        ax.add_patch(plt.Rectangle(
            (x, y), dx, dy,
            facecolor=color,
            edgecolor='white',
            linewidth=1
        ))
        area = dx * dy
        if area > area_min:
            entidad = row[col_etiqueta]
            palabras = str(entidad).split()
            if len(palabras) > 2:
                entidad_mod = '\n'.join([' '.join(palabras[i:i+2]) for i in range(0, len(palabras), 2)])
            else:
                entidad_mod = entidad
            fontsize_et = _calcular_fontsize(area, font_config['etiquetas']['size'])
            fontsize_val = _calcular_fontsize(area, font_config['valor']['size'])
            fontsize_pct = _calcular_fontsize(area, font_config['porcentaje']['size'])
            x_text = x + dx * 0.04
            y_text = y + dy * 0.55
            y_text2 = y_text - dy * 0.18
            y_text3 = y_text2 - dy * 0.18
            ax.text(
                x_text, y_text, entidad_mod,
                ha='left', va='bottom',
                fontsize=fontsize_et,
                fontweight=font_config['etiquetas']['weight'],
                color=font_config['etiquetas']['color'],
                zorder=font_config['etiquetas'].get('zorder', 10)
            )
            # Valor numérico robusto
            valor = row[col_valor]
            if isinstance(valor, float) and not valor.is_integer():
                valor_str = f"{valor:,.2f}"
            else:
                valor_str = f"{int(round(valor)):,}"
            ax.text(
                x_text, y_text2, valor_str,
                ha='left', va='bottom',
                fontsize=fontsize_val,
                fontweight=font_config['valor']['weight'],
                color=font_config['valor']['color'],
                zorder=font_config['valor'].get('zorder', 10)
            )
            ax.text(
                x_text, y_text3, f"{row['Porcentaje']}%",
                ha='left', va='bottom',
                fontsize=fontsize_pct,
                fontweight=font_config['porcentaje']['weight'],
                color=font_config['porcentaje']['color'],
                zorder=font_config['porcentaje'].get('zorder', 10)
            )

def _guardar_treemap(fig, output_dir, nombre_base):
    archivo_png = os.path.join(output_dir, f"{nombre_base}.png")
    archivo_svg = os.path.join(output_dir, f"{nombre_base}.svg")
    fig.savefig(archivo_png, format='png', bbox_inches='tight', dpi=300, transparent=True)
    fig.savefig(archivo_svg, format='svg', bbox_inches='tight')
    plt.close(fig)
    return {'png': archivo_png, 'svg': archivo_svg}

def generar_treemap(df, **kwargs):
    """
    Genera una gráfica treemap usando los datos y parámetros proporcionados.
    Si no se especifican columnas, las infiere automáticamente.
    Puedes personalizar los colores principales pasando una lista en 'colores': [color_max, color_otros].
    Si los nombres de entidad son muy largos, el texto puede desbordar el rectángulo.
    """
    output_dir = kwargs.get('output_dir', 'output')
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    font_config = _configurar_fuentes_treemap(kwargs)
    col_etiqueta, col_valor = _inferir_columnas_treemap(df, kwargs)
    df[col_valor] = pd.to_numeric(df[col_valor], errors='coerce').fillna(0).astype(float)
    df = df.sort_values(by=col_valor, ascending=False).copy()
    total_nacional = df[col_valor].sum()
    df['Porcentaje'] = (df[col_valor] / total_nacional * 100).round(1)
    colores = _asignar_colores_treemap(df, col_valor, kwargs.get('colores'))
    fig, ax = _configurar_figura_treemap(font_config['family'])
    sizes = df[col_valor].tolist()
    rectangles = squarify.normalize_sizes(sizes, 1, 1)
    rectangles = squarify.squarify(rectangles, 0, 0, 1, 1)
    area_min = kwargs.get('area_min', 0.001)
    _dibujar_treemap(ax, df, rectangles, colores, col_etiqueta, col_valor, font_config, area_min)
    ax.axis('off')
    plt.tight_layout()
    nombre_base = kwargs.get('nombre', 'treemap')
    return _guardar_treemap(fig, output_dir, nombre_base)
