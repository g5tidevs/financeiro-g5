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

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"

    @property
    def is_supervisor(self) -> bool:
        # O superusuário (administrador técnico) também enxerga tudo
        return self.is_superuser or self.papel == self.Papel.SUPERVISOR

    def __str__(self):
        return self.get_full_name() or self.username