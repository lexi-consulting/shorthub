from django.apps import AppConfig

class UnderstatApiConfig(AppConfig):
    name = 'understat.api'

    def ready(self):
        import understat.api.services.UnderstatDatabaseService  # noqa: F401 