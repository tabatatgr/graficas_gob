#!/usr/bin/env python3
"""
Sistema CLI para generación masiva de gráficas con recetas YAML
Incluye optimización automática de SVG para Figma
Uso: python grafico_cli.py --recetas-dir recetas/ --datos datos.xlsx --output output/
"""

import argparse
import yaml
import pandas as pd
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import importlib.util

# Importar las funciones de gráficas desde recetas_centrales
from recetas_centrales.barras.funcion_barras import barras_verticales
from recetas_centrales.agrupadasyapiladas.funcion_agrupadasyapiladas import agrupadasyapiladas
from recetas_centrales.areaplot2.funcion_areaplot2 import areaplot2
from recetas_centrales.areaplot.funcion_areaplot import areaplot
from recetas_centrales.barras_tendencias.funcion_barras_tendencias import barras_tendencias
from recetas_centrales.linea.funcion_linea import generar_linea
from recetas_centrales.lineas_tendencia.funcion_lineas_tendencia import generar_lineas_tendencia
from recetas_centrales.multilineas.funcion_multilineas import generar_multilineas
from recetas_centrales.treemap.funcion_treemap import generar_treemap

class GraficoCLI:
    def __init__(self):
        self.tipos_grafico = {
            'barras_verticales': barras_verticales,
            'agrupadasyapiladas': agrupadasyapiladas,
            'areaplot2': areaplot2,
            'areaplot': areaplot,
            'barras_tendencias': barras_tendencias,
            'linea': generar_linea,
            'lineas_tendencia': generar_lineas_tendencia,
            'multilineas': generar_multilineas,
            'treemap': generar_treemap,
        }
        
        print("Optimización SVG para Figma activada por defecto")
        self._verificar_dependencias_svg()
        
    def cargar_receta(self, archivo_yaml: str) -> Dict[str, Any]:
        """Carga una receta YAML y valida su estructura básica"""
        try:
            with open(archivo_yaml, 'r', encoding='utf-8') as f:
                receta = yaml.safe_load(f)
            
            # Validaciones básicas
            if 'tipo_grafico' not in receta:
                raise ValueError(f"La receta {archivo_yaml} debe especificar 'tipo_grafico'")
            
            if receta['tipo_grafico'] not in self.tipos_grafico:
                raise ValueError(f"Tipo de gráfico '{receta['tipo_grafico']}' no soportado")
            
            return receta
        except Exception as e:
            print(f"Error cargando receta {archivo_yaml}: {e}")
            return None
    
    def cargar_datos(self, archivo_datos: str, **filtros) -> pd.DataFrame:
        """Carga datos desde Excel o CSV con filtros opcionales"""
        if archivo_datos.endswith('.xlsx') or archivo_datos.endswith('.xls'):
            df = pd.read_excel(archivo_datos)
        elif archivo_datos.endswith('.csv'):
            df = pd.read_csv(archivo_datos)
        else:
            raise ValueError(f"Formato de archivo no soportado: {archivo_datos}")
        
        # Aplicar filtros si se especifican
        for columna, valores in filtros.items():
            if columna in df.columns:
                if isinstance(valores, list):
                    df = df[df[columna].isin(valores)]
                else:
                    df = df[df[columna] == valores]
        
        return df
    
    def preparar_dataframe(self, df: pd.DataFrame, config_datos: Dict[str, Any]) -> pd.DataFrame:
        """Prepara el DataFrame según la configuración de la receta"""
        df_resultado = df.copy()
        
        # Filtrar datos si se especifica
        if 'filtros' in config_datos:
            for filtro in config_datos['filtros']:
                columna = filtro['columna']
                valor = filtro['valor']
                operador = filtro.get('operador', '==')
                
                if operador == '==':
                    df_resultado = df_resultado[df_resultado[columna] == valor]
                elif operador == 'in':
                    df_resultado = df_resultado[df_resultado[columna].isin(valor)]
                elif operador == '!=':
                    df_resultado = df_resultado[df_resultado[columna] != valor]
        
        # Seleccionar columnas específicas
        if 'columnas' in config_datos:
            df_resultado = df_resultado[config_datos['columnas']]
        
        # Renombrar columnas si se especifica
        if 'renombrar_columnas' in config_datos:
            df_resultado = df_resultado.rename(columns=config_datos['renombrar_columnas'])
        
        # Aplicar transformaciones a columnas específicas
        if 'transformaciones' in config_datos:
            for transformacion in config_datos['transformaciones']:
                columna = transformacion['columna']
                operacion = transformacion['operacion']
                
                if operacion == 'negativo':
                    df_resultado[columna] = df_resultado[columna] * -1
                elif operacion == 'absoluto':
                    df_resultado[columna] = df_resultado[columna].abs()
                elif operacion == 'agregar_ceros':
                    df_resultado[columna] = 0
        
        return df_resultado
    
    def preparar_dataframes_agrupados(self, df: pd.DataFrame, config_datos: Dict[str, Any]) -> list:
        """Prepara múltiples DataFrames para gráficas agrupadas y apiladas"""
        # Aplicar filtros básicos primero
        df_filtrado = self.preparar_dataframe(df, config_datos)
        
        # Obtener la columna que define los grupos
        columna_agrupamiento = config_datos.get('agrupar_por', 'Tipo')
        
        if columna_agrupamiento not in df_filtrado.columns:
            raise ValueError(f"La columna '{columna_agrupamiento}' no existe en los datos")
        
        # Crear lista de DataFrames agrupados
        dataframes = []
        grupos = df_filtrado[columna_agrupamiento].unique()
        
        for grupo in grupos:
            df_grupo = df_filtrado[df_filtrado[columna_agrupamiento] == grupo].copy()
            dataframes.append(df_grupo)
        
        return dataframes

    def aplicar_exclusiones(self, parametros: Dict[str, Any], exclusiones: List[str]) -> Dict[str, Any]:
        """Aplica exclusiones removiendo elementos específicos"""
        parametros_filtrados = parametros.copy()
        
        for exclusion in exclusiones:
            if exclusion in parametros_filtrados:
                del parametros_filtrados[exclusion]
        
        return parametros_filtrados
    
    def generar_grafica(self, receta: Dict[str, Any], df: pd.DataFrame, kwargs_extra: Dict[str, Any] = None) -> bool:
        """Genera una gráfica individual basada en la receta"""
        try:
            # Obtener función de gráfica
            tipo_grafico = receta['tipo_grafico']
            funcion_grafica = self.tipos_grafico[tipo_grafico]
            
            # Preparar parámetros
            parametros = receta.get('parametros', {})
            
            # Agregar kwargs extra de la línea de comandos
            if kwargs_extra:
                parametros.update(kwargs_extra)
            
            # Aplicar exclusiones si se especifican
            if 'exclusiones' in receta:
                parametros = self.aplicar_exclusiones(parametros, receta['exclusiones'])
            
            # Configurar parámetros para optimización SVG
            parametros['output_dir'] = parametros.get('output_dir', 'output')
            parametros['usar_flujo_svg'] = True
            
            # Manejo especial para gráficas agrupadas y apiladas
            if tipo_grafico == 'agrupadasyapiladas':
                if 'datos' in receta:
                    dataframes = self.preparar_dataframes_agrupados(df, receta['datos'])
                else:
                    # Si no hay configuración de datos, asumir que el DataFrame ya está preparado
                    # y crear una lista con un solo DataFrame
                    dataframes = [df]
                
                # Remover parámetros específicos de configuración de datos
                parametros_limpio = parametros.copy()
                for key in ['agrupar_por', 'columnas_requeridas', 'formato']:
                    parametros_limpio.pop(key, None)
                
                funcion_grafica(dataframes, **parametros_limpio)
            else:
                # Preparar DataFrame para gráficas normales
                if 'datos' in receta:
                    df_preparado = self.preparar_dataframe(df, receta['datos'])
                else:
                    df_preparado = df
                
                funcion_grafica(df_preparado, **parametros)
            
            # Aplicar optimización SVG automáticamente si se generó un archivo SVG
            nombre_grafica = parametros.get('nombre', 'sin_nombre')
            print(f"Gráfica generada: {nombre_grafica}")
                
            return True
        except Exception as e:
            print(f"Error generando gráfica: {e}")
            return False
    
    def procesar_lote(self, directorio_recetas: str, archivo_datos: str, directorio_salida: str, kwargs_extra: Dict[str, Any] = None):
        """Procesa un lote completo de recetas"""
        # Crear directorio de salida si no existe
        Path(directorio_salida).mkdir(parents=True, exist_ok=True)
        
        # Cargar datos
        print(f"Cargando datos desde: {archivo_datos}")
        df = self.cargar_datos(archivo_datos)
        print(f"Datos cargados: {len(df)} filas, {len(df.columns)} columnas")
        
        # Buscar archivos YAML en el directorio
        archivos_yaml = list(Path(directorio_recetas).glob("*.yaml")) + list(Path(directorio_recetas).glob("*.yml"))
        
        if not archivos_yaml:
            print(f"No se encontraron archivos YAML en {directorio_recetas}")
            return
        
        print(f"Encontradas {len(archivos_yaml)} recetas")
        
        # Cambiar al directorio de salida para que las gráficas se guarden ahí
        directorio_original = os.getcwd()
        os.chdir(directorio_salida)
        
        exitosos = 0
        fallidos = 0
        
        try:
            for archivo_yaml in archivos_yaml:
                print(f"\nProcesando: {archivo_yaml.name}")
                # Usar la ruta absoluta del archivo
                ruta_completa = os.path.join(directorio_original, archivo_yaml)
                receta = self.cargar_receta(ruta_completa)
                
                if receta is None:
                    fallidos += 1
                    continue
                
                if self.generar_grafica(receta, df, kwargs_extra):
                    exitosos += 1
                else:
                    fallidos += 1
        
        finally:
            # Regresar al directorio original
            os.chdir(directorio_original)
        
        print(f"\n=== Resumen ===")
        print(f"Gráficas exitosas: {exitosos}")
        print(f"Gráficas fallidas: {fallidos}")
        print(f"Total procesadas: {exitosos + fallidos}")
        
        # Control de calidad básico
        self.verificar_calidad(directorio_salida)
    
    def verificar_calidad(self, directorio_salida: str):
        """Verifica que los archivos generados cumplan criterios básicos"""
        archivos_svg = list(Path(directorio_salida).glob("*.svg"))
        archivos_png = list(Path(directorio_salida).glob("*.png"))
        
        print(f"\n=== Control de Calidad ===")
        print(f"Archivos SVG generados: {len(archivos_svg)}")
        print(f"Archivos PNG generados: {len(archivos_png)}")
        
        # Verificar que los archivos no estén vacíos
        archivos_vacios = []
        for archivo in archivos_svg + archivos_png:
            if archivo.stat().st_size == 0:
                archivos_vacios.append(archivo)
        
        if archivos_vacios:
            print(f"Archivos vacíos detectados: {len(archivos_vacios)}")
            for archivo in archivos_vacios:
                print(f"  - {archivo}")
        else:
            print("Todos los archivos tienen contenido")
    
    def _verificar_dependencias_svg(self):
        """Verifica que las herramientas necesarias estén disponibles"""
        try:
            from svg_cleanup.flujo_exportacion import FlujoDeLimpieza
            flujo = FlujoDeLimpieza()
            
            if not flujo.verificar_herramientas():
                print("Algunas herramientas SVG no están disponibles")
                print("   - SVGO: npm install -g svgo")
                print("   - Scour: pip install scour")
                
        except ImportError:
            print("Módulo de optimización SVG no disponible")
        
    def _aplicar_optimizacion_svg(self, svg_path, nombre_base, output_dir):
        """Aplica optimización SVG a un archivo SVG"""
        try:
            from svg_cleanup.flujo_exportacion import exportar_grafica
            
            print(f"Aplicando optimización SVG a {nombre_base}...")
            archivo_final = exportar_grafica(svg_path, nombre_base, output_dir)
            
            if archivo_final:
                print(f"Archivo optimizado para Figma: {archivo_final}")
                return archivo_final
            else:
                print("Error en optimización SVG")
                return svg_path
                
        except ImportError:
            print("Optimizador SVG no disponible")
            return svg_path
        except Exception as e:
            print(f"Error en optimización SVG: {e}")
            return svg_path

def main():
    parser = argparse.ArgumentParser(description='Generador masivo de gráficas con recetas YAML')
    parser.add_argument('--recetas-dir', '-r', required=True, help='Directorio con archivos YAML de recetas')
    parser.add_argument('--datos', '-d', required=True, help='Archivo de datos (Excel o CSV)')
    parser.add_argument('--output', '-o', required=True, help='Directorio de salida para las gráficas')
    parser.add_argument('--receta-unica', '-u', help='Procesar solo una receta específica')
    
    # Permitir kwargs adicionales
    parser.add_argument('--kwargs', nargs='*', help='Parámetros adicionales en formato clave=valor')
    
    args, unknown = parser.parse_known_args()
    
    # Procesar kwargs adicionales
    kwargs_extra = {}
    if args.kwargs:
        for kwarg in args.kwargs:
            if '=' in kwarg:
                clave, valor = kwarg.split('=', 1)
                # Intentar convertir a número si es posible
                try:
                    if '.' in valor:
                        valor = float(valor)
                    else:
                        valor = int(valor)
                except ValueError:
                    # Mantener como string si no es numérico
                    pass
                kwargs_extra[clave] = valor
    
    # Procesar argumentos desconocidos como kwargs también
    for i in range(0, len(unknown), 2):
        if i + 1 < len(unknown):
            clave = unknown[i].lstrip('-')
            valor = unknown[i + 1]
            try:
                if '.' in valor:
                    valor = float(valor)
                else:
                    valor = int(valor)
            except ValueError:
                pass
            kwargs_extra[clave] = valor
    
    # Crear instancia del CLI con optimización SVG automática
    cli = GraficoCLI()
    
    if args.receta_unica:
        # Procesar una sola receta
        archivo_receta = Path(args.recetas_dir) / args.receta_unica
        if not archivo_receta.exists():
            print(f"Error: No se encontró la receta {archivo_receta}")
            sys.exit(1)
        
        receta = cli.cargar_receta(archivo_receta)
        if receta:
            df = cli.cargar_datos(args.datos)
            os.makedirs(args.output, exist_ok=True)
            os.chdir(args.output)
            cli.generar_grafica(receta, df, kwargs_extra)
    else:
        # Procesar lote completo
        cli.procesar_lote(args.recetas_dir, args.datos, args.output, kwargs_extra)

if __name__ == "__main__":
    main()
