from django.apps import AppConfig


class PixConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.pix"
    label = "pix"
    verbose_name = "Devolução de Pix"