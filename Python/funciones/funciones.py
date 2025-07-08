import subprocess
import pandas as pd
import numpy as np
import locale 
import re
from matplotlib.colors import to_rgb, to_hex


def limpiar_svg_con_scour(archivo_entrada, archivo_salida):
    """
    Optimiza un archivo SVG utilizando la herramienta de línea de comandos 'scour'.

    Reduce el tamaño del archivo SVG eliminando datos innecesarios, acortando IDs
    y aplicando otras optimizaciones sin afectar la apariencia visual.

    Args:
        archivo_entrada (str): Ruta al archivo SVG original.
        archivo_salida (str): Ruta donde se guardará el archivo SVG optimizado.
    """
    subprocess.run([
        'scour', '-i', archivo_entrada, '-o', archivo_salida,
        '--enable-viewboxing', '--enable-id-stripping',
        '--shorten-ids', '--remove-descriptive-elements'
    ], check=True)

def formato_fechas(fechas):
    """
    Formatea una lista de fechas a un formato de cadena de texto legible y conciso.

    La función adapta el formato según la variabilidad de las fechas en la lista:
    - Si solo cambia el año, muestra solo el año (ej. "2023").
    - Si cambia el mes o el año, muestra mes y año (ej. "Ene-2023").
    - Si cambia el día, muestra día, mes y año (ej. "01-01-2023").

    Args:
        fechas (list): Una lista de objetos de fecha (ej. pd.Timestamp).

    Returns:
        list: Una lista de cadenas de texto con las fechas formateadas.
    """
    fechas = pd.to_datetime(fechas)
    dias = set(f.day for f in fechas)
    meses = set(f.month for f in fechas)
    anios = set(f.year for f in fechas)
    # Si solo difieren en el año (mismo día y mes)
    if len(dias) == 1 and len(meses) == 1 and len(anios) >1:
        return [str(f.year) for f in fechas]
    elif len(dias) == 1 and (len(meses) > 1 or len(anios) > 1):
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
        return [f.strftime("%b-%Y").capitalize() for f in fechas]
    # Si difieren en día, mes o año
    else:
        return [f.strftime("%d-%m-%Y") for f in fechas]


def get_text_color_for_bg(bg_color):
    """
    Determina si el color del texto debe ser blanco o negro para un contraste adecuado.

    Calcula la luminosidad del color de fondo y devuelve negro ('#000000') para
    fondos claros y blanco ('#ffffff') para fondos oscuros.

    Args:
        bg_color (str): El color de fondo en un formato reconocido por Matplotlib 
                        (ej. '#RRGGBB', 'red', 'yellow').

    Returns:
        str: El código hexadecimal del color de texto ('#000000' o '#ffffff').
    """
    if not bg_color or bg_color.lower() == 'none':
        return '#000000'
    try:
        # Convertir el color de fondo a RGB
        rgb = to_rgb(bg_color)
        # Calcular la luminosidad usando la fórmula estándar (YIQ)
        luminance = (rgb[0] * 299 + rgb[1] * 587 + rgb[2] * 114) / 1000
        # Devolver negro para fondos claros, blanco para fondos oscuros
        return '#000000' if luminance > 0.5 else '#ffffff'
    except ValueError:
        # Si el color no es válido, devolver negro por defecto
        return '#000000'
    
def unir_barras(df, num_barras, lado):
    """
    Une un número específico de barras de un DataFrame en una sola barra sumada.

    Toma las primeras o las últimas 'num_barras' filas del DataFrame, las suma
    para crear una nueva fila consolidada y la reemplaza en el DataFrame original.
    La etiqueta de la nueva fila se genera a partir del rango de las etiquetas originales.

    Args:
        df (pd.DataFrame): El DataFrame de entrada con las barras a procesar.
        num_barras (int): El número de barras a unir desde el borde especificado.
        lado (str): El lado desde el cual unir las barras ('izquierda' o 'derecha').

    Returns:
        tuple: Un tuple conteniendo:
            - pd.DataFrame: El DataFrame modificado con las barras unidas.
            - str or None: La etiqueta de la nueva barra unida, o None si no se unió nada.
    """
    if num_barras <= 1 or len(df) < num_barras:
        return df, None
        
    if lado == 'izquierda':
        seleccion = df.iloc[:num_barras]
        df_resto = df.iloc[num_barras:]
    else: # derecha
        seleccion = df.iloc[-num_barras:]
        df_resto = df.iloc[:-num_barras]

    union = seleccion.sum()
    idxs = seleccion.index
        
    if np.issubdtype(type(idxs[0]), np.datetime64) or isinstance(idxs[0], pd.Timestamp):
        start_date, end_date = idxs[0], idxs[-1]
        
        if start_date == end_date:
            etiqueta_union = formato_fechas([start_date])[0]
        elif start_date.year == end_date.year:
            locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
            # Si los días son diferentes, muestra día y mes
            if start_date.day != end_date.day:
                start_format = start_date.strftime('%d de %b').capitalize()
                end_format = end_date.strftime('%d de %b').capitalize()
            # Si solo los meses son diferentes, muestra solo el mes
            else:
                start_format = start_date.strftime('%b').capitalize()
                end_format = end_date.strftime('%b').capitalize()
            
            etiqueta_union = f"{start_format} a {end_format} de {start_date.year}"
        else:
            # Si los años son diferentes, usa el formato completo
            formatted_dates = formato_fechas(idxs)
            etiqueta_union = f"{formatted_dates[0]}-{formatted_dates[-1]}"
    else:
        if idxs[0] == idxs[-1]:
            etiqueta_union = str(idxs[0])
        else:
            etiqueta_union = f"{idxs[0]}-{idxs[-1]}"
        
    df_union = pd.DataFrame([union], index=[etiqueta_union])

    if lado == 'izquierda':
        return pd.concat([df_union, df_resto]), etiqueta_union
    else:
        return pd.concat([df_resto, df_union]), etiqueta_union