import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ("clientes", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.AddField(
            model_name="cliente",
            name="usuario",
            field=models.OneToOneField(
                blank=True,
                help_text="Cuenta con la que este cliente inicia sesión.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="cliente",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
