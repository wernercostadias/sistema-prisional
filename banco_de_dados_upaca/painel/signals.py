# painel/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from painel.models import Pessoa  # Importa o modelo Pessoa do app painel

@receiver(post_save, sender=Pessoa)
def limpar_opcoes_associadas(sender, instance, created, **kwargs):
    """Limpa as opções associadas após salvar a pessoa, caso a transferência esteja ativa."""
    if instance.tem_transferencia_ativa:
        instance.limpar_opcoes_associadas()  # Chama o método para limpar as opções


