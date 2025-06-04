from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from core.models import Paciente, TipoDiagnostico, Doctor, Cita
from datetime import datetime, timedelta, date
from core.ml_system import PriorityMLSystem
import numpy as np
import random
import pytz

class Command(BaseCommand):
    help = 'Crea datos de prueba para el sistema'

    def handle(self, *args, **options):
        # Verificar doctor
        doctor = Doctor.objects.first()
        if not doctor:
            self.stdout.write('No hay doctores en el sistema. Crea un usuario doctor primero.')
            return

        # Inicializar sistema ML
        ml_system = PriorityMLSystem()

        # Crear y entrenar modelo ML con datos sintéticos
        X_train = np.array([
            # [edad_norm, prior_base, genero, tiempo_espera, asistencia]
            [0.2, 0.9, 1.0, 0.1, 1.0],  # Joven, alta prioridad
            [0.4, 0.7, 0.0, 0.2, 0.9],  # Adulto joven, media prioridad
            [0.6, 0.5, 1.0, 0.3, 0.8],  # Adulto, media prioridad
            [0.8, 0.3, 0.0, 0.4, 0.7],  # Adulto mayor, baja prioridad
            [0.3, 0.8, 0.5, 0.5, 1.0],  # Joven, alta prioridad
            [0.7, 0.4, 1.0, 0.6, 0.9],  # Adulto mayor, media prioridad
            [0.5, 0.6, 0.0, 0.7, 0.8],  # Adulto, media prioridad
            [0.9, 0.2, 1.0, 0.8, 0.7],  # Anciano, baja prioridad
            [0.1, 1.0, 0.5, 0.9, 1.0],  # Niño, alta prioridad
            [0.4, 0.5, 0.0, 1.0, 0.9],  # Adulto joven, media prioridad
        ])

        y_train = np.array([
            0.85,  # Alta prioridad (joven + diagnóstico grave)
            0.65,  # Media-alta prioridad
            0.55,  # Media prioridad
            0.45,  # Media-baja prioridad
            0.75,  # Alta prioridad
            0.50,  # Media prioridad
            0.60,  # Media prioridad
            0.35,  # Baja prioridad
            0.90,  # Muy alta prioridad (niño + diagnóstico grave)
            0.55,  # Media prioridad
        ])

        # Entrenar modelo
        ml_system.scaler.fit(X_train)
        ml_system.model.fit(X_train, y_train)
        ml_system.save_model()

        # Crear diagnósticos
        diagnosticos = [
            {'nombre': 'Fractura', 'prioridad_base': 0.9},
            {'nombre': 'Luxación', 'prioridad_base': 0.8},
            {'nombre': 'Esguince', 'prioridad_base': 0.7},
            {'nombre': 'Tendinitis', 'prioridad_base': 0.5},
            {'nombre': 'Control Rutinario', 'prioridad_base': 0.3}
        ]

        for diag in diagnosticos:
            TipoDiagnostico.objects.get_or_create(
                nombre=diag['nombre'],
                defaults={'prioridad_base': diag['prioridad_base']}
            )

        # Datos para pacientes
        nombres = ['Juan', 'María', 'Pedro', 'Ana', 'Luis', 'Carmen', 'José', 'Isabel', 'Miguel', 'Laura']
        apellidos = ['García', 'Rodríguez', 'López', 'Martínez', 'González', 'Pérez', 'Sánchez', 'Romero', 'Torres', 'Díaz']
        
        # Fecha base
        fecha_base = timezone.now()
        
        # Crear pacientes
        for i in range(12):
            # Determinar edad
            if i < 3:  # Menores
                edad = random.randint(5, 17)
            elif i < 8:  # Adultos
                edad = random.randint(18, 59)
            else:  # Mayores
                edad = random.randint(60, 85)
            
            fecha_nacimiento = date.today() - timedelta(days=edad*365)
            
            # Seleccionar diagnóstico según prioridad
            if i < 4:  # Alta prioridad
                diagnostico = TipoDiagnostico.objects.filter(prioridad_base__gte=0.8).first()
            elif i < 8:  # Media prioridad
                diagnostico = TipoDiagnostico.objects.filter(prioridad_base__range=(0.5, 0.7)).first()
            else:  # Baja prioridad
                diagnostico = TipoDiagnostico.objects.filter(prioridad_base__lte=0.4).first()

            # Crear paciente
            paciente = Paciente.objects.create(
                nombre=random.choice(nombres),
                apellido=random.choice(apellidos),
                fecha_nacimiento=fecha_nacimiento,
                genero=random.choice(['M', 'F']),
                telefono=f'9{random.randint(10000000, 99999999)}',
                correo=f'paciente{i+1}@example.com',
                diagnostico=diagnostico,
                motivo_consulta=f'Motivo de consulta del paciente {i+1}'
            )

            # Crear cita
            hora_base = 9  # Comenzar a las 9 AM
            minutos = 0 if i % 2 == 0 else 30
            
            hora_cita = fecha_base.replace(
                hour=hora_base + (i % 8),
                minute=minutos,
                second=0,
                microsecond=0
            )

            if hora_cita.hour >= 17:  # Si pasa de las 5 PM
                hora_cita = hora_cita + timedelta(days=1)  # Siguiente día
                hora_cita = hora_cita.replace(hour=9)  # Comenzar a las 9 AM

            Cita.objects.create(
                paciente=paciente,
                doctor=doctor,
                fecha_hora=hora_cita,
                estado='P'
            )

        self.stdout.write(self.style.SUCCESS('Datos de prueba creados exitosamente'))