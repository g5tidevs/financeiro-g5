from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from apps.core.models import ModeloBase


class DevolucaoEspecie(ModeloBase):
    data = models.DateField("Data", db_index=True)
    loja = models.ForeignKey(
        "cadastros.Loja", verbose_name="Loja", on_delete=models.PROTECT, related_name="devolucoes_especie"
    )
    cliente = models.CharField("Cliente", max_length=150)
    valor = models.DecimalField(
        "Valor",
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"), message="O valor precisa ser maior que zero.")],
    )
    motivo = models.CharField("Motivo", max_length=255)

    class Meta:
        verbose_name = "Devolução em espécie"
        verbose_name_plural = "Devoluções em espécie"
        ordering = ["-data", "-id"]

    def __str__(self):
        return f"{self.cliente} - {self.data:%d/%m/%Y}"