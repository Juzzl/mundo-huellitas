from datetime import date
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from citas.forms import CitaForm, a_local, cierre
from citas.models import Cita

def citas(request):
    return redirect("citas_lista")

def lista_citas(request):
    citas = Cita.objects.select_related("mascota", "servicio", "empleado")
    estado = request.GET.get("estado", "")
    fecha = request.GET.get("fecha", "")
    if estado:
        citas = citas.filter(estado=estado)
    if fecha:
        citas = citas.filter(fecha_hora_inicio__date=fecha)
    else:
        citas = citas.filter(fecha_hora_inicio__date__gte=date.today())
    return render(request, "citas/lista.html", {
        "citas": citas.order_by("fecha_hora_inicio"),
        "estados": Cita.ESTADO_CHOICES,
        "estado_sel": estado,
        "fecha_sel": fecha,
    })


def crear_cita(request):
    form = CitaForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Cita agendada correctamente.")
        return redirect("citas_lista")
    return render(request, "citas/form.html", {"form": form, "titulo": "Nueva cita"})

def editar_cita(request, pk):
    cita = get_object_or_404(Cita, pk=pk)
    form = CitaForm(request.POST or None, instance=cita)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Cita actualizada correctamente.")
        return redirect("citas_lista")
    return render(request, "citas/form.html", {"form": form, "titulo": "Editar cita"})

@require_POST
def cambiar_estado(request, pk, estado):
    if estado not in dict(Cita.ESTADO_CHOICES):
        messages.error(request, "El estado no es válido.")
        return redirect("citas_lista")
    cita = get_object_or_404(Cita, pk=pk)
    cita.estado = estado
    cita.save(update_fields=["estado"])
    messages.success(request, f"Cita marcada como {cita.get_estado_display().lower()}.")
    return redirect("citas_lista")


def horas_ocupadas(request):
    minutos_cierre = cierre.hour * 60 + cierre.minute
    fecha_texto = request.GET.get("fecha", "")
    empleado = request.GET.get("empleado", "")
    excluir = request.GET.get("excluir", "")
    try:
        fecha = date.fromisoformat(fecha_texto)
    except ValueError:
        return JsonResponse({"intervalos": [], "cierre": minutos_cierre})
    if not empleado.isdigit():
        return JsonResponse({"intervalos": [], "cierre": minutos_cierre})

    qs = Cita.objects.exclude(estado="CANCELADA").filter(
        empleado_id=empleado, fecha_hora_inicio__date=fecha
    )
    if excluir.isdigit():
        qs = qs.exclude(pk=excluir)

    intervalos = []
    for c in qs:
        ini, fin = a_local(c.fecha_hora_inicio), a_local(c.fecha_hora_fin)
        intervalos.append({"inicio": ini.hour * 60 + ini.minute, "fin": fin.hour * 60 + fin.minute})
    return JsonResponse({"intervalos": intervalos, "cierre": minutos_cierre})