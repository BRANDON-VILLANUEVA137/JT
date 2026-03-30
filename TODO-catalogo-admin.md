# Arreglar NoReverseMatch en Catalogo para añadir productos

Status: Pendiente

**Problema:**
@staff_member_required en Catalogo/views.py causa error 'admin' namespace

**Plan:**
1. Reemplazar todos @staff_member_required con @login_required + manual check rol='admin'
2. Usar decoradores existentes en usuarios/decoradores.py
3. Mantener URLs custom (no usar Django admin)

**Archivos a editar:**
- Catalogo/views.py (múltiples funciones: product_create, product_update, etc.)

**Próximo paso:** Editar Catalogo/views.py

