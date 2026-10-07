from django.db import models


class Servicio(models.Model):
    TIPO_CHOICES = [
        ("ESTETICA", "Estética"),
        ("GUARDERIA", "Guardería"),
    ]

    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    duracion = models.DurationField(
    "Duración estimada",
    blank=True,
    null=True,
    help_text="Escriba horas:minutos:segundos. Ejemplo: 02:30:00"
)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"


class TarifaServicio(models.Model):
    APLICA_A_CHOICES = [
        ("1-4_KG", "1 a 4 kg"),
        ("5-10_KG", "5 a 10 kg"),
        ("11-15_KG", "11 a 15 kg"),
        ("16-19_KG", "16 a 19 kg"),
        ("20-25_KG", "20 a 25 kg"),
        ("26-30_KG", "26 a 30 kg"),
        ("31-35_KG", "31 a 35 kg"),
        ("GATOS", "Gatos"),
        ("UNICO", "Precio único"),
        
    ]

    servicio = models.ForeignKey(
        Servicio,
        on_delete=models.CASCADE,
        related_name="tarifas"
    )
    aplica_a = models.CharField(max_length=100, choices=APLICA_A_CHOICES)
    precio = models.DecimalField(max_digits=8, decimal_places=2)
  

    def __str__(self):
        return f"{self.servicio.nombre} - {self.get_aplica_a_display()}: ₡{self.precio}"