from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    class Papel(models.TextChoices):
        COMUM = "COMUM", "Usuário comum"
        SUPERVISOR = "SUPERVISOR", "Supervisor"

    papel = models.CharField(
        "Papel",
        max_length=20,
        choices=Papel.choices,
        default=Papel.COMUM,
    )
    loja = models.ForeignKey(
        "cadastros.Loja",
        verbose_name="Loja",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="usuarios",
    )
    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"

    @property
    def is_supervisor(self) -> bool:
        # O superusuário (administrador técnico) também enxerga tudo
        return self.is_superuser or self.papel == self.Papel.SUPERVISOR

    def __str__(self):
        return self.get_full_name() or self.username


class RegistroAcesso(models.Model):
    """Log de acessos: cada entrada, saída e tentativa de login que falhou."""

    class Tipo(models.TextChoices):
        ENTRADA = "ENTRADA", "Entrou"
        FALHA = "FALHA", "Falha no login"
        SAIDA = "SAIDA", "Saiu"

    data_hora = models.DateTimeField("Data e hora", auto_now_add=True, db_index=True)
    tipo = models.CharField("Evento", max_length=10, choices=Tipo.choices, db_index=True)
    usuario = models.ForeignKey(
        "contas.Usuario", verbose_name="Usuário", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="acessos",
    )
    username = models.CharField("Usuário digitado", max_length=150, blank=True)
    detalhe = models.CharField("Detalhe", max_length=100, blank=True)
    ip = models.GenericIPAddressField("IP", null=True, blank=True)
    user_agent = models.CharField("Navegador (bruto)", max_length=300, blank=True)

    class Meta:
        verbose_name = "Registro de acesso"
        verbose_name_plural = "Registros de acesso"
        ordering = ["-data_hora"]

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.username} - {self.data_hora:%d/%m/%Y %H:%M}"

    @property
    def navegador(self):
        """Resumo legível do user agent, como "Chrome no Windows"."""
        ua = self.user_agent
        if not ua:
            return "—"
        if "Edg/" in ua:
            nav = "Edge"
        elif "OPR/" in ua or "Opera" in ua:
            nav = "Opera"
        elif "Chrome/" in ua:
            nav = "Chrome"
        elif "Firefox/" in ua:
            nav = "Firefox"
        elif "Safari/" in ua:
            nav = "Safari"
        else:
            nav = "Outro navegador"

        if "Android" in ua:
            so = "Android"
        elif "iPhone" in ua or "iPad" in ua:
            so = "iPhone/iPad"
        elif "Windows" in ua:
            so = "Windows"
        elif "Mac OS" in ua:
            so = "Mac"
        elif "Linux" in ua:
            so = "Linux"
        else:
            so = "sistema desconhecido"
        return f"{nav} no {so}"        