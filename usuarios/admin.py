from django.contrib import admin

from django.contrib import admin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('get_nombre_completo', 'username', 'numero_documento', 'email', 'rol', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('rol', 'is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('primer_nombre', 'username', 'numero_documento', 'email')
    readonly_fields = ('date_joined', 'last_login')
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('primer_nombre', 'numero_documento', 'email', 'rol')
        }),
        ('Dirección y Contacto', {
            'fields': ('direccion_principal', 'referencias_direccion', 'telefono')
        }),
        ('Estado y Seguridad', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'date_joined', 'last_login')
        }),
    )
    
    def get_nombre_completo(self, obj):
        return obj.get_nombre_completo()
    get_nombre_completo.short_description = 'Nombre Completo'
    get_nombre_completo.admin_order_field = 'primer_nombre'

