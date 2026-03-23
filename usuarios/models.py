from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator


class Usuario(AbstractUser):
    """
    Modelo de Usuario extendido de AbstractUser.
    Centraliza la gestión de identidad, autenticación y autorización.
    """
    
    TIPO_DOCUMENTO_CHOICES = [
        ('TI', 'Tarjeta de Identidad'),
        ('CC', 'Cédula de Ciudadanía'),
        ('CE', 'Cédula de Extranjería'),
        ('RC', 'Registro Civil'),
    ]
    
    ROL_CHOICES = [
        ('buyer', 'Comprador'),
        ('seller', 'Vendedor'),
        ('admin', 'Administrador'),
    ]
    
    # Información Personal
    primer_nombre = models.CharField(
        max_length=100,
        help_text="Primer nombre del usuario"
    )
    segundo_nombre = models.CharField(
        max_length=100,
        blank=True,
        help_text="Segundo nombre del usuario (opcional)"
    )
    primer_apellido = models.CharField(
        max_length=100,
        help_text="Primer apellido del usuario"
    )
    segundo_apellido = models.CharField(
        max_length=100,
        blank=True,
        help_text="Segundo apellido del usuario (opcional)"
    )
    
    # Documento de Identidad
    tipo_documento = models.CharField(
        max_length=2,
        choices=TIPO_DOCUMENTO_CHOICES,
        help_text="Tipo de documento de identidad"
    )
    numero_documento = models.CharField(
        max_length=20,
        unique=True,
        help_text="Número de documento (único en el sistema)"
    )
    
    # Contacto y Seguridad
    email = models.EmailField(
        unique=True,
        help_text="Email único para recuperación de cuenta"
    )
    rol = models.CharField(
        max_length=10,
        choices=ROL_CHOICES,
        default='estudiante',
        help_text="Rol del usuario en el sistema"
    )
    
    # Seguridad
    intentos_fallidos = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Contador de intentos fallidos de login"
    )
    bloqueado_hasta = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha y hora hasta la cual la cuenta está bloqueada por intentos fallidos"
    )
    must_change_password = models.BooleanField(
        default=False,
        help_text="Obliga al usuario a cambiar la contraseña en el primer inicio de sesión"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Indica si la cuenta está activa o bloqueada permanentemente"
    )
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ['primer_nombre', 'primer_apellido']
        indexes = [
            models.Index(fields=['numero_documento']),
            models.Index(fields=['email']),
            models.Index(fields=['rol']),
        ]
    
    def __str__(self):
        nombre_completo = f"{self.primer_nombre} {self.primer_apellido}"
        if self.segundo_nombre:
            nombre_completo = f"{self.primer_nombre} {self.segundo_nombre} {self.primer_apellido}"
        if self.segundo_apellido:
            nombre_completo += f" {self.segundo_apellido}"
        return nombre_completo.strip()
    
    def get_nombre_completo(self):
        """Retorna el nombre completo del usuario."""
        partes = [self.primer_nombre]
        if self.segundo_nombre:
            partes.append(self.segundo_nombre)
        partes.append(self.primer_apellido)
        if self.segundo_apellido:
            partes.append(self.segundo_apellido)
        return " ".join(partes)
    
    def bloquear_cuenta(self):
        """
        Bloquea la cuenta temporalmente por 30 minutos tras múltiples intentos fallidos.
        No la desactiva permanentemente, solo establece un tiempo de bloqueo.
        """
        from django.utils import timezone
        from datetime import timedelta
        self.bloqueado_hasta = timezone.now() + timedelta(minutes=30)
        self.save(update_fields=['bloqueado_hasta', 'intentos_fallidos'])
    
    def desbloquear_cuenta(self):
        """
        Desbloquea la cuenta y reinicia los intentos fallidos.
        Usada por administrador si necesita desbloquear manualmente.
        """
        self.bloqueado_hasta = None
        self.intentos_fallidos = 0
        self.is_active = True
        self.save(update_fields=['bloqueado_hasta', 'intentos_fallidos', 'is_active'])
    
    def cuenta_bloqueada_temporalmente(self):
        """
        Verifica si la cuenta está bloqueada temporalmente.
        Retorna True si aún está dentro del período de bloqueo.
        """
        from django.utils import timezone
        if self.bloqueado_hasta is None:
            return False
        if timezone.now() >= self.bloqueado_hasta:
            # El bloqueo ha expirado, limpiar y devolver False
            self.bloqueado_hasta = None
            self.intentos_fallidos = 0
            self.save(update_fields=['bloqueado_hasta', 'intentos_fallidos'])
            return False
        return True
    
    def incrementar_intentos_fallidos(self):
        """
        Incrementa el contador de intentos fallidos.
        Bloquea temporalmente la cuenta después de 5 intentos.
        """
        self.intentos_fallidos += 1
        if self.intentos_fallidos >= 5:
            self.bloquear_cuenta()
        else:
            self.save(update_fields=['intentos_fallidos'])
    
    def reiniciar_intentos_fallidos(self):
        """Reinicia el contador de intentos fallidos tras login exitoso."""
        if self.intentos_fallidos != 0:
            self.intentos_fallidos = 0
            self.save(update_fields=['intentos_fallidos'])





# ==================== SEÑALES ====================
from django.db.models.signals import pre_save
from django.dispatch import receiver


@receiver(pre_save, sender=Usuario)
def asegurar_rol_admin_superusuario(sender, instance, **kwargs):
    """
    Señal que asegura que todos los superusuarios tengan rol='admin'.
    """
    if instance.is_superuser:
        instance.rol = 'admin'
        if not instance.primer_nombre:
            instance.primer_nombre = instance.username or 'Admin'
        if not instance.primer_apellido:
            instance.primer_apellido = 'Sistema'

