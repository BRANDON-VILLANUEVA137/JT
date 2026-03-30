# TODO: Rediseñar Dashboard Admin (E-commerce)

**Plan aprobado por usuario - Dashboard separado para staff.**

## Pasos:

- [x] **Paso 1:** Actualizar `usuarios/views.py`:
  - Modificar `dashboard_view`: Si `request.user.is_staff` → redirect a `dashboard_admin_view`.
  - Crear `dashboard_admin_view `@staff_member_required` con métricas (total_pedidos, pedidos_pendientes='preparacion', ventas_totales=Sum(Pedido.total), total_usuarios) + últimos 5 pedidos. ✅

- [x] **Paso 2:** Actualizar `usuarios/urls.py`: Agregar `path('dashboard-admin/', views.dashboard_admin_view, name='dashboard_admin')`. ✅

- [x] **Paso 3:** Crear `usuarios/templates/usuarios/dashboard_admin.html`:
  - Cards métricas (4).
  - Cards acciones grandes (Pedidos, Usuarios, Productos, Django Admin).
  - Tabla pedidos recientes (últimos 5). ✅

**Queries para context:**
```python
from pedidos.models import Pedido
from django.db.models import Sum, Count
from Catalogo.models import Product  # para total productos si necesario

total_usuarios = Usuario.objects.count()
total_pedidos = Pedido.objects.count()
pedidos_pendientes = Pedido.objects.filter(estado='preparacion').count()
ventas_totales = Pedido.objects.aggregate(total=Sum('total'))['total'] or 0
pedidos_recientes = Pedido.objects.select_related('user').order_by('-fecha_creacion')[:5]
```

**Post:**
- Test: Login staff → auto /usuarios/dashboard-admin/
- User normal → dashboard.html original.
