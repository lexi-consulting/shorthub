from django.apps import AppConfig


class UnderstatConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "understat"

    def ready(self):
        import understat.api.services.UnderstatDatabaseService  # noqa: F401 
