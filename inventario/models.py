from django.db import models
from django.conf import settings
from Catalogo.models import Product
from django.utils import timezone

# ============================
# TIPOS DE MOVIMIENTO
# ============================
TIPO_MOVIMIENTO_CHOICES = [
    ('entrada_compra', 'Entrada - Compra a proveedor'),
    ('entrada_devolucion', 'Entrada - Devolución de cliente'),
    ('entrada_ajuste', 'Entrada - Ajuste de inventario'),
    ('salida_venta', 'Salida - Venta'),
    ('salida_devolucion_proveedor', 'Salida - Devolución a proveedor'),
    ('salida_merma', 'Salida - Merma/Pérdida'),
    ('salida_ajuste', 'Salida - Ajuste de inventario'),
]

REFERENCIA_TIPO_CHOICES = [
    ('pedido', 'Pedido'),
    ('proveedor', 'Proveedor'),
    ('conteo', 'Conteo físico'),
    ('manual', 'Manual/Ajuste'),
]


class Lote(models.Model):
    """Lote para rastrear productos con fecha de vencimiento."""
    codigo_lote = models.CharField(max_length=100, verbose_name='Código de lote')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='lotes')
    cantidad_inicial = models.PositiveIntegerField(default=0)
    cantidad_actual = models.PositiveIntegerField(default=0)
    fecha_vencimiento = models.DateField(null=True, blank=True, verbose_name='Fecha de vencimiento')
    fecha_ingreso = models.DateField(default=timezone.now, verbose_name='Fecha de ingreso')
    proveedor = models.CharField(max_length=200, blank=True, verbose_name='Proveedor')
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Costo unitario')
    notas = models.TextField(blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['-fecha_ingreso']
        verbose_name = 'Lote'
        verbose_name_plural = 'Lotes'
        unique_together = ['codigo_lote', 'product']

    def __str__(self):
        return f"{self.product.name} - Lote {self.codigo_lote} ({self.cantidad_actual} uds)"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.cantidad_actual = self.cantidad_inicial
        super().save(*args, **kwargs)

    @property
    def esta_vencido(self):
        if self.fecha_vencimiento:
            return self.fecha_vencimiento < timezone.now().date()
        return False

    @property
    def por_vencer(self):
        """Devuelve True si vence en los próximos 30 días."""
        if self.fecha_vencimiento:
            dias_restantes = (self.fecha_vencimiento - timezone.now().date()).days
            return 0 <= dias_restantes <= 30
        return False


class UnidadIndividual(models.Model):
    """Tracking individual para productos usados/refurbished (cada unidad con su estado)."""
    ESTADO_CHOICES = [
        ('disponible', 'Disponible'),
        ('vendido', 'Vendido'),
        ('merma', 'Merma/Pérdida'),
        ('en_reparacion', 'En reparación'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='unidades_individuales')
    codigo_interno = models.CharField(max_length=100, unique=True, verbose_name='Código interno')
    lote = models.ForeignKey(Lote, on_delete=models.SET_NULL, null=True, blank=True, related_name='unidades')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='disponible')
    fecha_ingreso = models.DateField(default=timezone.now)
    precio_costo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    notas = models.TextField(blank=True)
    
    class Meta:
        ordering = ['codigo_interno']
        verbose_name = 'Unidad individual'
        verbose_name_plural = 'Unidades individuales'

    def __str__(self):
        return f"{self.product.name} - {self.codigo_interno} ({self.get_estado_display()})"


class MovimientoInventario(models.Model):
    """Registro de todos los movimientos de inventario."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='movimientos')
    lote = models.ForeignKey(Lote, on_delete=models.SET_NULL, null=True, blank=True, related_name='movimientos')
    tipo = models.CharField(max_length=30, choices=TIPO_MOVIMIENTO_CHOICES, verbose_name='Tipo de movimiento')
    referencia_tipo = models.CharField(max_length=20, choices=REFERENCIA_TIPO_CHOICES, default='manual', verbose_name='Tipo de referencia')
    referencia_id = models.CharField(max_length=100, blank=True, verbose_name='ID de referencia')
    cantidad = models.IntegerField(verbose_name='Cantidad (positiva=entrada, negativa=salida)')
    stock_anterior = models.PositiveIntegerField(verbose_name='Stock antes del movimiento')
    stock_posterior = models.PositiveIntegerField(verbose_name='Stock después del movimiento')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Usuario que realizó el movimiento')
    notas = models.TextField(blank=True)
    fecha = models.DateTimeField(default=timezone.now, verbose_name='Fecha del movimiento')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Movimiento de inventario'
        verbose_name_plural = 'Movimientos de inventario'

    def __str__(self):
        signo = "+" if self.cantidad > 0 else ""
        return f"{self.get_tipo_display()} - {self.product.name}: {signo}{self.cantidad}"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.stock_anterior = self.product.stock
            self.product.stock += self.cantidad
            if self.product.stock < 0:
                self.product.stock = 0  # Evitar stock negativo
            self.stock_posterior = self.product.stock
            self.product.save()
        super().save(*args, **kwargs)


class ConteoFisico(models.Model):
    """Conteo físico de inventario para ajustar diferencias."""
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_progreso', 'En progreso'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
    ]

    codigo_conteo = models.CharField(max_length=100, unique=True, verbose_name='Código de conteo')
    fecha_conteo = models.DateField(default=timezone.now)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    notas = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_conteo']
        verbose_name = 'Conteo físico'
        verbose_name_plural = 'Conteos físicos'

    def __str__(self):
        return f"Conteo {self.codigo_conteo} - {self.get_estado_display()}"


class ConteoFisicoItem(models.Model):
    """Producto contado en un conteo físico."""
    conteo = models.ForeignKey(ConteoFisico, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    stock_sistema = models.PositiveIntegerField(verbose_name='Stock según sistema')
    stock_contado = models.PositiveIntegerField(verbose_name='Stock contado físicamente')
    diferencia = models.IntegerField(verbose_name='Diferencia', editable=False)
    notas = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Item de conteo'
        verbose_name_plural = 'Items de conteo'
        unique_together = ['conteo', 'product']

    def save(self, *args, **kwargs):
        self.diferencia = self.stock_contado - self.stock_sistema
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name}: sistema={self.stock_sistema}, contado={self.stock_contado}"


class AlertaStock(models.Model):
    """Configuración y registro de alertas de stock bajo."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='alertas_stock')
    stock_minimo = models.PositiveIntegerField(default=5, verbose_name='Stock mínimo')
    activo = models.BooleanField(default=True)
    ultima_notificacion = models.DateTimeField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Alerta de stock'
        verbose_name_plural = 'Alertas de stock'
        unique_together = ['product']

    def __str__(self):
        return f"Alerta: {self.product.name} (mín: {self.stock_minimo})"

    def verificar_stock(self):
        """Devuelve True si el stock está por debajo del mínimo."""
        return self.product.stock <= self.stock_minimo