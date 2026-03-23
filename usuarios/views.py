from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.db import transaction
from django.db.models import Q
from django.core.paginator import Paginator
from administracion.models import Matricula, AsignacionDocente, Nota

from .models import Usuario, Estudiante, Docente, PasswordResetToken
from .forms import UsuarioCreacionForm, UsuarioLoginForm
from .decoradores import requiere_admin, requiere_docente, requiere_estudiante


# ==================== Vistas Generales ====================

def index_view(request):
    """
    Vista de índice - redirige al login si no está autenticado,
    o al dashboard si está autenticado.
    """
    if request.user.is_authenticated:
        return redirect_por_rol(request.user)
    return redirect('usuarios:login')


# ==================== Vistas de Autenticación ====================

@require_http_methods(["GET", "POST"])
def login_view(request):
    """
    Vista de inicio de sesión con protección contra intentos fallidos.
    Permite login con número de documento o correo electrónico.
    Redirige automáticamente según el rol del usuario (admin, docente, estudiante).
    Bloquea temporalmente la cuenta durante 30 minutos después de 5 intentos fallidos.
    """
    if request.user.is_authenticated:
        return redirect_por_rol(request.user)
    
    contexto = {}
    
    if request.method == 'POST':
        form = UsuarioLoginForm(request.POST)
        if form.is_valid():
            usuario_input = form.cleaned_data['numero_documento']
            password = form.cleaned_data['password']
            
            # Buscar por número de documento o correo
            usuario = Usuario.objects.filter(
                Q(numero_documento=usuario_input) | Q(email=usuario_input)
            ).first()
            
            if not usuario:
                messages.error(request, 'Usuario no encontrado.')
                return render(request, 'usuarios/login.html', {'form': form})
            
            # Verificar si la cuenta está bloqueada permanentemente (por admin)
            if not usuario.is_active:
                messages.error(
                    request, 
                    'Su cuenta está bloqueada. Contacte al administrador.'
                )
                return render(request, 'usuarios/login.html', {'form': form})
            
            # Verificar si la cuenta está bloqueada temporalmente por intentos fallidos
            if usuario.cuenta_bloqueada_temporalmente():
                messages.error(
                    request, 
                    'Demasiados intentos fallidos. Intente más tarde.'
                )
                return render(request, 'usuarios/login.html', {'form': form})
            
            # Autenticar usuario
            user = authenticate(request, username=usuario.username, password=password)
            
            if user is not None:
                login(request, user)
                # Refrescar usuario desde BD después del login
                usuario.refresh_from_db()
                usuario.reiniciar_intentos_fallidos()
                
                # Forzar cambio de contraseña en primer inicio de sesión
                if request.user.must_change_password:
                    return redirect('usuarios:cambiar_password')
                
                # Redirigir según rol usando request.user
                return redirect_por_rol(request.user)
            else:
                usuario.incrementar_intentos_fallidos()
                messages.error(request, 'Contraseña incorrecta.')
        else:
            messages.error(request, 'Por favor complete los campos correctamente.')
    else:
        form = UsuarioLoginForm()
    
    contexto['form'] = form
    return render(request, 'usuarios/login.html', contexto)


def redirect_por_rol(user):
    """
    Redirige al usuario según su rol a su panel correspondiente.
    """
    if user.rol == 'admin':
        return redirect('usuarios:dashboard_admin')
    elif user.rol == 'docente':
        return redirect('usuarios:dashboard_docente')
    elif user.rol == 'estudiante':
        return redirect('usuarios:dashboard_estudiante')
    else:
        return redirect('usuarios:dashboard')


@login_required(login_url='usuarios:login')
@require_http_methods(["GET"])
def logout_view(request):
    """
    Vista de logout - cierra la sesión del usuario.
    """
    logout(request)
    messages.success(request, 'Ha cerrado sesión exitosamente.')
    return redirect('usuarios:login')


# ==================== Vistas de Registro ====================

class RegistroUsuarioView(CreateView):
    """
    Vista para registrar nuevos usuarios.
    Solo Admin puede crear usuarios en el sistema.
    Protegida: requiere estar autenticado como admin.
    """
    model = Usuario
    form_class = UsuarioCreacionForm
    template_name = 'usuarios/registro.html'
    success_url = reverse_lazy('usuarios:lista_usuarios')
    
    def get(self, request, *args, **kwargs):
        # Solo admin puede acceder
        if not request.user.is_authenticated or request.user.rol != 'admin':
            messages.error(request, 'No tiene permiso para crear usuarios.')
            return redirect('usuarios:login')
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        # Solo admin puede acceder
        if not request.user.is_authenticated or request.user.rol != 'admin':
            messages.error(request, 'No tiene permiso para crear usuarios.')
            return redirect('usuarios:login')
        return super().post(request, *args, **kwargs)
    
    @transaction.atomic
    def form_valid(self, form):
        response = super().form_valid(form)
        usuario = self.object
        
        # Si es estudiante, crear perfil de estudiante
        if usuario.rol == 'estudiante':
            datos_estudiante = form.get_estudiante_data()
            estudiante = Estudiante.objects.create(
                usuario=usuario,
                **datos_estudiante
            )
            datos_matricula = form.get_matricula_data()
            if datos_matricula:
                matricula, _ = Matricula.objects.get_or_create(
                    estudiante=estudiante,
                    año_lectivo=datos_matricula['año_lectivo'],
                    defaults={
                        'curso': datos_matricula['curso'],
                        'activa': True,
                    }
                )
                asignaciones_activas = AsignacionDocente.objects.filter(
                    curso=datos_matricula['curso'],
                    activo=True,
                ).select_related('periodo')
                notas_iniciales = [
                    Nota(
                        matrícula=matricula,
                        asignacion=asignacion,
                        periodo=asignacion.periodo,
                        valor=0.00,
                        observacion='Nota inicial automática',
                        creada_por=self.request.user,
                    )
                    for asignacion in asignaciones_activas
                    if not asignacion.periodo.cerrado
                ]
                if notas_iniciales:
                    Nota.objects.bulk_create(notas_iniciales, ignore_conflicts=True)
        
        # Si es docente, crear perfil de docente
        elif usuario.rol == 'docente':
            datos_docente = form.get_docente_data()
            Docente.objects.create(
                usuario=usuario,
                **datos_docente
            )

        # Enviar correo con credenciales iniciales
        asunto = 'Credenciales de acceso - PlaColegio'
        mensaje = (
            f'Hola {usuario.get_nombre_completo()},\n\n'
            'Tu cuenta ha sido creada en el sistema PlaColegio.\n'
            f'Usuario: {usuario.numero_documento}\n'
            f'Contraseña temporal: {usuario.numero_documento}\n\n'
            'Por seguridad, al iniciar sesión por primera vez se te pedirá cambiar la contraseña.\n\n'
            'Saludos,\nEquipo PlaColegio'
        )
        send_mail(
            asunto,
            mensaje,
            getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@placolegio.local'),
            [usuario.email],
            fail_silently=True,
        )
        
        messages.success(self.request, f'Usuario {usuario.get_nombre_completo()} creado exitosamente.')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Crear Nuevo Usuario'
        return context


# ==================== Vistas de Recuperación de Contraseña ====================

@require_http_methods(["GET", "POST"])
def password_reset_request(request):
    """
    Vista para solicitar recuperación de contraseña.
    Genera un token seguro y lo envía por correo.
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            usuario = Usuario.objects.get(email=email)
            
            # Generar token seguro
            token = PasswordResetToken.generate_token()
            
            # Guardar token en base de datos (eliminar tokens anteriores expirados)
            PasswordResetToken.objects.filter(usuario=usuario, created_at__lt=
                                            timezone.now() - timezone.timedelta(hours=24)).delete()
            
            # Crear nuevo token
            reset_token = PasswordResetToken.objects.create(
                usuario=usuario,
                token=token
            )
            
            # Construir URL de recuperación
            reset_url = request.build_absolute_uri(
                reverse_lazy('usuarios:password_reset_confirm', kwargs={'token': token})
            )
            
            # Enviar correo
            asunto = 'Recuperación de Contraseña - PlaColegio'
            mensaje = (
                f'Hola {usuario.get_nombre_completo()},\n\n'
                'Has solicitado recuperar tu contraseña en PlaColegio.\n'
                'Haz clic en el siguiente enlace para crear una nueva contraseña:\n\n'
                f'{reset_url}\n\n'
                'Este enlace es válido por 24 horas.\n'
                'Si no solicitaste esto, ignora este mensaje.\n\n'
                'Saludos,\nEquipo PlaColegio'
            )
            send_mail(
                asunto,
                mensaje,
                getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@placolegio.local'),
                [usuario.email],
                fail_silently=True,
            )
            
            messages.success(
                request,
                'Se ha enviado un enlace de recuperación a su email. Revise su bandeja de entrada.'
            )
        except Usuario.DoesNotExist:
            # Por seguridad, mostrar mismo mensaje aunque el correo no exista
            messages.success(
                request,
                'Si el correo existe en el sistema, recibirá un enlace de recuperación.'
            )
        
        return redirect('usuarios:login')
    
    return render(request, 'usuarios/password_reset.html')


@require_http_methods(["GET", "POST"])
def password_reset_confirm(request, token):
    """
    Vista para confirmar y cambiar la contraseña con el token de recuperación.
    """
    try:
        reset_token = PasswordResetToken.objects.get(token=token)
        
        if not reset_token.is_valid():
            messages.error(
                request,
                'El enlace de recuperación ha expirado. Solicite uno nuevo.'
            )
            return redirect('usuarios:password_reset')
        
        usuario = reset_token.usuario
        
        if request.method == 'POST':
            nueva_password = request.POST.get('nueva_password')
            confirmar_password = request.POST.get('confirmar_password')
            
            if not nueva_password or not confirmar_password:
                messages.error(request, 'Debe llenar todos los campos.')
                return render(request, 'usuarios/password_reset_confirm.html')
            
            if nueva_password != confirmar_password:
                messages.error(request, 'Las contraseñas no coinciden.')
                return render(request, 'usuarios/password_reset_confirm.html')
            
            if len(nueva_password) < 8:
                messages.error(request, 'La contraseña debe tener al menos 8 caracteres.')
                return render(request, 'usuarios/password_reset_confirm.html')
            
            # Cambiar contraseña en la base de datos
            usuario.set_password(nueva_password)
            usuario.save()
            
            # Eliminar el token usado
            reset_token.delete()
            
            messages.success(request, 'Contraseña actualizada exitosamente. Inicie sesión.')
            return redirect('usuarios:login')
        
        return render(request, 'usuarios/password_reset_confirm.html', {
            'usuario': usuario,
            'token': token
        })
    
    except PasswordResetToken.DoesNotExist:
        messages.error(
            request,
            'El enlace de recuperación es inválido o ha expirado.'
        )
        return redirect('usuarios:password_reset')


# ==================== Vistas de Cambio de Contraseña ====================

@login_required(login_url='usuarios:login')
@require_http_methods(["GET", "POST"])
def cambiar_password(request):
    """
    Fuerza el cambio de contraseña en el primer inicio de sesión.
    Protegida: requiere estar autenticado.
    """
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            user.must_change_password = False
            user.save(update_fields=['must_change_password'])
            update_session_auth_hash(request, user)
            messages.success(request, 'Contraseña actualizada correctamente.')
            return redirect_por_rol(request.user)
        else:
            messages.error(request, 'Revise los errores del formulario.')
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, 'usuarios/cambiar_password.html', {'form': form})


# ==================== Vistas de Dashboard ====================

@login_required(login_url='usuarios:login')
def dashboard_view(request):
    """
    Dashboard principal - redirige según el rol.
    """
    return redirect_por_rol(request.user)


@login_required(login_url='usuarios:login')
@requiere_admin
def dashboard_admin(request):
    """
    Panel de control para administradores.
    Protegida: requiere estar autenticado como admin.
    """
    contexto = {
        'total_usuarios': Usuario.objects.count(),
        'total_estudiantes': Estudiante.objects.count(),
        'total_docentes': Docente.objects.count(),
        'usuarios_bloqueados': Usuario.objects.filter(is_active=False).count(),
    }
    
    return render(request, 'usuarios/dashboard_admin.html', contexto)


@login_required(login_url='usuarios:login')
@requiere_docente
def dashboard_docente(request):
    """
    Panel de control para docentes.
    Protegida: requiere estar autenticado como docente.
    """
    try:
        perfil_docente = request.user.perfil_docente
    except Docente.DoesNotExist:
        perfil_docente = None
    
    contexto = {
        'perfil_docente': perfil_docente,
    }
    
    return render(request, 'usuarios/dashboard_docente.html', contexto)


@login_required(login_url='usuarios:login')
@requiere_estudiante
def dashboard_estudiante(request):
    """
    Panel de control para estudiantes.
    Protegida: requiere estar autenticado como estudiante.
    """
    try:
        perfil_estudiante = request.user.perfil_estudiante
    except Estudiante.DoesNotExist:
        perfil_estudiante = None
    
    contexto = {
        'perfil_estudiante': perfil_estudiante,
    }
    
    return render(request, 'usuarios/dashboard_estudiante.html', contexto)


# ==================== Vistas de Perfil ====================

@login_required(login_url='usuarios:login')
def perfil_usuario(request):
    """
    Vista del perfil del usuario autenticado.
    """
    usuario = request.user
    estudiante = None
    docente = None
    
    if usuario.rol == 'estudiante':
        try:
            estudiante = usuario.perfil_estudiante
        except Estudiante.DoesNotExist:
            pass
    
    elif usuario.rol == 'docente':
        try:
            docente = usuario.perfil_docente
        except Docente.DoesNotExist:
            pass
    
    contexto = {
        'usuario': usuario,
        'estudiante': estudiante,
        'docente': docente,
    }
    
    return render(request, 'usuarios/perfil.html', contexto)


@login_required(login_url='usuarios:login')
def perfil_usuario_admin(request, pk):
    """
    Vista para que admin vea el perfil de un usuario específico.
    """
    if request.user.rol != 'admin':
        messages.error(request, 'No tiene permiso para acceder a esta página.')
        return redirect_por_rol(request.user)
    
    usuario = get_object_or_404(Usuario, pk=pk)
    estudiante = None
    docente = None
    
    if usuario.rol == 'estudiante':
        try:
            estudiante = usuario.perfil_estudiante
        except Estudiante.DoesNotExist:
            pass
    
    elif usuario.rol == 'docente':
        try:
            docente = usuario.perfil_docente
        except Docente.DoesNotExist:
            pass
    
    contexto = {
        'usuario': usuario,
        'estudiante': estudiante,
        'docente': docente,
        'es_admin_view': True,
    }
    
    return render(request, 'usuarios/perfil.html', contexto)


# ==================== Vistas de Admin ====================

@login_required(login_url='usuarios:login')
@requiere_admin
def lista_usuarios(request):
    """
    Lista todos los usuarios del sistema.
    Protegida: requiere estar autenticado como admin.
    """
    busqueda = (request.GET.get('q') or '').strip()
    rol = (request.GET.get('rol') or '').strip()
    estado = (request.GET.get('estado') or '').strip()

    usuarios = Usuario.objects.all().order_by(
        'primer_apellido',
        'segundo_apellido',
        'primer_nombre',
    )

    if busqueda:
        usuarios = usuarios.filter(
            Q(primer_nombre__icontains=busqueda)
            | Q(segundo_nombre__icontains=busqueda)
            | Q(primer_apellido__icontains=busqueda)
            | Q(segundo_apellido__icontains=busqueda)
            | Q(numero_documento__icontains=busqueda)
            | Q(email__icontains=busqueda)
            | Q(username__icontains=busqueda)
        )

    if rol in {'admin', 'docente', 'estudiante'}:
        usuarios = usuarios.filter(rol=rol)

    if estado == 'activos':
        usuarios = usuarios.filter(is_active=True)
    elif estado == 'bloqueados':
        usuarios = usuarios.filter(is_active=False)

    paginador = Paginator(usuarios, 10)
    usuarios_pagina = paginador.get_page(request.GET.get('page'))

    contexto = {
        'usuarios': usuarios_pagina,
        'total_usuarios': paginador.count,
        'q': busqueda,
        'rol_filtro': rol,
        'estado_filtro': estado,
    }
    
    return render(request, 'usuarios/lista_usuarios.html', contexto)


@login_required(login_url='usuarios:login')
@requiere_admin
def bloquear_usuario(request, pk):
    """
    Bloquea una cuenta de usuario.
    Protegida: requiere estar autenticado como admin.
    """
    usuario = get_object_or_404(Usuario, pk=pk)

    # Evitar que un administrador se bloquee a sí mismo
    if request.user.pk == usuario.pk:
        messages.error(request, 'No puede bloquear su propia cuenta.')
        return redirect('usuarios:lista_usuarios')

    # Bloqueo por parte del administrador: desactivar la cuenta permanentemente
    usuario.is_active = False
    # Limpiar cualquier bloqueo temporal previo
    usuario.bloqueado_hasta = None
    usuario.save(update_fields=['is_active', 'bloqueado_hasta'])

    messages.success(request, f'Usuario {usuario.get_nombre_completo()} bloqueado.')
    return redirect('usuarios:lista_usuarios')


@login_required(login_url='usuarios:login')
@requiere_admin
def desbloquear_usuario(request, pk):
    """
    Desbloquea una cuenta de usuario.
    Protegida: requiere estar autenticado como admin.
    """
    usuario = get_object_or_404(Usuario, pk=pk)
    usuario.desbloquear_cuenta()
    messages.success(request, f'Usuario {usuario.get_nombre_completo()} desbloqueado.')
    
    return redirect('usuarios:lista_usuarios')


@login_required(login_url='usuarios:login')
@require_http_methods(["GET", "POST"])
@requiere_admin
def editar_usuario(request, pk):
    """
    Edita los datos de un usuario.
    Protegida: requiere estar autenticado como admin.
    """
    usuario = get_object_or_404(Usuario, pk=pk)
    
    if request.method == 'POST':
        # Actualizar datos básicos
        usuario.primer_nombre = request.POST.get('primer_nombre', usuario.primer_nombre)
        usuario.segundo_nombre = request.POST.get('segundo_nombre', usuario.segundo_nombre)
        usuario.primer_apellido = request.POST.get('primer_apellido', usuario.primer_apellido)
        usuario.segundo_apellido = request.POST.get('segundo_apellido', usuario.segundo_apellido)
        usuario.email = request.POST.get('email', usuario.email)
        
        try:
            usuario.save()
            # Actualizar perfil específico si existe
            if usuario.rol == 'estudiante':
                try:
                    estudiante = usuario.perfil_estudiante
                    estudiante.fecha_nacimiento = request.POST.get('fecha_nacimiento') or None
                    estudiante.nombre_acudiente = request.POST.get('nombre_acudiente', '')
                    estudiante.telefono_acudiente = request.POST.get('telefono_acudiente', '')
                    estudiante.save()
                except Estudiante.DoesNotExist:
                    pass
            
            elif usuario.rol == 'docente':
                try:
                    docente = usuario.perfil_docente
                    docente.especialidad = request.POST.get('especialidad', docente.especialidad)
                    docente.telefono_institucional = request.POST.get('telefono_institucional', '')
                    docente.save()
                except Docente.DoesNotExist:
                    pass
            
            messages.success(request, f'Usuario {usuario.get_nombre_completo()} actualizado exitosamente.')
            return redirect('usuarios:lista_usuarios')
        except Exception as e:
            messages.error(request, f'Error al actualizar: {str(e)}')
    
    estudiante = None
    docente = None
    
    if usuario.rol == 'estudiante':
        try:
            estudiante = usuario.perfil_estudiante
        except Estudiante.DoesNotExist:
            pass
    elif usuario.rol == 'docente':
        try:
            docente = usuario.perfil_docente
        except Docente.DoesNotExist:
            pass
    
    contexto = {
        'usuario': usuario,
        'estudiante': estudiante,
        'docente': docente,
    }
    
    return render(request, 'usuarios/editar_usuario.html', contexto)


@login_required(login_url='usuarios:login')
@require_http_methods(["GET", "POST"])
@requiere_admin
def eliminar_usuario(request, pk):
    """
    Elimina un usuario del sistema (no puede eliminarse a sí mismo).
    Protegida: requiere estar autenticado como admin.
    """
    usuario = get_object_or_404(Usuario, pk=pk)
    
    # No permitir que un admin se elimine a sí mismo
    if request.user.pk == usuario.pk:
        messages.error(request, 'No puede eliminar su propia cuenta.')
        return redirect('usuarios:lista_usuarios')
    
    if request.method == 'POST':
        nombre = usuario.get_nombre_completo()
        usuario.delete()
        messages.success(request, f'Usuario {nombre} eliminado exitosamente.')
        return redirect('usuarios:lista_usuarios')
    
    contexto = {
        'usuario': usuario,
    }
    
    return render(request, 'usuarios/confirmar_eliminar.html', contexto)
