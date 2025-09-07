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
    livros = Livro.objects.prefetch_related("exemplares").all().order_by("titulo")

    mes_atual, ano_atual = timezone.now().month, timezone.now().year
    ciclo_atual, _ = CicloLeitura.objects.get_or_create(mes=mes_atual, ano=ano_atual)

    # 🔍 Print do livro e ciclo atual de cada pessoa na frente de leitura
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
        "livros": livros,
    })



# views.py
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from .models import FrenteDeLeitura, Exemplar, CicloLeitura
from painel.models import Pessoa


@require_POST
def adicionar_exemplar_interno(request):
    pessoa_id = request.POST.get("pessoa_id")
    exemplar_id = request.POST.get("exemplar_id")

    pessoa = get_object_or_404(Pessoa, id=pessoa_id)
    exemplar = get_object_or_404(Exemplar, id=exemplar_id)

    # ciclo atual
    mes, ano = now().month, now().year
    ciclo, _ = CicloLeitura.objects.get_or_create(mes=mes, ano=ano)

    # cria ou atualiza frente de leitura
    frente, created = FrenteDeLeitura.objects.get_or_create(
        pessoa=pessoa,
        defaults={"exemplar": exemplar, "ciclo": ciclo}
    )

    if not created:
        frente.exemplar = exemplar
        frente.ciclo = ciclo
        frente.save()

    # marcar exemplar como indisponível
    exemplar.disponivel = False
    exemplar.save()

    return JsonResponse({
        "sucesso": True,  # necessário bater com JS
        "livro": exemplar.livro.titulo,
        "codigo": exemplar.codigo,
        "ciclo": str(ciclo),
        "pessoa": pessoa.nome_completo
    })


@require_POST
def remover_exemplar_interno(request):
    pessoa_id = request.POST.get("pessoa_id")
    codigo_exemplar = request.POST.get("exemplar_codigo")

    if not pessoa_id or not codigo_exemplar:
        return JsonResponse({"success": False, "erro": "Dados incompletos."})

    try:
        pessoa = Pessoa.objects.get(id=pessoa_id)
        exemplar = Exemplar.objects.get(codigo=codigo_exemplar)
    except (Pessoa.DoesNotExist, Exemplar.DoesNotExist):
        return JsonResponse({"success": False, "erro": "Pessoa ou exemplar não encontrado."})

    # 1️⃣ Tentar remover da FrenteDeLeitura (ciclo atual)
    try:
        frente = FrenteDeLeitura.objects.get(pessoa=pessoa, exemplar=exemplar)
        frente.exemplar = None
        frente.save()
        exemplar.disponivel = True
        exemplar.save()
        return JsonResponse({"success": True, "exemplar_codigo": codigo_exemplar})
    except FrenteDeLeitura.DoesNotExist:
        # 2️⃣ Tentar remover do histórico de leituras (Leitura)
        leituras = Leitura.objects.filter(pessoa=pessoa, exemplar=exemplar)
        if leituras.exists():
            leituras.delete()  # remove registro de leitura antigo
            exemplar.disponivel = True
            exemplar.save()
            return JsonResponse({"success": True, "exemplar_codigo": codigo_exemplar})
        else:
            return JsonResponse({"success": False, "erro": "Exemplar não atribuído a esta pessoa."})


from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import Exemplar, FrenteDeLeitura, CicloLeitura
from django.utils.timezone import now

@require_GET
def livro_exemplares(request, livro_id):
    exemplares = Exemplar.objects.filter(livro_id=livro_id).select_related("livro")
    mes, ano = now().month, now().year
    ciclo_atual, _ = CicloLeitura.objects.get_or_create(mes=mes, ano=ano)

    dados = []
    for ex in exemplares:
        leitor = None
        # busca na frente de leitura se alguém está lendo este exemplar no ciclo atual
        try:
            frente = FrenteDeLeitura.objects.get(exemplar=ex, ciclo=ciclo_atual)
            leitor = frente.pessoa.nome_completo
        except FrenteDeLeitura.DoesNotExist:
            leitor = None

        dados.append({
            "id": ex.id,
            "codigo": ex.codigo,
            "disponivel": ex.disponivel,
            "leitor_atual": leitor
        })

    return JsonResponse({"exemplares": dados})



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
from .models import Leitura, FrenteDeLeitura, CicloLeitura

@require_GET
def listar_livros_interno(request):
    pessoa_id = request.GET.get("pessoa_id")
    if not pessoa_id:
        return JsonResponse({"erro": "ID da pessoa não enviado"}, status=400)
    
    dados = []

    # 1️⃣ Frente de Leitura (ciclo atual)
    try:
        frente = FrenteDeLeitura.objects.select_related("exemplar__livro", "ciclo", "pessoa").get(pessoa_id=pessoa_id)
        if frente.exemplar:
            dados.append({
                "livro": frente.exemplar.livro.titulo,
                "codigo_exemplar": frente.exemplar.codigo,
                "ciclo": f"{frente.ciclo.mes}/{frente.ciclo.ano}",
                "status": "Ativo",
                "leitor_atual": frente.pessoa.nome_completo  # mostra quem está lendo agora
            })
    except FrenteDeLeitura.DoesNotExist:
        frente = None

    # 2️⃣ Leituras anteriores (todos os ciclos, exceto o atual)
    ciclo_atual = frente.ciclo if frente else None
    leituras = Leitura.objects.filter(pessoa_id=pessoa_id)
    if ciclo_atual:
        leituras = leituras.exclude(ciclo=ciclo_atual)
    leituras = leituras.select_related("livro", "ciclo", "exemplar", "pessoa")

    for l in leituras:
        dados.append({
            "livro": l.livro.titulo,
            "codigo_exemplar": l.exemplar.codigo if l.exemplar else "-",
            "ciclo": f"{l.ciclo.mes}/{l.ciclo.ano}",
            "status": "Concluído",
            "leitor_atual": l.pessoa.nome_completo  # opcional: quem leu anteriormente
        })

    # 🔹 Log para debug no console do backend
    for i, item in enumerate(dados):
        print(f"[{i}] Livro: {item['livro']}, Código: {item['codigo_exemplar']}, Ciclo: {item['ciclo']}, Status: {item['status']}, Leitor atual: {item['leitor_atual']}")

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
