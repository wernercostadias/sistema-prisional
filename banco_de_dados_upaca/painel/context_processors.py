from django.utils import timezone
from .models import PDI, Notification
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


def enviar_notificacao_geral(titulo, mensagem):
    # Verificar se a notificação já foi criada
    if not Notification.objects.filter(titulo=titulo, mensagem=mensagem).exists():
        usuarios = User.objects.all()  # Recupera todos os usuários
        for usuario in usuarios:
            Notification.objects.create(
                usuario=usuario,
                titulo=titulo,
                mensagem=mensagem,
                tipo='warning'
            )

def notificacoes_context(request):
    if request.user.is_authenticated:
        notificacoes = Notification.objects.filter(usuario=request.user, lida=False).order_by('-data_criacao')
        notificacoes_count = notificacoes.count()

        # Verificar os PDIs do usuário e enviar notificações se necessário
        pd_is = PDI.objects.filter(data_fim__isnull=False)  # Filtra apenas PDIs com data_fim definida
        for pdi in pd_is:
            dias_restantes = calcular_dias_restantes(pdi.data_fim)
            if dias_restantes == 1:
                if not Notification.objects.filter(
                    titulo="PDI prestes a expirar",
                    mensagem__icontains=f"(Nº PDI {pdi.id})"
                ).exists():
                    enviar_notificacao_geral(
                        titulo="PDI prestes a expirar",
                        mensagem=f"O PDI com id:{pdi.id} de {pdi.pessoa.nome_completo} (Nº PDI {pdi.numero_pdi} ) está prestes a expirar (falta 1 dia)."
                    )
    else:
        notificacoes = []
        notificacoes_count = 0

    return {
        'notificacoes_nao_lidas': notificacoes,
        'notificacoes_count': notificacoes_count,
    }