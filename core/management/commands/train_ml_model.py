from django.core.management.base import BaseCommand
from core.models import Paciente
from core.ml_system import PriorityMLSystem

class Command(BaseCommand):
    help = 'Entrena el modelo ML con todos los datos disponibles'

    def handle(self, *args, **options):
        pacientes = Paciente.objects.all()
        
        if len(pacientes) < 10:
            self.stdout.write(self.style.WARNING(
                'No hay suficientes pacientes para entrenar el modelo'
            ))
            return
            
        ml_system = PriorityMLSystem()
        success = ml_system.entrenar(pacientes)
        
        if success:
            self.stdout.write(self.style.SUCCESS(
                'Modelo ML entrenado exitosamente'
            ))
        else:
            self.stdout.write(self.style.ERROR(
                'Error entrenando el modelo ML'
            ))