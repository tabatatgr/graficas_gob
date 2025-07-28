import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from pathlib import Path
from matplotlib import font_manager
import subprocess
import os

def generar_lineas_tendencia(df, **kwargs):
    """
    Genera una gráfica de líneas de tendencia usando matplotlib que produce PNG y SVG
    
    Args:
        df: DataFrame con los datos
        **kwargs: Parámetros de configuración que pueden incluir:
            - columna_entidad: Nombre de la columna con entidades (default: 'entity_name')
            - columna_fecha: Nombre de la columna con fechas/años (default: 'data_year')
            - columna_valor: Nombre de la columna con valores (default: 'data_value')
            - nombre_archivo: Nombre del archivo de salida (default: 'lineas_tendencia')
            - entidad_destacada: Nombre de la entidad a destacar (default: 'México')
            - color_destacado: Color para la entidad destacada (default: '#8B0000')
            - color_otras: Color para otras entidades (default: '#10302C')
            - alpha_otras: Transparencia para otras entidades (default: 0.3)
            - config: Configuración adicional
    """
    try:
        # Extraer parámetros con valores por defecto
        columna_entidad = kwargs.get('columna_entidad', 'entity_name')
        columna_fecha = kwargs.get('columna_fecha', 'data_year')
        columna_valor = kwargs.get('columna_valor', 'data_value')
        nombre_archivo = kwargs.get('nombre_archivo', kwargs.get('nombre', 'lineas_tendencia'))
        entidad_destacada = kwargs.get('entidad_destacada', 'México')
        color_destacado = kwargs.get('color_destacado', '#8B0000')
        color_otras = kwargs.get('color_otras', '#10302C')
        alpha_otras = kwargs.get('alpha_otras', 0.3)
        config = kwargs.get('config', {})
        
        # Verificar que las columnas especificadas existan en el DataFrame
        if columna_entidad not in df.columns:
            raise ValueError(f"La columna '{columna_entidad}' no existe en el DataFrame.")
        if columna_fecha not in df.columns:
            raise ValueError(f"La columna '{columna_fecha}' no existe en el DataFrame.")
        if columna_valor not in df.columns:
            raise ValueError(f"La columna '{columna_valor}' no existe en el DataFrame.")
        
        # Configurar matplotlib
        plt.rcParams['svg.fonttype'] = 'none'
        font_dirs = [Path("../0_fonts")]
        font_files = font_manager.findSystemFonts(fontpaths=font_dirs)
        for font_file in font_files:
            font_manager.fontManager.addfont(font_file)

        nombre_df = nombre_archivo or "lineas_tendencia"
        
        # Crear la figura
        fig, ax = plt.subplots(figsize=(12, 4))

        # Dibujar líneas para cada entidad
        for name, group in df.groupby(columna_entidad):
            alpha = 1 if name == entidad_destacada else alpha_otras
            color = color_destacado if name == entidad_destacada else color_otras
            ax.plot(group[columna_fecha], group[columna_valor], 
                   label=name if name == entidad_destacada else "",
                   alpha=alpha, color=color, linewidth=1.5)

        # Configurar ejes
        years = sorted(df[columna_fecha].unique())
        ax.set_xticks(years)
        ax.set_xticklabels(years, rotation=0, ha='right', fontweight='bold')
        
        # Formatear eje Y con formato de dinero
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
        
        # Configurar ticks automáticamente basado en los datos
        y_min, y_max = df[columna_valor].min(), df[columna_valor].max()
        ax.set_yticks(np.linspace(y_min, y_max, num=5))
        
        # Configurar estilo de ejes
        ax.tick_params(axis='x', which='both', bottom=False, top=False)
        ax.tick_params(axis='y', which='both', left=False, right=False)
        ax.set_xlabel('')
        ax.set_ylabel('')
        
        # Configurar bordes
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(True)

        # Ajustar layout
        plt.tight_layout()
        
        # Guardar archivos
        # --- 9. GUARDADO Y VISUALIZACIÓN ---
        output_dir = kwargs.get('output_dir', 'output')
        os.makedirs(output_dir, exist_ok=True)

        # Ajustar márgenes (idéntico a barras)
        left_margin = 0.15
        right_margin = 0.95
        bottom_margin = 0.2
        top_margin = 0.95
        plt.subplots_adjust(left=left_margin, right=right_margin, top=top_margin, bottom=bottom_margin)

        nombre_archivo = f"{nombre_df}.svg"
        ruta_temporal = os.path.join(output_dir, nombre_archivo)
        plt.savefig(ruta_temporal, format='svg', dpi=300, transparent=True)

        # Aplicar el flujo de exportación
        try:
            from svg_cleanup.flujo_exportacion import exportar_grafica
            archivo_final = exportar_grafica(ruta_temporal, nombre_df, output_dir)
            # Limpiar archivo temporal
            if archivo_final and os.path.exists(ruta_temporal):
                os.remove(ruta_temporal)
        except ImportError:
            print("Nota: Módulo de exportación no disponible. Se guardará el SVG sin optimizar.")
        except Exception as e:
            print(f"Advertencia: Error en el flujo de exportación: {e}")

        plt.close(fig)  # Cerrar la figura para liberar memoria
        print(f"Gráfica de líneas de tendencia guardada como: {ruta_temporal}")
        return ruta_temporal
        
    except Exception as e:
        print(f"Error al generar gráfica de líneas de tendencia: {e}")
        return None
