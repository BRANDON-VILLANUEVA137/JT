# DEBUG: Cliente no ve Guía/PDF en Mis Pedidos - Checklist

**Objetivo:** Diagnosticar por qué no muestra sección (no errores consola).

## 1. PYTHON & SERVIDOR
```
- [ ] py --version
- [ ] py manage.py runserver
```
✓ Consola limpia? http://127.0.0.1:8000 OK?

## 2. DATOS PEDIDO (Admin)
```
- [ ] Login ADMIN → /admin/pedidos/pedido/
- [ ] Elegir pedido de CLIENTE
- [ ] Número de Guía = "TEST-GUIA-123" 
- [ ] Orden Flete
