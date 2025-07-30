import matplotlib.pyplot as plt

def ajusta_etiquetas(
    dataframe, 
    columnas, 
    colores, 
    columna_x, 
    sin_tag=2, 
    max=True, 
    fontsize=16, 
    fontname=None,
    fontweight=None,
    fontcolor=None,
    escala=None
):
    """
    Devuelve la lista de textos a etiquetar, pero NO llama a adjust_text.
    Uso genérico para cualquier gráfico multilineas.
    """
    texts = []
    for col, color in zip(columnas, colores):
        total_puntos = len(dataframe)
        max_index = dataframe[col].idxmax() if max else None
        for i, row in dataframe.iterrows():
            tiene_etiqueta = (total_puntos - i - 1) % (sin_tag + 1) == 0 or i == total_puntos - 1 or (max and i == max_index)
            if tiene_etiqueta:
                bbox_props = dict(boxstyle="round,pad=0.25,rounding_size=0.99", fc=color, ec="none", alpha=1.0)
                espacio = "\u00A0"
                va = 'bottom' if i % 2 == 0 else 'top'
                offset = escala if va == 'bottom' else -escala
                texts.append(
                    plt.text(
                        row[columna_x], 
                        row[col] + offset,
                        f"{espacio*1}{int(row[col]):,}{espacio*1}",
                        fontsize=fontsize, 
                        color=fontcolor if fontcolor else "white",
                        weight=fontweight,
                        ha='center', 
                        va=va, 
                        bbox=bbox_props,
                        fontname=fontname
                    )
                )
    return texts
