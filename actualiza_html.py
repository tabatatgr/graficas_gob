import nbformat
import re
import os

def extrae_codigo_py_r(ruta):
    with open(ruta, encoding="utf-8") as f:
        return f.read()

def extrae_codigo_ipynb(ruta, marcador):
    with open(ruta, encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)
    for cell in nb.cells:
        if cell.cell_type == "code" and cell.source.strip().startswith(f"# EXPORTAR: {marcador}"):
            return cell.source
    raise ValueError(f"No se encontró la celda con el marcador {marcador} en {ruta}")

# Mapea identificadores a rutas y tipo de archivo
bloques = {
    #"verticales": {"ruta": "Python/barras apiladas verticales/barras_apiladas_verticales.py", "tipo": "py"},
    #"ejemplo_r": {"ruta": "R/ejemplo.R", "tipo": "r"},
    #"notebook_celda": {"ruta": "notebooks/ejemplo.ipynb", "tipo": "ipynb"},
    "barras_agrupadas_y_apiladas": {"ruta": "Python/agrupadasyapiladas/agrupadasyapiladas.ipynb", "tipo": "ipynb"},
    "areaplot": {"ruta": "Python/areaplot/areaplot.ipynb", "tipo": "ipynb"},
    "areaplot2": {"ruta": "Python/areaplot2/areaplot2.ipynb", "tipo": "ipynb"},
    "linea": {"ruta": "Python/linea/linea.ipynb", "tipo": "ipynb"},
    "treemap": {"ruta": "Python/treemap/treemap.ipynb", "tipo": "ipynb"},
    "barras_apiladas": {"ruta": "Python/barras_apiladas/barras_apiladas.ipynb", "tipo": "ipynb"},
    "barras_verticales_simples": {"ruta": "Python/barras_apiladas/barras_apiladas.ipynb", "tipo": "ipynb"},
    "barras_horizontales_simples": {"ruta": "Python/barras_apiladas/barras_apiladas.ipynb", "tipo": "ipynb"},
    "barra_previa": {"ruta": "Python/barras_apiladas/barras_apiladas.ipynb", "tipo": "ipynb"},
    "union_barras_izquierda": {"ruta": "Python/barras_apiladas/barras_apiladas.ipynb", "tipo": "ipynb"},
    "union_barras_derecha": {"ruta": "Python/barras_apiladas/barras_apiladas.ipynb", "tipo": "ipynb"},
    "sustitucion_etiquetas": {"ruta": "Python/barras_apiladas/barras_apiladas.ipynb", "tipo": "ipynb"},
    "espacio_entre_barras": {"ruta": "Python/barras_apiladas/barras_apiladas.ipynb", "tipo": "ipynb"},
    "porcentaje_inicio": {"ruta": "Python/barras_apiladas/barras_apiladas.ipynb", "tipo": "ipynb"},
    "resaltar_etiquetas": {"ruta": "Python/barras_apiladas/barras_apiladas.ipynb", "tipo": "ipynb"},
    "barras_porcentaje": {"ruta": "Python/barras_apiladas/barras_apiladas.ipynb", "tipo": "ipynb"},
    "barras_apiladas_con_ceros": {"ruta": "Python/barras_apiladas/barras_apiladas.ipynb", "tipo": "ipynb"},
    # Agrega más bloques aquí
}

with open("graficas-python.html", encoding="utf-8") as f:
    html = f.read()

for bloque, info in bloques.items():
    ruta = info["ruta"]
    tipo = info["tipo"]
    if tipo == "py" or tipo == "r":
        codigo = extrae_codigo_py_r(ruta)
    elif tipo == "ipynb":
        codigo = extrae_codigo_ipynb(ruta, bloque)
    else:
        raise ValueError(f"Tipo de archivo no soportado: {tipo}")
    # Escapa el código para HTML
    codigo_html = codigo.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    # Selecciona el lenguaje para el bloque <code>
    lang = "r" if tipo == "r" else "python"
    patron = re.compile(
        rf"(<!-- INICIO_CODIGO:{bloque} -->)(.*?)(<!-- FIN_CODIGO:{bloque} -->)",
        re.DOTALL
    )
    def reemplazo(match):
        return f"{match.group(1)}\n<pre><code class=\"language-{lang}\">\n{codigo_html}\n</code></pre>\n{match.group(3)}"
    html = patron.sub(reemplazo, html)

with open("graficas-python.html", "w", encoding="utf-8") as f:
    f.write(html)