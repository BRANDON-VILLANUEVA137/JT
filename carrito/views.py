from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Cart, CartItem
from Catalogo.models import Product

def cart_view(request):
    session_key = request.session.session_key
    cart = None
    items = []
    
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    elif session_key:
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    
    if cart:
        items = cart.items.all()
    
    total = sum(item.subtotal() for item in items) if items else 0
    
    context = {
        'cart': cart,
        'items': items,
        'total': total,
    }
    return render(request, 'carrito/cart.html', context)

@login_required
@require_http_methods(["POST"])
def add_to_cart(request):
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 1))
    product = get_object_or_404(Product, id=product_id, stock__gte=quantity)
    
    cart, created = Cart.objects.get_or_create(user=request.user)
    item, item_created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )
    
    if not item_created:
        new_qty = item.quantity + quantity
        if new_qty <= product.stock:
            item.quantity = new_qty
            item.save()
            messages.success(request, f'{product.name} actualizado en carrito!')
        else:
            messages.warning(request, f'Solo {product.stock} disponibles.')
    else:
        messages.success(request, f'{product.name} añadido al carrito!')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'total_items': cart.items.count()})
    return redirect('carrito:cart')

@login_required
@require_http_methods(["POST"])
def update_cart_item(request):
    item_id = request.POST.get('item_id')
    quantity = int(request.POST.get('quantity'))
    
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    
    if quantity <= 0:
        item.delete()
        messages.success(request, 'Item eliminado del carrito.')
    elif quantity <= item.product.stock:
        item.quantity = quantity
        item.save()
        messages.success(request, 'Cantidad actualizada.')
    else:
        messages.warning(request, f'Solo {item.product.stock} disponibles.')
    
    return redirect('carrito:cart')

@login_required
def checkout(request):
    cart = Cart.objects.filter(user=request.user).first()
    if not cart or not cart.items.exists():
        messages.warning(request, 'Carrito vacío')
        return redirect('carrito:cart')
    
    messages.info(request, 'Procediendo al pago...')
    return redirect('pedidos:mis_pedidos')  # Integrate with pedidos

@login_required
def clear_cart(request):
    cart = Cart.objects.filter(user=request.user).first()
    if cart:
        cart.items.all().delete()
        cart.delete()
    messages.success(request, 'Carrito limpiado')
    return redirect('carrito:cart')
