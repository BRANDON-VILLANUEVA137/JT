# TODO: Show User Address/Phone in Pedidos Management

**Status:** Plan approved ✅

## Steps:
- [x] 1. Create TODO ✅
- [x] 2. Create carrito/templates/carrito/checkout.html: Prefill form with user.direccion_principal/telefono ✅
- [ ] 3. Update carrito/views.py checkout: Use form data → create Pedido with address/phone
- [ ] 4. Update pedidos/webhooks.py: Use checkout data for final Pedido
- [ ] 5. Test: Add to cart → checkout → verify pedidos show address/phone
- [ ] 6. Complete

**Note:** Templates already expect fields; just populate at creation.

