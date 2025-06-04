document.addEventListener('DOMContentLoaded', function() {
    const logoutForm = document.getElementById('logout-form');
    if (logoutForm) {
        logoutForm.addEventListener('submit', function(e) {
            if (!confirm('¿Estás seguro que deseas cerrar sesión?')) {
                e.preventDefault();
            }
        });
    }
});