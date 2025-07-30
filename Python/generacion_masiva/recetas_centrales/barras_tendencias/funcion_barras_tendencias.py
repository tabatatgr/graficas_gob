# Función para gráficas de barras de tendencias temporales
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager
from pathlib import Path
import os


def _configurar_fuentes(font, fontsize_titulo, fontsize_ejes, fontsize_etiquetas):
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
    return font_config

def _preparar_datos(df, columna_fecha, columna_indicador, columna_valor, columna_filtro=None, valor_filtro=None):
    data = df.copy()
    if columna_filtro and valor_filtro:
        data = data[data[columna_filtro] == valor_filtro]
    elif columna_filtro and columna_filtro in data.columns:
        unique_values = data[columna_filtro].unique()
        if len(unique_values) > 1:
            primer_valor = unique_values[0]
            data = data[data[columna_filtro] == primer_valor]
            print(f"Advertencia: Se detectaron múltiples valores en '{columna_filtro}'. Usando '{primer_valor}'")
    if not pd.api.types.is_datetime64_any_dtype(data[columna_fecha]):
        data[columna_fecha] = pd.to_datetime(data[columna_fecha])
    duplicados = data.duplicated(subset=[columna_fecha, columna_indicador])
    if duplicados.any():
        print(f"Advertencia: Se encontraron {duplicados.sum()} filas duplicadas, se eliminarán.")
        data = data.drop_duplicates(subset=[columna_fecha, columna_indicador])
    return data

def _crear_pivot(data, columna_fecha, columna_indicador, columna_valor, columnas_orden=None):
    pivot_df = data.pivot(
        index=columna_fecha,
        columns=columna_indicador,
        values=columna_valor
    ).fillna(0)
    if columnas_orden is not None:
        columnas_existentes = [col for col in columnas_orden if col in pivot_df.columns]
        pivot_df = pivot_df[columnas_existentes]
    return pivot_df

def _graficar_barras_apiladas(ax, pivot_df, paleta_colores, ancho_barras):
    pivot_df.plot(
        kind='bar',
        stacked=True,
        color=paleta_colores,
        ax=ax,
        width=ancho_barras
    )

def _configurar_grafico(ax, pivot_df, font_config, mostrar_titulo, titulo_personalizado, columna_filtro, valor_filtro, formato_fecha, intervalo_etiquetas, rotacion_etiquetas, mostrar_leyenda, mostrar_grid):
    # Título
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
    ax.set_xticks(range(0, len(pivot_df), intervalo_etiquetas))
    ax.set_xticklabels([date.strftime(formato_fecha) for date in pivot_df.index[::intervalo_etiquetas]],
                      rotation=rotacion_etiquetas,
                      fontsize=font_config['etiquetas']['size'],
                      fontfamily=font_config['family'])
    if mostrar_leyenda:
        ax.legend(title='',
                 frameon=False,
                 fontsize=font_config['etiquetas']['size'],
                 loc='upper center',
                 bbox_to_anchor=(0.5, -0.15),
                 ncol=2)
    else:
        ax.legend().remove()
    ax.grid(mostrar_grid)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(True)
    ax.spines['bottom'].set_visible(True)
    plt.tight_layout()

def _guardar_figura(fig, nombre, dpi):
    os.makedirs("output", exist_ok=True)
    base_path = f"output/{nombre}"
    original_svg_path = f"{base_path}.svg"
    png_path = f"{base_path}.png"
    fig.savefig(png_path, format="png", bbox_inches='tight', dpi=dpi, transparent=True)
    fig.savefig(original_svg_path, format="svg", bbox_inches='tight', dpi=dpi, transparent=True)

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
    usar_flujo_svg=False,
    columnas_orden=None,
    opciones_grafico=None,
    **kwargs
):
    """
    Genera gráficas de barras apiladas de tendencias temporales.
    """
    # Permitir agrupación de opciones visuales
    if opciones_grafico:
        mostrar_titulo = opciones_grafico.get('mostrar_titulo', mostrar_titulo)
        titulo_personalizado = opciones_grafico.get('titulo_personalizado', titulo_personalizado)
        mostrar_leyenda = opciones_grafico.get('mostrar_leyenda', mostrar_leyenda)
        mostrar_grid = opciones_grafico.get('mostrar_grid', mostrar_grid)
    font_config = _configurar_fuentes(font, fontsize_titulo, fontsize_ejes, fontsize_etiquetas)
    data = _preparar_datos(df, columna_fecha, columna_indicador, columna_valor, columna_filtro, valor_filtro)
    pivot_df = _crear_pivot(data, columna_fecha, columna_indicador, columna_valor, columnas_orden)
    if paleta_colores is None or len(paleta_colores) < 2:
        paleta_colores = ["#584290", "#b1adcf"]
    else:
        paleta_colores = paleta_colores[:2]
    fig, ax = plt.subplots(figsize=(ancho_figura, alto_figura), dpi=dpi)
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)
    _graficar_barras_apiladas(ax, pivot_df, paleta_colores, ancho_barras)
    _configurar_grafico(
        ax, pivot_df, font_config, mostrar_titulo, titulo_personalizado,
        columna_filtro, valor_filtro, formato_fecha, intervalo_etiquetas,
        rotacion_etiquetas, mostrar_leyenda, mostrar_grid
    )
    _guardar_figura(fig, nombre, dpi)
    plt.show()
