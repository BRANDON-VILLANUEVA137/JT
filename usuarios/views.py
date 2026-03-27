from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoginForm, RegisterForm
from .models import Usuario

def login_view(request):
    if request.user.is_authenticated:
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
    if request.method == 'POST':
        form = PasswordChangeCustomForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Contraseña cambiada exitosamente.')
            logout(request)
            return redirect('usuarios:login')
    else:
        form = PasswordChangeCustomForm(request.user)

    return render(request, 'usuarios/cambiar_password.html', {
        'form': form,
    })


@login_required(login_url='usuarios:login')
def cambiar_email_view(request):
    if request.method == 'POST':
        form = EmailChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Email actualizado correctamente.')
            return redirect('usuarios:perfil')
    else:
        form = EmailChangeForm(request.user)

    return render(request, 'usuarios/cambiar_email.html', {
        'form': form,
    })