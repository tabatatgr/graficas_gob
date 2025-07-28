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

def generar_treemap(df, **kwargs):
    """
    Genera una gráfica treemap usando los datos y parámetros proporcionados.
    
    Args:
        df (pd.DataFrame): DataFrame con los datos
        **kwargs: Parámetros de configuración de la gráfica
    """
    # Directorio de salida por defecto
    output_dir = kwargs.get('output_dir', 'output')
    
    # Crear directorio de salida si no existe
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Configurar fuentes
    font_config = {
        'family': kwargs.get('font', 'Montserrat'),
        'etiquetas': {
            'size': kwargs.get('fontsize_etiqueta', 26), 
            'weight': 'bold', 
            'color': '#ffffff'
        },
        'valor': {
            'size': kwargs.get('fontsize_valor', 26), 
            'weight': 'bold', 
            'color': '#ffffff'
        },
        'porcentaje': {
            'size': kwargs.get('fontsize_porcentaje', 26), 
            'weight': 'medium', 
            'color': '#ffffff'
        }
    }
    
    plt.rcParams['svg.fonttype'] = 'none'
    
    # Cargar fuentes desde directorios posibles
    font_paths = [
        Path("Python/0_fonts"),
        Path("../0_fonts"),
        Path("0_fonts"),
        Path("../../0_fonts")
    ]
    
    for font_dir in font_paths:
        if font_dir.exists():
            font_files = font_manager.findSystemFonts(fontpaths=[font_dir])
            for font_file in font_files:
                font_manager.fontManager.addfont(font_file)
            break
    
    # Obtener nombres de columnas de los kwargs
    col_etiqueta = kwargs.get('columna_etiqueta', 'ENTIDAD FEDERATIVA')
    col_valor = kwargs.get('columna_valor', 'NUMERO DE VICTIMAS')
    
    # Asegurar que todos los valores sean numéricos tipo float
    df[col_valor] = pd.to_numeric(df[col_valor], errors='coerce').fillna(0).astype(float)
    
    # Ordenar y calcular porcentaje
    df = df.sort_values(by=col_valor, ascending=False).copy()
    total_nacional = df[col_valor].sum()
    df['Porcentaje'] = (df[col_valor] / total_nacional * 100).round(1)
    
    # Colores
    max_valor = df[col_valor].max()
    colores = ['#10302C' if val == max_valor else '#4C6A67' for val in df[col_valor]]
    
    # Configurar la figura
    plt.rc('font', family=font_config['family'])
    fig, ax = plt.subplots(figsize=(16, 10), dpi=300)
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    
    # Crear rectángulos
    sizes = df[col_valor].tolist()
    rectangles = squarify.normalize_sizes(sizes, 1, 1)
    rectangles = squarify.squarify(rectangles, 0, 0, 1, 1)
    
    # Función para calcular tamaño de fuente basado en área
    def calcular_fontsize(area, base):
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
    
    area_min = kwargs.get('area_min', 0.001)
    
    # Dibujar rectángulos y etiquetas
    for rect, (_, row), color in zip(rectangles, df.iterrows(), colores):
        x, y, dx, dy = rect['x'], rect['y'], rect['dx'], rect['dy']
        
        # Dibujar rectángulo
        ax.add_patch(plt.Rectangle(
            (x, y), dx, dy,
            facecolor=color,
            edgecolor='white',
            linewidth=1
        ))
        
        area = dx * dy
        
        # Añadir etiquetas solo si el área es suficiente
        if area > area_min:
            entidad = row[col_etiqueta]
            palabras = entidad.split()
            
            # Dividir texto en líneas si es muy largo
            if len(palabras) > 2:
                entidad_mod = '\n'.join([' '.join(palabras[i:i+2]) for i in range(0, len(palabras), 2)])
            else:
                entidad_mod = entidad
            
            # Ajuste de tamaño de fuente según área
            fontsize_et = calcular_fontsize(area, font_config['etiquetas']['size'])
            fontsize_val = calcular_fontsize(area, font_config['valor']['size'])
            fontsize_pct = calcular_fontsize(area, font_config['porcentaje']['size'])
            
            # Posiciones del texto
            x_text = x + dx * 0.04
            y_text = y + dy * 0.55
            y_text2 = y_text - dy * 0.18
            y_text3 = y_text2 - dy * 0.18
            
            # Etiqueta de entidad
            ax.text(
                x_text, y_text, entidad_mod,
                ha='left', va='bottom',
                fontsize=fontsize_et,
                fontweight=font_config['etiquetas']['weight'],
                color=font_config['etiquetas']['color'],
                zorder=10
            )
            
            # Valor numérico
            ax.text(
                x_text, y_text2, f"{int(row[col_valor]):,}",
                ha='left', va='bottom',
                fontsize=fontsize_val,
                fontweight=font_config['valor']['weight'],
                color=font_config['valor']['color'],
                zorder=10
            )
            
            # Porcentaje
            ax.text(
                x_text, y_text3, f"{row['Porcentaje']}%",
                ha='left', va='bottom',
                fontsize=fontsize_pct,
                fontweight=font_config['porcentaje']['weight'],
                color=font_config['porcentaje']['color'],
                zorder=10
            )
    
    ax.axis('off')
    plt.tight_layout()
    
    # Generar nombres de archivo y guardar
    nombre_base = kwargs.get('nombre', 'treemap')
    archivo_png = os.path.join(output_dir, f"{nombre_base}.png")
    archivo_svg = os.path.join(output_dir, f"{nombre_base}.svg")
    
    plt.savefig(archivo_png, format='png', bbox_inches='tight', dpi=300, transparent=True)
    plt.savefig(archivo_svg, format='svg', bbox_inches='tight')
    plt.close()
    
    return {
        'png': archivo_png,
        'svg': archivo_svg
    }
