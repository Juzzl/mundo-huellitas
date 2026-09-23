from django.db import models

class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.nombre


class Mascota(models.Model):
    TAMANO_CHOICES = [
        ("PEQUENO", "Pequeño"),
        ("MEDIANO", "Mediano"),
        ("GRANDE", "Grande"),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="mascotas")
    nombre = models.CharField(max_length=100)
    especie = models.CharField(max_length=50, default="Perro")
    raza = models.CharField(max_length=100, blank=True, null=True)
    tamano = models.CharField(max_length=10, choices=TAMANO_CHOICES, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    notas = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} ({self.cliente.nombre})"