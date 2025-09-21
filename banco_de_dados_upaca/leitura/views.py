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
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib import messages
from django.http import JsonResponse
from .models import FrenteDeLeitura, FilaDeEspera, HistoricoLeitura, Livro, Exemplar, CicloLeitura
from painel.models import Pessoa

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone

def pedagogia_view(request):
    # Ordenação para que os mais recentes fiquem no topo
    internos_frente = FrenteDeLeitura.objects.select_related("pessoa", "exemplar", "ciclo").order_by('-data_inicio', '-id')
    fila_espera = FilaDeEspera.objects.select_related("pessoa").order_by('-data_inclusao')
    internos_sairam = HistoricoLeitura.objects.select_related("pessoa").order_by('-data_saida', '-id')
    livros = Livro.objects.prefetch_related("exemplares").all().order_by("titulo")

    # Obtém o ciclo atual pelo modelo
    ciclo_atual = CicloLeitura.ciclo_atual()

    # 🔍 Print do livro e ciclo atual de cada pessoa na frente de leitura
    for interno in internos_frente:
        if interno.exemplar:
            livro_titulo = interno.exemplar.livro.titulo
            codigo_exemplar = interno.exemplar.codigo
        else:
            livro_titulo = "Sem livro"
            codigo_exemplar = "Sem código"

        if interno.ciclo:
            inicio = interno.ciclo.inicio.strftime('%d/%m/%Y') if interno.ciclo.inicio else "Não definido"
            fim = interno.ciclo.fim.strftime('%d/%m/%Y') if interno.ciclo.fim else "Não definido"
            ciclo_info = f"{inicio} - {fim}"
        else:
            ciclo_info = "Sem ciclo"

        print(f"PESSOA: {interno.pessoa.nome_completo} | LIVRO: {livro_titulo} | CÓDIGO: {codigo_exemplar} | CICLO: {ciclo_info}")

    # Processamento de POST (movimentações)
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

            # Pega o ciclo correto
            ciclo = CicloLeitura.ciclo_atual() or CicloLeitura.proximo_ciclo_numerico()
            
            FrenteDeLeitura.objects.get_or_create(
                pessoa=pessoa,
                defaults={
                    "data_inicio": timezone.now().date(),
                    "ciclo": ciclo,
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
                    ciclo=frente.ciclo,
                    data_saida=data_saida or timezone.now().date(),
                    motivo_saida=motivo_saida,
                )
                frente.delete()
                messages.warning(request, f"{pessoa.nome_completo} saiu da Frente de Leitura ({motivo_saida}) ❌")
                return redirect("pedagogia_view")
            else:
                return JsonResponse({"erro": "Interno não está na frente de leitura."}, status=400)

        return JsonResponse({"erro": "Preencha todos os campos necessários."}, status=400)

    # Render do template
    return render(request, "painel/leitura.html", {
        "internos_frente": internos_frente,
        "fila_espera": fila_espera,
        "internos_sairam": internos_sairam,
        "livros": livros,
        "ciclo_atual": ciclo_atual,
    })



from django.http import JsonResponse
from django.utils.timezone import now
from .models import FrenteDeLeitura

def avancar_ciclos_ativos_ajax(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "mensagem": "Método inválido"})

    internos_frente = FrenteDeLeitura.objects.select_related("ciclo", "pessoa", "exemplar").all()
    total_avancados = 0
    motivos_nao_avancar = []

    for frente in internos_frente:
        ciclo_atual = frente.ciclo
        if ciclo_atual and ciclo_atual.fim:
            if ciclo_atual.fim < now().date():
                # 1️⃣ Liberar exemplar atual, se houver
                if frente.exemplar:
                    frente.exemplar.disponivel = True
                    frente.exemplar.save()
                    frente.exemplar = None  # remove da frente
                    frente.save()

                # 2️⃣ Avançar para próximo ciclo
                proximo_ciclo = frente.avancar_ciclo()
                if proximo_ciclo:
                    total_avancados += 1
                else:
                    motivos_nao_avancar.append({
                        "nome": frente.pessoa.nome_completo,
                        "motivo": "Não há próximo ciclo definido"
                    })
            else:
                motivos_nao_avancar.append({
                    "nome": frente.pessoa.nome_completo,
                    "motivo": f"Ciclo atual ({ciclo_atual.numero}/{ciclo_atual.ano}) ainda não terminou ({ciclo_atual.fim.strftime('%d/%m/%Y')})"
                })
        else:
            motivos_nao_avancar.append({
                "nome": frente.pessoa.nome_completo,
                "motivo": "Ciclo não definido ou datas ausentes"
            })

    return JsonResponse({
        "status": "success",
        "mensagem": f"Ciclos avançados: {total_avancados}, não avançados: {len(motivos_nao_avancar)}",
        "motivos": motivos_nao_avancar
    })

from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET   # <- aqui incluímos require_GET
from django.shortcuts import get_object_or_404

# Função utilitária
from .utils import ja_leu_livro  # importando do utils

# ---------------------------
# Endpoint para checar se o interno já leu um livro
# ---------------------------
@require_GET
def checar_livro_lido(request):
    pessoa_id = request.GET.get("pessoa_id")
    livro_id = request.GET.get("livro_id")
    if not pessoa_id or not livro_id:
        return JsonResponse({"sucesso": False, "erro": "Parâmetros obrigatórios"}, status=400)
    
    try:
        ja_leu = ja_leu_livro(pessoa_id, livro_id)
        pessoa = Pessoa.objects.get(id=pessoa_id)
        livro = Livro.objects.get(id=livro_id)
    except (Pessoa.DoesNotExist, Livro.DoesNotExist):
        return JsonResponse({"sucesso": False, "erro": "Pessoa ou livro não encontrado"}, status=404)

    return JsonResponse({
        "sucesso": True,
        "ja_leu": ja_leu,
        "mensagem": f"{pessoa.nome_completo} {'já leu' if ja_leu else 'não leu'} o livro '{livro.titulo}'"
    })

# ---------------------------
# View para adicionar exemplar a um interno
# ---------------------------
@require_POST
def adicionar_exemplar_interno(request):
    pessoa_id = request.POST.get("pessoa_id")
    exemplar_id = request.POST.get("exemplar_id")
    ciclo_id = request.POST.get("ciclo_id")

    pessoa = get_object_or_404(Pessoa, id=pessoa_id)
    novo_exemplar = get_object_or_404(Exemplar, id=exemplar_id)

    # ---------------------------
    # 1️⃣ Checar se o livro já foi lido
    # ---------------------------
    livro = novo_exemplar.livro
    if Leitura.objects.filter(pessoa=pessoa, livro=livro).exists():
        return JsonResponse({
            "sucesso": False,
            "erro": f"{pessoa.nome_completo} já leu o livro '{livro.titulo}'."
        }, status=400)

    # ---------------------------
    # 2️⃣ Descobre ciclo escolhido
    # ---------------------------
    ciclo_escolhido = CicloLeitura.objects.filter(id=ciclo_id).first() if ciclo_id else None
    ciclo_atual = CicloLeitura.ciclo_atual()

    # ---------------------------
    # 3️⃣ Caso 1: ciclo atual → atualizar FrenteDeLeitura
    # ---------------------------
    if ciclo_escolhido and ciclo_atual and ciclo_escolhido.id == ciclo_atual.id:
        frente, created = FrenteDeLeitura.objects.get_or_create(pessoa=pessoa)

        # Se já tinha exemplar, libera ele
        if frente.exemplar and frente.exemplar != novo_exemplar:
            frente.exemplar.disponivel = True
            frente.exemplar.save()

        # Atualiza frente
        frente.exemplar = novo_exemplar
        frente.ciclo = ciclo_atual
        frente.save()

        # Marca novo exemplar como indisponível
        novo_exemplar.disponivel = False
        novo_exemplar.save()

        # Cria histórico de leitura
        leitura = Leitura.objects.create(
            pessoa=pessoa,
            livro=livro,
            exemplar=novo_exemplar,
            ciclo=ciclo_atual,
            ciclo_indefinido=False
        )

        status = "atualizado"

    # ---------------------------
    # 4️⃣ Caso 2: ciclo diferente → apenas histórico
    # ---------------------------
    else:
        leitura = Leitura.objects.create(
            pessoa=pessoa,
            livro=livro,
            exemplar=novo_exemplar,
            ciclo=ciclo_escolhido,
            ciclo_indefinido=True if not ciclo_escolhido else False
        )

        # Marca exemplar como indisponível
        #novo_exemplar.disponivel = False
        #novo_exemplar.save()

        status = "historico"

    # ---------------------------
    # 5️⃣ Retorno JSON
    # ---------------------------
    return JsonResponse({
        "sucesso": True,
        "status": status,
        "livro": livro.titulo,
        "codigo": novo_exemplar.codigo,
        "ciclo": (
            f"Ciclo {ciclo_escolhido.numero}/{ciclo_escolhido.ano}"
            if ciclo_escolhido else "Indefinido"
        ),
        "pessoa": pessoa.nome_completo,
        "leitura_id": leitura.id,
    })

from random import choice

# ============================================
# View para sortear livros para todos internos sem exemplar
# ============================================
@require_POST
def sortear_livros_frente(request):
    """
    Sorteia um livro disponível para cada interno na frente de leitura
    que atualmente não possui exemplar. Verifica histórico de leitura
    usando a função ja_leu_livro do utils.
    """

    internos = FrenteDeLeitura.objects.select_related("pessoa", "exemplar", "ciclo").all()
    resultados = []

    for frente in internos:
        # Só sorteia se não houver exemplar atualmente
        if frente.exemplar is None:
            # Pega todos exemplares disponíveis
            exemplares_disponiveis = Exemplar.objects.filter(disponivel=True)

            # Filtra apenas livros que o interno ainda não leu
            livros_validos = [
                ex for ex in exemplares_disponiveis
                if not ja_leu_livro(frente.pessoa.id, ex.livro.id)
            ]

            if livros_validos:
                exemplar_escolhido = choice(livros_validos)

                # Atualiza a frente
                frente.exemplar = exemplar_escolhido
                frente.save()

                # Marca exemplar como indisponível
                exemplar_escolhido.disponivel = False
                exemplar_escolhido.save()

                # Cria registro de leitura no histórico
                Leitura.objects.create(
                    pessoa=frente.pessoa,
                    livro=exemplar_escolhido.livro,
                    exemplar=exemplar_escolhido,
                    ciclo=frente.ciclo,
                    ciclo_indefinido=False if frente.ciclo else True
                )

                resultados.append({
                    "pessoa__nome_completo": frente.pessoa.nome_completo,
                    "exemplar__livro__titulo": exemplar_escolhido.livro.titulo,
                    "exemplar__codigo": exemplar_escolhido.codigo,
                    "ciclo__mes": frente.ciclo.numero if frente.ciclo else None,
                    "ciclo__ano": frente.ciclo.ano if frente.ciclo else None,
                    "pessoa__bloco": getattr(frente.pessoa, 'bloco', ''),
                    "pessoa__cela": getattr(frente.pessoa, 'cela', ''),
                })
            else:
                resultados.append({
                    "pessoa": frente.pessoa.nome_completo,
                    "status": "sem_livro_disponivel"
                })

    return JsonResponse({
        "sucesso": True,
        "mensagem": f"{len(resultados)} internos processados",
        "resultados": resultados
    })


from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import CicloLeitura
from datetime import datetime

@require_POST
def definir_ciclo(request):
    ciclo_id = request.POST.get("ciclo_id")
    numero = request.POST.get("numero")
    ano = request.POST.get("ano")
    inicio = request.POST.get("inicio")  # "YYYY-MM-DD" ou vazio
    fim = request.POST.get("fim")        # "YYYY-MM-DD" ou vazio

    # Validação básica: apenas número e ano são obrigatórios
    if not numero or not ano:
        return JsonResponse({"sucesso": False, "erro": "Número e ano são obrigatórios"})

    try:
        numero = int(numero)
        ano = int(ano)
        # Só converte se tiver valor, senão deixa None
        inicio = datetime.strptime(inicio, "%Y-%m-%d").date() if inicio else None
        fim = datetime.strptime(fim, "%Y-%m-%d").date() if fim else None
    except Exception:
        return JsonResponse({"sucesso": False, "erro": "Formato de número/ano/data inválido"})

    if ciclo_id:
        # Editar ciclo existente
        ciclo = CicloLeitura.objects.filter(id=ciclo_id).first()
        if ciclo:
            ciclo.numero = numero
            ciclo.ano = ano
            ciclo.inicio = inicio
            ciclo.fim = fim
            ciclo.save()
        else:
            return JsonResponse({"sucesso": False, "erro": "Ciclo não encontrado"})
    else:
        # Criar novo ciclo
        ciclo, created = CicloLeitura.objects.get_or_create(
            numero=numero, ano=ano,
            defaults={"inicio": inicio, "fim": fim}
        )
        if not created:
            ciclo.inicio = inicio
            ciclo.fim = fim
            ciclo.save()

    return JsonResponse({"sucesso": True, "mensagem": "Ciclo definido com sucesso"})


    return JsonResponse({"sucesso": True, "ciclo": str(ciclo)})

from django.http import JsonResponse
from .models import CicloLeitura

from django.http import JsonResponse
from .models import CicloLeitura

def listar_ciclos(request):
    ano = request.GET.get("ano")
    
    if ano:
        ciclos = CicloLeitura.objects.filter(ano=ano).order_by("numero")
    else:
        ciclos = CicloLeitura.objects.all().order_by("ano", "numero")

    data = [
        {
            "id": ciclo.id,
            "numero": ciclo.numero,
            "ano": ciclo.ano,
            "inicio": ciclo.inicio.strftime("%d/%m/%Y") if ciclo.inicio else "",
            "fim": ciclo.fim.strftime("%d/%m/%Y") if ciclo.fim else "",
        }
        for ciclo in ciclos
    ]

    return JsonResponse({"ciclos": data})

from django.http import JsonResponse
from .models import CicloLeitura

def detalhar_ciclo(request, ciclo_id):
    ciclo = CicloLeitura.objects.filter(id=ciclo_id).first()
    if not ciclo:
        return JsonResponse({"erro": "Ciclo não encontrado"}, status=404)

    data = {
        "id": ciclo.id,
        "numero": ciclo.numero,
        "ano": ciclo.ano,
        "inicio": ciclo.inicio.strftime("%Y-%m-%d") if ciclo.inicio else "",
        "fim": ciclo.fim.strftime("%Y-%m-%d") if ciclo.fim else "",
    }
    return JsonResponse(data)


from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import FrenteDeLeitura, Exemplar, Leitura
from painel.models import Pessoa

@require_POST
def remover_exemplar_interno(request):
    pessoa_id = request.POST.get("pessoa_id")
    codigo_exemplar = request.POST.get("exemplar_codigo")

    if not pessoa_id or not codigo_exemplar:
        return JsonResponse({"success": False, "erro": "Dados incompletos."})

    pessoa = get_object_or_404(Pessoa, id=pessoa_id)
    exemplar = get_object_or_404(Exemplar, codigo=codigo_exemplar)

    # 1️⃣ Verifica se o exemplar estava na FrenteDeLeitura
    frente = FrenteDeLeitura.objects.filter(pessoa=pessoa, exemplar=exemplar).first()
    if frente:
        # Remove da FrenteDeLeitura
        frente.exemplar = None
        frente.save()
        
        # Marca exemplar como disponível, pois estava em uso
        exemplar.disponivel = True
        exemplar.save()

    # 2️⃣ Remove o exemplar apenas do histórico, sem alterar disponibilidade
    Leitura.objects.filter(pessoa=pessoa, exemplar=exemplar).delete()

    return JsonResponse({
        "success": True,
        "exemplar_codigo": codigo_exemplar,
        "mensagem": f"Exemplar {codigo_exemplar} removido da FrenteDeLeitura e do histórico de leituras."
    })



from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import Exemplar, FrenteDeLeitura, CicloLeitura
from django.utils.timezone import now

from django.views.decorators.http import require_GET

@require_GET
def livro_exemplares(request, livro_id):
    exemplares = Exemplar.objects.filter(livro_id=livro_id).select_related("livro")
    
    dados = []
    for ex in exemplares:
        leitor = None
        try:
            # Verifica se o exemplar está em uso na frente de leitura, sem se importar com ciclo
            frente = FrenteDeLeitura.objects.get(exemplar=ex)
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

    # Frente de Leitura (ciclo atual)
    try:
        frente = FrenteDeLeitura.objects.select_related("exemplar__livro", "ciclo", "pessoa").get(pessoa_id=pessoa_id)
        if frente.exemplar:
            ciclo_formatado = "Não definido"
            if frente.ciclo and frente.ciclo.inicio:
                ciclo_formatado = f"{frente.ciclo.inicio.day}/{frente.ciclo.inicio.month}/{frente.ciclo.ano}"

            dados.append({
                "livro": frente.exemplar.livro.titulo,
                "codigo_exemplar": frente.exemplar.codigo,
                "ciclo": ciclo_formatado,
                "status": "Ativo",
                "leitor_atual": frente.pessoa.nome_completo
            })
    except FrenteDeLeitura.DoesNotExist:
        frente = None

    # Leituras anteriores
    ciclo_atual = frente.ciclo if frente else None
    leituras = Leitura.objects.filter(pessoa_id=pessoa_id)
    if ciclo_atual:
        leituras = leituras.exclude(ciclo=ciclo_atual)
    leituras = leituras.select_related("livro", "ciclo", "exemplar", "pessoa")

    for l in leituras:
        ciclo_formatado = "Não definido"
        if l.ciclo and l.ciclo.inicio:
            ciclo_formatado = f"{l.ciclo.inicio.day}/{l.ciclo.inicio.month}/{l.ciclo.ano}"

        dados.append({
            "livro": l.livro.titulo,
            "codigo_exemplar": l.exemplar.codigo if l.exemplar else "-",
            "ciclo": ciclo_formatado,
            "status": "Concluído",
            "leitor_atual": l.pessoa.nome_completo
        })

    # Log backend
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


