from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.contas.models import RegistroAcesso


class Command(BaseCommand):
    help = "Apaga registros de acesso mais antigos que N dias (padrão: 180)."

    def add_arguments(self, parser):
        parser.add_argument("--dias", type=int, default=180)

    def handle(self, *args, **opcoes):
        limite = timezone.now() - timedelta(days=opcoes["dias"])
        apagados, _ = RegistroAcesso.objects.filter(data_hora__lt=limite).delete()
        self.stdout.write(self.style.SUCCESS(f"{apagados} registro(s) de acesso apagado(s)."))