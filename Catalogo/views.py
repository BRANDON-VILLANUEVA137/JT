from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Product
from .forms import ProductForm

# 1. LISTAR (PÚBLICO - cualquiera puede ver)
def product_list(request):
    products_list = Product.objects.all().order_by('-created_at')
    query = request.GET.get('q')
    if query:
        products_list = products_list.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    paginator = Paginator(products_list, 12)
    products = paginator.get_page(request.GET.get('page'))
    return render(request, 'catalogo/product_list.html', {'products': products})

# 2. DETALLE (PÚBLICO)
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'catalogo/product_detail.html', {'product': product})

# 3. CREAR (SOLO ADMIN/STAFF)
@staff_member_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user  # El admin es el vendedor
            product.save()
            messages.success(request, 'Producto creado con éxito')
            return redirect('catalogo:product_list')
    else:
        form = ProductForm()
    return render(request, 'catalogo/product_form.html', {'form': form})

# 4. EDITAR (SOLO ADMIN)
@staff_member_required
def product_update(request, slug):
    product = get_object_or_404(Product, slug=slug)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado')
            return redirect('catalogo:product_detail', slug=product.slug)
    else:
        form = ProductForm(instance=product)
    return render(request, 'catalogo/product_form.html', {'form': form})

# 5. ELIMINAR (SOLO ADMIN)
@staff_member_required
def product_delete(request, slug):
    product = get_object_or_404(Product, slug=slug)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Producto eliminado')
        return redirect('catalogo:product_list')
    return render(request, 'catalogo/product_confirm_delete.html', {'product': product})