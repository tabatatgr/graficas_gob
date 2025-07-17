"""
Flujo para exportar gráficas correctamente
Este flujo permite convertir visualizaciones generadas automáticamente en gráficos listos 
para ser editados visualmente en herramientas como Figma, manteniendo la estructura 
semántica de los elementos y optimizando el archivo para su uso en diseño.

Proceso:
1. Optimización SVGO
2. Limpieza Scour
3. Asignación semántica de capas
4. Compatibilidad Figma
5. Exportación final
"""

import os
import subprocess
import xml.etree.ElementTree as ET
import re
from pathlib import Path

class FlujoDeLimpieza:
    """Clase principal para el flujo de limpieza de SVG"""
    
    def __init__(self, output_dir="output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def procesar_svg(self, svg_original, nombre_base):
        """
        Procesa un SVG siguiendo el flujo completo de exportación
        
        Args:
            svg_original (str): Ruta al archivo SVG original
            nombre_base (str): Nombre base para los archivos de salida
            
        Returns:
            str: Ruta al archivo SVG final optimizado para Figma
        """
        print(f"Iniciando flujo de exportación para: {nombre_base}")
        
        try:
            # Paso 1: Optimización SVGO (primero limpiar el archivo "sucio")
            print("Optimizando con SVGO...")
            svgo_file = self._optimizar_svgo(svg_original, nombre_base)
            
            # Paso 2: Limpieza Scour (limpieza profunda)
            print("Limpiando con Scour...")
            scour_file = self._limpiar_scour(svgo_file, nombre_base)
            
            # Paso 3: Asignación semántica (después de optimizar)
            print("Asignando IDs semánticos...")
            semantico_file = self._asignar_ids_semanticos(scour_file, nombre_base)
            
            # Paso 4: Compatibilidad Figma
            print("Preparando para Figma...")
            figma_file = self._preparar_figma(semantico_file, nombre_base)
            
            # Paso 5: Limpiar archivos intermedios
            self._limpiar_archivos_intermedios([svgo_file, scour_file, semantico_file])
            
            print(f"Flujo completado exitosamente: {figma_file}")
            return figma_file
            
        except Exception as e:
            print(f"Error en el flujo: {e}")
            return None
    
    def _asignar_ids_semanticos(self, svg_original, nombre_base):
        """Paso 3: Asignar identificadores descriptivos e inteligentes a elementos clave"""
        output_file = self.output_dir / f"{nombre_base}_semantico.svg"
        
        try:
            # Registrar namespaces para evitar prefijos ns0:
            ET.register_namespace('', 'http://www.w3.org/2000/svg')
            ET.register_namespace('xlink', 'http://www.w3.org/1999/xlink')
            
            # Parsear el SVG
            tree = ET.parse(svg_original)
            root = tree.getroot()
            
            # Contadores para diferentes tipos de elementos
            contadores = {
                'bar': 0, 'line': 0, 'point': 0, 'label': 0, 'tick': 0, 
                'axis': 0, 'legend': 0, 'grid': 0, 'background': 0, 
                'title': 0, 'annotation': 0, 'area': 0, 'treemap': 0
            }
            
            # Set para evitar IDs duplicados
            used_ids = set()
            
            # Registrar IDs existentes
            for elem in root.iter():
                existing_id = elem.get('id')
                if existing_id:
                    used_ids.add(existing_id)
            
            # Recorrer todos los elementos y asignar IDs semánticos detallados
            for elem in root.iter():
                # Saltar si ya tiene ID
                if elem.get('id'):
                    continue
                    
                tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
                semantic_id = None
                element_class = None
                
                if tag == 'text':
                    semantic_id, element_class = self._asignar_id_texto(elem, contadores, used_ids)
                
                elif tag == 'rect':
                    semantic_id, element_class = self._asignar_id_rectangulo(elem, contadores, used_ids)
                
                elif tag == 'line':
                    semantic_id, element_class = self._asignar_id_linea(elem, contadores, used_ids)
                
                elif tag == 'path':
                    semantic_id, element_class = self._asignar_id_path(elem, contadores, used_ids)
                
                elif tag == 'circle':
                    semantic_id, element_class = self._asignar_id_circulo(elem, contadores, used_ids)
                
                elif tag == 'g':
                    semantic_id, element_class = self._asignar_id_grupo(elem, contadores, used_ids)
                
                # Asignar ID y clase si se determinó
                if semantic_id:
                    elem.set('id', semantic_id)
                    used_ids.add(semantic_id)
                    
                    if element_class:
                        current_class = elem.get('class', '')
                        if current_class:
                            elem.set('class', f"{current_class} {element_class}")
                        else:
                            elem.set('class', element_class)
            
            # Guardar el archivo con IDs semánticos
            tree.write(output_file, encoding='utf-8', xml_declaration=True)
            
            print(f"   IDs semánticos detallados asignados: {output_file}")
            print(f"     - Títulos: {contadores['title']}, Barras: {contadores['bar']}, Ejes: {contadores['axis']}")
            print(f"     - Etiquetas: {contadores['label']}, Líneas: {contadores['line']}, Áreas: {contadores['area']}")
            return str(output_file)
            
        except Exception as e:
            print(f"   Error al asignar IDs semánticos: {e}")
            return svg_original
    
    def _limpiar_texto(self, texto):
        """Limpia texto para usar en IDs"""
        if not texto:
            return ""
        # Limpiar y normalizar texto
        texto_limpio = texto.strip()[:25]  # Máximo 25 caracteres
        texto_limpio = re.sub(r'[^\w\s-]', '', texto_limpio)  # Solo letras, números, espacios y guiones
        texto_limpio = re.sub(r'\s+', '-', texto_limpio)  # Espacios a guiones
        texto_limpio = texto_limpio.lower()
        return texto_limpio
    
    def _asegurar_id_unico(self, base_id, used_ids):
        """Asegura que el ID sea único"""
        if base_id not in used_ids:
            return base_id
        
        counter = 1
        while f"{base_id}-{counter}" in used_ids:
            counter += 1
        
        return f"{base_id}-{counter}"
    
    def _extraer_tamaño_fuente(self, elem):
        """Extrae el tamaño de fuente de un elemento"""
        font_size = elem.get('font-size', '12')
        style = elem.get('style', '')
        
        # Buscar font-size en style
        font_size_match = re.search(r'font-size:\s*(\d+(?:\.\d+)?)', style)
        if font_size_match:
            font_size = font_size_match.group(1)
        
        try:
            return float(font_size)
        except ValueError:
            return 12
    
    def _obtener_contenido_texto(self, elem):
        """Obtiene el contenido de texto de un elemento"""
        texto = elem.text or ''
        if not texto:
            # Buscar en elementos hijos
            for child in elem:
                if child.text:
                    texto = child.text
                    break
        return texto.strip()
    
    def _asignar_id_texto(self, elem, contadores, used_ids):
        """Asigna ID semántico a elementos de texto"""
        texto = self._obtener_contenido_texto(elem)
        font_size = self._extraer_tamaño_fuente(elem)
        
        # Determinar tipo de texto
        if font_size > 20:  # Títulos
            contadores['title'] += 1
            if texto:
                texto_limpio = self._limpiar_texto(texto)
                if texto_limpio:
                    semantic_id = f"titulo-{texto_limpio}"
                else:
                    semantic_id = f"titulo-{contadores['title']}"
            else:
                semantic_id = f"titulo-{contadores['title']}"
            element_class = 'title-element'
        
        elif texto and texto.replace(',', '').replace('.', '').replace('%', '').replace('-', '').replace(' ', '').isdigit():
            # Valores numéricos
            contadores['label'] += 1
            texto_limpio = self._limpiar_texto(texto)
            semantic_id = f"valor-{texto_limpio}" if texto_limpio else f"valor-{contadores['label']}"
            element_class = 'value-element'
        
        else:
            # Etiquetas regulares
            contadores['label'] += 1
            if texto:
                texto_limpio = self._limpiar_texto(texto)
                if texto_limpio:
                    semantic_id = f"etiqueta-{texto_limpio}"
                else:
                    semantic_id = f"etiqueta-{contadores['label']}"
            else:
                semantic_id = f"texto-{contadores['label']}"
            element_class = 'label-element'
        
        return self._asegurar_id_unico(semantic_id, used_ids), element_class
    
    def _asignar_id_rectangulo(self, elem, contadores, used_ids):
        """Asigna ID semántico a elementos rectangulares"""
        try:
            width = float(elem.get('width', 0))
            height = float(elem.get('height', 0))
            fill = elem.get('fill', '')
            stroke = elem.get('stroke', '')
            
            # Detectar tipo de rectángulo
            if width > 10 and height > 10:  # Tamaño mínimo para barra
                if fill != 'none' and stroke != 'none':
                    # Probablemente treemap
                    contadores['treemap'] += 1
                    semantic_id = f"treemap-rect-{contadores['treemap']}"
                    element_class = 'treemap-element'
                else:
                    # Barra regular
                    contadores['bar'] += 1
                    if width > height:  # Barra horizontal
                        semantic_id = f"barra-horizontal-{contadores['bar']}"
                    else:  # Barra vertical
                        semantic_id = f"barra-vertical-{contadores['bar']}"
                    element_class = 'bar-element'
            else:
                # Elemento de grid o decorativo
                contadores['grid'] += 1
                semantic_id = f"grid-{contadores['grid']}"
                element_class = 'grid-element'
            
            return self._asegurar_id_unico(semantic_id, used_ids), element_class
            
        except ValueError:
            contadores['bar'] += 1
            return self._asegurar_id_unico(f"rect-{contadores['bar']}", used_ids), 'rect-element'
    
    def _asignar_id_linea(self, elem, contadores, used_ids):
        """Asigna ID semántico a elementos de línea"""
        try:
            x1, y1 = float(elem.get('x1', 0)), float(elem.get('y1', 0))
            x2, y2 = float(elem.get('x2', 0)), float(elem.get('y2', 0))
            
            # Calcular longitud y orientación
            length = ((x2-x1)**2 + (y2-y1)**2)**0.5
            
            # Detectar tipo de línea
            if length > 100:  # Líneas largas probablemente son ejes
                contadores['axis'] += 1
                if abs(y2-y1) < 5:  # Línea horizontal = eje X
                    semantic_id = f"eje-x-{contadores['axis']}"
                elif abs(x2-x1) < 5:  # Línea vertical = eje Y
                    semantic_id = f"eje-y-{contadores['axis']}"
                else:
                    semantic_id = f"eje-{contadores['axis']}"
                element_class = 'axis-element'
            else:
                # Líneas cortas probablemente son ticks o grid
                contadores['tick'] += 1
                semantic_id = f"tick-{contadores['tick']}"
                element_class = 'tick-element'
            
            return self._asegurar_id_unico(semantic_id, used_ids), element_class
            
        except ValueError:
            contadores['line'] += 1
            return self._asegurar_id_unico(f"linea-{contadores['line']}", used_ids), 'line-element'
    
    def _asignar_id_path(self, elem, contadores, used_ids):
        """Asigna ID semántico a elementos path"""
        d_attr = elem.get('d', '')
        fill = elem.get('fill', '')
        stroke = elem.get('stroke', '')
        
        # Detectar tipo de path
        if 'Z' in d_attr and fill != 'none':  # Forma cerrada con relleno
            contadores['area'] += 1
            semantic_id = f"area-{contadores['area']}"
            element_class = 'area-element'
        elif d_attr.count('L') > 5 or d_attr.count('C') > 3:  # Línea compleja
            contadores['line'] += 1
            semantic_id = f"linea-datos-{contadores['line']}"
            element_class = 'line-plot-element'
        else:
            # Path genérico
            contadores['line'] += 1
            semantic_id = f"path-{contadores['line']}"
            element_class = 'path-element'
        
        return self._asegurar_id_unico(semantic_id, used_ids), element_class
    
    def _asignar_id_circulo(self, elem, contadores, used_ids):
        """Asigna ID semántico a elementos circulares"""
        contadores['point'] += 1
        semantic_id = f"punto-{contadores['point']}"
        element_class = 'point-element'
        return self._asegurar_id_unico(semantic_id, used_ids), element_class
    
    def _asignar_id_grupo(self, elem, contadores, used_ids):
        """Asigna ID semántico a grupos"""
        children = list(elem)
        if not children:
            return None, None
        
        # Analizar contenido del grupo
        child_tags = [child.tag.split('}')[-1] if '}' in child.tag else child.tag for child in children]
        
        if 'rect' in child_tags:
            semantic_id = 'grupo-barras'
            element_class = 'bars-container'
        elif 'text' in child_tags:
            semantic_id = 'grupo-etiquetas'
            element_class = 'labels-container'
        elif 'line' in child_tags:
            semantic_id = 'grupo-ejes'
            element_class = 'axes-container'
        elif 'path' in child_tags:
            semantic_id = 'grupo-lineas'
            element_class = 'lines-container'
        else:
            contadores['legend'] += 1
            semantic_id = f"grupo-{contadores['legend']}"
            element_class = 'group-element'
        
        return self._asegurar_id_unico(semantic_id, used_ids), element_class
    
    def _optimizar_svgo(self, svg_file, nombre_base):
        """Paso 1: Optimización SVGO básica"""
        output_file = self.output_dir / f"{nombre_base}_svgo.svg"
        
        try:
            comando = [
                "svgo",
                svg_file,
                "-o", str(output_file),
                "--multipass",
                "--pretty"
            ]
            
            subprocess.run(comando, capture_output=True, text=True, check=True, shell=True)
            print(f"   SVGO completado: {output_file}")
            return str(output_file)
            
        except subprocess.CalledProcessError as e:
            print(f"   Error en SVGO: {e}")
            return svg_file
    
    def _limpiar_scour(self, svg_file, nombre_base):
        """Paso 2: Limpieza Scour profunda"""
        output_file = self.output_dir / f"{nombre_base}_scour.svg"
        
        try:
            comando = [
                "scour",
                "-i", svg_file,
                "-o", str(output_file),
                "--enable-viewboxing",
                "--enable-id-stripping",
                "--shorten-ids",
                "--remove-descriptive-elements",
                "--strip-xml-prolog",
                "--remove-metadata",
                "--indent=space",
                "--nindent=2"
            ]
            
            subprocess.run(comando, capture_output=True, text=True, check=True, shell=True)
            print(f"   Scour completado: {output_file}")
            return str(output_file)
            
        except subprocess.CalledProcessError as e:
            print(f"   Error en Scour: {e}")
            return svg_file
    
    def _preparar_figma(self, svg_file, nombre_base):
        """Paso 4: Preparar SVG para compatibilidad con Figma"""
        output_file = self.output_dir / f"{nombre_base}_figma.svg"
        
        try:
            with open(svg_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Limpiezas específicas para Figma
            content = self._limpiar_para_figma(content)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"   SVG optimizado para Figma: {output_file}")
            return str(output_file)
            
        except Exception as e:
            print(f"   Error al preparar para Figma: {e}")
            return svg_file
    
    def _limpiar_para_figma(self, content):
        """Aplica limpiezas específicas para Figma"""
        
        # Eliminar comentarios XML
        content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
        
        # Asegurar que el viewBox esté presente
        if 'viewBox=' not in content and 'width=' in content and 'height=' in content:
            width_match = re.search(r'width="([^"]*)"', content)
            height_match = re.search(r'height="([^"]*)"', content)
            if width_match and height_match:
                width = width_match.group(1)
                height = height_match.group(1)
                content = content.replace('<svg', f'<svg viewBox="0 0 {width} {height}"')
        
        # Arreglar namespaces problemáticos
        content = self._arreglar_namespaces(content)
        
        # Limpiar atributos problemáticos para Figma
        problematic_attrs = [
            'data-.*?="[^"]*"',  # Atributos data-*
            'xml:space="[^"]*"',  # Atributos xml:space
        ]
        
        for pattern in problematic_attrs:
            content = re.sub(pattern, '', content)
        
        # Formatear el SVG para mejor legibilidad
        content = self._formatear_svg(content)
        
        return content
    
    def _formatear_svg(self, content):
        """Formatea el SVG para mejor legibilidad"""
        
        # Agregar saltos de línea después de elementos principales
        content = re.sub(r'(<svg[^>]*>)', r'\1\n', content)
        content = re.sub(r'(<defs[^>]*>)', r'\n\1\n', content)
        content = re.sub(r'(</defs>)', r'\n\1\n', content)
        content = re.sub(r'(<g[^>]*>)', r'\n\1\n', content)
        content = re.sub(r'(</g>)', r'\n\1\n', content)
        content = re.sub(r'(<path[^>]*/>)', r'\n\1\n', content)
        content = re.sub(r'(<text[^>]*>)', r'\n\1', content)
        content = re.sub(r'(</text>)', r'\1\n', content)
        content = re.sub(r'(<use[^>]*/>)', r'\n\1\n', content)
        content = re.sub(r'(</svg>)', r'\n\1', content)
        
        # Limpiar múltiples saltos de línea
        content = re.sub(r'\n\n+', '\n\n', content)
        
        # Normalizar espacios en líneas individuales
        lines = content.split('\n')
        formatted_lines = []
        for line in lines:
            # Mantener la estructura pero limpiar espacios excesivos
            line = re.sub(r'\s+', ' ', line.strip())
            if line:
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
    def _arreglar_namespaces(self, content):
        """Arregla problemas de namespaces en el SVG"""
        
        # Buscar el tag svg inicial
        svg_match = re.search(r'<svg[^>]*>', content)
        if not svg_match:
            return content
        
        svg_tag = svg_match.group(0)
        
        # Asegurar que los namespaces necesarios estén declarados
        # Pero solo si se usan en el documento
        if 'xlink:href' in content:
            if 'xmlns:xlink' not in svg_tag:
                svg_tag = svg_tag.replace('<svg', '<svg xmlns:xlink="http://www.w3.org/1999/xlink"')
        
        # Asegurar namespace SVG principal
        if 'xmlns=' not in svg_tag:
            svg_tag = svg_tag.replace('<svg', '<svg xmlns="http://www.w3.org/2000/svg"')
        
        # Reemplazar el tag svg original
        content = content.replace(svg_match.group(0), svg_tag)
        
        # Convertir xlink:href a href para compatibilidad moderna
        # Pero mantener xlink:href si es necesario para compatibilidad
        content = re.sub(r'xlink:href=', 'href=', content)
        
        # Eliminar namespaces duplicados o problemáticos
        content = re.sub(r'xmlns:xlink="[^"]*"\s*xmlns:xlink="[^"]*"', 'xmlns:xlink="http://www.w3.org/1999/xlink"', content)
        
        return content
    
    def _limpiar_archivos_intermedios(self, archivos):
        """Elimina archivos intermedios del proceso"""
        for archivo in archivos:
            if archivo and os.path.exists(archivo):
                try:
                    os.remove(archivo)
                except:
                    pass  # Ignorar errores al limpiar
    
    def verificar_herramientas(self):
        """Verifica que las herramientas necesarias estén disponibles"""
        herramientas = {
            'svgo': 'npm install -g svgo',
            'scour': 'pip install scour'
        }
        
        disponibles = {}
        print("Verificando herramientas necesarias:")
        
        for herramienta, instalacion in herramientas.items():
            try:
                subprocess.run([herramienta, '--version'], 
                             capture_output=True, text=True, check=True, shell=True)
                disponibles[herramienta] = True
                print(f"   {herramienta} disponible")
            except:
                disponibles[herramienta] = False
                print(f"    {herramienta} no disponible. Instalar con: {instalacion}")
        
        return all(disponibles.values())


def exportar_grafica(svg_original, nombre_base, output_dir="output"):
    """
    Función principal para exportar una gráfica usando el flujo completo
    
    Args:
        svg_original (str): Ruta al archivo SVG original
        nombre_base (str): Nombre base para los archivos de salida
        output_dir (str): Directorio de salida
        
    Returns:
        str: Ruta al archivo SVG final optimizado para Figma
    """
    flujo = FlujoDeLimpieza(output_dir)
    
    if not flujo.verificar_herramientas():
        print(" No se pueden ejecutar todas las herramientas necesarias")
        return None
    
    return flujo.procesar_svg(svg_original, nombre_base)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python flujo_exportacion.py <archivo_svg> [nombre_base] [directorio_salida]")
        sys.exit(1)
    
    svg_file = sys.argv[1]
    nombre = sys.argv[2] if len(sys.argv) > 2 else Path(svg_file).stem
    output_dir = sys.argv[3] if len(sys.argv) > 3 else "output"
    
    resultado = exportar_grafica(svg_file, nombre, output_dir)
    
    if resultado:
        print(f" Exportación completada: {resultado}")
    else:
        print(" Error en la exportación")
