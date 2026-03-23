from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Product
from .forms import ProductForm

# 1. LISTAR
def product_list(request):
    products = Product.objects.all().order_by('-created_at')
    # Búsqueda simple
    query = request.GET.get('q')
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
    return render(request, 'catalogo/product_list.html', {'products': products})

# 2. DETALLE
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'catalogo/product_detail.html', {'product': product})

# 3. CREAR
@login_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            messages.success(request, 'Producto creado con éxito')
            return redirect('catalogo:product_list')
    else:
        form = ProductForm()
    return render(request, 'catalogo/product_form.html', {'form': form})

# 4. EDITAR
@login_required
def product_update(request, slug):
    product = get_object_or_404(Product, slug=slug)
    # Validar permisos: solo dueño o admin
    if product.seller != request.user and not request.user.is_superuser:
        messages.error(request, 'No tienes permiso para editar este producto')
        return redirect('catalogo:product_detail', slug=product.slug)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado')
            return redirect('catalogo:product_detail', slug=product.slug)
    else:
        form = ProductForm(instance=product)
    return render(request, 'catalogo/product_form.html', {'form': form})

# 5. ELIMINAR
@login_required
def product_delete(request, slug):
    product = get_object_or_404(Product, slug=slug)
    # Validar permisos
    if product.seller != request.user and not request.user.is_superuser:
        messages.error(request, 'No tienes permiso para eliminar este producto')
        return redirect('catalogo:product_detail', slug=product.slug)

    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Producto eliminado')
        return redirect('catalogo:product_list')
    return render(request, 'catalogo/product_confirm_delete.html', {'product': product})