from django.urls import path
from . import views

app_name = 'pedidos'

urlpatterns = [
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
    path('cancelar/<int:pedido_id>/', views.cancelar_pedido, name='cancelar_pedido'),
    path('admin/', views.admin_pedidos, name='admin_pedidos'),
    path('admin/<int:pedido_id>/estado/', views.actualizar_estado_pedido, name='actualizar_estado_pedido'),
    path('admin/<int:pedido_id>/editar/', views.admin_edit_pedido, name='admin_edit_pedido'),
    path('admin/<int:pedido_id>/eliminar/', views.admin_delete_pedido, name='admin_delete_pedido'),
]
