from django.db import models

class Servicio(models.Model):
    TIPO_CHOICES = [
        ("ESTETICA", "Estética"),
        ("GUARDERIA", "Guardería"),
    ]

    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    duracion_minutos = models.PositiveIntegerField(blank=True, null=True)
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"
