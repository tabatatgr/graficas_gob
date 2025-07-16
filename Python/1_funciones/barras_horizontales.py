# EXPORTAR: gráfica de barras horizontales
        
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

from funciones import limpiar_svg_con_scour, formato_fechas, get_text_color_for_bg, unir_barras 


def barras_horizontales(
    # --- DATOS Y ESTRUCTURA ---
    df,                         # DataFrame de entrada
    agregar_datos=None,         # Datos extra para agregar como barras
    asignar_etiquetas=None,     # Columna para etiquetas personalizadas
    ordenar_por='valor',        # Ordenar por 'valor' o 'etiqueta'
    orden='descendente',        # Orden ascendente o descendente
    union_sup=0,                # Unir barras superiores
    union_inf=0,                # Unir barras inferiores
    columnas_lineas=None,       # Lista de nombres de columnas que serán graficadas como líneas verticales
    paleta_colores_lineas=None, # Lista de colores para las líneas
    capsu_fin_lineas=False,     # Mostrar cápsula con el valor al final de cada línea

    # --- GRÁFICA GENERAL ---
    nombre="barras_horizontales", # Nombre base para archivos de salida
    tipo_letra='Montserrat',    # Tipo de letra para todo el texto en la gráfica
    ancho_fig=None,             # Ancho de la figura 
    alto_fig=None,              # Alto de la figura
    grillas=True,               # Mostrar grillas verticales

    # --- BARRAS ---
    ancho_barra=0.85,            # Ancho de cada barra
    tam_letra_valor_barra=20,   # Tamaño de letra para valores dentro de las barras
    weight_valor_barra='bold',  # Grosor de letra para valores dentro de las barras
    color_valor_barra=None,     # Color del texto de valor en barra
    tam_letra_porce_barra=15,   # Tamaño de letra para porcentajes dentro de las barras
    weight_porce_barra='bold',  # Grosor de letra para porcentajes dentro de las barras
    color_porce_barra=None,     # Color de letra para porcentajes dentro de las barras
    paleta_colores=None,        # Lista de colores para las barras
    area_min=0,                 # Área mínima para mostrar texto en barra
    ancho_min=0,                # Ancho mínimo para mostrar texto dentro de barra
    valor_barra=True,           # Mostrar valor numérico en la barra
    porce_barra=True,           # Mostrar porcentaje en la barra
    porce_al_lado=True,         # Mostrar porcentaje al lado del valor dentro de la barra
    porce_diver=False,          # Porcentaje respecto a suma absoluta (divergente)
    alinea_texto_barra=False,   # Alinear el texto dentro de la barra horizontalmente

    # --- CÁPSULAS ---
    valor_capsu=True,           # Mostrar cápsula de total al final de la barra
    tam_letra_valor_capsu=20,   # Tamaño de letra para valores dentro de las cápsulas
    weight_valor_capsu='bold',  # Grosor de letra para valores dentro de las cápsulas
    color_valor_capsu='#000000',# Color de letra para valores dentro de las cápsulas
    color_borde_capsu='#002F2A',# Color del borde de la cápsula
    weight_borde_capsu=1.5,     # Grosor del borde de la cápsula
    quitar_capsu=False,         # Quitar la cápsula de total
    capsu_cero=True,            # Mostrar cápsula aunque el valor sea cero
    ajusta_pos_capsu=0.02,      # Ajusta la posición de la cápsula respecto a la barra
    alinea_capsu=False,         # Alinear la cápsula horizontalmente

    # --- PORCENTAJES TOTALES ---
    porce_total=True,           # Mostrar porcentaje respecto al total general
    porce_total_inicio=False,   # Mostrar porcentaje respecto al total general al inicio
    separar_por_total=-0.09,    # Separación extra para porcentaje total
    tam_porce_total=25,         # Tamaño de letra para porcentaje total
    weight_porce_total='semibold', # Grosor de letra para porcentaje total
    color_porce_total='#4C6A67',   # Color de letra para porcentaje total

    # --- LEYENDA ---
    leyenda=None,               # Título de la leyenda
    pos_leyenda='arriba',       # Posición de la leyenda ('arriba' o 'abajo')
    aumenta_sep_leyenda=0.0,    # Espacio extra para la leyenda
    ncol_leyenda=None,          # Número de columnas en la leyenda
    tam_letra_leyenda=24,       # Tamaño de letra para la leyenda
    weight_letra_leyenda='medium', # Grosor de letra para la leyenda
    color_letra_leyenda='#767676', # Color de letra para la leyenda

    # --- EJE Y (ETIQUETAS) ---
    tam_letra_ejeY=35,          # Tamaño de letra para etiquetas eje Y
    weight_letra_ejeY='medium', # Grosor de letra para etiquetas eje Y
    color_letra_ejeY="#000000", # Color de letra para etiquetas eje Y
    espacio_inicio=0,           # Espacio extra al inicio del eje Y
    nombre_eje_y=None,          # Nombre del eje Y
    tam_letra_nombre_eje_y=25,  # Tamaño de letra para nombre del eje Y
    weight_letra_nombre_eje_y='medium', # Grosor de letra para nombre del eje Y
    color_letra_nombre_eje_y='#000000', # Color de letra para nombre del eje Y
    sustituir_etiquetas=None,   # Lista para sustituir etiquetas del eje Y
    orientacion_etiqu_ejeY=None,# Orientación de etiquetas eje Y ('vertical' o None)
    aumenta_sep_eje_y=0.0,      # Aumenta separación en eje Y
    resaltar_etiquetas=None,    # Lista de etiquetas a resaltar
    color_resalt_etique="#a3173e", # Color para el resaltado de etiquetas
    color_borde_resalt='none',  # Color del borde de resaltado de etiquetas
    ejeY_der=False,             # Colocar el eje Y a la derecha

    # --- EJE X (VALORES) ---
    tam_letra_ejeX=30,          # Tamaño de letra para etiquetas eje X
    weight_letra_ejeX='medium', # Grosor de letra para etiquetas eje X
    color_letra_ejeX="#000000", # Color de letra para etiquetas eje X
    nombre_eje_x=None,          # Nombre del eje X
    tam_letra_nombre_eje_x=22,  # Tamaño de letra para nombre del eje X
    weight_letra_nombre_eje_x='medium', # Grosor de letra para nombre del eje X
    color_letra_nombre_eje_x='#000000', # Color de letra para nombre del eje X
    x_limits=None,              # Límites del eje X
    ejeX_positivo=False,        # Eje X solo muestra valores positivos
    div_ejeX=False,             # División personalizada del eje X
    graf_resp_porce=False,      # Graficar con respecto al porcentaje en el eje X
):
    """
    Genera un gráfico de barras horizontales apiladas, personalizable y con múltiples opciones de formato.

    Esta función toma un DataFrame de pandas y crea un gráfico de barras horizontales. Permite una amplia
    personalización que incluye el orden de las barras, colores, etiquetas, leyendas, y la capacidad
    de agregar datos adicionales o resaltar barras específicas. Está diseñada para ser flexible y
    cubrir una variedad de casos de uso para la visualización de datos.
    """
    # --- 1. CONFIGURACIÓN INICIAL ---
    hay_annotations_externas = False
    espacio = "\u00A0"

    font_config = {
        'family': tipo_letra,
        'variable_y': {'size': tam_letra_ejeY, 'weight': weight_letra_ejeY, 'color': color_letra_ejeY},
        'variable_x': {'size': tam_letra_ejeX, 'weight': weight_letra_ejeX, 'color': color_letra_ejeX},
        'nombre_eje_y': {'size': tam_letra_nombre_eje_y, 'weight': weight_letra_nombre_eje_y, 'color': color_letra_nombre_eje_y},
        'nombre_eje_x': {'size': tam_letra_nombre_eje_x, 'weight': weight_letra_nombre_eje_x, 'color': color_letra_nombre_eje_x},
        'valor_capsula': {'size': tam_letra_valor_capsu, 'weight': weight_valor_capsu, 'color': color_valor_capsu},
        'valor_porcentaje_barra': {'size': tam_letra_valor_barra, 'weight': weight_valor_barra, 'color': color_valor_barra},
        'valor_porcentaje_barra_porcentaje': {'size': tam_letra_porce_barra, 'weight': weight_porce_barra, 'color': color_porce_barra},
        'porcentaje_total': {'size': tam_porce_total, 'weight': weight_porce_total, 'color': color_porce_total},
        'leyenda': {'size': tam_letra_leyenda, 'weight': weight_letra_leyenda, 'color': color_letra_leyenda}
    }

    plt.rcParams['svg.fonttype'] = 'none'
    font_dirs = [Path("../0_fonts")]
    font_files = font_manager.findSystemFonts(fontpaths=font_dirs)
    for font_file in font_files:
        font_manager.fontManager.addfont(font_file)

    colores_asignados = paleta_colores or ["#10302C", "#4C6A67", "#8FA8A6", "#A3C9A8"]

    # --- 2. PREPARACIÓN DE DATOS ---
    if not isinstance(df, pd.DataFrame):
        raise ValueError("El argumento df debe ser un DataFrame de pandas.")
    
    df = df.copy()
    categorias_y = df.columns[0]
    if pd.api.types.is_integer_dtype(df[categorias_y]) and df[categorias_y].between(1900, 2100).all():
        df[categorias_y] = pd.to_datetime(df[categorias_y], format='%Y')
    df = df.set_index(categorias_y)

    df, etiqueta_union_sup = unir_barras(df, union_sup, 'izquierda') # 'izquierda' en vertical es 'arriba' en horizontal
    df, etiqueta_union_inf = unir_barras(df, union_inf, 'derecha')   # 'derecha' en vertical es 'abajo' en horizontal

    etiquetas_personalizadas = {}
    textos_barra_personalizados = {}
    colores_fondo_personalizados = {}
    colores_borde_personalizados = {}
    estilos_borde_personalizados = {}
    grosores_borde_personalizados = {}
    colores_texto_personalizados = {}
    datos_para_separadores = []

    if agregar_datos:
        filas_a_agregar = []
        for item in agregar_datos:
            etiqueta, texto_barra, opciones_extra = None, None, {}
            if len(item) == 2: categoria, valor = item
            elif len(item) == 3: categoria, etiqueta, valor = item
            elif len(item) == 4: categoria, etiqueta, valor, texto_barra = item
            elif len(item) == 5: categoria, etiqueta, valor, texto_barra, opciones_extra = item

            if etiqueta: etiquetas_personalizadas[categoria] = etiqueta
            if texto_barra: textos_barra_personalizados[categoria] = texto_barra
            if isinstance(opciones_extra, dict):
                if 'colores_fondo' in opciones_extra: colores_fondo_personalizados[categoria] = opciones_extra['colores_fondo']
                if 'colores_borde' in opciones_extra: colores_borde_personalizados[categoria] = opciones_extra['colores_borde']
                if 'estilos_borde' in opciones_extra: estilos_borde_personalizados[categoria] = opciones_extra['estilos_borde']
                if 'grosores_borde' in opciones_extra: grosores_borde_personalizados[categoria] = opciones_extra['grosores_borde']
                if 'colores_texto' in opciones_extra: colores_texto_personalizados[categoria] = opciones_extra['colores_texto']
                if 'separador_derecha' in opciones_extra: datos_para_separadores.append({'posicion': 'despues', 'referencia': categoria, 'texto': opciones_extra['separador_derecha']})
                if 'separador_izquierda' in opciones_extra: datos_para_separadores.append({'posicion': 'antes', 'referencia': categoria, 'texto': opciones_extra['separador_izquierda']})

            fila = pd.Series(dict(zip(df.columns, valor)) if isinstance(valor, (list, tuple, np.ndarray)) else {col: valor if i == 0 else 0 for i, col in enumerate(df.columns)}, name=categoria)
            filas_a_agregar.append(fila)

        if filas_a_agregar:
            df_agregado = pd.DataFrame(filas_a_agregar)
            df = pd.concat([df, df_agregado])

    etiquetas_finales = None
    if asignar_etiquetas and asignar_etiquetas in df.columns:
        etiquetas_finales = df[asignar_etiquetas].copy()
        df = df.drop(columns=[asignar_etiquetas])

    categorias = df.columns

    # --- 3. ORDENAMIENTO DE DATOS ---
    if ordenar_por == 'valor':
        sort_index = df.sum(axis=1).sort_values(ascending=(orden != 'descendente')).index
    elif ordenar_por == 'etiqueta':
        indices = list(df.index)
        sup = [etiqueta_union_sup] if etiqueta_union_sup else []
        inf = [etiqueta_union_inf] if etiqueta_union_inf else []
        centro = [i for i in indices if i not in sup + inf]
        
        tipos = set(type(idx) for idx in centro)
        reverse_sort = (orden == 'descendente')
        centro_ordenado = sorted(centro, key=lambda x: str(x), reverse=reverse_sort) if len(tipos) > 1 else sorted(centro, reverse=reverse_sort)
        
        sort_index = sup + centro_ordenado + inf
    else:
        sort_index = df.index

    df = df.loc[sort_index]
    
    if datos_para_separadores:
        datos_para_separadores.sort(key=lambda x: x['posicion'] == 'antes', reverse=True)
        df_list = list(df.iterrows())
        current_indices = [item[0] for item in df_list]

        for sep_info in datos_para_separadores:
            try:
                idx_pos = current_indices.index(sep_info['referencia'])
                idx_separador = f"__espaciador__{sep_info['referencia']}_{sep_info['posicion']}_{np.random.randint(1000)}"
                fila_separador = pd.Series({col: 0 for col in df.columns}, name=idx_separador)
                etiquetas_personalizadas[idx_separador] = sep_info['texto']
                insert_at = idx_pos if sep_info['posicion'] == 'antes' else idx_pos + 1
                df_list.insert(insert_at, (idx_separador, fila_separador))
                current_indices.insert(insert_at, idx_separador)
            except ValueError:
                print(f"Advertencia: No se encontró la clave '{sep_info['referencia']}' para añadir un separador.")
        
        df = pd.DataFrame.from_dict(dict(df_list), orient='index')
        df.columns = categorias

    # --- 4. CÁLCULOS PARA LA GRÁFICA ---
    if columnas_lineas is None: columnas_lineas = []
    
    columnas_barras = [col for col in df.columns if col not in columnas_lineas]
    
    suma_total = df[columnas_barras].sum(axis=1) if columnas_barras else pd.Series(0, index=df.index)
    total_general = suma_total.sum()

    df_plot = df.copy()
    if graf_resp_porce:
        suma_total_no_cero = suma_total.replace(0, np.nan)
        for col in columnas_barras:
            df_plot[col] = df[col].div(suma_total_no_cero, axis=0).multiply(100).fillna(0)
    
    es_divergente = (any(df[columnas_barras].min() < 0) if columnas_barras else False) or \
                   (any(df[columnas_lineas].min() < 0) if columnas_lineas else False)
    
    suma_positivos_por_barra, suma_negativos_por_barra, suma_absoluta_por_barra, total_general_absoluto, total_general_positivos = None, None, None, None, None
    if es_divergente:
        suma_negativos_por_barra = df[columnas_barras][df[columnas_barras] < 0].sum(axis=1)
        if porce_diver:
            suma_positivos_por_barra = df[columnas_barras][df[columnas_barras] > 0].sum(axis=1)
            total_general_positivos = suma_positivos_por_barra.sum()
        else:
            suma_absoluta_por_barra = df[columnas_barras].abs().sum(axis=1)
            total_general_absoluto = suma_absoluta_por_barra.sum()

    x_max_pos = df[df > 0].sum(axis=1).max()
    x_max_neg = df[df < 0].sum(axis=1).min()
    min_lineas = df[columnas_lineas].min().min() if columnas_lineas else 0
    x_max = max(x_max_pos, abs(x_max_neg), abs(min_lineas) if min_lineas < 0 else 0) * 1.15
    if pd.isna(x_max): x_max = suma_total.max() * 1.15
    if graf_resp_porce: x_max = 100 * 1.15

    # --- 5. FORMATEO DE ETIQUETAS DEL EJE Y ---
    entidades = df.index.values
    es_fecha = any(isinstance(idx, (pd.Timestamp, np.datetime64)) for idx in df.index if idx not in [etiqueta_union_sup, etiqueta_union_inf])
    if es_fecha:
        fechas_a_formatear = [idx for idx in df.index if isinstance(idx, (pd.Timestamp, np.datetime64))]
        mapa_fechas = dict(zip(fechas_a_formatear, formato_fechas(fechas_a_formatear)))
        entidades_formateadas = [mapa_fechas.get(idx, str(idx)) for idx in df.index]
    else:
        entidades_formateadas = [str(idx) for idx in df.index]

    if sustituir_etiquetas:
        if len(sustituir_etiquetas) != len(entidades_formateadas):
            raise ValueError("La longitud de 'sustituir_etiquetas' debe coincidir con el número de barras.")
        entidades_formateadas = list(sustituir_etiquetas)

    for i, entidad in enumerate(df.index):
        if entidad in etiquetas_personalizadas and etiquetas_personalizadas[entidad]:
            entidades_formateadas[i] = etiquetas_personalizadas[entidad]

    for i, entidad in enumerate(entidades_formateadas):
        if "__espaciador__" in str(df.index[i]):
            entidades_formateadas[i] = etiquetas_personalizadas.get(df.index[i], "...")

    # --- 6. CREACIÓN DE LA FIGURA Y EJES ---
    posiciones = np.arange(len(entidades))
    
    longitudes = [len(str(e)) for e in entidades_formateadas]
    moda_etiqueta_len = mode(longitudes) if longitudes else 10
    extra_height = moda_etiqueta_len * 0.1
    base_height = max(8, len(entidades) * 0.5)
    fig_height = alto_fig if alto_fig is not None else base_height
    fig_width = ancho_fig if ancho_fig is not None else fig_height * 2
    fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=300)

    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)

    # --- 7. DIBUJO DE BARRAS Y TEXTOS ---
    line_handles, line_labels = [], []
    
    for pos, entidad, total_valor in zip(posiciones, entidades, suma_total):
        left_pos, left_neg = 0, 0
        
        for i, col in enumerate(columnas_barras):
            current_val = df_plot[col].iloc[pos]
            if current_val == 0: continue

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
            
            text_color_valor = custom_text_color or color_valor_barra or get_text_color_for_bg(color)
            text_color_porcentaje = custom_text_color or color_porce_barra or get_text_color_for_bg(color)
            
            bar_left = left_pos if current_val > 0 else left_neg
            ax.barh(pos, current_val, height=ancho_barra, left=bar_left, color=color, edgecolor=edge_color, linestyle=line_style, linewidth=line_width, zorder=2, label=col)
            
            if current_val > 0: left_pos += current_val
            else: left_neg += current_val

            ancho_barra_val = abs(current_val)
            if (porce_barra or valor_barra or (entidad in textos_barra_personalizados)) and ancho_barra_val >= ancho_min:
                if es_divergente:
                    if porce_diver:
                        base_porcentaje = suma_positivos_por_barra.loc[entidad] if current_val > 0 else suma_negativos_por_barra.loc[entidad]
                    else:
                        base_porcentaje = suma_absoluta_por_barra.loc[entidad]
                else:
                    base_porcentaje = total_valor
                porcentaje_valor = (df.iloc[pos, df.columns.get_loc(col)] / base_porcentaje) * 100 if base_porcentaje != 0 else 0

                text_pos_x = bar_left + current_val / 2
                
                texto_final, texto_a_dibujar = "", True
                rotacion_texto_barra = 0 if alinea_texto_barra else 270
                va_texto_barra = 'center'
                ha_texto_barra_valor = 'right' if porce_al_lado else 'center'
                ha_texto_barra_porce = 'left' if porce_al_lado else 'center'
                ha_texto_barra_unificado = 'center'

                if entidad in textos_barra_personalizados:
                    textos_barra = textos_barra_personalizados[entidad]
                    if i < len(textos_barra) and textos_barra[i] is not None: texto_final = textos_barra[i]
                elif valor_barra and porce_barra:
                    texto_valor = f"{abs(df.iloc[pos, df.columns.get_loc(col)]):,.0f}"
                    texto_porcentaje = f"({abs(porcentaje_valor):.1f}%)" if not porce_al_lado else f"{abs(porcentaje_valor):.1f}%"
                    
                    if porce_al_lado:
                        ax.text(text_pos_x, pos, texto_valor, va=va_texto_barra, ha=ha_texto_barra_valor, rotation=rotacion_texto_barra, fontsize=font_config['valor_porcentaje_barra']['size'], fontfamily=font_config['family'], fontweight=font_config['valor_porcentaje_barra']['weight'], color=text_color_valor, linespacing=1.5)
                        ax.text(text_pos_x, pos, texto_porcentaje, va=va_texto_barra, ha=ha_texto_barra_porce, rotation=rotacion_texto_barra, fontsize=font_config['valor_porcentaje_barra_porcentaje']['size'], fontfamily=font_config['family'], fontweight=font_config['valor_porcentaje_barra_porcentaje']['weight'], color=text_color_porcentaje, linespacing=1.5)
                        texto_a_dibujar = False
                    else:
                        texto_final = f"{texto_valor}\n{texto_porcentaje}"
                elif valor_barra: texto_final = f"{abs(df.iloc[pos, df.columns.get_loc(col)]):,.0f}"
                elif porce_barra: texto_final = f"{abs(porcentaje_valor):.1f}%"

                if texto_a_dibujar and texto_final:
                    font_size_a_usar = font_config['valor_porcentaje_barra_porcentaje']['size'] if not valor_barra and porce_barra else font_config['valor_porcentaje_barra']['size']
                    color_a_usar = text_color_porcentaje if not valor_barra and porce_barra else text_color_valor
                    ax.text(text_pos_x, pos, texto_final, va=va_texto_barra, ha=ha_texto_barra_unificado, rotation=rotacion_texto_barra, fontsize=font_size_a_usar, fontfamily=font_config['family'], fontweight=font_config['valor_porcentaje_barra']['weight'], color=color_a_usar, linespacing=1.2)

        if valor_capsu and "__espaciador__" not in str(entidad):
            valor_a_mostrar = total_valor
            if es_divergente:
                if not porce_diver: valor_a_mostrar = suma_absoluta_por_barra.loc[entidad]
                else: valor_a_mostrar = suma_positivos_por_barra.loc[entidad]

            if capsu_cero or valor_a_mostrar != 0:
                texto_a_mostrar = f"{int(valor_a_mostrar):,}"
                if etiquetas_finales is not None and not pd.isna(etiquetas_finales.iloc[pos]): texto_a_mostrar = str(etiquetas_finales.iloc[pos])
                
                texto_capsula = f"{espacio*2}{texto_a_mostrar}{espacio*2}"
                base_pos_x = left_pos if es_divergente else (100 if graf_resp_porce else total_valor)
                text_x_pos = base_pos_x + x_max * ajusta_pos_capsu
                
                rotacion_capsula = 0 if alinea_capsu else 270
                ha_capsula, va_capsula = 'left', 'center'
                pos_x_capsula, pos_y_capsula = text_x_pos, pos
                color_texto_capsula = color_valor_capsu or get_text_color_for_bg('#FFFFFF')

                bbox_dict = dict(boxstyle="round,pad=0.15,rounding_size=0.8", facecolor=(1, 1, 1, 0), edgecolor=color_borde_capsu, linewidth=weight_borde_capsu)
                font_dict = {'family': font_config['family'], 'size': font_config['valor_capsula']['size'], 'weight': font_config['valor_capsula']['weight'], 'color': color_texto_capsula}
                
                if not quitar_capsu:
                    ax.text(pos_x_capsula, pos_y_capsula, texto_capsula, bbox=bbox_dict, ha=ha_capsula, va=va_capsula, rotation=rotacion_capsula, fontdict=font_dict)
                else:
                    ax.text(pos_x_capsula, pos_y_capsula, texto_a_mostrar, ha=ha_capsula, va=va_capsula, rotation=rotacion_capsula, fontdict=font_dict)

        if es_divergente and valor_capsu and left_neg < 0:
            valor_negativo_total = suma_negativos_por_barra.loc[entidad]
            if capsu_cero or valor_negativo_total != 0:
                texto_a_mostrar_neg = f"{int(abs(valor_negativo_total)):,}"
                texto_capsula_neg = f"{espacio*2}{texto_a_mostrar_neg}{espacio*2}"
                text_x_pos_neg = left_neg - x_max * ajusta_pos_capsu
                color_texto_capsula_neg = color_valor_capsu or get_text_color_for_bg('#FFFFFF')
                bbox_dict = dict(boxstyle="round,pad=0.15,rounding_size=0.8", facecolor=(1, 1, 1, 0), edgecolor=color_borde_capsu, linewidth=weight_borde_capsu)
                font_dict = {'family': font_config['family'], 'size': font_config['valor_capsula']['size'], 'weight': font_config['valor_capsula']['weight'], 'color': color_texto_capsula_neg}

                if not quitar_capsu:
                    ax.text(text_x_pos_neg, pos, texto_capsula_neg, bbox=bbox_dict, ha='right', va='center', fontdict=font_dict)
                else:
                    ax.text(text_x_pos_neg, pos, texto_a_mostrar_neg, ha='right', va='center', fontdict=font_dict)

        if porce_total_inicio:
            valor_numerador = total_valor
            valor_denominador = total_general
            if es_divergente:
                if not porce_diver: valor_numerador, valor_denominador = suma_absoluta_por_barra.loc[entidad], total_general_absoluto
                else: valor_numerador, valor_denominador = suma_positivos_por_barra.loc[entidad], total_general_positivos
            
            porcentaje = round((valor_numerador / valor_denominador) * 100, 1) if valor_denominador != 0 else 0
            etiqueta_actual = entidades_formateadas[pos]

            if resaltar_etiquetas and etiqueta_actual in resaltar_etiquetas:
                texto_a_mostrar = f"{espacio*1}{etiqueta_actual}   {porcentaje}%{espacio*1}"
                color_texto_resaltado = get_text_color_for_bg(color_resalt_etique)
                bbox_capsula = dict(facecolor=color_resalt_etique, edgecolor=color_borde_resalt, boxstyle="round,pad=0.15,rounding_size=0.8")
                pos_x_resaltado = x_max * 1.02 if ejeY_der else -x_max * 0.02
                ha_resaltado = 'left' if ejeY_der else 'right'
                ax.text(pos_x_resaltado, pos, texto_a_mostrar, ha=ha_resaltado, va='center', bbox=bbox_capsula, fontdict={'family': font_config['family'], 'size': font_config['porcentaje_total']['size'], 'weight': font_config['porcentaje_total']['weight'], 'color': color_texto_resaltado})
            else:
                texto_a_mostrar = f"{espacio*1}{porcentaje}%{espacio*1}"
                ax.text(0, pos, texto_a_mostrar, ha='left', va='bottom', color=font_config['porcentaje_total']['color'], fontdict={'family': font_config['family'], 'size': font_config['porcentaje_total']['size'], 'weight': font_config['porcentaje_total']['weight']})

        if porce_total:
            valor_numerador = total_valor
            valor_denominador = total_general
            if es_divergente:
                if not porce_diver: valor_numerador, valor_denominador = suma_absoluta_por_barra.loc[entidad], total_general_absoluto
                else: valor_numerador, valor_denominador = suma_positivos_por_barra.loc[entidad], total_general_positivos

            porcentaje = round((valor_numerador / valor_denominador) * 100, 1) if valor_denominador != 0 else 0
            desplazamiento_x = x_max * (0.15 if valor_capsu and not quitar_capsu else 0.08)
            base_pos_x = left_pos if es_divergente else (100 if graf_resp_porce else total_valor)
            desplazamiento_final = base_pos_x + desplazamiento_x + (x_max * separar_por_total)
            ax.text(desplazamiento_final, pos, f"{porcentaje}%", ha='center', va='center', color=font_config['porcentaje_total']['color'], fontdict={'family': font_config['family'], 'size': font_config['porcentaje_total']['size'], 'weight': font_config['porcentaje_total']['weight']})

    for i, col in enumerate(columnas_lineas):
        if paleta_colores_lineas and i < len(paleta_colores_lineas): line_color = paleta_colores_lineas[i]
        else: line_color = colores_asignados[(i + len(columnas_barras)) % len(colores_asignados)]
        valores_linea = df_plot[col].values
        line, = ax.plot(valores_linea, posiciones, marker='o', markersize=6, linewidth=2, color=line_color, label=col, zorder=5)
        line_handles.append(line)
        line_labels.append(col)
        
        if capsu_fin_lineas and len(valores_linea) > 0:
            ultimo_pos, ultimo_valor = posiciones[-1], valores_linea[-1]
            if capsu_cero or ultimo_valor != 0:
                texto_a_mostrar = f"{int(abs(ultimo_valor)):,}"
                texto_capsula = f"{espacio*2}{texto_a_mostrar}{espacio*2}"
                pos_x_capsula, pos_y_capsula = ultimo_valor, ultimo_pos
                color_texto_capsula = color_valor_capsu or get_text_color_for_bg('#FFFFFF')
                bbox_dict = dict(boxstyle="round,pad=0.15,rounding_size=0.8", facecolor=(1, 1, 1, 0), edgecolor=color_borde_capsu, linewidth=weight_borde_capsu)
                font_dict = {'family': font_config['family'], 'size': font_config['valor_capsula']['size'], 'weight': font_config['valor_capsula']['weight'], 'color': color_texto_capsula}
                ha_val = 'left' if ultimo_valor >= 0 else 'right'
                if not quitar_capsu:
                    ax.text(pos_x_capsula, pos_y_capsula, texto_capsula, bbox=bbox_dict, ha=ha_val, va='center', fontdict=font_dict)
                else:
                    ax.text(pos_x_capsula, pos_y_capsula, texto_a_mostrar, ha=ha_val, va='center', fontdict=font_dict)

    # --- 8. AJUSTES FINALES DE LA GRÁFICA ---
    if (porce_total_inicio or resaltar_etiquetas) and resaltar_etiquetas:
        entidades_formateadas = ["" if e in resaltar_etiquetas else e for e in entidades_formateadas]

    ax.set_yticks(posiciones)
    rotation_val = 90 if orientacion_etiqu_ejeY == 'vertical' else 0
    ha_val = 'center' if orientacion_etiqu_ejeY == 'vertical' else ('left' if ejeY_der else 'right')
    ax.set_yticklabels(entidades_formateadas, fontsize=font_config['variable_y']['size'], fontweight=font_config['variable_y']['weight'], fontfamily=font_config['family'], color=font_config['variable_y']['color'], rotation=rotation_val, ha=ha_val)
    
    if resaltar_etiquetas and not porce_total_inicio:
        original_labels = [str(idx) for idx in df.index]
        if sustituir_etiquetas: original_labels = sustituir_etiquetas
        for pos, etiqueta_actual in enumerate(original_labels):
            if etiqueta_actual in resaltar_etiquetas:
                texto_capsula = f"{espacio*1}{etiqueta_actual}{espacio*1}"
                color_texto_resaltado = get_text_color_for_bg(color_resalt_etique)
                bbox_capsula = dict(facecolor=color_resalt_etique, edgecolor=color_borde_resalt, boxstyle="round,pad=0.15,rounding_size=0.8")
                pos_x_resaltado = x_max * 1.02 if ejeY_der else -x_max * 0.02
                ha_resaltado = 'left' if ejeY_der else 'right'
                ax.text(pos_x_resaltado, pos, texto_capsula, ha=ha_resaltado, va='center', bbox=bbox_capsula, fontdict={'family': font_config['family'], 'size': font_config['porcentaje_total']['size'], 'weight': font_config['porcentaje_total']['weight'], 'color': color_texto_resaltado})

    bottom_y_limit = -0.5
    top_y_limit = len(entidades) - 0.5 + (0.8 if hay_annotations_externas else 0)
    ax.set_ylim(bottom_y_limit, top_y_limit)
    ax.invert_yaxis()
    
    if x_limits and not graf_resp_porce: ax.set_xlim(x_limits)
    else:
        x_min = (-x_max * (1 + aumenta_sep_eje_y)) if es_divergente and not graf_resp_porce else 0
        x_max_val = 100 if graf_resp_porce else x_max
        ax.set_xlim(x_min, x_max_val)
        
    if div_ejeX: ax.xaxis.set_major_locator(mticker.MultipleLocator(div_ejeX))
    else: ax.xaxis.set_major_locator(mticker.MaxNLocator(nbins='auto', steps=[1, 2, 5, 10]))
    
    if graf_resp_porce: ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{int(x)}%'))
    else: ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{int(abs(x)) if ejeX_positivo else int(x):,}"))
    
    plt.setp(ax.get_xticklabels(), fontsize=font_config['variable_x']['size'], fontweight=font_config['variable_x']['weight'], color=font_config['variable_x']['color'], fontfamily=font_config['family'])
    
    ax.grid(visible=grillas, axis='x', color='#B9B9B9', linewidth=0.75, linestyle='-')
    if porce_total_inicio: ax.tick_params(axis='y', pad=espacio_inicio)
        
    if nombre_eje_y: ax.set_ylabel(nombre_eje_y, labelpad=18, **font_config['nombre_eje_y'])
    if nombre_eje_x: ax.set_xlabel(nombre_eje_x, labelpad=18, **font_config['nombre_eje_x'])

    for label, entidad_formateada in zip(ax.get_yticklabels(), entidades_formateadas):
        try:
            mapa_formato_a_original = {ent_fmt: ent_orig for ent_fmt, ent_orig in zip(entidades_formateadas, df.index)}
            original_index = mapa_formato_a_original.get(entidad_formateada)
            if original_index and "__espaciador__" in str(original_index):
                label.set_rotation(0)
                label.set_ha('center')
        except (ValueError, IndexError, KeyError): pass

    if ejeY_der:
        ax.yaxis.tick_right()
        ax.yaxis.set_label_position("right")
        ax.invert_xaxis()

    if leyenda:
        handles, labels = ax.get_legend_handles_labels()
        by_label = {lbl: h for h, lbl in zip(handles, labels)}
        
        all_labels, final_handles = [], []
        for i, lbl in enumerate(columnas_barras):
            all_labels.append(lbl)
            final_handles.append(by_label.get(lbl, Patch(color=colores_asignados[i % len(colores_asignados)])))
        for i, lbl in enumerate(columnas_lineas):
            all_labels.append(lbl)
            if paleta_colores_lineas and i < len(paleta_colores_lineas): line_color = paleta_colores_lineas[i]
            else: line_color = colores_asignados[(i + len(columnas_barras)) % len(colores_asignados)]
            final_handles.append(by_label.get(lbl, plt.Line2D([0], [0], color=line_color, marker='o', markersize=6, linewidth=2)))
        
        loc_leyenda, bbox_leyenda = ('upper center', (0.5, -0.15 - aumenta_sep_leyenda)) if pos_leyenda == 'abajo' else ('upper center', (0.5, 1.08 + aumenta_sep_leyenda))
        num_cols_leyenda = ncol_leyenda if ncol_leyenda is not None else len(all_labels)
        ax.legend(final_handles, all_labels, title=leyenda if isinstance(leyenda, str) else None, fontsize=font_config['leyenda']['size'], title_fontsize=font_config['leyenda']['size'], loc=loc_leyenda, bbox_to_anchor=bbox_leyenda, frameon=False, ncol=num_cols_leyenda, handlelength=1, handleheight=1)
        
    ax.spines[['top', 'bottom']].set_visible(False)
    ax.spines['left'].set_visible(not ejeY_der)
    ax.spines['right'].set_visible(ejeY_der)

    if es_divergente and not graf_resp_porce: ax.axvline(0, color='black', linewidth=1)

    # --- 9. GUARDADO Y VISUALIZACIÓN ---
    os.makedirs("output", exist_ok=True)
    plt.tight_layout()
    
    base_path = f"output/{nombre}"
    original_svg_path = f"{base_path}.svg"
    scour_svg_path = f"{base_path}_scour.svg"
    plt.savefig(original_svg_path, format='svg', bbox_inches='tight', dpi=300, transparent=True)
    plt.savefig(f"{base_path}.png", format='png', bbox_inches='tight', dpi=300, transparent=True)

    try:
        limpiar_svg_con_scour(original_svg_path, scour_svg_path)
        os.remove(original_svg_path)
    except Exception as e:
        print(f"Error al optimizar o eliminar el SVG: {e}")

    plt.show()