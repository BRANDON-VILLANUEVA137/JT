# usuarios/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.conf import settings
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from datetime import timedelta, date

from .forms import LoginForm, RegisterForm, UserUpdateForm, PasswordChangeCustomForm, EmailChangeForm
from .models import Usuario
from .tokens import EmailChangeToken
from usuarios.decoradores import requiere_admin
from pedidos.models import Pedido

from django.db.models.functions import TruncDay
from collections import OrderedDict
import json

# ──────────────────────────────────────────────
# AUTH VIEWS
# ──────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        if request.user.rol == 'admin':
            return redirect('usuarios:dashboard')
        return redirect('/')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            login_field = form.cleaned_data['login_field']
            password    = form.cleaned_data['password']

            try:
                user = Usuario.objects.get(numero_documento=login_field)
                user = authenticate(request, username=user.username, password=password)
            except Usuario.DoesNotExist:
                user = authenticate(request, username=login_field, password=password)

            if user:
                login(request, user)
                return redirect('usuarios:dashboard' if user.rol == 'admin' else '/')
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
            form.save()
            messages.success(request, 'Usuario creado. Inicia sesión.')
            return redirect('usuarios:login')
    else:
        form = RegisterForm()
    return render(request, 'usuarios/registro.html', {'form': form})


# ──────────────────────────────────────────────
# USER VIEWS
# ──────────────────────────────────────────────

@login_required(login_url='usuarios:login')
def dashboard_view(request):
    if request.user.rol == 'admin':
        return redirect('usuarios:dashboard_admin')
    return render(request, 'usuarios/dashboard.html')


@login_required(login_url='usuarios:login')
def perfil_view(request):
    return render(request, 'usuarios/perfil.html', {'usuario': request.user})


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
            form.request_user.set_password(form.cleaned_data['new_password1'])
            form.request_user.save(update_fields=['password'])
            messages.success(request, 'Contraseña cambiada exitosamente.')
            logout(request)
            return redirect('usuarios:login')
    return render(request, 'usuarios/cambiar_password.html', {'form': form})


@login_required(login_url='usuarios:login')
def cambiar_email_view(request):
    form = EmailChangeForm(request.user)
    if request.method == 'POST':
        form = EmailChangeForm(request.user, request.POST)
        if form.is_valid():
            new_email = form.cleaned_data['new_email']
            token = EmailChangeToken.generate_token(request.user, new_email)
            verification_url = request.build_absolute_uri(f'/usuarios/confirm-email/{token}/')
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
    return render(request, 'usuarios/cambiar_email.html', {'form': form})


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


# ──────────────────────────────────────────────
# HELPERS PARA EL DASHBOARD ADMIN
# ──────────────────────────────────────────────

def _parse_period(request):
    """
    Lee el período del querystring y devuelve (start_date, end_date, period_key).
    Períodos soportados: hoy | 7d | 30d | 90d | custom
    """
    hoy = timezone.localdate()
    periodo = request.GET.get('periodo', '30d')

    if periodo == 'hoy':
        start = hoy
        end   = hoy
    elif periodo == '7d':
        start = hoy - timedelta(days=6)
        end   = hoy
    elif periodo == '90d':
        start = hoy - timedelta(days=89)
        end   = hoy
    elif periodo == 'custom':
        try:
            start = date.fromisoformat(request.GET.get('fecha_inicio', ''))
            end   = date.fromisoformat(request.GET.get('fecha_fin', ''))
            if start > end:
                start, end = end, start         # swap silencioso
        except ValueError:
            # Fechas inválidas → caer a 30d
            periodo = '30d'
            start   = hoy - timedelta(days=29)
            end     = hoy
    else:  # 30d (default)
        periodo = '30d'
        start   = hoy - timedelta(days=29)
        end     = hoy

    return start, end, periodo


def _ventas_por_periodo(start_date, end_date):
    """Suma de totales de pedidos completados en el rango."""
    return (
        Pedido.objects
        .filter(
            fecha_creacion__date__gte=start_date,
            fecha_creacion__date__lte=end_date,
            estado='entregado',          # ajusta al estado que representa venta cerrada en tu proyecto
        )
        .aggregate(total=Sum('total'))['total'] or 0
    )


def _ingresos_hoy():
    hoy = timezone.localdate()
    return (
        Pedido.objects
        .filter(fecha_creacion__date=hoy, estado='entregado')
        .aggregate(total=Sum('total'))['total'] or 0
    )


def _ingresos_rango(days):
    hoy   = timezone.localdate()
    start = hoy - timedelta(days=days - 1)
    return (
        Pedido.objects
        .filter(fecha_creacion__date__gte=start, fecha_creacion__date__lte=hoy, estado='entregado')
        .aggregate(total=Sum('total'))['total'] or 0
    )


def _tasa_conversion(start_date, end_date):
    """
    Pedidos completados / total de pedidos en el período * 100.
    Si no hay pedidos devuelve 0.
    """
    total = Pedido.objects.filter(
        fecha_creacion__date__gte=start_date,
        fecha_creacion__date__lte=end_date,
    ).count()
    if not total:
        return 0
    completados = Pedido.objects.filter(
        fecha_creacion__date__gte=start_date,
        fecha_creacion__date__lte=end_date,
        estado='entregado',
    ).count()
    return round((completados / total) * 100, 1)


def _ticket_promedio(start_date, end_date):
    result = (
        Pedido.objects
        .filter(
            fecha_creacion__date__gte=start_date,
            fecha_creacion__date__lte=end_date,
            estado='entregado',
        )
        .aggregate(avg=Avg('total'))['avg']
    )
    return round(result, 2) if result else 0


def _clientes_nuevos(start_date, end_date):
    """Usuarios cuya fecha de registro cae dentro del período."""
    return Usuario.objects.filter(
        date_joined__date__gte=start_date,
        date_joined__date__lte=end_date,
    ).count()


def _clientes_recurrentes(start_date, end_date):
    """
    Clientes que hicieron más de 1 pedido en el período.
    """
    return (
        Pedido.objects
        .filter(
            fecha_creacion__date__gte=start_date,
            fecha_creacion__date__lte=end_date,
        )
        .values('user')
        .annotate(num_pedidos=Count('id'))
        .filter(num_pedidos__gt=1)
        .count()
    )


# ──────────────────────────────────────────────
# DASHBOARD ADMIN
# ──────────────────────────────────────────────

@requiere_admin
def dashboard_admin_view(request):
    start_date, end_date, period = _parse_period(request)

    # ── Pedidos del período ──────────────────
    pedidos_periodo_qs = Pedido.objects.filter(
        fecha_creacion__date__gte=start_date,
        fecha_creacion__date__lte=end_date,
    )
    total_pedidos_periodo = pedidos_periodo_qs.count()

    # ── Ingresos ────────────────────────────
    ventas_periodo    = _ventas_por_periodo(start_date, end_date)
    ingresos_hoy      = _ingresos_hoy()
    ingresos_semanal  = _ingresos_rango(7)
    ingresos_mensual  = _ingresos_rango(30)

    # ── KPIs ────────────────────────────────
    tasa_conversion   = _tasa_conversion(start_date, end_date)
    ticket_promedio   = _ticket_promedio(start_date, end_date)

    # ── Clientes ────────────────────────────
    clientes_nuevos      = _clientes_nuevos(start_date, end_date)
    clientes_recurrentes = _clientes_recurrentes(start_date, end_date)

    # ── Pedidos pendientes (globales) ───────
    pedidos_pendientes = Pedido.objects.filter(estado='preparacion').count()

    # ── Totales generales ───────────────────
    total_usuarios = Usuario.objects.count()
    total_pedidos  = Pedido.objects.count()
    ventas_totales = Pedido.objects.filter(estado='entregado').aggregate(
        total=Sum('total')
    )['total'] or 0

    # ── Tabla reciente ───────────────────────
    pedidos_recientes = (
        Pedido.objects
        .select_related('user')
        .order_by('-fecha_creacion')[:10]
    )


    ventas_7d = (
        Pedido.objects
        .filter(
            fecha_creacion__date__gte=end_date - timedelta(days=6),
            fecha_creacion__date__lte=end_date,
            estado='entregado'
        )
        .annotate(dia=TruncDay('fecha_creacion'))
        .values('dia')
        .annotate(total=Sum('total'))
        .order_by('dia')
    )

    dias = OrderedDict()
    for i in range(7):
        d = end_date - timedelta(days=6 - i)
        dias[d] = 0

    for item in ventas_7d:
        if item['dia']:
            dias[item['dia'].date()] = float(item['total'] or 0)

    chart_ingresos_labels = [d.strftime('%d %b') for d in dias.keys()]
    chart_ingresos_values = list(dias.values())

    estados = (
        pedidos_periodo_qs
        .values('estado')
        .annotate(total=Count('id'))
    )

    chart_estados_labels = [item['estado'] for item in estados]
    chart_estados_values = [item['total'] for item in estados]


    context = {
        # Período activo
        'start_date': start_date,
        'end_date':   end_date,
        'period':     period,

        # Ingresos
        'ventas_periodo':   ventas_periodo,
        'ingresos_hoy':     ingresos_hoy,
        'ingresos_semanal': ingresos_semanal,
        'ingresos_mensual': ingresos_mensual,

        # Pedidos
        'total_pedidos_periodo': total_pedidos_periodo,
        'pedidos_pendientes':    pedidos_pendientes,

        # KPIs
        'tasa_conversion': tasa_conversion,
        'ticket_promedio': ticket_promedio,

        # Clientes
        'clientes_nuevos':      clientes_nuevos,
        'clientes_recurrentes': clientes_recurrentes,

        # Totales históricos (útiles para otros bloques del template)
        'total_usuarios': total_usuarios,
        'total_pedidos':  total_pedidos,
        'ventas_totales': ventas_totales,

        # Tabla
        'pedidos_recientes': pedidos_recientes,

        # Usuario actual
        'user': request.user,

        # Datos para gráficos
        'chart_ingresos_labels': json.dumps(chart_ingresos_labels),
        'chart_ingresos_values': json.dumps(chart_ingresos_values),
        'chart_estados_labels': json.dumps(chart_estados_labels),
        'chart_estados_values': json.dumps(chart_estados_values),
    }
    return render(request, 'usuarios/dashboard_admin.html', context)


# ──────────────────────────────────────────────
# CRUD USUARIOS (ADMIN)
# ──────────────────────────────────────────────

from django.core.paginator import Paginator
from .forms import AdminUserForm


@requiere_admin
def lista_usuarios_view(request):
    query           = request.GET.get('q', '')
    rol_filter      = request.GET.get('rol', '')
    is_active_filter = request.GET.get('is_active', '')

    usuarios = Usuario.objects.all()

    if query:
        usuarios = usuarios.filter(
            Q(primer_nombre__icontains=query) |
            Q(username__icontains=query)       |
            Q(numero_documento__icontains=query)|
            Q(email__icontains=query)
        )
    if rol_filter:
        usuarios = usuarios.filter(rol=rol_filter)
    if is_active_filter:
        usuarios = usuarios.filter(is_active=(is_active_filter == 'true'))

    total_usuarios = usuarios.count()
    total_activos  = usuarios.filter(is_active=True).count()

    paginator  = Paginator(usuarios, 20)
    page_obj   = paginator.get_page(request.GET.get('page'))

    return render(request, 'usuarios/lista_usuarios.html', {
        'page_obj':        page_obj,
        'query':           query,
        'rol_filter':      rol_filter,
        'is_active_filter': is_active_filter,
        'total_usuarios':  total_usuarios,
        'total_activos':   total_activos,
    })


@requiere_admin
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


@requiere_admin
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


@requiere_admin
def desactivar_usuario_view(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.user.pk == pk:
        messages.error(request, 'No puedes desactivar tu propia cuenta.')
        return redirect('usuarios:lista_usuarios')
    if request.method == 'POST':
        usuario.is_active = False
        usuario.save()
        messages.success(request, f'Usuario {usuario.get_nombre_completo()} desactivado.')
        return redirect('usuarios:lista_usuarios')
    return render(request, 'usuarios/confirmar_desactivar_usuario.html', {'usuario': usuario})


@requiere_admin
def eliminar_usuario_view(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.user.pk == pk:
        messages.error(request, 'No puedes eliminar tu propia cuenta.')
        return redirect('usuarios:lista_usuarios')
    if request.method == 'POST':
        nombre = usuario.get_nombre_completo()
        usuario.delete()
        messages.success(request, f'Usuario {nombre} eliminado permanentemente.')
        return redirect('usuarios:lista_usuarios')
    return render(request, 'usuarios/confirmar_eliminar_usuario.html', {'usuario': usuario})