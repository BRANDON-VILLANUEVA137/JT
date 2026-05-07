from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro_view, name='registro'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard-admin/', views.dashboard_admin_view, name='dashboard_admin'),
    path('perfil/', views.perfil_view, name='perfil'),
    path('editar/', views.editar_usuario_view, name='editar'),
    path('cambiar-password/', views.cambiar_password_view, name='cambiar-password'),
    path('cambiar-email/', views.cambiar_email_view, name='cambiar_email'),
    path('confirm-email/<str:token>/', views.confirm_email_view, name='confirm_email'),
    path('lista-usuarios/', views.lista_usuarios_view, name='lista_usuarios'),
    path('crear-usuario/', views.crear_usuario_view, name='crear_usuario'),
    path('editar-usuario/<int:pk>/', views.editar_usuario_admin_view, name='editar_usuario_admin'),
    path('desactivar-usuario/<int:pk>/', views.desactivar_usuario_view, name='desactivar_usuario'),
    path('eliminar-usuario/<int:pk>/', views.eliminar_usuario_view, name='eliminar_usuario'),
    path('recuperar-contrasena/', views.password_reset_request_view, name='password_reset_request'),
    path('restablecer-contrasena/<str:token>/', views.password_reset_view, name='password_reset'),
]
