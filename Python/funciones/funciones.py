import subprocess
import pandas as pd
import numpy as np
import locale 

def limpiar_svg_con_scour(archivo_entrada, archivo_salida):
    subprocess.run([
        'scour', '-i', archivo_entrada, '-o', archivo_salida,
        '--enable-viewboxing', '--enable-id-stripping',
        '--shorten-ids', '--remove-descriptive-elements'
    ], check=True)

def formato_fechas(fechas):
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

def get_text_color_for_bg(bg_color_hex):
    """Determina si el texto debe ser negro o blanco según el color de fondo hexadecimal."""
    try:
        hex_color = bg_color_hex.lstrip('#')
        if len(hex_color) != 6:
            return '#ffffff'
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        return '#000000' if luminance > 0.6 else '#ffffff'
    except (ValueError, TypeError):
        return '#ffffff'
    
def unir_barras(df, num_barras, lado):
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