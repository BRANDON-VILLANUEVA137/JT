from django.contrib import admin
from .models import Pedido, PedidoItem, PedidoDocument

class PedidoItemInline(admin.TabularInline):
    model = PedidoItem
    readonly_fields = ('subtotal',)
    fields = ('product', 'cantidad', 'precio_unitario', 'subtotal')
    extra = 0
    can_delete = False

    def subtotal(self, obj):
        return obj.subtotal()
    subtotal.short_description = 'Subtotal'
    subtotal.admin_order_field = 'subtotal'

class PedidoDocumentInline(admin.TabularInline):
    model = PedidoDocument
    fields = ('description', 'file', 'uploaded_at')
    readonly_fields = ('uploaded_at',)
    extra = 1

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total', 'estado', 'fecha_creacion', 'stripe_session_id')
    list_filter = ('estado', 'fecha_creacion')
    search_fields = ('id', 'user__username', 'stripe_session_id')
    readonly_fields = ('fecha_creacion', 'stripe_session_id')
    inlines = [PedidoItemInline, PedidoDocumentInline]
    fieldsets = (
        ('Info Pedido', {
            'fields': ('user', 'total', 'estado', 'direccion', 'telefono', 'fecha_creacion', 'stripe_session_id')
        }),
    )

admin.site.register(PedidoItem)  # Simple list
