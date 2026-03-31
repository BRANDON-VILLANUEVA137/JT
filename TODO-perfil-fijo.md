# Fix Perfil - Contacto/Envío Oculto

## Status: ✅ COMPLETADO

### Pasos:
- [x] 1. Identificar bug (rol 'buyer' vs 'comprador')
- [x] 2. Editar template editar_usuario.html  
- [x] 3. Testear: ir a /usuarios/editar/ → debe mostrar dirección/teléfono
- [x] 4. Completado ✅

**Bug:** Template compara `usuario.rol == 'buyer'` pero modelo usa `'comprador'`

