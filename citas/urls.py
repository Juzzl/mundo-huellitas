from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('agenda/', views.lista_citas, name='citas_lista'),
    path('agenda/nueva/', views.crear_cita, name='citas_crear'),
    path('agenda/<init:pk>/editar/', views.editar_cita, name='citas_editar'),
    path('agenda/<init:pk>/estado/<str:estado>/', views.cambiar_estado, name='citas_estado'),
    path('agenda/horas-ocupadas/', views.hora_ocupadas, name='citas_horas_ocupadas'),
]