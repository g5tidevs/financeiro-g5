from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from apps.core.models import ModeloBase


class DevolucaoPix(ModeloBase):
    data = models.DateField("Data", db_index=True)
    loja = models.ForeignKey(
        "cadastros.Loja", verbose_name="Loja", on_delete=models.PROTECT, related_name="devolucoes_pix"
    )
    cliente = models.CharField("Cliente", max_length=150)
    valor = models.DecimalField(
        "Valor",
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"), message="O valor precisa ser maior que zero.")],
    )
    banco = models.ForeignKey(
        "cadastros.Banco", verbose_name="Banco", on_delete=models.PROTECT, related_name="devolucoes_pix"
    )
    motivo = models.ForeignKey(
        "cadastros.Motivo",
        verbose_name="Motivo",
        on_delete=models.PROTECT,
        limit_choices_to={"tipo": "PIX"},
        related_name="devolucoes_pix",
    )
    conciliado = models.BooleanField("Conciliado (EJL)", default=False)

    class Meta:
        verbose_name = "Devolução de Pix"
        verbose_name_plural = "Devoluções de Pix"
        ordering = ["-data", "-id"]

    def __str__(self):
        return f"{self.cliente} - {self.data:%d/%m/%Y}"