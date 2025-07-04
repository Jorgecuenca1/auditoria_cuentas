# Generated by Django 5.2.4 on 2025-07-05 00:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facturacion', '0006_remove_contrato_tipo_contrato_fecha_conciliacion_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='contrato',
            name='tipo_auditoria',
            field=models.CharField(blank=True, choices=[('Acuerdo', 'Acuerdo'), ('Contrato', 'Contrato'), ('Ambulatorio', 'Ambulatorio'), ('Hospitalizacion', 'Hospitalización'), ('Urgencias', 'Urgencias')], help_text='Tipo de auditoría para este contrato', max_length=20, null=True),
        ),
    ]
