from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models.functions import Lower
from .models import Product, Category, Brand
from .forms import ProductForm

def product_list(request):
    products = Product.objects.filter(activo=True).select_related('category', 'brand', 'seller').order_by('-created_at')
    
    # Filtros
    query = request.GET.get('q')
    category_id = request.GET.get('category')
    brand_id = request.GET.get('brand')
    condition = request.GET.get('condition')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    sort = request.GET.get('sort', '-created_at')
    
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
    
    if category_id:
        products = products.filter(category_id=category_id)
    
    if brand_id:
        products = products.filter(brand_id=brand_id)
    
    if condition:
        products = products.filter(condition=condition)
    
    if min_price:
        products = products.filter(price__gte=min_price)
    
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # Sorting
    if sort == 'price':
        products = products.order_by('price')
    elif sort == '-price':
        products = products.order_by('-price')
    elif sort == 'name':
        products = products.order_by(Lower('name'))
    else:
        products = products.order_by('-created_at')
    
    # Paginación
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    products_page = paginator.get_page(page_number)
    
    # Context
    context = {
        'products': products_page,
        'categories': Category.objects.all(),
        'brands': Brand.objects.all(),
        'query': query,
        'current_category': category_id,
        'current_brand': brand_id,
        'current_condition': condition,
        'current_sort': sort,
    }
    
    return render(request, 'Catalogo/product_list.html', context)

def product_detail(request, slug):
    product = get_object_or_404(Product.objects.filter(activo=True), slug=slug)
    
    context = {
        'product': product,
        'related_products': Product.objects.filter(
            category=product.category,
            activo=True
        ).exclude(slug=slug)[:4]
    }
    return render(request, 'Catalogo/product_detail.html', context)

@login_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            messages.success(request, 'Producto creado!')
            return redirect('Catalogo:product_list')
    else:
        form = ProductForm()
    return render(request, 'Catalogo/product_form.html', {'form': form, 'title': 'Crear Producto'})

@login_required
def product_update(request, slug):
    product = get_object_or_404(Product, slug=slug, seller=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado!')
            return redirect('Catalogo:product_detail', slug=slug)
    else:
        form = ProductForm(instance=product)
    return render(request, 'Catalogo/product_form.html', {'form': form, 'title': 'Editar Producto'})

@login_required
def product_delete(request, slug):
    product = get_object_or_404(Product, slug=slug, seller=request.user)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Producto eliminado!')
        return redirect('Catalogo:product_list')
    return render(request, 'Catalogo/product_confirm_delete.html', {'product': product})

