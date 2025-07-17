#!/usr/bin/env python3
"""
Inicializador de proyectos para el workflow de gráficas
Crea la estructura de carpetas y archivos necesarios para un nuevo proyecto
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
import yaml

class InicializadorProyecto:
    def __init__(self, directorio_base: str = "proyectos"):
        """
        Inicializa el creador de proyectos
        
        Args:
            directorio_base: Directorio donde se crearán los proyectos
        """
        self.directorio_base = Path(directorio_base)
        self.directorio_recetas_central = Path("recetas_centrales")
        
    def crear_estructura_proyecto(self, nombre_proyecto: str) -> str:
        """
        Crea la estructura completa de un nuevo proyecto
        
        Args:
            nombre_proyecto: Nombre del proyecto
            
        Returns:
            Ruta al directorio del proyecto creado
        """
        # Crear directorio del proyecto
        directorio_proyecto = self.directorio_base / nombre_proyecto
        directorio_proyecto.mkdir(parents=True, exist_ok=True)
        
        print(f"Creando proyecto: {nombre_proyecto}")
        print(f"Directorio: {directorio_proyecto}")
        
        # Crear estructura de carpetas
        carpetas = [
            "input",
            "output", 
            "temp",
            "docs"
        ]
        
        for carpeta in carpetas:
            (directorio_proyecto / carpeta).mkdir(exist_ok=True)
            print(f"✓ Creada carpeta: {carpeta}/")
        
        self._crear_archivo_config(directorio_proyecto, nombre_proyecto)
        self._crear_readme_proyecto(directorio_proyecto, nombre_proyecto)
        self._crear_gitignore(directorio_proyecto)
        
        # Crear archivo de ejemplo de datos
        self._crear_ejemplo_datos(directorio_proyecto)
        
        # Crear scripts de proyecto
        self._crear_scripts_proyecto(directorio_proyecto, nombre_proyecto)
        
        print(f"✓ Proyecto '{nombre_proyecto}' creado exitosamente")
        return str(directorio_proyecto)
    
    def _crear_archivo_config(self, directorio_proyecto: Path, nombre_proyecto: str):
        """Crea archivo de configuración del proyecto"""
        config = {
            'proyecto': {
                'nombre': nombre_proyecto,
                'fecha_creacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'version': '1.0.0',
                'descripcion': f'Proyecto de gráficas: {nombre_proyecto}',
            },
            'directorios': {
                'input': 'input',
                'output': 'output',
                'recetas_centrales': '../recetas_centrales',
                'temp': 'temp'
            },
            'configuracion_graficas': {
                'formato_salida': 'svg',
                'optimizacion_svg': True,
                'generar_png': False,
                'generar_catalogo': True
            },
            'equipo': {
                'responsable': '',
                'colaboradores': [],
                'contacto': ''
            }
        }
        
        archivo_config = directorio_proyecto / "config_proyecto.yaml"
        with open(archivo_config, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        
        print(f"✓ Creado: config_proyecto.yaml")
    
    def _crear_readme_proyecto(self, directorio_proyecto: Path, nombre_proyecto: str):
        """Crea el README del proyecto"""
        readme_content = f"""# Proyecto: {nombre_proyecto}

## Descripción
Este proyecto contiene las gráficas y visualizaciones para: {nombre_proyecto}

## Estructura del Proyecto

```
{nombre_proyecto}/
├── input/              # Archivos de datos de entrada
├── output/             # Gráficas generadas (SVG/PNG)
├── temp/               # Archivos temporales
├── docs/               # Documentación del proyecto
├── config_proyecto.yaml # Configuración del proyecto
├── generar_graficas.py # Script para generar todas las gráficas
├── generar_catalogo.py # Script para generar el catálogo Excel
└── resumen.xlsx        # Catálogo técnico del proyecto
```

## Uso

### 1. Colocar los datos
Guarda tus archivos de datos (.csv, .xlsx) en la carpeta `input/`.

### 2. Revisar recetas disponibles
Las recetas están en `../recetas_centrales/` - no se copian, se usan directamente.

### 3. Generar gráficas
```bash
python generar_graficas.py
```

### 4. Generar catálogo
```bash
python generar_catalogo.py
```

### 5. Editar en Figma
Los archivos SVG optimizados están listos para importar en Figma.

## Archivos Importantes

- `resumen.xlsx`: Catálogo técnico con información de todas las gráficas
- `config_proyecto.yaml`: Configuración general del proyecto
- `output/`: Carpeta con todos los archivos generados

## Notas para el Equipo

- Las recetas están centralizadas en `../recetas_centrales/`
- No copiar recetas localmente, usar las centrales
- Usar el catálogo Excel para tracking de cambios
- Los archivos SVG están optimizados para Figma
- Mantener la estructura de carpetas intacta

---
Generado automáticamente el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        archivo_readme = directorio_proyecto / "README.md"
        with open(archivo_readme, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print(f"✓ Creado: README.md")
    
    def _crear_gitignore(self, directorio_proyecto: Path):
        """Crea archivo .gitignore para el proyecto"""
        gitignore_content = """# Archivos temporales
temp/
*.tmp
*.temp

# Archivos de sistema
.DS_Store
Thumbs.db

# Archivos de Python
__pycache__/
*.pyc
*.pyo
*.pyd

# Archivos de Excel temporales
~$*.xlsx
~$*.xls

# Logs
*.log

# Archivos de respaldo
*.bak
*.backup

# Archivos de configuración local
.env
.vscode/settings.json
"""
        
        archivo_gitignore = directorio_proyecto / ".gitignore"
        with open(archivo_gitignore, 'w', encoding='utf-8') as f:
            f.write(gitignore_content)
        
        print(f"✓ Creado: .gitignore")
    
    def _copiar_recetas_centrales(self, directorio_proyecto: Path):
        """Copia las recetas centrales al proyecto"""
        if not self.directorio_recetas_central.exists():
            print("⚠ No se encontraron recetas centrales")
            return
        
        directorio_recetas = directorio_proyecto / "recetas"
        
        try:
            # Copiar todos los archivos YAML
            for archivo_yaml in self.directorio_recetas_central.glob("*.yaml"):
                shutil.copy2(archivo_yaml, directorio_recetas)
                print(f"✓ Copiada receta: {archivo_yaml.name}")
            
            # Crear archivo de índice de recetas
            self._crear_indice_recetas(directorio_recetas)
            
        except Exception as e:
            print(f"⚠ Error copiando recetas: {e}")
    
    def _crear_indice_recetas(self, directorio_recetas: Path):
        """Crea un índice de las recetas disponibles"""
        indice = {
            'recetas_disponibles': [],
            'fecha_actualizacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'notas': [
                'Este archivo se genera automáticamente',
                'No editar manualmente',
                'Para actualizar recetas, sincronizar con el repositorio central'
            ]
        }
        
        for archivo_yaml in directorio_recetas.glob("*.yaml"):
            try:
                with open(archivo_yaml, 'r', encoding='utf-8') as f:
                    receta = yaml.safe_load(f)
                
                info_receta = {
                    'archivo': archivo_yaml.name,
                    'tipo_grafico': receta.get('tipo_grafico', 'desconocido'),
                    'nombre': receta.get('parametros', {}).get('nombre', ''),
                    'descripcion': receta.get('descripcion', ''),
                }
                
                indice['recetas_disponibles'].append(info_receta)
                
            except Exception as e:
                print(f"⚠ Error leyendo receta {archivo_yaml.name}: {e}")
        
        archivo_indice = directorio_recetas / "indice_recetas.yaml"
        with open(archivo_indice, 'w', encoding='utf-8') as f:
            yaml.dump(indice, f, default_flow_style=False, allow_unicode=True)
        
        print(f"✓ Creado: indice_recetas.yaml")
    
    def _crear_ejemplo_datos(self, directorio_proyecto: Path):
        """Crea un archivo de ejemplo de datos"""
        import pandas as pd
        
        # Crear datos de ejemplo más completos que funcionen con todas las gráficas
        datos_ejemplo = {
            # Columnas básicas para barras verticales
            'Categoria': ['Ventas', 'Marketing', 'Desarrollo', 'Soporte', 'Administración', 'Finanzas'],
            'Valor': [150000, 85000, 120000, 65000, 95000, 110000],
            
            # Columnas para series temporales
            'Fecha': ['2024-01', '2024-02', '2024-03', '2024-04', '2024-05', '2024-06'],
            'Mes': ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio'],
            'Año': [2024, 2024, 2024, 2024, 2024, 2024],
            
            # Columnas para agrupación
            'Tipo': ['Tipo A', 'Tipo B', 'Tipo A', 'Tipo B', 'Tipo A', 'Tipo B'],
            'Region': ['Norte', 'Sur', 'Centro', 'Norte', 'Sur', 'Centro'],
            'Producto': ['Producto 1', 'Producto 2', 'Producto 1', 'Producto 2', 'Producto 1', 'Producto 2'],
            
            # Valores adicionales para múltiples series
            'Valor_Anterior': [140000, 80000, 110000, 60000, 90000, 100000],
            'Objetivo': [160000, 90000, 130000, 70000, 100000, 120000],
            'Porcentaje': [85.5, 72.3, 91.2, 68.7, 78.9, 88.1],
            
            # Para treemap
            'Tamaño': [25, 18, 22, 15, 19, 21],
            'Jerarquia': ['Nivel 1', 'Nivel 2', 'Nivel 1', 'Nivel 2', 'Nivel 1', 'Nivel 2'],
        }
        
        # Crear DataFrame más extenso
        df_base = pd.DataFrame(datos_ejemplo)
        
        # Duplicar datos para tener más registros
        df_extendido = []
        regiones = ['Norte', 'Sur', 'Centro', 'Este', 'Oeste']
        años = [2022, 2023, 2024]
        
        for año in años:
            for region in regiones:
                for idx, row in df_base.iterrows():
                    nueva_fila = row.copy()
                    nueva_fila['Año'] = año
                    nueva_fila['Region'] = region
                    # Variar los valores según año y región
                    factor = 1 + (año - 2022) * 0.1 + hash(region) % 10 * 0.05
                    nueva_fila['Valor'] = int(nueva_fila['Valor'] * factor)
                    nueva_fila['Valor_Anterior'] = int(nueva_fila['Valor_Anterior'] * factor)
                    nueva_fila['Objetivo'] = int(nueva_fila['Objetivo'] * factor)
                    df_extendido.append(nueva_fila)
        
        df_final = pd.DataFrame(df_extendido)
        
        # Guardar archivo principal
        archivo_ejemplo = directorio_proyecto / "input" / "datos_ejemplo.csv"
        df_final.to_csv(archivo_ejemplo, index=False)
        
        # Crear también un archivo Excel para pruebas
        archivo_excel = directorio_proyecto / "input" / "datos_ejemplo.xlsx"
        df_final.to_excel(archivo_excel, index=False)
        
        print(f"✓ Creado: input/datos_ejemplo.csv ({len(df_final)} registros)")
        print(f"✓ Creado: input/datos_ejemplo.xlsx ({len(df_final)} registros)")
        
        # Crear un archivo de datos simplificado también
        archivo_simple = directorio_proyecto / "input" / "datos_simple.csv"
        df_base.to_csv(archivo_simple, index=False)
        print(f"✓ Creado: input/datos_simple.csv ({len(df_base)} registros)")
    
    def _crear_scripts_proyecto(self, directorio_proyecto: Path, nombre_proyecto: str):
        """Crea los scripts específicos del proyecto"""
        # Script para generar gráficas
        script_generar = f"""#!/usr/bin/env python3
'''
Script para generar todas las gráficas del proyecto: {nombre_proyecto}
'''

import os
import sys
from pathlib import Path

# Agregar el directorio padre al path para importar los módulos
sys.path.append(str(Path(__file__).parent.parent))

from grafico_cli import GraficoCLI

def main():
    # Configuración del proyecto
    directorio_proyecto = Path(__file__).parent
    directorio_recetas = directorio_proyecto.parent / "recetas_centrales"
    directorio_input = directorio_proyecto / "input"
    directorio_output = directorio_proyecto / "output"
    
    print(f"Proyecto: {nombre_proyecto}")
    print(f"Directorio: {{directorio_proyecto}}")
    
    # Buscar archivos de datos
    archivos_datos = list(directorio_input.glob("*.csv")) + list(directorio_input.glob("*.xlsx"))
    
    if not archivos_datos:
        print("⚠ No se encontraron archivos de datos en input/")
        return
    
    # Usar el primer archivo encontrado
    archivo_datos = archivos_datos[0]
    print(f"Usando datos: {{archivo_datos.name}}")
    
    # Crear instancia del CLI
    cli = GraficoCLI()
    
    # Procesar todas las recetas
    cli.procesar_lote(
        directorio_recetas=str(directorio_recetas),
        archivo_datos=str(archivo_datos),
        directorio_salida=str(directorio_output)
    )
    
    print("✓ Generación completada")

if __name__ == "__main__":
    main()
"""
        
        archivo_script = directorio_proyecto / "generar_graficas.py"
        with open(archivo_script, 'w', encoding='utf-8') as f:
            f.write(script_generar)
        
        print(f"✓ Creado: generar_graficas.py")
        
        # Script para generar catálogo
        script_catalogo = f"""#!/usr/bin/env python3
'''
Script para generar el catálogo Excel del proyecto: {nombre_proyecto}
'''

import sys
from pathlib import Path

# Agregar el directorio padre al path para importar los módulos
sys.path.append(str(Path(__file__).parent.parent))

from generador_catalogo import GeneradorCatalogo

def main():
    # Configuración del proyecto
    directorio_proyecto = Path(__file__).parent
    
    print(f"Generando catálogo para: {nombre_proyecto}")
    print(f"Directorio: {{directorio_proyecto}}")
    
    # Crear instancia del generador
    generador = GeneradorCatalogo(str(directorio_proyecto))
    
    # Generar catálogo
    archivo_catalogo = generador.generar_catalogo_excel()
    
    print(f"✓ Catálogo generado: {{archivo_catalogo}}")

if __name__ == "__main__":
    main()
"""
        
        archivo_catalogo_script = directorio_proyecto / "generar_catalogo.py"
        with open(archivo_catalogo_script, 'w', encoding='utf-8') as f:
            f.write(script_catalogo)
        
        print(f"✓ Creado: generar_catalogo.py")
    
    def listar_proyectos(self) -> list:
        """Lista todos los proyectos existentes"""
        if not self.directorio_base.exists():
            return []
        
        proyectos = []
        for item in self.directorio_base.iterdir():
            if item.is_dir():
                config_file = item / "config_proyecto.yaml"
                if config_file.exists():
                    try:
                        with open(config_file, 'r', encoding='utf-8') as f:
                            config = yaml.safe_load(f)
                        
                        proyectos.append({
                            'nombre': item.name,
                            'ruta': str(item),
                            'fecha_creacion': config.get('proyecto', {}).get('fecha_creacion', ''),
                            'descripcion': config.get('proyecto', {}).get('descripcion', ''),
                        })
                    except Exception as e:
                        print(f"Error leyendo config de {item.name}: {e}")
        
        return proyectos

def main():
    """Función principal para usar desde línea de comandos"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Inicializador de proyectos de gráficas')
    parser.add_argument('--crear', '-c', help='Nombre del nuevo proyecto a crear')
    parser.add_argument('--listar', '-l', action='store_true', help='Listar proyectos existentes')
    parser.add_argument('--base-dir', '-b', default='proyectos', help='Directorio base para proyectos')
    parser.add_argument('--sin-recetas', action='store_true', help='No copiar recetas centrales')
    
    args = parser.parse_args()
    
    inicializador = InicializadorProyecto(args.base_dir)
    
    if args.listar:
        proyectos = inicializador.listar_proyectos()
        if not proyectos:
            print("No se encontraron proyectos")
        else:
            print(f"Proyectos encontrados ({len(proyectos)}):")
            for proyecto in proyectos:
                print(f"  - {proyecto['nombre']} ({proyecto['fecha_creacion']})")
                print(f"    {proyecto['descripcion']}")
                print(f"    Ruta: {proyecto['ruta']}")
                print()
    
    elif args.crear:
        copiar_recetas = not args.sin_recetas
        directorio_proyecto = inicializador.crear_estructura_proyecto(args.crear, copiar_recetas)
        print(f"\\n✓ Proyecto creado en: {directorio_proyecto}")
        print("\\nPróximos pasos:")
        print("1. Colocar archivos de datos en input/")
        print("2. Configurar recetas en recetas/")
        print("3. Ejecutar: python generar_graficas.py")
        print("4. Ejecutar: python generar_catalogo.py")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
