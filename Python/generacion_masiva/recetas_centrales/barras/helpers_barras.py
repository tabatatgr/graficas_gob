import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager
from pathlib import Path
import matplotlib.ticker as mticker
from matplotlib.ticker import FuncFormatter
from matplotlib.patches import Patch
import datetime

def preparar_datos_barras(
    df_wide,
    nombre=None,
    union_izquierda=0,
    union_derecha=0,
    agregar_datos=None,
    asignar_etiquetas=None,
    ordenar_por='valor',
    orden='descendente',
    sustituir_etiquetas=None,
    kwargs=None
):
    """
    Procesa y prepara todos los datos necesarios para graficar barras.
    Devuelve un diccionario con todos los datos y metadatos requeridos para la visualización.
    """
    # --- INICIO MIGRACIÓN LÓGICA DE DATOS ---
    import numpy as np
    import datetime
    if kwargs is None:
        kwargs = {}
    df_wide = df_wide.copy()
    categorias_x = df_wide.columns[0]
    if pd.api.types.is_integer_dtype(df_wide[categorias_x]) and df_wide[categorias_x].between(1900, 2100).all():
        df_wide[categorias_x] = pd.to_datetime(df_wide[categorias_x], format='%Y')
    df_wide = df_wide.set_index(categorias_x)

    # --- Lógica para detectar y estilizar proyecciones automáticamente ---
    import datetime
    hoy = datetime.date.today()
    anio_actual = hoy.year
    estilos_proyeccion = kwargs.get('estilos_proyeccion', {
        'colores_fondo': 'none',
        'colores_borde': '#114a44',
        'estilos_borde': 'dotted',
        'grosores_borde': 3.5,
        'colores_texto': '#114a44',
    })
    # Si el índice es fecha o año, aplicar estilos a filas futuras
    if hasattr(df_wide.index, 'dtype') and (np.issubdtype(df_wide.index.dtype, np.datetime64) or np.issubdtype(df_wide.index.dtype, np.integer)):
        for idx in df_wide.index:
            anio = idx.year if hasattr(idx, 'year') else int(str(idx)[:4]) if str(idx)[:4].isdigit() else None
            if anio and anio > anio_actual:
                # Aplica estilos personalizados a la fila de proyección
                if 'estilos' not in df_wide.columns:
                    df_wide['estilos'] = None
                if pd.isnull(df_wide.at[idx, 'estilos']):
                    df_wide.at[idx, 'estilos'] = {}
                for k, v in estilos_proyeccion.items():
                    df_wide.at[idx, 'estilos'][k] = v

    # Unir barras si aplica
    df_wide, etiqueta_union_izq = unir_barras(df_wide, union_izquierda, 'izquierda')
    df_wide, etiqueta_union_der = unir_barras(df_wide, union_derecha, 'derecha')

    # --- Agregar barra 'Previo' y puntos suspensivos si se solicita ---
    if kwargs is None:
        kwargs = {}
    agregar_barra_previa = kwargs.get('agregar_barra_previa', False)
    fecha_corte = kwargs.get('fecha_corte', None)
    nombre_barra_previa = kwargs.get('nombre_barra_previa', 'Previo')
    columnas_valores = list(df_wide.columns)
    if agregar_barra_previa and fecha_corte is not None:
        # Separar datos previos al corte
        mask_previos = df_wide.index < fecha_corte
        if mask_previos.any():
            suma_previos = df_wide.loc[mask_previos, columnas_valores].sum()
            # Crear barra 'Previo'
            df_previo = pd.DataFrame([suma_previos.values], columns=columnas_valores, index=[nombre_barra_previa])
            # Crear barra de puntos suspensivos
            df_puntos = pd.DataFrame([[0]*len(columnas_valores)], columns=columnas_valores, index=['...'])
            # Filtrar datos normales (a partir del corte)
            df_restantes = df_wide.loc[~mask_previos]
            # Concatenar: Previo, ..., resto
            df_wide = pd.concat([df_previo, df_puntos, df_restantes])
    # Si no, procesar agregar_datos manual si existe
    elif agregar_datos:
        for fila in agregar_datos:
            if len(fila) >= 3:
                fecha, etiqueta, valores = fila[:3]
                if etiqueta not in df_wide.index:
                    df_wide.loc[etiqueta] = valores
        df_wide = df_wide.sort_index()


    # --- Agregar barra especial punteada si se solicita ---
    barra_especial = kwargs.get('barra_especial', False)
    valor_barra_especial = kwargs.get('valor_barra_especial', None)
    texto_barra_especial = kwargs.get('texto_barra_especial', None)
    if barra_especial and valor_barra_especial is not None:
        # Determinar número de columnas de valores
        cols_valores = [c for c in df_wide.columns if c not in ['estilos', 'texto_personalizado']]
        valores = [0]*(len(cols_valores)-1) + [valor_barra_especial]
        etiqueta_especial = " "  # Etiqueta vacía
        # Agregar fila al final
        df_wide.loc[etiqueta_especial] = valores
        # Agregar texto personalizado si se solicita
        if texto_barra_especial:
            if 'texto_personalizado' not in df_wide.columns:
                df_wide['texto_personalizado'] = None
            df_wide.at[etiqueta_especial, 'texto_personalizado'] = texto_barra_especial
        # Agregar estilos punteados
        if 'estilos' not in df_wide.columns:
            df_wide['estilos'] = None
        estilos_punteado = {
            'colores_fondo': 'none',
            'colores_borde': '#114a44',
            'estilos_borde': 'dotted',
            'grosores_borde': 3.5,
            'colores_texto': '#114a44',
        }
        df_wide.at[etiqueta_especial, 'estilos'] = estilos_punteado

    # Asignar etiquetas personalizadas
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
        if kwargs.get('porcentaje_divergente', False):
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

    # Ordenar
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

    # Etiquetas formateadas
    es_fecha = any(isinstance(idx, (pd.Timestamp, np.datetime64)) for idx in df_wide.index if idx not in [etiqueta_union_izq, etiqueta_union_der])
    if es_fecha:
        fechas_a_formatear = [idx for idx in df_wide.index if isinstance(idx, (pd.Timestamp, np.datetime64))]
        mapa_fechas = dict(zip(fechas_a_formatear, formato_fechas(fechas_a_formatear)))
        entidades_formateadas = [mapa_fechas.get(idx, str(idx)) for idx in df_wide.index]
    else:
        entidades_formateadas = [str(idx) for idx in df_wide.index]

    # Sustitución de etiquetas
    if sustituir_etiquetas:
        if isinstance(sustituir_etiquetas, dict):
            for i, etiqueta in enumerate(entidades_formateadas):
                if etiqueta in sustituir_etiquetas:
                    entidades_formateadas[i] = str(sustituir_etiquetas[etiqueta])
        elif isinstance(sustituir_etiquetas, list):
            if len(sustituir_etiquetas) != len(entidades_formateadas):
                raise ValueError("La longitud de 'sustituir_etiquetas' debe coincidir con el número de barras.")
            entidades_formateadas = list(sustituir_etiquetas)
        else:
            raise ValueError("sustituir_etiquetas debe ser un diccionario o una lista.")

    # --- Empaquetar todo en un dict para la visualización ---
    datos = {
        'df_wide': df_wide,
        'nombre': nombre,
        'etiquetas_finales': etiquetas_finales,
        'suma_total': suma_total,
        'total_general': total_general,
        'es_divergente': es_divergente,
        'suma_positivos_por_barra': suma_positivos_por_barra,
        'suma_negativos_por_barra': suma_negativos_por_barra,
        'suma_absoluta_por_barra': suma_absoluta_por_barra,
        'total_general_absoluto': total_general_absoluto,
        'total_general_positivos': total_general_positivos,
        'entidades': entidades,
        'entidades_formateadas': entidades_formateadas,
        'etiqueta_union_izq': etiqueta_union_izq,
        'etiqueta_union_der': etiqueta_union_der,
    }
    return datos

# --- Helper para visualización y ploteo de barras ---
def graficar_barras(
    datos,
    font='Montserrat',
    fontsize_barra=15,
    fontsize_valor_total=20,
    bar_height=0.95,
    bar_height_override=False,
    aumenta_ancho_fig=0,
    aumenta_alto_fig=0,
    orientacion='vertical',
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
    grillas=True,
    leyenda=None,
    posicion_leyenda='arriba',
    separar_por_total=0.0,
    y_limits=None,
    nombre_eje_x=None,
    nombre_eje_y=None,
    resaltar_etiquetas=None,
    porcentaje_abajo=True,
    orientacion_etiqueta_x=None,
    altura_min=0,
    ejeY_negativo_a_positivo=False,
    capsulas_cero=True,
    ncol_leyenda=None,
    desplazamiento_capsula=0.03,
    output_dir="output",
    kwargs=None
):
    """
    Recibe los datos procesados y todos los parámetros de visualización, y genera el gráfico de barras.
    Devuelve (fig, ax) de matplotlib.
    """
    import matplotlib.pyplot as plt
    from matplotlib import ticker
    from matplotlib.patches import Patch
    from matplotlib.ticker import FuncFormatter
    # --- Extraer datos del dict ---
    df = datos['df_wide'] if 'df_wide' in datos else datos['df'] if 'df' in datos else None
    if df is None:
        raise ValueError("No se encontró DataFrame procesado en los datos.")
    entidades = datos.get('entidades', df.index.values)
    etiquetas = datos.get('entidades_formateadas', [str(e) for e in entidades])
    suma_total = datos.get('suma_total', df.sum(axis=1))
    etiquetas_finales = datos.get('etiquetas_finales', None)
    es_divergente = datos.get('es_divergente', False)
    suma_positivos_por_barra = datos.get('suma_positivos_por_barra', None)
    suma_negativos_por_barra = datos.get('suma_negativos_por_barra', None)
    suma_absoluta_por_barra = datos.get('suma_absoluta_por_barra', None)
    total_general = datos.get('total_general', suma_total.sum())
    total_general_absoluto = datos.get('total_general_absoluto', None)
    total_general_positivos = datos.get('total_general_positivos', None)
    etiqueta_union_izq = datos.get('etiqueta_union_izq', None)
    etiqueta_union_der = datos.get('etiqueta_union_der', None)

    # --- Configuración de figura ---
    n_barras = len(df)
    n_series = df.shape[1]
    bar_height, aumenta_alto_fig, aumenta_ancho_fig, aumenta_sep_leyenda = procesar_espaciado(kwargs or {}, bar_height, aumenta_alto_fig, aumenta_ancho_fig, aumenta_sep_leyenda)
    width = max(8 + aumenta_ancho_fig, 2)
    height = max(0.6 * n_barras * bar_height + 2 + aumenta_alto_fig, 2)
    fig, ax = plt.subplots(figsize=(width, height), dpi=300)

    # --- Paleta de colores ---
    if paleta_colores is None:
        paleta_colores = plt.get_cmap('tab10').colors if n_series <= 10 else plt.get_cmap('tab20').colors
    if isinstance(paleta_colores, dict):
        colores = [paleta_colores.get(col, '#888888') for col in df.columns]
    else:
        colores = paleta_colores[:n_series]

    # --- Plot principal ---
    indices = range(n_barras)
    bottom = np.zeros(n_barras)
    bars = []
    for i, col in enumerate(df.columns):
        valores = df[col].values
        b = ax.bar(indices, valores, bottom=bottom, color=colores[i], label=str(col), height=bar_height)
        bars.append(b)
        bottom += valores

    # --- Etiquetas de barra (valores) ---
    if valor_barra:
        for b in bars:
            for rect in b:
                h = rect.get_height()
                if h == 0:
                    continue
                ax.text(rect.get_x() + rect.get_width()/2, rect.get_y() + h/2, f"{h:,.0f}", ha='center', va='center', fontsize=fontsize_barra, color='white')

    # --- Etiqueta de total ---
    if valor_total:
        for idx, total in enumerate(suma_total):
            ax.text(idx, total, f"{total:,.0f}", ha='center', va='bottom', fontsize=fontsize_valor_total, fontweight='bold')

    # --- Ejes y etiquetas ---
    ax.set_xticks(indices)
    ax.set_xticklabels(etiquetas, fontsize=fontsize_barra, rotation=orientacion_etiqueta_x or 0)
    if nombre_eje_y:
        ax.set_ylabel(nombre_eje_y, fontsize=fontsize_barra)
    if nombre_eje_x:
        ax.set_xlabel(nombre_eje_x, fontsize=fontsize_barra)

    # --- Leyenda ---
    if leyenda is not False:
        ax.legend(loc='upper right' if posicion_leyenda=='arriba' else 'lower right', ncol=ncol_leyenda or 1)

    # --- Grillas ---
    if grillas:
        ax.yaxis.grid(True, linestyle='--', alpha=0.5)

    # --- Límites ---
    if y_limits:
        ax.set_ylim(*y_limits)

    # --- Ajustes visuales extra ---
    fig.tight_layout()
    return fig, ax
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager
from pathlib import Path
import matplotlib.ticker as mticker
from matplotlib.ticker import FuncFormatter
from matplotlib.patches import Patch

ESPACIADO_CONFIGS = {
    "compacto": {"bar_height": 0.9, "aumenta_alto_fig": -5, "aumenta_ancho_fig": -2, "aumenta_sep_leyenda": 0.08},
    "normal": {"bar_height": 0.7, "aumenta_alto_fig": 0, "aumenta_ancho_fig": 0, "aumenta_sep_leyenda": 0.0},
    "amplio": {"bar_height": 0.5, "aumenta_alto_fig": 3, "aumenta_ancho_fig": 1, "aumenta_sep_leyenda": 0.0},
    "muy_compacto": {"bar_height": 0.95, "aumenta_alto_fig": -8, "aumenta_ancho_fig": -3, "aumenta_sep_leyenda": 0.12}
}

def formato_fechas(fechas):
    fechas = pd.to_datetime(fechas)
    if len(set(f.year for f in fechas)) == len(fechas):
        return [str(f.year) for f in fechas]
    else:
        return [f.strftime("%d-%m-%Y") for f in fechas]

def get_text_color_for_bg(bg_color_hex):
    try:
        hex_color = bg_color_hex.lstrip('#')
        if len(hex_color) != 6:
            return '#ffffff'
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        return '#000000' if luminance > 0.6 else '#ffffff'
    except (ValueError, TypeError):
        return '#ffffff'

def procesar_espaciado(kwargs, bar_height, aumenta_alto_fig, aumenta_ancho_fig, aumenta_sep_leyenda):
    espaciado = kwargs.get('espaciado', None)
    if espaciado and espaciado in ESPACIADO_CONFIGS:
        config = ESPACIADO_CONFIGS[espaciado]
        if bar_height == 0.5:
            bar_height = config['bar_height']
        if aumenta_alto_fig == 0:
            aumenta_alto_fig = config['aumenta_alto_fig']
        if aumenta_ancho_fig == 0:
            aumenta_ancho_fig = config['aumenta_ancho_fig']
        if aumenta_sep_leyenda == 0.0:
            aumenta_sep_leyenda = config['aumenta_sep_leyenda']
    elif espaciado and espaciado not in ESPACIADO_CONFIGS:
        print(f"Advertencia: espaciado='{espaciado}' no reconocido. Opciones: {list(ESPACIADO_CONFIGS.keys())}")
    return bar_height, aumenta_alto_fig, aumenta_ancho_fig, aumenta_sep_leyenda

def cargar_fuentes(font_dirs=None):
    if font_dirs is None:
        font_dirs = [Path("../0_fonts")]
    font_files = font_manager.findSystemFonts(fontpaths=font_dirs)
    for font_file in font_files:
        font_manager.fontManager.addfont(font_file)

def unir_barras(df, num_barras, lado):
    if num_barras <= 1 or len(df) < num_barras:
        return df, None
    if lado == 'izquierda':
        seleccion = df.iloc[:num_barras]
        df_resto = df.iloc[num_barras:]
    else:
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

