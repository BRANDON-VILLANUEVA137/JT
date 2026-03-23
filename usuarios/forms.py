from django import forms
from .models import Usuario, Estudiante, Docente
from administracion.models import Curso


class UsuarioLoginForm(forms.Form):
    """
    Formulario de inicio de sesión personalizado.
    Permite iniciar sesión con número de documento o correo electrónico.
    """
    numero_documento = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Número de documento o correo electrónico',
            'required': True,
        }),
        label='Documento o Correo'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña',
            'required': True,
        })
    )


class UsuarioCreacionForm(forms.ModelForm):
    """
    Formulario para crear nuevos usuarios (solo Admin).
    Valida que el documento sea único en el sistema.
    """
    primer_nombre = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Primer nombre',
        })
    )
    segundo_nombre = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Segundo nombre (opcional)',
        })
    )
    primer_apellido = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Primer apellido',
        })
    )
    segundo_apellido = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Segundo apellido (opcional)',
        })
    )
    tipo_documento = forms.ChoiceField(
        choices=Usuario.TIPO_DOCUMENTO_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control',
        })
    )
    numero_documento = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Número de documento',
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Correo electrónico',
        })
    )
    rol = forms.ChoiceField(
        choices=Usuario.ROL_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control',
        })
    )
    
    # Campos opcionales para Estudiante
    codigo_estudiantil = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Código estudiantil (ej: EST-123456)',
        })
    )
    fecha_nacimiento = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
        })
    )
    nombre_acudiente = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre del acudiente',
        })
    )
    telefono_acudiente = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Teléfono del acudiente',
        })
    )
    curso = forms.ModelChoiceField(
        queryset=Curso.objects.select_related('año_lectivo').order_by('-año_lectivo__nombre', 'nombre'),
        required=False,
        empty_label='Sin curso por ahora',
        widget=forms.Select(attrs={
            'class': 'form-control',
        })
    )
    
    # Campos opcionales para Docente
    especialidad = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Especialidad docente',
        })
    )
    telefono_institucional = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Teléfono institucional',
        })
    )
    class Meta:
        model = Usuario
        fields = (
            'primer_nombre',
            'segundo_nombre',
            'primer_apellido',
            'segundo_apellido',
            'tipo_documento',
            'numero_documento',
            'email',
            'rol',
        )
    
    def clean_numero_documento(self):
        numero_documento = self.cleaned_data.get('numero_documento')
        if Usuario.objects.filter(numero_documento=numero_documento).exists():
            raise forms.ValidationError('Este número de documento ya está registrado.')
        return numero_documento
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError('Este correo electrónico ya está registrado.')
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['numero_documento']
        user.primer_nombre = self.cleaned_data['primer_nombre']
        user.segundo_nombre = self.cleaned_data['segundo_nombre']
        user.primer_apellido = self.cleaned_data['primer_apellido']
        user.segundo_apellido = self.cleaned_data['segundo_apellido']
        user.tipo_documento = self.cleaned_data['tipo_documento']
        user.numero_documento = self.cleaned_data['numero_documento']
        user.email = self.cleaned_data['email']
        user.rol = self.cleaned_data['rol']
        # Contraseña inicial = numero de documento
        user.set_password(self.cleaned_data['numero_documento'])
        user.must_change_password = True
        
        if commit:
            user.save()
        return user
    
    def get_estudiante_data(self):
        """Retorna diccionario con datos de estudiante."""
        codigo = self.cleaned_data.get('codigo_estudiantil') or f"EST-{self.cleaned_data['numero_documento']}"
        return {
            'codigo_estudiantil': codigo,
            'fecha_nacimiento': self.cleaned_data.get('fecha_nacimiento'),
            'nombre_acudiente': self.cleaned_data.get('nombre_acudiente'),
            'telefono_acudiente': self.cleaned_data.get('telefono_acudiente'),
        }

    def get_matricula_data(self):
        """Retorna curso/año para crear matrícula automática del estudiante."""
        curso = self.cleaned_data.get('curso')
        if not curso:
            return None
        return {
            'curso': curso,
            'año_lectivo': curso.año_lectivo,
        }
    
    def get_docente_data(self):
        """Retorna diccionario con datos de docente."""
        return {
            'especialidad': self.cleaned_data.get('especialidad') or 'No especificada',
            'telefono_institucional': self.cleaned_data.get('telefono_institucional'),
        }


class EstudianteActualizacionForm(forms.ModelForm):
    """
    Formulario para actualizar perfil de estudiante.
    """
    class Meta:
        model = Estudiante
        fields = (
            'nombre_acudiente',
            'telefono_acudiente',
        )
        widgets = {
            'nombre_acudiente': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'telefono_acudiente': forms.TextInput(attrs={
                'class': 'form-control',
            }),
        }


class DocenteActualizacionForm(forms.ModelForm):
    """
    Formulario para actualizar perfil de docente.
    """
    class Meta:
        model = Docente
        fields = (
            'especialidad',
            'telefono_institucional',
        )
        widgets = {
            'especialidad': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'telefono_institucional': forms.TextInput(attrs={
                'class': 'form-control',
            }),
        }
