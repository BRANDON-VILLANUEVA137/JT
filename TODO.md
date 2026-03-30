# TODO: Implementar funcionalidades de Editar y Eliminar Pedidos para Admin

**Estado del proyecto:** Plan aprobado por usuario con ajustes específicos.

## Pasos del Plan (marcar con [x] al completar):

- [x] **Paso 1:** Crear `pedidos/forms.py` con `PedidoForm` (solo editable: estado, telefono, direccion; exclude: user, total, fecha_creacion, stripe_session_id). ✅

- [x] **Paso 2:** Crear templates:\n  - `pedidos/templates/pedidos/admin_editar_pedido.html` (form para editar).\n  - `pedidos/templates/pedidos/admin_confirmar_eliminar.html` (confirm delete). ✅

- [x] **Paso 3:** Actualizar `pedidos/views.py`:
  - Agregar `admin_edit_pedido` (GET/POST form).
  - Agregar `admin_delete_pedido` (solo si estado='preparacion' Y no stripe_session_id). ✅

- [x] **Paso 4:** Actualizar `pedidos/urls.py` con nuevas rutas:
  - `admin/<int:pedido_id>/editar/`
  - `admin/<int:pedido_id>/eliminar/` ✅

- [x] **Paso 5:** Actualizar `pedidos/templates/pedidos/admin_pedidos.html`: Agregar botones Editar/Eliminar en columna Acciones. ✅

**Notas/Ajustes del usuario:**
- NO editar `total`.
- Eliminar solo si `estado='preparacion'` Y `stripe_session_id` vacío/null.
- Páginas separadas (no modals).
- Solo `is_staff=True` (@staff_member_required).

**Post-implementación:**
- Probar con `python manage.py runserver`.
- Verificar en /pedidos/admin/ como admin.
