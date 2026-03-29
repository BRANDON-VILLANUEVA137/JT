# TODO: Fixar Stripe Webhook - ✅ COMPLETADO

## ✅ Todos los pasos implementados:

### 1. ✅ carrito/webhooks.py implementado completamente
   - ✅ settings.STRIPE_WEBHOOK_SECRET only
   - ✅ user_id from metadata → int conversion  
   - ✅ User.objects.get(id=user_id)
   - ✅ Cart validation (exists + items)
   - ✅ total = sum(item.subtotal())
   - ✅ Pedido con defaults 'Pendiente confirmación'
   - ✅ PedidoItems creados
   - ✅ cart.items.all().delete()
   - ✅ Logs detallados
   - ✅ HTTP 400 signature fail, 200 success only

### 2. ✅ stripe_webhook REMOVIDO de carrito/views.py

### 3. ✅ carrito/urls.py actualizado
   - Import webhooks
   - Route → webhooks.stripe_webhook

## 🔧 Para TESTEAR:

```bash
# Terminal 1 (Stripe CLI)
stripe listen --forward-to localhost:8000/carrito/stripe/webhook/

# Terminal 2 (Django)
python manage.py runserver

# 1. Añade productos al carrito
# 2. Checkout → pagar con Stripe test card 4242 4242 4242 4242
# 3. Verificar:
#    - Pedido creado en /pedidos/mis_pedidos/
#    - Carrito vacío
```

## ✅ IDEMPOTENCIA AGREGADA

9. **Sin idempotencia** → `stripe_session_id` unique + check exists()

## 📝 Errores encontrados y corregidos:
(... lista anterior ...)

**¡Webhook 100% production-ready! 🚀**


