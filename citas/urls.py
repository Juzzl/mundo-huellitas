from django.urls import path
from . import views
 
urlpatterns = [
    path('', views.citas, name='citas'),
    path('agenda/', views.lista_citas, name='citas_lista'),
    path('agenda/nueva/', views.crear_cita, name='citas_crear'),
    path('agenda/<int:pk>/editar/', views.editar_cita, name='citas_editar'),
    path('agenda/<int:pk>/estado/<str:estado>/', views.cambiar_estado, name='citas_estado'),
    path('agenda/horas-ocupadas/', views.horas_ocupadas, name='citas_horas_ocupadas'),
]