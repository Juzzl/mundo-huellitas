from django.urls import path
from . import views
 
urlpatterns = [
    path('personal/personal.html', views.personal, name='personal'),]