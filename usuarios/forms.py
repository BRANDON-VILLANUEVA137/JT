from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario

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
        help_text='Mínimo 8 caracteres.'
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

