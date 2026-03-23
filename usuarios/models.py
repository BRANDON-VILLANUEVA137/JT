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
        ('admin', 'Administrador'),
        ('docente', 'Docente'),
        ('estudiante', 'Estudiante'),
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


class Estudiante(models.Model):
    """
    Modelo extendido para perfiles de estudiantes.
    Contiene información específica del estudiante y su desempeño académico.
    """
    
    ESTADO_FINAL_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('reprobado', 'Reprobado'),
    ]
    
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name='perfil_estudiante',
        limit_choices_to={'rol': 'estudiante'},
        help_text="Usuario asociado al perfil de estudiante"
    )
    
    codigo_estudiantil = models.CharField(
        max_length=20,
        unique=True,
        help_text="Código único del estudiante"
    )
    
    fecha_nacimiento = models.DateField(
        null=True,
        blank=True,
        help_text="Fecha de nacimiento del estudiante"
    )
    
    # Información del Acudiente
    nombre_acudiente = models.CharField(
        max_length=200,
        blank=True,
        help_text="Nombre del acudiente o tutor"
    )
    
    telefono_acudiente = models.CharField(
        max_length=20,
        blank=True,
        help_text="Teléfono de contacto del acudiente"
    )
    
    # Información Académica
    promedio_general = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
        help_text="Promedio general del estudiante (0.0 - 5.0)"
    )
    
    estado_final = models.CharField(
        max_length=10,
        choices=ESTADO_FINAL_CHOICES,
        default='pendiente',
        help_text="Estado final del periodo académico"
    )
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Estudiante"
        verbose_name_plural = "Estudiantes"
        ordering = ['usuario__primer_apellido', 'usuario__primer_nombre']
        indexes = [
            models.Index(fields=['codigo_estudiantil']),
        ]
    
    def __str__(self):
        return f"{self.usuario.get_nombre_completo()} ({self.codigo_estudiantil})"
    
    def calcular_edad(self):
        """Calcula la edad actual del estudiante."""
        if not self.fecha_nacimiento:
            return None
        from datetime import date
        hoy = date.today()
        edad = hoy.year - self.fecha_nacimiento.year
        if (hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day):
            edad -= 1
        return edad
    
    def actualizar_promedio(self, nuevo_promedio):
        """Actualiza el promedio general del estudiante."""
        if 0.0 <= nuevo_promedio <= 5.0:
            self.promedio_general = nuevo_promedio
            self.save()
    
    def determinar_estado_final(self):
        """Determina el estado final basado en el promedio."""
        if self.promedio_general >= 3.0:
            self.estado_final = 'aprobado'
        else:
            self.estado_final = 'reprobado'
        self.save()


class Docente(models.Model):
    """
    Modelo extendido para perfiles de docentes.
    Contiene información específica del docente.
    """
    
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name='perfil_docente',
        limit_choices_to={'rol': 'docente'},
        help_text="Usuario asociado al perfil de docente"
    )
    
    especialidad = models.CharField(
        max_length=200,
        help_text="Especialidad o materia principal que enseña"
    )
    
    telefono_institucional = models.CharField(
        max_length=20,
        blank=True,
        help_text="Teléfono de contacto institucional"
    )
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Docente"
        verbose_name_plural = "Docentes"
        ordering = ['usuario__primer_apellido']
    
    def __str__(self):
        return f"Prof. {self.usuario.get_nombre_completo()} - {self.especialidad}"


class PasswordResetToken(models.Model):
    """
    Modelo para guardar tokens de recuperación de contraseña.
    Los tokens expiran después de 24 horas.
    """
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='reset_tokens')
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Token de Reset"
        verbose_name_plural = "Tokens de Reset"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Reset token para {self.usuario.email}"
    
    def is_valid(self):
        """Verifica si el token no ha expirado (24 horas)."""
        from django.utils import timezone
        from datetime import timedelta
        return timezone.now() - self.created_at < timedelta(hours=24)
    
    @staticmethod
    def generate_token():
        """Genera un token único y seguro."""
        import secrets
        return secrets.token_urlsafe(32)


# ==================== SEÑALES ====================
from django.db.models.signals import pre_save
from django.dispatch import receiver


@receiver(pre_save, sender=Usuario)
def asegurar_rol_admin_superusuario(sender, instance, **kwargs):
    """
    Señal que asegura que todos los superusuarios tengan rol='admin'.
    Se ejecuta antes de guardar cualquier usuario.
    """
    if instance.is_superuser:
        # Si es superusuario, forzar rol='admin'
        instance.rol = 'admin'
        
        # Completar campos requeridos si están vacíos
        if not instance.primer_nombre:
            instance.primer_nombre = instance.username or 'Admin'
        if not instance.primer_apellido:
            instance.primer_apellido = 'Sistema'
        if not instance.tipo_documento:
            instance.tipo_documento = 'CC'
        if not instance.numero_documento:
            instance.numero_documento = instance.username or str(instance.id)

