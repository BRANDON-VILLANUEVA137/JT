from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0006_alter_estudiante_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='docente',
            name='firma_digital_url',
        ),
    ]
