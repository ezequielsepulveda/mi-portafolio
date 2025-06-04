from django.contrib import admin
from .models import Doctor, Paciente, TipoDiagnostico, Cita, HistorialPaciente

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('user', 'especialidad', 'telefono')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')

@admin.register(TipoDiagnostico)
class TipoDiagnosticoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'prioridad_base')
    search_fields = ('nombre',)

@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'fecha_nacimiento', 'genero', 'prioridad')
    search_fields = ('nombre', 'apellido', 'telefono')
    list_filter = ('genero', 'diagnostico')

@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'doctor', 'fecha_hora', 'estado')
    list_filter = ('estado', 'doctor')
    search_fields = ('paciente__nombre', 'paciente__apellido')
    date_hierarchy = 'fecha_hora'

@admin.register(HistorialPaciente)
class HistorialPacienteAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'tipo', 'fecha', 'doctor')
    list_filter = ('tipo', 'doctor')
    search_fields = ('paciente__nombre', 'paciente__apellido', 'descripcion')
    date_hierarchy = 'fecha'