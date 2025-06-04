document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'timeGridWeek',
        locale: 'es',
        buttonText: {
            today: 'Hoy',
            month: 'Mes',
            week: 'Semana',
            day: 'Día'
        },
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        slotMinTime: '09:00:00',
        slotMaxTime: '17:00:00',
        allDaySlot: false,
        weekends: false,
        events: {{ eventos|safe }},
        eventClick: function(info) {
            const evento = info.event;
            const props = evento.extendedProps;
            
            // Actualizar el modal con la información del paciente
            document.getElementById('paciente-nombre').textContent = evento.title;
            document.getElementById('paciente-diagnostico').textContent = props.diagnostico;
            
            // Actualizar prioridad
            const prioridadBadge = document.getElementById('paciente-prioridad');
            prioridadBadge.textContent = props.prioridad >= 0.8 ? 'Alta Prioridad' :
                                        props.prioridad >= 0.5 ? 'Media Prioridad' :
                                        'Baja Prioridad';
            prioridadBadge.className = 'priority-badge ' + 
                                     (props.prioridad >= 0.8 ? 'priority-high' :
                                      props.prioridad >= 0.5 ? 'priority-medium' :
                                      'priority-low');
            
            // Actualizar detalles de la cita
            document.getElementById('cita-fecha').textContent = evento.start.toLocaleDateString();
            document.getElementById('cita-hora').textContent = evento.start.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
            
            // Actualizar estado
            const estadoBadge = document.getElementById('cita-estado');
            estadoBadge.textContent = props.estado;
            estadoBadge.className = 'badge ' + 
                                  (props.estado === 'Pendiente' ? 'bg-primary' :
                                   props.estado === 'Completada' ? 'bg-success' :
                                   props.estado === 'Reprogramada' ? 'bg-warning' :
                                   'bg-danger');

            // Actualizar botones de acciones
            const accionesContainer = document.getElementById('cita-acciones');
            accionesContainer.innerHTML = `
                <a href="/citas/${evento.id}/" class="btn btn-info btn-sm">
                    <i class="fas fa-eye"></i> Ver Detalles
                </a>
                <a href="/citas/${evento.id}/editar/" class="btn btn-warning btn-sm">
                    <i class="fas fa-edit"></i> Editar
                </a>
                <a href="/citas/${evento.id}/eliminar/" class="btn btn-danger btn-sm">
                    <i class="fas fa-trash"></i> Eliminar
                </a>
            `;
            
            // Mostrar el modal
            const modal = new bootstrap.Modal(document.getElementById('citaModal'));
            modal.show();
        }
    });
    calendar.render();
});