# EXPORTAR: gráfica de barras verticales

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

def barras_verticales(
    # --- DATOS Y ESTRUCTURA ---
    df,                         # DataFrame de entrada
    agregar_datos=None,         # Datos extra para agregar como barras
    asignar_etiquetas=None,     # Columna para etiquetas personalizadas
    ordenar_por='valor',        # Ordenar por 'valor' o 'etiqueta'
    orden='descendente',        # Orden ascendente o descendente
    union_izq=0,                # Unir barras a la izquierda
    union_der=0,                # Unir barras a la derecha

    # --- GRÁFICA GENERAL ---
    nombre="barras_verticales", # Nombre base para archivos de salida
    tipo_letra='Montserrat',    # Tipo de letra para todo el texto en la gráfica
    ancho_fig=None,             # Ancho de la figura 
    alto_fig=None,              # Alto de la figura
    grillas=True,               # Mostrar grillas horizontales

    # --- BARRAS ---
    ancho_barra=0.85,            # Ancho de cada barra
    tam_letra_valor_barra=20,   # Tamaño de letra para valores dentro de las barras
    color_valor_barra=None,     # Color del texto de valor en barra
    tam_letra_porce_barra=15,   # Tamaño de letra para porcentajes dentro de las barras
    paleta_colores=None,        # Lista de colores para las barras
    area_min=0,                 # Área mínima para mostrar texto en barra
    altura_min=0,               # Altura mínima para mostrar texto dentro de barra
    valor_barra=True,           # Mostrar valor numérico en la barra
    porce_barra=True,           # Mostrar porcentaje en la barra
    porce_abajo=True,           # Mostrar porcentaje debajo del valor dentro de la barra
    porce_diver=False,          # Porcentaje respecto a suma absoluta (divergente)
    alinea_texto_barra=False,   # Alinear el texto dentro de la barra verticalmente

    # --- CÁPSULAS ---
    valor_capsu=True,           # Mostrar cápsula de total arriba de la barra
    tam_letra_valor_capsu=20,   # Tamaño de letra para valores dentro de las cápsulas
    quitar_capsu=False,         # Quitar la cápsula de total
    capsu_cero=True,            # Mostrar cápsula aunque el valor sea cero
    ajusta_pos_capsu=0.02,      # Ajusta la posición de la cápsula respecto a la barra
    alinea_capsu=False,        # Alinear la cápsula verticalmente

    # --- PORCENTAJES TOTALES ---
    porce_total=True,           # Mostrar porcentaje respecto al total general
    porce_total_inicio=False,   # Mostrar porcentaje respecto al total general al inicio
    separar_por_total=-0.09,      # Separación extra para porcentaje total
    tam_porce_total=25,         # Tamaño de letra para porcentaje total

    # --- LEYENDA ---
    leyenda=None,               # Título de la leyenda
    pos_leyenda='arriba',       # Posición de la leyenda ('arriba' o 'abajo')
    aumenta_sep_leyenda=0.0,    # Espacio extra para la leyenda
    ncol_leyenda=None,          # Número de columnas en la leyenda

    # --- EJE X ---
    tam_letra_ejeX=35,          # Tamaño de letra para etiquetas eje X
    color_letra_ejeX="#000000", # Color de letra para etiquetas eje X
    espacio_inicio=0,           # Espacio extra al inicio del eje x
    nombre_eje_x=None,          # Nombre del eje x
    sustituir_etiquetas=None,   # Lista para sustituir etiquetas del eje x
    orientacion_etiqu_ejeX=None,# Orientación de etiquetas eje x ('horizontal' o None)
    aumenta_sep_eje_x=0.0,      # Aumenta separación en eje x

    # --- EJE Y ---
    tam_letra_ejeY=30,          # Tamaño de letra para etiquetas eje Y
    color_letra_ejeY="#000000", # Color de letra para etiquetas eje Y
    nombre_eje_y=None,          # Nombre del eje y
    y_limits=None,              # Límites del eje y
    ejeY_positivo=False,        # Eje Y solo muestra valores positivos
    div_ejeY=False,             # División personalizada del eje y
    resaltar_etiquetas=None,    # Lista de etiquetas a resaltar
    graf_resp_porce=False,      # Graficar con respecto al porcentaje en el eje Y

):
    """
    Genera un gráfico de barras verticales apiladas a partir de un DataFrame de pandas.
    """
    hay_annotations_externas = False
    espacio = "\u00A0"

    font_config = {
        'family': tipo_letra,
        'variable_x': {'size': tam_letra_ejeX, 'weight': 'medium', 'color': color_letra_ejeX},
        'variable_y': {'size': tam_letra_ejeY, 'weight': 'medium', 'color': color_letra_ejeY},
        'nombre_eje_x': {'size': 25, 'weight': 'medium', 'color': '#000000'},
        'nombre_eje_y': {'size': 22, 'weight': 'medium', 'color': '#000000'},
        'valor_capsula': {'size': tam_letra_valor_capsu, 'weight': 'bold', 'color': '#000000'},
        'valor_porcentaje_barra': {'size': tam_letra_valor_barra, 'weight': 'bold', 'color': '#584290'},
        'valor_porcentaje_barra_porcentaje': {'size': tam_letra_porce_barra, 'weight': 'bold', 'color': '#584290'},
        'porcentaje_total': {'size': tam_porce_total, 'weight': 'semibold', 'color': '#4C6A67'},
        'leyenda': {'size': 24, 'weight': 'medium', 'color': '#767676'}
    }

    plt.rcParams['svg.fonttype'] = 'none'
    font_dirs = [Path("../0_fonts")]
    font_files = font_manager.findSystemFonts(fontpaths=font_dirs)
    for font_file in font_files:
        font_manager.fontManager.addfont(font_file)

    colores_asignados = paleta_colores or ["#10302C", "#4C6A67", "#8FA8A6", "#A3C9A8"]

    if not isinstance(df, pd.DataFrame):
        raise ValueError("El argumento df debe ser un DataFrame de pandas.")
    
    df = df.copy()
    categorias_x = df.columns[0]
    if pd.api.types.is_integer_dtype(df[categorias_x]) and df[categorias_x].between(1900, 2100).all():
        df[categorias_x] = pd.to_datetime(df[categorias_x], format='%Y')
    df = df.set_index(categorias_x)

    df, etiqueta_union_izq = unir_barras(df, union_izq, 'izquierda')
    df, etiqueta_union_der = unir_barras(df, union_der, 'derecha')

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
                if 'separador_derecha' in opciones_extra:
                    datos_para_separadores.append({'posicion': 'despues', 'referencia': categoria, 'texto': opciones_extra['separador_derecha']})
                if 'separador_izquierda' in opciones_extra:
                    datos_para_separadores.append({'posicion': 'antes', 'referencia': categoria, 'texto': opciones_extra['separador_izquierda']})

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

    if ordenar_por == 'valor':
        sort_index = df.sum(axis=1).sort_values(ascending=(orden == 'ascendente')).index
    elif ordenar_por == 'etiqueta':
        indices = list(df.index)
        izq = [etiqueta_union_izq] if etiqueta_union_izq else []
        der = [etiqueta_union_der] if etiqueta_union_der else []
        centro = [i for i in indices if i not in izq + der]
        
        tipos = set(type(idx) for idx in centro)
        reverse_sort = (orden == 'descendente')
        centro_ordenado = sorted(centro, key=lambda x: str(x), reverse=reverse_sort) if len(tipos) > 1 else sorted(centro, reverse=reverse_sort)
        
        sort_index = izq + centro_ordenado + der
    else:
        sort_index = df.index

    df = df.loc[sort_index]
    
    if datos_para_separadores:
        # Ordenar los separadores para procesar 'antes' primero y evitar problemas de índice
        datos_para_separadores.sort(key=lambda x: x['posicion'] == 'antes', reverse=True)
        
        df_list = list(df.iterrows())
        
        # Usar una lista de índices en lugar de get_loc para manejar duplicados
        current_indices = [item[0] for item in df_list]

        for sep_info in datos_para_separadores:
            try:
                # Encontrar la posición del índice de referencia en la lista actual
                idx_pos = current_indices.index(sep_info['referencia'])
                
                idx_separador = f"__espaciador__{sep_info['referencia']}_{sep_info['posicion']}_{np.random.randint(1000)}"
                fila_separador = pd.Series({col: 0 for col in df.columns}, name=idx_separador)
                etiquetas_personalizadas[idx_separador] = sep_info['texto']
                
                # La posición de inserción es relativa a la lista que se está modificando
                insert_at = idx_pos if sep_info['posicion'] == 'antes' else idx_pos + 1
                
                df_list.insert(insert_at, (idx_separador, fila_separador))
                
                # Actualizar la lista de índices después de la inserción
                current_indices.insert(insert_at, idx_separador)

            except ValueError:
                print(f"Advertencia: No se encontró la clave '{sep_info['referencia']}' para añadir un separador.")
        
        df = pd.DataFrame.from_dict(dict(df_list), orient='index')
        df.columns = categorias

    suma_total = df.sum(axis=1)
    total_general = suma_total.sum()

    df_plot = df.copy()
    if graf_resp_porce:
        # Evitar división por cero y convertir a porcentajes
        suma_total_no_cero = suma_total.replace(0, np.nan)
        df_plot = df.div(suma_total_no_cero, axis=0).multiply(100).fillna(0)
    
    es_divergente = any(df.min() < 0)
    suma_positivos_por_barra = None
    suma_negativos_por_barra = None
    suma_absoluta_por_barra = None
    total_general_absoluto = None
    total_general_positivos = None
    if es_divergente:
        suma_negativos_por_barra = df[df < 0].sum(axis=1)
        if porce_diver:
            suma_positivos_por_barra = df[df > 0].sum(axis=1)
            total_general_positivos = suma_positivos_por_barra.sum()
        else:
            suma_absoluta_por_barra = df.abs().sum(axis=1)
            total_general_absoluto = suma_absoluta_por_barra.sum()

    x_max_pos = df[df > 0].sum(axis=1).max()
    x_max_neg = df[df < 0].sum(axis=1).min()
    x_max = max(x_max_pos, abs(x_max_neg)) * 1.15
    if pd.isna(x_max): x_max = suma_total.max() * 1.15

    if graf_resp_porce:
        x_max = 100 * 1.15

    entidades = df.index.values

    es_fecha = any(isinstance(idx, (pd.Timestamp, np.datetime64)) for idx in df.index if idx not in [etiqueta_union_izq, etiqueta_union_der])
    
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

    valores = [df_plot[col].values for col in df_plot.columns]
    posiciones = np.arange(len(entidades))

    longitudes = [len(f"{espacio*4}{int(total_valor):,}{espacio*4}") for total_valor in suma_total]
    moda_capsula_len = mode(longitudes) if longitudes else 10
    extra_width = moda_capsula_len * 0.1
    base_width = max(12, len(entidades) * extra_width)
    fig_width = ancho_fig if ancho_fig is not None else base_width
    fig_height = alto_fig if alto_fig is not None else fig_width / 2
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
            ax.bar(pos, current_val, width=ancho_barra, bottom=bar_bottom, color=color, edgecolor=edge_color, linestyle=line_style, linewidth=line_width, zorder=2, label=label)
            
            if current_val > 0: bottom_pos += current_val
            else: bottom_neg += current_val

            area_barra = abs(current_val) * ancho_barra
            if (porce_barra or valor_barra or (entidad in textos_barra_personalizados)) and area_barra >= area_min:
                
                if es_divergente:
                    if porce_diver:
                        if current_val > 0:
                            base_porcentaje = suma_positivos_por_barra.loc[entidad]
                            porcentaje_valor = (current_val / base_porcentaje) * 100 if base_porcentaje != 0 else 0
                        else: # current_val < 0
                            base_porcentaje = suma_negativos_por_barra.loc[entidad]
                            porcentaje_valor = (current_val / base_porcentaje) * 100 if base_porcentaje != 0 else 0
                    else: # porce_diver es False
                        base_porcentaje = suma_absoluta_por_barra.loc[entidad]
                        porcentaje_valor = (current_val / base_porcentaje) * 100 if base_porcentaje != 0 else 0
                else: # no es divergente
                    porcentaje_valor = (df.iloc[pos, i] / total_valor) * 100 if total_valor != 0 else 0

                text_pos_y = bar_bottom + current_val / 2
                
                texto_final = ""
                texto_a_dibujar = True

                # Parámetros para la alineación del texto en la barra
                rotacion_texto_barra = 90 if alinea_texto_barra else 0
                ha_texto_barra = 'center'
                va_texto_barra_valor = 'bottom' if porce_abajo else 'center'
                va_texto_barra_porce = 'top' if porce_abajo else 'center'
                va_texto_barra_unificado = 'center'

                if entidad in textos_barra_personalizados:
                    textos_barra = textos_barra_personalizados[entidad]
                    if i < len(textos_barra) and textos_barra[i] is not None:
                        texto_final = textos_barra[i]
                elif valor_barra and porce_barra:
                    texto_valor = f"{abs(df.iloc[pos, i]):,.0f}"
                    texto_porcentaje = f"({abs(porcentaje_valor):.1f}%)" if not porce_abajo else f"{abs(porcentaje_valor):.1f}%"
                    
                    if porce_abajo:
                        ax.text(pos, text_pos_y, texto_valor, va=va_texto_barra_valor, ha=ha_texto_barra, rotation=rotacion_texto_barra,
                                fontsize=font_config['valor_porcentaje_barra']['size'],
                                fontfamily=font_config['family'],
                                fontweight=font_config['valor_porcentaje_barra']['weight'],
                                color=text_color_interior,
                                linespacing=1.5)
                        ax.text(pos, text_pos_y, texto_porcentaje, va=va_texto_barra_porce, ha=ha_texto_barra, rotation=rotacion_texto_barra,
                                fontsize=font_config['valor_porcentaje_barra_porcentaje']['size'],
                                fontfamily=font_config['family'],
                                fontweight=font_config['valor_porcentaje_barra_porcentaje']['weight'],
                                color=text_color_interior,
                                linespacing=1.5)
                        texto_a_dibujar = False
                    else:
                        texto_final = f"{texto_valor} {texto_porcentaje}"
                elif valor_barra:
                    texto_final = f"{abs(df.iloc[pos, i]):,.0f}"
                elif porce_barra:
                    texto_final = f"{abs(porcentaje_valor):.1f}%"

                if texto_a_dibujar and texto_final:
                    font_size_a_usar = font_config['valor_porcentaje_barra_porcentaje']['size'] if not valor_barra and porce_barra else font_config['valor_porcentaje_barra']['size']
                    ax.text(pos, text_pos_y, texto_final, va=va_texto_barra_unificado, ha=ha_texto_barra, rotation=rotacion_texto_barra,
                            fontsize=font_size_a_usar,
                            fontfamily=font_config['family'],
                            fontweight=font_config['valor_porcentaje_barra']['weight'],
                            color=text_color_interior,
                            linespacing=1.5 if porce_abajo else 1.2)

        if annotations_externas:
            texto_x_base = pos + ancho_barra * 0.6 
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

        if valor_capsu and "__espaciador__" not in str(entidad):
            valor_a_mostrar = total_valor
            if es_divergente:
                if not porce_diver:
                    valor_a_mostrar = suma_absoluta_por_barra.loc[entidad]
                else: # porce_diver es True
                    valor_a_mostrar = suma_positivos_por_barra.loc[entidad]

            if capsu_cero or valor_a_mostrar != 0:
                texto_a_mostrar = f"{int(valor_a_mostrar):,}"
                if etiquetas_finales is not None and not pd.isna(etiquetas_finales.iloc[pos]):
                    texto_a_mostrar = str(etiquetas_finales.iloc[pos])
                
                texto_capsula = f"{espacio*2}{texto_a_mostrar}{espacio*2}"
                base_pos_y = bottom_pos if es_divergente else (100 if graf_resp_porce else total_valor)
                text_y_pos = base_pos_y + x_max * ajusta_pos_capsu
                
                # Parámetros para la alineación de la cápsula
                rotacion_capsula = 90 if alinea_capsu else 0
                ha_capsula = 'center'
                va_capsula = 'bottom'
                pos_x_capsula = pos
                pos_y_capsula = text_y_pos

                if not quitar_capsu:
                    ax.text(pos_x_capsula, pos_y_capsula, texto_capsula,
                        bbox=dict(boxstyle="round,pad=0.15,rounding_size=0.8", facecolor=(1, 1, 1, 0), edgecolor='#002F2A', linewidth=1.5),
                        ha=ha_capsula, va=va_capsula, rotation=rotacion_capsula,
                        fontdict={
                            'family': font_config['family'], 'size': font_config['valor_capsula']['size'],
                            'weight': font_config['valor_capsula']['weight'], 'color': font_config['valor_capsula']['color']
                        })
                else:
                    ax.text(pos_x_capsula, pos_y_capsula, texto_a_mostrar, ha=ha_capsula, va=va_capsula, rotation=rotacion_capsula,
                        fontdict={
                            'family': font_config['family'], 'size': font_config['valor_capsula']['size'],
                            'weight': font_config['valor_capsula']['weight'], 'color': font_config['valor_capsula']['color']
                        })

        if es_divergente and valor_capsu and bottom_neg < 0:
            valor_negativo_total = suma_negativos_por_barra.loc[entidad]
            if capsu_cero or valor_negativo_total != 0:
                texto_a_mostrar_neg = f"{int(abs(valor_negativo_total)):,}"
                texto_capsula_neg = f"{espacio*2}{texto_a_mostrar_neg}{espacio*2}"
                text_y_pos_neg = bottom_neg - x_max * ajusta_pos_capsu

                if not quitar_capsu:
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

        if porce_total_inicio:
            valor_numerador = total_valor
            valor_denominador = total_general
            if es_divergente:
                if not porce_diver:
                    valor_numerador = suma_absoluta_por_barra.loc[entidad]
                    valor_denominador = total_general_absoluto
                else: # porce_diver es True
                    valor_numerador = suma_positivos_por_barra.loc[entidad]
                    valor_denominador = total_general_positivos
            
            porcentaje = round((valor_numerador / valor_denominador) * 100, 1) if valor_denominador != 0 else 0
            etiqueta_actual = entidades_formateadas[pos]
            
            if resaltar_etiquetas and etiqueta_actual in resaltar_etiquetas:
                texto_a_mostrar = f"{espacio*1}{etiqueta_actual}   {porcentaje}%{espacio*1}"
                bbox_capsula = dict(facecolor="#a3173e", edgecolor="none", boxstyle="round,pad=0.15,rounding_size=0.8")
                ax.text(pos, -x_max*0.02, texto_a_mostrar, ha='center', va='top', rotation=90,
                        color="white", bbox=bbox_capsula,
                        fontdict={'family': font_config['family'], 'size': font_config['porcentaje_total']['size'], 'weight': font_config['porcentaje_total']['weight']})
            else:
                texto_a_mostrar = f"{espacio*1}{porcentaje}%{espacio*1}"
                ax.text(pos, 0, texto_a_mostrar, ha='right', va='top', rotation=90,
                        color=font_config['porcentaje_total']['color'],
                        fontdict={'family': font_config['family'], 'size': font_config['porcentaje_total']['size'], 'weight': font_config['porcentaje_total']['weight']})

        if porce_total:
            valor_numerador = total_valor
            valor_denominador = total_general
            if es_divergente:
                if not porce_diver:
                    valor_numerador = suma_absoluta_por_barra.loc[entidad]
                    valor_denominador = total_general_absoluto
                else: # porce_diver es True
                    valor_numerador = suma_positivos_por_barra.loc[entidad]
                    valor_denominador = total_general_positivos

            porcentaje = round((valor_numerador / valor_denominador) * 100, 1) if valor_denominador != 0 else 0
            
            desplazamiento_y = 0
            if valor_capsu:
                desplazamiento_y = x_max * (0.15 if not quitar_capsu else 0.08)
            else:
                desplazamiento_y = x_max * 0.03
            
            base_pos_y = bottom_pos if es_divergente else (100 if graf_resp_porce else total_valor)
            desplazamiento_final = base_pos_y + desplazamiento_y + (x_max * separar_por_total)

            ax.text(pos, desplazamiento_final, f"{porcentaje}%", ha='center', va='bottom',
                    color=font_config['porcentaje_total']['color'],
                    fontdict={'family': font_config['family'], 'size': font_config['porcentaje_total']['size'], 'weight': font_config['porcentaje_total']['weight']})

    if (porce_total_inicio or resaltar_etiquetas) and resaltar_etiquetas:
        entidades_formateadas_final = []
        for e in entidades_formateadas:
            if e in resaltar_etiquetas:
                entidades_formateadas_final.append("")
            else:
                entidades_formateadas_final.append(e)
        entidades_formateadas = entidades_formateadas_final

    ax.set_xticks(posiciones)
    rotation_val = 90 if orientacion_etiqu_ejeX != 'horizontal' else 0
    ha_val = 'right' if orientacion_etiqu_ejeX != 'horizontal' else 'center'
    ax.set_xticklabels(
        entidades_formateadas,
        fontsize=font_config['variable_x']['size'],
        fontweight=font_config['variable_x']['weight'],
        fontfamily=font_config['family'],
        color=font_config['variable_x']['color'],
        rotation=rotation_val,
        ha=ha_val
    )
    
    if resaltar_etiquetas and not porce_total_inicio:
        original_labels = [str(idx) for idx in df.index]
        if sustituir_etiquetas:
            original_labels = sustituir_etiquetas
        
        for pos, etiqueta_actual in enumerate(original_labels):
            if etiqueta_actual in resaltar_etiquetas:
                texto_capsula = f"{espacio*1}{etiqueta_actual}{espacio*1}"
                bbox_capsula = dict(facecolor="#a3173e", edgecolor="none", boxstyle="round,pad=0.15,rounding_size=0.8")
                ax.text(pos, -x_max*0.02, texto_capsula, ha='center', va='top', rotation=90,
                        color="white", bbox=bbox_capsula,
                        fontdict={'family': font_config['family'], 'size': font_config['porcentaje_total']['size'], 'weight': font_config['porcentaje_total']['weight']})

    right_x_limit = len(entidades) - 0.5 + (0.8 if hay_annotations_externas else 0)
    ax.set_xlim(-0.5, right_x_limit)
    
    if y_limits and not graf_resp_porce:
        ax.set_ylim(y_limits)
    else:
        y_min = (-x_max * (1 + aumenta_sep_eje_x)) if es_divergente and not graf_resp_porce else 0
        y_max_val = 100 if graf_resp_porce else x_max
        ax.set_ylim(y_min, y_max_val)
        
    if div_ejeY:
        ax.yaxis.set_major_locator(mticker.MultipleLocator(div_ejeY))
    else:
        ax.yaxis.set_major_locator(mticker.MaxNLocator(nbins='auto', steps=[1, 2, 5, 10]))
    
    if graf_resp_porce:
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{int(x)}%'))
    else:
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{int(abs(x)) if ejeY_positivo else int(x):,}"))

    plt.setp(ax.get_yticklabels(), **font_config['variable_y'])
    
    ax.grid(visible=grillas, axis='y', color='#B9B9B9', linewidth=0.75, linestyle='-')
    if porce_total_inicio:
        ax.tick_params(axis='x', pad=espacio_inicio)
        
    if nombre_eje_x:
        ax.set_xlabel(nombre_eje_x, labelpad=18, **font_config['nombre_eje_x'])
    if nombre_eje_y:
        ax.set_ylabel(nombre_eje_y, labelpad=18, **font_config['nombre_eje_y'])

    for label, entidad_formateada in zip(ax.get_xticklabels(), entidades_formateadas):
        try:
            mapa_formato_a_original = {ent_fmt: ent_orig for ent_fmt, ent_orig in zip(entidades_formateadas, df.index)}
            original_index = mapa_formato_a_original.get(entidad_formateada)
            
            if original_index and "__espaciador__" in str(original_index):
                label.set_rotation(0)
                label.set_ha('center')
        except (ValueError, IndexError, KeyError):
            pass

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
        
    ax.spines[['top', 'right', 'left']].set_visible(False)
    ax.spines['bottom'].set_visible(True)

    if es_divergente and not graf_resp_porce:
        ax.axhline(0, color='black', linewidth=1)

    os.makedirs("output", exist_ok=True)
    plt.tight_layout()
    
    base_path = f"output/{nombre}"
    plt.savefig(f"{base_path}.svg", format='svg', bbox_inches='tight', dpi=300, transparent=True)
    #plt.savefig(f"{base_path}.png", format='png', bbox_inches='tight', dpi=300, transparent=True)
    
    try:
        limpiar_svg_con_scour(f"{base_path}.svg", f"{base_path}_scour.svg")
    except Exception as e:
        print(f"Error al optimizar SVG: {e}")

    plt.show()