from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from apps.core.models import ModeloBase


class EstornoCartao(ModeloBase):
    data = models.DateField("Data do estorno", db_index=True)
    loja = models.ForeignKey(
        "cadastros.Loja", verbose_name="Loja", on_delete=models.PROTECT, related_name="estornos"
    )
    cliente = models.CharField("Cliente", max_length=150)
    contato_cliente = models.CharField("Contato do cliente", max_length=100, help_text="Telefone ou e-mail")
    data_venda = models.DateField("Data da venda")
    valor = models.DecimalField(
        "Valor",
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"), message="O valor precisa ser maior que zero.")],
    )
    nsu = models.CharField(
        "NSU",
        max_length=30,
        db_index=True,
        validators=[RegexValidator(r"^\d+$", "O NSU deve conter apenas números.")],
    )
    motivo = models.CharField("Motivo", max_length=255)
    solicitado_banco = models.BooleanField("Solicitado no Safra", default=False)
    conciliado = models.BooleanField("Conciliado (EJL)", default=False)

class Meta:
        verbose_name = "Estorno de cartão"
        verbose_name_plural = "Estornos de cartão"
        ordering = ["-data", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["nsu"],
                condition=models.Q(ativo=True) & ~models.Q(nsu=""),
                name="estorno_nsu_unico",
                violation_error_message="Já existe um estorno ativo com este NSU.",
            ),
        ]
