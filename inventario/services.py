"""
Servicios para el módulo de inventario.
Funciones reutilizables para registrar movimientos, verificar alertas, etc.
"""
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import (
    MovimientoInventario, Lote, UnidadIndividual, AlertaStock
)
from Catalogo.models import Product

User = get_user_model()


@transaction.atomic
def registrar_movimiento(
    product,
    cantidad,
    tipo,
    usuario=None,
    lote=None,
    referencia_tipo='manual',
    referencia_id='',
    notas=''
):
    """
    Registra un movimiento de inventario y actualiza el stock del producto.
    
    Args:
        product: Instancia de Product
        cantidad: int (positivo para entrada, negativo para salida)
        tipo: str (clave de TIPO_MOVIMIENTO_CHOICES)
        usuario: User instance (opcional)
        lote: Lote instance (opcional)
        referencia_tipo: str (clave de REFERENCIA_TIPO_CHOICES)
        referencia_id: str (ID de la referencia ej: pedido #123)
        notas: str (opcional)
    
    Returns:
        MovimientoInventario instance
    """
    movimiento = MovimientoInventario.objects.create(
        product=product,
        lote=lote,
        tipo=tipo,
        referencia_tipo=referencia_tipo,
        referencia_id=referencia_id,
        cantidad=cantidad,
        stock_anterior=0,  # Se calcula en el save()
        stock_posterior=0,  # Se calcula en el save()
        usuario=usuario,
        notas=notas,
    )
    
    # Si hay lote, actualizar cantidad_actual del lote
    if lote:
        lote.cantidad_actual += cantidad
        if lote.cantidad_actual < 0:
            lote.cantidad_actual = 0
        lote.save()
    
    # Verificar alertas de stock bajo
    verificar_alertas_stock(product)
    
    return movimiento


@transaction.atomic
def registrar_venta(product, cantidad, pedido_id, usuario=None):
    """
    Registra la salida de inventario por una venta.
    """
    return registrar_movimiento(
        product=product,
        cantidad=-cantidad,
        tipo='salida_venta',
        usuario=usuario,
        referencia_tipo='pedido',
        referencia_id=str(pedido_id),
        notas=f'Venta - Pedido #{pedido_id}'
    )


@transaction.atomic
def registrar_entrada_compra(product, cantidad, lote=None, proveedor='', costo=None, usuario=None):
    """
    Registra la entrada de inventario por compra a proveedor.
    Si no se proporciona lote, se crea uno automáticamente.
    """
    if not lote:
        # Generar código de lote automático
        codigo_lote = f"COMP-{timezone.now().strftime('%Y%m%d%H%M%S')}"
        lote = Lote.objects.create(
            codigo_lote=codigo_lote,
            product=product,
            cantidad_inicial=cantidad,
            proveedor=proveedor,
            costo_unitario=costo,
        )
    
    movimiento = registrar_movimiento(
        product=product,
        cantidad=cantidad,
        tipo='entrada_compra',
        usuario=usuario,
        lote=lote,
        referencia_tipo='proveedor',
        notas=f'Compra a {proveedor}' if proveedor else 'Compra a proveedor'
    )
    
    return movimiento


@transaction.atomic
def registrar_ajuste(product, cantidad, motivo='', usuario=None):
    """
    Registra un ajuste de inventario (positivo o negativo).
    """
    tipo = 'entrada_ajuste' if cantidad > 0 else 'salida_ajuste'
    return registrar_movimiento(
        product=product,
        cantidad=cantidad,
        tipo=tipo,
        usuario=usuario,
        referencia_tipo='manual',
        notas=motivo
    )


@transaction.atomic
def aplicar_conteo_fisico(conteo_item, usuario=None):
    """
    Aplica la diferencia de un conteo físico como un movimiento de ajuste.
    """
    diferencia = conteo_item.diferencia
    if diferencia == 0:
        return None
    
    tipo = 'entrada_ajuste' if diferencia > 0 else 'salida_ajuste'
    return registrar_movimiento(
        product=conteo_item.product,
        cantidad=diferencia,
        tipo=tipo,
        usuario=usuario,
        referencia_tipo='conteo',
        referencia_id=str(conteo_item.conteo.id),
        notas=f'Ajuste por conteo físico: {conteo_item.conteo.codigo_conteo} '
              f'(sistema: {conteo_item.stock_sistema}, contado: {conteo_item.stock_contado})'
    )


def verificar_alertas_stock(product):
    """
    Verifica si un producto ha llegado a su stock mínimo y registra la alerta.
    """
    try:
        alerta = AlertaStock.objects.get(product=product, activo=True)
        if alerta.verificar_stock():
            # Actualizar timestamp de última notificación
            alerta.ultima_notificacion = timezone.now()
            alerta.save()
            return True
    except AlertaStock.DoesNotExist:
        pass
    return False


def obtener_productos_bajo_stock():
    """
    Retorna un queryset de productos cuyo stock está por debajo del mínimo configurado.
    """
    from django.db.models import F, OuterRef, Subquery
    
    alertas = AlertaStock.objects.filter(activo=True, product__stock__lte=F('stock_minimo'))
    return alertas.select_related('product')


def obtener_productos_por_vencer(dias=30):
    """
    Retorna lotes que vencen en los próximos `dias` días.
    """
    from datetime import timedelta
    hoy = timezone.now().date()
    fecha_limite = hoy + timedelta(days=dias)
    
    return Lote.objects.filter(
        activo=True,
        cantidad_actual__gt=0,
        fecha_vencimiento__isnull=False,
        fecha_vencimiento__gte=hoy,
        fecha_vencimiento__lte=fecha_limite,
    ).select_related('product')


def obtener_stock_por_lote(product):
    """
    Retorna el desglose de stock de un producto por lote.
    """
    lotes = Lote.objects.filter(
        product=product,
        activo=True,
        cantidad_actual__gt=0
    ).order_by('fecha_vencimiento', 'fecha_ingreso')
    
    return lotes