from django.urls import path
from . import views

app_name = 'catalogo'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('crear/', views.product_create, name='product_create'),
    path('<slug:slug>/editar/', views.product_update, name='product_update'),
    path('<slug:slug>/eliminar/', views.product_delete, name='product_delete'),
    path('<slug:slug>/', views.product_detail, name='product_detail'),
]
