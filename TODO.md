# TODO.md - TECH-JUANJO Marketplace MVP

Proyecto Django e-commerce marketplace (nuevos/usados tech products).

## Plan Aprobado (6 Sprints)

### 1. Config & Auth Adaptation ✅ In Progress
- [ ] Update settings.py (apps, AUTH_USER_MODEL, static/media)
- [ ] Adapt usuarios/models.py (roles: buyer/seller/admin, remove school models)
- [ ] Update usuarios/decorators.py, forms.py, views.py, templates (marketplace UI/roles)
- [ ] Base templates/ base.html (nav: catalog/cart/orders/profile)
- [ ] Wire urls
- [ ] Migrations + test auth

### 2. Catalog (Sprint 2)
- [ ] Catalogo/models.py (Product/Category/Brand)
- [ ] Views: list/search/filter/detail
- [ ] URLs/templates

### 3. Cart (Sprint 3)
- [ ] carrito/models.py (Cart/CartItem)
- [ ] Views/URLs/templates

### 4. Orders & Checkout (Sprint 4-5)
- [ ] pedidos/models.py (Order/OrderItem)
- [ ] Views/URLs/templates

### 5. Payments (Sprint 6)
- [ ] payments app + Stripe

### 6. Polish/Deploy
- [ ] HTMX, seed data, tests

## Next: Config & Auth (Step 1 complete → mark here after)
