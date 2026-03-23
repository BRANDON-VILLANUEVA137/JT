'''from django.urls import path
from . import views

app_name = 'Catalogo'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('<slug:slug>/', views.product_detail, name='product_detail'),
]
'''

# Catalogo/urls.py
from django.urls import path
from . import views

app_name = 'catalogo'  # ← MINÚSCULA, importante

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('producto/<slug:slug>/', views.product_detail, name='product_detail'),
    path('producto/crear/', views.product_create, name='product_create'),
    path('producto/<slug:slug>/editar/', views.product_update, name='product_update'),
    path('producto/<slug:slug>/eliminar/', views.product_delete, name='product_delete'),
]