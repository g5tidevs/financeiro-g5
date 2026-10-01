from simple_history.admin import SimpleHistoryAdmin


class ModeloBaseAdmin(SimpleHistoryAdmin):
    """Admin padrão para models que herdam de ModeloBase."""

    readonly_fields = ("criado_por", "criado_em", "atualizado_em")

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.criado_por = request.user
        super().save_model(request, obj, form, change)