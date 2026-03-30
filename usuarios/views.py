from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.conf import settings
from .forms import LoginForm, RegisterForm, UserUpdateForm, PasswordChangeCustomForm, EmailChangeForm
from .models import Usuario
from .tokens import EmailChangeToken

def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('usuarios:dashboard')
        return redirect('/')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            login_field = form.cleaned_data['login_field']
            password = form.cleaned_data['password']
            
            # Try numero_documento
            try:
                user = Usuario.objects.get(numero_documento=login_field)
                user = authenticate(request, username=user.username, password=password)
            except Usuario.DoesNotExist:
                # Try username or email
                user = authenticate(request, username=login_field, password=password)
            
            if user:
                login(request, user)
                if user.is_staff:
                    return redirect('usuarios:dashboard')
                return redirect('/')
            else:
                messages.error(request, 'Credenciales inválidas')
    else:
        form = LoginForm()
    
    return render(request, 'usuarios/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'Sesión cerrada')
    return redirect('usuarios:login')

def registro_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Usuario creado. Inicia sesión.')
            return redirect('usuarios:login')
    else:
        form = RegisterForm()
    
    return render(request, 'usuarios/registro.html', {'form': form})


@login_required(login_url='usuarios:login')
def dashboard_view(request):
    if request.user.is_staff:
        return redirect('usuarios:dashboard_admin')
    return render(request, 'usuarios/dashboard.html')


@login_required(login_url='usuarios:login')
def perfil_view(request):
    return render(request, 'usuarios/perfil.html', {
        'usuario': request.user,
    })


@login_required(login_url='usuarios:login')
def editar_usuario_view(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('usuarios:perfil')
    else:
        form = UserUpdateForm(instance=request.user)

    return render(request, 'usuarios/editar_usuario.html', {
        'form': form,
        'usuario': request.user,
    })


@login_required(login_url='usuarios:login')
def cambiar_password_view(request):
    form = PasswordChangeCustomForm(request.user)
    if request.method == 'POST':
        form = PasswordChangeCustomForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Contraseña cambiada exitosamente.')
            logout(request)
            return redirect('usuarios:login')

    return render(request, 'usuarios/cambiar_password.html', {
        'form': form,
    })


@login_required(login_url='usuarios:login')
def cambiar_email_view(request):
    form = EmailChangeForm(request.user)
    if request.method == 'POST':
        form = EmailChangeForm(request.user, request.POST)
        if form.is_valid():
            new_email = form.cleaned_data['new_email']
            token = EmailChangeToken.generate_token(request.user, new_email)
            
            # Email verification link
            verification_url = request.build_absolute_uri(f'/usuarios/confirm-email/{token}/')
            
            # Send email (console in dev)
            send_mail(
                'Confirmar cambio de email - TECH-JUANJO',
                f'Hola {request.user.get_nombre_completo()},\n\n'
                f'Para confirmar tu nuevo email {new_email}, click:\n{verification_url}\n\n'
                f'Token expira en 1 hora.\n\nSaludos,\nTECH-JUANJO',
                settings.DEFAULT_FROM_EMAIL,
                [new_email],
                fail_silently=False,
            )
            
            messages.success(request, f'Verificación enviada a {new_email}. Click link en 1h.')
            return redirect('usuarios:perfil')
    
    return render(request, 'usuarios/cambiar_email.html', {
        'form': form,
    })


@login_required(login_url='usuarios:login')
def confirm_email_view(request, token):
    try:
        token_obj = EmailChangeToken.objects.get(token=token)
        if token_obj.is_valid():
            request.user.email = token_obj.new_email
            request.user.save()
            token_obj.delete()
            messages.success(request, f'Email cambiado a {request.user.email} exitosamente.')
        else:
            messages.error(request, 'Token expirado o inválido.')
    except EmailChangeToken.DoesNotExist:
        messages.error(request, 'Token inválido.')
    
    return redirect('usuarios:perfil')

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum
from pedidos.models import Pedido
from .models import Usuario

@staff_member_required
def dashboard_admin_view(request):
    total_usuarios = Usuario.objects.count()
    total_pedidos = Pedido.objects.count()
    pedidos_pendientes = Pedido.objects.filter(estado='preparacion').count()
    ventas_totales = Pedido.objects.aggregate(total=Sum('total'))['total'] or 0
    pedidos_recientes = Pedido.objects.select_related('user').order_by('-fecha_creacion')[:5]
    
    context = {
        'total_usuarios': total_usuarios,
        'total_pedidos': total_pedidos,
        'pedidos_pendientes': pedidos_pendientes,
        'ventas_totales': ventas_totales,
        'pedidos_recientes': pedidos_recientes,
    }
    return render(request, 'usuarios/dashboard_admin.html', context)


from django.core.paginator import Paginator
from django.db.models import Q
from .forms import AdminUserForm, RegisterForm


@staff_member_required
def lista_usuarios_view(request):
    query = request.GET.get('q', '')
    rol_filter = request.GET.get('rol', '')
    is_active_filter = request.GET.get('is_active', '')

    usuarios = Usuario.objects.all()

    if query:
        usuarios = usuarios.filter(
            Q(primer_nombre__icontains=query) |
            Q(username__icontains=query) |
            Q(numero_documento__icontains=query) |
            Q(email__icontains=query)
        )

    if rol_filter:
        usuarios = usuarios.filter(rol=rol_filter)

    if is_active_filter:
        usuarios = usuarios.filter(is_active=(is_active_filter == 'true'))

    total_usuarios = usuarios.count()
    total_activos = usuarios.filter(is_active=True).count()

    paginator = Paginator(usuarios, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
        'rol_filter': rol_filter,
        'is_active_filter': is_active_filter,
        'total_usuarios': total_usuarios,
        'total_activos': total_activos,
    }

    return render(request, 'usuarios/lista_usuarios.html', context)


@staff_member_required
def crear_usuario_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario creado exitosamente.')
            return redirect('usuarios:lista_usuarios')
    else:
        form = RegisterForm()

    return render(request, 'usuarios/crear_usuario.html', {'form': form})


@staff_member_required
def editar_usuario_admin_view(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)

    if request.method == 'POST':
        form = AdminUserForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario actualizado.')
            return redirect('usuarios:lista_usuarios')
    else:
        form = AdminUserForm(instance=usuario)

    return render(request, 'usuarios/editar_usuario_admin.html', {
        'form': form,
        'usuario': usuario,
    })


@staff_member_required
def eliminar_usuario_view(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)

    if request.user.pk == pk:
        messages.error(request, 'No puedes eliminar tu propia cuenta.')
        return redirect('usuarios:lista_usuarios')

    if request.method == 'POST':
        # Soft delete
        usuario.is_active = False
        usuario.save()
        messages.success(request, f'Usuario {usuario.get_nombre_completo()} desactivado.')
        return redirect('usuarios:lista_usuarios')

    return render(request, 'usuarios/confirmar_eliminar_usuario.html', {'usuario': usuario})