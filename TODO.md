# TODO: Fix Mis Pedidos 404 Error

## Completado ✅
- [x] 1. Edit templates/base.html: Replace hardcoded `/mis-pedidos/` with `{% url 'pedidos:mis_pedidos' %}`  
- [x] 2. Fix template inheritance: Changed `{% extends 'usuarios/base.html' %}` → `{% extends 'base.html' %}` in all 4 pedidos templates

## Pendientes
- [ ] 3. Test navigation from navbar dropdown  
- [ ] 4. Verify /pedidos/mis-pedidos/ loads correctly
- [ ] 5. Complete task
