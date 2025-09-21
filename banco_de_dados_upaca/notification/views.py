from django.shortcuts import render

# Create your views here.
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from notification.models import Notificacao
from notification.models import NotificacaoUsuario
@login_required
@require_POST
def marcar_notificacao_como_lida(request, notif_id):
    try:
        rel = NotificacaoUsuario.objects.get(notificacao_id=notif_id, usuario=request.user)
        rel.marcar_como_lida()
        return JsonResponse({'status': 'ok'})
    except NotificacaoUsuario.DoesNotExist:
        return JsonResponse({'status': 'erro', 'mensagem': 'Notificação não encontrada'}, status=404)


from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Notificacao
from django.contrib.auth.decorators import login_required

@login_required
def carregar_notificacoes(request):
    tipo = request.GET.get('tipo')
    pagina = int(request.GET.get('pagina', 1))
    por_pagina = 5

    notificacoes_qs = Notificacao.objects.filter(usuarios=request.user, tipo=tipo).order_by('-data_criacao')
    paginator = Paginator(notificacoes_qs, por_pagina)
    
    try:
        notificacoes_page = paginator.page(pagina)
    except:
        return JsonResponse({'notificacoes': [], 'fim': True})

    dados = []
    for n in notificacoes_page:
        # pegar o relacionamento NotificacaoUsuario para o usuário
        try:
            rel = n.notificacaousuario_set.get(usuario=request.user)
            lida = rel.lida
        except NotificacaoUsuario.DoesNotExist:
            lida = False  # ou True, dependendo da lógica que desejar

        dados.append({
            'id': n.id,
            'titulo': n.titulo,
            'mensagem': n.mensagem,
            'lida': lida,
            'data_criacao': n.data_criacao.strftime("%d/%m/%Y %H:%M"),
            'grau': n.grau,
        })

    return JsonResponse({'notificacoes': dados, 'fim': not notificacoes_page.has_next()})
