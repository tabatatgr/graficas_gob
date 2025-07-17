# Función para gráficas de área apilada
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager
from pathlib import Path
from scipy.interpolate import make_interp_spline
import os
import sys

# Importar el flujo de exportación SVG
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))
from svg_cleanup.flujo_exportacion import exportar_grafica

def formato_fechas(fechas):
    """Formatea fechas para mostrar en el eje X"""
    import pandas as pd
    fechas = pd.to_datetime(fechas)
    # Si todos los años son diferentes, mostrar solo el año
    if len(set(f.year for f in fechas)) == len(fechas):
        return [str(f.year) for f in fechas]
    else:
        return [f.strftime("%d-%m-%Y") for f in fechas]

def areaplot(
    df,
    nombre="areaplot",
    font='Arial',
    mostrar_capsulas=True,
    columna_fechas='fechas',
    columnas_series=None,
    etiquetas_series=None,
    paleta_colores=None,
    suavizado=True,
    puntos_suavizado=300,
    formato_fecha='%b %Y',
    mostrar_porcentajes=True,
    ancho_figura=16,
    alto_figura=8,
    dpi=100,
    rotacion_etiquetas=90,
    posicion_leyenda=(0.5, 1.12),
    ncol_leyenda=3,
    mostrar_snapshot=False,  # ← Nueva funcionalidad
    snapshot_width_ratio=4,  # ← Ratio de ancho (área:snapshot)
    mostrar_leyenda=False,   # ← Control de leyenda
    usar_flujo_svg=False,    # ← Optimización SVG para Figma
    **kwargs
):
    """
    Genera un gráfico de área apilada con los datos proporcionados en un DataFrame.

    Args:
        df (pd.DataFrame): DataFrame con los datos
        nombre (str): Nombre del archivo de salida
        font (str): Fuente a utilizar
        mostrar_capsulas (bool): Mostrar cápsulas con totales
        columna_fechas (str): Nombre de la columna de fechas/categorías
        columnas_series (list): Lista de columnas para las series (si None, usa todas excepto fechas)
        etiquetas_series (list): Etiquetas personalizadas para las series
        paleta_colores (list): Colores personalizados para las áreas
        suavizado (bool): Aplicar suavizado a las curvas
        puntos_suavizado (int): Número de puntos para el suavizado
        formato_fecha (str): Formato para las fechas
        mostrar_porcentajes (bool): Mostrar eje Y como porcentajes
        ancho_figura (int): Ancho de la figura
        alto_figura (int): Alto de la figura
        dpi (int): Resolución
        rotacion_etiquetas (int): Rotación de etiquetas del eje X
        posicion_leyenda (tuple): Posición de la leyenda
        ncol_leyenda (int): Número de columnas en la leyenda
        mostrar_snapshot (bool): Mostrar barra lateral con snapshot de porcentajes
        snapshot_width_ratio (int): Ratio de ancho entre área principal y snapshot
        mostrar_leyenda (bool): Mostrar leyenda
    """

    # Configuración de fuentes
    font_config = {
        'family': font,
        'titulo': {'size': 16, 'weight': 'bold', 'color': '#10302C'},
        'eje_y': {'size': 24, 'weight': 'medium', 'color': '#767676'},
        'eje_x': {'size': 24, 'weight': 'semibold', 'color': '#767676'},
        'capsula_valor': {'size': 20, 'weight': 'medium', 'color': '#10302C'},
        'capsula_max': {'size': 12, 'weight': 'medium', 'color': 'white'},
        'porcentaje': {'size': 10, 'weight': 'medium', 'color': '#4C6A67'},
        'leyenda': {'size': 20, 'weight': 'medium', 'color': '#767676'}
    }

    plt.rcParams['svg.fonttype'] = 'none'
    font_dirs = [Path("../0_fonts")]
    font_files = font_manager.findSystemFonts(fontpaths=font_dirs)
    for font_file in font_files:
        font_manager.fontManager.addfont(font_file)

    # Preparar datos
    data = df.copy()
    
    # Obtener columnas de series
    if columnas_series is None:
        columnas_series = [col for col in data.columns if col != columna_fechas]
    
    # Obtener etiquetas de series
    if etiquetas_series is None:
        etiquetas_series = columnas_series
    
    # Colores por defecto
    if paleta_colores is None:
        paleta_colores = ['#215F53', '#7570B3', '#C7EAE5', '#A3C9A8', '#8FA8A6', '#4C6A67']
    
    # Extraer fechas
    fechas = data[columna_fechas]
    
    # Procesar fechas
    if not np.issubdtype(fechas.dtype, np.datetime64):
        fechas = fechas.astype(str)
    else:
        fechas = fechas.dt.strftime(formato_fecha)
        data = data.sort_values(columna_fechas)

    # Preparar datos para normalización (necesario para snapshot)
    valores = [data[col].values for col in columnas_series]
    
    # Normalizar si es necesario para snapshot
    if mostrar_snapshot:
        total = np.sum(valores, axis=0)
        total[total == 0] = 1  # Evitar división por cero
        valores_norm = [v / total for v in valores]
    else:
        valores_norm = valores

    # Crear figura con o sin snapshot
    if mostrar_snapshot:
        fig = plt.figure(figsize=(ancho_figura, alto_figura), dpi=dpi)
        gs = fig.add_gridspec(1, 2, width_ratios=[snapshot_width_ratio, 1], height_ratios=[1])
        ax = fig.add_subplot(gs[0])
        ax_snapshot = fig.add_subplot(gs[1])
    else:
        fig, ax = plt.subplots(figsize=(ancho_figura, alto_figura), dpi=dpi)
        ax_snapshot = None
    
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)
    
    n = len(fechas)
    x = np.arange(n) + 0.5  # Desfase visual

    # Preparar datos para stackplot (usar datos normalizados si es snapshot)
    series_data = valores_norm if mostrar_snapshot else valores

    if suavizado:
        # Suavizar las curvas
        x_suave = np.linspace(x.min(), x.max(), puntos_suavizado)
        series_suaves = []
        for serie in series_data:
            serie_suave = make_interp_spline(x, serie)(x_suave)
            if mostrar_snapshot:
                # Para snapshot, forzar límites y normalizar
                serie_suave = np.clip(serie_suave, 0, 1)
            series_suaves.append(serie_suave)
        
        # Renormalizar si es snapshot
        if mostrar_snapshot:
            suma_suave = np.sum(series_suaves, axis=0)
            suma_suave[suma_suave == 0] = 1
            series_suaves = [s / suma_suave for s in series_suaves]
        
        # Área apilada suavizada
        ax.stackplot(x_suave, *series_suaves, labels=etiquetas_series, colors=paleta_colores[:len(series_suaves)])
    else:
        # Área apilada sin suavizar
        ax.stackplot(x, *series_data, labels=etiquetas_series, colors=paleta_colores[:len(series_data)])

    # Configurar eje X
    ax.set_xticks(x)
    fechas_formateadas = formato_fechas(data[columna_fechas]) if pd.api.types.is_datetime64_any_dtype(data[columna_fechas]) else fechas
    ax.set_xticklabels(fechas_formateadas, rotation=rotacion_etiquetas, 
                      fontsize=font_config['eje_x']['size'],
                      fontweight=font_config['eje_x']['weight'], 
                      color=font_config['eje_x']['color'])
    ax.set_xlim(x[0] - 0.5, x[-1] + 0.5)

    # Configurar eje Y
    if mostrar_porcentajes:
        ax.set_yticks(np.linspace(0, 1, 5))
        # Usar el tamaño personalizado si está definido
        tamano_etiquetas = kwargs.get('tamano_etiquetas_y', font_config['eje_y']['size'])
        ax.set_yticklabels(['0%', '25%', '50%', '75%', '100%'], 
                        fontsize=tamano_etiquetas,
                        fontweight=font_config['eje_y']['weight'], 
                        color=font_config['eje_y']['color'],
                        verticalalignment='center')  # Alinear verticalmente las etiquetas
        ax.set_ylabel('Porcentaje', fontsize=tamano_etiquetas,
                    fontweight=font_config['eje_y']['weight'], 
                    color=font_config['eje_y']['color'],
                    labelpad=kwargs.get('espacio_etiquetas_y', 20))  # Aumentar el espacio para la etiqueta Y
        
        # Ajustar los márgenes
        left_margin = kwargs.get('margen_izquierdo', 0.15)
        right_margin = kwargs.get('padding_derecho', 0.95)
        plt.subplots_adjust(left=left_margin, right=right_margin)

        # Límite fijo para porcentajes
        ylim_sup = 1
    else:
        ax.tick_params(axis='y', 
                    labelsize=font_config['eje_y']['size'], 
                    labelcolor=font_config['eje_y']['color'])

        # Calcular el máximo de los datos apilados reales
        y_max = np.max(np.sum(series_data, axis=0))
        ylim_sup = y_max * 1.05  # margen de respiro arriba

    # Aplicar siempre el límite del eje Y
    ax.set_ylim(0, ylim_sup)


    # Configurar bordes y grid
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_linewidth(2)
    ax.grid(axis='y', linestyle='-', color='white', alpha=0.8, linewidth=1.25)
    ax.grid(axis='x', linestyle='-', color='white', alpha=0.3, linewidth=0.75)

    
    # capsulas
    if mostrar_capsulas:
        # Calcular totales de cada serie
        totales = [round(data[col].sum(), 2) for col in columnas_series]
        num_series = len(columnas_series)
        
        # Distribuir x_coords equitativamente
        n = len(fechas)
        x_coords = [int(n * (i + 1)/(num_series + 1)) for i in range(num_series)]
        
        # Distribuir y_coords según el área de cada serie
        y_coords = []
        acum = np.zeros_like(valores[0])
        for i, serie in enumerate(valores):
            acum = acum + serie
            y_pos = acum[x_coords[i]] * (0.6 if mostrar_porcentajes else 1)
            y_coords.append(y_pos)
        
        colores_borde = [paleta_colores[i] for i in range(num_series)]
        # Añadir las cápsulas solo dentro de su área correspondiente
        for x, y, total, color_borde in zip(x_coords, y_coords, totales, colores_borde):
            ax.text(
                x, y, f"{total:,}",
                ha='center', va='center',
                fontsize=font_config['capsula_valor']['size'],  # Aplicar configuración de fuente
                fontweight=font_config['capsula_valor']['weight'],
                color=font_config['capsula_valor']['color'],
                bbox=dict(
                    boxstyle="round,pad=0.6,rounding_size=1",
                    facecolor='white',
                    edgecolor=color_borde,
                    linewidth=1.8
                )
            )
    # Crear snapshot lateral si está habilitado
    if mostrar_snapshot and ax_snapshot is not None:
        # Calcular porcentajes totales
        totales_array = np.array([np.sum(v) for v in valores_norm])
        if totales_array.sum() != 0:
            porcentajes = totales_array / totales_array.sum() * 100
        else:
            porcentajes = np.zeros_like(totales_array)
        
        # Redondear y ajustar para que sumen exactamente 100%
        porcentajes = np.round(porcentajes, 1)
        diferencia = 100 - porcentajes.sum()
        if len(porcentajes) > 0:
            porcentajes[-1] += diferencia

        # Crear barra apilada vertical
        bar_width = 0.5
        bottom = 0
        for valor, color in zip(porcentajes, paleta_colores):
            altura = valor / 100
            ax_snapshot.bar(0, altura, width=bar_width, bottom=bottom,
                           color=color, edgecolor='white', linewidth=0.5)
            fontsize_snapshot = kwargs.get('tamano_texto_snapshot', 12)
            ax_snapshot.text(
                0, bottom + altura/2, f"{valor:.1f}%",
                ha='center', va='center',
                color='white',
                fontweight='medium',
                fontsize=fontsize_snapshot,
                family=font_config['family']
            )
            bottom += altura

        # Configurar snapshot axis
        ax_snapshot.set_xlim(-0.5, 0.5)
        ax_snapshot.set_ylim(0, 1)
        ax_snapshot.set_xticks([])
        ax_snapshot.set_yticks([])
        for spine in ax_snapshot.spines.values():
            spine.set_visible(False)
        ax_snapshot.tick_params(bottom=False, labelbottom=False)
        ax_snapshot.patch.set_alpha(0)

    # Configurar leyenda
    if mostrar_leyenda:
        if mostrar_snapshot:
            # Para snapshot, usar leyenda de la figura completa
            fig.legend(
                etiquetas_series,
                loc='upper center',
                bbox_to_anchor=posicion_leyenda,
                ncol=ncol_leyenda,
                frameon=False,
                prop=font_manager.FontProperties(
                    size=font_config['leyenda']['size'], 
                    weight=font_config['leyenda']['weight']
                )
            )
        else:
            # Para areaplot normal, usar leyenda del axis
            ax.legend(
                loc='upper center',
                bbox_to_anchor=posicion_leyenda,
                ncol=ncol_leyenda,
                frameon=False,
                prop=font_manager.FontProperties(
                    size=font_config['leyenda']['size'], 
                    weight=font_config['leyenda']['weight']
                )
            )

    # Ajustar espaciado
    if mostrar_snapshot:
        plt.subplots_adjust(wspace=0.05, hspace=0.05)
    else:
        plt.tight_layout()

    # --- GUARDADO Y VISUALIZACIÓN ---
    os.makedirs("output", exist_ok=True)
    output_path = os.path.join("output", f"{nombre}.svg")
    
    # Guardar la gráfica
    plt.savefig(output_path, format="svg", bbox_inches='tight', dpi=dpi, transparent=True)
    
    # Aplicar el flujo de exportación SVG si está habilitado
    if usar_flujo_svg:
        try:
            archivo_final = exportar_grafica(output_path, nombre, "output")
            if archivo_final and os.path.exists(output_path):
                os.remove(output_path)
        except Exception as e:
            print(f"Error en flujo SVG: {e}")
    
    plt.show()
