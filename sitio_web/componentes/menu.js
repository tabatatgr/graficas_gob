function toggleMenu(menuToggle, menuDropdown) {
  menuToggle.addEventListener('click', function (e) {
    e.stopPropagation();
    menuDropdown.style.display = menuDropdown.style.display === 'flex' ? 'none' : 'flex';
  });
  document.addEventListener('click', function (e) {
    if (!menuDropdown.contains(e.target) && !menuToggle.contains(e.target)) {
      menuDropdown.style.display = 'none';
    }
  });
}

// Uso:
const menuToggle = document.querySelector('.menu-toggle');
const menuDropdown = document.getElementById('menuDropdown');
if (menuToggle && menuDropdown) toggleMenu(menuToggle, menuDropdown);