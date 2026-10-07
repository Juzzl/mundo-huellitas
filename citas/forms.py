from datetime import date, datetime, time, timedelta
from django import forms
from django.conf import settings
from django.utils import timezone
from .models import Cita

# horario de atencion
apertura = time(8, 0)
cierre = time(17, 30)
intervalo = 30                              
duracion_estandart = timedelta(hours=3)    
duracion_maxima = 360                       

temporada_alta = [((12, 15), (1, 15)), ((7, 1), (7, 31))]


def es_temporada_alta(fecha):
    md = (fecha.month, fecha.day)
    for ini, fin in temporada_alta:
        if ini <= fin:
            if ini <= md <= fin:
                return True
        elif md >= ini or md <= fin: 
            return True
    return False


def generar_horarios():
    horas = []
    m = apertura.hour * 60 + apertura.minute   
    fin = cierre.hour * 60 + cierre.minute     
    while m < fin:
        horas.append(time(m // 60, m % 60))
        m += intervalo
    return horas

horarios = generar_horarios()


def etiqueta_duracion(minutos):
    h, m = divmod(minutos, 60)
    if h and m:
        return f"{h} h {m} min"
    return f"{h} h" if h else f"{m} min"


def duracion_servicio(servicio):
    for attr in ("duracion_minutos", "duracion_min", "duracion", "tiempo_estimado"):
        v = getattr(servicio, attr, None)
        if isinstance(v, timedelta):
            return v
        if isinstance(v, (int, float)) and v > 0:
            return timedelta(minutes=v)
    return duracion_estandart


def a_datetime(fecha, hora):
    dt = datetime.combine(fecha, hora)
    return timezone.make_aware(dt) if settings.USE_TZ else dt


def a_local(dt):
    return timezone.localtime(dt) if timezone.is_aware(dt) else dt


def a_time(valor):
    return datetime.strptime(valor, "%H:%M").time()


class CitaForm(forms.ModelForm):
    fecha = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    hora = forms.TypedChoiceField(
        label="Hora de inicio",
        choices=[("", "Seleccione una hora")]
        + [(h.strftime("%H:%M"), h.strftime("%H:%M")) for h in horarios],
        coerce=a_time,
        empty_value=None,
    )
    duracion = forms.TypedChoiceField(
        label="Duración estimada",
        required=False,
        choices=[("", "Según el servicio")]
        + [(str(m), etiqueta_duracion(m)) for m in range(30, duracion_maxima + 1, 30)],
        coerce=int,
        empty_value=None,
        help_text="Depende de la raza, el tamaño y el comportamiento (ej. un husky puede tardar 4 h).",
    )

    field_order = ["mascota", "servicio", "empleado", "fecha", "hora", "duracion", "notas"]

    class Meta:
        model = Cita
        fields = ["mascota", "servicio", "empleado", "notas"]
        widgets = {"notas": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["empleado"].required = False
        if self.instance.pk:
            inicio = a_local(self.instance.fecha_hora_inicio)
            fin = a_local(self.instance.fecha_hora_fin)
            minutos = int((fin - inicio).total_seconds() // 60)
            if str(minutos) not in dict(self.fields["duracion"].choices):
                self.fields["duracion"].choices = list(self.fields["duracion"].choices) + [
                    (str(minutos), etiqueta_duracion(minutos))
                ]
            self.initial["fecha"] = inicio.date()
            self.initial["hora"] = inicio.strftime("%H:%M")
            self.initial["duracion"] = str(minutos)
        else:
            self.initial["duracion"] = "180"

    def clean_fecha(self):
        fecha = self.cleaned_data["fecha"]
        es_la_misma = self.instance.pk and a_local(self.instance.fecha_hora_inicio).date() == fecha
        if fecha < date.today() and not es_la_misma:
            raise forms.ValidationError("No se pueden agendar citas en fechas pasadas.")
        if fecha.weekday() == 6 and not es_temporada_alta(fecha):
            raise forms.ValidationError("Los domingos solo se atiende en temporada alta, bajo cita.")
        return fecha 

    def clean(self):
        datos = super().clean()
        fecha, hora = datos.get("fecha"), datos.get("hora")
        servicio = datos.get("servicio")
        if not (fecha and hora and servicio):
            return datos
        minutos = datos.get("duracion")
        duracion = timedelta(minutes=minutos) if minutos else duracion_servicio(servicio)
        inicio = a_datetime(fecha, hora)
        fin = inicio + duracion
        if fin > a_datetime(fecha, cierre):
            self.add_error(
                "hora",
                f"Con {etiqueta_duracion(int(duracion.total_seconds() // 60))} de duración, "
                f"la cita terminaría después del cierre ({cierre:%H:%M}).",
            )
            return datos        
        choques = Cita.objects.exclude(estado="CANCELADA").filter(
            fecha_hora_inicio__lt=fin, fecha_hora_fin__gt=inicio
        )
        if self.instance.pk:
            choques = choques.exclude(pk=self.instance.pk)
        empleado = datos.get("empleado")
        if empleado and choques.filter(empleado=empleado).exists():
            self.add_error("hora", "Ese empleado ya tiene una cita que se cruza con ese horario.")
        mascota = datos.get("mascota")
        if mascota and choques.filter(mascota=mascota).exists():
            self.add_error("hora", "Esa mascota ya tiene una cita que se cruza con ese horario.")
        self._inicio, self._fin = inicio, fin
        return datos

    def save(self, commit=True):
        cita = super().save(commit=False)
        cita.fecha_hora_inicio = self._inicio
        cita.fecha_hora_fin = self._fin  
        if commit:
            cita.save()
        return cita                      