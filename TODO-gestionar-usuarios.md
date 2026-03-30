# TODO: Hacer que Gestionar Usuarios funcione (Aprobado)

**Estado**: Pendiente

## Pasos del Plan:

### 1. Registrar Usuario en Django Admin\n- [x] Editar `usuarios/admin.py`: Custom ModelAdmin (list_display, search_fields, etc.) ✅

### 2. Forms\n- [x] `usuarios/forms.py`: Añadir `AdminUserForm` (edit rol/is_active) ✅

### 3. Vistas CRUD Admin
- [ ] `usuarios/views.py`: 
  - lista_usuarios_view (paginated/search/filter)
  - crear_usuario_view
  - editar_usuario_admin_view(pk)
  - eliminar_usuario_view(pk)

### 4. URLs
- [ ] `usuarios/urls.py`: paths lista-usuarios/, crear-usuario/, editar-usuario/<int:pk>/, eliminar-usuario/<int:pk>/

### 5. Templates
- [ ] Editar `dashboard_admin.html`: Añadir card/link a lista_usuarios
- [ ] Crear `lista_usuarios.html` (tabla/search/paginate/actions)
- [ ] Crear `crear_usuario.html`
- [ ] Crear `editar_usuario_admin.html`
- [ ] Crear `confirmar_eliminar_usuario.html`

### 6. Limpieza
- [ ] `decoradores.py`: Simplificar o remover (usa is_staff)

### 7. Test
- [ ] Crear superuser si no existe
- [ ] Test CRUD con staff user
- [ ] Marcar completado

**Post-edits**: Actualizar este TODO con [x] al completar cada paso.

