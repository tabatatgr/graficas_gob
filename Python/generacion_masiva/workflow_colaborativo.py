#!/usr/bin/env python3
"""
Workflow completo para generación colaborativa de gráficas
Integra todos los componentes del sistema en un flujo unificado
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime
import yaml

# Importar componentes del sistema
from inicializador_proyecto import InicializadorProyecto
from grafico_cli import GraficoCLI
from generador_catalogo import GeneradorCatalogo

class WorkflowGraficas:
    def __init__(self, directorio_base: str = "proyectos"):
        """
        Inicializa el workflow de gráficas
        
        Args:
            directorio_base: Directorio base donde se almacenan los proyectos
        """
        self.directorio_base = Path(directorio_base)
        self.inicializador = InicializadorProyecto(directorio_base)
        
    def crear_nuevo_proyecto(self, nombre_proyecto: str, descripcion: str = "") -> str:
        """
        Paso 1: Crear un nuevo proyecto con la estructura completa
        
        Args:
            nombre_proyecto: Nombre del proyecto
            descripcion: Descripción del proyecto
            
        Returns:
            Ruta al directorio del proyecto
        """
        print("=" * 60)
        print("PASO 1: CREANDO NUEVO PROYECTO")
        print("=" * 60)
        
        directorio_proyecto = self.inicializador.crear_estructura_proyecto(
            nombre_proyecto
        )
        
        # Actualizar descripción si se proporcionó
        if descripcion:
            self._actualizar_descripcion_proyecto(directorio_proyecto, descripcion)
        
        print(f"\\n✓ Proyecto '{nombre_proyecto}' creado exitosamente")
        print(f"Directorio: {directorio_proyecto}")
        
        return directorio_proyecto
    
    def preparar_datos_proyecto(self, directorio_proyecto: str, archivos_datos: list) -> bool:
        """
        Paso 2: Preparar los datos del proyecto
        
        Args:
            directorio_proyecto: Ruta al directorio del proyecto
            archivos_datos: Lista de archivos de datos a copiar
            
        Returns:
            True si se prepararon correctamente
        """
        print("=" * 60)
        print("PASO 2: PREPARANDO DATOS DEL PROYECTO")
        print("=" * 60)
        
        directorio_input = Path(directorio_proyecto) / "input"
        
        for archivo_datos in archivos_datos:
            archivo_origen = Path(archivo_datos)
            if not archivo_origen.exists():
                print(f"⚠ Archivo no encontrado: {archivo_datos}")
                continue
            
            import shutil
            archivo_destino = directorio_input / archivo_origen.name
            shutil.copy2(archivo_origen, archivo_destino)
            print(f"✓ Copiado: {archivo_origen.name}")
        
        # Listar archivos preparados
        archivos_preparados = list(directorio_input.glob("*.csv")) + list(directorio_input.glob("*.xlsx"))
        print(f"\\n✓ Archivos de datos preparados: {len(archivos_preparados)}")
        
        return True
    
    def configurar_recetas_proyecto(self, directorio_proyecto: str, recetas_usar: list = None) -> bool:
        """
        Paso 3: Configurar las recetas del proyecto
        
        Args:
            directorio_proyecto: Ruta al directorio del proyecto
            recetas_usar: Lista de recetas específicas a usar (opcional)
            
        Returns:
            True si se configuraron correctamente
        """
        print("=" * 60)
        print("PASO 3: CONFIGURANDO RECETAS DEL PROYECTO")
        print("=" * 60)
        
        # Usar recetas centrales directamente
        directorio_recetas = Path(directorio_proyecto).parent.parent / "recetas_centrales"
        
        # Listar recetas disponibles
        recetas_disponibles = list(directorio_recetas.glob("*.yaml"))
        print(f"Recetas centrales disponibles: {len(recetas_disponibles)}")
        
        for receta in recetas_disponibles:
            print(f"  - {receta.name}")
        
        # Si se especificaron recetas específicas, filtrar
        if recetas_usar:
            for receta_nombre in recetas_usar:
                receta_path = directorio_recetas / receta_nombre
                if not receta_path.exists():
                    print(f"⚠ Receta no encontrada: {receta_nombre}")
        
        print(f"\\nRecetas configuradas correctamente")
        return True
    
    def generar_graficas_proyecto(self, directorio_proyecto: str) -> bool:
        """
        Paso 4: Generar todas las gráficas del proyecto
        
        Args:
            directorio_proyecto: Ruta al directorio del proyecto
            
        Returns:
            True si se generaron correctamente
        """
        print("=" * 60)
        print("PASO 4: GENERANDO GRÁFICAS DEL PROYECTO")
        print("=" * 60)
        
        directorio_proyecto = Path(directorio_proyecto)
        directorio_recetas = directorio_proyecto.parent.parent / "recetas_centrales"
        directorio_input = directorio_proyecto / "input"
        directorio_output = directorio_proyecto / "output"
        
        # Buscar archivos de datos
        archivos_datos = list(directorio_input.glob("*.csv")) + list(directorio_input.glob("*.xlsx"))
        
        if not archivos_datos:
            print("⚠ No se encontraron archivos de datos")
            return False
        
        # Usar el primer archivo encontrado
        archivo_datos = archivos_datos[0]
        print(f"Usando datos: {archivo_datos.name}")
        
        # Crear instancia del CLI
        cli = GraficoCLI()
        
        # Procesar todas las recetas
        try:
            cli.procesar_lote(
                directorio_recetas=str(directorio_recetas),
                archivo_datos=str(archivo_datos),
                directorio_salida=str(directorio_output)
            )
            
            print("\\nGraficas generadas exitosamente")
            return True
            
        except Exception as e:
            print(f"✗ Error generando gráficas: {e}")
            return False
    
    def optimizar_svg_proyecto(self, directorio_proyecto: str) -> bool:
        """
        Paso 5: Optimizar archivos SVG para Figma
        
        Args:
            directorio_proyecto: Ruta al directorio del proyecto
            
        Returns:
            True si se optimizaron correctamente
        """
        print("=" * 60)
        print("PASO 5: OPTIMIZANDO SVG PARA FIGMA")
        print("=" * 60)
        
        directorio_output = Path(directorio_proyecto) / "output"
        archivos_svg = list(directorio_output.glob("*.svg"))
        
        if not archivos_svg:
            print("⚠ No se encontraron archivos SVG")
            return False
        
        print(f"Archivos SVG encontrados: {len(archivos_svg)}")
        
        # La optimización SVG ya se hace automáticamente en el CLI
        # Aquí solo verificamos que se haya hecho
        archivos_optimizados = 0
        for archivo_svg in archivos_svg:
            try:
                with open(archivo_svg, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                
                if 'figma-ready' in contenido or 'id="titulo-' in contenido:
                    archivos_optimizados += 1
                    
            except Exception as e:
                print(f"Error verificando {archivo_svg.name}: {e}")
        
        print(f"Archivos SVG optimizados: {archivos_optimizados}/{len(archivos_svg)}")
        return True
    
    def generar_catalogo_proyecto(self, directorio_proyecto: str) -> str:
        """
        Paso 6: Generar el catálogo Excel del proyecto
        
        Args:
            directorio_proyecto: Ruta al directorio del proyecto
            
        Returns:
            Ruta al archivo de catálogo generado
        """
        print("=" * 60)
        print("PASO 6: GENERANDO CATÁLOGO EXCEL")
        print("=" * 60)
        
        generador = GeneradorCatalogo(directorio_proyecto)
        archivo_catalogo = generador.generar_catalogo_excel()
        
        print(f"Catalogo generado: {archivo_catalogo}")
        return archivo_catalogo
    
    def verificar_calidad_proyecto(self, directorio_proyecto: str) -> dict:
        """
        Paso 7: Verificar la calidad del proyecto
        
        Args:
            directorio_proyecto: Ruta al directorio del proyecto
            
        Returns:
            Diccionario con métricas de calidad
        """
        print("=" * 60)
        print("PASO 7: VERIFICANDO CALIDAD DEL PROYECTO")
        print("=" * 60)
        
        directorio_proyecto = Path(directorio_proyecto)
        directorio_output = directorio_proyecto / "output"
        
        metricas = {
            'archivos_svg': len(list(directorio_output.glob("*.svg"))),
            'archivos_png': len(list(directorio_output.glob("*.png"))),
            'archivos_optimizados': 0,
            'archivos_con_errores': 0,
            'tamaño_total_mb': 0,
        }
        
        # Verificar archivos SVG
        for archivo_svg in directorio_output.glob("*.svg"):
            try:
                with open(archivo_svg, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                
                if 'figma-ready' in contenido or 'id="titulo-' in contenido:
                    metricas['archivos_optimizados'] += 1
                
                metricas['tamaño_total_mb'] += archivo_svg.stat().st_size / (1024 * 1024)
                
            except Exception as e:
                metricas['archivos_con_errores'] += 1
        
        # Mostrar métricas
        print("Métricas de calidad:")
        print(f"  - Archivos SVG: {metricas['archivos_svg']}")
        print(f"  - Archivos PNG: {metricas['archivos_png']}")
        print(f"  - Archivos optimizados: {metricas['archivos_optimizados']}")
        print(f"  - Archivos con errores: {metricas['archivos_con_errores']}")
        print(f"  - Tamaño total: {metricas['tamaño_total_mb']:.2f} MB")
        
        return metricas
    
    def ejecutar_workflow_completo(self, nombre_proyecto: str, archivos_datos: list, 
                                  descripcion: str = "", recetas_usar: list = None) -> str:
        """
        Ejecuta el workflow completo de generación de gráficas
        
        Args:
            nombre_proyecto: Nombre del proyecto
            archivos_datos: Lista de archivos de datos
            descripcion: Descripción del proyecto
            recetas_usar: Lista de recetas específicas
            
        Returns:
            Ruta al directorio del proyecto
        """
        print("INICIANDO WORKFLOW COMPLETO DE GENERACIÓN DE GRÁFICAS")
        print(f"Proyecto: {nombre_proyecto}")
        print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        try:
            # Paso 1: Crear proyecto
            directorio_proyecto = self.crear_nuevo_proyecto(nombre_proyecto, descripcion)
            
            # Paso 2: Preparar datos
            if archivos_datos:
                self.preparar_datos_proyecto(directorio_proyecto, archivos_datos)
            
            # Paso 3: Configurar recetas
            self.configurar_recetas_proyecto(directorio_proyecto, recetas_usar)
            
            # Paso 4: Generar gráficas
            if not self.generar_graficas_proyecto(directorio_proyecto):
                raise Exception("Error generando gráficas")
            
            # Paso 5: Optimizar SVG
            self.optimizar_svg_proyecto(directorio_proyecto)
            
            # Paso 6: Generar catálogo
            archivo_catalogo = self.generar_catalogo_proyecto(directorio_proyecto)
            
            # Paso 7: Verificar calidad
            metricas = self.verificar_calidad_proyecto(directorio_proyecto)
            
            # Resumen final
            print("\\n" + "=" * 60)
            print("WORKFLOW COMPLETADO EXITOSAMENTE")
            print("=" * 60)
            print(f"Proyecto: {nombre_proyecto}")
            print(f"Directorio: {directorio_proyecto}")
            print(f"Catálogo: {archivo_catalogo}")
            print(f"Gráficas generadas: {metricas['archivos_svg']}")
            print("\\nPróximos pasos:")
            print("1. Revisar el catálogo Excel (resumen.xlsx)")
            print("2. Importar archivos SVG en Figma")
            print("3. Editar diseños según lineamientos")
            print("4. Entregar visualizaciones finales")
            
            return directorio_proyecto
            
        except Exception as e:
            print(f"\\nERROR EN WORKFLOW: {e}")
            return None
    
    def _actualizar_descripcion_proyecto(self, directorio_proyecto: str, descripcion: str):
        """Actualiza la descripción en el archivo de configuración"""
        config_file = Path(directorio_proyecto) / "config_proyecto.yaml"
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            config['proyecto']['descripcion'] = descripcion
            
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
                
        except Exception as e:
            print(f"Error actualizando descripción: {e}")

def main():
    """Función principal para usar desde línea de comandos"""
    parser = argparse.ArgumentParser(description='Workflow completo de generación de gráficas')
    
    # Comandos principales
    subparsers = parser.add_subparsers(dest='comando', help='Comandos disponibles')
    
    # Comando: crear proyecto
    parser_crear = subparsers.add_parser('crear', help='Crear nuevo proyecto')
    parser_crear.add_argument('nombre', help='Nombre del proyecto')
    parser_crear.add_argument('--descripcion', '-d', help='Descripción del proyecto')
    parser_crear.add_argument('--datos', nargs='+', help='Archivos de datos a incluir')
    parser_crear.add_argument('--recetas', nargs='+', help='Recetas específicas a usar')
    
    # Comando: ejecutar workflow completo
    parser_workflow = subparsers.add_parser('workflow', help='Ejecutar workflow completo')
    parser_workflow.add_argument('nombre', help='Nombre del proyecto')
    parser_workflow.add_argument('--datos', nargs='+', required=True, help='Archivos de datos')
    parser_workflow.add_argument('--descripcion', '-d', help='Descripción del proyecto')
    parser_workflow.add_argument('--recetas', nargs='+', help='Recetas específicas a usar')
    
    # Comando: generar gráficas para proyecto existente
    parser_generar = subparsers.add_parser('generar', help='Generar gráficas para proyecto existente')
    parser_generar.add_argument('proyecto', help='Directorio del proyecto')
    
    # Comando: generar catálogo para proyecto existente
    parser_catalogo = subparsers.add_parser('catalogo', help='Generar catálogo para proyecto existente')
    parser_catalogo.add_argument('proyecto', help='Directorio del proyecto')
    
    # Comando: listar proyectos
    parser_listar = subparsers.add_parser('listar', help='Listar proyectos existentes')
    
    # Opciones globales
    parser.add_argument('--base-dir', '-b', default='proyectos', help='Directorio base para proyectos')
    
    args = parser.parse_args()
    
    if not args.comando:
        parser.print_help()
        return
    
    # Crear instancia del workflow
    workflow = WorkflowGraficas(args.base_dir)
    
    if args.comando == 'crear':
        directorio_proyecto = workflow.crear_nuevo_proyecto(args.nombre, args.descripcion or "")
        
        if args.datos:
            workflow.preparar_datos_proyecto(directorio_proyecto, args.datos)
        
        workflow.configurar_recetas_proyecto(directorio_proyecto, args.recetas)
        
        print(f"\\nProyecto creado: {directorio_proyecto}")
        
    elif args.comando == 'workflow':
        directorio_proyecto = workflow.ejecutar_workflow_completo(
            args.nombre, 
            args.datos, 
            args.descripcion or "",
            args.recetas
        )
        
        if directorio_proyecto:
            print(f"\\nWorkflow completado: {directorio_proyecto}")
        else:
            print("\\nError en workflow")
            sys.exit(1)
    
    elif args.comando == 'generar':
        if workflow.generar_graficas_proyecto(args.proyecto):
            print(f"\\nGraficas generadas para: {args.proyecto}")
        else:
            print("\\nError generando graficas")
            sys.exit(1)
    
    elif args.comando == 'catalogo':
        archivo_catalogo = workflow.generar_catalogo_proyecto(args.proyecto)
        print(f"\\nCatalogo generado: {archivo_catalogo}")
    
    elif args.comando == 'listar':
        proyectos = workflow.inicializador.listar_proyectos()
        if not proyectos:
            print("No se encontraron proyectos")
        else:
            print(f"\\nProyectos encontrados ({len(proyectos)}):")
            for proyecto in proyectos:
                print(f"  {proyecto['nombre']} ({proyecto['fecha_creacion']})")
                print(f"     {proyecto['descripcion']}")
                print(f"     {proyecto['ruta']}")
                print()

if __name__ == "__main__":
    main()
