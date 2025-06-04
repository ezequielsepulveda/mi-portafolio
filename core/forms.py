from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm 
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from .models import Doctor, Paciente, Cita, TipoDiagnostico


class CustomLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remover labels
        self.fields['username'].label = ''
        self.fields['password'].label = ''
        
        # Añadir placeholders
        self.fields['username'].widget.attrs.update({
            'placeholder': 'Usuario',
            'class': 'form-control'
        })
        self.fields['password'].widget.attrs.update({
            'placeholder': 'Contraseña',
            'class': 'form-control'
        })




class DoctorRegistrationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remover los asteriscos y personalizar las etiquetas
        self.fields['username'].label = 'Usuario'
        self.fields['email'].label = 'Correo electrónico'
        self.fields['first_name'].label = 'Nombre'
        self.fields['last_name'].label = 'Apellido'
        self.fields['especialidad'].label = 'Especialidad'
        self.fields['telefono'].label = 'Teléfono'
        self.fields['password1'].label = 'Contraseña'
        self.fields['password2'].label = 'Confirmar contraseña'

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'ejemplo@correo.com',
            'style': 'height: 38px;'
        })
    )
    
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'Nombre',
            'style': 'height: 38px;'
        })
    )
    
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'Apellido',
            'style': 'height: 38px;'
        })
    )

    ESPECIALIDAD_CHOICES = [
        ('', 'Seleccione especialidad...'),
        ('traumatologia', 'Traumatología'),
        ('cardiovascular', 'Cardiovascular'),
    ]
    
    especialidad = forms.ChoiceField(
        choices=ESPECIALIDAD_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control form-control-sm'
        })
    )

    telefono = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'Ingrese teléfono'
        })
    )

    class Meta:
        model = User
        fields = [
            'username', 
            'email', 
            'first_name', 
            'last_name', 
            'password1', 
            'password2',
            'especialidad',
            'telefono'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar los mensajes de ayuda para que sean más cortos
        self.fields['username'].help_text = 'Requerido. 150 caracteres máximo.'
        self.fields['password1'].help_text = 'Mínimo 8 caracteres.'

class PacienteForm(forms.ModelForm):

    diagnostico = forms.ModelChoiceField(
        queryset=TipoDiagnostico.objects.all(),
        empty_label="Seleccione diagnóstico...",
        widget=forms.Select(attrs={
            'class': 'form-control',
            'placeholder': 'Seleccione diagnóstico'
        })
    )

    rut = forms.CharField(
        max_length=12,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': '12345678-9',
                'pattern': '^\\d{7,8}-[\\dkK]$'

            }
        )
    )

    
    telefono = forms.CharField(
        required=True,
        max_length=9,
        validators=[
            RegexValidator(
                regex=r'^9\d{8}$',
                message='El número debe comenzar con 9 y tener 9 dígitos'
            )
        ],
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'type': 'tel',
                'pattern': '9[0-9]{8}',
                'maxlength': '9',
                'placeholder': '9 XXXX XXXX'
            }
        )
    )
    correo = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'ejemplo@correo.com'
            }
        )
    )
    direccion = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese la dirección completa (calle, número, comuna, ciudad)',
                'rows': 2,  # Ajusta el número de filas visibles
                'style': 'resize: vertical;', # Permite redimensionar verticalmente
            }
        ),
        help_text='Incluya todos los detalles necesarios para ubicar la dirección'
    )
    class Meta:
        model = Paciente
        fields = ['rut','nombre', 'apellido', 'fecha_nacimiento', 'genero', 
                 'telefono', 'correo', 'direccion', 'diagnostico', 
                 'motivo_consulta']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
            'motivo_consulta': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field != 'telefono':  # Excluimos teléfono porque ya tiene sus propios atributos
                self.fields[field].widget.attrs.update({'class': 'form-control'})
                self.fields['direccion'].label = "Dirección Completa"


class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['paciente', 'fecha_hora', 'notas']
        widgets = {
            'fecha_hora': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
            'notas': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fecha_hora'].input_formats = ('%Y-%m-%dT%H:%M',)