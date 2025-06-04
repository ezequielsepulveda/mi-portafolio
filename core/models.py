from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime, time, timedelta, date
from django.utils import timezone
from django.core.validators import RegexValidator
from .ml_system import PriorityMLSystem


class Doctor(models.Model):
    ESPECIALIDAD_CHOICES = [
        ('traumatologia', 'Traumatologia'),
        ('cardiovascular', 'Cirugia Cardiovascular')
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    especialidad = models.CharField(
        max_length=20,
        choices=ESPECIALIDAD_CHOICES,
        default='traumatologia'
    )
    telefono = models.CharField(max_length=20)

    def __str__(self):
        return f'Dr. {self.user.first_name} {self.user.last_name}'

    def get_pacientes(self):
        return Paciente.objects.filter(diagnostico__especialidad=self.especialidad)
    
    
class TipoDiagnostico(models.Model):
    ESPECIALIDAD_CHOICES = [
        ('traumatologia', 'Traumatologia'),
        ('cardiovascular', 'Cirugia Cardiovascular')
    ]
    
    nombre = models.CharField(max_length=100)
    especialidad = models.CharField(
        max_length=20,
        choices=ESPECIALIDAD_CHOICES,
        default='traumatologia'
    )
    prioridad_base = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    descripcion = models.TextField(blank=True)

    @classmethod
    def initialize_default_diagnosticos(cls):
        diagnosticos_default = {
            'traumatologia': [
                ('Fractura', 0.9),
                ('Esguince', 0.7),
                ('Luxación', 0.8),
                ('Tendinitis', 0.5),
                ('Contusión', 0.4),
                ('Desgarro Muscular', 0.6),
                ('Artritis', 0.5),
                ('Control Post-Operatorio', 0.8),
                ('Control Rutinario', 0.2)
            ],
            'cardiovascular': [
                ('Cardiopatía isquémica', 0.9),
                ('Insuficiencia cardíaca', 0.8),
                ('Arritmias cardíacas', 0.7),
                ('Valvulopatías', 0.7),
                ('Control Post-Operatorio Cardíaco', 0.9)
            ]
        }

        for especialidad, diagnosticos in diagnosticos_default.items():
            for nombre, prioridad in diagnosticos:
                cls.objects.get_or_create(
                    nombre=nombre,
                    especialidad=especialidad,
                    defaults={'prioridad_base': prioridad}
                )

    class Meta:
        ordering = ['especialidad', 'nombre']

    def __str__(self):
        return f"{self.nombre} ({self.get_especialidad_display()})"

class Paciente(models.Model):
    GENERO_CHOICES = [
        ('', 'Seleccione...'),  # Añade esta línea
        ('M', 'Masculino'),
        ('F', 'Femenino')
    ]
    
    genero = models.CharField(
        max_length=1,
        choices=GENERO_CHOICES,
        default=''  # Añade esto si usas la primera opción
    )
    rut = models.CharField(
        max_length=12,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\d{7,8}-[\dkK]$',
                message='Formato de RUT inválido. Debe ser como "12345678-9"'
            )
        ]
    )
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES)
    telefono = models.CharField(max_length=20)
    correo = models.EmailField()
    direccion = models.TextField(blank=True, default="")
    fecha_registro = models.DateTimeField(auto_now_add=True)
    diagnostico = models.ForeignKey('TipoDiagnostico', on_delete=models.SET_NULL, null=True)
    motivo_consulta = models.TextField(blank=True, default="")
    prioridad = models.FloatField(default=0)
    ultima_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    def calcular_edad(self):
        today = date.today()
        return today.year - self.fecha_nacimiento.year - (
            (today.month, today.day) < 
            (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )

    def actualizar_prioridad(self):
        """Actualiza la prioridad del paciente usando ML"""
        try:
            ml_system = PriorityMLSystem()
            antigua_prioridad = self.prioridad
            nueva_prioridad = ml_system.predecir_prioridad(self)
            
            if abs(nueva_prioridad - antigua_prioridad) > 0.1:
                self.prioridad = nueva_prioridad
                self.save(update_fields=['prioridad'])
                
                # Registrar cambio en el historial
                HistorialPaciente.objects.create(
                    paciente=self,
                    tipo='PRIORIDAD',
                    descripcion=f'Prioridad actualizada de {antigua_prioridad:.2f} a {nueva_prioridad:.2f}'
                )
            
            return nueva_prioridad
        except Exception as e:
            print(f"Error actualizando prioridad: {e}")
            return self.prioridad

    def save(self, *args, **kwargs):
        if not self.pk:  # Si es nuevo paciente
            super().save(*args, **kwargs)  # Guardar primero para tener ID
            self.actualizar_prioridad()
        else:
            super().save(*args, **kwargs)

class Cita(models.Model):
    ESTADO_CHOICES = [
        ('P', 'Pendiente'),
        ('C', 'Completada'),
        ('R', 'Reprogramada'),
        ('N', 'No Asistió')
    ]
    
    paciente = models.ForeignKey('Paciente', on_delete=models.CASCADE)
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE)
    fecha_hora = models.DateTimeField()
    estado = models.CharField(max_length=1, choices=ESTADO_CHOICES, default='P')
    notas = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['fecha_hora']

    def __str__(self):
        return f"Cita: {self.paciente} - {self.fecha_hora}"

    @staticmethod
    def encontrar_siguiente_horario_disponible(doctor):
        """Encuentra el siguiente horario disponible para una cita"""
        HORA_INICIO = 7  # 9 AM
        HORA_FIN = 24    # 5 PM
        DURACION_CITA = 30  # minutos
        
        # Usar timezone.localtime() para obtener la hora local
        hora_actual = timezone.localtime()
        
        # Redondear a la siguiente marca de 30 minutos
        minutos = ((hora_actual.minute // DURACION_CITA) + 1) * DURACION_CITA
        hora_inicio = hora_actual.replace(minute=0, second=0, microsecond=0)
        
        if minutos >= 60:
            hora_inicio = hora_inicio + timedelta(hours=1)
            minutos = 0
        
        hora_inicio = hora_inicio.replace(minute=minutos)

        if hora_inicio.hour >= HORA_FIN:
            # Si es después del horario de atención
            siguiente_dia = hora_inicio.date() + timedelta(days=1)
            hora_inicio = datetime.combine(siguiente_dia, time(HORA_INICIO, 0))
            hora_inicio = timezone.make_aware(hora_inicio)
        elif hora_inicio.hour < HORA_INICIO:
            # Si es antes del horario de atención
            hora_inicio = hora_inicio.replace(hour=HORA_INICIO, minute=0)
        
        # Asegurarse de que hora_inicio tenga timezone
        if timezone.is_naive(hora_inicio):
            hora_inicio = timezone.make_aware(hora_inicio)

        # Buscar el siguiente horario disponible
        hora_propuesta = hora_inicio
        while True:
            # Verificar si es día laboral (lunes a viernes)
            if hora_propuesta.weekday() < 6:  # 0 = Lunes, 4 = Viernes
                # Verificar si es horario laboral
                if HORA_INICIO <= hora_propuesta.hour < HORA_FIN:
                    # Verificar si el horario está disponible
                    if not Cita.objects.filter(
                        doctor=doctor,
                        fecha_hora=hora_propuesta,
                        estado='P'
                    ).exists():
                        return hora_propuesta

            # Avanzar al siguiente intervalo
            hora_propuesta += timedelta(minutes=DURACION_CITA)

            # Si pasamos el horario de cierre, ir al siguiente día
            if hora_propuesta.hour >= HORA_FIN:
                siguiente_dia = hora_propuesta.date() + timedelta(days=1)
                hora_propuesta = datetime.combine(siguiente_dia, time(HORA_INICIO, 0))
                hora_propuesta = timezone.make_aware(hora_propuesta)


class HistorialPaciente(models.Model):
    TIPO_CHOICES = [
        ('CITA', 'Cita Médica'),
        ('DIAGNOSTICO', 'Cambio de Diagnóstico'),
        ('PRIORIDAD', 'Cambio de Prioridad'),
        ('OTRO', 'Otro')
    ]

    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    tipo = models.CharField(
        max_length=50, 
        choices=TIPO_CHOICES,
        default='OTRO'  # Añadimos un valor por defecto
    )
    descripcion = models.TextField(blank=True, default="")
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = 'Historial de Paciente'
        verbose_name_plural = 'Historial de Pacientes'
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.paciente} - {self.tipo} - {self.fecha.strftime('%d/%m/%Y')}"