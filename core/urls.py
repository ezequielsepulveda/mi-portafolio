from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    # Autenticación
    path('', views.CustomLoginView.as_view(), name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('api/dashboard/stats/', views.dashboard_stats, name='dashboard_stats'),
    
    # Pacientes
    path('pacientes/', views.lista_pacientes, name='lista_pacientes'),
    path('pacientes/crear/', views.crear_paciente, name='crear_paciente'),
    path('pacientes/<int:pk>/editar/', views.editar_paciente, name='editar_paciente'),
    path('pacientes/<int:pk>/eliminar/', views.eliminar_paciente, name='eliminar_paciente'),
    path('pacientes/<int:pk>/detalle/', views.detalle_paciente, name='detalle_paciente'),
    
    # Citas
    path('citas/', views.lista_citas, name='lista_citas'),
    path('citas/crear/', views.crear_cita, name='crear_cita'),
    path('citas/<int:pk>/editar/', views.editar_cita, name='editar_cita'),
    path('citas/<int:pk>/eliminar/', views.eliminar_cita, name='eliminar_cita'),
    path('citas/<int:pk>/', views.detalle_cita, name='detalle_cita'),
    path('citas/<int:cita_id>/notificar/', views.notificar_paciente, name='notificar_paciente'),
    path('citas/<int:pk>/cambiar-estado/', views.cambiar_estado_cita, name='cambiar_estado_cita'),
    path('citas/', views.lista_citas, name='lista_citas'),  # Vista actual de lista
    path('citas/calendario/', views.calendario_citas, name='calendario_citas'),

]
