# Configuración global de estilos para gráficas
# Este archivo permite ajustar temas corporativos y tipografías de forma centralizada

import os
from pathlib import Path

class EstilosGlobales:
    """Configuración centralizada de estilos para todas las gráficas"""
    
    # Paletas de colores temáticas
    PALETAS = {
        'gubernamental': ["#114a44", "#739489", "#3d5c93", "#7393b3", "#6B5B95"],
        'corporativo': ["#2C3E50", "#3498DB", "#E74C3C", "#F39C12", "#9B59B6"],
        'amigable': ["#16a085", "#2ecc71", "#3498db", "#9b59b6", "#e67e22"],
        'neutro': ["#34495e", "#7f8c8d", "#95a5a6", "#bdc3c7", "#ecf0f1"],
        'contraste_alto': ["#000000", "#ffffff", "#ff0000", "#00ff00", "#0000ff"]
    }
    
    # Fuentes disponibles
    FUENTES = {
        'principal': 'Montserrat',
        'alternativa': 'Arial',
        'monospace': 'Courier New'
    }
    
    # Configuraciones base por tipo de gráfica
    CONFIGURACIONES_BASE = {
        'barras_verticales': {
            'font': 'Montserrat',
            'fontsize_barra': 7,
            'fontsize_valor_total': 15,
            'bar_height': 0.65,
            'grillas': True,
            'orientacion_etiqueta_x': 'horizontal',
            'capsulas_cero': False,
            'porcentaje_divergente': True,
            'ejeY_negativo_a_positivo': True,
        },
        'barras_horizontales': {
            'font': 'Montserrat',
            'fontsize_barra': 8,
            'fontsize_valor_total': 16,
            'bar_width': 0.6,
            'grillas': True,
        },
        'lineas': {
            'font': 'Montserrat',
            'fontsize_etiquetas': 12,
            'grosor_linea': 2.5,
            'marcadores': True,
        }
    }
    
    # Configuraciones por tema corporativo
    TEMAS_CORPORATIVOS = {
        'gobierno': {
            'paleta': 'gubernamental',
            'font': 'Montserrat',
            'colores_especiales': {
                'texto_principal': '#000000',
                'texto_secundario': '#4C6A67',
                'fondo': '#ffffff',
                'grillas': '#B9B9B9'
            }
        },
        'empresa_privada': {
            'paleta': 'corporativo',
            'font': 'Arial',
            'colores_especiales': {
                'texto_principal': '#2C3E50',
                'texto_secundario': '#7F8C8D',
                'fondo': '#ffffff',
                'grillas': '#BDC3C7'
            }
        }
    }
    
    @classmethod
    def get_configuracion_completa(cls, tipo_grafico, tema='gobierno', personalizaciones=None):
        """
        Retorna la configuración completa para un tipo de gráfica y tema específico
        """
        # Configuración base
        config = cls.CONFIGURACIONES_BASE.get(tipo_grafico, {}).copy()
        
        # Aplicar tema corporativo
        tema_config = cls.TEMAS_CORPORATIVOS.get(tema, cls.TEMAS_CORPORATIVOS['gobierno'])
        config['paleta_colores'] = cls.PALETAS[tema_config['paleta']]
        config['font'] = tema_config['font']
        
        # Agregar colores especiales
        config.update(tema_config['colores_especiales'])
        
        # Aplicar personalizaciones si existen
        if personalizaciones:
            config.update(personalizaciones)
        
        return config
    
    @classmethod
    def get_paleta(cls, nombre_paleta):
        """Retorna una paleta de colores específica"""
        return cls.PALETAS.get(nombre_paleta, cls.PALETAS['gubernamental'])
    
    @classmethod
    def agregar_paleta_personalizada(cls, nombre, colores):
        """Permite agregar una nueva paleta de colores"""
        cls.PALETAS[nombre] = colores
    
    @classmethod
    def verificar_fonts_disponibles(cls):
        """Verifica que las fuentes estén disponibles en el sistema"""
        try:
            from matplotlib import font_manager
            fuentes_sistema = [f.name for f in font_manager.fontManager.ttflist]
            
            disponibles = {}
            for tipo, nombre in cls.FUENTES.items():
                disponibles[tipo] = nombre in fuentes_sistema
            
            return disponibles
        except ImportError:
            return {tipo: False for tipo in cls.FUENTES}

# Funciones de conveniencia para uso directo
def get_estilos_gobierno():
    """Retorna estilos para gráficas gubernamentales"""
    return EstilosGlobales.get_configuracion_completa('barras_verticales', 'gobierno')

def get_estilos_empresa():
    """Retorna estilos para gráficas empresariales"""
    return EstilosGlobales.get_configuracion_completa('barras_verticales', 'empresa_privada')

def aplicar_estilos_globales(parametros_grafica, tema='gobierno'):
    """
    Aplica estilos globales a los parámetros de una gráfica
    Los parámetros específicos de la gráfica tienen prioridad sobre los globales
    """
    estilos_globales = EstilosGlobales.get_configuracion_completa('barras_verticales', tema)
    
    # Los parámetros específicos sobrescriben los globales
    for key, value in estilos_globales.items():
        if key not in parametros_grafica:
            parametros_grafica[key] = value
    
    return parametros_grafica
