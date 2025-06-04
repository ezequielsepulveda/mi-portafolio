from django.core.management.base import BaseCommand
from core.notifications import NotificationSystem

class Command(BaseCommand):
    help = 'Envía recordatorios de citas programadas'

    def handle(self, *args, **options):
        NotificationSystem.enviar_recordatorios_diarios()
        self.stdout.write(self.style.SUCCESS('Recordatorios enviados exitosamente'))