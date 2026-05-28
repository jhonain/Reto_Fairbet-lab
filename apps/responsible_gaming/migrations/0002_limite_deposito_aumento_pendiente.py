from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("responsible_gaming", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="limitedeposito",
            name="monto_pendiente",
            field=models.DecimalField(
                blank=True,
                decimal_places=4,
                max_digits=18,
                null=True,
                verbose_name="Monto pendiente",
            ),
        ),
        migrations.AddField(
            model_name="limitedeposito",
            name="pendiente_desde",
            field=models.DateTimeField(
                blank=True,
                null=True,
                verbose_name="Pendiente desde",
            ),
        ),
        migrations.AddField(
            model_name="limitedeposito",
            name="pendiente_aplicable_desde",
            field=models.DateTimeField(
                blank=True,
                null=True,
                verbose_name="Pendiente aplicable desde",
            ),
        ),
    ]
