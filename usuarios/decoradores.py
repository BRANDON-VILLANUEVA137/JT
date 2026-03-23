"""
Decoradores personalizados para proteger vistas según roles y permisos.
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def requiere_admin(view_func):
    """
    Decorador que verifica si el usuario autenticado es administrador.
    Si no lo es, redirige a su dashboard correspondiente.
    
    Uso:
        @requiere_admin
        def mi_vista(request):
            ...
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('usuarios:login')
        
        if request.user.rol != 'admin':
            messages.error(request, 'No tiene permiso para acceder a esta página.')
            # Redirigir según rol
            if request.user.rol == 'buyer':
                return redirect('usuarios:dashboard_buyer')
            elif request.user.rol == 'seller':
                return redirect('usuarios:dashboard_seller')
            else:
                return redirect('usuarios:dashboard')
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def requiere_rol(*roles):
    """
    Decorador que verifica si el usuario autenticado tiene uno de los roles especificados.
    Si no los tiene, redirige a su dashboard correspondiente.
    
    Uso:
        @requiere_rol('admin', 'seller')
        def mi_vista(request):
            ...
    """
    def decorador(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('usuarios:login')
            
            if request.user.rol not in roles:
                messages.error(request, 'No tiene permiso para acceder a esta página.')
                # Redirigir según rol
                if request.user.rol == 'admin':
                    return redirect('usuarios:dashboard_admin')
                elif request.user.rol == 'seller':
                    return redirect('usuarios:dashboard_seller')
                else:
                    return redirect('usuarios:dashboard_buyer')
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    
    return decorador


def requiere_docente(view_func):
    """
    Decorador que verifica si el usuario autenticado es docente o admin.
    Si no lo es, redirige a su dashboard correspondiente.
    
    Uso:
        @requiere_docente
        def mi_vista(request):
            ...
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('usuarios:login')
        
        if request.user.rol not in ['docente', 'admin']:
            messages.error(request, 'No tiene permiso para acceder a esta página.')
            # Redirigir según el rol del usuario
            if request.user.rol == 'estudiante':
                return redirect('usuarios:dashboard_estudiante')
            else:
                return redirect('usuarios:dashboard')
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def requiere_estudiante(view_func):
    """
    Decorador que verifica si el usuario autenticado es estudiante.
    Si no lo es, redirige a su dashboard correspondiente.
    
    Uso:
        @requiere_estudiante
        def mi_vista(request):
            ...
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('usuarios:login')
        
        if request.user.rol != 'estudiante':
            messages.error(request, 'No tiene permiso para acceder a esta página.')
            # Redirigir según el rol del usuario
            if request.user.rol == 'admin':
                return redirect('usuarios:dashboard_admin')
            elif request.user.rol == 'docente':
                return redirect('usuarios:dashboard_docente')
            else:
                return redirect('usuarios:dashboard_estudiante')
        
        return view_func(request, *args, **kwargs)
    
    return wrapper
