from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from citas.models import Cita
from citas.roles import ADMIN, PERSONAL, rol_de, rol_requerido
from personal.models import Empleado
from .forms import ClienteForm, MascotaForm
from .models import Cliente, Mascota


def plural(cantidad, singular, plural_):
    return f"{cantidad} {singular if cantidad == 1 else plural_}"

@rol_requerido(*PERSONAL)
def clientes(request):
    busqueda = request.GET.get("q", "").strip()
    lista = Cliente.objects.annotate(total_mascotas=Count("mascotas")).order_by("nombre")
    if busqueda:
        lista = lista.filter(
            Q(nombre__icontains=busqueda)
            | Q(telefono__icontains=busqueda)
            | Q(email__icontains=busqueda)
            | Q(pk__in=Mascota.objects.filter(nombre__icontains=busqueda).values("cliente_id"))
        )
    pagina = Paginator(lista, 10).get_page(request.GET.get("page"))
    return render(request, "clientes/lista.html", {"pagina": pagina, "q": busqueda})

@rol_requerido(*PERSONAL)
def detalle_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    mascotas = cliente.mascotas.annotate(total_citas=Count("citas")).order_by("nombre")
    citas = (
        Cita.objects.filter(mascota__cliente=cliente)
        .select_related("mascota", "servicio", "empleado")
        .order_by("-fecha_hora_inicio")[:10]
    )
    return render(request, "clientes/detalle.html", {
        "cliente": cliente,
        "mascotas": mascotas,
        "citas": citas,
    })

@rol_requerido(ADMIN)
def crear_cliente(request):
    form = ClienteForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        cliente = form.save()
        messages.success(request, f"Cliente {cliente.nombre} registrado. Ya puede agregarle sus mascotas.")
        return redirect("clientes_detalle", pk=cliente.pk)
    return render(request, "clientes/form.html", {
        "form": form,
        "etiqueta": "Clientes",
        "titulo": "Nuevo cliente",
        "descripcion": "Registre los datos del dueño. Las mascotas se agregan después, desde su ficha.",
        "volver": reverse("clientes"),
    })

@rol_requerido(ADMIN)
def editar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    form = ClienteForm(request.POST or None, instance=cliente)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Datos del cliente actualizados.")
        return redirect("clientes_detalle", pk=cliente.pk)
    return render(request, "clientes/form.html", {
        "form": form,
        "etiqueta": "Clientes",
        "titulo": "Editar cliente",
        "descripcion": cliente.nombre,
        "volver": reverse("clientes_detalle", args=[cliente.pk]),
    })

@rol_requerido(ADMIN)
def eliminar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == "POST":
        nombre = cliente.nombre
        cliente.delete()
        messages.success(request, f"Cliente {nombre} eliminado.")
        return redirect("clientes")
    avisos = []
    mascotas = cliente.mascotas.count()
    citas = Cita.objects.filter(mascota__cliente=cliente).count()
    if mascotas:
        avisos.append(plural(mascotas, "mascota registrada", "mascotas registradas"))
    if citas:
        avisos.append(plural(citas, "cita del historial", "citas del historial"))
    return render(request, "clientes/confirmar_eliminar.html", {
        "etiqueta": "Clientes",
        "titulo": "Eliminar cliente",
        "pregunta": f"¿Seguro que desea eliminar a {cliente.nombre}? Esta acción no se puede deshacer.",
        "avisos": avisos,
        "volver": reverse("clientes_detalle", args=[cliente.pk]),
    })

@rol_requerido(ADMIN)
def crear_mascota(request, cliente_pk):
    cliente = get_object_or_404(Cliente, pk=cliente_pk)
    form = MascotaForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        mascota = form.save(commit=False)
        mascota.cliente = cliente
        mascota.save()
        messages.success(request, f"{mascota.nombre} fue registrado como mascota de {cliente.nombre}.")
        return redirect("clientes_detalle", pk=cliente.pk)
    return render(request, "clientes/form.html", {
        "form": form,
        "etiqueta": "Mascotas",
        "titulo": "Nueva mascota",
        "descripcion": f"Dueño: {cliente.nombre}",
        "volver": reverse("clientes_detalle", args=[cliente.pk]),
    })

@rol_requerido(ADMIN)
def editar_mascota(request, pk):
    mascota = get_object_or_404(Mascota.objects.select_related("cliente"), pk=pk)
    form = MascotaForm(request.POST or None, instance=mascota)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"Datos de {mascota.nombre} actualizados.")
        return redirect("clientes_detalle", pk=mascota.cliente_id)
    return render(request, "clientes/form.html", {
        "form": form,
        "etiqueta": "Mascotas",
        "titulo": "Editar mascota",
        "descripcion": f"Dueño: {mascota.cliente.nombre}",
        "volver": reverse("clientes_detalle", args=[mascota.cliente_id]),
    })

@rol_requerido(ADMIN)
def eliminar_mascota(request, pk):
    mascota = get_object_or_404(Mascota.objects.select_related("cliente"), pk=pk)
    if request.method == "POST":
        nombre = mascota.nombre
        mascota.delete()
        messages.success(request, f"{nombre} fue eliminado de las mascotas.")
        return redirect("clientes_detalle", pk=mascota.cliente_id)
    avisos = []
    citas = mascota.citas.count()
    if citas:
        avisos.append(plural(citas, "cita del historial", "citas del historial"))
    return render(request, "clientes/confirmar_eliminar.html", {
        "etiqueta": "Mascotas",
        "titulo": "Eliminar mascota",
        "pregunta": f"¿Seguro que desea eliminar a {mascota.nombre}? Esta acción no se puede deshacer.",
        "avisos": avisos,
        "volver": reverse("clientes_detalle", args=[mascota.cliente_id]),
    })

@login_required
def redireccion_por_rol(request):
    if rol_de(request.user) in PERSONAL:
        return redirect("citas_lista")
    return redirect("perfil")


@login_required
def perfil(request):
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
