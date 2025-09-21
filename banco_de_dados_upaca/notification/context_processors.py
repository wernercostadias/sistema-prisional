from .models import Notificacao, NotificacaoUsuario

def notificacoes_context(request):
    if request.user.is_authenticated:
        relacoes = NotificacaoUsuario.objects.select_related('notificacao').filter(
            usuario=request.user
        ).order_by('-notificacao__data_criacao')

        notificacoes_por_tipo = {tipo: [] for tipo, _ in Notificacao.TIPOS}
        qtd_nao_lidas_por_tipo = {tipo: 0 for tipo, _ in Notificacao.TIPOS}

        for rel in relacoes:
            tipo = rel.notificacao.tipo

            # Popula as primeiras 5 para exibição
            if len(notificacoes_por_tipo[tipo]) < 5:
                notificacoes_por_tipo[tipo].append({
                    'id': rel.notificacao.id,
                    'titulo': rel.notificacao.titulo,
                    'mensagem': rel.notificacao.mensagem,
                    'data_criacao': rel.notificacao.data_criacao,
                    'grau': rel.notificacao.grau,
                    'lida': rel.lida,
                })

            # Conta as não lidas por tipo
            if not rel.lida:
                qtd_nao_lidas_por_tipo[tipo] += 1

        qtd_nao_lidas = sum(qtd_nao_lidas_por_tipo.values())

        return {
            'notificacoes_por_tipo': notificacoes_por_tipo,
            'qtd_nao_lidas': qtd_nao_lidas,
            'qtd_nao_lidas_por_tipo': qtd_nao_lidas_por_tipo,
        }

    return {}
