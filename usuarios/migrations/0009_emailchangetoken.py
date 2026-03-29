from django.db import migrations, models
import django.db.models.deletion
from usuarios.tokens import EmailChangeToken

class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0008_remove_docente_usuario_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailChangeToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('new_email', models.EmailField(max_length=254)),
                ('token', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='usuarios.usuario')),
            ],
        ),
    ]
