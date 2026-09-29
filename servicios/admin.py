from django.contrib import admin
from .models import Servicio, TarifaServicio


class TarifaServicioInline(admin.StackedInline):
    model = TarifaServicio
    extra = 1


@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ("nombre", "tipo", "duracion")
    inlines = [TarifaServicioInline]