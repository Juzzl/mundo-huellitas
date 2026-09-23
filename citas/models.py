from django.db import models
from clientes.models import Mascota
from servicios.models import Servicio
from personal.models import Empleado


class Cita(models.Model):
    ESTADO_CHOICES = [
        ("PENDIENTE", "Pendiente"),
        ("CONFIRMADA", "Confirmada"),
        ("EN_PROCESO", "En proceso"),
        ("COMPLETADA", "Completada"),
        ("CANCELADA", "Cancelada"),
    ]

    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE, related_name="citas")
    servicio = models.ForeignKey(Servicio, on_delete=models.PROTECT, related_name="citas")
    empleado = models.ForeignKey(Empleado, on_delete=models.SET_NULL, null=True, blank=True, related_name="citas")
    fecha_hora_inicio = models.DateTimeField()
    fecha_hora_fin = models.DateTimeField()
    estado = models.CharField(max_length=12, choices=ESTADO_CHOICES, default="PENDIENTE")
    notas = models.TextField(blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.mascota.nombre} - {self.servicio.nombre} ({self.fecha_hora_inicio:%d/%m/%Y %H:%M})"