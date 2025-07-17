# Sitio Web - Agencia Digital

## Estructura del Proyecto

```
sitio_web/
├── archivos_html/           # Páginas HTML
│   ├── index.html
│   ├── graficas-python.html
│   ├── graficas-r.html
│   └── prueba_componentes.html
├── componentes/             # Componentes JavaScript
│   ├── header.js           # Componente de header
│   ├── footer.js           # Componente de footer
│   ├── menu.js             # Funcionalidad de menú
│   └── main.js             # Scripts centralizados
├── estilos/                # Archivos CSS
│   └── style.css           # Estilos principales
└── imagenes_general/       # Imágenes del sitio
    ├── Logo Gobierno 2025.svg
    ├── Menu.svg
    ├── Pattern.svg
    ├── fb.svg
    └── twitter.svg
```

## Componentes Disponibles

### 1. Header (`<header-gob>`)
- Logo del gobierno
- Menú desplegable
- Navegación responsive

### 2. Footer (`<footer-gob>`)
- Enlaces oficiales
- Redes sociales
- Información legal

### 3. Componentes de UI

#### KPIs
```html
<div class="contenedor-kpis">
  <div class="kpi-box">
    <div class="kpi-body">
      <h3 class="kpi-titulo">Título</h3>
      <div class="texto1-caja positivo">25</div>
      <div class="texto2-caja">Descripción</div>
    </div>
    <div class="kpi-footer positivo">
      <div class="texto4-caja">Categoría</div>
    </div>
  </div>
</div>
```

#### Indicadores
```html
<div class="indicadores-resumen">
  <div class="indicador-box">
    <div class="etiqueta">Nombre</div>
    <div class="contenedor-valores">
      <div class="valor-actual fondo-verde">
        <div class="porcentaje">+15%</div>
        <div class="cantidad">8</div>
      </div>
      <div class="valor-promedio">
        <div class="texto">Promedio</div>
        <div class="valor">6.5</div>
      </div>
    </div>
  </div>
</div>
```

#### Botones
```html
<div class="fila-botones">
  <div class="grupo-botones-izq">
    <button class="boton-selector activo">Opción 1</button>
    <button class="boton-selector">Opción 2</button>
  </div>
  <div class="grupo-botones-der">
    <button class="boton-doble activo">Vista 1</button>
    <button class="boton-doble">Vista 2</button>
  </div>
</div>
```

#### Tabs
```html
<div class="tabs-resumen">
  <div class="tab-resumen activo">
    <div>Tab 1</div>
  </div>
  <div class="tab-resumen">
    <div>Tab 2</div>
  </div>
</div>
```

#### Dropdowns
```html
<div class="dropdown-container">
  <button class="dropdown-toggle">
    Filtros
    <span>▼</span>
  </button>
  <div class="dropdown-content">
    <div class="dropdown-filtro">
      <label for="filtro">Filtro:</label>
      <select id="filtro">
        <option value="">Todos</option>
      </select>
    </div>
  </div>
</div>
```

## Uso Básico

### 1. Estructura HTML base
```html
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Título - Agencia Digital</title>
  
  <!-- Fuentes -->
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap" rel="stylesheet">
  <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
  
  <!-- Estilos -->
  <link rel="stylesheet" href="../estilos/style.css">
</head>
<body>
  <!-- Header -->
  <header-gob></header-gob>
  
  <!-- Título con textura -->
  <div class="franja-titulo">
    <div class="textura-superior"></div>
    <h1 class="titulo-centro">Título de la Página</h1>
  </div>

  <!-- Contenido principal -->
  <div class="page-wrapper">
    <div class="container">
      <!-- Tu contenido aquí -->
    </div>
  </div>

  <!-- Footer -->
  <footer-gob></footer-gob>

  <!-- Scripts -->
  <script src="../componentes/header.js"></script>
  <script src="../componentes/footer.js"></script>
  <script src="../componentes/main.js"></script>
</body>
</html>
```

### 2. Estilos CSS

#### Variables disponibles
```css
:root {
  --Primary-Color-GOB-MX: #611232;
  --Secundarios-Dorado-500: #A57F2C;
  --Neutro-Neutro-500: #AAAAAA;
  --Neutro-Neutro-600: #767676;
  --Text-Text-primary-enabled: #611232;
  --box-shadow-default: 0 2px 6px rgba(0, 0, 0, 0.1);
}
```

#### Clases utilitarias
- `.fondo-verde`: Fondo verde para valores positivos
- `.fondo-rojo`: Fondo rojo para valores negativos
- `.positivo`: Estilo para elementos positivos
- `.negativo`: Estilo para elementos negativos
- `.activo`: Estado activo para botones y tabs

### 3. JavaScript

#### Funciones disponibles
```javascript
// Mostrar notificación
showNotification('Mensaje', 'success'); // success, error, warning, info

// Cargar contenido dinámicamente
loadContent('url', 'containerId');

// Inicializar formularios AJAX
initForms();
```

## Archivos de Prueba

- `prueba_componentes.html`: Página que muestra todos los componentes disponibles
- `index.html`: Página principal con catálogo de gráficas

## Personalización

### Colores
Edita las variables CSS en `estilos/style.css`:
```css
:root {
  --Primary-Color-GOB-MX: #tu-color;
  --Secundarios-Dorado-500: #tu-color;
}
```

### Componentes
- Los componentes están en `componentes/`
- Cada componente es una clase que extiende `HTMLElement`
- Se registran automáticamente en `main.js`

## Notas Importantes

1. **Rutas**: Los archivos HTML deben estar en `archivos_html/` y usar rutas relativas `../`
2. **Imágenes**: Deben estar en `imagenes_general/`
3. **Fuentes**: Se cargan desde Google Fonts
4. **Dependencias**: Masonry.js se carga desde CDN solo donde se necesita

## Soporte

Para dudas o problemas, contacta al equipo de desarrollo de la Agencia Digital.
