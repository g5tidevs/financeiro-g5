from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models

from apps.core.models import ModeloBase, ModeloBaseQuerySet


class LinkQuerySet(ModeloBaseQuerySet):
    def completos(self):
        return self.filter(pago=True, no_caixa=True, nc_assinada=True, doc_enviado=True)

    def pendentes(self):
        return self.exclude(pago=True, no_caixa=True, nc_assinada=True, doc_enviado=True)


class LinkPagamento(ModeloBase):
    # As quatro etapas do checklist, na ordem em que acontecem
    ETAPAS = [
        ("pago", "Pago"),
        ("no_caixa", "No caixa"),
        ("nc_assinada", "NC assinada"),
        ("doc_enviado", "DOC enviado"),
    ]

    data = models.DateField("Data", db_index=True)
    vendedor = models.ForeignKey(
        "cadastros.Vendedor", verbose_name="Vendedor", on_delete=models.PROTECT, related_name="links"
    )
    cliente = models.CharField("Cliente", max_length=150)
    parcelas = models.PositiveSmallIntegerField(
        "Parcelamento",
        default=1,
        validators=[
            MinValueValidator(1, "O mínimo é 1 parcela."),
            MaxValueValidator(24, "O máximo é 24 parcelas."),
        ],
    )
    valor = models.DecimalField(
        "Valor",
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.01"), message="O valor precisa ser maior que zero.")],
    )
    nsu = models.CharField(
        "NSU",
        max_length=30,
        blank=True,
        db_index=True,
        validators=[RegexValidator(r"^\d+$", "O NSU deve conter apenas números.")],
    )
    pago = models.BooleanField("Pago", default=False)
    no_caixa = models.BooleanField("No caixa", default=False)
    nc_assinada = models.BooleanField("Nota de crédito assinada", default=False)
    doc_enviado = models.BooleanField("Documentação enviada", default=False)

    objects = LinkQuerySet.as_manager()

    class Meta:
        verbose_name = "Link de pagamento"
        verbose_name_plural = "Links de pagamento"
        ordering = ["-data", "-id"]

    def __str__(self):
        return f"{self.cliente} - {self.data:%d/%m/%Y}"

    @property
    def etapas_pendentes(self):
        return [rotulo for campo, rotulo in self.ETAPAS if not getattr(self, campo)]

    @property
    def completo(self):
        return not self.etapas_pendentes

    def clean(self):
        super().clean()
        if self.pago and not self.nsu:
            raise ValidationError({"nsu": "Informe o NSU ao marcar o link como pago."})