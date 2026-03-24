from django.urls import path
from . import views

app_name = 'catalogo'

urlpatterns = [
    path('', views.home, name='home'),
    path('catalogo/', views.catalog_list, name='product_list'),
    path('catalogo/crear/', views.product_create, name='product_create'),
    path('catalogo/<slug:slug>/editar/', views.product_update, name='product_update'),
    path('catalogo/<slug:slug>/eliminar/', views.product_delete, name='product_delete'),
    path('catalogo/<slug:slug>/', views.product_detail, name='product_detail'),
    
    # Categorías
    path('category/', views.category_list, name='category_list'),
    path('category/crear/', views.category_create, name='category_create'),
    path('category/<slug:slug>/editar/', views.category_update, name='category_update'),
    
    # Marcas
    path('brand/', views.brand_list, name='brand_list'),
    path('brand/crear/', views.brand_create, name='brand_create'),
    path('brand/<slug:slug>/editar/', views.brand_update, name='brand_update'),
]
