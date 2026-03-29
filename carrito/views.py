from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
from django.conf import settings
import stripe
import os
from .models import Cart, CartItem
from Catalogo.models import Product
from pedidos.models import Pedido, PedidoItem

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
    
    stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
    
    line_items = []
    for item in cart.items.all():
        line_items.append({
            'price_data': {
                'currency': 'cop',
                'product_data': {
                    'name': str(item.product),
                },
                'unit_amount': int(item.product.price * 100),  # cents
            },
            'quantity': item.quantity,
        })
    
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        metadata={
            'user_id': str(request.user.id),
            'cart_id': str(cart.id),
        },
        success_url=request.build_absolute_uri('/carrito/success/?session_id={CHECKOUT_SESSION_ID}'),
        cancel_url=request.build_absolute_uri('/carrito/?cancelled=true'),
    )
    
    return redirect(session.url, code=303)

@login_required
def checkout_success(request):
    session_id = request.GET.get('session_id')
    if session_id and '{{ CHECKOUT_SESSION_ID }}' not in session_id:
        stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            if session.payment_status == 'paid':
                messages.success(request, '¡Pago exitoso! Revisa tus pedidos.')
        except:
            pass
    else:
        messages.info(request, 'Proceso de pago completado. Revisa tus pedidos.')
    return redirect('pedidos:mis_pedidos')

@login_required
def clear_cart(request):
    cart = Cart.objects.filter(user=request.user).first()
    if cart:
        cart.items.all().delete()
        cart.delete()
    messages.success(request, 'Carrito limpiado')
    return redirect('carrito:cart')


