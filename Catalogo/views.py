from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils.text import slugify
from .models import Product, Category, Brand
from .forms import ProductForm, CategoryForm, BrandForm

def home(request):
    if request.user.is_staff:
        return catalog_list(request)
    featured = Product.objects.filter(activo=True).order_by('-created_at')[:6]
    offers = Product.objects.filter(activo=True).order_by('price')[:8]
    categories = Category.objects.all().order_by('name')[:10]
    brands = Brand.objects.all().order_by('name')[:10]
    return render(request, 'catalogo/home.html', {
        'featured': featured,
        'offers': offers,
        'categories': categories,
        'brands': brands,
    })


# 1. LISTAR (PÚBLICO - cualquiera puede ver)
def catalog_list(request):
    CONDITION_CHOICES = [
        ('new', 'Nuevo'),
        ('used', 'Usado'),
    ]
    
    # Base queryset - solo activos
    products_list = Product.objects.filter(activo=True).order_by('-created_at')
    
    # Filtros GET
    category_id = request.GET.get('category')
    brand_id = request.GET.get('brand')
    condition = request.GET.get('condition')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    query = request.GET.get('q')
    
    if category_id:
        products_list = products_list.filter(category_id=category_id)
    if brand_id:
        products_list = products_list.filter(brand_id=brand_id)
    if condition:
        products_list = products_list.filter(condition=condition)
    if min_price:
        products_list = products_list.filter(price__gte=min_price)
    if max_price:
        products_list = products_list.filter(price__lte=max_price)
    if query:
        products_list = products_list.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    
    # Context para sidebar
    context = {
        'products': products_list,
        'categories': Category.objects.all(),
        'brands': Brand.objects.all(),
        'conditions': CONDITION_CHOICES,
    }
    
    # Paginación
    paginator = Paginator(products_list, 12)
    context['products'] = paginator.get_page(request.GET.get('page'))
    
    return render(request, 'catalogo/product_list.html', context)

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
            
            # Crear nueva categoría si se especificó
            new_cat_name = form.cleaned_data.get('new_category_name')
            if new_cat_name:
                cat, created = Category.objects.get_or_create(name=new_cat_name, defaults={'slug': slugify(new_cat_name)})
                product.category = cat
                messages.info(request, f'{"Creada" if created else "Usada"} categoría: {cat.name}')
            
            # Crear nueva marca si se especificó
            new_brand_name = form.cleaned_data.get('new_brand_name')
            if new_brand_name:
                brand, created = Brand.objects.get_or_create(name=new_brand_name, defaults={'slug': slugify(new_brand_name)})
                product.brand = brand
                messages.info(request, f'{"Creada" if created else "Usada"} marca: {brand.name}')
            
            product.seller = request.user
            if not product.category:
                form.add_error('new_category_name', 'Selecciona una categoría existente o ingresa una nueva')
            elif not product.brand:
                form.add_error('new_brand_name', 'Selecciona una marca existente o ingresa una nueva')
            else:
                product.save()
                messages.success(request, 'Producto creado con éxito')
                return redirect('catalogo:product_list')
            return render(request, 'catalogo/product_form.html', {'form': form})
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
            # Crear nueva categoría si se especificó
            new_cat_name = form.cleaned_data.get('new_category_name')
            if new_cat_name:
                cat, created = Category.objects.get_or_create(name=new_cat_name, defaults={'slug': slugify(new_cat_name)})
                product.category = cat
                messages.info(request, f'{"Creada" if created else "Usada"} categoría: {cat.name}')
            
            # Crear nueva marca si se especificó
            new_brand_name = form.cleaned_data.get('new_brand_name')
            if new_brand_name:
                brand, created = Brand.objects.get_or_create(name=new_brand_name, defaults={'slug': slugify(new_brand_name)})
                product.brand = brand
                messages.info(request, f'{"Creada" if created else "Usada"} marca: {brand.name}')
            
            if not product.category:
                form.add_error('new_category_name', 'Selecciona una categoría existente o ingresa una nueva')
            elif not product.brand:
                form.add_error('new_brand_name', 'Selecciona una marca existente o ingresa una nueva')
            else:
                form.save()
                messages.success(request, 'Producto actualizado')
                return redirect('catalogo:product_detail', slug=product.slug)
            return render(request, 'catalogo/product_form.html', {'form': form})
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

# ========== CATEGORÍAS ==========
@staff_member_required
def category_list(request):
    categories = Category.objects.all().order_by('name')
    return render(request, 'catalogo/category_list.html', {'categories': categories, 'title': 'Categorías'})

@staff_member_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría creada exitosamente')
            return redirect('catalogo:category_list')
    else:
        form = CategoryForm()
    return render(request, 'catalogo/category_form.html', {'form': form, 'title': 'Nueva Categoría'})

@staff_member_required
def category_update(request, slug):
    category = get_object_or_404(Category, slug=slug)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría actualizada')
            return redirect('catalogo:category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'catalogo/category_form.html', {'form': form, 'title': f'Editar {category.name}'})

# ========== MARCAS ==========
@staff_member_required
def brand_list(request):
    brands = Brand.objects.all().order_by('name')
    return render(request, 'catalogo/brand_list.html', {'brands': brands, 'title': 'Marcas'})

@staff_member_required
def brand_create(request):
    if request.method == 'POST':
        form = BrandForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Marca creada exitosamente')
            return redirect('catalogo:brand_list')
    else:
        form = BrandForm()
    return render(request, 'catalogo/brand_form.html', {'form': form, 'title': 'Nueva Marca'})

@staff_member_required
def brand_update(request, slug):
    brand = get_object_or_404(Brand, slug=slug)
    if request.method == 'POST':
        form = BrandForm(request.POST, instance=brand)
        if form.is_valid():
            form.save()
            messages.success(request, 'Marca actualizada')
            return redirect('catalogo:brand_list')
    else:
        form = BrandForm(instance=brand)
    return render(request, 'catalogo/brand_form.html', {'form': form, 'title': f'Editar {brand.name}'})

