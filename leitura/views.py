from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.utils import timezone
from .models import FrenteDeLeitura, FilaDeEspera, HistoricoLeitura
from painel.models import Pessoa
from django.contrib import messages
from datetime import datetime
from leitura.models import CicloLeitura
from leitura.models import Livro
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.utils import timezone
from .models import FrenteDeLeitura, FilaDeEspera, HistoricoLeitura
from painel.models import Pessoa
from django.contrib import messages
from leitura.models import CicloLeitura, Livro

def pedagogia_view(request):
    # Ordenação para que os mais recentes fiquem no topo
    internos_frente = FrenteDeLeitura.objects.select_related("pessoa", "exemplar", "ciclo").order_by('-data_inicio', '-id')
    fila_espera = FilaDeEspera.objects.select_related("pessoa").order_by('-data_inclusao')
    internos_sairam = HistoricoLeitura.objects.select_related("pessoa").order_by('-data_saida', '-id')

    mes_atual, ano_atual = timezone.now().month, timezone.now().year
    ciclo_atual, _ = CicloLeitura.objects.get_or_create(mes=mes_atual, ano=ano_atual)
    livro_inicial = Livro.objects.first()

    # 🔍 Print do livro e ciclo atual de cada pessoa na frente de leitura
# Print do livro e ciclo atual de cada pessoa na frente de leitura
# Print do exemplar, código e ciclo
    for interno in internos_frente:
        if interno.exemplar:
            livro_titulo = interno.exemplar.livro.titulo
            codigo_exemplar = interno.exemplar.codigo
        else:
            livro_titulo = "Sem livro"
            codigo_exemplar = "Sem código"

        if interno.ciclo:
            ciclo_info = f"{interno.ciclo.mes}/{interno.ciclo.ano}"
        else:
            ciclo_info = "Sem ciclo"

        print(f"PESSOA: {interno.pessoa.nome_completo} | LIVRO: {livro_titulo} | CÓDIGO: {codigo_exemplar} | CICLO: {ciclo_info}")


    if request.method == "POST":
        pessoa_id = request.POST.get("pessoa_id")
        lista = request.POST.get("lista")  # "frente" ou "espera"
        motivo_saida = request.POST.get("motivo_saida")
        data_saida = request.POST.get("data_saida")

        if not pessoa_id:
            return JsonResponse({"erro": "ID da pessoa não foi enviado"}, status=400)

        pessoa = get_object_or_404(Pessoa, id=pessoa_id)

        # 🔁 Mover da fila para frente de leitura
        if lista == "frente":
            FilaDeEspera.objects.filter(pessoa=pessoa).delete()
            FrenteDeLeitura.objects.get_or_create(
                pessoa=pessoa,
                defaults={
                    "data_inicio": timezone.now().date(),
                    "livro": livro_inicial,
                    "ciclo": ciclo_atual,
                }
            )
            messages.success(request, f"{pessoa.nome_completo} foi movido para a Frente de Leitura ✅")
            return redirect("pedagogia_view")

        # ➕ Adicionar à fila de espera
        elif lista == "espera":
            FrenteDeLeitura.objects.filter(pessoa=pessoa).delete()
            FilaDeEspera.objects.get_or_create(
                pessoa=pessoa,
                defaults={"data_inclusao": timezone.now().date()}
            )
            messages.info(request, f"{pessoa.nome_completo} foi adicionado à Fila de Espera 📚")
            return redirect("pedagogia_view")

        # 📤 Registrar saída da leitura
        elif motivo_saida:
            frente = FrenteDeLeitura.objects.filter(pessoa=pessoa).first()
            if frente:
                HistoricoLeitura.objects.create(
                    pessoa=pessoa,
                    ciclo=frente.ciclo,   # pega o ciclo atual
                    data_saida=data_saida or timezone.now().date(),
                    motivo_saida=motivo_saida,
                )
                frente.delete()
                messages.warning(request, f"{pessoa.nome_completo} saiu da Frente de Leitura ({motivo_saida}) ❌")
                return redirect("pedagogia_view")
            else:
                return JsonResponse({"erro": "Interno não está na frente de leitura."}, status=400)

        return JsonResponse({"erro": "Preencha todos os campos necessários."}, status=400)

    return render(request, "painel/leitura.html", {
        "internos_frente": internos_frente,
        "fila_espera": fila_espera,
        "internos_sairam": internos_sairam,
    })



from django.views.decorators.http import require_POST


@require_POST
def excluir_interno_view(request):
    pessoa_id = request.POST.get("pessoa_id")
    lista = request.POST.get("lista")
    historico_id = request.POST.get("historico_id")

    if not pessoa_id or not lista:
        return JsonResponse({"erro": "Dados incompletos."}, status=400)

    pessoa = get_object_or_404(Pessoa, id=pessoa_id)

    if lista == "frente":
        FrenteDeLeitura.objects.filter(pessoa=pessoa).delete()
        messages.error(request, f"{pessoa.nome_completo} foi excluido da Frente de Leitura ❌")

    elif lista == "espera":
        FilaDeEspera.objects.filter(pessoa=pessoa).delete()
        messages.error(request, f"{pessoa.nome_completo} foi excluido da Fila de Espera ❌")

    elif lista == "historico":
        if not historico_id:
            return JsonResponse({"erro": "ID do histórico não informado."}, status=400)
        HistoricoLeitura.objects.filter(id=historico_id, pessoa=pessoa).delete()
        messages.error(request, f"Registro de saída de {pessoa.nome_completo} foi excluido do histórico ❌")

    else:
        return JsonResponse({"erro": "Lista inválida."}, status=400)

    return redirect("pedagogia_view")



# pedagogia/views.py
from django.http import JsonResponse
from django.db.models import Count, Sum
from .models import FilaDeEspera, FrenteDeLeitura, HistoricoLeitura
from .models import FilaDeEspera, FrenteDeLeitura, HistoricoLeitura, Leitura

from django.db.models import Count
def dados_grafico_leitura(request):
    total_frente = FrenteDeLeitura.objects.count()
    total_espera = FilaDeEspera.objects.count()
    total_saida = HistoricoLeitura.objects.count()

    motivos_saida = (
        HistoricoLeitura.objects
        .values('motivo_saida')
        .annotate(total=Count('id'))
    )

    livros_por_saida = (
        Leitura.objects
        .values('pessoa__nome_completo')
        .annotate(total=Count('livro'))
        .order_by('-total')[:10]
    )

    return JsonResponse({
        "distribuicao": {
            "frente": total_frente,
            "espera": total_espera,
            "saida": total_saida,
        },
        "motivos_saida": list(motivos_saida),
        "livros_saida": list(livros_por_saida),
    })

from django.http import JsonResponse
from django.views.decorators.http import require_GET

@require_GET
def buscar_interno(request):
    query = request.GET.get("q", "").strip()

    if not query:
        return JsonResponse({"erro": "Nenhum termo de busca enviado."}, status=400)

    # Buscar nas três tabelas
    internos_frente = list(
        FrenteDeLeitura.objects.select_related("pessoa", "exemplar", "ciclo", "exemplar__livro")
        .filter(pessoa__nome_completo__icontains=query)
        .values(
            "pessoa__id",
            "pessoa__nome_completo",
            "pessoa__bloco",
            "pessoa__cela",
            "exemplar__livro__titulo",
            "exemplar__codigo",
            "ciclo__mes",
            "ciclo__ano",
            "data_inicio"
        )
    )

    fila_espera = list(
        FilaDeEspera.objects.select_related("pessoa")
        .filter(pessoa__nome_completo__icontains=query)
        .values(
            "pessoa__id",
            "pessoa__nome_completo",
            "pessoa__bloco",
            "pessoa__cela",
            "data_inclusao"
        )
    )

    internos_sairam = list(
        HistoricoLeitura.objects.select_related("pessoa")
        .filter(pessoa__nome_completo__icontains=query)
        .values(
            "pessoa__id",
            "pessoa__nome_completo",
            "pessoa__bloco",
            "pessoa__cela",
            "data_saida",
            "motivo_saida"
        )
    )


    return JsonResponse({
        "frente": internos_frente,
        "espera": fila_espera,
        "sairam": internos_sairam,
    })


from django.views.decorators.http import require_GET
from django.http import JsonResponse
from .models import Leitura
from .models import FrenteDeLeitura

@require_GET
def listar_livros_interno(request):
    pessoa_id = request.GET.get("pessoa_id")
    if not pessoa_id:
        return JsonResponse({"erro": "ID da pessoa não enviado"}, status=400)
    
    # Pegando todos os exemplares que a pessoa leu no ciclo atual
    leituras = FrenteDeLeitura.objects.filter(pessoa_id=pessoa_id).select_related("exemplar__livro", "ciclo")
    
    dados = []
    for f in leituras:
        dados.append({
            "livro": f.exemplar.livro.titulo if f.exemplar else "Sem livro",
            "codigo_exemplar": f.exemplar.codigo if f.exemplar else "Sem código",
            "ciclo": f"{f.ciclo.mes}/{f.ciclo.ano}" if f.ciclo else "Sem ciclo"
        })
    return JsonResponse({"livros": dados})


from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import Livro, Exemplar

@require_POST
def cadastrar_livro(request):
    id_livro = request.POST.get("id_livro")
    codigo = request.POST.get("codigo", "").strip()
    titulo = request.POST.get("titulo", "").strip()
    autor = request.POST.get("autor", "").strip()

    if not codigo:
        return JsonResponse({"erro": "O código do exemplar é obrigatório."}, status=400)

    # Se id_livro foi enviado, apenas cadastra exemplar
    if id_livro:
        try:
            livro = Livro.objects.get(pk=id_livro)
        except Livro.DoesNotExist:
            return JsonResponse({"erro": "Livro selecionado não encontrado."}, status=400)
    else:
        if not titulo:
            return JsonResponse({"erro": "O título do livro é obrigatório."}, status=400)
        livro, criado = Livro.objects.get_or_create(titulo=titulo, defaults={"autor": autor})

    # Criar o exemplar
    if Exemplar.objects.filter(codigo=codigo).exists():
        return JsonResponse({"erro": "Já existe um exemplar com esse código."}, status=400)

    Exemplar.objects.create(livro=livro, codigo=codigo)

    total_exemplares = livro.exemplares.count()

    return JsonResponse({
        "mensagem": "Exemplar cadastrado com sucesso!" if id_livro else "Livro e exemplar cadastrados com sucesso!",
        "total_exemplares": total_exemplares
    })


from django.views.decorators.http import require_GET
from django.http import JsonResponse
from .models import Livro

@require_GET
def buscar_livro(request):
    query = request.GET.get("q", "").strip()
    if not query:
        return JsonResponse({"livros": []})

    livros = Livro.objects.filter(titulo__icontains=query)[:10]  # limitar a 10 resultados
    resultados = [{"id": l.id, "titulo": l.titulo, "autor": l.autor} for l in livros]
    return JsonResponse({"livros": resultados})
