from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path("", views.clientes, name="clientes"),
    path("nuevo/", views.crear_cliente, name="clientes_crear"),
    path("<int:pk>/", views.detalle_cliente, name="clientes_detalle"),
    path("<int:pk>/editar/", views.editar_cliente, name="clientes_editar"),
    path("<int:pk>/eliminar/", views.eliminar_cliente, name="clientes_eliminar"),
    path("<int:cliente_pk>/mascotas/nueva/", views.crear_mascota, name="mascotas_crear"),
    path("mascotas/<int:pk>/editar/", views.editar_mascota, name="mascotas_editar"),
    path("mascotas/<int:pk>/eliminar/", views.eliminar_mascota, name="mascotas_eliminar"),
    path("login/", auth_views.LoginView.as_view(
        template_name="clientes/login.html",
        redirect_authenticated_user=True,
    ), name="login"),
    path("salir/", auth_views.LogoutView.as_view(), name="logout"),
    path("perfil/", views.perfil, name="perfil"),
    path("entrar/", views.redireccion_por_rol, name="redireccion_rol"),
]
