/**
 * Funciones JavaScript centralizadas para el sitio web
 */

// Inicializar componentes cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
  // Registrar componentes personalizados
  if (typeof HeaderGob !== 'undefined') {
    customElements.define('header-gob', HeaderGob);
  }
  if (typeof FooterGob !== 'undefined') {
    customElements.define('footer-gob', FooterGob);
  }

  // Inicializar funcionalidades
  initDropdowns();
  initButtons();
  initTabs();
  initMasonry();
});

/**
 * Funcionalidad de dropdowns
 */
function initDropdowns() {
  const toggles = document.querySelectorAll('.dropdown-toggle');
  toggles.forEach(toggle => {
    toggle.addEventListener('click', function(e) {
      e.preventDefault();
      const content = this.nextElementSibling;
      const isVisible = content.classList.contains('visible');
      
      // Cerrar todos los dropdowns
      document.querySelectorAll('.dropdown-content').forEach(el => {
        el.classList.remove('visible');
      });
      
      // Abrir este dropdown si no estaba visible
      if (!isVisible) {
        content.classList.add('visible');
      }
    });
  });

  // Cerrar dropdown al hacer clic fuera
  document.addEventListener('click', function(e) {
    if (!e.target.closest('.dropdown-container')) {
      document.querySelectorAll('.dropdown-content').forEach(el => {
        el.classList.remove('visible');
      });
    }
  });
}

/**
 * Funcionalidad de botones selectores
 */
function initButtons() {
  const botones = document.querySelectorAll('.boton-selector, .boton-doble');
  botones.forEach(boton => {
    boton.addEventListener('click', function() {
      // Remover activo de hermanos del mismo grupo
      const hermanos = this.parentElement.querySelectorAll('.boton-selector, .boton-doble');
      hermanos.forEach(hermano => hermano.classList.remove('activo'));
      
      // Agregar activo a este botón
      this.classList.add('activo');
    });
  });
}

/**
 * Funcionalidad de tabs
 */
function initTabs() {
  const tabs = document.querySelectorAll('.tab-resumen');
  tabs.forEach(tab => {
    tab.addEventListener('click', function() {
      // Remover activo de todos los tabs
      document.querySelectorAll('.tab-resumen').forEach(t => t.classList.remove('activo'));
      
      // Agregar activo a este tab
      this.classList.add('activo');
    });
  });
}

/**
 * Inicializar Masonry para el catálogo de gráficas
 */
function initMasonry() {
  const grid = document.querySelector('.catalogo-grid');
  if (grid && typeof Masonry !== 'undefined' && typeof imagesLoaded !== 'undefined') {
    imagesLoaded(grid, function() {
      new Masonry(grid, {
        itemSelector: 'a',
        columnWidth: '.grid-sizer',
        percentPosition: true,
        gutter: 16
      });
    });
  }
}

/**
 * Función para mostrar notificaciones
 */
function showNotification(message, type = 'info') {
  const notification = document.createElement('div');
  notification.className = `notification notification-${type}`;
  notification.textContent = message;
  
  // Agregar estilos inline básicos
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 1rem 1.5rem;
    border-radius: 8px;
    color: white;
    font-weight: 500;
    z-index: 9999;
    transform: translateX(100%);
    transition: transform 0.3s ease;
  `;
  
  // Colores según tipo
  const colors = {
    info: '#3498db',
    success: '#27ae60',
    warning: '#f39c12',
    error: '#e74c3c'
  };
  notification.style.backgroundColor = colors[type] || colors.info;
  
  document.body.appendChild(notification);
  
  // Animación de entrada
  setTimeout(() => {
    notification.style.transform = 'translateX(0)';
  }, 100);
  
  // Remover después de 3 segundos
  setTimeout(() => {
    notification.style.transform = 'translateX(100%)';
    setTimeout(() => {
      document.body.removeChild(notification);
    }, 300);
  }, 3000);
}

/**
 * Función para cargar contenido dinámicamente
 */
async function loadContent(url, containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;
  
  try {
    container.innerHTML = '<div class="loading">Cargando...</div>';
    const response = await fetch(url);
    const content = await response.text();
    container.innerHTML = content;
  } catch (error) {
    container.innerHTML = '<div class="error">Error al cargar el contenido</div>';
    console.error('Error loading content:', error);
  }
}

/**
 * Función para manejar formularios
 */
function initForms() {
  const forms = document.querySelectorAll('form[data-ajax]');
  forms.forEach(form => {
    form.addEventListener('submit', async function(e) {
      e.preventDefault();
      
      const formData = new FormData(this);
      const url = this.action || window.location.href;
      const method = this.method || 'POST';
      
      try {
        const response = await fetch(url, {
          method: method,
          body: formData
        });
        
        if (response.ok) {
          showNotification('Formulario enviado correctamente', 'success');
          this.reset();
        } else {
          showNotification('Error al enviar el formulario', 'error');
        }
      } catch (error) {
        showNotification('Error de conexión', 'error');
        console.error('Form submission error:', error);
      }
    });
  });
}
