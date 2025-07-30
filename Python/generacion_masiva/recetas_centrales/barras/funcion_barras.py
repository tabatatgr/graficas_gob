# barras_apiladas
import numpy as np

# Modularización total: toda la lógica se delega a helpers_barras y el flujo SVG centralizado siempre se ejecuta
import os
import matplotlib.pyplot as plt
from helpers_barras import (
    formato_fechas,
    get_text_color_for_bg,
    procesar_espaciado,
    cargar_fuentes,
    unir_barras,
    preparar_datos_barras,
    graficar_barras
)
def guardar_y_exportar_svg(fig, nombre, output_dir):
    import os
    import matplotlib.pyplot as plt
    os.makedirs(output_dir, exist_ok=True)
    nombre_archivo = f"{nombre or 'barras_verticales'}.svg"
    ruta_temporal = os.path.join(output_dir, nombre_archivo)
    plt.savefig(ruta_temporal, format='svg', dpi=300, transparent=True)
    try:
        from svg_cleanup.flujo_exportacion import exportar_grafica
        archivo_final = exportar_grafica(ruta_temporal, nombre or 'barras_verticales', output_dir)
        if archivo_final and os.path.exists(ruta_temporal):
            os.remove(ruta_temporal)
    except ImportError:
        print("Nota: Módulo de exportación no disponible. Se guardará el SVG sin optimizar.")
    except Exception as e:
        print(f"Advertencia: Error en el flujo de exportación: {e}")

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
    output_dir="output",
    desplazamiento_capsula=0.03,
    **kwargs
):
    """
    Gráfica de barras flexible (vertical u horizontal) con helpers y flujo SVG centralizado SIEMPRE activo.
    """
    # 1. Procesar espaciado y fuentes
    bar_height, aumenta_alto_fig, aumenta_ancho_fig, aumenta_sep_leyenda = procesar_espaciado(
        kwargs, bar_height, aumenta_alto_fig, aumenta_ancho_fig, aumenta_sep_leyenda
    )
    cargar_fuentes()

    # 2. Procesar y preparar datos (modularizado)
    datos = preparar_datos_barras(
        df_wide=df_wide,
        nombre=nombre,
        union_izquierda=union_izquierda,
        union_derecha=union_derecha,
        agregar_datos=agregar_datos,
        asignar_etiquetas=asignar_etiquetas,
        ordenar_por=ordenar_por,
        orden=orden,
        sustituir_etiquetas=sustituir_etiquetas,
        kwargs=kwargs
    )
    # datos es un dict con todo lo necesario para graficar
    fig, ax = graficar_barras(
        datos=datos,
        font=font,
        fontsize_barra=fontsize_barra,
        fontsize_valor_total=fontsize_valor_total,
        bar_height=bar_height,
        bar_height_override=bar_height_override,
        aumenta_ancho_fig=aumenta_ancho_fig,
        aumenta_alto_fig=aumenta_alto_fig,
        orientacion=orientacion,
        aumenta_sep_leyenda=aumenta_sep_leyenda,
        valor_barra=valor_barra,
        valor_total=valor_total,
        porcentaje_barra=porcentaje_barra,
        porcentaje_divergente=porcentaje_divergente,
        porcentaje_total=porcentaje_total,
        porcentaje_total_inicio=porcentaje_total_inicio,
        ordenar_por=ordenar_por,
        orden=orden,
        quitar_capsula=quitar_capsula,
        area_min=area_min,
        espacio_inicio=espacio_inicio,
        paleta_colores=paleta_colores,
        color_valor_barra=color_valor_barra,
        grillas=grillas,
        leyenda=leyenda,
        posicion_leyenda=posicion_leyenda,
        separar_por_total=separar_por_total,
        y_limits=y_limits,
        nombre_eje_x=nombre_eje_x,
        nombre_eje_y=nombre_eje_y,
        resaltar_etiquetas=resaltar_etiquetas,
        porcentaje_abajo=porcentaje_abajo,
        orientacion_etiqueta_x=orientacion_etiqueta_x,
        altura_min=altura_min,
        ejeY_negativo_a_positivo=ejeY_negativo_a_positivo,
        capsulas_cero=capsulas_cero,
        ncol_leyenda=ncol_leyenda,
        desplazamiento_capsula=desplazamiento_capsula,
        output_dir=output_dir,
        kwargs=kwargs
    )

    # 3. Guardar SVG y aplicar flujo SVG centralizado SIEMPRE
    guardar_y_exportar_svg(fig, nombre, output_dir)
    plt.show()