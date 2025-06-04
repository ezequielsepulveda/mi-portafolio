import json
from os import truncate
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.views import LoginView
from django.urls import reverse, reverse_lazy
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import logout
from .forms import CustomLoginForm
from core import notifications
from .forms import DoctorRegistrationForm, PacienteForm, CitaForm
from .models import Doctor, HistorialPaciente, Paciente, Cita, TipoDiagnostico
from datetime import date, datetime, time, timedelta
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.db.models import Count


class CustomLoginView(LoginView):
    template_name = 'core/login.html'
    redirect_authenticated_user = True
    form_class = CustomLoginForm  # Añade esta línea


    def get_success_url(self):
        return reverse_lazy('dashboard')

    def form_invalid(self, form):
        messages.error(self.request, 'Usuario o contraseña incorrectos')
        return super().form_invalid(form)
    
def logout_view(request):
    logout(request)
    return redirect('login')

# Busca la función register y reemplázala
def register(request):
    if request.method == 'POST':
        form = DoctorRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                especialidad = form.cleaned_data['especialidad']
                
                Doctor.objects.create(
                    user=user,
                    especialidad=especialidad,
                    telefono=form.cleaned_data['telefono']
                )
                
                messages.success(request, f'Cuenta creada exitosamente para {user.username}!')
                return redirect('login')
            except Exception as e:
                messages.error(request, f'Error al crear la cuenta: {str(e)}')
                User.objects.filter(username=form.cleaned_data['username']).delete()
    else:
        form = DoctorRegistrationForm()
    
    # Obtener diagnósticos por especialidad
    diagnosticos = {}
    for esp, _ in TipoDiagnostico.ESPECIALIDAD_CHOICES:
        diagnosticos[esp] = list(TipoDiagnostico.objects.filter(
            especialidad=esp
        ).values('id', 'nombre'))
    
    return render(request, 'core/register.html', {
        'form': form,
        'diagnosticos_json': json.dumps(diagnosticos)
    })

    
@login_required
def dashboard(request):
    doctor = Doctor.objects.get(user=request.user)
    today = timezone.now().date()
    
    # Obtener datos para los últimos 7 días
    fechas = [(today - timedelta(days=i)) for i in range(6, -1, -1)]
    
    # Modificamos la consulta de próximas citas para incluir más días
    proximas_citas = Cita.objects.filter(
        doctor=doctor,
        fecha_hora__gte=timezone.now(),  # Cambiamos a gte para incluir la hora actual
        estado='P'
    ).select_related(
        'paciente', 
        'paciente__diagnostico'
    ).order_by('fecha_hora')[:10]  # Aumentamos a 10 para ver más citas futuras

    context = {
        # Mantenemos todas las estadísticas existentes
        'citas_hoy': Cita.objects.filter(
            doctor=doctor,
            fecha_hora__date=today
        ).count(),
        
        'pacientes_espera': Cita.objects.filter(
            doctor=doctor,
            estado='P'
        ).count(),
        
        'atendidos': Cita.objects.filter(
            doctor=doctor,
            estado='C'
        ).count(),
        
        'total_pacientes': Paciente.objects.filter(
            cita__doctor=doctor
        ).distinct().count(),
        
        'today': today,  # Ya tienes esto correctamente
        'proximas_citas': proximas_citas,
        'fechas': fechas,  # Mantenemos esto para el gráfico
    }
    
    return render(request, 'core/dashboard.html', context)

def get_priority_color(priority):
    """Retorna el color según la prioridad"""
    if priority >= 0.8:
        return '#e74a3b'  # Rojo - Alta prioridad
    elif priority >= 0.5:
        return '#f6c23e'  # Amarillo - Media prioridad
    else:
        return '#1cc88a'  # Verde - Baja prioridad
    
@login_required
def dashboard_stats(request):
    doctor = Doctor.objects.get(user=request.user)
    today = timezone.now().date()
    start_date = today - timedelta(days=6)

    print(f"\nVerificando registros del {start_date} al {today}")

    # Primero obtenemos todos los pacientes y los organizamos por fecha
    registros_diarios = {}
    
    # Inicializamos todas las fechas con 0
    current_date = start_date
    while current_date <= today:
        registros_diarios[current_date] = 0
        current_date += timedelta(days=1)

    # Ahora contamos los pacientes por día
    pacientes = Paciente.objects.filter(
        diagnostico__especialidad=doctor.especialidad
    ).values('id', 'nombre', 'fecha_registro')

    print("\nContando pacientes por día:")
    for paciente in pacientes:
        fecha_registro = timezone.localtime(paciente['fecha_registro']).date()
        if fecha_registro in registros_diarios:
            registros_diarios[fecha_registro] += 1
            print(f"Paciente {paciente['nombre']} contado para {fecha_registro}")

    # Preparamos los datos para el gráfico
    fechas_registro = []
    conteos = []

    for fecha in sorted(registros_diarios.keys()):
        fechas_registro.append(fecha.strftime('%d/%m'))
        conteos.append(registros_diarios[fecha])
        print(f"Día {fecha}: {registros_diarios[fecha]} pacientes")

    response_data = {
        'fechas': fechas_registro,
        'pacientes_registrados': conteos,
        'citas_hoy': Cita.objects.filter(
            doctor=doctor,
            fecha_hora__date=today
        ).count(),
        'pacientes_espera': Cita.objects.filter(
            doctor=doctor,
            estado='P'
        ).count(),
        'citas_completadas': Cita.objects.filter(
            doctor=doctor,
            estado='C'
        ).count(),
        'total_pacientes': len(pacientes)
    }

    print("\nDatos enviados al frontend:")
    print(f"Fechas: {response_data['fechas']}")
    print(f"Registros: {response_data['pacientes_registrados']}")

    response = JsonResponse(response_data)
    response["Access-Control-Allow-Origin"] = request.META.get('HTTP_ORIGIN', '*')
    response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"
    response["Content-Type"] = "application/json"

    return response

def get_datos_semana(doctor):
    """Obtiene datos de citas para los últimos 7 días"""
    datos = []
    labels = []
    today = timezone.now().date()
    
    for i in range(6, -1, -1):
        fecha = today - timedelta(days=i)
        citas = Cita.objects.filter(
            doctor=doctor,
            fecha_hora__date=fecha
        ).count()
        
        labels.append(fecha.strftime('%d/%m'))
        datos.append(citas)
    
    return {
        'labels': labels,
        'datos': datos
    }

def get_datos_diagnosticos():
    """Obtiene estadísticas de diagnósticos"""
    diagnosticos = TipoDiagnostico.objects.all()
    datos = []
    labels = []
    
    for diagnostico in diagnosticos:
        count = Paciente.objects.filter(diagnostico=diagnostico).count()
        if count > 0:  # Solo incluir diagnósticos con pacientes
            labels.append(diagnostico.nombre)
            datos.append(count)
    
    return {
        'labels': labels,
        'datos': datos
    }

def get_datos_edades():
    """Obtiene distribución de edades de pacientes"""
    rangos = [(0, 18), (19, 30), (31, 50), (51, 70), (71, 120)]
    labels = ['0-18', '19-30', '31-50', '51-70', '71+']
    datos = []
    
    for rango in rangos:
        count = Paciente.objects.filter(
            fecha_nacimiento__year__lte=timezone.now().year - rango[0],
            fecha_nacimiento__year__gt=timezone.now().year - rango[1]
        ).count()
        datos.append(count)
    
    return {
        'labels': labels,
        'datos': datos
    }

@login_required
def lista_pacientes(request):
    doctor = Doctor.objects.get(user=request.user)
    pacientes = doctor.get_pacientes()
    
    # Obtener parámetros de filtro
    prioridad_filtro = request.GET.get('prioridad')
    diagnostico_filtro = request.GET.get('diagnostico')
    
    # Aplicar filtros
    if prioridad_filtro:
        if prioridad_filtro == 'alta':
            pacientes = pacientes.filter(prioridad__gte=0.8)
        elif prioridad_filtro == 'media':
            pacientes = pacientes.filter(prioridad__range=(0.5, 0.79))
        elif prioridad_filtro == 'baja':
            pacientes = pacientes.filter(prioridad__lt=0.5)
    
    if diagnostico_filtro:
        pacientes = pacientes.filter(diagnostico=diagnostico_filtro)
    
    # Obtener diagnósticos para el filtro
    diagnosticos = TipoDiagnostico.objects.filter(especialidad=doctor.especialidad)
    
    for paciente in pacientes:
        paciente.proxima_cita = Cita.objects.filter(
            paciente=paciente,
            fecha_hora__gte=timezone.now(),
            estado__in=['P', 'R']
        ).order_by('fecha_hora').first()
    
    context = {
        'pacientes': pacientes,
        'diagnosticos': diagnosticos,
        'prioridad_actual': prioridad_filtro,
        'diagnostico_actual': diagnostico_filtro
    }
    
    return render(request, 'core/pacientes/lista_pacientes.html', context)

@login_required
def crear_paciente(request):
    doctor = Doctor.objects.get(user=request.user)
    
    # Inicializar diagnósticos si no existen
    TipoDiagnostico.initialize_default_diagnosticos()
    
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            try:
                # Guardar paciente
                paciente = form.save(commit=False)
                paciente.save()
                
                # Encontrar horario disponible
                fecha_hora = Cita.encontrar_siguiente_horario_disponible(doctor)
                
                if fecha_hora:
                    # Crear la cita
                    cita = Cita.objects.create(
                        paciente=paciente,
                        doctor=doctor,
                        fecha_hora=fecha_hora,
                        estado='P'
                    )
                    
                    # Enviar notificación con la cita incluida
                    try:
                        from core.notifications import NotificationSystem
                        NotificationSystem.notificar_registro_paciente(paciente, cita)
                        messages.success(request, 'Paciente registrado exitosamente. Se ha enviado un correo de confirmación.')
                    except Exception as e:
                        print(f"Error enviando correo: {e}")
                        messages.success(request, 'Paciente registrado exitosamente. No se pudo enviar el correo de confirmación.')
                
                return redirect('lista_pacientes')
                
            except Exception as e:
                print(f"Error en el proceso de registro: {e}")
                messages.error(request, f'Error en el proceso de registro: {str(e)}')
    else:
        form = PacienteForm()
        # Filtrar diagnósticos por especialidad del doctor
        form.fields['diagnostico'].queryset = TipoDiagnostico.objects.filter(
            especialidad=doctor.especialidad
        )

    return render(request, 'core/pacientes/crear_paciente.html', {
        'form': form
    })

@login_required
def editar_paciente(request, pk):
    paciente = get_object_or_404(Paciente, pk=pk)
    
    if request.method == 'POST':
        # Solo actualizar datos de contacto
        paciente.telefono = request.POST.get('telefono')
        paciente.correo = request.POST.get('correo')
        paciente.save()
        
        messages.success(request, 'Datos de contacto actualizados exitosamente')
        return redirect('lista_pacientes')
    
    return render(request, 'core/pacientes/editar_paciente.html', {
        'paciente': paciente
    })

@login_required
def eliminar_paciente(request, pk):
    paciente = get_object_or_404(Paciente, pk=pk)
    if request.method == 'POST':
        paciente.delete()
        messages.success(request, 'Paciente eliminado exitosamente')
        return redirect('lista_pacientes')
    
    return render(request, 'core/pacientes/eliminar_paciente.html', {
        'paciente': paciente
    })

@login_required
def lista_citas(request):
    doctor = Doctor.objects.get(user=request.user)
    
    # Obtener el estado del filtro
    estado = request.GET.get('estado')
    
    # Consulta base
    citas = Cita.objects.filter(doctor=doctor)
    
    # Aplicar filtro por estado
    if estado in ['P', 'C', 'R', 'N']:
        citas = citas.filter(estado=estado)
    
    # Ordenar por fecha_hora y optimizar consultas
    citas = citas.select_related('paciente', 'paciente__diagnostico').order_by('fecha_hora')
    
    context = {
        'citas': citas,
        'estados': {
            'P': 'Pendientes',
            'C': 'Completadas',
            'R': 'Reprogramadas',
            'N': 'No Asistió'
        }
    }
    
    return render(request, 'core/citas/lista_citas.html', context)

@login_required
def crear_cita(request):
    if request.method == 'POST':
        form = CitaForm(request.POST)
        if form.is_valid():
            cita = form.save(commit=False)
            cita.doctor = Doctor.objects.get(user=request.user)
            cita.save()
            messages.success(request, 'Cita creada exitosamente')
            return redirect('lista_citas')
    else:
        form = CitaForm()
    
    return render(request, 'core/citas/crear_cita.html', {
        'form': form
    })

@login_required
def editar_cita(request, pk):
    cita = get_object_or_404(Cita, pk=pk)
    
    if request.method == 'POST':
        form = CitaForm(request.POST, instance=cita)
        if form.is_valid():
            cita_anterior = Cita.objects.get(pk=pk)
            cita_actualizada = form.save(commit=False)
            
            # Verificar si la fecha/hora ha cambiado
            if cita_anterior.fecha_hora != cita_actualizada.fecha_hora:
                cita_actualizada.estado = 'R'  # Marcar como reprogramada
                try:
                    # Registrar el cambio en el historial
                    HistorialPaciente.objects.create(
                        paciente=cita_actualizada.paciente,
                        doctor=request.user.doctor,
                        tipo='CITA',
                        descripcion=f'Cita reprogramada para {cita_actualizada.fecha_hora.strftime("%d/%m/%Y %H:%M")}'
                    )
                    
                    # Enviar notificación
                    notifications.NotificationSystem.notificar_nueva_cita(cita_actualizada)
                    messages.success(request, 'Cita reprogramada exitosamente. Se ha enviado una notificación al paciente.')
                except Exception as e:
                    print(f"Error en el proceso de reprogramación: {e}")
                    messages.warning(request, 'Cita reprogramada, pero hubo un error en la notificación.')
            
            cita_actualizada.save()
            return redirect('lista_citas')
    else:
        form = CitaForm(instance=cita)
    
    return render(request, 'core/citas/editar_cita.html', {
        'form': form,
        'cita': cita
    })

@login_required
def eliminar_cita(request, pk):
    cita = get_object_or_404(Cita, pk=pk)
    if request.method == 'POST':
        cita.delete()
        messages.success(request, 'Cita eliminada exitosamente')
        return redirect('lista_citas')
    
    return render(request, 'core/citas/eliminar_cita.html', {
        'cita': cita
    })

@login_required
def detalle_cita(request, pk):
    cita = get_object_or_404(Cita, pk=pk)
    return render(request, 'core/citas/detalles_citas.html', {
        'cita': cita,
        'mostrar_botones_estado': cita.estado in ['P', 'R'] 
    })

@login_required
def detalle_paciente(request, pk):
    paciente = get_object_or_404(Paciente, pk=pk)
    citas = Cita.objects.filter(paciente=paciente).order_by('-fecha_hora')
    
    return render(request, 'core/pacientes/detalle_paciente.html', {
        'paciente': paciente,
        'citas': citas
    })
@login_required
def notificar_paciente(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)
    # Aquí implementarías la lógica de notificación (email, SMS, etc.)
    messages.success(request, f'Notificación enviada a {cita.paciente}')
    return redirect('lista_citas')


@login_required
def calendario_citas(request):
    # Obtener el doctor actual
    doctor = Doctor.objects.get(user=request.user)
    
    # Calcular el rango de fechas para asegurar que incluya el día 30
    today = timezone.now()
    start_of_week = today - timedelta(days=today.weekday())  # Lunes de la semana actual
    end_of_week = start_of_week + timedelta(days=6)  # Domingo de la semana actual
    
    # Obtener todas las citas del doctor
    citas = Cita.objects.filter(
        doctor=doctor,
    ).select_related(
        'paciente',
        'paciente__diagnostico'
    )
    
    print(f"Cantidad de citas encontradas: {citas.count()}")
    
    eventos = []
    for cita in citas:
        # Debug: imprimir información de cada cita
        print(f"Procesando cita: {cita.id} - {cita.fecha_hora}")
        
        # Determinar el color según el estado
        color = {
            'P': '#4e73df',  # Azul para pendientes
            'C': '#1cc88a',  # Verde para completadas
            'R': '#f6c23e',  # Amarillo para reprogramadas
            'N': '#e74a3b',  # Rojo para no asistió
        }.get(cita.estado, '#4e73df')
        
        # Crear el evento con toda la información necesaria
        evento = {
            'id': str(cita.id),
            'title': f"{cita.paciente.nombre} {cita.paciente.apellido}",
            'start': cita.fecha_hora.isoformat(),
            'end': (cita.fecha_hora + timedelta(minutes=30)).isoformat(),
            'backgroundColor': color,
            'borderColor': color,
            'extendedProps': {
                'diagnostico': cita.paciente.diagnostico.nombre if cita.paciente.diagnostico else 'Sin diagnóstico',
                'prioridad': float(cita.paciente.prioridad),
                'estado': cita.get_estado_display(),
                'edad': cita.paciente.calcular_edad(),
                'telefono': cita.paciente.telefono,
                'correo': cita.paciente.correo
            }
        }
        eventos.append(evento)
        print(f"Evento creado: {evento}")
    
    # Convertir a JSON con indentación para mejor legibilidad en debug
    eventos_json = json.dumps(eventos, indent=2)
    print(f"JSON final: {eventos_json}")
    
    # Pasar datos adicionales para el calendario
    context = {
        'eventos': eventos_json,
        'inicio_semana': start_of_week.strftime('%Y-%m-%d'),
        'fin_semana': end_of_week.strftime('%Y-%m-%d'),
        'fecha_actual': today.strftime('%Y-%m-%d'),
    }
    
    return render(request, 'core/citas/calendario.html', context)

@login_required
def cambiar_estado_cita(request, pk):
    if request.method == 'POST':
        try:
            cita = get_object_or_404(Cita, id=pk)
            nuevo_estado = request.POST.get('estado')
            
            if nuevo_estado in ['C', 'N']:
                cita.estado = nuevo_estado
                cita.save()
                
                # Registrar el cambio en el historial
                HistorialPaciente.objects.create(
                    paciente=cita.paciente,
                    doctor=request.user.doctor,
                    tipo='CITA',
                    descripcion=f'Estado cambiado a {cita.get_estado_display()}'
                )
                
                return JsonResponse({
                    'success': True,
                    'message': 'Estado actualizado correctamente'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Estado no válido'
                })
                
        except Cita.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Cita no encontrada'
            })
            
    return JsonResponse({
        'success': False,
        'message': 'Método no permitido'
    })