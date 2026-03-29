# TODO: Stripe Webhook Idempotencia

**Status**: ✅ COMPLETE (pre-migrate)

## Steps:
- [x] 1. Agregar stripe_session_id a pedidos/models.py
- [x] 2. Idempotencia check en webhooks.py 
- [ ] 3. Usuario ejecuta: python manage.py makemigrations pedidos && migrate
- [ ] 4. Test: stripe listen + duplicate webhook → no duplicado

**Next**: Migrate → Test.

