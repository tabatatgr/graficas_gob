# Función para gráficas de barras agrupadas y apiladas
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager
from pathlib import Path
import matplotlib.ticker as mticker
import os

def agrupadasyapiladas(
    dataframes, 
    nombre="grafica_agrupadasyapiladas",
    font='Arial',
    barra_valor=True, 
    porcentaje=True, 
    capsula_max=True,
    ancho_px=3200,
    alto_px=520,
    dpi=100,
    paleta_colores=None,
    columna_grupo='Categoria',
    columna_subgrupo='Mes',
    columna_valor='Valor',
    excluir_total=False,
    output_dir="output",
    **kwargs
):
    """
    Genera una gráfica de barras apiladas agrupadas para múltiples DataFrames.

    Args:
        dataframes (list of pd.DataFrame): Lista de DataFrames con los datos de los grupos de subgrupos apilados.
        font_size (int): Tamaño de la fuente para los elementos de la gráfica.
    """

    # Configuración de la fuente
    font_config = {
        'family': 'Arial',
        'titulo': {'size': 36, 'weight': 'medium', 'color': '#000000'},
        'eje_y': {'size': 18, 'weight': 'medium', 'color': '#000000'},
        'eje_x': {'size': 18, 'weight': 'medium', 'color': '#000000'},
        'etiquetas_eje_y': {'size': 24, 'weight': 'medium', 'color': '#767676'},
        'etiquetas_eje_x': {'size': 24, 'weight': 'semibold', 'color': '#767676'},
        'barra_valor': {'size': 9, 'weight': 'medium', 'color': '#10302C'},
        'capsula_max': {'size': 12, 'weight': 'medium', 'color': 'white'},
        'porcentaje': {'size': 10, 'weight': 'medium', 'color': '#4C6A67'},
        'leyenda': {'size': 14, 'weight': 'medium', 'color': '#767676'}  # Nueva categoría para la leyenda
    }

    plt.rcParams['svg.fonttype'] = 'none'
    font_dirs = [Path("../0_fonts")]
    font_files = font_manager.findSystemFonts(fontpaths=font_dirs)
    for font_file in font_files:
        font_manager.fontManager.addfont(font_file)

    # Configuración de los grupos y subgrupos
    grupos = dataframes[0]['Sexo'].unique().tolist()
    subgrupos_list = [df['Edad'].unique().tolist() for df in dataframes]

    # Configuración para fechas
    #grupos_raw = dataframes[0]['Sexo'].unique().tolist()

    #if pd.api.types.is_datetime64_any_dtype(dataframes[0]['Sexo']):
        #meses = {
            #1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
            #7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
        #}
        #grupos = [f"{meses[fecha.month]} {fecha.year}" for fecha in grupos_raw]
    #else:
        #grupos = grupos_raw

    # Obtener colores desde la función colores()
    lista_colores = ["#006157", "#767676", "#671435", "#9B2247", "#9D792A", "#D5B162", "#10302C", "#E6D194", "#018477", "#FF6666", "#00008B", "#854991"]
    colores_por_grupo = []
    color_index = 0
    for subgrupos in subgrupos_list:
        colores_por_grupo.append(lista_colores[color_index:color_index + len(subgrupos)])
        color_index += len(subgrupos)

    # Configuración visual
    ancho_barra = 0.2  # Ancho fijo para cada barra
    espacio_entre_barras = 0.05  # Espacio entre barras del mismo grupo
    espacio_entre_grupos = 1.0  # Espacio entre grupos
    
    # Calcular el ancho total del grupo y el desplazamiento inicial
    ancho_grupo = len(dataframes) * (ancho_barra + espacio_entre_barras)
    desplazamiento_inicial = -ancho_grupo / 2

    # Configurar el tamaño de la figura en píxeles
    ancho_px = 1480
    alto_px = 520
    dpi = 100  # Resolución en píxeles por pulgada
    ancho_in = ancho_px / dpi
    alto_in = alto_px / dpi

    # Crear la figura con el tamaño especificado
    fig, ax = plt.subplots(figsize=(ancho_in, alto_in), dpi=dpi)
    x_pos = np.arange(len(grupos))

    # Dibujar barras apiladas para cada DataFrame
    for df, colores, offset in zip(dataframes, colores_por_grupo, range(len(dataframes))):
        bottom = np.zeros(len(grupos))  # Inicializar con ceros
        total_grupo = (
            df.groupby("Sexo")["Cantidad"].sum()
            .reindex(grupos)
            .values
            )
        # Usar los valores únicos de 'Edad' en vez de df.columns
        subgrupos = df['Edad'].unique().tolist()
        for subgrupo, color in zip(subgrupos, colores):
            valores = df[df['Edad'] == subgrupo].sort_values('Sexo')['Cantidad'].values
            # Asegurarse de que valores tenga la misma longitud que grupos
            if len(valores) < len(grupos):
                # Rellenar con ceros si faltan valores
                valores = np.pad(valores, (0, len(grupos) - len(valores)), 'constant')
            # Calcular la posición de cada barra para que esté centrada en su grupo
            posicion_barra = x_pos + desplazamiento_inicial + offset * ancho_barra
            ax.bar(
                posicion_barra,
                valores,
                width=ancho_barra,
                bottom=bottom,
                color=color,
                label=subgrupo,
                zorder=3
            )
            # Calcular el tamaño dinámico de la fuente basado en el ancho de la barra
            font_size_dynamic = max(1, min(12, int(ancho_barra * 40)))

            # Agregar etiquetas dentro de las barras
            for i, valor in enumerate(valores):
                porcentaje = (valor / total_grupo[i]) * 100 if total_grupo[i] != 0 else 0
                if barra_valor:
                    ax.text(
                        posicion_barra[i],  # Usar la misma posición que la barra
                        bottom[i] + valor / 2,
                        f"{int(valor):,} ({porcentaje:.1f}%)" if porcentaje else f"{int(valor):,}",
                        ha='center',
                        va='center',
                        fontsize=font_config['barra_valor']['size'],
                        fontweight=font_config['barra_valor']['weight'],
                        color='white' if porcentaje > 10 else 'black'
                    )
            bottom += np.array(valores)  # Sumar para el siguiente apilamiento

        # Agregar acumulados encima de las barras apiladas
        if capsula_max:
            factor_separacion = max(bottom) * 0.05
            for i, total in enumerate(bottom):
                ax.text(
                    posicion_barra[i],  # Usar la misma posición que las barras
                    total + factor_separacion,
                    f"{int(total):,}",
                    ha="center",
                    va="bottom",
                    fontsize=font_config['capsula_max']['size'],
                    fontweight=font_config['capsula_max']['weight'],
                    color=colores[1] if len(colores) > 1 else 'black',
                    bbox=dict(boxstyle="round,pad=0.35,rounding_size=0.99", fc="white", ec=colores[0], alpha=1.0)
                )

    # Modificar la posición de la leyenda
    ax.legend(
        loc='upper center',
        bbox_to_anchor=(0.5, 1.5),
        frameon=False,
        prop={'size': font_config['leyenda']['size'], 'weight': font_config['leyenda']['weight']},
        ncol=max(1, len(dataframes)),  # Ajustar dinámicamente el número de columnas
    )

    # Desactivar o activar bordes
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(True)

    # Asignar grosor a los ejes visibles
    ax.spines['bottom'].set_linewidth(2)

    # Mantener las líneas del grid
    ax.grid(axis='y', linestyle='-', color='#000000', alpha=0.2, linewidth=0.75)

    # Formatear los números del eje Y con comas
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))

    # Configurar las etiquetas del eje Y
    ax.tick_params(axis='y', labelsize=font_config['eje_y']['size'], labelcolor=font_config['eje_y']['color'])
    ax.yaxis.label.set_size(font_config['eje_y']['size'])
    ax.yaxis.label.set_weight(font_config['eje_y']['weight'])
    ax.yaxis.label.set_color(font_config['eje_y']['color'])

    # Calcular las posiciones centrales de cada grupo para las etiquetas
    posiciones_centrales = []
    for i in x_pos:
        # Calcula el centro del grupo sumando la posición de la barra del medio
        barra_central = i + desplazamiento_inicial + (len(dataframes) // 2) * ancho_barra
        posiciones_centrales.append(barra_central)

    # Asignar las etiquetas centradas debajo de las barras
    ax.set_xticks(posiciones_centrales)  # Usar las posiciones centrales calculadas
    ax.set_xticklabels(grupos, fontsize=font_config['eje_x']['size'],
                    fontweight=font_config['eje_x']['weight'],
                    color=font_config['eje_x']['color'])
    ax.set_ylabel('Valores', fontsize=font_config['etiquetas_eje_y']['size'], fontweight=font_config['etiquetas_eje_y']['weight'], color=font_config['etiquetas_eje_y']['color'])
    plt.tight_layout()

    # Crear directorio de salida si no existe
    os.makedirs(output_dir, exist_ok=True)
    
    # Guardar la gráfica como archivo SVG
    output_path = os.path.join(output_dir, f"{nombre}.svg")
    plt.savefig(output_path, format="svg", bbox_inches='tight', dpi=dpi)
    plt.show()