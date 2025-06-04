from django.db import migrations

def generate_unique_ruts(apps, schema_editor):
    Paciente = apps.get_model('core', 'Paciente')
    for index, paciente in enumerate(Paciente.objects.all(), start=1):
        paciente.rut = f"{10000000 + index}-{index % 9}"
        paciente.save()

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0002_paciente_rut'),
    ]

    operations = [
        migrations.RunPython(generate_unique_ruts),
    ]