import re
from datetime import date

from django import forms

from .models import Cliente, Mascota


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ["nombre", "telefono", "email", "direccion"]
        labels = {
            "nombre": "Nombre completo",
            "telefono": "Teléfono",
            "email": "Correo electrónico",
            "direccion": "Dirección",
        }
        widgets = {
            "telefono": forms.TextInput(attrs={"placeholder": "8888-8888"}),
        }

    def clean_nombre(self):
        return " ".join(self.cleaned_data["nombre"].split())

    def clean_telefono(self):
        telefono = self.cleaned_data["telefono"].strip()
        if not re.fullmatch(r"[0-9+\-\s]{8,20}", telefono):
            raise forms.ValidationError(
                "Ingrese un teléfono válido. Solo se permiten números, espacios, guiones y el signo +."
            )
        repetidos = Cliente.objects.filter(telefono=telefono)
        if self.instance.pk:
            repetidos = repetidos.exclude(pk=self.instance.pk)
        if repetidos.exists():
            raise forms.ValidationError("Ya existe un cliente registrado con ese teléfono.")
        return telefono


class MascotaForm(forms.ModelForm):
    class Meta:
        model = Mascota
        fields = ["nombre", "especie", "raza", "tamano", "fecha_nacimiento", "notas"]
        labels = {
            "nombre": "Nombre de la mascota",
            "especie": "Especie",
            "raza": "Raza",
            "tamano": "Tamaño",
            "fecha_nacimiento": "Fecha de nacimiento",
            "notas": "Notas",
        }
        widgets = {
            "fecha_nacimiento": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "notas": forms.Textarea(attrs={
                "rows": 3,
                "placeholder": "Alergias, temperamento, cuidados especiales",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["tamano"].choices = [("", "Seleccione un tamaño")] + list(Mascota.TAMANO_CHOICES)

    def clean_nombre(self):
        return " ".join(self.cleaned_data["nombre"].split())

    def clean_fecha_nacimiento(self):
        fecha = self.cleaned_data.get("fecha_nacimiento")
        if fecha and fecha > date.today():
            raise forms.ValidationError("La fecha de nacimiento no puede ser futura.")
        return fecha