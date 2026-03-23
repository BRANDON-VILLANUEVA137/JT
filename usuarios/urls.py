from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    # Autenticación
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('password-reset/', views.password_reset_request, name='password_reset'),
    path('password-reset/<str:token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('cambiar-password/', views.cambiar_password, name='cambiar_password'),
    
    # Registro
    path('registro/', views.RegistroUsuarioView.as_view(), name='registro'),
    
    # Dashboard
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/admin/', views.dashboard_admin, name='dashboard_admin'),
    path('dashboard/docente/', views.dashboard_docente, name='dashboard_docente'),
    path('dashboard/estudiante/', views.dashboard_estudiante, name='dashboard_estudiante'),
    
    # Perfil
    path('perfil/', views.perfil_usuario, name='perfil'),
    path('perfil/<int:pk>/', views.perfil_usuario_admin, name='perfil_admin'),
    
    # Administración de usuarios
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('usuarios/<int:pk>/editar/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/<int:pk>/eliminar/', views.eliminar_usuario, name='eliminar_usuario'),
    path('usuarios/<int:pk>/bloquear/', views.bloquear_usuario, name='bloquear_usuario'),
    path('usuarios/<int:pk>/desbloquear/', views.desbloquear_usuario, name='desbloquear_usuario'),
]
