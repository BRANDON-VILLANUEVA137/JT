from django.contrib import admin
from .models import Lote, MovimientoInventario, UnidadIndividual, ConteoFisico, ConteoFisicoItem, AlertaStock


@admin.register(Lote)
class LoteAdmin(admin.ModelAdmin):
    list_display = ('codigo_lote', 'product', 'cantidad_actual', 'fecha_vencimiento', 'activo')
    list_filter = ('activo', 'product')
    search_fields = ('codigo_lote', 'product__name', 'proveedor')


@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'product', 'tipo', 'cantidad', 'stock_anterior', 'stock_posterior', 'usuario')
    list_filter = ('tipo', 'referencia_tipo')
    search_fields = ('product__name', 'notas', 'referencia_id')
    readonly_fields = ('stock_anterior', 'stock_posterior', 'fecha_creacion')


@admin.register(UnidadIndividual)
class UnidadIndividualAdmin(admin.ModelAdmin):
    list_display = ('codigo_interno', 'product', 'estado', 'lote', 'fecha_ingreso')
    list_filter = ('estado', 'product')
    search_fields = ('codigo_interno', 'product__name')


@admin.register(ConteoFisico)
class ConteoFisicoAdmin(admin.ModelAdmin):
    list_display = ('codigo_conteo', 'fecha_conteo', 'estado', 'usuario')
    list_filter = ('estado',)


@admin.register(ConteoFisicoItem)
class ConteoFisicoItemAdmin(admin.ModelAdmin):
    list_display = ('conteo', 'product', 'stock_sistema', 'stock_contado', 'diferencia')
    list_filter = ('conteo__estado',)


@admin.register(AlertaStock)
class AlertaStockAdmin(admin.ModelAdmin):
    list_display = ('product', 'stock_minimo', 'activo', 'ultima_notificacion')
    list_filter = ('activo',)
    search_fields = ('product__name',)