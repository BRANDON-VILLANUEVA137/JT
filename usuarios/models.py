from django.contrib.auth.models import AbstractUser
from django.db import models
import secrets

class Usuario(AbstractUser):
    """
    Modelo Usuario simplificado para ecommerce TECH-JUANJO.
    Campos esenciales + nombre + documento + rol simple.
    """
    
    ROL_CHOICES = [
        ('comprador', 'Usuario normal'),
        ('admin', 'Administrador'),
    ]
    
    primer_nombre = models.CharField(max_length=100, blank=False)
    numero_documento = models.CharField(max_length=20,unique=True,null=True,blank=True)
    rol = models.CharField(max_length=10, choices=ROL_CHOICES, default='comprador')
    
    direccion_principal = models.TextField(blank=True, null=True, verbose_name="Dirección Principal")
    referencias_direccion = models.TextField(blank=True, null=True, verbose_name="Referencias/Indicaciones")
    telefono = models.CharField(max_length=20, blank=True, verbose_name="Teléfono Personal")
    
    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
    
    def __str__(self):
        return f"{self.primer_nombre} ({self.username})"
    
    def get_nombre_completo(self):
        return self.primer_nombre or self.username


class PasswordResetToken(models.Model):
    """
    Token para recuperación de contraseña vía email.
    Válido por 24 horas.
    """
    user = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='password_reset_token')
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Token de Recuperación de Contraseña"
        verbose_name_plural = "Tokens de Recuperación de Contraseña"
    
    def __str__(self):
        return f"Token de recuperación para {self.user.get_nombre_completo()}"
    
    def is_valid(self):
        """Verifica si el token es válido (no usado y menor a 24h)"""
        from django.utils import timezone
        return (timezone.now() - self.created_at).total_seconds() < 86400 and not self.is_used
    
    @classmethod
    def generate_token(cls, user):
        """Genera un nuevo token para el usuario, eliminando anteriores no usados"""
        token = secrets.token_urlsafe(32)
        cls.objects.filter(user=user, is_used=False).delete()
        obj = cls.objects.create(user=user, token=token)
        return token

