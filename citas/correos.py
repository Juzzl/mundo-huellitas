from django.core.mail import send_mail
from django.template.loader import render_to_string

from .forms import a_local

# Asunto y frase principal según la acción realizada
ACCIONES = {
    "creada": ("Tu cita fue agendada", "agendamos una nueva cita"),
    "editada": ("Tu cita fue modificada", "realizamos cambios en la cita"),
    "estado": ("Actualización de tu cita", "actualizamos el estado de la cita"),
    "cancelada": ("Tu cita fue cancelada", "cancelamos la cita"),
}


def notificar_cita(cita, accion):
    """Envía un correo al cliente dueño de la mascota sobre su cita."""
    cliente = cita.mascota.cliente

    # Si el cliente no tiene correo registrado, no se envía nada
    if not cliente.email:
        return False

    asunto, frase = ACCIONES[accion]
    inicio = a_local(cita.fecha_hora_inicio)
    fin = a_local(cita.fecha_hora_fin)
    empleado = cita.empleado.nombre if cita.empleado else "Por asignar"

    # Datos que usa la plantilla HTML
    contexto = {
        "asunto": asunto,
        "frase": frase,
        "cliente": cliente.nombre,
        "mascota": cita.mascota.nombre,
        "servicio": cita.servicio.nombre,
        "inicio": inicio,
        "fin": fin,
        "empleado": empleado,
        "estado": cita.get_estado_display(),
    }
    mensaje_html = render_to_string("correos/cita.html", contexto)

    # Versión en texto plano (para programas de correo que no muestran HTML)
    mensaje_texto = (
        f"Hola {cliente.nombre},\n\n"
        f"Te informamos que {frase} de {cita.mascota.nombre}.\n\n"
        f"Servicio: {cita.servicio.nombre}\n"
        f"Fecha: {inicio:%d/%m/%Y}\n"
        f"Hora: {inicio:%I:%M %p} a {fin:%I:%M %p}\n"
        f"Atiende: {empleado}\n"
        f"Estado: {cita.get_estado_display()}\n\n"
        f"Gracias por confiar en Mi Mundo de Huellitas."
    )

    enviados = send_mail(
        asunto,
        mensaje_texto,
        None,  # usa DEFAULT_FROM_EMAIL de settings.py
        [cliente.email],
        html_message=mensaje_html,
        fail_silently=True,  # si el correo falla, la cita igual se guarda
    )
    return enviados == 1