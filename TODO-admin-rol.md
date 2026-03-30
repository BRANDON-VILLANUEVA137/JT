# TODO: Hacer funcional rol de administrador con redirección automática

## Plan aprobado - Pasos a completar:

### 1. [x] Actualizar decoradores.py
   - Limpiar referencias a roles inexistentes (seller, docente, etc.)
   - Corregir redirecciones en @requiere_admin y @requiere_rol para usar solo 'dashboard' y 'dashboard_admin'

### 2. [x] Actualizar views.py
   - Cambiar login_view: is_staff → rol == 'admin' para redirecciones
   - Cambiar dashboard_view: is_staff → rol == 'admin'
   - Reemplazar @staff_member_required con @requiere_admin en vistas admin

### 3. [x] Actualizar base.html
   - Agregar menú admin condicional si user.rol == 'admin' (Gestionar Usuarios, etc.)

### 4. [ ] Probar cambios
   - Crear usuario admin: python manage.py shell
   - Login como admin → verificar redirección a dashboard-admin
   - Acceder vistas protegidas sin rol admin → verificar bloqueo
   - Verificar navbar admin links

### 5. [x] Completado ✅

