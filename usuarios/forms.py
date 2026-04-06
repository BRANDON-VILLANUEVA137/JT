from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario
import re

class LoginForm(forms.Form):
    """
    Formulario login: permite numero_documento, email o username.
    """
    login_field = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Usuario, email o documento',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña',
        })
    )

class RegisterForm(UserCreationForm):
    """
    Registro simple.
    """
    primer_nombre = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    numero_documento = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Usuario
        fields = ['username', 'primer_nombre', 'numero_documento', 'email', 'password1', 'password2']
    
    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if len(username) < 4:
            raise forms.ValidationError('El usuario debe tener al menos 4 caracteres.')
        if Usuario.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError('Este nombre de usuario ya está registrado.')
        return username

    def clean_primer_nombre(self):
        primer_nombre = self.cleaned_data.get('primer_nombre', '').strip()
        if len(primer_nombre) < 2:
            raise forms.ValidationError('El nombre debe tener al menos 2 caracteres.')
        if not re.fullmatch(r'[A-Za-zÁÉÍÓÚáéíóúÑñ ]+', primer_nombre):
            raise forms.ValidationError('El nombre solo puede contener letras y espacios.')
        return primer_nombre

    def clean_numero_documento(self):
        numero_documento = self.cleaned_data.get('numero_documento', '').strip()
        if not numero_documento.isdigit():
            raise forms.ValidationError('El número de documento solo debe contener números.')
        if len(numero_documento) < 6:
            raise forms.ValidationError('El número de documento debe tener al menos 6 dígitos.')
        if Usuario.objects.filter(numero_documento=numero_documento).exists():
            raise forms.ValidationError('Este número de documento ya está registrado.')
        return numero_documento

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if Usuario.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Este correo electrónico ya está registrado.')
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.numero_documento = self.cleaned_data['numero_documento']
        user.rol = 'comprador'  # default
        if commit:
            user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    """
    Form para editar perfil usuario: nombre, email, direccion, telefono, referencias.
    """
    def clean_primer_nombre(self):
        primer_nombre = self.cleaned_data.get('primer_nombre', '').strip()
        if len(primer_nombre) < 2:
            raise forms.ValidationError('El nombre debe tener al menos 2 caracteres.')
        if not re.fullmatch(r'[A-Za-zÁÉÍÓÚáéíóúÑñ ]+', primer_nombre):
            raise forms.ValidationError('El nombre solo puede contener letras y espacios.')
        return primer_nombre

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if Usuario.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Este correo electrónico ya está en uso.')
        return email

    def clean_telefono(self):
        telefono = (self.cleaned_data.get('telefono') or '').strip()
        if telefono and not re.fullmatch(r'[\d+\-\s()]+', telefono):
            raise forms.ValidationError('El teléfono solo puede contener números, espacios y símbolos + - ( ).')
        if telefono and len(re.sub(r'\D', '', telefono)) < 7:
            raise forms.ValidationError('Ingresa un teléfono válido de al menos 7 dígitos.')
        return telefono

    def clean_direccion_principal(self):
        direccion = (self.cleaned_data.get('direccion_principal') or '').strip()
        if direccion and len(direccion) < 10:
            raise forms.ValidationError('La dirección debe tener al menos 10 caracteres.')
        return direccion

    class Meta:
        model = Usuario
        fields = ['primer_nombre', 'email', 'direccion_principal', 'telefono', 'referencias_direccion']
        widgets = {
            'primer_nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tu primer nombre'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'tu@email.com'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono para contacto'
            }),
            'direccion_principal': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Calle, número, barrio...'
            }),
            'referencias_direccion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Cerca del supermercado, esquina azul, etc. (opcional)'
            }),
        }


class PasswordChangeCustomForm(forms.Form):
    """
    Cambio de contraseña con contraseña actual (no usa PasswordChangeForm para custom auth).
    """
    old_password = forms.CharField(
        label='Contraseña actual',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        strip=False
    )
    new_password1 = forms.CharField(
        label='Nueva contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        strip=False,
        help_text='Mín 12 chars, 1 mayús, 1 minús, 1 núm, 1 especial'
    )
    new_password2 = forms.CharField(
        label='Confirmar nueva contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        strip=False,
    )

    def __init__(self, request_user, *args, **kwargs):
        self.request_user = request_user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if old_password and not self.request_user.check_password(old_password):
            raise forms.ValidationError('Contraseña actual incorrecta.')
        return old_password

    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1')
        if len(password) < 12:
            raise forms.ValidationError('La contraseña debe tener al menos 12 caracteres.')
        if not re.search(r'[A-Z]', password):
            raise forms.ValidationError('Debe incluir al menos 1 mayúscula.')
        if not re.search(r'[a-z]', password):
            raise forms.ValidationError('Debe incluir al menos 1 minúscula.')
        if not re.search(r'\d', password):
            raise forms.ValidationError('Debe incluir al menos 1 número.')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise forms.ValidationError('Debe incluir al menos 1 carácter especial (!@#$%^&*(),.?":{}|<>).')
        if re.search(r'(.)\1{2,}', password):
            raise forms.ValidationError('No uses la misma carácter 3+ veces seguidas.')
        return password

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        return password2

    def save(self, commit=True):
        password = self.cleaned_data['new_password1']
        if commit:
            self.request_user.set_password(password)
            self.request_user.save()
        return self.request_user


class EmailChangeForm(forms.Form):
    """
    Cambio de email con autenticación de contraseña actual.
    """
    old_password = forms.CharField(
        label='Contraseña actual (para confirmar)',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        strip=False
    )
    new_email = forms.EmailField(
        label='Nuevo correo',
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
    )
    new_email_confirm = forms.EmailField(
        label='Confirmar nuevo correo',
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
    )

    def __init__(self, request_user, *args, **kwargs):
        self.request_user = request_user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if old_password and not self.request_user.check_password(old_password):
            raise forms.ValidationError('Contraseña incorrecta. Necesaria para cambiar email.')
        return old_password

    def clean_new_email(self):
        new_email = self.cleaned_data.get('new_email')
        if Usuario.objects.filter(email=new_email).exclude(pk=self.request_user.pk).exists():
            raise forms.ValidationError('Este email ya está en uso.')
        return new_email

    def clean_new_email_confirm(self):
        new_email = self.cleaned_data.get('new_email')
        new_email_confirm = self.cleaned_data.get('new_email_confirm')
        if new_email and new_email_confirm and new_email != new_email_confirm:
            raise forms.ValidationError('Los emails no coinciden.')
        return new_email_confirm

    def save(self, commit=True):
        self.request_user.email = self.cleaned_data['new_email']
        if commit:
            self.request_user.save()
        return self.request_user


class AdminUserForm(forms.ModelForm):
    """
    Form para admin editar usuario: + rol, is_active, is_staff, is_superuser.
    """
    def clean_primer_nombre(self):
        primer_nombre = self.cleaned_data.get('primer_nombre', '').strip()
        if len(primer_nombre) < 2:
            raise forms.ValidationError('El nombre debe tener al menos 2 caracteres.')
        if not re.fullmatch(r'[A-Za-zÁÉÍÓÚáéíóúÑñ ]+', primer_nombre):
            raise forms.ValidationError('El nombre solo puede contener letras y espacios.')
        return primer_nombre

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if Usuario.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Este correo electrónico ya está en uso.')
        return email

    def clean_telefono(self):
        telefono = (self.cleaned_data.get('telefono') or '').strip()
        if telefono and not re.fullmatch(r'[\d+\-\s()]+', telefono):
            raise forms.ValidationError('El teléfono solo puede contener números, espacios y símbolos + - ( ).')
        if telefono and len(re.sub(r'\D', '', telefono)) < 7:
            raise forms.ValidationError('Ingresa un teléfono válido de al menos 7 dígitos.')
        return telefono

    def clean_direccion_principal(self):
        direccion = (self.cleaned_data.get('direccion_principal') or '').strip()
        if direccion and len(direccion) < 10:
            raise forms.ValidationError('La dirección debe tener al menos 10 caracteres.')
        return direccion

    def clean(self):
        cleaned_data = super().clean()
        rol = cleaned_data.get('rol')
        is_staff = cleaned_data.get('is_staff')
        is_superuser = cleaned_data.get('is_superuser')

        if rol == 'admin' and not is_staff:
            self.add_error('is_staff', 'Un usuario con rol admin debe tener permisos de staff.')

        if is_superuser and rol != 'admin':
            self.add_error('rol', 'Solo un usuario con rol admin puede ser superusuario.')

        return cleaned_data

    class Meta:
        model = Usuario
        fields = ['primer_nombre', 'email', 'rol', 'direccion_principal', 'telefono', 'referencias_direccion', 'is_active', 'is_staff', 'is_superuser']
        widgets = {
            'primer_nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'rol': forms.Select(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion_principal': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'referencias_direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_superuser': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
