from django.db import models
from django.conf import settings
from Catalogo.models import Product
from django.utils import timezone

class Pedido(models.Model):
    ESTADO_CHOICES = [
        ('preparacion', 'En preparación'),
        ('enviado', 'Enviado/En tránsito'),
        ('reparto', 'En reparto'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pedidos')
    total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='preparacion')
    fecha_creacion = models.DateTimeField(default=timezone.now)
    direccion = models.TextField()
    telefono = models.CharField(max_length=20)
    stripe_session_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    
    class Meta:
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"Pedido #{self.id} - {self.user} - ${self.total}"

class PedidoItem(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    
    def subtotal(self):
        return self.cantidad * self.precio_unitario
    
    def __str__(self):
        return f"{self.cantidad}x {self.product.name}"
