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
]