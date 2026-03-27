from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [    
    path('login/', views.login_view, name='login'),    
    path('logout/', views.logout_view, name='logout'),    
    path('registro/', views.registro_view, name='registro'),    
    path('dashboard/', views.dashboard_view, name='dashboard'),    
    path('perfil/', views.perfil_view, name='perfil'),    
    path('editar/', views.editar_usuario_view, name='editar_usuario'),    
    path('cambiar-password/', views.cambiar_password_view, name='cambiar_password'),    
    path('cambiar-email/', views.cambiar_email_view, name='cambiar_email'),]
