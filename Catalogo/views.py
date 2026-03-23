from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Product

def product_list(request):
    products = Product.objects.all()
    
    # Search
    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    
    # Filters
    category = request.GET.get('category')
    if category:
        products = products.filter(category__slug=category)
    
    brand = request.GET.get('brand')
    if brand:
        products = products.filter(brand__slug=brand)
    
    condition = request.GET.get('condition')
    if condition:
        products = products.filter(condition=condition)
    
    # Pagination
    paginator = Paginator(products, 12)
    page = request.GET.get('page')
    products_page = paginator.get_page(page)
    
    context = {
        'products': products_page,
        'query': query,
    }
    return render(request, 'Catalogo/product_list.html', context)

def product_detail(request, slug):
    product = Product.objects.get(slug=slug)
    context = {'product': product}
    return render(request, 'Catalogo/product_detail.html', context)
