import nbformat
import re
import os
from config_graficas import CONFIGURACION_SITIO

def extrae_codigo_ipynb(ruta_notebook, marcador):
    """Extrae el código de una celda específica de un notebook."""
    try:
        with open(ruta_notebook, encoding="utf-8") as f:
            nb = nbformat.read(f, as_version=4)
        for cell in nb.cells:
            if cell.cell_type == "code" and cell.source.strip().startswith(f"# EXPORTAR: {marcador}"):
                return cell.source
        print(f"ADVERTENCIA: No se encontró el marcador '{marcador}' en {ruta_notebook}")
        return None
    except FileNotFoundError:
        print(f"ERROR: No se encontró el archivo de notebook: {ruta_notebook}")
        return None

def generar_sitio(config, plantilla_path):
    """Genera todas las páginas de detalle y actualiza los catálogos."""
    try:
        with open(plantilla_path, 'r', encoding='utf-8') as f:
            plantilla = f.read()
    except FileNotFoundError:
        print(f"ERROR: No se encontró el archivo de plantilla: {plantilla_path}")
        return

    for categoria, datos_categoria in config.items():
        print(f"\nProcesando categoría: {categoria}...")
        
        # 1. Generar páginas de detalle para la categoría
        output_dir = datos_categoria['output_dir']
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for nombre_grafica, info_grafica in datos_categoria['graficas'].items():
            codigo_python = extrae_codigo_ipynb(datos_categoria['notebook_path'], info_grafica['marcador'])
            if not codigo_python:
                continue

            codigo_html_escaped = codigo_python.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            
            contenido_final = plantilla.replace("{{TITULO_GRAFICA}}", info_grafica['titulo'])
            contenido_final = contenido_final.replace("{{RUTA_IMAGEN}}", f"../{info_grafica['ruta_img']}")
            contenido_final = contenido_final.replace("{{CODIGO_PYTHON}}", codigo_html_escaped)
            contenido_final = contenido_final.replace("{{VOLVER_HREF}}", f"../{datos_categoria['catalogo_html_path']}")
            contenido_final = contenido_final.replace("{{VOLVER_TEXTO}}", f"Volver a {categoria.replace('_', ' ').title()}")

            ruta_salida = os.path.join(output_dir, f"{nombre_grafica}.html")
            with open(ruta_salida, 'w', encoding='utf-8') as f:
                f.write(contenido_final)
            # print(f"  - Creado: {ruta_salida}")

        # 2. Actualizar enlaces en el archivo de catálogo correspondiente
        catalogo_path = datos_categoria['catalogo_html_path']
        try:
            with open(catalogo_path, 'r', encoding='utf-8') as f:
                html_catalogo = f.read()
        except FileNotFoundError:
            print(f"ADVERTENCIA: No se encontró el archivo de catálogo: {catalogo_path}. Saltando actualización de enlaces.")
            continue

        for nombre_grafica, info_grafica in datos_categoria['graficas'].items():
            patron = re.compile(rf'(<a href=")[^"]*(".*?<img src="{info_grafica["ruta_img"]}".*?</a>)', re.DOTALL)
            ruta_detalle_rel = os.path.join(output_dir, f"{nombre_grafica}.html").replace("\\", "/")
            html_catalogo = patron.sub(rf'\g<1>{ruta_detalle_rel}\g<2>', html_catalogo)
        
        with open(catalogo_path, 'w', encoding='utf-8') as f:
            f.write(html_catalogo)
        print(f"Catálogo actualizado: {catalogo_path}")

# --- EJECUCIÓN ---
if __name__ == "__main__":
    PLANTILLA_PATH = "plantilla_detalle.html" # La misma plantilla para todos
    generar_sitio(CONFIGURACION_SITIO, PLANTILLA_PATH)
    print("\n¡Proceso completado!")