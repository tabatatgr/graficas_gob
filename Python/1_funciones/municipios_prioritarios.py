from pathlib import Path
import pandas as pd
import matplotlib.font_manager as font_manager
import matplotlib.pyplot as plt
import os
from matplotlib.patches import FancyBboxPatch

from caja import caja
from lineas import lineas  
from funciones import mostrar_guardar_figura

def municipios_prioritarios(
    df_caja1,                        # DataFrame para la primera caja (pandas.DataFrame)
    df_caja2,                        # DataFrame para la segunda caja (pandas.DataFrame)
    df_linea,                        # DataFrame para la gráfica de líneas (pandas.DataFrame)
    titulo="Título de la gráfica",   # Título principal de la gráfica (str)
    tipo_letra="Montserrat",         # Tipo de letra para todo el texto (str, ej: 'Montserrat', 'Arial')
    ancho_fig=6,                     # Ancho de la figura en pulgadas (int o float)
    alto_fig=5,                      # Alto de la figura en pulgadas (int o float)
    fecha_linea_vertical=pd.to_datetime('2024-10-01'), # Fecha para la línea vertical en la gráfica de líneas (pandas.Timestamp)
    fondo='transparente',            # Color de fondo de la figura ('transparente' o 'white')
    mostrar_fig=True,                # Si True, muestra la figura en pantalla (bool)
    guardar_fig=True                 # Si True, guarda la figura como archivo (bool)
):
    
    # --- VALIDACIONES DE DATOS ---
    # Validación para df_caja1
    if df_caja1.iloc[0, 0] > df_caja1.iloc[0, 1] and df_caja1.iloc[0, 2] > 0:
        raise ValueError("df_caja1: inconsistencia de los datos de la segunda y tercera columna. Verifica los signos.")
    if df_caja1.iloc[0, 0] < df_caja1.iloc[0, 1] and df_caja1.iloc[0, 2] < 0:
        raise ValueError("df_caja1: inconsistencia de los datos de la segunda y tercera columna. Verifica los signos.")

    # Validación para df_caja2
    if df_caja2.iloc[0, 0] > df_caja2.iloc[0, 1] and df_caja2.iloc[0, 2] > 0:
        raise ValueError("df_caja2: inconsistencia de los datos de la segunda y tercera columna. Verifica los signos.")
    if df_caja2.iloc[0, 0] < df_caja2.iloc[0, 1] and df_caja2.iloc[0, 2] < 0:
        raise ValueError("df_caja2: inconsistencia de los datos de la segunda y tercera columna. Verifica los signos.")

    plt.close('all')
    plt.rcParams['svg.fonttype'] = 'none'

    font_dirs = [Path("../0_fonts")]
    font_files = font_manager.findSystemFonts(fontpaths=font_dirs)
    for font_file in font_files:
        font_manager.fontManager.addfont(font_file)
    plt.rcParams['font.family'] = tipo_letra

    # FASE 1: Crear y guardar la parte superior
    fig_top = plt.figure(figsize=(ancho_fig, alto_fig*0.45))
    gs_top = fig_top.add_gridspec(2, 2, height_ratios=[0.65, 0.35], wspace=0, hspace=0)
    ax_top = [None for _ in range(3)]
    ax_top[0] = fig_top.add_subplot(gs_top[0, 0])
    ax_top[1] = fig_top.add_subplot(gs_top[0, 1])
    ax_top[2] = fig_top.add_subplot(gs_top[1, :])

    # Determinar el color para la primera caja basado en la condición
    color_caja1 = "#054c32" if df_caja1.iloc[0, 0] > df_caja1.iloc[0, 1] else "#801741"

    caja(df_caja1,
         tam_letra_per1=15,
         tam_letra_per2=22,
         tam_letra_dif=14,
         color_letra_per1='#000000',
         color_letra_per2=color_caja1,
         color_letra_dif=color_caja1,
         weight_letra_per1='bold',
         weight_letra_per2='bold',
         weight_letra_dif='bold',
         tam_letra_titulo=11,
         color_letra_titulo='black',
         weight_letra_titulo='medium',
         mostrar_fig=False,
         guardar_fig=False,
         fig=fig_top,
         ax=ax_top[0]
    )

    # Determinar el color para la segunda caja basado en la condición
    color_caja2 = "#054c32" if df_caja2.iloc[0, 0] > df_caja2.iloc[0, 1] else "#801741"

    caja(df_caja2,
         tam_letra_per1=15,
         tam_letra_per2=22,
         tam_letra_dif=14,
         color_letra_per1='#000000',
         color_letra_per2=color_caja2,
         color_letra_dif=color_caja2,
         weight_letra_per1='bold',
         weight_letra_per2='bold',
         weight_letra_dif='bold',
         tam_letra_titulo=11,
         color_letra_titulo='black',
         weight_letra_titulo='medium',
         mostrar_fig=False,
         guardar_fig=False,
         fig=fig_top,
         ax=ax_top[1]
    )

    rect_height = 0.65
    rect_y = 0.23
    # Define un inicio para el rectángulo y ajusta el ancho para mantener el final fijo
    rect_x_start = 0.03
    ax_top[2].add_patch(FancyBboxPatch(
        (rect_x_start, rect_y), 1 - rect_x_start, rect_height,
        boxstyle='square,pad=0',
        facecolor='#525252', alpha=0.8, transform=ax_top[2].transAxes, clip_on=False, zorder=0,
        edgecolor='black', linewidth=1.0
    ))
    ax_top[2].text(0.52, rect_y + rect_height/2, titulo, fontsize=16, fontweight='bold', color='#ffffff',
                   ha='center', va='center', transform=ax_top[2].transAxes, zorder=1)
    ax_top[2].axis('off')

    es_transparente = (fondo == 'transparente')

    temp_top_path = 'temp_top.png'
    fig_top.savefig(temp_top_path, bbox_inches='tight', dpi=300, transparent=es_transparente, pad_inches=0)
    plt.close(fig_top)

    # FASE 2: Crear la parte inferior
    fig_bottom = plt.figure(figsize=(ancho_fig, alto_fig*0.6))
    lineas(df_linea,
        nombre='df_linea', 
        tipo_letra=tipo_letra,
        ancho_fig=ancho_fig,
        alto_fig=alto_fig*0.6,
        tam_letra_ejeX=7.4,
        tam_letra_ejeY=16,
        color_letra_ejeX='#535353',
        color_letra_ejeY='#535353',
        weight_letra_ejeX='bold',
        weight_letra_ejeY='bold',
        escalonada=True,
        paleta_colores=['#691c32'],
        modalidad_fechas=2,
        lineas_verticales=[
            {'x': fecha_linea_vertical, 'color': '#DC8F12', 'linewidth': 3},
        ],
        sin_tag=100000,
        tag_max=True,
        tag_final=True,
        tag_especifico=[fecha_linea_vertical - pd.DateOffset(months=1)],
        decimales_capsu=1,
        rounding_size=0.5,
        capsula_valor_weight='bold',
        ancho_linea=3.5,
        margen=True,
        margen_color='#e5e5e5',
        margen_ancho=3,
        marcas_ejes=False,
        mostrar_fig=False,
        guardar_fig=False,
        ajusta_pos_capsu=0.07,
        reducir_ticks_y=True, 
    )

    temp_bottom_path = 'temp_bottom.png'
    plt.savefig(temp_bottom_path, bbox_inches='tight', dpi=300, transparent=es_transparente, pad_inches=0)
    plt.close('all')

    # FASE 3: Combinar ambas partes en una única figura final
    fig_final = plt.figure(figsize=(ancho_fig, alto_fig))
    if es_transparente:
        fig_final.patch.set_alpha(0.0) # <-- Hace transparente el fondo de la figura
    img_top = plt.imread(temp_top_path)
    img_bottom = plt.imread(temp_bottom_path)
    # Ajusta hspace a un valor negativo pequeño si es necesario para eliminar el espacio restante
    gs_final = fig_final.add_gridspec(2, 1, height_ratios=[0.4, 0.6], hspace=-0.05)

    ax_final_top = fig_final.add_subplot(gs_final[0])
    ax_final_bottom = fig_final.add_subplot(gs_final[1])

    ax_final_top.imshow(img_top, aspect='auto')
    ax_final_top.axis('off')
    ax_final_bottom.imshow(img_bottom, aspect='auto')
    ax_final_bottom.axis('off')
    
    if es_transparente:
        ax_final_top.patch.set_alpha(0.0) # <-- Hace transparente el fondo de los ejes
        ax_final_bottom.patch.set_alpha(0.0) # <-- Hace transparente el fondo de los ejes

    mostrar_guardar_figura(
        fig=fig_final,
        ax=None,
        nombre_df=titulo,
        guardar_fig=guardar_fig,
        mostrar_fig=mostrar_fig,
        limpiar_svg_con_scour=False
    )

    for temp_file in [temp_top_path, temp_bottom_path]:
        if os.path.exists(temp_file):
            os.remove(temp_file)