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
]
