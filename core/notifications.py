from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

class NotificationSystem:
    @staticmethod
    def notificar_registro_paciente(paciente, cita=None):
        """Envía email de bienvenida al paciente cuando se registra"""
        try:
            subject = f'Bienvenido/a {paciente.nombre} - ¡¡ Su Cita Ha Sido Registrado Exitosamente !!'
            
            # Preparar contexto para el template
            context = {
                'paciente': paciente,
                'cita': cita
            }
            
            # Renderizar mensajes
            html_message = render_to_string('core/emails/bienvenida.html', context)
            plain_message = render_to_string('core/emails/bienvenida.txt', context)
            
            # Imprimir para debugging
            print(f"Enviando correo a: {paciente.correo}")
            print(f"Mensaje: {plain_message}")
            
            # Enviar correo
            send_mail(
                subject=subject,
                message=plain_message,
                html_message=html_message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[paciente.correo],
                fail_silently=False,
            )
            
            print("Correo enviado exitosamente")
            return True
            
        except Exception as e:
            print(f"Error enviando email de bienvenida: {e}")
            return False

    @staticmethod
    def notificar_nueva_cita(cita):
        """Notifica al paciente sobre una cita reprogramada"""
        try:
            subject = 'Reprogramación de Cita Médica - GESMEDIC'
            
            # Preparar el contexto para la plantilla HTML
            context = {
                'paciente': cita.paciente,
                'cita': cita,
                'doctor': cita.doctor,
                'fecha': cita.fecha_hora.strftime('%d/%m/%Y'),
                'hora': cita.fecha_hora.strftime('%H:%M')
            }
            
            # Crear versiones HTML y texto plano del correo
            html_message = render_to_string('core/emails/reprogramacion_cita.html', context)
            plain_message = f"""
            Estimado/a {cita.paciente.nombre} {cita.paciente.apellido}

            NOTIFICACIÓN DE REPROGRAMACIÓN DE CITA

            Le informamos que su cita médica ha sido reprogramada:

            📅 Fecha: {cita.fecha_hora.strftime('%d/%m/%Y')}
            🕒 Hora: {cita.fecha_hora.strftime('%H:%M')}
            👨‍⚕️ Doctor: Dr. {cita.doctor.user.get_full_name()}
            🏥 Especialidad: {cita.doctor.get_especialidad_display()}

            Por favor, confirme su asistencia respondiendo este correo.
            En caso de no poder asistir, le agradecemos notificar con anticipación.

            Saludos cordiales,
            GESMEDIC
            """
            
            send_mail(
                subject=subject,
                message=plain_message,
                html_message=html_message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[cita.paciente.correo],
                fail_silently=False,
            )
            
            return True
            
        except Exception as e:
            print(f"Error enviando notificación de reprogramación: {e}")
            return False