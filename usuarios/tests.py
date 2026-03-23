from django.test import TestCase
from django.urls import reverse

from usuarios.models import Usuario, PasswordResetToken


class UsuariosHistoriaUsuarioTests(TestCase):
	def setUp(self):
		self.password = 'PassSegura123!'

		self.usuario_admin = Usuario.objects.create_user(
			username='admin1',
			email='admin1@test.com',
			password=self.password,
			primer_nombre='Ana',
			primer_apellido='Admin',
			tipo_documento='CC',
			numero_documento='10001',
			rol='admin',
		)

		self.usuario_docente = Usuario.objects.create_user(
			username='docente1',
			email='docente1@test.com',
			password=self.password,
			primer_nombre='Diego',
			primer_apellido='Docente',
			tipo_documento='CC',
			numero_documento='20001',
			rol='docente',
		)

		self.usuario_estudiante = Usuario.objects.create_user(
			username='estudiante1',
			email='estudiante1@test.com',
			password=self.password,
			primer_nombre='Elena',
			primer_apellido='Estudiante',
			tipo_documento='TI',
			numero_documento='30001',
			rol='estudiante',
		)

	def test_admin_visualiza_formulario_registro(self):
		self.client.force_login(self.usuario_admin)

		response = self.client.get(reverse('usuarios:registro'))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Crear Nuevo Usuario')

	def test_admin_puede_registrar_nuevo_usuario(self):
		self.client.force_login(self.usuario_admin)

		response = self.client.post(
			reverse('usuarios:registro'),
			{
				'primer_nombre': 'Nuevo',
				'segundo_nombre': '',
				'primer_apellido': 'Usuario',
				'segundo_apellido': '',
				'tipo_documento': 'CC',
				'numero_documento': '40001',
				'email': 'nuevo_usuario@test.com',
				'rol': 'docente',
				'especialidad': 'Matemáticas',
				'telefono_institucional': '3001234567',
			},
		)

		self.assertRedirects(response, reverse('usuarios:lista_usuarios'))
		nuevo_usuario = Usuario.objects.get(numero_documento='40001')
		self.assertEqual(nuevo_usuario.rol, 'docente')
		self.assertTrue(nuevo_usuario.must_change_password)

	def test_usuario_no_admin_no_puede_abrir_registro(self):
		self.client.force_login(self.usuario_docente)

		response = self.client.get(reverse('usuarios:registro'))

		self.assertEqual(response.status_code, 302)
		self.assertEqual(response.url, reverse('usuarios:login'))

	def test_login_exitoso_redirige_por_rol_estudiante(self):
		response = self.client.post(
			reverse('usuarios:login'),
			{'numero_documento': '30001', 'password': self.password},
		)
		self.assertRedirects(response, reverse('usuarios:dashboard_estudiante'))

	def test_login_exitoso_redirige_por_rol_docente(self):
		response = self.client.post(
			reverse('usuarios:login'),
			{'numero_documento': '20001', 'password': self.password},
		)
		self.assertRedirects(response, reverse('usuarios:dashboard_docente'))

	def test_bloqueo_temporal_tras_multiples_intentos_fallidos(self):
		for _ in range(5):
			self.client.post(
				reverse('usuarios:login'),
				{'numero_documento': '30001', 'password': 'clave_incorrecta'},
			)

		self.usuario_estudiante.refresh_from_db()
		self.assertGreaterEqual(self.usuario_estudiante.intentos_fallidos, 5)
		self.assertIsNotNone(self.usuario_estudiante.bloqueado_hasta)

	def test_usuario_bloqueado_no_puede_iniciar_sesion(self):
		for _ in range(5):
			self.client.post(
				reverse('usuarios:login'),
				{'numero_documento': '30001', 'password': 'clave_incorrecta'},
			)

		response = self.client.post(
			reverse('usuarios:login'),
			{'numero_documento': '30001', 'password': self.password},
			follow=True,
		)

		self.assertContains(response, 'Demasiados intentos fallidos', status_code=200)

	def test_recuperacion_con_email_valido_crea_token(self):
		response = self.client.post(
			reverse('usuarios:password_reset'),
			{'email': self.usuario_estudiante.email},
			follow=True,
		)

		self.assertEqual(response.status_code, 200)
		self.assertTrue(
			PasswordResetToken.objects.filter(usuario=self.usuario_estudiante).exists()
		)

	def test_reset_confirm_cambia_contrasena_y_elimina_token(self):
		token = PasswordResetToken.objects.create(
			usuario=self.usuario_estudiante,
			token=PasswordResetToken.generate_token(),
		)

		response = self.client.post(
			reverse('usuarios:password_reset_confirm', kwargs={'token': token.token}),
			{
				'nueva_password': 'NuevaPass456!',
				'confirmar_password': 'NuevaPass456!',
			},
			follow=True,
		)

		self.assertEqual(response.status_code, 200)
		self.assertFalse(
			PasswordResetToken.objects.filter(token=token.token).exists()
		)

		login_ok = self.client.login(username='estudiante1', password='NuevaPass456!')
		self.assertTrue(login_ok)
