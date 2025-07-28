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

def generar_linea(df, **kwargs):
    """
    Genera una gráfica de línea usando matplotlib que produce PNG y SVG
    
    Args:
        df: DataFrame con los datos
        **kwargs: Parámetros de configuración que pueden incluir:
            - columna_fecha: Nombre de la columna con fechas
            - columna_grafica: Nombre de la columna con valores principales
            - columna_linea: Nombre de la columna con la línea punteada
            - nombre_archivo: Nombre del archivo de salida
            - config: Configuración adicional
    """
    try:
        # Extraer parámetros con valores por defecto
        columna_fecha = kwargs.get('columna_fecha', 'fecha')
        columna_grafica = kwargs.get('columna_grafica', 'valores')
        columna_linea = kwargs.get('columna_linea', 'referencia')
        nombre_archivo = kwargs.get('nombre_archivo', kwargs.get('nombre', 'linea'))
        config = kwargs.get('config', {})
        
        # Verificar que las columnas especificadas existan en el DataFrame
        if columna_fecha not in df.columns:
            raise ValueError(f"La columna '{columna_fecha}' no existe en el DataFrame.")
        if columna_grafica not in df.columns:
            raise ValueError(f"La columna '{columna_grafica}' no existe en el DataFrame.")
        if columna_linea not in df.columns:
            raise ValueError(f"La columna '{columna_linea}' no existe en el DataFrame.")
        
        # Convertir la columna de fecha a datetime si no lo es
        if df[columna_fecha].dtype == 'object':
            df[columna_fecha] = pd.to_datetime(df[columna_fecha])
        
        font_config = {
            'family': 'Montserrat',  
            'variable_x': {'size': 24, 'weight': 'semibold', 'color': '#767676'},
            'variable_y': {'size': 24, 'weight': 'medium', 'color': '#767676'},
            'capsula': {'size': 18, 'weight': 'medium', 'color': 'white'},
        }

        plt.rcParams['svg.fonttype'] = 'none'
        font_dirs = [Path("../0_fonts")]
        font_files = font_manager.findSystemFonts(fontpaths=font_dirs)
        for font_file in font_files:
            font_manager.fontManager.addfont(font_file)

        nombre_df = nombre_archivo or "linea"
        
        # Configurar el tamaño de la figura en píxeles
        ancho_px = 1480
        alto_px = 520
        dpi = 100  # Resolución en píxeles por pulgada
        ancho_in = ancho_px / dpi
        alto_in = alto_px / dpi
        
        # Crear la figura con el tamaño especificado
        fig, ax = plt.subplots(figsize=(ancho_in, alto_in), dpi=dpi)
        
        # Seleccionar colores específicos
        color_area = '#d4dce9'  # Primer color de la lista
        color_linea = '#2f5597'  # Segundo color de la lista
        color_linea_punteada = '#c00000'  # Color para la línea punteada
        
        # Graficar el área
        ax.fill_between(
            df[columna_fecha],
            df[columna_grafica],
            color=color_area,  # Color del área
            alpha=1.,
        )
        
        # Graficar la línea sobre el área
        ax.plot(
            df[columna_fecha],
            df[columna_grafica],
            color=color_linea,  # Color de la línea
            linewidth=2
        )
        
        # Graficar la línea punteada
        ax.plot(
            df[columna_fecha],
            df[columna_linea],
            color=color_linea_punteada,  # Color de la línea punteada
            linestyle='--',  # Estilo de línea punteada
            linewidth=2
        )

        # Configurar las etiquetas del eje X
        ax.tick_params(axis='x', labelsize=font_config['variable_x']['size'], labelcolor=font_config['variable_x']['color'])
        ax.tick_params(axis='y', labelsize=font_config['variable_y']['size'], labelcolor=font_config['variable_y']['color'])

        # Posicionar el eje X en y=0
        ax.spines['bottom'].set_position(('data', 0))

        # Rotar las etiquetas del eje X
        plt.xticks(rotation=90, fontname=font_config['family'], fontsize=font_config['variable_x']['size'], color=font_config['variable_x']['color'], weight=font_config['variable_x']['weight'])
        plt.yticks(fontname=font_config['family'], fontsize=font_config['variable_y']['size'], color=font_config['variable_y']['color'], weight=font_config['variable_y']['weight'])
        
        # Desactivar o activar bordes
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(True)
        
        # Asignar grosor a los ejes visibles
        ax.spines['bottom'].set_linewidth(2)  # Grosor del eje inferior
        
        # Mantener las líneas del grid
        ax.grid(axis='y', linestyle='-', color='#000000', alpha=0.2, linewidth=0.75)
        ax.grid(axis='x', linestyle='-', color='#000000', alpha=0.2, linewidth=0.75)
        
        # Convertir la fecha 2024 a un índice o posición en el eje X
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

        # Calcular los factores proporcionales
        x_min, x_max = ax.get_xlim()  # Obtener los límites del eje X
        y_min, y_max = ax.get_ylim()  # Obtener los límites del eje Y

        factor_ancho = 0.04 * (x_max - x_min)  # Proporcional al rango del eje X
        factor_alto = 0.05 * (y_max - y_min)   # Proporcional al rango del eje Y

        # Añadir el símbolo de la llave
        curly_at_fechas(x_pos, y_pos_min+0.2*factor_alto, width=factor_ancho, height=altura+factor_alto, ax=ax, color="#af0b19")
        
        # Calcular la diferencia entre y_pos_gra y y_pos_lin
        diferencia = round(y_pos_gra - y_pos_lin)

        # Añadir una cápsula con la diferencia en la parte derecha de la gráfica
        color_capsula = "#af0b19"  # Color de la cápsula
        bbox_props = dict(boxstyle="round,pad=0.25,rounding_size=0.99", fc=color_capsula, ec="none", alpha=1.0)

        x_pos_numeric = date2num(x_pos)  # Convertir la fecha a un número

        # Posicionar la cápsula en la parte derecha de la gráfica
        ax.text(
            x_pos_numeric + 1.8 * factor_ancho,  # Usar el valor numérico de x_pos
            y_pos_min + altura / 2.5,  # Centrar verticalmente entre y_pos_gra y y_pos_lin
            diferencia,  # Texto de la cápsula
            color=font_config['capsula']['color'],
            fontsize=font_config['capsula']['size'],
            fontweight=font_config['capsula']['weight'],
            fontname=font_config['family'],
            bbox=bbox_props,
            ha="center",
            va="center"
        )

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
        print(f"Gráfica guardada como: {ruta_temporal}")
        return ruta_temporal
    except Exception as e:
        print(f"Error al generar gráfica de línea: {e}")
        return None
