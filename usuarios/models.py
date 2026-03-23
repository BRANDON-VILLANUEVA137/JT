from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    """
    Modelo Usuario simplificado para ecommerce TECH-JUANJO.
    Campos esenciales + nombre + documento + rol simple.
    """
    
    ROL_CHOICES = [
        ('buyer', 'Comprador'),
        ('seller', 'Vendedor'),
    ]
    
    primer_nombre = models.CharField(max_length=100, blank=False)
    numero_documento = models.CharField(max_length=20, unique=True)
    rol = models.CharField(max_length=10, choices=ROL_CHOICES, default='buyer')
    
    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
    
    def __str__(self):
        return f"{self.primer_nombre} ({self.username})"
    
    def get_nombre_completo(self):
        return self.primer_nombre or self.username

