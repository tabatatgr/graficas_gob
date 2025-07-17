# Función para gráficas de barras de tendencias temporales
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager
from pathlib import Path
import os

def barras_tendencias(
    df,
    nombre="barras_tendencias",
    font='Arial',
    columna_fecha='fecha',
    columna_indicador='indicador',
    columna_valor='valor',
    columna_filtro=None,
    valor_filtro=None,
    paleta_colores=None,
    ancho_figura=12,
    alto_figura=6,
    dpi=300,
    intervalo_etiquetas=12,
    formato_fecha='%Y',
    rotacion_etiquetas=45,
    fontsize_etiquetas=8,
    fontsize_titulo=14,
    fontsize_ejes=12,
    mostrar_titulo=True,
    titulo_personalizado=None,
    mostrar_leyenda=True,
    mostrar_grid=False,
    ancho_barras=1.0,
    usar_flujo_svg=False,    # ← Optimización SVG para Figma
    **kwargs
):
    """
    Genera gráficas de barras apiladas de tendencias temporales.

    Args:
        df (pd.DataFrame): DataFrame con los datos
        nombre (str): Nombre del archivo de salida
        font (str): Fuente a utilizar
        columna_fecha (str): Nombre de la columna de fechas
        columna_indicador (str): Nombre de la columna de indicadores/categorías
        columna_valor (str): Nombre de la columna de valores
        columna_filtro (str): Columna para filtrar datos (ej: 'estado')
        valor_filtro (str): Valor específico para filtrar
        paleta_colores (list): Colores personalizados
        ancho_figura (int): Ancho de la figura
        alto_figura (int): Alto de la figura
        dpi (int): Resolución
        intervalo_etiquetas (int): Intervalo entre etiquetas del eje X
        formato_fecha (str): Formato para las fechas
        rotacion_etiquetas (int): Rotación de las etiquetas
        fontsize_etiquetas (int): Tamaño de fuente de etiquetas
        fontsize_titulo (int): Tamaño de fuente del título
        fontsize_ejes (int): Tamaño de fuente de los ejes
        mostrar_titulo (bool): Mostrar título
        titulo_personalizado (str): Título personalizado
        mostrar_leyenda (bool): Mostrar leyenda
        mostrar_grid (bool): Mostrar grid
        ancho_barras (float): Ancho de las barras
    """

    # Configuración de fuentes
    font_config = {
        'family': font,
        'titulo': {'size': fontsize_titulo, 'weight': 'bold', 'color': '#000000'},
        'ejes': {'size': fontsize_ejes, 'weight': 'medium', 'color': '#000000'},
        'etiquetas': {'size': fontsize_etiquetas, 'weight': 'medium', 'color': '#000000'},
    }

    plt.rcParams['svg.fonttype'] = 'none'
    font_dirs = [Path("../0_fonts")]
    font_files = font_manager.findSystemFonts(fontpaths=font_dirs)
    for font_file in font_files:
        font_manager.fontManager.addfont(font_file)

    # Preparar datos
    data = df.copy()
    
    # Filtrar datos si se especifica
    if columna_filtro and valor_filtro:
        data = data[data[columna_filtro] == valor_filtro]
    
    # Si no hay filtro pero hay múltiples valores en columna_filtro, tomar el primero
    elif columna_filtro and columna_filtro in data.columns:
        unique_values = data[columna_filtro].unique()
        if len(unique_values) > 1:
            primer_valor = unique_values[0]
            data = data[data[columna_filtro] == primer_valor]
            print(f"Advertencia: Se detectaron múltiples valores en '{columna_filtro}'. Usando '{primer_valor}'")
    
    # Asegurar que la columna de fecha sea datetime
    if not pd.api.types.is_datetime64_any_dtype(data[columna_fecha]):
        data[columna_fecha] = pd.to_datetime(data[columna_fecha])
    
    # Verificar que no hay duplicados antes de hacer pivot
    duplicados = data.duplicated(subset=[columna_fecha, columna_indicador])
    if duplicados.any():
        print(f"Advertencia: Se encontraron {duplicados.sum()} filas duplicadas, se eliminarán.")
        data = data.drop_duplicates(subset=[columna_fecha, columna_indicador])
    
    # Crear tabla pivot
    pivot_df = data.pivot(
        index=columna_fecha, 
        columns=columna_indicador, 
        values=columna_valor
    ).fillna(0)
    
    # Asegurar que las columnas están en el orden correcto
    columnas_orden = ['Con datos', 'Sin datos']
    pivot_df = pivot_df[columnas_orden]
    
    # Colores específicos para Con datos/Sin datos
    paleta_colores = ["#584290", "#b1adcf"]
    
    # Crear figura
    fig, ax = plt.subplots(figsize=(ancho_figura, alto_figura), dpi=dpi)
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)
    
    # Crear gráfico de barras apiladas
    pivot_df.plot(
        kind='bar', 
        stacked=True, 
        color=paleta_colores, 
        ax=ax, 
        width=ancho_barras
    )
    
    # Configurar título
    if mostrar_titulo:
        if titulo_personalizado:
            titulo = titulo_personalizado
        elif columna_filtro and valor_filtro:
            titulo = f'{valor_filtro} - Casos con y sin datos'
        else:
            titulo = 'Casos con y sin datos'
        
        ax.set_title(titulo, 
                    fontsize=font_config['titulo']['size'],
                    fontweight=font_config['titulo']['weight'],
                    color=font_config['titulo']['color'],
                    fontfamily=font_config['family'])
    
    # Configurar ejes
    ax.set_xlabel('Fecha', 
                  fontsize=font_config['ejes']['size'],
                  fontweight=font_config['ejes']['weight'],
                  color=font_config['ejes']['color'],
                  fontfamily=font_config['family'])
    
    ax.set_ylabel('Número de casos', 
                  fontsize=font_config['ejes']['size'],
                  fontweight=font_config['ejes']['weight'],
                  color=font_config['ejes']['color'],
                  fontfamily=font_config['family'])
    
    # Configurar etiquetas del eje X
    ax.set_xticks(range(0, len(pivot_df), intervalo_etiquetas))
    ax.set_xticklabels([date.strftime(formato_fecha) for date in pivot_df.index[::intervalo_etiquetas]], 
                      rotation=rotacion_etiquetas, 
                      fontsize=font_config['etiquetas']['size'],
                      fontfamily=font_config['family'])
    
    # Configurar leyenda
    if mostrar_leyenda:
        ax.legend(title='', 
                 frameon=False,
                 fontsize=font_config['etiquetas']['size'],
                 loc='upper center',  # Centrado
                 bbox_to_anchor=(0.5, -0.15),  # Debajo de la gráfica
                 ncol=2)  # Mostrar en una sola fila
    else:
        ax.legend().remove()
    
    # Configurar grid
    ax.grid(mostrar_grid)
    
    # Configurar bordes
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(True)
    ax.spines['bottom'].set_visible(True)
    
    plt.tight_layout()

    # --- GUARDADO Y VISUALIZACIÓN ---
    os.makedirs("output", exist_ok=True)
    
    base_path = f"output/{nombre}"
    original_svg_path = f"{base_path}.svg"
    scour_svg_path = f"{base_path}_scour.svg"
    png_path = f"{base_path}.png"
    
    # Guardar en múltiples formatos
    plt.savefig(png_path, format="png", bbox_inches='tight', dpi=dpi, transparent=True)
    plt.savefig(original_svg_path, format="svg", bbox_inches='tight', dpi=dpi, transparent=True)
    
    # Dejar que grafico_cli.py maneje la optimización SVG
    plt.show()
