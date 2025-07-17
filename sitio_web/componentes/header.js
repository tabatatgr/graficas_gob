class HeaderGob extends HTMLElement {
  connectedCallback() {
    this.innerHTML = `
      <header class="barra-logo">
        <div class="logo-titulo">
          <img src="../imagenes_general/Logo Gobierno 2025.svg" alt="Logo del gobierno" class="logo-izquierdo" />
        </div>
        <div class="menu-dropdown-wrapper">
          <button class="menu-toggle" id="menuToggle">
            <img src="../imagenes_general/Menu.svg" alt="Menú" width="30" height="30" />
          </button>
          <div class="menu-dropdown" id="menuDropdown">
            <a href="index.html">Inicio</a>
            <a href="graficas-python.html">Python</a>
            <a href="graficas-r.html">RStudio</a>
          </div>
        </div>
      </header>
    `;

    // Lógica simple para mostrar/ocultar el menú
    const toggle = this.querySelector('#menuToggle');
    const dropdown = this.querySelector('#menuDropdown');
    if (toggle && dropdown) {
      toggle.addEventListener('click', (e) => {
        e.stopPropagation();
        dropdown.classList.toggle('show');
      });
      document.addEventListener('click', () => {
        dropdown.classList.remove('show');
      });
    }
  }
}