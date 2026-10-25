from datetime import date
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .forms import CitaForm, a_local, cierre
from .models import Cita
from .roles import ADMIN, PERSONAL, rol_de, rol_requerido

def citas(request):
    return redirect("citas_lista")

@rol_requerido(*PERSONAL)
def lista_citas(request):
    citas = Cita.objects.select_related("mascota", "servicio", "empleado")
    if rol_de(request.user) != ADMIN:
        citas = citas.filter(empleado__usuario=request.user)
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

@rol_requerido(ADMIN)
def crear_cita(request):
    form = CitaForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Cita agendada correctamente.")
        return redirect("citas_lista")
    return render(request, "citas/form.html", {"form": form, "titulo": "Nueva cita"})

@rol_requerido(ADMIN)
def editar_cita(request, pk):
    cita = get_object_or_404(Cita, pk=pk)
    form = CitaForm(request.POST or None, instance=cita)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Cita actualizada correctamente.")
        return redirect("citas_lista")
    return render(request, "citas/form.html", {"form": form, "titulo": "Editar cita"})

@require_POST
@rol_requerido(*PERSONAL)
def cambiar_estado(request, pk, estado):
    if estado not in dict(Cita.ESTADO_CHOICES):
        messages.error(request, "El estado no es válido.")
        return redirect("citas_lista")
    cita = get_object_or_404(Cita, pk=pk)
    if rol_de(request.user) != ADMIN:
        es_suya = cita.empleado is not None and cita.empleado.usuario_id == request.user.id
        if not es_suya or estado not in ("EN_PROCESO", "COMPLETADA"):
            raise PermissionDenied
    cita.estado = estado
    cita.save(update_fields=["estado"])
    messages.success(request, f"Cita marcada como {cita.get_estado_display().lower()}.")
    return redirect("citas_lista")

@rol_requerido(ADMIN)
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