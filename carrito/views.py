from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
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
    
    total = sum(item.subtotal() for item in cart.items.all())
    
    if request.method == 'POST':
        # Validate checkout form
        telefono = request.POST.get('telefono', '').strip()
        direccion_principal = request.POST.get('direccion_principal', '').strip()
        referencias_direccion = request.POST.get('referencias_direccion', '').strip()
        
        if not telefono or not direccion_principal:
            messages.error(request, 'Teléfono y dirección son obligatorios.')
            context = {'cart': cart, 'total': total, 'user': request.user}
            return render(request, 'carrito/checkout.html', context)
        
        # Store checkout data in session for webhook
        request.session['checkout_data'] = {
            'telefono': telefono,
            'direccion_principal': direccion_principal,
            'referencias_direccion': referencias_direccion,
        }
        
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
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
                'telefono': telefono,
                'direccion': direccion_principal[:255],  # Truncate for metadata
                'referencias': referencias_direccion[:255],
            },
            success_url=request.build_absolute_uri(f'/carrito/success/?session_id={{CHECKOUT_SESSION_ID}}'),
            cancel_url=request.build_absolute_uri('/carrito/?cancelled=true'),
        )
        
        return redirect(session.url, code=303)
    
    # GET: Show form prefilled from user profile
    context = {
        'cart': cart,
        'total': total,
        'user': request.user,
    }
    return render(request, 'carrito/checkout.html', context)

@login_required
def checkout_success(request):
    session_id = request.GET.get('session_id')
    if session_id:
        messages.success(request, '¡Pago exitoso! Pedido creado.')
    return redirect('pedidos:mis_pedidos')

@login_required
def clear_cart(request):
    cart = Cart.objects.filter(user=request.user).first()
    if cart:
        cart.items.all().delete()
        cart.delete()
    messages.success(request, 'Carrito limpiado')
    return redirect('carrito:cart')
