from django.apps import AppConfig


class ContasConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.contas"
    label = "contas"
    verbose_name = "Contas de usuário"

    def ready(self):
        from . import signals  # noqa: F401  (liga o log de acessos)