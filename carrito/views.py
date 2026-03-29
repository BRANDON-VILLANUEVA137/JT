from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Cart, CartItem
from Catalogo.models import Product

def cart_view(request):
    # View cart for anon (session) and logged (user)
    session_key = request.session.session_key
    cart = None
    items = []
    
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    elif session_key:
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    
    if cart:
        items = cart.items.all()
    
    context = {
        'cart': cart,
        'items': items,
        'total': sum(item.quantity * item.product.price for item in items),
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
        item.quantity += quantity
        item.save()
    
    messages.success(request, f'{product.name} añadido al carrito!')
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'total_items': cart.items.count()})
    return redirect('carrito:cart')

@login_required
def checkout(request):
    # Checkout view - require login
    cart = Cart.objects.filter(user=request.user).first()
    if not cart or not cart.items.exists():
        messages.warning(request, 'Carrito vacío')
        return redirect('carrito:cart')
    
    # Process checkout logic here (pedidos)
    messages.info(request, 'Redirigiendo a checkout...')
    return redirect('pedidos:mis_pedidos')  # Placeholder

def clear_cart(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            cart.items.all().delete()
            cart.delete()
    messages.success(request, 'Carrito limpiado')
    return redirect('carrito:cart')
