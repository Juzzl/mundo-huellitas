from django.contrib import admin
from .models import Cita

admin.site.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ("mascota", "servicio", "empleado", "fecha_hora_inicio", "fecha_hora_fin", "estado")
    list_filter = ("estado", "empleado", "servicio")
    date_hierarchy = "fecha_hora_inicio"
    list_select_related = ("mascota", "servicio", "empleado")