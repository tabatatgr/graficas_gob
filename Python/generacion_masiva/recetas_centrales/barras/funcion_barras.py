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

def aplicar_flujo_optimizado(archivo_entrada, nombre_base, output_dir="output"):
    """Aplica el flujo completo optimizado para Figma"""
    try:
        # Importar el optimizador unificado
        import sys
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from svg_cleanup.flujo_exportacion import exportar_grafica
        
        return exportar_grafica(archivo_entrada, nombre_base, output_dir)
    except Exception as e:
        print(f"⚠️ Error en flujo optimizado: {e}")
        return archivo_entrada
    
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

def barras_verticales(
    df_wide, 
    nombre=None,
    font='Montserrat',
    fontsize_barra=15, 
    fontsize_valor_total=20,
    bar_height=0.5, 
    aumenta_ancho_fig=0,
    aumenta_alto_fig=0,
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
    porcentaje_abajo=True,
    orientacion_etiqueta_x=None,
    altura_min=0,
    ejeY_negativo_a_positivo=False,
    capsulas_cero=True,
    ncol_leyenda=None,
    usar_flujo_svg=False,
    output_dir="output",
    **kwargs
):
    """
    Genera un gráfico de barras verticales apiladas a partir de un DataFrame de pandas.
    
    Nuevos kwargs para espaciado:
    - espaciado: str. Presets: "compacto", "normal", "amplio", "muy_compacto"
    - sustituir_etiquetas: dict o list. Sustituye etiquetas específicas
    """
    
    # ** PROCESAMIENTO DE KWARGS DE ESPACIADO **
    espaciado = kwargs.get('espaciado', None)
    
    if espaciado and espaciado in ESPACIADO_CONFIGS:
        config = ESPACIADO_CONFIGS[espaciado]
        
        # Solo aplicar si no fueron especificados directamente como parámetros
        # Verificamos si los valores son los por defecto
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

            if etiqueta:
                etiquetas_personalizadas[categoria] = etiqueta
            if texto_barra:
                textos_barra_personalizados[categoria] = texto_barra
            if isinstance(opciones_extra, dict):
                if 'colores_fondo' in opciones_extra:
                    colores_fondo_personalizados[categoria] = opciones_extra['colores_fondo']
                if 'colores_borde' in opciones_extra:
                    colores_borde_personalizados[categoria] = opciones_extra['colores_borde']
                if 'estilos_borde' in opciones_extra:
                    estilos_borde_personalizados[categoria] = opciones_extra['estilos_borde']
                if 'grosores_borde' in opciones_extra:
                    grosores_borde_personalizados[categoria] = opciones_extra['grosores_borde']
                if 'colores_texto' in opciones_extra:
                    colores_texto_personalizados[categoria] = opciones_extra['colores_texto']

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
            total_general_positivos = suma_positivos_por_barra.sum()
        else:
            suma_absoluta_por_barra = df_wide.abs().sum(axis=1)
            total_general_absoluto = suma_absoluta_por_barra.sum()

    x_max_pos = df_wide[df_wide > 0].sum(axis=1).max()
    x_max_neg = df_wide[df_wide < 0].sum(axis=1).min()
    x_max = max(x_max_pos, abs(x_max_neg)) * 1.15
    if pd.isna(x_max): x_max = suma_total.max() * 1.15

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
                    entidades_formateadas[i] = sustituir_etiquetas[etiqueta]
        elif isinstance(sustituir_etiquetas, list):
            # Mantener la funcionalidad original para retrocompatibilidad
            if len(sustituir_etiquetas) != len(entidades_formateadas):
                raise ValueError("La longitud de 'sustituir_etiquetas' debe coincidir con el número de barras.")
            entidades_formateadas = list(sustituir_etiquetas)
        else:
            raise ValueError("sustituir_etiquetas debe ser un diccionario o una lista.")

    for i, entidad in enumerate(df_wide.index):
        if entidad in etiquetas_personalizadas and etiquetas_personalizadas[entidad]:
            entidades_formateadas[i] = etiquetas_personalizadas[entidad]

    for i, entidad in enumerate(entidades_formateadas):
        if "__espaciador__" in str(entidad) or (es_fecha and (df_wide.iloc[i] == 0).all()):
            entidades_formateadas[i] = "..."

    valores = [df_wide[col].values for col in df_wide.columns]
    categorias = df_wide.columns
    posiciones = np.arange(len(entidades))

    longitudes = [len(f"{espacio*4}{int(total_valor):,}{espacio*4}") for total_valor in suma_total]
    moda_capsula_len = mode(longitudes) if longitudes else 10
    extra_width = moda_capsula_len * 0.1
    base_width = max(12, len(entidades) * extra_width)
    
    # ** AJUSTES DE ESPACIADO EN DIMENSIONES **
    if espaciado == "compacto":
        base_width = max(10, base_width * 0.9)
    elif espaciado == "muy_compacto":
        base_width = max(8, base_width * 0.8)
    elif espaciado == "amplio":
        base_width = base_width * 1.15
    
    fig_width = base_width + aumenta_ancho_fig
    fig_height = 8 + aumenta_alto_fig
    
    # Validar dimensiones mínimas
    fig_width = max(6, fig_width)
    fig_height = max(4, fig_height)
    
    fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=300)

    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)

    for pos, entidad, total_valor in zip(posiciones, entidades, suma_total):
        bottom_pos = 0
        bottom_neg = 0
        annotations_externas = []
        for i, valor_col in enumerate(valores):
            current_val = valor_col[pos]
            if current_val == 0:
                continue

            color_fondo_personalizado = colores_fondo_personalizados.get(entidad)
            color_borde_personalizado = colores_borde_personalizados.get(entidad)
            estilo_borde_personalizado = estilos_borde_personalizados.get(entidad)
            grosor_borde_personalizado = grosores_borde_personalizados.get(entidad)
            color_texto_personalizado = colores_texto_personalizados.get(entidad)

            color = color_fondo_personalizado[i] if color_fondo_personalizado and i < len(color_fondo_personalizado) and color_fondo_personalizado[i] else colores_asignados[i % len(colores_asignados)]
            edge_color = color_borde_personalizado[i] if color_borde_personalizado and i < len(color_borde_personalizado) and color_borde_personalizado[i] else 'none'
            line_style = estilo_borde_personalizado[i] if estilo_borde_personalizado and i < len(estilo_borde_personalizado) and estilo_borde_personalizado[i] else '-'
            line_width = grosor_borde_personalizado[i] if grosor_borde_personalizado and i < len(grosor_borde_personalizado) and grosor_borde_personalizado[i] is not None else 1.5
            
            custom_text_color = color_texto_personalizado[i] if color_texto_personalizado and i < len(color_texto_personalizado) and color_texto_personalizado[i] else None
            text_color_interior = custom_text_color or color_valor_barra or get_text_color_for_bg(color)
            label = categorias[i]
            
            bar_bottom = bottom_pos if current_val > 0 else bottom_neg
            ax.bar(pos, current_val, width=bar_height, bottom=bar_bottom, color=color, edgecolor=edge_color, linestyle=line_style, linewidth=line_width, zorder=2, label=label)
            
            if current_val > 0: bottom_pos += current_val
            else: bottom_neg += current_val

            area_barra = abs(current_val) * bar_height
            if (porcentaje_barra or valor_barra or (entidad in textos_barra_personalizados)) and area_barra >= area_min:
                
                if es_divergente:
                    if porcentaje_divergente:
                        if current_val > 0:
                            base_porcentaje = suma_positivos_por_barra.loc[entidad]
                            porcentaje_valor = (current_val / base_porcentaje) * 100 if base_porcentaje != 0 else 0
                        else: # current_val < 0
                            base_porcentaje = suma_negativos_por_barra.loc[entidad]
                            porcentaje_valor = (current_val / base_porcentaje) * 100 if base_porcentaje != 0 else 0
                    else: # porcentaje_divergente es False
                        base_porcentaje = suma_absoluta_por_barra.loc[entidad]
                        porcentaje_valor = (current_val / base_porcentaje) * 100 if base_porcentaje != 0 else 0
                else: # no es divergente
                    porcentaje_valor = (current_val / total_valor) * 100 if total_valor != 0 else 0

                text_pos_y = bar_bottom + current_val / 2
                
                texto_final = ""
                if entidad in textos_barra_personalizados:
                    textos_barra = textos_barra_personalizados[entidad]
                    if i < len(textos_barra) and textos_barra[i] is not None:
                        texto_final = textos_barra[i]
                elif valor_barra and porcentaje_barra:
                    texto_final = f"{abs(current_val):,.0f} ({abs(porcentaje_valor):.1f}%)" if not porcentaje_abajo else f"{abs(current_val):,.0f}\n{abs(porcentaje_valor):.1f}%"
                elif valor_barra:
                    texto_final = f"{abs(current_val):,.0f}"
                elif porcentaje_barra:
                    texto_final = f"{abs(porcentaje_valor):.1f}%"

                if altura_min > 0 and abs(current_val) < altura_min:
                    hay_annotations_externas = True
                    annotations_externas.append({'text': texto_final, 'x_center': pos, 'y_center': text_pos_y})
                else:
                    ax.text(pos, text_pos_y, texto_final, va='center', ha='center',
                            fontsize=font_config['valor_porcentaje_barra']['size'],
                            fontfamily=font_config['family'],
                            fontweight=font_config['valor_porcentaje_barra']['weight'],
                            color=text_color_interior,
                            linespacing=1.5 if porcentaje_abajo else 1.2)

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
                else: # porcentaje_divergente es True
                    valor_a_mostrar = suma_positivos_por_barra.loc[entidad]

            if capsulas_cero or valor_a_mostrar != 0:
                texto_a_mostrar = f"{int(valor_a_mostrar):,}"
                if etiquetas_finales is not None and not pd.isna(etiquetas_finales.iloc[pos]):
                    texto_a_mostrar = str(etiquetas_finales.iloc[pos])
                
                texto_capsula = f"{espacio*2}{texto_a_mostrar}{espacio*2}"
                base_pos_y = bottom_pos if es_divergente else total_valor
                text_y_pos = base_pos_y + x_max * 0.03
                
                if not quitar_capsula:
                    ax.text(pos, text_y_pos, texto_capsula,
                        bbox=dict(boxstyle="round,pad=0.15,rounding_size=0.8", facecolor=(1, 1, 1, 0), edgecolor='#002F2A', linewidth=1.5),
                        ha='center', va='bottom',
                        fontdict={
                            'family': font_config['family'], 'size': font_config['valor_capsula']['size'],
                            'weight': font_config['valor_capsula']['weight'], 'color': font_config['valor_capsula']['color']
                        })
                else:
                    ax.text(pos, text_y_pos, texto_a_mostrar, ha='center', va='bottom',
                        fontdict={
                            'family': font_config['family'], 'size': font_config['valor_capsula']['size'],
                            'weight': font_config['valor_capsula']['weight'], 'color': font_config['valor_capsula']['color']
                        })

        if es_divergente and valor_total and bottom_neg < 0:
            valor_negativo_total = suma_negativos_por_barra.loc[entidad]
            if capsulas_cero or valor_negativo_total != 0:
                texto_a_mostrar_neg = f"{int(abs(valor_negativo_total)):,}"
                texto_capsula_neg = f"{espacio*2}{texto_a_mostrar_neg}{espacio*2}"
                text_y_pos_neg = bottom_neg - x_max * 0.03

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

        if porcentaje_total_inicio:
            valor_numerador = total_valor
            valor_denominador = total_general
            if es_divergente:
                if not porcentaje_divergente:
                    valor_numerador = suma_absoluta_por_barra.loc[entidad]
                    valor_denominador = total_general_absoluto
                else: # porcentaje_divergente es True
                    valor_numerador = suma_positivos_por_barra.loc[entidad]
                    valor_denominador = total_general_positivos
            
            porcentaje = round((valor_numerador / valor_denominador) * 100, 1) if valor_denominador != 0 else 0
            etiqueta_actual = entidades_formateadas[pos]
            resaltar = resaltar_etiquetas and etiqueta_actual in resaltar_etiquetas
            
            if resaltar:
                texto_capsula = f"{espacio*1}{etiqueta_actual}   {porcentaje}%{espacio*1}"
                bbox_capsula = dict(facecolor="#a3173e", edgecolor="none", boxstyle="round,pad=0.15,rounding_size=0.8")
                ax.text(pos, -x_max*0.02, texto_capsula, ha='center', va='top', rotation=90,
                        color="white", bbox=bbox_capsula,
                        fontdict={'family': font_config['family'], 'size': font_config['porcentaje_total']['size'], 'weight': font_config['porcentaje_total']['weight']})
            else:
                ax.text(pos, 0, f"{espacio*1}{porcentaje}%{espacio*1}", ha='right', va='top', rotation=90,
                        color=font_config['porcentaje_total']['color'],
                        fontdict={'family': font_config['family'], 'size': font_config['porcentaje_total']['size'], 'weight': font_config['porcentaje_total']['weight']})

        if porcentaje_total:
            valor_numerador = total_valor
            valor_denominador = total_general
            if es_divergente:
                if not porcentaje_divergente:
                    valor_numerador = suma_absoluta_por_barra.loc[entidad]
                    valor_denominador = total_general_absoluto
                else: # porcentaje_divergente es True
                    valor_numerador = suma_positivos_por_barra.loc[entidad]
                    valor_denominador = total_general_positivos

            porcentaje = round((valor_numerador / valor_denominador) * 100, 1) if valor_denominador != 0 else 0
            
            desplazamiento_y = 0
            if valor_total:
                desplazamiento_y = x_max * (0.15 if not quitar_capsula else 0.08)
            else:
                desplazamiento_y = x_max * 0.03
            
            base_pos_y = bottom_pos if es_divergente else total_valor
            desplazamiento_final = base_pos_y + desplazamiento_y + (x_max * separar_por_total)

            ax.text(pos, desplazamiento_final, f"{porcentaje}%", ha='center', va='bottom',
                    color=font_config['porcentaje_total']['color'],
                    fontdict={'family': font_config['family'], 'size': font_config['porcentaje_total']['size'], 'weight': font_config['porcentaje_total']['weight']})

    if porcentaje_total_inicio and resaltar_etiquetas:
        entidades_formateadas = ["" if e in resaltar_etiquetas else e for e in entidades_formateadas]

    ax.set_xticks(posiciones)
    rotation_val = 90 if orientacion_etiqueta_x != 'horizontal' else 0
    ha_val = 'right' if orientacion_etiqueta_x != 'horizontal' else 'center'
    ax.set_xticklabels(entidades_formateadas, fontsize=font_config['variable_x']['size'], fontweight=font_config['variable_x']['weight'], fontfamily=font_config['family'], rotation=rotation_val, ha=ha_val)
    
    right_x_limit = len(entidades) - 0.5 + (0.8 if hay_annotations_externas else 0)
    ax.set_xlim(-0.5, right_x_limit)
    
    if y_limits:
        ax.set_ylim(y_limits)
    else:
        ax.set_ylim(-x_max if es_divergente else 0, x_max)
        
    ax.yaxis.set_major_locator(mticker.MaxNLocator(nbins='auto', steps=[1, 2, 5, 10]))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{int(abs(x)) if ejeY_negativo_a_positivo else int(x):,}"))
    plt.setp(ax.get_yticklabels(), **font_config['variable_y'])
    
    ax.grid(visible=grillas, axis='y', color='#B9B9B9', linewidth=0.75, linestyle='-')
    if porcentaje_total_inicio:
        ax.tick_params(axis='x', pad=espacio_inicio)
        
    if nombre_eje_x:
        ax.set_xlabel(nombre_eje_x, labelpad=18, **font_config['nombre_eje_x'])
    if nombre_eje_y:
        ax.set_ylabel(nombre_eje_y, labelpad=18, **font_config['nombre_eje_y'])

    for label, entidad in zip(ax.get_xticklabels(), entidades_formateadas):
        if str(entidad) == "Previo":
            label.set_rotation(90)
            label.set_ha('center')
        elif str(entidad) == "...":
            label.set_rotation(0)
            label.set_ha('center')
            
     # Configuración de la leyenda.
    if leyenda:
        handles, labels = ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        
        all_labels = list(categorias)
        final_handles = [by_label.get(lbl, Patch(color=colores_asignados[i % len(colores_asignados)])) for i, lbl in enumerate(all_labels)]
        
        loc_leyenda, bbox_leyenda = ('upper center', (0.5, -0.15 - aumenta_sep_leyenda)) if pos_leyenda == 'abajo' else ('upper center', (0.5, 1.08 + aumenta_sep_leyenda))

        num_cols_leyenda = ncol_leyenda if ncol_leyenda is not None else len(all_labels)

        ax.legend(final_handles, all_labels, title=leyenda if isinstance(leyenda, str) else None,
                  fontsize=font_config['leyenda']['size'], title_fontsize=font_config['leyenda']['size'],
                  loc=loc_leyenda, bbox_to_anchor=bbox_leyenda, frameon=False,
                  ncol=num_cols_leyenda, handlelength=1, handleheight=1)
        
    # Limpieza de los bordes del gráfico.
    ax.spines[['top', 'right', 'left']].set_visible(False)
    ax.spines['bottom'].set_visible(True)

    # Línea en cero para gráficos divergentes.
    if es_divergente and not graf_resp_porce:
        ax.axhline(0, color='black', linewidth=1)

    # --- 9. GUARDADO Y VISUALIZACIÓN ---
    # Creación del directorio de salida si no existe.
    os.makedirs(output_dir, exist_ok=True)
    plt.tight_layout()
    
    # Guardado de la gráfica en formato SVG.
    base_path = f"{output_dir}/{nombre}"
    original_svg_path = f"{base_path}.svg"
    
    plt.savefig(original_svg_path, format='svg', bbox_inches='tight', dpi=300, transparent=True)
    
    # Aplicar flujo semántico si está habilitado
    if usar_flujo_svg:
        try:
            from svg_cleanup.flujo_exportacion import exportar_grafica
            print(f"🔄 Aplicando flujo semántico a {nombre}...")
            archivo_final = exportar_grafica(original_svg_path, nombre, output_dir)
            if archivo_final:
                print(f"Archivo optimizado para Figma: {archivo_final}")
                # Eliminar el archivo SVG original después de la optimización
                if os.path.exists(original_svg_path):
                    os.remove(original_svg_path)
            else:
                print("Error en flujo semántico, manteniendo archivo original")
        except ImportError:
            print("Módulo de optimización semántica no disponible")
            # Aplicar optimización completa
            try:
                archivo_optimizado = aplicar_flujo_optimizado(original_svg_path, nombre, output_dir)
                if archivo_optimizado and archivo_optimizado != original_svg_path:
                    os.remove(original_svg_path)
                    print(f"✓ Archivo optimizado: {archivo_optimizado}")
            except Exception as e:
                print(f"Error al optimizar SVG: {e}")
        except Exception as e:
            print(f"Error en flujo semántico: {e}")
            # Aplicar optimización completa como respaldo
            try:
                archivo_optimizado = aplicar_flujo_optimizado(original_svg_path, nombre, output_dir)
                if archivo_optimizado and archivo_optimizado != original_svg_path:
                    os.remove(original_svg_path)
                    print(f"✓ Archivo optimizado: {archivo_optimizado}")
            except Exception as e:
                print(f"Error al optimizar SVG: {e}")
    else:
        # Optimización completa del archivo SVG
        try:
            archivo_optimizado = aplicar_flujo_optimizado(original_svg_path, nombre, output_dir)
            if archivo_optimizado and archivo_optimizado != original_svg_path:
                os.remove(original_svg_path)
                print(f"✓ Archivo optimizado: {archivo_optimizado}")
        except Exception as e:
            print(f"Error al optimizar SVG: {e}")

    # Muestra la gráfica en el entorno de ejecución (ej. Jupyter Notebook).
    plt.show()