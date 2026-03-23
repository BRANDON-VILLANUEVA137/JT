from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User


# ================= LOGIN =================

def login_view(request):
    if request.user.is_authenticated:
        return redirect('usuarios:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('usuarios:dashboard')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')

    return render(request, 'usuarios/login.html')


# ================= LOGOUT =================

def logout_view(request):
    logout(request)
    return redirect('usuarios:login')


# ================= REGISTRO =================

def registro_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'El usuario ya existe')
            return redirect('usuarios:registro')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(request, 'Usuario creado correctamente')
        return redirect('usuarios:login')

    return render(request, 'usuarios/registro.html')


# ================= DASHBOARD =================

@login_required(login_url='usuarios:login')
def dashboard_view(request):
    return render(request, 'usuarios/dashboard.html')


# ================= PERFIL =================

@login_required(login_url='usuarios:login')
def perfil_view(request):
    return render(request, 'usuarios/perfil.html')