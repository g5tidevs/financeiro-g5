from django.db import models

from apps.core.models import ModeloBase


class Loja(ModeloBase):
    nome = models.CharField("Nome", max_length=100, unique=True)
    codigo = models.CharField("Código", max_length=20, blank=True)

    class Meta:
        verbose_name = "Loja"
        verbose_name_plural = "Lojas"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Vendedor(ModeloBase):
    nome = models.CharField("Nome", max_length=150)
    loja = models.ForeignKey(Loja, verbose_name="Loja", on_delete=models.PROTECT, related_name="vendedores")

    class Meta:
        verbose_name = "Vendedor"
        verbose_name_plural = "Vendedores"
        ordering = ["nome"]
        constraints = [
            models.UniqueConstraint(
                fields=["nome", "loja"],
                name="vendedor_unico_por_loja",
                violation_error_message="Já existe um vendedor com esse nome nesta loja.",
            ),
        ]

    def __str__(self):
        return f"{self.nome} ({self.loja})"


class Banco(ModeloBase):
    nome = models.CharField("Nome", max_length=100, unique=True)
    codigo = models.CharField("Código COMPE", max_length=3, blank=True, help_text="Ex.: 001, 237, 341")

    class Meta:
        verbose_name = "Banco"
        verbose_name_plural = "Bancos"
        ordering = ["nome"]

    def __str__(self):
        return f"{self.codigo} - {self.nome}" if self.codigo else self.nome

