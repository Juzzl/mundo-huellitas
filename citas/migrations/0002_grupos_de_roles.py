from django.db import migrations

GRUPOS = ["administrador", "groomer", "cuidador", "clientes"]

def crear_grupos(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    for nombre in GRUPOS:
        Group.objects.get_or_create(name=nombre)

class Migration(migrations.Migration):
    dependencies = [
        ("citas", "0001_initial"),
        ("auth", "0001_initial"),
    ]
    operations = [
        migrations.RunPython(crear_grupos, migrations.RunPython.noop),
    ]
