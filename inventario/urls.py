from django.urls import path
from . import views

app_name = 'inventario'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Movimientos
    path('movimientos/', views.movimiento_list, name='movimiento_list'),
    path('movimientos/nuevo/', views.movimiento_create, name='movimiento_create'),
    path('movimientos/entrada-compra/', views.entrada_compra, name='entrada_compra'),
    path('movimientos/salida-merma/', views.salida_merma, name='salida_merma'),
    
    # Lotes
    path('lotes/', views.lote_list, name='lote_list'),
    path('lotes/nuevo/', views.lote_create, name='lote_create'),
    path('lotes/<int:pk>/', views.lote_detail, name='lote_detail'),
    
    # Unidades individuales
    path('unidades/', views.unidad_list, name='unidad_list'),
    path('unidades/nuevo/', views.unidad_create, name='unidad_create'),
    path('unidades/<int:pk>/editar/', views.unidad_update, name='unidad_update'),
    
    # Conteo físico
    path('conteos/', views.conteo_list, name='conteo_list'),
    path('conteos/nuevo/', views.conteo_create, name='conteo_create'),
    path('conteos/<int:pk>/', views.conteo_detail, name='conteo_detail'),
    path('conteos/<int:pk>/completar/', views.conteo_completar, name='conteo_completar'),
    path('conteos/<int:pk>/cancelar/', views.conteo_cancelar, name='conteo_cancelar'),
    path('conteos/item/<int:item_pk>/eliminar/', views.conteo_eliminar_item, name='conteo_eliminar_item'),
    
    # Alertas de stock
    path('alertas/', views.alerta_list, name='alerta_list'),
    path('alertas/nuevo/', views.alerta_create, name='alerta_create'),
    path('alertas/<int:pk>/editar/', views.alerta_update, name='alerta_update'),
    path('alertas/<int:pk>/eliminar/', views.alerta_delete, name='alerta_delete'),
    
    # Stock general de productos
    path('productos/', views.producto_stock, name='producto_stock'),
]