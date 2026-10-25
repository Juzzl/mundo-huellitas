from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('', views.clientes, name='clientes'),
    path('login/', auth_views.LoginView.as_view(
        template_name='clientes/login.html',
        redirect_authenticated_user=True,
    ), name='login'),
    path('salir/', auth_views.LogoutView.as_view(), name='logout'),
    path('perfil/', views.perfil, name='perfil'),
    path('entrar/', views.redireccion_por_rol, name='redireccion_rol'),
]
