import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

from funciones import mostrar_guardar_figura  

def caja(
    df,                         # DataFrame de entrada (debe tener al menos 3 columnas: previo, actual, diferencia)
    tam_letra_per1=18,          # Tamaño de letra para el valor previo (int)
    tam_letra_per2=38,          # Tamaño de letra para el valor actual (int)
    tam_letra_dif=20,           # Tamaño de letra para la diferencia porcentual (int)
    color_letra_per1='black',   # Color de letra para el valor previo (str, ej: 'black', '#123456')
    color_letra_per2='#054c32', # Color de letra para el valor actual (str)
    color_letra_dif='#054c32',  # Color de letra para la diferencia porcentual (str)
    weight_letra_per1='normal', # Grosor de letra para el valor previo ('normal', 'bold', etc.)
    weight_letra_per2='bold',   # Grosor de letra para el valor actual ('normal', 'bold', etc.)
    weight_letra_dif='bold',    # Grosor de letra para la diferencia porcentual ('normal', 'bold', etc.)
    tam_letra_titulo=14,        # Tamaño de letra para el título (int)
    color_letra_titulo='#595959', # Color de letra para el título (str)
    weight_letra_titulo='bold', # Grosor de letra para el título ('normal', 'bold', etc.)
    ancho_rec=0.9,              # Ancho del rectángulo de fondo (float, 0 a 1)
    alto_rec=0.7,               # Alto del rectángulo de fondo (float, 0 a 1)
    nombre_df="caja",           # Nombre base para archivos de salida (str)
    guardar_fig=True,           # Guardar la figura al terminar (bool: True/False)
    mostrar_fig=True,           # Mostrar la figura al terminar (bool: True/False)
    limpiar_svg_con_scour=None, # Función para limpiar SVG al guardar (None o función)
    fig=None,                   # Figura de matplotlib existente (None o matplotlib.figure.Figure)
    ax=None,                    # Ejes de matplotlib existentes (None o matplotlib.axes.Axes)
):
    # Usar fig y ax existentes si se pasan, si no crear nuevos
    if fig is None or ax is None:
        fig, ax = plt.subplots(figsize=(4, 2))

    previo = df.iloc[0, 0]
    actual = df.iloc[0, 1]
    diferencia = df.iloc[0, 2]
    titulo = df.columns[0]

    # Sombra del rectángulo
    shadow_rect = FancyBboxPatch((0.06, 0.13), ancho_rec, alto_rec,
                               boxstyle='Round, pad=0, rounding_size=0.05',
                               color='grey', alpha=0.15,
                               transform=ax.transAxes)
    ax.add_patch(shadow_rect)

    # Caja de fondo
    rounded_rect = FancyBboxPatch((0.05, 0.15), ancho_rec, alto_rec,
                               boxstyle='Round, pad=0, rounding_size=0.05',
                               color='#f8f8ff', alpha=1.0,
                               transform=ax.transAxes)
    ax.add_patch(rounded_rect)

    # Elementos centrados verticalmente
    ax.text(0.3, 0.62, actual,
            fontsize=tam_letra_per2, fontweight=weight_letra_per2,
            color=color_letra_per2, va='center', ha='center', transform=ax.transAxes)
    ax.text(0.3, 0.35, f'({diferencia}%)',
            fontsize=tam_letra_dif, fontweight=weight_letra_dif,
            color=color_letra_dif, va='center', ha='center', transform=ax.transAxes)
    ax.text(0.7, 0.6, titulo,
            fontsize=tam_letra_titulo, fontweight=weight_letra_titulo,
            color=color_letra_titulo, va='center', ha='center', transform=ax.transAxes)
    ax.text(0.7, 0.33, previo,
            fontsize=tam_letra_per1, fontweight=weight_letra_per1,
            color=color_letra_per1, va='center', ha='center', transform=ax.transAxes)

    ax.set_yticks([])
    ax.set_xticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_ylim(0, 1)
    ax.set_xlim(0, 1)
    plt.tight_layout()
    
    return mostrar_guardar_figura(fig, ax, nombre_df, guardar_fig, mostrar_fig, limpiar_svg_con_scour)