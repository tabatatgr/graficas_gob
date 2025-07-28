# barras_apiladas
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager
from pathlib import Path
import matplotlib.ticker as mticker
from matplotlib.ticker import FuncFormatter
from statistics import mode
import subprocess
from matplotlib.patches import Patch
import os

def formato_fechas(fechas):
    fechas = pd.to_datetime(fechas)
    if len(set(f.year for f in fechas)) == len(fechas):
        return [str(f.year) for f in fechas]
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

ESPACIADO_CONFIGS = {
    "compacto": {
        "bar_height": 0.9,
        "aumenta_alto_fig": -5,
        "aumenta_ancho_fig": -2,
        "aumenta_sep_leyenda": 0.08
    },
    "normal": {
        "bar_height": 0.7,
        "aumenta_alto_fig": 0,
        "aumenta_ancho_fig": 0,
        "aumenta_sep_leyenda": 0.0
    },
    "amplio": {
        "bar_height": 0.5,
        "aumenta_alto_fig": 3,
        "aumenta_ancho_fig": 1,
        "aumenta_sep_leyenda": 0.0
    },
    "muy_compacto": {
        "bar_height": 0.95,
        "aumenta_alto_fig": -8,
        "aumenta_ancho_fig": -3,
        "aumenta_sep_leyenda": 0.12
    }
}

def barras(
    df_wide,
    nombre=None,
    font='Montserrat',
    fontsize_barra=15,
    fontsize_valor_total=20,
    bar_height=0.95,
    bar_height_override=False,
    aumenta_ancho_fig=0,
    aumenta_alto_fig=0,
    orientacion='vertical',  # 'vertical' o 'horizontal'
    aumenta_sep_leyenda=0.0,
    valor_barra=False,
    valor_total=True,
    porcentaje_barra=False,
    porcentaje_divergente=False,
    porcentaje_total=False,
    porcentaje_total_inicio=False,
    ordenar_por='valor',
    orden='descendente',
    quitar_capsula=False,
    area_min=0,
    espacio_inicio=0,
    paleta_colores=None,
    color_valor_barra=None,
    agregar_datos=None,
    asignar_etiquetas=None,
    grillas=True,
    leyenda=None,
    posicion_leyenda='arriba',
    union_izquierda=0,
    union_derecha=0,
    separar_por_total=0.0,
    y_limits=None,
    nombre_eje_x=None,
    nombre_eje_y=None,
    resaltar_etiquetas=None,
    sustituir_etiquetas=None,
    porcentaje_abajo=True,
    orientacion_etiqueta_x=None,
    altura_min=0,
    ejeY_negativo_a_positivo=False,
    capsulas_cero=True,
    ncol_leyenda=None,
    usar_flujo_svg=False,
    output_dir="output",
    desplazamiento_capsula=0.03,
    **kwargs
):
    """
    Gráfica de barras flexible (vertical u horizontal) con resaltado y sustitución de etiquetas robustos.
    orientacion: 'vertical' o 'horizontal'.
    resaltar_etiquetas: lista de etiquetas a resaltar (insensible a tildes, mayúsculas, espacios).
    sustituir_etiquetas: dict o lista para sustituir etiquetas del eje.
    """
    """
    Genera un gráfico de barras verticales apiladas a partir de un DataFrame de pandas.
    
    Nuevos kwargs para espaciado:
    - espaciado: str. Presets: "compacto", "normal", "amplio", "muy_compacto"
    - sustituir_etiquetas: dict o list. Sustituye etiquetas específicas
    """
    # --- Parámetros de separación para porcentaje al inicio ---
    DX_PCT_PTS = 14 # desplazamiento entre % y barra (puntos)
    GAP_LAB_PCT = 6 # espacio entre etiqueta‑Y y % (puntos)
    
    # ** PROCESAMIENTO DE KWARGS DE ESPACIADO **
    espaciado = kwargs.get('espaciado', None)
    
    if espaciado and espaciado in ESPACIADO_CONFIGS:
        config = ESPACIADO_CONFIGS[espaciado]
        
        if bar_height == 0.5:  # Valor por defecto
            bar_height = config['bar_height']
        if aumenta_alto_fig == 0:  # Valor por defecto
            aumenta_alto_fig = config['aumenta_alto_fig']
        if aumenta_ancho_fig == 0:  # Valor por defecto
            aumenta_ancho_fig = config['aumenta_ancho_fig']
        if aumenta_sep_leyenda == 0.0:  # Valor por defecto
            aumenta_sep_leyenda = config['aumenta_sep_leyenda']
    
    elif espaciado and espaciado not in ESPACIADO_CONFIGS:
        print(f"Advertencia: espaciado='{espaciado}' no reconocido. Opciones disponibles: {list(ESPACIADO_CONFIGS.keys())}")
    
    # ** VALIDACIONES DE ESPACIADO **
    if bar_height < 0.1 or bar_height > 1.0:
        print(f"Advertencia: bar_height={bar_height} está fuera del rango recomendado (0.1-1.0)")
    
    hay_annotations_externas = False
    espacio = "\u00A0"

    font_config = {
        'family': font,
        'variable_x': {'size': 25, 'weight': 'medium', 'color': '#000000'},
        'variable_y': {'size': 22, 'weight': 'medium', 'color': '#000000'},
        'nombre_eje_x': {'size': 25, 'weight': 'medium', 'color': '#000000'},
        'nombre_eje_y': {'size': 22, 'weight': 'medium', 'color': '#000000'},
        'valor_capsula': {'size': fontsize_valor_total, 'weight': 'bold', 'color': '#000000'},
        'valor_porcentaje_barra': {'size': fontsize_barra, 'weight': 'bold', 'color': '#584290'},
        'porcentaje_total': {'size': 22, 'weight': 'semibold', 'color': '#4C6A67'},
        'leyenda': {'size': 24, 'weight': 'medium', 'color': '#767676'}
    }

    plt.rcParams['svg.fonttype'] = 'none'
    font_dirs = [Path("../0_fonts")]
    font_files = font_manager.findSystemFonts(fontpaths=font_dirs)
    for font_file in font_files:
        font_manager.fontManager.addfont(font_file)

    # Si el nombre es None o vacío, intentar obtenerlo de kwargs (por si viene como 'grafico' o 'parametros')
    if not nombre:
        nombre = kwargs.get('nombre') or kwargs.get('grafico', {}).get('nombre') or kwargs.get('parametros', {}).get('nombre')
    nombre_df = nombre or "barras_verticales"
    colores_asignados = paleta_colores or ["#10302C", "#4C6A67", "#8FA8A6", "#A3C9A8"]

    if not isinstance(df_wide, pd.DataFrame):
        raise ValueError("El argumento df_wide debe ser un DataFrame de pandas.")
    
    df_wide = df_wide.copy()
    categorias_x = df_wide.columns[0]
    if pd.api.types.is_integer_dtype(df_wide[categorias_x]) and df_wide[categorias_x].between(1900, 2100).all():
        df_wide[categorias_x] = pd.to_datetime(df_wide[categorias_x], format='%Y')
    df_wide = df_wide.set_index(categorias_x)

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
            etiqueta_union = f"{idxs[0].year}-{idxs[-1].year}"
        else:
            etiqueta_union = f"{idxs[0]}-{idxs[-1]}"
        
        df_union = pd.DataFrame([union], index=[etiqueta_union])

        if lado == 'izquierda':
            return pd.concat([df_union, df_resto]), etiqueta_union
        else:
            return pd.concat([df_resto, df_union]), etiqueta_union

    df_wide, etiqueta_union_izq = unir_barras(df_wide, union_izquierda, 'izquierda')
    df_wide, etiqueta_union_der = unir_barras(df_wide, union_derecha, 'derecha')

    etiquetas_personalizadas = {}
    textos_barra_personalizados = {}
    colores_fondo_personalizados = {}
    colores_borde_personalizados = {}
    estilos_borde_personalizados = {}
    grosores_borde_personalizados = {}
    colores_texto_personalizados = {}
    if agregar_datos:

        df_dates = [idx for idx in df_wide.index if isinstance(idx, (pd.Timestamp, np.datetime64))]
        min_date_df = min(df_dates) if df_dates else None
        max_date_df = max(df_dates) if df_dates else None

        filas_previas = []
        filas_posteriores = []

        num_cols = len(df_wide.columns)

        for item in agregar_datos:
            etiqueta, texto_barra, opciones_extra = None, None, {}

            if len(item) == 2:
                categoria, valor = item
            elif len(item) == 3:
                categoria, etiqueta, valor = item
            elif len(item) == 4:
                categoria, etiqueta, valor, texto_barra = item
            elif len(item) == 5:
                categoria, etiqueta, valor, texto_barra, opciones_extra = item

            # --- AJUSTE DINÁMICO DE LONGITUD ---
            # Ajustar el vector de valores
            if isinstance(valor, (list, tuple, np.ndarray)):
                if len(valor) < num_cols:
                    valor = list(valor) + [0] * (num_cols - len(valor))
                elif len(valor) > num_cols:
                    valor = list(valor)[:num_cols]

            # Ajustar listas de personalización
            def ajustar_lista_personalizacion(lst):
                if not isinstance(lst, (list, tuple, np.ndarray)):
                    return [lst] * num_cols
                if len(lst) < num_cols:
                    return list(lst) + [None] * (num_cols - len(lst))
                elif len(lst) > num_cols:
                    return list(lst)[:num_cols]
                return list(lst)

            if etiqueta:
                etiquetas_personalizadas[categoria] = etiqueta
            if texto_barra:
                textos_barra_personalizados[categoria] = texto_barra
            if isinstance(opciones_extra, dict):
                if 'colores_fondo' in opciones_extra:
                    colores_fondo_personalizados[categoria] = ajustar_lista_personalizacion(opciones_extra['colores_fondo'])
                if 'colores_borde' in opciones_extra:
                    colores_borde_personalizados[categoria] = ajustar_lista_personalizacion(opciones_extra['colores_borde'])
                if 'estilos_borde' in opciones_extra:
                    estilos_borde_personalizados[categoria] = ajustar_lista_personalizacion(opciones_extra['estilos_borde'])
                if 'grosores_borde' in opciones_extra:
                    grosores_borde_personalizados[categoria] = ajustar_lista_personalizacion(opciones_extra['grosores_borde'])
                if 'colores_texto' in opciones_extra:
                    colores_texto_personalizados[categoria] = ajustar_lista_personalizacion(opciones_extra['colores_texto'])

            fila = pd.Series(dict(zip(df_wide.columns, valor)) if isinstance(valor, (list, tuple, np.ndarray)) else {col: valor if i == 0 else 0 for i, col in enumerate(df_wide.columns)}, name=categoria)

            if min_date_df and isinstance(categoria, (pd.Timestamp, np.datetime64)) and categoria < min_date_df:
                filas_previas.append(fila)
            elif max_date_df and isinstance(categoria, (pd.Timestamp, np.datetime64)) and categoria > max_date_df:
                filas_posteriores.append(fila)
            elif not min_date_df and not max_date_df: # Non-date index
                filas_previas.append(fila) # Default to prepending for non-date indexes

        if filas_previas:
            df_previo = pd.DataFrame(filas_previas)
            df_wide = pd.concat([df_previo, df_wide])
            if isinstance(df_wide.index[0], (pd.Timestamp, np.datetime64)):
                fechas_agregar = df_previo.index
                fecha_max_agregar = max(fechas_agregar)
                fechas_resto = [idx for idx in df_wide.index[len(fechas_agregar):] if isinstance(idx, pd.Timestamp)]
                if fechas_resto:
                    fecha_min_resto = min(fechas_resto)
                    categoria_espaciadora = fecha_max_agregar + (fecha_min_resto - fecha_max_agregar) / 2
                    fila_espaciadora = pd.Series({col: 0 for col in df_wide.columns}, name=categoria_espaciadora)
                    df_wide = pd.concat([df_wide.iloc[:len(fechas_agregar)], pd.DataFrame([fila_espaciadora]), df_wide.iloc[len(fechas_agregar):]])

        if filas_posteriores:
            df_posterior = pd.DataFrame(filas_posteriores)
            df_wide = pd.concat([df_wide, df_posterior])
            if isinstance(df_wide.index[-1], (pd.Timestamp, np.datetime64)):
                fechas_agregar = df_posterior.index
                fecha_min_agregar = min(fechas_agregar)
                fechas_resto = [idx for idx in df_wide.index[:-len(fechas_agregar)] if isinstance(idx, pd.Timestamp)]
                if fechas_resto:
                    fecha_max_resto = max(fechas_resto)
                    categoria_espaciadora = fecha_max_resto + (fecha_min_agregar - fecha_max_resto) / 2
                    fila_espaciadora = pd.Series({col: 0 for col in df_wide.columns}, name=categoria_espaciadora)
                    df_wide = pd.concat([df_wide.iloc[:-len(fechas_agregar)], pd.DataFrame([fila_espaciadora]), df_wide.iloc[-len(fechas_agregar):]])

    etiquetas_finales = None
    if asignar_etiquetas and asignar_etiquetas in df_wide.columns:
        etiquetas_finales = df_wide[asignar_etiquetas].copy()
        df_wide = df_wide.drop(columns=[asignar_etiquetas])

    suma_total = df_wide.sum(axis=1)
    total_general = suma_total.sum()
    
    es_divergente = any(df_wide.min() < 0)
    suma_positivos_por_barra = None
    suma_negativos_por_barra = None
    suma_absoluta_por_barra = None
    total_general_absoluto = None
    total_general_positivos = None
    if es_divergente:
        suma_negativos_por_barra = df_wide[df_wide < 0].sum(axis=1)
        if porcentaje_divergente:
            suma_positivos_por_barra = df_wide[df_wide > 0].sum(axis=1)
            if hasattr(suma_positivos_por_barra, 'sum'):
                total_general_positivos = suma_positivos_por_barra.sum()
            else:
                total_general_positivos = float(suma_positivos_por_barra)
        else:
            suma_absoluta_por_barra = df_wide.abs().sum(axis=1)
            if hasattr(suma_absoluta_por_barra, 'sum'):
                total_general_absoluto = suma_absoluta_por_barra.sum()
            else:
                total_general_absoluto = float(suma_absoluta_por_barra)

    # Inicializar los límites
    x_max_pos = df_wide[df_wide > 0].sum(axis=1).max()
    x_max_neg = df_wide[df_wide < 0].sum(axis=1).min()
    x_max = max(x_max_pos, abs(x_max_neg)) * 1.15 if not pd.isna(x_max_pos) else suma_total.max() * 1.15
    x_min = min(x_max_neg, 0) * 1.15 if not pd.isna(x_max_neg) else suma_total.min() * 1.15
    
    # Asegurar que x_min y x_max son números válidos
    if pd.isna(x_max): x_max = 1
    if pd.isna(x_min): x_min = -1

    if ordenar_por == 'valor':
        sort_index = suma_total.sort_values(ascending=(orden == 'ascendente')).index
    elif ordenar_por == 'etiqueta':
        indices = list(df_wide.index)
        izq = [etiqueta_union_izq] if etiqueta_union_izq else []
        der = [etiqueta_union_der] if etiqueta_union_der else []
        centro = [i for i in indices if i not in izq + der]
        
        tipos = set(type(idx) for idx in centro)
        reverse_sort = (orden == 'descendente')
        centro_ordenado = sorted(centro, key=lambda x: str(x), reverse=reverse_sort) if len(tipos) > 1 else sorted(centro, reverse=reverse_sort)
        
        sort_index = izq + centro_ordenado + der
    else:
        sort_index = df_wide.index

    df_wide = df_wide.loc[sort_index]
    suma_total = suma_total.loc[sort_index]
    entidades = df_wide.index.values

    es_fecha = any(isinstance(idx, (pd.Timestamp, np.datetime64)) for idx in df_wide.index if idx not in [etiqueta_union_izq, etiqueta_union_der])
    
    if es_fecha:
        fechas_a_formatear = [idx for idx in df_wide.index if isinstance(idx, (pd.Timestamp, np.datetime64))]
        mapa_fechas = dict(zip(fechas_a_formatear, formato_fechas(fechas_a_formatear)))
        entidades_formateadas = [mapa_fechas.get(idx, str(idx)) for idx in df_wide.index]
    else:
        entidades_formateadas = [str(idx) for idx in df_wide.index]

    # Manejo de sustituir_etiquetas como kwarg
    sustituir_etiquetas = kwargs.get('sustituir_etiquetas', None)
    
    if sustituir_etiquetas:
        if isinstance(sustituir_etiquetas, dict):
            # Sustituir solo las etiquetas especificadas en el diccionario
            for i, etiqueta in enumerate(entidades_formateadas):
                if etiqueta in sustituir_etiquetas:
                    entidades_formateadas[i] = str(sustituir_etiquetas[etiqueta])
        elif isinstance(sustituir_etiquetas, list):
            # Mantener la funcionalidad original para retrocompatibilidad
            if len(sustituir_etiquetas) != len(entidades_formateadas):
                raise ValueError("La longitud de 'sustituir_etiquetas' debe coincidir con el número de barras.")
            entidades_formateadas = list(sustituir_etiquetas)
        else:
            raise ValueError("sustituir_etiquetas debe ser un diccionario o una lista.")

    for i, entidad in enumerate(df_wide.index):
        if entidad in etiquetas_personalizadas and etiquetas_personalizadas[entidad]:
            entidades_formateadas[i] = str(etiquetas_personalizadas[entidad])

    for i, entidad in enumerate(entidades_formateadas):
        if "__espaciador__" in str(entidad) or (es_fecha and (df_wide.iloc[i] == 0).all()):
            entidades_formateadas[i] = "..."

    # Asegurar que valores y suma_total sean iterables
    if hasattr(df_wide, 'columns') and hasattr(df_wide, 'index'):
        valores = [df_wide[col].values for col in df_wide.columns]
        categorias = df_wide.columns
        posiciones = np.arange(len(entidades))
    else:
        # Si por algún motivo df_wide no es un DataFrame, forzar a listas
        valores = [np.array([df_wide])] if not isinstance(df_wide, (list, np.ndarray)) else [np.array(df_wide)]
        categorias = [0]
        posiciones = np.arange(1)

    # Asegurar que suma_total sea iterable
    if not hasattr(suma_total, '__iter__') or isinstance(suma_total, (str, bytes)):
        suma_total = [suma_total]

    # Calcular dimensiones basadas en el contenido
    # Para etiquetas de las categorías
    longitudes_etiquetas = [len(str(etiqueta)) for etiqueta in entidades_formateadas]
    max_etiqueta_len = max(longitudes_etiquetas) if longitudes_etiquetas else 10
    
    # Para valores en las barras
    longitudes_capsula = [len(f"{int(total_valor):,}") for total_valor in suma_total]
    max_capsula_len = max(longitudes_capsula) if longitudes_capsula else 10
    
    # Para porcentajes
    if porcentaje_barra:
        porcentajes = [(valor/suma * 100 if suma != 0 else 0) for valor, suma in zip(df_wide.sum(axis=1), suma_total)]
        longitudes_porcentaje = [len(f"{int(p):,}%") for p in porcentajes]
        max_porcentaje_len = max(longitudes_porcentaje) if longitudes_porcentaje else 0
    else:
        max_porcentaje_len = 0
    
    # Calcular dimensiones de la figura según la orientación
    if orientacion == 'horizontal':
        # Para barras horizontales
        max_texto_len = max_etiqueta_len  # Las etiquetas determinan el espacio necesario a la izquierda
        base_height = max(8, len(entidades) * 0.8)  # Altura base según número de categorías
        base_width = 12  # Ancho base fijo
        # Siempre dejar un pequeño espacio entre barras
        espacio_minimo = 0.05  # 5% de espacio entre barras
        bar_height_max = 1.0 - espacio_minimo
        # Ajustar el grosor de barra para que sea proporcional al texto/cápsula
        bar_height = min(0.95, bar_height_max, max(0.7, max_capsula_len * 0.09))
    else:
        # Para barras verticales
        max_texto_len = max(max_capsula_len, max_porcentaje_len)
        base_width = max(12, len(entidades) * 0.05)  # Espacio entre barras más generoso
        base_height = 8  # Altura base fija
        if not bar_height_override:
            bar_height = min(0.95, max(0.7, max_texto_len * 0.09))
    
    # Ajustes de espaciado según orientación y configuración
    if orientacion == 'horizontal':
        # Ajustes para barras horizontales
        margen_izquierdo = max(2, max_texto_len * 0.12)  # Mucho menos espacio para etiquetas
        if espaciado == "compacto":
            base_height *= 0.85
        elif espaciado == "muy_compacto":
            base_height *= 0.75
        elif espaciado == "amplio":
            base_height *= 1.2
        # Hacer la figura más ancha para evitar encimamiento
        fig_width = max(22, base_width + aumenta_ancho_fig + margen_izquierdo)
        fig_height = max(len(entidades) * 0.6, base_height + aumenta_alto_fig)
        if fig_height < 8:
            fig_height = 8
    else:
        # Ajustes para barras verticales 
        if espaciado == "compacto":
            base_width = max(10, base_width * 0.95)
        elif espaciado == "muy_compacto":
            base_width = max(8, base_width * 0.85)
        elif espaciado == "amplio":
            base_width = base_width * 1.2
        
        fig_width = base_width + aumenta_ancho_fig
        fig_height = base_height + aumenta_alto_fig
    
    # Validar dimensiones mínimas
    fig_width = max(6, fig_width)
    fig_height = max(4, fig_height)
    
    fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=300)

    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)

    # --- FORZAR VISIBILIDAD DE BARRA ESPECIAL EN EL EJE ---
    min_valor_especial = None
    max_valor_especial = None
    # Buscar el valor mínimo y máximo de las barras especiales (con borde punteado)
    for entidad in df_wide.index:
        estilos_borde = estilos_borde_personalizados.get(entidad)
        if estilos_borde:
            for i, estilo in enumerate(estilos_borde):
                if estilo in ['dotted', 'punteado']:
                    val = df_wide.loc[entidad].values[i]
                    if min_valor_especial is None or val < min_valor_especial:
                        min_valor_especial = val
                    if max_valor_especial is None or val > max_valor_especial:
                        max_valor_especial = val

    # Ajustar los límites del eje para incluir la barra especial si es necesario
    if orientacion == 'horizontal':
        x_min_final = min(x_min, min_valor_especial) if min_valor_especial is not None else x_min
        x_max_final = max(x_max, max_valor_especial) if max_valor_especial is not None else x_max
        ax.set_xlim(x_min_final, x_max_final)
        ax.set_ylim(-0.5, len(entidades) - 0.5)
        ax.invert_yaxis()
    else:
        y_min_final = min(x_min, min_valor_especial) if min_valor_especial is not None else x_min
        y_max_final = max(x_max, max_valor_especial) if max_valor_especial is not None else x_max
        ax.set_xlim(-0.5, len(entidades) - 0.5)
        ax.set_ylim(y_min_final, y_max_final)

    # --- Lógica para destacar el valor máximo ---
    destacar_maximo = kwargs.get('destacar_maximo', False)
    color_maximo = kwargs.get('color_maximo', '#8B0000')
    color_texto_maximo = kwargs.get('color_texto_maximo', '#FFFFFF')
    color_capsula_maximo = kwargs.get('color_capsula_maximo', '#8B0000')

    # Identificar la(s) barra(s) de valor máximo
    idx_max = None
    if destacar_maximo:
        max_valor = max(suma_total)
        idx_max = [i for i, v in enumerate(suma_total) if v == max_valor]

    # --- Obtener lista de etiquetas a resaltar (por nombre, no por número) ---
    import ast, unicodedata
    def normaliza(s):
        if not isinstance(s, str):
            s = str(s)
        s = s.strip().lower()
        s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('ascii')
        return s

    # --- Sustitución de etiquetas robusta ---
    etiquetas_eje = list(df_wide.index if orientacion == 'horizontal' else df_wide.columns)
    etiquetas_originales = etiquetas_eje.copy()
    if sustituir_etiquetas:
        if isinstance(sustituir_etiquetas, dict):
            etiquetas_eje = [sustituir_etiquetas.get(e, e) for e in etiquetas_eje]
        elif isinstance(sustituir_etiquetas, list):
            if len(sustituir_etiquetas) == len(etiquetas_eje):
                etiquetas_eje = sustituir_etiquetas
    # --- Resaltado de etiquetas robusto ---
    etiquetas_resaltadas = resaltar_etiquetas or kwargs.get('resaltar_etiquetas', [])
    if isinstance(etiquetas_resaltadas, dict):
        etiquetas_resaltadas = list(etiquetas_resaltadas.values())
    if isinstance(etiquetas_resaltadas, str):
        try:
            etiquetas_resaltadas = ast.literal_eval(etiquetas_resaltadas)
        except Exception:
            etiquetas_resaltadas = [etiquetas_resaltadas]
    if etiquetas_resaltadas is None:
        etiquetas_resaltadas = []
    etiquetas_resaltadas_norm = set(normaliza(e) for e in etiquetas_resaltadas if e)
    color_resaltado = kwargs.get('color_resalt_etique', '#900c3f')
    borde_resaltado = kwargs.get('color_borde_resalt', 'black')
    # --- Debug de etiquetas ---
    try:
        with open(os.path.join(output_dir, 'debug_labels.txt'), 'a', encoding='utf-8') as f:
            f.write('--- ETIQUETAS EJE ---\n')
            for e in etiquetas_eje:
                f.write(f'{e}\n')
            f.write('--- ETIQUETAS A RESALTAR ---\n')
            for e in etiquetas_resaltadas:
                f.write(f'{e}\n')
            f.write('\n')
    except Exception as e:
        print(f"[DEBUG] No se pudo escribir debug_labels.txt: {e}")

    for pos, entidad, total_valor in zip(posiciones, entidades, suma_total):
        bottom_pos = 0
        bottom_neg = 0
        annotations_externas = []
        for i, valor_col in enumerate(valores):
            current_val = valor_col[pos]
            # --- FORZAR VISIBILIDAD DE LA BARRA ESPECIAL ---
            es_barra_especial = False
            # Detectar si esta barra es la especial (por ejemplo, si tiene borde punteado y color_borde personalizado)
            estilo_borde_personalizado = estilos_borde_personalizados.get(entidad)
            color_borde_personalizado = colores_borde_personalizados.get(entidad)
            if estilo_borde_personalizado and i < len(estilo_borde_personalizado):
                if estilo_borde_personalizado[i] in ['dotted', 'punteado']:
                    es_barra_especial = True

            # Si es la barra especial, nunca la omitas
            if not es_barra_especial:
                if current_val == 0 and capsulas_cero:
                    continue

            color_fondo_personalizado = colores_fondo_personalizados.get(entidad)
            grosor_borde_personalizado = grosores_borde_personalizados.get(entidad)
            color_texto_personalizado = colores_texto_personalizados.get(entidad)

            # --- RESALTADO POR NOMBRE DE ETIQUETA (solo en la etiqueta del eje, no en la barra) ---
            nombre_etiqueta = entidades_formateadas[pos]
            if destacar_maximo and idx_max and pos in idx_max:
                color = color_maximo
                edge_color = 'none'
                line_style = '-'
                line_width = 2
                custom_text_color = color_texto_maximo
            else:
                # Si el fondo es 'none' o 'transparente', usar 'white' para que el borde se vea
                if color_fondo_personalizado and i < len(color_fondo_personalizado):
                    cf = color_fondo_personalizado[i]
                    if cf in ['none', 'transparente', None]:
                        color = 'white'
                    else:
                        color = cf
                else:
                    color = colores_asignados[i % len(colores_asignados)]
                # Soporte para borde punteado y estilos personalizados
                if color_borde_personalizado and i < len(color_borde_personalizado) and color_borde_personalizado[i]:
                    edge_color = color_borde_personalizado[i]
                else:
                    edge_color = '#114a44' if es_barra_especial else 'none'
                # Traducir estilos de borde YAML a matplotlib
                estilo = estilo_borde_personalizado[i] if estilo_borde_personalizado and i < len(estilo_borde_personalizado) and estilo_borde_personalizado[i] else '-'
                if estilo in ['dotted', 'punteado']:
                    line_style = (0, (1, 2))
                elif estilo in ['dashed', 'rayado']:
                    line_style = '--'
                elif estilo in ['solid', 'solido']:
                    line_style = '-'
                else:
                    line_style = estilo
                line_width = grosor_borde_personalizado[i] if grosor_borde_personalizado and i < len(grosor_borde_personalizado) and grosor_borde_personalizado[i] is not None else (3.5 if es_barra_especial else 1.5)
                custom_text_color = color_texto_personalizado[i] if color_texto_personalizado and i < len(color_texto_personalizado) and color_texto_personalizado[i] else (edge_color if es_barra_especial else None)

            text_color_interior = custom_text_color or color_valor_barra or get_text_color_for_bg(color)
            label = categorias[i]

            bar_bottom = bottom_pos if current_val > 0 else bottom_neg
            if orientacion == 'horizontal':
                ax.barh(pos, current_val, height=bar_height, left=bar_bottom, color=color, 
                       edgecolor=edge_color, linestyle=line_style, linewidth=line_width, zorder=2, label=label)
                if current_val > x_max:
                    x_max = current_val
                if current_val < x_min:
                    x_min = current_val
            else:
                ax.bar(pos, current_val, width=bar_height, bottom=bar_bottom, color=color, 
                      edgecolor=edge_color, linestyle=line_style, linewidth=line_width, zorder=2, label=label)

            if current_val > 0: bottom_pos += current_val
            else: bottom_neg += current_val

            area_barra = abs(current_val) * bar_height
            # Queremos filtrar por área mínima sólo cuando la etiqueta ES un porcentaje
            mostrar_valor   = valor_barra and current_val != 0          # siempre dentro
            mostrar_porcent = porcentaje_barra and (area_barra >= area_min or es_barra_especial)

            if mostrar_valor or mostrar_porcent or (entidad in textos_barra_personalizados):
                # ―──────── centro de la etiqueta ―────────
                if orientacion == 'horizontal':          # barras horizontales
                    x_text = bar_bottom + current_val / 2
                    y_text = pos
                else:                             # barras verticales
                    x_text = pos
                    y_text = bar_bottom + current_val / 2

                texto_final = ""
                if entidad in textos_barra_personalizados:
                    # lista de textos específicos por segmento
                    textos_barra = textos_barra_personalizados[entidad]
                    if i < len(textos_barra) and textos_barra[i] is not None:
                        texto_final = str(textos_barra[i])
                elif mostrar_valor and mostrar_porcent:
                    pct_val = 100 * current_val / total_valor if total_valor else 0
                    texto_final = f"{abs(current_val):,.0f}\n{abs(pct_val):.1f}%"
                elif mostrar_valor:
                    texto_final = f"{abs(current_val):,.0f}"
                elif mostrar_porcent:
                    pct_val = 100 * current_val / total_valor if total_valor else 0
                    texto_final = f"{abs(pct_val):.1f}%"

                ax.text(
                    x_text, y_text, texto_final,
                    ha='center', va='center',
                    fontdict={
                        'family': font_config['family'],
                        'size'  : font_config['valor_porcentaje_barra']['size'],
                        'weight': font_config['valor_porcentaje_barra']['weight'],
                        'color' : color_valor_barra or get_text_color_for_bg(color)
                    },
                    linespacing=1.3, zorder=10
                )

        if annotations_externas:
            texto_x_base = pos + bar_height * 0.6 
            annotations_externas.sort(key=lambda item: item['y_center'])
            num_ann = len(annotations_externas)
            y_coords = np.linspace(annotations_externas[0]['y_center'], annotations_externas[-1]['y_center'], num_ann) if num_ann > 1 else [annotations_externas[0]['y_center']] if num_ann == 1 else []
            
            for j, ann in enumerate(annotations_externas):
                texto_y = y_coords[j]
                ax.text(texto_x_base, texto_y, ann['text'], ha='left', va='center',
                        fontsize=font_config['valor_porcentaje_barra']['size'] * 0.9,
                        fontfamily=font_config['family'],
                        fontweight=font_config['valor_porcentaje_barra']['weight'],
                        color='#333333', zorder=5)
                ax.plot([texto_x_base, ann['x_center']], [texto_y, ann['y_center']], color='grey', linewidth=0.6, zorder=4)

        if valor_total and "..." not in str(entidades_formateadas[pos]):
            valor_a_mostrar = total_valor
            if es_divergente:
                if not porcentaje_divergente:
                    valor_a_mostrar = suma_absoluta_por_barra.loc[entidad]
                else:
                    valor_a_mostrar = suma_positivos_por_barra.loc[entidad]

            if capsulas_cero or valor_a_mostrar != 0:
                texto_a_mostrar = f"{int(valor_a_mostrar):,}"
                if etiquetas_finales is not None and not pd.isna(etiquetas_finales.iloc[pos]):
                    texto_a_mostrar = str(etiquetas_finales.iloc[pos])

                # --- TOTAL por barra (fuera de la barra) ---
                if orientacion == 'horizontal': 
                    x_text = (bottom_pos if es_divergente else total_valor) + x_max * desplazamiento_capsula
                    y_text = pos
                    ha_val, va_val = 'left', 'center'
                else:  # Barras verticales
                    x_text = pos
                    y_text = (bottom_pos if es_divergente else total_valor) + x_max * desplazamiento_capsula
                    ha_val, va_val = 'center', 'bottom'

                ax.text(
                    x_text, y_text, texto_a_mostrar,
                    ha=ha_val, va=va_val,
                    fontdict={
                        'family': font_config['family'],
                        'size'  : font_config['valor_capsula']['size'],
                        'weight': font_config['valor_capsula']['weight'],
                        'color' : (color_texto_maximo if (destacar_maximo and idx_max and pos in idx_max)
                                   else font_config['valor_capsula']['color'])
                    },
                    zorder=10
                )

        if es_divergente and valor_total and bottom_neg < 0:
            valor_negativo_total = suma_negativos_por_barra.loc[entidad]
            if capsulas_cero or valor_negativo_total != 0:
                texto_a_mostrar_neg = f"{int(abs(valor_negativo_total)):,}"
                texto_capsula_neg = f"{espacio*2}{texto_a_mostrar_neg}{espacio*2}"
                text_y_pos_neg = bottom_neg - x_max * desplazamiento_capsula

                if not quitar_capsula:
                    ax.text(pos, text_y_pos_neg, texto_capsula_neg,
                        bbox=dict(boxstyle="round,pad=0.15,rounding_size=0.8", facecolor=(1, 1, 1, 0), edgecolor='#002F2A', linewidth=1.5),
                        ha='center', va='top',
                        fontdict={
                            'family': font_config['family'], 'size': font_config['valor_capsula']['size'],
                            'weight': font_config['valor_capsula']['weight'], 'color': font_config['valor_capsula']['color']
                        })
                else:
                    ax.text(pos, text_y_pos_neg, texto_a_mostrar_neg, ha='center', va='top',
                        fontdict={
                            'family': font_config['family'], 'size': font_config['valor_capsula']['size'],
                            'weight': font_config['valor_capsula']['weight'], 'color': font_config['valor_capsula']['color']
                        })

        if porcentaje_total:
            valor_numerador = total_valor
            valor_denominador = total_general
            if es_divergente:
                if not porcentaje_divergente:
                    if hasattr(suma_absoluta_por_barra, 'loc'):
                        valor_numerador = suma_absoluta_por_barra.loc[entidad]
                    else:
                        valor_numerador = suma_absoluta_por_barra
                    valor_denominador = total_general_absoluto
                else: # porcentaje_divergente es True
                    if hasattr(suma_positivos_por_barra, 'loc'):
                        valor_numerador = suma_positivos_por_barra.loc[entidad]
                    else:
                        valor_numerador = suma_positivos_por_barra
                    valor_denominador = total_general_positivos

            porcentaje = round((valor_numerador / valor_denominador) * 100, 1) if valor_denominador != 0 else 0
            
            desplazamiento_y = 0
            if valor_total:
                desplazamiento_y = x_max * (0.15 if not quitar_capsula else 0.08)
            else:
                desplazamiento_y = x_max * 0.03
            
            base_pos_y = bottom_pos if es_divergente else total_valor
            if ejeY_negativo_a_positivo:
                desplazamiento_y = -desplazamiento_y
            
            desplazamiento_final = base_pos_y + desplazamiento_y + (x_max * separar_por_total)

            ax.text(pos, desplazamiento_final, f"{porcentaje}%", ha='center', va='bottom',
                    color=font_config['porcentaje_total']['color'],
                    fontdict={'family': font_config['family'], 'size': font_config['porcentaje_total']['size'], 'weight': font_config['porcentaje_total']['weight']})

    if porcentaje_total_inicio and resaltar_etiquetas:
        entidades_formateadas = ["" if e in resaltar_etiquetas else e for e in entidades_formateadas]

    # Configurar las etiquetas y límites según la orientación
    if orientacion == 'horizontal':
        # Para barras horizontales
        ax.set_yticks(posiciones)
        # --- empujar etiquetas Y hacia la izquierda (sin que invadan el %) ---
        renderer = fig.canvas.get_renderer()
        etiqueta_mas_larga = max(entidades_formateadas, key=len)
        bb_lbl = fig.text(0, 0, etiqueta_mas_larga,
                          fontsize=font_config['variable_y']['size'],
                          fontfamily=font_config['family'],
                          visible=False).get_window_extent(renderer=renderer)

        bb_pct = fig.text(0, 0, "100.0 %",
                          fontsize=font_config['porcentaje_total']['size'],
                          fontfamily=font_config['family'],
                          visible=False).get_window_extent(renderer=renderer)


        GAP_PX  = 6                             
        EXTRA_CM = 2                  
        EXTRA_PX = EXTRA_CM * fig.dpi / 2.54     # 2 cm → px con dpi actual
        pad_px = bb_pct.width + GAP_PX + EXTRA_PX
        pad_pt = pad_px * 72.0 / fig.dpi  # píxeles → puntos
        pad_pt += espacio_inicio          # suma extra desde YAML

        ax.tick_params(axis='y', pad=pad_pt)

        ancho_px = bb_lbl.width + pad_px + 20 # etiqueta + % + colchón extra
    else:
        # valores nulos para la rama vertical (evita NameError)
        bb_lbl = bb_pct = None
        pad_px = pad_pt = 0
        ancho_px = 60  # Valor fijo para barras verticales
    fig_w_px = fig.get_size_inches()[0] * fig.dpi
    left_margin = max(0.25, ancho_px / fig_w_px)

    # --- 1. margen izquierdo dinámico si hay porcentaje al inicio ---
    extra_margin = 0.25  # Valor base (en fracción de ancho figura)
    if orientacion == 'horizontal' and porcentaje_total_inicio:
        import matplotlib.transforms as mtrans
        txt = fig.text(0, 0, "100.0 %", fontsize=font_config['porcentaje_total']['size'],
                      fontfamily=font_config['family'], visible=False)
        fig.canvas.draw()
        bb = txt.get_window_extent()
        txt.remove()
        pts_w = bb.width + kwargs.get('espacio_inicio', 70)  # 70 pt = padding configurable
        extra_margin = pts_w / fig.get_size_inches()[0] / fig.dpi
        # Nos quedamos con el mayor margen calculado hasta ahora
        left_margin = max(left_margin, extra_margin)


    # --- 2. porcentaje a la izquierda de cada barra horizontal ---
    if porcentaje_total_inicio and orientacion == 'horizontal':
        import matplotlib.transforms as mtrans
        trans = mtrans.blended_transform_factory(ax.transAxes, ax.transData)  # x en fracción-eje, y en datos
        x_frac = -0.01
        for pos, entidad in enumerate(entidades):
            valor_numerador = suma_total.iloc[pos]
            if es_divergente and not porcentaje_divergente:
                valor_numerador = suma_absoluta_por_barra.loc[entidad]
            perc = 0 if total_general == 0 else round(valor_numerador / total_general * 100, 1)
            ax.text(x_frac, pos, f"{perc:.1f} %", transform=trans,
                    ha='right', va='center',
                    fontsize=font_config['porcentaje_total']['size'],
                    fontfamily=font_config['family'],
                    fontweight=font_config['porcentaje_total']['weight'],
                    color=kwargs.get('color_porcentaje_inicio', font_config['porcentaje_total']['color']))
        # Ajustar límites para barras horizontales
        ax.set_ylim(len(entidades) - 0.5, -0.5)  # Invertir eje Y para que las barras vayan de arriba a abajo
        # Ajustar límites del eje X (ahora horizontal)
        if y_limits:
            x_min, x_max = y_limits
            ax.set_xlim(0, x_max)  # Empezar desde 0 para barras horizontales
        else:
            ax.set_xlim(0, x_max * 1.15)  # Dar un poco más de espacio para valores
    else:
        # Para barras verticales 
        ax.set_xticks(posiciones)
        if orientacion_etiqueta_x == 'horizontal':
            rotation_val = 0
        elif orientacion_etiqueta_x == '45':
            rotation_val = 45
        else:
            rotation_val = 90
        ha_val = 'right' if orientacion_etiqueta_x != 'horizontal' else 'center'

        # Etiquetas de categorías en eje X para barras verticales
        ax.set_xticklabels(entidades_formateadas,
                           fontsize=font_config['variable_x']['size'],
                           fontweight=font_config['variable_x']['weight'],
                           fontfamily=font_config['family'],
                           rotation=rotation_val,
                           ha=ha_val)
        # Forzar renderizado para inicializar los objetos Text
        fig.canvas.draw()
    if orientacion == 'horizontal':
        # Para barras horizontales
        if y_limits:
            y_min, y_max = y_limits
            ax.set_xlim(y_min, y_max)
        else:
            ax.set_xlim(0, x_max * 1.1)

        # Mostrar etiquetas del eje X (valores)
        ax.set_xticklabels(
            [str(x) for x in ax.get_xticks()],
            fontsize=font_config['variable_x']['size'],
            fontweight=font_config['variable_x']['weight'],
            fontfamily=font_config['family']
        )
    else:
        # Para barras verticales
        if y_limits:
            y_min, y_max = y_limits
            ax.set_ylim(y_max if ejeY_negativo_a_positivo else y_min, 
                       y_min if ejeY_negativo_a_positivo else y_max)
        else:
            y_min = -x_max if es_divergente else 0
            y_max = x_max
            ax.set_ylim(y_max if ejeY_negativo_a_positivo else y_min, 
                       y_min if ejeY_negativo_a_positivo else y_max)
        
    # Configurar el formato de los valores según la orientación
    if orientacion == 'horizontal':
        ax.xaxis.set_major_locator(mticker.MaxNLocator(nbins='auto', steps=[1, 2, 5, 10]))
        ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{int(abs(x)):,}"))
        plt.setp(ax.get_xticklabels(), **font_config['variable_x'])
        
        if grillas:
            ax.grid(visible=True, axis='x', color='#B9B9B9', linewidth=0.75, linestyle='-')
    else:
        ax.yaxis.set_major_locator(mticker.MaxNLocator(nbins='auto', steps=[1, 2, 5, 10]))
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{int(abs(x)):,}"))
        plt.setp(ax.get_yticklabels(), **font_config['variable_y'])
        
        if grillas:
            ax.grid(visible=True, axis='y', color='#B9B9B9', linewidth=0.75, linestyle='-')
        if porcentaje_total_inicio:
            ax.tick_params(axis='x', pad=espacio_inicio)
        
    if nombre_eje_x:
        ax.set_xlabel(nombre_eje_x, labelpad=18, **font_config['nombre_eje_x'])
    if nombre_eje_y:
        ax.set_ylabel(nombre_eje_y, labelpad=18, **font_config['nombre_eje_y'])

    # Ajustes finales de etiquetas del eje X (rotación, alineación y resaltado robusto)
    # Forzar renderizado para asegurar que las etiquetas existen y están actualizadas
    fig.canvas.draw()
    xticklabels = ax.get_xticklabels()
    # Ajustar rotación y alineación según el texto real
    for label in xticklabels:
        txt = label.get_text()
        if txt == "Previo":
            label.set_rotation(90)
            label.set_ha('center')
        elif txt == "...":
            label.set_rotation(0)
            label.set_ha('center')
    # --- RESALTADO VISUAL DE ETIQUETAS EN EL EJE X (comparación flexible) ---
    etiquetas_eje_x = [label.get_text() for label in xticklabels]
    etiquetas_eje_x_norm = [normaliza(e) for e in etiquetas_eje_x]
    import os
    debug_path = os.path.abspath("debug_labels.txt")
    try:
        with open(debug_path, "w", encoding="utf-8") as f:
            f.write("[DEBUG] Etiquetas reales eje X:\n" + str(etiquetas_eje_x) + "\n")
            f.write("[DEBUG] Etiquetas eje X normalizadas:\n" + str(etiquetas_eje_x_norm) + "\n")
            f.write("[DEBUG] Etiquetas a resaltar:\n" + str(list(etiquetas_resaltadas)) + "\n")
            f.write("[DEBUG] Etiquetas a resaltar normalizadas:\n" + str(list(etiquetas_resaltadas_norm)) + "\n")
    except Exception as e:
        pass
    # Resaltado visual solo si hay etiquetas a resaltar
    if etiquetas_resaltadas_norm:
        for label, txt_norm in zip(xticklabels, etiquetas_eje_x_norm):
            if txt_norm in etiquetas_resaltadas_norm:
                color_resaltado = kwargs.get('color_resalt_etique', '#a3173e')
                color_texto = '#fff'
                # El borde será igual al color de fondo
                label.set_bbox(dict(facecolor=color_resaltado, edgecolor=color_resaltado, boxstyle="round,pad=0.15,rounding_size=0.8"))
                label.set_color(color_texto)
                label.set_fontweight('bold')
            
     # Configuración de la leyenda.
    if leyenda:
        handles, labels = ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        
        all_labels = list(categorias)
        final_handles = [by_label.get(lbl, Patch(color=colores_asignados[i % len(colores_asignados)])) for i, lbl in enumerate(all_labels)]
        
        # Ajustar posición de la leyenda
        if posicion_leyenda == 'abajo':
            # Aumentar la separación cuando las etiquetas están rotadas
            extra_sep = 0.15 if orientacion_etiqueta_x in ['45', '90'] else 0
            loc_leyenda, bbox_leyenda = ('upper center', (0.5, -0.25 - extra_sep - aumenta_sep_leyenda))
        else:
            loc_leyenda, bbox_leyenda = ('upper center', (0.5, 1.15 + aumenta_sep_leyenda))

        num_cols_leyenda = ncol_leyenda if ncol_leyenda is not None else len(all_labels)

        ax.legend(final_handles, all_labels, title=leyenda if isinstance(leyenda, str) else None,
                  fontsize=font_config['leyenda']['size'], title_fontsize=font_config['leyenda']['size'],
                  loc=loc_leyenda, bbox_to_anchor=bbox_leyenda, frameon=False,
                  ncol=num_cols_leyenda, handlelength=1, handleheight=1)
        
    # Limpieza de los bordes del gráfico según la orientación
    if orientacion == 'horizontal':
        ax.spines[['top', 'right', 'bottom']].set_visible(False)
        ax.spines['left'].set_visible(True)
    else:
        ax.spines[['top', 'right', 'left']].set_visible(False)
        ax.spines['bottom'].set_visible(True)

    # Ajustar las líneas de grilla según la orientación
    if orientacion == 'horizontal':
        ax.grid(visible=grillas, axis='x', color='#B9B9B9', linewidth=0.75, linestyle='-')
        # Línea en cero para gráficos divergentes
        if es_divergente:
            ax.axvline(0, color='black', linewidth=1)
    else:
        ax.grid(visible=grillas, axis='y', color='#B9B9B9', linewidth=0.75, linestyle='-')
        # Línea en cero para gráficos divergentes
        if es_divergente:
            ax.axhline(0, color='black', linewidth=1)

    # --- 9. GUARDADO Y VISUALIZACIÓN ---
    # Creación del directorio de salida si no existe.
    os.makedirs(output_dir, exist_ok=True)
    
    # Ajustar los márgenes según la orientación y la presencia de leyenda
    if orientacion == 'horizontal':
        right_margin = 0.95
        bottom_margin = 0.15
        top_margin = 0.85 if leyenda and posicion_leyenda == 'arriba' else 0.95
    else:
        left_margin = 0.15
        right_margin = 0.95
        bottom_margin = 0.2
        top_margin = 0.85 if leyenda and posicion_leyenda == 'arriba' else 0.95
    # Ajustar los márgenes al final
    plt.subplots_adjust(left=left_margin, right=right_margin,
                       top=top_margin, bottom=bottom_margin)
    
    # Guardado de la gráfica en formato SVG y aplicación del flujo de exportación
    nombre_archivo = f"{nombre}.svg"
    ruta_temporal = os.path.join(output_dir, nombre_archivo)
    
    # Guardar SVG sin recorte para evitar que se pierda contenido a la izquierda
    plt.savefig(ruta_temporal, format='svg', dpi=300, transparent=True)
    
    # Aplicar el flujo de exportación
    try:
        from svg_cleanup.flujo_exportacion import exportar_grafica
        archivo_final = exportar_grafica(ruta_temporal, nombre, output_dir)
        
        # Limpiar archivo temporal
        if archivo_final and os.path.exists(ruta_temporal):
            os.remove(ruta_temporal)
    except ImportError:
        print("Nota: Módulo de exportación no disponible. Se guardará el SVG sin optimizar.")
    except Exception as e:
        print(f"Advertencia: Error en el flujo de exportación: {e}")
    
    plt.show()