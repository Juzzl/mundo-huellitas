from django.shortcuts import render
from django.db.models import Prefetch

from .models import Servicio, TarifaServicio


def lista_servicios(request):
    tarifas = TarifaServicio.objects.order_by("id")
    servicios = Servicio.objects.prefetch_related(
        Prefetch("tarifas", queryset=tarifas)
    ).order_by("nombre")

    return render(
        request,
        "servicios/lista.html",
        {"servicios": servicios}
    )