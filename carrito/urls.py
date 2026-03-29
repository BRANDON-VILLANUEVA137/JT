from django.urls import path
from . import views, webhooks

app_name = 'carrito'

urlpatterns = [
    path('', views.cart_view, name='cart'),
    path('add/', views.add_to_cart, name='add_to_cart'),
    path('update/', views.update_cart_item, name='update_cart_item'),
    path('checkout/', views.checkout, name='checkout'),
    path('success/', views.checkout_success, name='success'),
    path('clear/', views.clear_cart, name='clear_cart'),
    path('stripe/webhook/', webhooks.stripe_webhook, name='webhook'),
]
