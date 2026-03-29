from django.urls import path
from . import views

app_name = 'carrito'

urlpatterns = [
    path('', views.cart_view, name='cart'),
    path('add/', views.add_to_cart, name='add_to_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('clear/', views.clear_cart, name='clear_cart'),
]
