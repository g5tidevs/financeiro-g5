from django.conf import settings
from django.db import models
from simple_history.models import HistoricalRecords


class ModeloBaseQuerySet(models.QuerySet):
    def ativos(self):
        return self.filter(ativo=True)


class ModeloBase(models.Model):
    """Campos de controle que todo registro do sistema terá."""

    criado_em = models.DateTimeField("Criado em", auto_now_add=True)
    atualizado_em = models.DateTimeField("Atualizado em", auto_now=True)
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Criado por",
        on_delete=models.PROTECT,
        related_name="+",
        null=True,
        blank=True,
        editable=False,
    )
    ativo = models.BooleanField("Ativo", default=True)

    # inherit=True: todo model que herdar deste ganha histórico automaticamente
    history = HistoricalRecords(inherit=True)

    objects = ModeloBaseQuerySet.as_manager()

    class Meta:
        abstract = True