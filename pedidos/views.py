from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Sum
from .models import Pedido, PedidoItem
from django.utils import timezone
from decimal import Decimal

@login_required
def mis_pedidos(request):
    """
    Pedidos del usuario logueado, agrupados por estado con opción cancelar.
    """
    pedidos = Pedido.objects.filter(user=request.user).select_related().order_by('-fecha_creacion')
    
    # Agrupar por estado
    estados = {}
    for pedido in pedidos:
        estado = pedido.estado
        if estado not in estados:
            estados[estado] = []
        estados[estado].append(pedido)
    
    context = {
        'estados': estados,
        'total_pedidos': pedidos.count(),
    }
    return render(request, 'pedidos/mis_pedidos.html', context)

@login_required
def cancelar_pedido(request, pedido_id):
    """
    Cancelar pedido del usuario (solo preparación).
    """
    pedido = get_object_or_404(Pedido, id=pedido_id, user=request.user, estado='preparacion')
    
    if request.method == 'POST':
        pedido.estado = 'cancelado'
        pedido.save()
        messages.success(request, f'Pedido #{pedido.id} cancelado exitosamente.')
        return redirect('pedidos:mis_pedidos')
    
    return render(request, 'pedidos/confirmar_cancelar.html', {'pedido': pedido})

@staff_member_required
def admin_pedidos(request):
    """
    Admin ve todos los pedidos con info comprador.
    """
    pedidos = Pedido.objects.all().prefetch_related('items__product').order_by('-fecha_creacion')
    
    context = {
        'pedidos': pedidos,
    }
    return render(request, 'pedidos/admin_pedidos.html', context)

@staff_member_required
def actualizar_estado_pedido(request, pedido_id):
    """
    Admin cambia estado pedido.
    """
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        if nuevo_estado in dict(Pedido.ESTADO_CHOICES):
            pedido.estado = nuevo_estado
            pedido.save()
            messages.success(request, f'Estado de pedido #{pedido.id} actualizado a "{dict(Pedido.ESTADO_CHOICES)[nuevo_estado]}"')
        return redirect('pedidos:admin_pedidos')
    
    return render(request, 'pedidos/actualizar_estado.html', {'pedido': pedido})
