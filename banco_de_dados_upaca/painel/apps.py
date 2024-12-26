# painel/apps.py
from django.apps import AppConfig

class PainelConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'painel'

    def ready(self):
        import painel.signals  # Registra os sinais no momento da inicialização do app
