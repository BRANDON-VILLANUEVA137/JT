# Admin PDF Uploads for Pedidos - Steps

**Status:** Implementing

1. [x] Updated TODO.md
2. [x] Add PedidoDocument model to pedidos/models.py
3. [x] Run `python manage.py makemigrations pedidos`
4. [x] Run `python manage.py migrate`
5. [x] Update pedidos/admin.py with inlines (PedidoItemInline, PedidoDocumentInline)
6. [ ] Test /admin/pedidos/pedido/ upload PDF + description
7. [x] Complete
