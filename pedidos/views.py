from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from .models import Pedido, PedidoItem
from .forms import PedidoForm
from django.utils import timezone
from decimal import Decimal
from collections import defaultdict

@login_required
def mis_pedidos(request):
    """
    Pedidos del usuario logueado, agrupados por estado con opción cancelar.
    """
    pedidos = Pedido.objects.filter(user=request.user).prefetch_related('items__product').order_by('-fecha_creacion')
    
    pedidos_by_state = defaultdict(list)
    for pedido in pedidos:
        pedidos_by_state[pedido.estado].append(pedido)
    
    estados_data = [
        {
            'key': key,
            'label': label,
            'pedidos': pedidos_by_state[key]
        }
        for key, label in Pedido.ESTADO_CHOICES
    ]
    
    context = {
        'estados_data': estados_data,
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

@login_required
def admin_pedidos(request):
    if request.user.rol != 'admin':
        messages.error(request, 'No tienes permiso para acceder a esta página.')
        return redirect('usuarios:dashboard')
    """
    Admin ve todos los pedidos con info comprador.
    """
    pedidos = Pedido.objects.all().prefetch_related('items__product').order_by('-fecha_creacion')
    
    context = {
        'pedidos': pedidos,
    }
    return render(request, 'pedidos/admin_pedidos.html', context)

@login_required
def actualizar_estado_pedido(request, pedido_id):
    if request.user.rol != 'admin':
        messages.error(request, 'No tienes permiso para acceder a esta página.')
        return redirect('usuarios:dashboard')
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

@login_required
def admin_edit_pedido(request, pedido_id):
    if request.user.rol != 'admin':
        messages.error(request, 'No tienes permiso para acceder a esta página.')
        return redirect('usuarios:dashboard')
    """
    Admin edita telefono, direccion, estado del pedido.
    """
    pedido = get_object_or_404(Pedido, id=pedido_id)
    form = PedidoForm(instance=pedido)
    
    if request.method == 'POST':
        form = PedidoForm(request.POST, instance=pedido)
        if form.is_valid():
            form.save()
            messages.success(request, f'Pedido #{pedido.id} actualizado exitosamente.')
            return redirect('pedidos:admin_pedidos')
    
    context = {
        'pedido': pedido,
        'form': form,
    }
    return render(request, 'pedidos/admin_editar_pedido.html', context)

@login_required
def admin_delete_pedido(request, pedido_id):
    if request.user.rol != 'admin':
        messages.error(request, 'No tienes permiso para acceder a esta página.')
        return redirect('usuarios:dashboard')
    """
    Admin elimina pedido (solo si preparacion y sin pago Stripe).
    """
    pedido = get_object_or_404(Pedido, id=pedido_id)
    puede_eliminar = (pedido.estado == 'preparacion' and not pedido.stripe_session_id)
    
    if request.method == 'POST' and puede_eliminar:
        pedido_id = pedido.id
        pedido.delete()  # Cascade a items
        messages.success(request, f'Pedido #{pedido_id} eliminado permanentemente.')
        return redirect('pedidos:admin_pedidos')
    elif request.method == 'POST':
        messages.error(request, 'No se puede eliminar este pedido: debe estar en preparación y sin pago Stripe.')
    
    context = {
        'pedido': pedido,
        'puede_eliminar': puede_eliminar,
    }
    return render(request, 'pedidos/admin_confirmar_eliminar.html', context)
