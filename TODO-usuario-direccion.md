# TODO: Mejorar Perfil Usuario - Dirección y Referencias

**Estado:** Plan aprobado.

## Pasos:

- [x] **1.** `usuarios/models.py`: Add fields to Usuario:\n  - `direccion_principal = models.TextField(blank=True, null=True)`\n  - `referencias_direccion = models.TextField(blank=True, null=True)`\n  - `telefono = models.CharField(max_length=20, blank=True)` ✅


- [ ] **2.** `python manage.py makemigrations usuarios && python manage.py migrate`

- [ ] **3.** `usuarios/forms.py`: Update UserUpdateForm:
  - fields += ['direccion_principal', 'referencias_direccion', 'telefono']
  - widgets Textarea for direccion_principal/referencias_direccion

- [ ] **4.** Update templates:
  - `usuarios/templates/usuarios/perfil.html`: Show new fields section
  - `usuarios/templates/usuarios/editar_usuario.html`: Form + new fields

- [ ] **5.** Test: Editar perfil → save → view en pedidos autocompletar.

**Post:** Update carrito/views.py usar user.direccion_principal/telefono/notas en create Pedido.

