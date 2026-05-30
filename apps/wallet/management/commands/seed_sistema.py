from django.core.management.base import BaseCommand
from apps.wallet.models import asegurar_cuentas_sistema

class Command(BaseCommand):
    help = 'Crea cuentas de sistema (casa, pendientes, bonos).'

    def handle(self, *args, **options):
        asegurar_cuentas_sistema()
        self.stdout.write(self.style.SUCCESS('Cuentas de sistema listas.'))
