# TODO: Implementar Eliminar y Desactivar Usuarios

## Plan aprobado:
1. ✅ Create TODO.md (this file)
2. ✅ Refreshed urls.py and views.py contents
3. ✅ Edit usuarios/urls.py: Added desactivar-usuario/<pk>/ (points to current view temp), eliminar-usuario/<pk>/
4. ✅ Edit usuarios/views.py: Added desactivar_usuario_view (soft), eliminar_usuario_view (hard)
5. ✅ Created confirmar_desactivar_usuario.html
6. ✅ Overwrote confirmar_eliminar_usuario.html (hard delete warning)
7. ✅ Edit lista_usuarios.html: Added Desactivar (warning btn-group) + Eliminar buttons for active users
8. ✅ Task complete!

## Summary:
- Added desactivar_usuario (soft) and eliminar_usuario (hard) functions
- Separate styled confirmation templates
- Buttons in lista_usuarios: Desactivar (yellow), Eliminar (red danger) for active users only

Test: `python manage.py runserver` → admin login → /usuarios/lista-usuarios/ → click buttons on active user → confirmations work, soft deactivates, hard deletes with strong warning.


