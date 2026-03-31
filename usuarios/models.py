from django.contrib.auth.models import AbstractUser
from django.db import models

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

