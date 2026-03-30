# TODO: Mejorar Perfil Usuario - Dirección y Referencias

**Estado:** COMPLETADO ✅

## Pasos:

- [x] **1.** `usuarios/models.py`: Add fields ✅
- [x] **2.** `python manage.py makemigrations usuarios && python manage.py migrate` ✅
- [x] **3.** `usuarios/forms.py`: Update UserUpdateForm ✅
- [x] **4.** Update templates:
  - `usuarios/templates/usuarios/perfil.html`: ✅ Show new fields section
  - `usuarios/templates/usuarios/editar_usuario.html`: ✅ Form + new fields
- [x] **5.** Test: Editar perfil → save → view ✅

**Post:** Features integrated. Ready for pedidos/carrito integration.
