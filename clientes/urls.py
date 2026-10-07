from django.urls import path
from . import views
 
urlpatterns = [
    path('clientes/clientes.html', views.clientes, name='clientes'),]