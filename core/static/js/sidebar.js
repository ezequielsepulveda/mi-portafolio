// core/static/js/sidebar.js
document.addEventListener('DOMContentLoaded', function() {
    // Botón para colapsar el sidebar
    const sidebarCollapse = document.getElementById('sidebarCollapse');
    const sidebar = document.getElementById('sidebar');
    const content = document.getElementById('content');

    if (sidebarCollapse) {
        sidebarCollapse.addEventListener('click', function() {
            sidebar.classList.toggle('active');
            content.classList.toggle('active');
        });
    }

    // Marcar el ítem activo en el sidebar
    const currentPath = window.location.pathname;
    const sidebarLinks = document.querySelectorAll('#sidebar ul li a');
    
    sidebarLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.parentElement.classList.add('active');
        }
    });

    // Ajuste automático en móviles
    function checkWidth() {
        if (window.innerWidth <= 768) {
            sidebar.classList.add('active');
            content.classList.remove('active');
        } else {
            sidebar.classList.remove('active');
            content.classList.add('active');
        }
    }

    // Verificar al cargar y al cambiar el tamaño de la ventana
    window.addEventListener('resize', checkWidth);
    checkWidth();
});