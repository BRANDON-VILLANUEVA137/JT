from django.core.management.base import BaseCommand
from usuarios.models import Usuario, Estudiante, Docente
from django.db.utils import IntegrityError
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Crea múltiples usuarios de prueba en el sistema'

    def handle(self, *args, **options):
        """
        Script para crear usuarios de prueba
        """
        
        # Definir datos de usuarios a crear
        usuarios_data = [
            # Administradores
            {
                'username': 'admin01',
                'primer_nombre': 'Juan',
                'segundo_nombre': '',
                'primer_apellido': 'Administrador',
                'segundo_apellido': '',
                'tipo_documento': 'CC',
                'numero_documento': '1001001001',
                'email': 'admin@colegio.edu.co',
                'password': 'Admin123@2024',
                'rol': 'admin',
                'is_staff': True,
                'is_superuser': True,
            },
            {
                'username': 'admin_staff',
                'primer_nombre': 'Sofía',
                'segundo_nombre': '',
                'primer_apellido': 'Soporte',
                'segundo_apellido': '',
                'tipo_documento': 'CC',
                'numero_documento': '1005005005',
                'email': 'soporte@colegio.edu.co',
                'password': 'Soporte123@2024',
                'rol': 'admin',
                'is_staff': True,
                'is_superuser': False,
            },

            # Docentes
            {
                'username': 'docente01',
                'primer_nombre': 'María',
                'segundo_nombre': 'del',
                'primer_apellido': 'García',
                'segundo_apellido': 'López',
                'tipo_documento': 'CC',
                'numero_documento': '1002002002',
                'email': 'maria.garcia@colegio.edu.co',
                'password': 'Docente123@2024',
                'rol': 'docente',
                'is_staff': True,
                'perfil': {'especialidad': 'Matemáticas', 'telefono_institucional': '601-555-1001'},
            },
            {
                'username': 'docente02',
                'primer_nombre': 'Carlos',
                'segundo_nombre': '',
                'primer_apellido': 'Rodriguez',
                'segundo_apellido': 'Martínez',
                'tipo_documento': 'CC',
                'numero_documento': '1003003003',
                'email': 'carlos.rodriguez@colegio.edu.co',
                'password': 'Docente123@2024',
                'rol': 'docente',
                'is_staff': True,
                'perfil': {'especialidad': 'Historia', 'telefono_institucional': '601-555-1002'},
            },
            {
                'username': 'docente_bloqueado',
                'primer_nombre': 'Luis',
                'segundo_nombre': '',
                'primer_apellido': 'Castaño',
                'segundo_apellido': '',
                'tipo_documento': 'CC',
                'numero_documento': '1006006006',
                'email': 'luis.castano@colegio.edu.co',
                'password': 'Docente123@2024',
                'rol': 'docente',
                'is_staff': True,
                'is_active': False,
                'perfil': {'especialidad': 'Física', 'telefono_institucional': '601-555-1003'},
            },

            # Estudiantes
            {
                'username': 'estudiante01',
                'primer_nombre': 'Pedro',
                'segundo_nombre': '',
                'primer_apellido': 'Gómez',
                'segundo_apellido': 'Pérez',
                'tipo_documento': 'TI',
                'numero_documento': '2001001001',
                'email': 'pedro.gomez@estudiante.edu.co',
                'password': 'Estudiante123@2024',
                'rol': 'estudiante',
                'is_staff': False,
                'perfil': {'codigo_estudiantil': 'EST-1001', 'grado_actual': '10-01', 'nombre_acudiente': 'Carlos Gómez', 'telefono_acudiente': '310-555-1001', 'promedio_general': 4.2},
            },
            {
                'username': 'estudiante02',
                'primer_nombre': 'Laura',
                'segundo_nombre': 'Sofia',
                'primer_apellido': 'Martínez',
                'segundo_apellido': 'Ruiz',
                'tipo_documento': 'TI',
                'numero_documento': '2002002002',
                'email': 'laura.martinez@estudiante.edu.co',
                'password': 'Estudiante123@2024',
                'rol': 'estudiante',
                'is_staff': False,
                'perfil': {'codigo_estudiantil': 'EST-1002', 'grado_actual': '11-01', 'nombre_acudiente': 'Ana Ruiz', 'telefono_acudiente': '310-555-1002', 'promedio_general': 3.5},
            },
            {
                'username': 'est_mustchange',
                'primer_nombre': 'Diana',
                'segundo_nombre': '',
                'primer_apellido': 'Vega',
                'segundo_apellido': '',
                'tipo_documento': 'TI',
                'numero_documento': '2007007007',
                'email': 'diana.vega@estudiante.edu.co',
                'password': 'Temporal123!',
                'rol': 'estudiante',
                'is_staff': False,
                'must_change_password': True,
                'perfil': {'codigo_estudiantil': 'EST-1003', 'grado_actual': '9-02', 'nombre_acudiente': 'Roberto Vega', 'telefono_acudiente': '310-555-1003', 'promedio_general': 2.8},
            },

            # Usuarios con bloqueo temporal
            {
                'username': 'locked_user',
                'primer_nombre': 'Santiago',
                'segundo_nombre': '',
                'primer_apellido': 'Ruiz',
                'segundo_apellido': '',
                'tipo_documento': 'CC',
                'numero_documento': '1008008008',
                'email': 'santiago.ruiz@colegio.edu.co',
                'password': 'Usuario123@2024',
                'rol': 'docente',
                'is_staff': False,
                'bloqueado_hasta': timezone.now() + timedelta(hours=1),
                'perfil': {'especialidad': 'Inglés', 'telefono_institucional': '601-555-1004'},
            },

            # Usuario inactivo permanentemente
            {
                'username': 'usuario_inactivo',
                'primer_nombre': 'Miguel',
                'segundo_nombre': '',
                'primer_apellido': 'Torres',
                'segundo_apellido': '',
                'tipo_documento': 'CC',
                'numero_documento': '1009009009',
                'email': 'miguel.torres@colegio.edu.co',
                'password': 'Usuario123@2024',
                'rol': 'estudiante',
                'is_staff': False,
                'is_active': False,
                'perfil': {'codigo_estudiantil': 'EST-1004', 'grado_actual': '8-01', 'nombre_acudiente': 'Laura Torres', 'telefono_acudiente': '310-555-1004', 'promedio_general': 3.0},
            },
        ]

        # Generar 100 usuarios adicionales (mezcla de admins/docentes/estudiantes)
        extra_total = 100
        admins_extra = 5
        docentes_extra = 25
        estudiantes_extra = extra_total - admins_extra - docentes_extra

        base_doc = 3000000000
        # Administradores extra
        for i in range(1, admins_extra + 1):
            usuarios_data.append({
                'username': f'admin_bulk_{i}',
                'primer_nombre': f'AdminBulk{i}',
                'segundo_nombre': '',
                'primer_apellido': 'Sistema',
                'segundo_apellido': '',
                'tipo_documento': 'CC',
                'numero_documento': str(base_doc + i),
                'email': f'admin.bulk{i}@colegio.edu.co',
                'password': f'AdminBulk{i}#2024',
                'rol': 'admin',
                'is_staff': True,
                'is_superuser': False,
            })

        # Docentes extra
        for i in range(1, docentes_extra + 1):
            usuarios_data.append({
                'username': f'doc_bulk_{i}',
                'primer_nombre': f'Doc{i}',
                'segundo_nombre': '',
                'primer_apellido': 'Profesor',
                'segundo_apellido': '',
                'tipo_documento': 'CC',
                'numero_documento': str(base_doc + admins_extra + i),
                'email': f'doc.bulk{i}@colegio.edu.co',
                'password': f'DocBulk{i}#2024',
                'rol': 'docente',
                'is_staff': True,
                'perfil': {'especialidad': 'Asignatura ' + str(i % 10 + 1), 'telefono_institucional': f'601-555-{2000+i}'},
            })

        # Estudiantes extra
        for i in range(1, estudiantes_extra + 1):
            usuarios_data.append({
                'username': f'est_bulk_{i}',
                'primer_nombre': f'Estudiante{i}',
                'segundo_nombre': '',
                'primer_apellido': 'Alumno',
                'segundo_apellido': '',
                'tipo_documento': 'TI',
                'numero_documento': str(base_doc + admins_extra + docentes_extra + i),
                'email': f'est.bulk{i}@estudiante.edu.co',
                'password': f'EstBulk{i}#2024',
                'rol': 'estudiante',
                'is_staff': False,
                'perfil': {'codigo_estudiantil': f'BULK-EST-{i:04d}', 'grado_actual': f'{9 + (i % 3)}-0{(i%6)+1}', 'nombre_acudiente': f'Acudiente{i}', 'telefono_acudiente': f'310-600-{1000+i}', 'promedio_general': round(2.0 + (i % 30) * 0.1, 2)},
            })

        # Crear usuarios
        usuarios_creados = 0
        usuarios_existentes = 0
        errores = 0

        for dato in usuarios_data:
            try:
                # Verificar si el usuario ya existe
                if Usuario.objects.filter(username=dato['username']).exists():
                    self.stdout.write(
                        self.style.WARNING(
                            f"⚠ Usuario '{dato['username']}' ya existe - omitido"
                        )
                    )
                    usuarios_existentes += 1
                    continue

                # Preparar y extraer campos especiales
                raw = dato.copy()
                password = raw.pop('password')
                perfil_data = raw.pop('perfil', None)
                is_superuser = raw.pop('is_superuser', False)
                bloqueado_hasta = raw.pop('bloqueado_hasta', None)
                must_change = raw.pop('must_change_password', False)
                # is_active e is_staff pueden venir o no; dejar en raw si existen

                # Crear usuario con los campos válidos para Usuario
                usuario = Usuario(**raw)
                usuario.set_password(password)
                usuario.is_superuser = is_superuser
                usuario.must_change_password = must_change
                if bloqueado_hasta:
                    usuario.bloqueado_hasta = bloqueado_hasta
                # Guardar
                usuario.save()

                # Crear perfil relacionado según rol
                try:
                    if perfil_data and usuario.rol == 'estudiante':
                        Estudiante.objects.create(usuario=usuario,
                                                   codigo_estudiantil=perfil_data.get('codigo_estudiantil', f"EST-{usuario.id}"),
                                                   grado_actual=perfil_data.get('grado_actual', '0-00'),
                                                   fecha_nacimiento=perfil_data.get('fecha_nacimiento', None),
                                                   nombre_acudiente=perfil_data.get('nombre_acudiente', ''),
                                                   telefono_acudiente=perfil_data.get('telefono_acudiente', ''),
                                                   promedio_general=perfil_data.get('promedio_general', 0.0)
                                                   )
                    elif perfil_data and usuario.rol == 'docente':
                        Docente.objects.create(usuario=usuario,
                                               especialidad=perfil_data.get('especialidad', 'General'),
                                               telefono_institucional=perfil_data.get('telefono_institucional', '')
                                               )
                except IntegrityError:
                    # Si el perfil ya existe o hay conflicto, continuar
                    self.stdout.write(self.style.WARNING(f"⚠ Perfil ya existe o conflicto para {usuario.username}"))

                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Usuario '{usuario.username}' ({usuario.get_nombre_completo()}) creado con rol: {usuario.rol}"
                    )
                )
                usuarios_creados += 1

            except IntegrityError as e:
                self.stdout.write(
                    self.style.ERROR(f"✗ Error de integridad para {dato.get('username','?')}: {str(e)}")
                )
                errores += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"✗ Error al crear {dato.get('username','?')}: {str(e)}")
                )
                errores += 1

        # Resumen
        self.stdout.write("-" * 60)
        self.stdout.write(self.style.SUCCESS(f"✓ Usuarios creados: {usuarios_creados}"))
        self.stdout.write(
            self.style.WARNING(f"⚠ Usuarios existentes: {usuarios_existentes}")
        )
        if errores > 0:
            self.stdout.write(self.style.ERROR(f"✗ Errores: {errores}"))
        self.stdout.write("-" * 60)
