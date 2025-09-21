from django.utils import timezone
from .models import PDI
from django.contrib.auth.models import User

def calcular_dias_restantes(data_fim):
    if data_fim is None:
        return None  # Ou um valor apropriado

    # Certifique-se de que data_fim tem um timezone
    if data_fim.tzinfo is None:
        data_fim = timezone.make_aware(data_fim)

    # Obter a data atual com timezone
    data_atual = timezone.now()

    # Calcular dias restantes
    dias_restantes = (data_fim - data_atual).days
    return dias_restantes


