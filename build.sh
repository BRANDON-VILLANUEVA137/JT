#!/usr/bin/env bash

pip install -r requirements.txt

python manage.py migrate

echo "
from django.contrib.auth import get_user_model
User = get_user_model()

user, created = User.objects.get_or_create(
    username='ADMIN',
    defaults={
        'email': 'admin@gmail.com',
        'primer_nombre': 'ADMIN',
        'numero_documento': '0000000000',
        'rol': 'admin'
    }
)

user.set_password('admin')
user.is_staff = True
user.is_superuser = True
user.primer_nombre = 'ADMIN'
user.numero_documento = '0000000000'
user.rol = 'admin'
user.email = 'admin@gmail.com'
user.save()
" | python manage.py shell