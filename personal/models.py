from django.conf import settings
from django.db import models

class Empleado(models.Model):
    ROL_CHOICES = [
        ("GROOMER", "Groomer"),
        ("CUIDADOR_GUARDERIA", "Cuidador de guardería"),
        ("ADMIN", "Administrador"),
    ]
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="empleado",
        help_text="Cuenta con la que este empleado inicia sesión.",
    )
    nombre = models.CharField(max_length=100)
    rol = models.CharField(max_length=20, choices=ROL_CHOICES)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} ({self.get_rol_display()})"
