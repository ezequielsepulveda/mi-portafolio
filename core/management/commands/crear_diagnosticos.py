from django.core.management.base import BaseCommand
from core.models import TipoDiagnostico

class Command(BaseCommand):
    help = 'Crea los diagnósticos predeterminados para todas las especialidades'

    def handle(self, *args, **kwargs):
        diagnosticos_por_especialidad = {
            'traumatologia': [
                {'nombre': 'Fractura', 'prioridad_base': 0.9},
                {'nombre': 'Esguince', 'prioridad_base': 0.7},
                {'nombre': 'Luxación', 'prioridad_base': 0.8},
                {'nombre': 'Tendinitis', 'prioridad_base': 0.5},
                {'nombre': 'Contusión', 'prioridad_base': 0.4},
                {'nombre': 'Desgarro Muscular', 'prioridad_base': 0.6},
                {'nombre': 'Artritis', 'prioridad_base': 0.5},
                {'nombre': 'Bursitis', 'prioridad_base': 0.4},
                {'nombre': 'Lesión de Ligamentos', 'prioridad_base': 0.7},
                {'nombre': 'Hernia Discal', 'prioridad_base': 0.8},
                {'nombre': 'Escoliosis', 'prioridad_base': 0.5},
                {'nombre': 'Osteoporosis', 'prioridad_base': 0.6},
                {'nombre': 'Síndrome del Túnel Carpiano', 'prioridad_base': 0.4},
                {'nombre': 'Fascitis Plantar', 'prioridad_base': 0.3},
                {'nombre': 'Control Post-Operatorio', 'prioridad_base': 0.8},
                {'nombre': 'Control Rutinario', 'prioridad_base': 0.2},
            ],
            'cardiovascular': [
                {'nombre': 'Cardiopatía isquémica', 'prioridad_base': 0.9},
                {'nombre': 'Insuficiencia cardíaca', 'prioridad_base': 0.8},
                {'nombre': 'Arritmias cardíacas', 'prioridad_base': 0.7},
                {'nombre': 'Valvulopatías', 'prioridad_base': 0.7},
                {'nombre': 'Aneurisma aórtico', 'prioridad_base': 0.9},
                {'nombre': 'Enfermedad coronaria', 'prioridad_base': 0.8},
                {'nombre': 'Trombosis venosa', 'prioridad_base': 0.7},
                {'nombre': 'Hipertensión pulmonar', 'prioridad_base': 0.8},
                {'nombre': 'Control Post-Operatorio Cardíaco', 'prioridad_base': 0.9},
                {'nombre': 'Control Rutinario Cardiovascular', 'prioridad_base': 0.3},
            ],
            'neurocirugia': [
                {'nombre': 'Tumor cerebral', 'prioridad_base': 0.9},
                {'nombre': 'Aneurisma cerebral', 'prioridad_base': 0.9},
                {'nombre': 'Hidrocefalia', 'prioridad_base': 0.8},
                {'nombre': 'Hernia discal cervical', 'prioridad_base': 0.7},
                {'nombre': 'Malformación arteriovenosa', 'prioridad_base': 0.8},
                {'nombre': 'Epilepsia refractaria', 'prioridad_base': 0.7},
                {'nombre': 'Traumatismo craneoencefálico', 'prioridad_base': 0.9},
                {'nombre': 'Compresión medular', 'prioridad_base': 0.8},
                {'nombre': 'Control Post-Operatorio Neurológico', 'prioridad_base': 0.9},
                {'nombre': 'Control Rutinario Neurológico', 'prioridad_base': 0.3},
            ]
        }

        for especialidad, diagnosticos in diagnosticos_por_especialidad.items():
            self.stdout.write(
                self.style.SUCCESS(f'\nCreando diagnósticos para {especialidad}:')
            )
            for diag in diagnosticos:
                obj, created = TipoDiagnostico.objects.get_or_create(
                    nombre=diag['nombre'],
                    especialidad=especialidad,
                    defaults={'prioridad_base': diag['prioridad_base']}
                )
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Creado: {diag["nombre"]}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'⚠ Ya existe: {diag["nombre"]}')
                    )

        self.stdout.write(
            self.style.SUCCESS('\nTodos los diagnósticos han sido creados exitosamente')
        )