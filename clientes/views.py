from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import redirect, render
from citas.models import Cita
from citas.roles import PERSONAL, rol_de, rol_requerido
from personal.models import Empleado
from .models import Cliente

@rol_requerido(*PERSONAL)
def clientes(request):
    """Lista de clientes con sus mascotas. Solo para el personal (el cliente recibe 403)."""
    q = request.GET.get("q", "").strip()
    lista = Cliente.objects.annotate(total_mascotas=Count("mascotas")).prefetch_related("mascotas")
    if q:
        lista = lista.filter(Q(nombre__icontains=q) | Q(telefono__icontains=q))
    return render(request, "clientes/clientes.html", {
        "clientes": lista.order_by("nombre"),
        "q": q,
    })


@login_required
def redireccion_por_rol(request):
    """Después de iniciar sesión: el personal va a la agenda y el cliente a su perfil."""
    if rol_de(request.user) in PERSONAL:
        return redirect("citas_lista")
    return redirect("perfil")


@login_required
def perfil(request):
    """Perfil de quien inició sesión. Un cliente ve sus datos, sus mascotas y sus citas."""
    cliente = Cliente.objects.filter(usuario=request.user).first()
    empleado = Empleado.objects.filter(usuario=request.user).first()
    mascotas, citas = [], []
    if cliente:
        mascotas = cliente.mascotas.order_by("nombre")
        citas = (
            Cita.objects.filter(mascota__cliente=cliente)
            .select_related("mascota", "servicio", "empleado")
            .order_by("-fecha_hora_inicio")[:20]
        )
    nombre = (
        (cliente.nombre if cliente else "")
        or (empleado.nombre if empleado else "")
        or request.user.first_name
        or request.user.username
    )
    return render(request, "clientes/perfil.html", {
        "nombre": nombre,
        "cliente": cliente,
        "empleado": empleado,
        "mascotas": mascotas,
        "citas": citas,
    })
