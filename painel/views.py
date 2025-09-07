from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import F, Q
from django.db.models.functions import Lower
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.utils.timezone import now
import os
import csv
from datetime import datetime, timedelta
from django.db import models

# Models
from .models import Pessoa, Transferencia, Sancao, Eletronico, HistoricoAlteracao, FrenteDeTrabalho

# Forms
from .forms import PessoaForm, TransferenciaForm, EletronicoForm, SancaoForm
from notification.models import Notificacao
# ReportLab (PDF Generation)
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from django.contrib.staticfiles import finders
from collections import defaultdict
@login_required
def index_view(request):
    # Contagem total de pessoas cadastradas, excluindo as com transferência ativa, saiu_temporariamente ativo e albergados
    pessoas_list = Pessoa.objects.exclude(tem_transferencia_ativa=True) \
    .exclude(saiu_temporariamente=True) \
    .exclude(albergado=True) \
    .exclude(status__in=["inativo", "foragido"])


    form = PessoaForm()  # Adicionando o formulário


    total_pessoas = pessoas_list.count()
    limite_maximo = 294  # Limite máximo para o gráfico
    porcentagem_cadastrados = (total_pessoas / limite_maximo) * 100  # Pode ultrapassar 100%
    total_saiu_temporariamente = Pessoa.objects.filter(saiu_temporariamente=True).count()  # Contagem das pessoas que saíram temporariamente
    total_albergado = Pessoa.objects.filter(albergado=True).count()  # Contagem das pessoas albergadas
    
    # Obter os nomes dos albergados
    albergados = Pessoa.objects.filter(albergado=True)
    # Passando uma lista de nomes ao invés de uma string concatenada
    nomes_albergados = [pessoa.nome_completo for pessoa in albergados]

    # Obter os nomes das pessoas que saíram temporariamente
    pessoas_saiu_temporariamente = Pessoa.objects.filter(saiu_temporariamente=True)
    nomes_saiu_temporariamente = ', '.join(pessoa.nome_completo for pessoa in pessoas_saiu_temporariamente)
    # Criando um dicionário para armazenar a contagem de eletrônicos por cela
    eletronicos_por_cela = defaultdict(lambda: {"tv": 0, "radio": 0, "ventilador": 0})

    # Obtendo todas as pessoas dentro do presídio
    pessoas_nas_celas = Pessoa.objects.exclude(saiu_temporariamente=True).exclude(albergado=True)

    # Filtra as pessoas para mostrar por bloco, excluindo as pessoas que saíram temporariamente ou são albergados
    bloco_a = Pessoa.objects.filter(bloco='A').exclude(saiu_temporariamente=True).exclude(albergado=True)
    bloco_b = Pessoa.objects.filter(bloco='B').exclude(saiu_temporariamente=True).exclude(albergado=True)
    bloco_c = Pessoa.objects.filter(bloco='C').exclude(saiu_temporariamente=True).exclude(albergado=True)
    bloco_d = Pessoa.objects.filter(bloco='D').exclude(saiu_temporariamente=True).exclude(albergado=True)
    bloco_e = Pessoa.objects.filter(bloco='E').exclude(saiu_temporariamente=True).exclude(albergado=True)

    # Mostrar os nomes dos internos que estão dentro de cada cela
    # Criando dicionários com as pessoas de cada cela
    celas_nomes = {
    'A1': sorted([{'id': pessoa.id, 'nome': pessoa.nome_completo} for pessoa in bloco_a.filter(cela='1')], key=lambda x: x['nome']),
    'A2': sorted([{'id': pessoa.id, 'nome': pessoa.nome_completo} for pessoa in bloco_a.filter(cela='2')], key=lambda x: x['nome']),
    'A3': sorted([{'id': pessoa.id, 'nome': pessoa.nome_completo} for pessoa in bloco_a.filter(cela='3')], key=lambda x: x['nome']),
    'A4': sorted([{'id': pessoa.id, 'nome': pessoa.nome_completo} for pessoa in bloco_a.filter(cela='4')], key=lambda x: x['nome']),
    'A5': sorted([{'id': pessoa.id, 'nome': pessoa.nome_completo} for pessoa in bloco_a.filter(cela='5')], key=lambda x: x['nome']),

    'B1': sorted([{'id': pessoa.id, 'nome': pessoa.nome_completo} for pessoa in bloco_b.filter(cela='1')], key=lambda x: x['nome']),
    'B2': sorted([{'id': pessoa.id, 'nome': pessoa.nome_completo} for pessoa in bloco_b.filter(cela='2')], key=lambda x: x['nome']),
    'B3': sorted([{'id': pessoa.id, 'nome': pessoa.nome_completo} for pessoa in bloco_b.filter(cela='3')], key=lambda x: x['nome']),
    'B4': sorted([{'id': pessoa.id, 'nome': pessoa.nome_completo} for pessoa in bloco_b.filter(cela='4')], key=lambda x: x['nome']),
    'B5': sorted([{'id': pessoa.id, 'nome': pessoa.nome_completo} for pessoa in bloco_b.filter(cela='5')], key=lambda x: x['nome']),

    'C1': sorted([{'id': pessoa.id, 'nome': pessoa.nome_completo} for pessoa in bloco_c.filter(cela='1')], key=lambda x: x['nome']),
    'C2': sorted([{'id': pessoa.id, 'nome': pessoa.nome_completo} for pessoa in bloco_c.filter(cela='2')], key=lambda x: x['nome']),
    'C3': sorted([{'id': pessoa.id, 'nome': pessoa.nome_completo} for pessoa in bloco_c.filter(cela='3')], key=lambda x: x['nome']),
    'C4': sorted([{'id': pessoa.id, 'nome': pessoa.nome_completo} for pessoa in bloco_c.filter(cela='4')], key=lambda x: x['nome']),
    'C5': sorted([{'id': pessoa.id, 'nome': pessoa.nome_completo} for pessoa in bloco_c.filter(cela='5')], key=lambda x: x['nome']),
    'C6': sorted([{'id': pessoa.id, 'nome': pessoa.nome_completo} for pessoa in bloco_c.filter(cela='6')], key=lambda x: x['nome']),
    'C7': sorted([{'id': pessoa.id, 'nome': pessoa.nome_completo} for pessoa in bloco_c.filter(cela='7')], key=lambda x: x['nome']),

    'D1': sorted([{'id': pessoa.id, 'nome': pessoa.nome_completo} for pessoa in bloco_d.filter(cela='1')], key=lambda x: x['nome']),
    'D2': sorted([{'id': pessoa.id, 'nome': pessoa.nome_completo} for pessoa in bloco_d.filter(cela='2')], key=lambda x: x['nome']),
    'D3': sorted([{'id': pessoa.id, 'nome': pessoa.nome_completo} for pessoa in bloco_d.filter(cela='3')], key=lambda x: x['nome']),
    'D4': sorted([{'id': pessoa.id, 'nome': pessoa.nome_completo} for pessoa in bloco_d.filter(cela='4')], key=lambda x: x['nome']),
    'D5': sorted([{'id': pessoa.id, 'nome': pessoa.nome_completo} for pessoa in bloco_d.filter(cela='5')], key=lambda x: x['nome']),

    'E1': sorted([{'id': pessoa.id, 'nome': pessoa.nome_completo} for pessoa in bloco_e.filter(cela='1')], key=lambda x: x['nome']),
    'E2': sorted([{'id': pessoa.id, 'nome': pessoa.nome_completo} for pessoa in bloco_e.filter(cela='2')], key=lambda x: x['nome']),
    'E3': sorted([{'id': pessoa.id, 'nome': pessoa.nome_completo} for pessoa in bloco_e.filter(cela='3')], key=lambda x: x['nome']),
    'E4': sorted([{'id': pessoa.id, 'nome': pessoa.nome_completo} for pessoa in bloco_e.filter(cela='4')], key=lambda x: x['nome']),
    'E5': sorted([{'id': pessoa.id, 'nome': pessoa.nome_completo} for pessoa in bloco_e.filter(cela='5')], key=lambda x: x['nome']),
    'E6': sorted([{'id': pessoa.id, 'nome': pessoa.nome_completo} for pessoa in bloco_e.filter(cela='6')], key=lambda x: x['nome']),
    'E7': sorted([{'id': pessoa.id, 'nome': pessoa.nome_completo} for pessoa in bloco_e.filter(cela='7')], key=lambda x: x['nome']),
}

    for pessoa in pessoas_nas_celas:
            # Verifica se a pessoa tem eletrônicos cadastrados
            for eletronico in pessoa.eletronicos.all():
                eletronicos_por_cela[f"{pessoa.bloco}{pessoa.cela}"][eletronico.tipo] += 1
    # Contagem por cela para cada bloco, excluindo as pessoas que saíram temporariamente ou são albergados
    cela_1_a = bloco_a.filter(cela='1').count()
    cela_2_a = bloco_a.filter(cela='2').count()
    cela_3_a = bloco_a.filter(cela='3').count()
    cela_4_a = bloco_a.filter(cela='4').count()
    cela_5_a = bloco_a.filter(cela='5').count()

    cela_b1 = bloco_b.filter(cela='1').count()
    cela_b2 = bloco_b.filter(cela='2').count()
    cela_b3 = bloco_b.filter(cela='3').count()
    cela_b4 = bloco_b.filter(cela='4').count()
    cela_b5 = bloco_b.filter(cela='5').count()

    cela_c1 = bloco_c.filter(cela='1').count()
    cela_c2 = bloco_c.filter(cela='2').count()
    cela_c3 = bloco_c.filter(cela='3').count()
    cela_c4 = bloco_c.filter(cela='4').count()
    cela_c5 = bloco_c.filter(cela='5').count()
    cela_c6 = bloco_c.filter(cela='6').count()
    cela_c7 = bloco_c.filter(cela='7').count()

    cela_d1 = bloco_d.filter(cela='1').count()
    cela_d2 = bloco_d.filter(cela='2').count()
    cela_d3 = bloco_d.filter(cela='3').count()
    cela_d4 = bloco_d.filter(cela='4').count()
    cela_d5 = bloco_d.filter(cela='5').count()

    cela_e1 = bloco_e.filter(cela='1').count()
    cela_e2 = bloco_e.filter(cela='2').count()
    cela_e3 = bloco_e.filter(cela='3').count()
    cela_e4 = bloco_e.filter(cela='4').count()
    cela_e5 = bloco_e.filter(cela='5').count()
    cela_e6 = bloco_e.filter(cela='6').count()
    cela_e7 = bloco_e.filter(cela='7').count()
    

    # Carrega o histórico de alterações
    historico_alteracoes = HistoricoAlteracao.objects.all().order_by('-data_alteracao')

    # Paginação: 10 alterações por página
    paginator = Paginator(historico_alteracoes, 10)  # 10 itens por página
    page_number = request.GET.get('page')  # Obtém o número da página da URL
    page_obj = paginator.get_page(page_number)  # Pega as alterações da página solicitada
    

    # Passa as contagens e o histórico para o template
    return render(request, 'painel/index.html', {
        'total_pessoas': total_pessoas,
        'form': form,
        'total_saiu_temporariamente': total_saiu_temporariamente,  # Passando a variável para o template
        'total_albergado': total_albergado,  # Passando a variável de albergados
        'nomes_albergados': nomes_albergados,  # Passando os nomes dos albergados
        'porcentagem_cadastrados': porcentagem_cadastrados,
        'limite_maximo': limite_maximo,
        'bloco_a': bloco_a,
        'bloco_b': bloco_b,
        'bloco_c': bloco_c,
        'bloco_d': bloco_d,
        'bloco_e': bloco_e,
        'cela_1_a': cela_1_a,
        'cela_2_a': cela_2_a,
        'cela_3_a': cela_3_a,
        'cela_4_a': cela_4_a,
        'cela_5_a': cela_5_a,
        'cela_b1': cela_b1,
        'cela_b2': cela_b2,
        'cela_b3': cela_b3,
        'cela_b4': cela_b4,
        'cela_b5': cela_b5,
        'cela_c1': cela_c1,
        'cela_c2': cela_c2,
        'cela_c3': cela_c3,
        'cela_c4': cela_c4,
        'cela_c5': cela_c5,
        'cela_c6': cela_c6,
        'cela_c7': cela_c7,
        'cela_d1': cela_d1,
        'cela_d2': cela_d2,
        'cela_d3': cela_d3,
        'cela_d4': cela_d4,
        'cela_d5': cela_d5,
        'cela_e1': cela_e1,
        'cela_e2': cela_e2,
        'cela_e3': cela_e3,
        'cela_e4': cela_e4,
        'cela_e5': cela_e5,
        'cela_e6': cela_e6,
        'cela_e7': cela_e7,
        'historico_alteracoes': page_obj,
        'nomes_albergados': nomes_albergados,  # Passando a lista de nomes para o template
        'nomes_saiu_temporariamente': nomes_saiu_temporariamente,  # Passando os nomes
        'celas_nomes': celas_nomes,
        'eletronicos_por_cela': dict(eletronicos_por_cela),
    })

def editar_pessoa_index(request):
    if request.method == 'POST':
        pessoa_id = request.POST.get('pessoa_id')
        bloco = request.POST.get('bloco')
        cela = request.POST.get('cela')

        pessoa = get_object_or_404(Pessoa, id=pessoa_id)

        # Se o bloco e a cela são os mesmos, não atualiza e exibe mensagem
        if pessoa.bloco == bloco and pessoa.cela == cela:
            messages.info(request, f"Este interno já está na {bloco} - {cela}")
            return redirect('index')

        # Captura do valor antigo antes de atualizar
        valor_antigo = f"{pessoa.bloco} - {pessoa.cela}"

        # Inicializa a variável para o campo alterado
        campo_alterado = []

        # Verifica se o bloco foi alterado
        if pessoa.bloco != bloco:
            pessoa.bloco = bloco
            campo_alterado.append("Bloco")

        # Verifica se a cela foi alterada
        if pessoa.cela != cela:
            pessoa.cela = cela
            campo_alterado.append("Cela")

        # Atualiza a pessoa
        pessoa.save()

        # Registra no histórico a alteração
        HistoricoAlteracao.objects.create(
            pessoa=pessoa,
            usuario=request.user,
            campo_alterado=" e ".join(campo_alterado),
            valor_antigo=valor_antigo,
            valor_novo=f"{bloco} - {cela}",
            data_alteracao=timezone.now()
        )

        # Exibe as mensagens apropriadas
        if "Bloco" in campo_alterado and "Cela" in campo_alterado:
            messages.success(request, f"Interno movido com sucesso para {bloco}-{cela} !")
        elif "Bloco" in campo_alterado:
            messages.success(request, f"Interno movido com sucesso para Bloco {bloco} !")
        elif "Cela" in campo_alterado:
            messages.success(request, f"Interno movido com sucesso para a nova Cela {cela} !")

        return redirect('index')

    return redirect('index')




import base64
from django.template.loader import get_template
from django.http import HttpResponse
from weasyprint import HTML
from django.contrib.staticfiles import finders

@login_required
def gerar_pdf(request):
    # Usar finders.find para localizar o arquivo de imagem
    img_path = finders.find('imagens/parapdf.png')
    
    if not img_path:
        return HttpResponse('Imagem não encontrada', status=404)
    
    # Carregar a imagem e converter para base64
    with open(img_path, 'rb') as img_file:
        img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
    # Capturar o tempo de geração do PDF
    tempo_geracao = datetime.now().strftime('%d/%m/%Y %H:%M:%S')


    # Capturar o usuário que gerou o PDF
    usuario = request.user.username
    pessoas_list = Pessoa.objects.exclude(tem_transferencia_ativa=True).exclude(saiu_temporariamente=True).exclude(albergado=True).exclude(status__in=["inativo", "foragido"])
    total_pessoas = pessoas_list.count()
    total_saiu_temporariamente = Pessoa.objects.filter(saiu_temporariamente=True).count()
    total_albergado = Pessoa.objects.filter(albergado=True).count()
    total_horta = Pessoa.objects.filter(
        frentes_de_trabalho__frente_trabalho='horta',
        frentes_de_trabalho__status='ativo'
    ).exclude(saiu_temporariamente=True).exclude(albergado=True).count()

    total_piscicultura = Pessoa.objects.filter(
        frentes_de_trabalho__frente_trabalho='piscicultura',
        frentes_de_trabalho__status='ativo'
    ).exclude(saiu_temporariamente=True).exclude(albergado=True).count()

    total_minhocario = Pessoa.objects.filter(
        frentes_de_trabalho__frente_trabalho='minhocario',
        frentes_de_trabalho__status='ativo'
    ).exclude(saiu_temporariamente=True).exclude(albergado=True).count()

    total_limpeza = Pessoa.objects.filter(
        frentes_de_trabalho__frente_trabalho='limpeza',
        frentes_de_trabalho__status='ativo'
    ).exclude(saiu_temporariamente=True).exclude(albergado=True).count()

    total_manutencao = Pessoa.objects.filter(
        frentes_de_trabalho__frente_trabalho='manutencao',
        frentes_de_trabalho__status='ativo'
    ).exclude(saiu_temporariamente=True).exclude(albergado=True).count()

    total_fabrica_blocos = Pessoa.objects.filter(
        frentes_de_trabalho__frente_trabalho='fabrica_blocos',
        frentes_de_trabalho__status='ativo'
    ).exclude(saiu_temporariamente=True).exclude(albergado=True).count()

    total_croche = Pessoa.objects.filter(
        frentes_de_trabalho__frente_trabalho='croche',
        frentes_de_trabalho__status='ativo'
    ).exclude(saiu_temporariamente=True).exclude(albergado=True).count()

    total_digitalizador = Pessoa.objects.filter(
        frentes_de_trabalho__frente_trabalho='digitalizador',
        frentes_de_trabalho__status='ativo'
    ).exclude(saiu_temporariamente=True).exclude(albergado=True).count()

    total_bibliotecario = Pessoa.objects.filter(
        frentes_de_trabalho__frente_trabalho='bibliotecario',
        frentes_de_trabalho__status='ativo'
    ).exclude(saiu_temporariamente=True).exclude(albergado=True).count()

    total_facilitador = Pessoa.objects.filter(
        frentes_de_trabalho__frente_trabalho='facilitador',
        frentes_de_trabalho__status='ativo'
    ).exclude(saiu_temporariamente=True).exclude(albergado=True).count()

    total_servicos_gerais = Pessoa.objects.filter(
        frentes_de_trabalho__frente_trabalho='servicos_gerais',
        frentes_de_trabalho__status='ativo'
    ).exclude(saiu_temporariamente=True).exclude(albergado=True).count()


    # Contagem por programas de estudo, excluindo as pessoas que saíram temporariamente ou são albergados
    total_ibraema = Pessoa.objects.filter(estudando=Pessoa.Estudando.IBRAEMA).exclude(saiu_temporariamente=True).exclude(albergado=True).count()
    total_eja_i = Pessoa.objects.filter(estudando=Pessoa.Estudando.EJA_I).exclude(saiu_temporariamente=True).exclude(albergado=True).count()
    total_eja_ii = Pessoa.objects.filter(estudando=Pessoa.Estudando.EJA_II).exclude(saiu_temporariamente=True).exclude(albergado=True).count()
    total_eja_iii = Pessoa.objects.filter(estudando=Pessoa.Estudando.EJA_III).exclude(saiu_temporariamente=True).exclude(albergado=True).count()
    total_ensino_superior = Pessoa.objects.filter(estudando=Pessoa.Estudando.ENSINO_SUPERIOR).exclude(saiu_temporariamente=True).exclude(albergado=True).count()

    # Contagem de TVs e Rádios
    total_tv = Eletronico.objects.filter(tipo='tv').count()
    total_radio = Eletronico.objects.filter(tipo='radio').count()
    total_ventilador = Eletronico.objects.filter(tipo='ventilador').count()

    # Contagem de PDIs ativos (data_inicio <= agora e (data_fim é nula ou data_fim > agora))
    now = timezone.now()
    # PDIs ativos (exceto sobrestado)
    pdis_ativos = PDI.objects.filter(
        data_inicio__lte=now
    ).filter(
        Q(data_fim__isnull=True) | Q(data_fim__gt=now)
    ).exclude(resultado='sobrestado')

    # Quantitativos por natureza (apenas ativos)
    total_pdi_leve = pdis_ativos.filter(natureza='leve').count()
    total_pdi_media = pdis_ativos.filter(natureza='media').count()
    total_pdi_grave = pdis_ativos.filter(natureza='grave').count()

    # Quantitativos por resultado (apenas ativos, exceto sobrestado)
    total_pdi_andamento = pdis_ativos.filter(resultado='andamento').count()
    total_pdi_condenado = pdis_ativos.filter(resultado='condenado').count()

    # Quantitativo de sobrestados (independente de ativo ou não)
    total_pdi_sobrestado = PDI.objects.filter(resultado='sobrestado').count()
    # Sanções ativas (de acordo com a data de início e fim)
    sancoes_ativas = Sancao.objects.filter(
        data_inicio__lte=now
    ).filter(
        Q(data_fim__isnull=True) | Q(data_fim__gt=now)
    )

    # Quantitativos de sanções ativas por tipo
    total_sancao_sem_castelo = sancoes_ativas.filter(tipo='sem_castelo').count()
    total_sancao_sem_visita_intima = sancoes_ativas.filter(tipo='sem_visita_intima').count()
    total_sancao_sem_visita_social = sancoes_ativas.filter(tipo='sem_visita_social').count()
    # Quantidade de pessoas com pelo menos uma sanção ativa (conta apenas uma vez por pessoa)
    total_pessoas_com_sancao_ativa = sancoes_ativas.values('pessoa').distinct().count()

    total_trabalhando = (
            total_horta +
            total_piscicultura +
            total_minhocario +
            total_limpeza +
            total_manutencao +
            total_fabrica_blocos +
            total_croche +
            total_digitalizador +
            total_bibliotecario +
            total_facilitador +
            total_servicos_gerais
        )
    context = {
        'total_pessoas': total_pessoas,
        'total_saiu_temporariamente': total_saiu_temporariamente,
        'total_albergado': total_albergado,
        'img_base64': img_base64,  # Passar a imagem em base64 para o template

        # Bloco A
        'cela_1_a': Pessoa.objects.filter(bloco='A', cela='1').exclude(saiu_temporariamente=True).count(),
        'cela_2_a': Pessoa.objects.filter(bloco='A', cela='2').exclude(saiu_temporariamente=True).count(),
        'cela_3_a': Pessoa.objects.filter(bloco='A', cela='3').exclude(saiu_temporariamente=True).count(),
        'cela_4_a': Pessoa.objects.filter(bloco='A', cela='4').exclude(saiu_temporariamente=True).count(),
        'cela_5_a': Pessoa.objects.filter(bloco='A', cela='5').exclude(saiu_temporariamente=True).count(),


        # Bloco B
        'cela_b1': Pessoa.objects.filter(bloco='B', cela='1').exclude(saiu_temporariamente=True).count(),
        'cela_b2': Pessoa.objects.filter(bloco='B', cela='2').exclude(saiu_temporariamente=True).count(),
        'cela_b3': Pessoa.objects.filter(bloco='B', cela='3').exclude(saiu_temporariamente=True).count(),
        'cela_b4': Pessoa.objects.filter(bloco='B', cela='4').exclude(saiu_temporariamente=True).count(),
        'cela_b5': Pessoa.objects.filter(bloco='B', cela='5').exclude(saiu_temporariamente=True).count(),

        # Bloco C
        'cela_c1': Pessoa.objects.filter(bloco='C', cela='1').exclude(saiu_temporariamente=True).count(),
        'cela_c2': Pessoa.objects.filter(bloco='C', cela='2').exclude(saiu_temporariamente=True).count(),
        'cela_c3': Pessoa.objects.filter(bloco='C', cela='3').exclude(saiu_temporariamente=True).count(),
        'cela_c4': Pessoa.objects.filter(bloco='C', cela='4').exclude(saiu_temporariamente=True).count(),
        'cela_c5': Pessoa.objects.filter(bloco='C', cela='5').exclude(saiu_temporariamente=True).count(),
        'cela_c6': Pessoa.objects.filter(bloco='C', cela='6').exclude(saiu_temporariamente=True).count(),
        'cela_c7': Pessoa.objects.filter(bloco='C', cela='7').exclude(saiu_temporariamente=True).count(),

        # Bloco D
        'cela_d1': Pessoa.objects.filter(bloco='D', cela='1').exclude(saiu_temporariamente=True).count(),
        'cela_d2': Pessoa.objects.filter(bloco='D', cela='2').exclude(saiu_temporariamente=True).count(),
        'cela_d3': Pessoa.objects.filter(bloco='D', cela='3').exclude(saiu_temporariamente=True).count(),
        'cela_d4': Pessoa.objects.filter(bloco='D', cela='4').exclude(saiu_temporariamente=True).count(),
        'cela_d5': Pessoa.objects.filter(bloco='D', cela='5').exclude(saiu_temporariamente=True).count(),

        # Bloco E
        'cela_e1': Pessoa.objects.filter(bloco='E', cela='1').exclude(saiu_temporariamente=True).count(),
        'cela_e2': Pessoa.objects.filter(bloco='E', cela='2').exclude(saiu_temporariamente=True).count(),
        'cela_e3': Pessoa.objects.filter(bloco='E', cela='3').exclude(saiu_temporariamente=True).count(),
        'cela_e4': Pessoa.objects.filter(bloco='E', cela='4').exclude(saiu_temporariamente=True).count(),
        'cela_e5': Pessoa.objects.filter(bloco='E', cela='5').exclude(saiu_temporariamente=True).count(),
        'cela_e6': Pessoa.objects.filter(bloco='E', cela='6').exclude(saiu_temporariamente=True).count(),
        'cela_e7': Pessoa.objects.filter(bloco='E', cela='7').exclude(saiu_temporariamente=True).count(),

        # Frente de Trabalhos
        'total_horta': total_horta,
        'total_piscicultura': total_piscicultura,
        'total_minhocario': total_minhocario,
        'total_limpeza': total_limpeza,
        'total_manutencao': total_manutencao,
        'total_fabrica_blocos': total_fabrica_blocos,
        'total_croche': total_croche,
        'total_digitalizador': total_digitalizador,
        'total_bibliotecario': total_bibliotecario,
        'total_facilitador': total_facilitador,
        'total_servicos_gerais': total_servicos_gerais,
        'total_trabalhando': total_trabalhando,
        #total estudo
        'total_ibraema': total_ibraema,
        'total_eja_i': total_eja_i,
        'total_eja_ii': total_eja_ii,
        'total_eja_iii': total_eja_iii,
        'total_ensino_superior': total_ensino_superior,
        #total eletronico
        'total_tv': total_tv,
        'total_radio': total_radio,
        'total_ventilador': total_ventilador,
        'total_pdi_ativos': pdis_ativos.count(),
        'total_pdi_leve': total_pdi_leve,
        'total_pdi_media': total_pdi_media,
        'total_pdi_grave': total_pdi_grave,
        'total_pdi_andamento': total_pdi_andamento,
        'total_pdi_condenado': total_pdi_condenado,
        'total_pdi_sobrestado': total_pdi_sobrestado,
        # Sanções
        'total_sancoes_ativas': sancoes_ativas.count(),
        'total_sancao_sem_castelo': total_sancao_sem_castelo,
        'total_sancao_sem_visita_intima': total_sancao_sem_visita_intima,
        'total_sancao_sem_visita_social': total_sancao_sem_visita_social,
        # Pessoas com pelo menos uma sanção ativa
        'total_pessoas_com_sancao_ativa': total_pessoas_com_sancao_ativa,

        #tempor gracao pdf e usuario que gerou
        'tempo_geracao': tempo_geracao,
        'usuario': usuario


    }

    # Renderizar o template HTML
    template_path = 'pdf/quantitativogeral.html'
    template = get_template(template_path)
    html = template.render(context)

    # Gerar PDF com WeasyPrint
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Quantitativo_Geral_Upaca.pdf"'

    # Gerar PDF e enviar na resposta
    HTML(string=html).write_pdf(response)

    return response





@login_required
def adicionar_pessoa_view(request):
    if request.method == 'POST':
        form = PessoaForm(request.POST)
        
        # Verifique se o formulário é válido
        if form.is_valid():
            pessoa = form.save(commit=False)
            pessoa.status = 'ativo'  # Garantir que o status tenha um valor fixo
            pessoa.save()
            
            messages.success(request, "Cadastrado com sucesso!")  # Mensagem de sucesso
            return redirect('adicionar_pessoa')  # Redireciona para a página de adicionar pessoa
        else:
            messages.error(request, "Por favor, corrija os erros abaixo.")
            # Exibe erros de cada campo no console para facilitar a depuração
    else:
        form = PessoaForm()
    
    return render(request, 'painel/adicionar_pessoa.html', {'form': form})


from django.http import JsonResponse
from django.db.models import Q
from .models import Pessoa

def autocomplete_nome_view(request):
    query = request.GET.get('term', '')
    if query:
        pessoas = Pessoa.objects.filter(
            Q(nome_completo__icontains=query)
        ).values('nome_completo', 'status')[:10]

        resultados = []
        for pessoa in pessoas:
            resultados.append({
                'label': f"{pessoa['nome_completo']} ({pessoa['status']})",  # para exibir
                'value': pessoa['nome_completo'],  # valor real que deve ir para o input
                'status': pessoa['status']
            })

        return JsonResponse(resultados, safe=False)

    return JsonResponse([], safe=False)



@login_required
def remover_pessoa(request, id):
    pessoa = get_object_or_404(Pessoa, id=id)
    if request.method == 'POST':
        try:
            # Excluir a pessoa fisicamente após o histórico ser registrado
            pessoa.delete()
            
            messages.success(request, 'Pessoa excluida com Sucesso!')
        except Exception as e:
            messages.error(request, f'Ocorreu um erro ao tentar excluir a pessoa! {e}')
    return redirect('ver_tabela')  # Redireciona para a tabela após a remoção
@login_required

# Método para conceder o alvará
def conceder_alvara(request, id):
    pessoa = get_object_or_404(Pessoa, id=id)

    if request.method == 'POST':
        try:
            if pessoa.pd_is.filter(resultado="sobrestado").exists():
                messages.error(request, f'Você não pode conceder alvará para {pessoa.nome_completo}, pois ele está com PDI Sobrestado.')
                return redirect('ver_tabela')

            if pessoa.albergado:
                valor_antigo = "Albergado"
            else:
                valor_antigo = f"{pessoa.bloco} - {pessoa.cela}" if pessoa.bloco and pessoa.cela else "Sem Registro"

            valor_novo = 'inativo'
            valor_novo_historico = 'Alvará' if pessoa.status == 'ativo' else 'Alvará OK'

            # Registrar no histórico
            HistoricoAlteracao.objects.create(
                pessoa=pessoa,
                usuario=request.user,
                campo_alterado='Status',
                valor_antigo=valor_antigo,
                valor_novo=valor_novo_historico,
                data_alteracao=timezone.now()
            )

            # Limpar opções associadas
            if hasattr(pessoa, 'limpar_opcoes_associadas_para_alvara'):
                pessoa.limpar_opcoes_associadas_para_alvara()
            else:
                messages.error(request, f'Erro ao conceder alvará: método "limpar_opcoes_associadas_para_alvara" não encontrado.')
                return redirect('ver_tabela')

            pessoa.status = valor_novo
            pessoa.save()

            messages.success(request, f'Alvará concedido com sucesso! {pessoa.nome_completo} agora está {valor_novo}.')

            # 📩 Notificação simples
            grau = 'geral'
            mensagem = "Alvará concedido."

            # ✅ Criar notificação
            User = get_user_model()
            notificacao = Notificacao.objects.create(
                tipo='alvara',
                titulo=pessoa.nome_completo,
                mensagem=mensagem,
                pessoa=pessoa,
                criado_por=request.user,
                grau=grau
            )
            notificacao.usuarios.set(User.objects.all())

            # 📡 Enviar notificação via WebSocket
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'notifications_group',
                {
                    'type': 'send_notification',
                    'message': f'[ALVARÁ - {grau.upper()}] {notificacao.mensagem}'
                }
            )
            print("📡 Notificação enviada via WebSocket")

        except Exception as e:
            messages.error(request, f'Ocorreu um erro ao tentar conceder o alvará! {e}')

    return redirect('ver_tabela')




from datetime import date, datetime
from unidecode import unidecode
from datetime import timedelta
from django.utils.timezone import now
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta
from django.utils.timezone import now

@login_required
def ver_tabela_view(request):
    hoje = timezone.now().date()  # Garante que hoje seja sempre definido
    # Filtros e base da queryset (já existente)
    bloco_filter = request.GET.getlist('bloco')
    cela_filter = request.GET.getlist('cela')
    matricula = request.GET.get('matricula')
    # Outros filtros mantêm a mesma lógica
    escolaridade_filter = request.GET.get('escolaridade')
    estudando_filter = request.GET.get('estudando')
    frente_trabalho_filter = request.GET.get('frente_trabalho')
    ordenar_nome = request.GET.get('ordenar_nome')
    ordenar_bloco_cela = request.GET.get('ordenar_bloco_cela')
    nome_filter = request.GET.get('nome')
    saiu_temporariamente_filter = request.GET.get('saiu_temporariamente')
    albergado_filter = request.GET.get('albergado')
   
    faixa_etaria_filtro = request.GET.get('faixa_etaria')
    # **Novo filtro de status**
    status_filter = request.GET.get('status')

    pessoas_list = Pessoa.objects.exclude(
        transferencia__transferencia_ativa=True
    ).order_by('-created_at')




    # **Filtrar por status (Padrão: apenas "ativo")**
    if status_filter:
        pessoas_list = pessoas_list.filter(status=status_filter)
    else:
        pessoas_list = pessoas_list.filter(status="ativo")
    # Filtro de Bloco (aplicado mesmo sem cela)
    if bloco_filter:
        pessoas_list = pessoas_list.filter(bloco__in=bloco_filter)

    # Filtro de Cela (independente do bloco)
    if cela_filter:
        pessoas_list = pessoas_list.filter(cela__in=cela_filter)
    if escolaridade_filter:
        pessoas_list = pessoas_list.filter(escolaridade=escolaridade_filter)
    if estudando_filter:
        pessoas_list = pessoas_list.filter(estudando=estudando_filter)
    if frente_trabalho_filter:
        pessoas_list = pessoas_list.filter(
            frentes_de_trabalho__frente_trabalho=frente_trabalho_filter,
            frentes_de_trabalho__status='ativo'
        )


    filtros = Q()  # Inicializa a variável

    if nome_filter:
        busca = unidecode(nome_filter.strip().lower())
        filtros &= Q(nome_completo__icontains=busca) | Q(matricula__icontains=busca)

    if filtros:  # Aplica o filtro somente se houver algum critério
        pessoas_list = pessoas_list.filter(filtros)



    if faixa_etaria_filtro:
        if faixa_etaria_filtro == "18-20":
            data_max = hoje - timedelta(days=18 * 365)
            data_min = hoje - timedelta(days=20 * 365)
        elif faixa_etaria_filtro == "21-30":
            data_max = hoje - timedelta(days=21 * 365)
            data_min = hoje - timedelta(days=30 * 365)
        elif faixa_etaria_filtro == "31-59":
            data_max = hoje - timedelta(days=31 * 365)
            data_min = hoje - timedelta(days=59 * 365)
        elif faixa_etaria_filtro == "60+":
            data_max = hoje - timedelta(days=60 * 365)
            data_min = hoje - timedelta(days=200 * 365)  # Definir um valor alto para evitar None

        # Aplicando os filtros
        if data_max:
            pessoas_list = pessoas_list.filter(data_nascimento__lte=data_max)
        if data_min:
            pessoas_list = pessoas_list.filter(data_nascimento__gte=data_min)
    
  # Adicionar a frente de trabalho mais recente de cada pessoa
    pessoas_list = pessoas_list.prefetch_related(
        models.Prefetch(
            'frentes_de_trabalho',
            queryset=FrenteDeTrabalho.objects.filter(status='ativo').order_by('-data_inicio'),
            to_attr='frente_trabalho_ativa'
        )
    )
    # Filtro para "Saiu Temporariamente"
    if saiu_temporariamente_filter == 'on':
        pessoas_list = pessoas_list.filter(saiu_temporariamente=True)

    # Filtro para "Albergado"
    if albergado_filter == 'on':
        pessoas_list = pessoas_list.filter(albergado=True)
    
     # **Aplicar o filtro de status**
    if status_filter:
        pessoas_list = pessoas_list.filter(status=status_filter)

    # Ordenações combinadas
    order_fields = []
    if ordenar_bloco_cela == 'on':
        order_fields.extend(['bloco', 'cela'])
    if ordenar_nome:
        order_fields.append('nome_completo')
    if order_fields:
        pessoas_list = pessoas_list.order_by(*order_fields)

    hoje = timezone.now()  # Correto para comparação com DateTimeField

    for pessoa in pessoas_list:
        # Filtra apenas PDIs ativos dentro do intervalo de datas
        pdi_ativo = pessoa.pd_is.filter(
            Q(data_inicio__lte=hoje) & Q(data_fim__gte=hoje)
        )

        # Verifica se há algum PDI com resultado "Sobrestado"
        pdi_sobrestado = pessoa.pd_is.filter(resultado="sobrestado")

        if pdi_sobrestado.exists():
            pessoa.pdi_ativo = "Sobrestado"
        elif pdi_ativo.exists():
            pessoa.pdi_ativo = "PDI Ativo"
        else:
            pessoa.pdi_ativo = "Não Há"


    # Atualização do status com base em created_at
    for pessoa in pessoas_list:
        now = timezone.now()
        days_difference = (now - pessoa.created_at).days

        if days_difference == 0:
            pessoa.status_novo = 'Hoje'
        elif days_difference == 1:
            pessoa.status_novo = 'Ontem'
        else:
            pessoa.status_novo = None
       
       # Adicionar status de "Saiu Temporariamente"
    for pessoa in pessoas_list:
        pessoa.saiu_temporariamente_ativo = pessoa.saiu_temporariamente  # Pode ser True ou False
        # Adicionar flag de status
    
    for pessoa in pessoas_list:
        # Adicionando o filtro de sanções ativas
        pessoa.sancoes_ativas = pessoa.sancoes.filter(data_fim__gte=datetime.now())

         # Agora, dentro do loop, você pode acessar o histórico de alterações
        pessoa.historico = pessoa.historico_alteracoes.all().order_by('-data_alteracao')

    # Paginação
    paginator = Paginator(pessoas_list, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Calcular o número de pessoas que já foram exibidas
    start_index = (page_obj.number - 1) * 20
    for i, pessoa in enumerate(page_obj.object_list):
        pessoa.counter = start_index + i + 1

    return render(request, 'painel/ver_tabela.html', {
        'page_obj': page_obj,
        'bloco_filter': bloco_filter,
        'cela_filter': cela_filter,
        'escolaridade_filter': escolaridade_filter,
        'estudando_filter': estudando_filter,
        'frente_trabalho_filter': frente_trabalho_filter,
        'ordenar_nome': ordenar_nome,
        'ordenar_bloco_cela': ordenar_bloco_cela,
        'nome_filter': nome_filter,
        'pessoas_list': pessoas_list,
        'saiu_temporariamente': saiu_temporariamente_filter,
        'albergado_filter': albergado_filter,
        'start_index': start_index,
        'status_filter': status_filter,
        'matricula': matricula,
        'faixa_etaria_filtro': faixa_etaria_filtro,
    })



from django.db.models import Prefetch
@login_required
def exportar_tabela_pdf(request):
    # Pegando os filtros da URL
    user_name = request.user.username
    bloco_filter = request.GET.getlist('bloco')
    cela_filter = request.GET.getlist('cela')
    escolaridade_filter = request.GET.get('escolaridade')
    estudando_filter = request.GET.get('estudando')
    sancao_filter = request.GET.get('sancao')
    frente_trabalho_filter = request.GET.get('frente_trabalho')
    ordenar_nome = request.GET.get('ordenar_nome')
    ordenar_bloco_cela = request.GET.get('ordenar_bloco_cela')
    albergado_filter = request.GET.get('albergado')
    saiu_temporariamente_filter = request.GET.get('saiu_temporariamente')
    status_filter = request.GET.get('status')
    # Base da queryset excluindo pessoas com transferência ativa
    pessoas_list = Pessoa.objects.exclude(
        transferencia__transferencia_ativa=True
    )

    # Aplica o filtro de status
    if status_filter:
        pessoas_list = pessoas_list.filter(status=status_filter)
    
    # Aplica os filtros de albergado e saiu_temporariamente, se fornecidos
    if albergado_filter == 'on':
        pessoas_list = pessoas_list.filter(albergado=True)
    else:
        pessoas_list = pessoas_list.exclude(albergado=True)

    if saiu_temporariamente_filter == 'on':
        pessoas_list = pessoas_list.filter(saiu_temporariamente=True)
    else:
        pessoas_list = pessoas_list.exclude(saiu_temporariamente=True)

    # Aplicar outros filtros dinâmicos
    if bloco_filter:
        pessoas_list = pessoas_list.filter(bloco__in=bloco_filter)
    if cela_filter:
        pessoas_list = pessoas_list.filter(cela__in=cela_filter)
    if escolaridade_filter:
        pessoas_list = pessoas_list.filter(escolaridade=escolaridade_filter)
    if estudando_filter:
        pessoas_list = pessoas_list.filter(estudando=estudando_filter)
    if frente_trabalho_filter:
        pessoas_list = pessoas_list.filter(
            frentes_de_trabalho__frente_trabalho=frente_trabalho_filter,
            frentes_de_trabalho__status='ativo'
        )

    if sancao_filter:
        pessoas_list = pessoas_list.filter(sancoes__tipo=sancao_filter, sancoes__data_fim__isnull=True)


    pessoas_list = pessoas_list.prefetch_related(
        models.Prefetch(
            'frentes_de_trabalho',
            queryset=FrenteDeTrabalho.objects.filter(status='ativo').order_by('-data_inicio'),
            to_attr='frente_trabalho_ativa'
        )
    )

    # Ordenação
    order_fields = []
    if ordenar_bloco_cela == 'on':
        order_fields.extend(['bloco', 'cela'])
    if ordenar_nome == 'on':
        order_fields.append(Lower('nome_completo'))

    if order_fields:
        pessoas_list = pessoas_list.order_by(*order_fields)

    # Definindo margens ajustadas para A4
    margem_esquerda = 20
    margem_superior = 20
    margem_direita = 20
    margem_inferior = 70

    # Cria a resposta para o arquivo PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Lista do Sistema Upaca.pdf"'

    # Criação do canvas para o PDF com ajuste nas margens
    c = canvas.Canvas(response, pagesize=letter)
    largura_pagina, altura_pagina = letter

    # Definindo a posição inicial
    y_position = altura_pagina - margem_superior
    x_position = margem_esquerda

    # Filtros aplicados no topo do PDF
    filtros = []
    if bloco_filter:
        filtros.append(f"Bloco(s): {', '.join(set(bloco_filter))}")
    if cela_filter:
        filtros.append(f"Cela(s): {', '.join(set(cela_filter))}")
    if escolaridade_filter:
        filtros.append(f"Escolaridade: {escolaridade_filter}")
    if estudando_filter:
        filtros.append(f"Estudando: {estudando_filter}")
    if frente_trabalho_filter:
        filtros.append(f"Frente de Trabalho: {frente_trabalho_filter}")
    if albergado_filter:
        filtros.append(f"Albergados")
    if saiu_temporariamente_filter:
        filtros.append(f"Saidas Temporárias")
    if status_filter:
        filtros.append(f"{status_filter}")


    col_widths = [20, 10, 20, 180, 58, 65, 70, 65, 65]  # Ajuste nas larguras das colunas
    col_titles = ["", "B", "C", "Nome Completo", "Entrada", "Eletrônicos", "Escola", "Trabalhando", "Sanções"]

    # Desenha o cabeçalho na primeira página
    y_position = desenhar_cabecalho(c, y_position, largura_pagina, altura_pagina, filtros, col_titles, col_widths)

    # Definindo o tamanho da fonte para as linhas de dados
    c.setFont("Helvetica", 9)

    # Verifica se há pessoas para exibir
    if pessoas_list.exists():
        # Escreve os dados das pessoas filtradas
        for pessoa in pessoas_list:
            frente_trabalho_ativa = next(iter(pessoa.frentes_de_trabalho.all()), None)

            row_data = [
                pessoa.bloco if pessoa.bloco else 'Inativo',
                pessoa.cela if pessoa.cela else '',
                pessoa.nome_completo.upper()[:40],
                pessoa.data_entrada.strftime("%d/%m/%Y") if pessoa.data_entrada else 'N/A',
                '',  # Eletrônicos
                dict(Pessoa.Estudando.choices).get(pessoa.estudando, 'N/A'),
                dict(FrenteDeTrabalho.FRONTEIRAS_TRABALHO_CHOICES).get(
                    frente_trabalho_ativa.frente_trabalho, 'N/A'
                ) if frente_trabalho_ativa else 'N/A',
            ]


            # Desenha o quadrado (representando o índice)
            c.rect(x_position, y_position - 3, 10, 10)  # Desenha o quadrado
            c.drawString(x_position + 3, y_position, "")  # O número dentro do quadrado está vazio

            # Desenha os dados nas colunas seguintes
            for i, data in enumerate(row_data):
                if i == 0 or i == 1:  # Bloco e Cela
                    c.setFont("Helvetica-Bold", 8)
                elif i == 2:  # Nome completo
                    c.setFont("Helvetica-Bold", 7)  # Aqui define o tamanho desejado, ex: 10
                else:
                    c.setFont("Helvetica", 8)
                c.drawString(x_position + sum(col_widths[:i+1]), y_position, data)
                
            # Processamento de Eletrônicos
            initial_y_position = y_position
            eletrônicos = Eletronico.objects.filter(pessoa=pessoa)

            if eletrônicos.exists():
                x_offset = x_position + sum(col_widths[:5])
                for eletronico in eletrônicos:
                    if eletronico.tipo == 'tv':
                        img_path = finders.find('imagens/tv.png')
                    elif eletronico.tipo == 'radio':
                        img_path = finders.find('imagens/radio.png')
                    elif eletronico.tipo == 'ventilador':
                        img_path = finders.find('imagens/ventilador.png')
                    else:
                        img_path = ''
                    if img_path:
                        c.drawImage(img_path, x_offset, y_position - 3, width=12, height=12, mask='auto')
                        x_offset += 18
                y_position -= 8
            else:
                c.setFont("Helvetica", 8)
                c.drawString(x_position + sum(col_widths[:5]), y_position, "Não há")
                y_position -= 8

            y_position = initial_y_position

            # Processamento das sanções
            sancao_atual = Sancao.objects.filter(pessoa=pessoa, data_fim__gt=datetime.now())

            if sancao_atual.exists():
                c.setFont("Helvetica", 8)
                for sancao in sancao_atual:
                    c.drawString(
                        x_position + sum(col_widths[:-1]),
                        y_position,
                        f"{sancao.tipo.replace('_', ' ').capitalize()}"
                    )
                    y_position -= 8.5
            else:
                c.setFont("Helvetica", 8)
                c.drawString(
                    x_position + sum(col_widths[:-1]),
                    y_position,
                    "Não há"
                )
                y_position -= 8

            c.setStrokeColorRGB(0.4, 0.4, 0.4)
            c.setLineWidth(0.3)
            c.line(x_position, y_position, x_position + 558, y_position)

            y_position -= 13

            if y_position < 40:
                c.showPage()
                y_position = altura_pagina - margem_superior
                y_position = desenhar_cabecalho(c, y_position, largura_pagina, altura_pagina, filtros, col_titles, col_widths)

        y_position = adicionar_rodape(c, y_position, user_name)
    else:
        c.drawString(x_position + 5, y_position, "Não há dados para exibir")

    c.showPage()
    c.save()
    return response



from datetime import datetime

def adicionar_rodape(c, y_position, user_name):
    # Obtendo a data e hora de geração
    data_geracao = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    # Obtendo a largura da página
    page_width, _ = letter  # Para uma página de tamanho carta (8.5 x 11)
    
    # Calcular a posição do canto direito
    margin = 43  # Margem para afastar o texto da borda direita
    x_position = page_width - margin
    
    # Adicionando o texto no rodapé
    c.setFont("Helvetica", 9)
    c.drawRightString(x_position, y_position, f"Gerado por: {user_name} | Data: {data_geracao}")
    y_position -= 15  # Ajuste de posição para o rodapé

    return y_position


def desenhar_cabecalho(c, y_position, largura_pagina,   altura_pagina, filtros, col_titles, col_widths):
    margem_superior = 20
    y_position -= 70
    
    # Definindo o tamanho da logo
    logo_path = "static/imagens/parapdf.png"
    logo_largura = 75  # Largura da logo
    logo_altura = 75   # Altura da logo
    
    # Calculando a posição central para logo e título, mas deslocando um pouco para a esquerda
    total_width = logo_largura + 10 + c.stringWidth("Tabela de Internos / UPACA", "Helvetica-Bold", 16)
    central_x = (largura_pagina - total_width) / 3 - 30  # Subtraindo 20 pixels para mover um pouco mais para a esquerda
    
    # Posição da logo
    logo_x = central_x
    c.drawImage(logo_path, logo_x, y_position, width=logo_largura, height=logo_altura)
    
    # Posição do título, que vem depois da logo
    title_text = "Lista do Sistema de Inteligência - UPACA"
    c.setFont("Helvetica-Bold", 16)
    title_x = logo_x + logo_largura + 10 + 8  # Adicionando 8 pixels para mover para a direita
    c.drawString(title_x, y_position + logo_altura / 2 - 8, title_text)

    
    y_position -= 1  # Ajustando o espaçamento após o título
    # Subtítulo logo abaixo
    c.setFont("Helvetica", 10)
    subtitle_text = "Unidade Prisional de Ressocialização de Açailândia"
    subtitle_width = c.stringWidth(subtitle_text, "Helvetica", 10)
    c.drawString((largura_pagina - subtitle_width) / 2, y_position, subtitle_text)
    y_position -= 10
    
    # Subtítulo logo abaixo
    c.setFont("Helvetica", 10)
    subtitle_text = "Relatório interno personalizado"
    subtitle_width = c.stringWidth(subtitle_text, "Helvetica", 10)
    c.drawString((largura_pagina - subtitle_width) / 2, y_position, subtitle_text)
    y_position -= 40  # Ajustando o espaçamento após o subtítulo

    # Filtros aplicados no topo do PDF
    c.setFont("Helvetica", 9)
    filtro_texto = "Filtros Aplicados: "
    if filtros:
        filtro_texto += ', '.join(filtros)
    else:
        filtro_texto += "Nenhum filtro aplicado"
    c.drawString(20, y_position, filtro_texto)
    y_position -= 20

    # Escreve os cabeçalhos com negrito
    c.setFont("Helvetica-Bold", 9)
    for i, title in enumerate(col_titles):
        c.drawString(20 + sum(col_widths[:i]), y_position, title)

    y_position -= 12

    # Linha de separação após os cabeçalhos
    c.setStrokeColorRGB(0.6, 0.6, 0.6)  # A cor foi ajustada para mais escura
    c.setLineWidth(0.5)
    c.line(20, y_position, 578, y_position)

    # Adiciona um espaço extra após a linha
    y_position -= 15

    # Após a linha de separação, mudamos a fonte para não negrito
    c.setFont("Helvetica", 9)

    return y_position


from .models import PDI
from .forms import PDIForm


def editar_pessoa(request, id):
    pessoa = get_object_or_404(Pessoa, id=id)
    form = PessoaForm(request.POST or None, instance=pessoa)
    transferencia = Transferencia.objects.filter(pessoa=pessoa).first()
    transferencia_form = TransferenciaForm(request.POST or None, instance=transferencia) if transferencia else TransferenciaForm(request.POST or None)
    
    sancoes = {
        'sem_castelo': pessoa.sancoes.filter(tipo='sem_castelo').first(),
        'sem_visita_intima': pessoa.sancoes.filter(tipo='sem_visita_intima').first(),
        'sem_visita_social': pessoa.sancoes.filter(tipo='sem_visita_social').first(),
        'isolamento_preventivo': pessoa.sancoes.filter(tipo='isolamento_preventivo').first(),
        'isolamento_reflexao': pessoa.sancoes.filter(tipo='isolamento_reflexao').first(),
    }

    historico = pessoa.historico_alteracoes.all().order_by('-data_alteracao')



    if request.method == 'POST':
        transferencia_ativa = request.POST.get('transferencia_ativa') == 'on'

        # Processando o formulário de pessoa
        if form.is_valid():
            pessoa = form.save(commit=False)
            pessoa.tem_transferencia_ativa = transferencia_ativa
            pessoa.save()

            # Histórico de alterações (bloco e cela)
            if not transferencia_ativa:  # Evitar registrar alterações de bloco/cela durante a transferência
                # Armazenar as modificações de bloco e cela em listas separadas
                

                modificacoes = []

                # Percorrendo as mudanças de bloco e cela
                for campo in ['bloco', 'cela']:
                    valor_novo = getattr(pessoa, campo)
                    valor_antigo = form.initial.get(campo)

                    if valor_novo != valor_antigo:
                        # Atribuindo nomes amigáveis para os campos
                        nome_campo = 'Bloco' if campo == 'bloco' else 'Cela'
                        
                        # Armazenar cada modificação separada para uso posterior
                        modificacoes.append({
                            'nome_campo': nome_campo,
                            'valor_antigo': str(valor_antigo) if valor_antigo else 'None',
                            'valor_novo': str(valor_novo) if valor_novo else 'None'
                        })

                # Se houver modificações em bloco ou cela, crie um único registro no histórico
                if modificacoes:
                    # Variáveis para armazenar as abreviações para "Antes" e "Agora"
                    abreviacao_antes_bloco = f"{form.initial.get('bloco')[0]} - {form.initial.get('cela')}" if form.initial.get('bloco') and form.initial.get('cela') else f"{pessoa.bloco[0]} - {pessoa.cela}"
                    abreviacao_antes_cela = f"{form.initial.get('bloco')[0]} - {form.initial.get('cela')}" if form.initial.get('cela') else f"{pessoa.bloco[0]} - {pessoa.cela}"

                    abreviacao_agora_bloco = f"{pessoa.bloco[0]} - {pessoa.cela}"
                    abreviacao_agora_cela = f"{pessoa.bloco[0]} - {pessoa.cela}"

                    acao_modificada = ""

                    # Se ambos os campos foram alterados, combinamos as abreviações
                    if len(modificacoes) > 1:
                        acao_modificada = 'Bloco e Cela'
                        # Certificando-se de mostrar as abreviações de bloco e cela apenas uma vez
                        abreviacao_antes = f"{form.initial.get('bloco')[0]} - {form.initial.get('cela')}" if form.initial.get('bloco') else f"{pessoa.bloco[0]} - {pessoa.cela}"
                        abreviacao_agora = f"{pessoa.bloco[0]} - {pessoa.cela}"
                    # Se apenas o Bloco foi alterado
                    elif 'bloco' in [mod['nome_campo'].lower() for mod in modificacoes]:
                        acao_modificada = 'Bloco'
                        abreviacao_antes = f"{form.initial.get('bloco')[0]} - {form.initial.get('cela')}" if form.initial.get('bloco') else f"{pessoa.bloco[0]} - {pessoa.cela}"
                        abreviacao_agora = f"{pessoa.bloco[0]} - {pessoa.cela}"
                    # Se apenas a Cela foi alterada
                    elif 'cela' in [mod['nome_campo'].lower() for mod in modificacoes]:
                        acao_modificada = 'Cela'
                        abreviacao_antes = f"{form.initial.get('bloco')[0]} - {form.initial.get('cela')}" if form.initial.get('cela') else f"{pessoa.bloco[0]} - {pessoa.cela}"
                        abreviacao_agora = f"{pessoa.bloco[0]} - {pessoa.cela}"

                    # Criando um único registro no histórico com as modificações
                    HistoricoAlteracao.objects.create(
                        pessoa=pessoa,
                        usuario=request.user,
                        campo_alterado=acao_modificada,  # Mostrando "Bloco" ou "Cela" ou "Bloco e Cela"
                        valor_antigo=abreviacao_antes,   # Exibindo as abreviações de bloco e cela antes
                        valor_novo=abreviacao_agora,     # Exibindo as abreviações de bloco e cela agora
                        data_alteracao=timezone.now()
                    )


            # Gerenciamento de Transferência
            if transferencia_ativa and not transferencia:
                transferencia = Transferencia.objects.create(
                    pessoa=pessoa,
                    penitenciaria_destino=request.POST.get('penitenciaria_destino', ''),
                    data_transferencia=request.POST.get('data_transferencia', None),
                    justificativa=request.POST.get('justificativa', ''),
                    transferencia_ativa=transferencia_ativa
                )
                
                destino = request.POST.get('penitenciaria_destino', 'Não Definido')
                notificar_transferencia(pessoa, request.user, destino)

            elif transferencia_ativa and transferencia_form.is_valid():
                transferencia = transferencia_form.save(commit=False)
                transferencia.pessoa = pessoa
                transferencia.save()

                destino = transferencia.penitenciaria_destino
                notificar_transferencia(pessoa, request.user, destino)
                


            # Histórico de transferência
            if transferencia_ativa:
                campo = 'penitenciaria_destino'
                valor_novo = getattr(transferencia, campo)
                valor_antigo = transferencia_form.initial.get(campo)
                if valor_novo != valor_antigo:
                    HistoricoAlteracao.objects.create(
                        pessoa=transferencia.pessoa,
                        usuario=request.user,
                        campo_alterado='Transferido',
                        valor_antigo=str(valor_antigo) if valor_antigo else 'UPACA',
                        valor_novo=str(valor_novo) if valor_novo else 'N/A',
                        data_alteracao=timezone.now()
                    )

            # Processando as sanções disciplinares
            tipos_sancao = ['sem_castelo', 'sem_visita_intima', 'sem_visita_social', 'isolamento_preventivo', 'isolamento_reflexao']
            for tipo in tipos_sancao:
                sancao_ativada = request.POST.get(f'sancao_{tipo}_{pessoa.id}') == 'on'
                if sancao_ativada:
                    form_data = {
                        'tipo': tipo,
                        'descricao': request.POST.get(f'descricao_sancao_{tipo}_{pessoa.id}', '').strip(),
                        'data_inicio': request.POST.get(f'data_inicio_{tipo}_{pessoa.id}'),
                        'data_fim': request.POST.get(f'data_fim_{tipo}_{pessoa.id}')
                    }

                    sancao_existente = Sancao.objects.filter(pessoa=pessoa, tipo=tipo).first()
                    if sancao_existente:
                        sancao_existente.descricao = form_data['descricao']
                        sancao_existente.data_inicio = form_data['data_inicio']
                        sancao_existente.data_fim = form_data['data_fim']
                        sancao_existente.save()
                        messages.success(request, f'Sanção "{tipo}" atualizada para {pessoa.nome_completo}')
                    else:
                        sancao_form = SancaoForm(form_data)
                        if sancao_form.is_valid():
                            Sancao.objects.create(
                                pessoa=pessoa,
                                tipo=tipo,
                                descricao=form_data['descricao'],
                                data_inicio=form_data['data_inicio'],
                                data_fim=form_data['data_fim']
                            )
                            messages.success(request, f'Sanção "{tipo}" criada para {pessoa.nome_completo}')
                        else:
                            messages.error(request, f'Erro ao processar a sanção "{tipo}". Por favor, verifique os campos.')      



            # Mensagem final para indicar sucesso
            messages.success(request, 'Informações atualizadas com sucesso!')
            return redirect('ver_tabela')

    return render(request, 'painel/ver_tabela.html', {
        'form': form,
        'pessoa': pessoa,
        'transferencia_form': transferencia_form,
        'sancoes': sancoes,
        'historico': historico
})


from notification.models import Notificacao
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
User = get_user_model()

def notificar_transferencia(pessoa, usuario_responsavel, destino):
    mensagem_transferencia = f"Foi transferido para: {destino}."
    
    notificacao_transferencia = Notificacao.objects.create(
        tipo='transferencia',
        titulo=pessoa.nome_completo,  # nome no título
        mensagem=mensagem_transferencia,
        pessoa=pessoa,
        criado_por=usuario_responsavel,
        grau='geral'
    )
    
    notificacao_transferencia.usuarios.set(User.objects.all())
    
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'notifications_group',
        {
            'type': 'send_notification',
            'message': f"[TRANSFERÊNCIA - GERAL] {mensagem_transferencia}"
        }
    )





def tabela_transferidos_view(request):
    # Filtros
    pessoa = request.GET.get('pessoa', '')
    penitenciaria_destino = request.GET.get('penitenciaria_destino', '')  # Corrigido
    status = request.GET.get('status', '')
    data_inicio = request.GET.get('data_inicio', '')
    data_fim = request.GET.get('data_fim', '')

    # Filtro inicial
    transferencias_ativas = Transferencia.objects.all()

    # Filtro por pessoa
    if pessoa:
        transferencias_ativas = transferencias_ativas.filter(pessoa__nome_completo__icontains=pessoa)

    # Filtro por penitenciária destino
    if penitenciaria_destino:
        transferencias_ativas = transferencias_ativas.filter(penitenciaria_destino__icontains=penitenciaria_destino)  # Corrigido

    # Filtro por status (Ativa/Inativa)
    if status:
        status_value = True if status == 'ativa' else False
        transferencias_ativas = transferencias_ativas.filter(transferencia_ativa=status_value)

    # Filtro por data de transferência
    if data_inicio:
        transferencias_ativas = transferencias_ativas.filter(data_transferencia__gte=data_inicio)

    if data_fim:
        transferencias_ativas = transferencias_ativas.filter(data_transferencia__lte=data_fim)

    # Ordenação por data de criação
    transferencias_ativas = transferencias_ativas.order_by('-created_at')

    # Paginação
    paginator = Paginator(transferencias_ativas, 20)
    page_number = request.GET.get('page', 1)
    try:
        page_obj = paginator.get_page(page_number)
    except EmptyPage:
        page_obj = paginator.get_page(paginator.num_pages)

    context = {
        'page_obj': page_obj,
        'pessoa': pessoa,
        'penitenciaria_destino': penitenciaria_destino,
        'status': status,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
    }

    return render(request, 'painel/tabela_transferidos.html', context)




from django.core.paginator import Paginator

def ver_tabela_sancoes_view(request):
    # Filtrar sanções ativas por padrão
    sancoes = Sancao.objects.select_related('pessoa').filter(tipo__isnull=False)

    # Ordenando por data de início (ou outro campo relevante)
    sancoes = sancoes.order_by('data_inicio')

    # Filtro de sanções finalizadas (se o checkbox for marcado)
    if 'finalizada' in request.GET:
        sancoes = sancoes.filter(data_fim__lt=timezone.now())  # Filtra sanções finalizadas
    else:
        sancoes = sancoes.filter(data_fim__gt=timezone.now())  # Filtra sanções ativas

    # Filtro pelo tipo de sanção, se fornecido
    tipo = request.GET.get('tipo')
    if tipo:
        sancoes = sancoes.filter(tipo=tipo)

    # Filtro por nome da pessoa
    nome = request.GET.get('nome')
    if nome:
        sancoes = sancoes.filter(pessoa__nome_completo__icontains=nome)

    # Filtro por data de início
    data_inicio = request.GET.get('data_inicio')
    if data_inicio:
        data_inicio = timezone.datetime.strptime(data_inicio, "%Y-%m-%d").date()
        sancoes = sancoes.filter(data_inicio__gte=data_inicio)

    # Filtro por data de fim
    data_fim = request.GET.get('data_fim')
    if data_fim:
        data_fim = timezone.datetime.strptime(data_fim, "%Y-%m-%d").date()
        sancoes = sancoes.filter(data_fim__lte=data_fim)

    # Paginador
    paginator = Paginator(sancoes, 10)  # 10 sanções por página
    page_number = request.GET.get('page')  # Obtém o número da página da query string
    page_obj = paginator.get_page(page_number)  # Obtém a página com os objetos

    # Passar os tipos de sanção para o template
    sancao_tipo_choices = dict(Sancao.TIPOS_SANCAO)

    # Processar os dados detalhados
    sancoes_detalhadas = []
    for sancao in page_obj:
        if sancao.data_inicio and sancao.data_fim:
            dias_aplicados = (sancao.data_fim - sancao.data_inicio).days
            if dias_aplicados < 0:
                dias_aplicados = "Data inválida"
            
            tempo_restante = sancao.data_fim - timezone.now()
            
            if tempo_restante.total_seconds() > 0:
                dias = tempo_restante.days
                horas, resto = divmod(tempo_restante.seconds, 3600)
                minutos, segundos = divmod(resto, 60)
                tempo_formatado = f"{dias} dias, {horas} horas, {minutos} minutos, {segundos} segundos restantes"
            else:
                tempo_formatado = "Sanção finalizada"
            
            if sancao.data_inicio > timezone.now():
                status = "A iniciar"
            elif tempo_restante.total_seconds() > 0:
                status = "Ativa"
            else:
                status = "Finalizada"
            
            sancoes_detalhadas.append({
                'sancao': sancao,
                'dias_aplicados': dias_aplicados,
                'tempo_restante': tempo_formatado,
                'terminou': tempo_restante.total_seconds() <= 0,
                'status': status
            })
        else:
            sancoes_detalhadas.append({
                'sancao': sancao,
                'dias_aplicados': "Data inválida",
                'tempo_restante': "Data inválida",
                'terminou': False,
                'status': "Finalizada"
            })

    return render(request, 'painel/tabela_sancao_disciplinar.html', {
        'sancoes_detalhadas': sancoes_detalhadas,
        'sancao_tipo_choices': sancao_tipo_choices,  # Passando os tipos de sanção para o template
        'page_obj': page_obj,  # Passando a página atual para o template
    })





# -------------------------------------------------
#             PARA ATUZALIZAR O AJAX DO TEMPORIZADOR DA PAGINA DE SANÇÃO DISCIPLINAR, OU SEJA MOSTRA O TEMPO ACABANDO EM TEMPO REAL                             
# --------------------------------------------------
from django.http import JsonResponse
from django.utils import timezone
from .models import Sancao

def atualizar_tempos_restantes_view(request):
    sancoes_ativas = Sancao.objects.filter(data_fim__isnull=False)
    sancoes_data = []

    for sancao in sancoes_ativas:
        tempo_restante = sancao.data_fim - timezone.now()

        if tempo_restante.total_seconds() > 0:
            dias = tempo_restante.days
            horas, resto = divmod(tempo_restante.seconds, 3600)
            minutos, segundos = divmod(resto, 60)
            tempo_formatado = f"{dias} dias, {horas} horas, {minutos} minutos, {segundos} segundos restantes"
        else:
            tempo_formatado = "Sanção finalizada"

        sancoes_data.append({'id': sancao.id, 'tempo_restante': tempo_formatado})

    return JsonResponse({'sancoes': sancoes_data})

    
    
    
def apagar_sancao_view(request, sancao_id):
    # Obter a sanção pelo ID
    sancao = get_object_or_404(Sancao, id=sancao_id)

    # Apagar a sanção
    sancao.delete()

    # Adicionar uma mensagem de sucesso
    messages.success(request, 'A sanção foi apagada com sucesso.')

    # Redirecionar de volta para a tabela de sanções
    return redirect('ver_tabela_sancoes')  



def tabela_eletronico(request):
    # Inicializando a queryset de eletrônicos e ordenando pela data de entrada de forma decrescente
    eletronicos = Eletronico.objects.all().order_by('-data_entrada')

    # Calcular o próximo ID
    ultimo_eletronico = Eletronico.objects.all().order_by('id').last()
    proximo_id = ultimo_eletronico.id + 1 if ultimo_eletronico else 1

    # Se o formulário de filtro for enviado via GET
    if request.method == 'GET':
        tipo = request.GET.get('tipo')
        pessoa = request.GET.get('pessoa')
        data_entrada = request.GET.get('data_entrada')
        id_eletronico = request.GET.get('id')  # Buscar ID do eletrônico

        # Aplicando os filtros, se eles forem fornecidos
        if tipo:
            eletronicos = eletronicos.filter(tipo=tipo)
        if pessoa:
            eletronicos = eletronicos.filter(pessoa__nome_completo__icontains=pessoa)
        if data_entrada:
            try:
                data_entrada = datetime.strptime(data_entrada, '%Y-%m-%d')
                eletronicos = eletronicos.filter(data_entrada=data_entrada)
            except ValueError:
                messages.error(request, "Formato de data inválido!")
                return redirect('tabela-eletronico')
        if id_eletronico:  # Filtra pelo ID do eletrônico, se fornecido
            try:
                id_eletronico = int(id_eletronico)
                eletronicos = eletronicos.filter(id=id_eletronico)
            except ValueError:
                messages.error(request, "ID inválido! Somente números são permitidos.")
                return redirect('tabela-eletronico')

    # Filtro adicional: Exclui eletrônicos cujas pessoas têm transferência ativa
    eletronicos = eletronicos.exclude(pessoa__transferencia__transferencia_ativa=True)

    # Paginação
    paginator = Paginator(eletronicos, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    pessoas = Pessoa.objects.all()

    # Se o formulário para cadastrar eletrônico for enviado via POST
    if request.method == 'POST':
        form = EletronicoForm(request.POST, request.FILES)
        if form.is_valid():
            # Cria o objeto sem salvar no banco ainda
            eletronico = form.save(commit=False)
            eletronico.save()  # Agora o ID é gerado pelo banco de dados

            messages.success(request, f"Eletrônico cadastrado com sucesso! ID: {eletronico.id}")
            return redirect('tabela-eletronico')
        else:
            messages.error(request, "Erro ao cadastrar o eletrônico.")
    else:
        form = EletronicoForm()

    # Passando o próximo ID para o template
    context = {
        'eletronicos': page_obj,
        'form': form,
        'form_errors': form.errors,
        'pessoas': pessoas,
        'proximo_id': proximo_id,  # Passa o próximo ID para o template
    }

    return render(request, 'painel/tabela_eletronico.html', context)


from django.http import JsonResponse
from django.db.models import Q

def pessoa_search(request):
    q = request.GET.get('q', '').strip()
    
    if not q:
        return JsonResponse([], safe=False)
    
    pessoas = Pessoa.objects.filter(
        Q(nome_completo__icontains=q) | Q(matricula__icontains=q)
    ).exclude(
        transferencia__transferencia_ativa=True
    ).exclude(
        status__in=['inativo', 'foragido']
    ).distinct()[:10]

    results = [{
        'id': pessoa.id,
        'nome_completo': pessoa.nome_completo,
        'matricula': pessoa.matricula or '-',
        'bloco': pessoa.bloco or '-',
        'cela': pessoa.cela or '-'
    } for pessoa in pessoas]

    return JsonResponse(results, safe=False)


def excluir_eletronico(request, id):
    eletronico = get_object_or_404(Eletronico, id=id)
    
    if request.method == 'POST':
        # Excluir o arquivo de nota fiscal, se existir
        if eletronico.nova_fiscal:
            # Checa se o arquivo existe e exclui
            file_path = eletronico.nova_fiscal.path
            if os.path.exists(file_path):
                os.remove(file_path)
        
        # Excluir o objeto Eletronico
        eletronico.delete()
        messages.success(request, "Eletrônico excluído com sucesso!")
        return redirect('tabela-eletronico')
    
    return redirect('tabela-eletronico')

def transferir_eletronico(request, id):
    eletronico = get_object_or_404(Eletronico, id=id)
    
    if request.method == 'POST':
        nova_pessoa_id = request.POST.get('nova_pessoa')
        nova_pessoa = get_object_or_404(Pessoa, id=nova_pessoa_id)

        # Verificar se a nova pessoa já tem um eletrônico do mesmo tipo
        if nova_pessoa.eletronicos.filter(tipo=eletronico.tipo).exists():
            messages.error(request, f"A pessoa já possui um eletrônico do tipo {eletronico.get_tipo_display()}. A transferência não pode ser realizada.")
            return redirect('tabela-eletronico')  # Redireciona sem fazer a transferência

        # Caso a verificação passe, realiza a transferência
        eletronico.pessoa = nova_pessoa
        eletronico.save()
        
        messages.success(request, "Eletrônico transferido com sucesso!")
        return redirect('tabela-eletronico')
    
    return redirect('tabela-eletronico')



def arquivos_view(request):
    
    return render(request, 'pdf/quantitativogeral.html')


def informacao_view(request):
    return render(request, 'painel/informacao.html')


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models.functions import Lower
from django.core.paginator import Paginator
from django.utils import timezone
from django.contrib.auth import get_user_model

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import PDI, Pessoa
from .forms import PDIForm
from notification.models import Notificacao  # ✅ Import correto do modelo Notificacao

def tabela_e_aplicar_pdi_view(request, pdi_id=None):
    pd_is = PDI.objects.all().order_by('-id')
    pessoas = Pessoa.objects.all()

    filtros = {
        'pessoa': request.GET.get('pessoa'),
        'natureza': request.GET.get('natureza'),
        'descricao': request.GET.get('descricao'),
        'data_inicio': request.GET.get('data_inicio'),
        'data_fim': request.GET.get('data_fim'),
        'resultado': request.GET.get('resultado'),
        'ordenar_por_letra': request.GET.get('ordenar_por_letra'),
        'status_pdi': request.GET.get('status_pdi'),
        'ordenar_por_expiracao': request.GET.get('ordenar_por_expiracao'),
    }

    if filtros['pessoa']:
        pd_is = pd_is.filter(pessoa__nome_completo__icontains=filtros['pessoa'])
    if filtros['natureza']:
        pd_is = pd_is.filter(natureza=filtros['natureza'])
    if filtros['descricao']:
        pd_is = pd_is.filter(descricao__icontains=filtros['descricao'])
    if filtros['resultado']:
        pd_is = pd_is.filter(resultado=filtros['resultado'])
    if filtros['ordenar_por_letra'] == "1":
        pd_is = pd_is.order_by(Lower('pessoa__nome_completo'))

    if filtros['status_pdi'] == "expirado":
        pd_is = pd_is.filter(data_fim__lt=timezone.now())
    elif filtros['status_pdi'] == "em_vigor":
        pd_is = pd_is.filter(data_fim__gte=timezone.now())

    if filtros['ordenar_por_expiracao'] == "1":
        pd_is = sorted(pd_is, key=lambda pdi: (pdi.data_fim - timezone.now()).days if pdi.data_fim else float('inf'))

    try:
        if filtros['data_inicio']:
            filtros['data_inicio'] = timezone.datetime.strptime(filtros['data_inicio'], "%Y-%m-%dT%H:%M")
        if filtros['data_fim']:
            filtros['data_fim'] = timezone.datetime.strptime(filtros['data_fim'], "%Y-%m-%dT%H:%M")
    except ValueError:
        messages.error(request, "Formato de data inválido.")
        return redirect('tabela_pdi')

    paginator = Paginator(pd_is, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    def calcular_diferença(data_inicio, data_fim):
        if not data_fim:
            return 0, 0
        diff = data_fim - data_inicio
        meses = diff.days // 30
        dias = diff.days % 30
        return meses, dias

    def calcular_dias_restantes(data_fim):
        if not data_fim:
            return 'Não definido'
        data_fim = timezone.make_aware(data_fim) if data_fim.tzinfo is None else data_fim
        dias_restantes = (data_fim - timezone.now()).days
        if dias_restantes > 0:
            return f"{dias_restantes} dias restantes"
        elif dias_restantes == 0:
            return "Expira Hoje"
        return f"Expirou há {abs(dias_restantes)} dias"

    pd_is_info = [
        {
            'pdi': pdi,
            'meses_aplicados': calcular_diferença(pdi.data_inicio, pdi.data_fim)[0],
            'dias_aplicados': calcular_diferença(pdi.data_inicio, pdi.data_fim)[1],
            'dias_restantes': calcular_dias_restantes(pdi.data_fim),
        }
        for pdi in page_obj
    ]

    pdi = get_object_or_404(PDI, id=pdi_id) if pdi_id else None

    if request.method == "POST":
        form = PDIForm(request.POST, instance=pdi)
        if form.is_valid():
            resultado_anterior = pdi.resultado if pdi else None
            print("📌 Resultado anterior:", resultado_anterior)
            novo_pdi = form.save()
            print("📌 Resultado novo (salvo):", novo_pdi.resultado)

            if resultado_anterior != 'condenado' and novo_pdi.resultado == 'condenado':
                print("✅ Condição para notificação satisfeita!")

                frente_ativa = novo_pdi.pessoa.frentes_de_trabalho.filter(status='ativo').first()

                if frente_ativa:
                    grau = 'importante'
                    mensagem = (
                        f"Foi aplicada penalidade disciplinar de natureza {novo_pdi.get_natureza_display().lower()}. "
                        f"Possui frente de trabalho ativa ({frente_ativa.get_frente_trabalho_display()}), a qual se recomenda a revogação imediata."
                    )
                else:
                    grau = 'geral'
                    mensagem = f"Foi aplicada penalidade disciplinar de natureza {novo_pdi.get_natureza_display().lower()}."


                # ✅ Criar notificação para todos os usuários
                User = get_user_model()
                notificacao = Notificacao.objects.create(
                    tipo='pdi',
                    titulo=novo_pdi.pessoa.nome_completo,
                    mensagem=mensagem,
                    pessoa=novo_pdi.pessoa,
                    criado_por=request.user,
                    grau=grau
                )
                notificacao.usuarios.set(User.objects.all())

                print("📨 Notificação criada e atribuída a todos os usuários")

                # 📡 Enviar WebSocket para grupo
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    'notifications_group',
                    {
                        'type': 'send_notification',
                        'message': f'[PDI - {grau.upper()}] {notificacao.mensagem}'
                    }
                )
                print("📡 Notificação enviada via WebSocket")

            return redirect('tabela_pdi')

        messages.error(request, "Erro ao salvar o PDI.")
        return redirect('tabela_pdi')

    return render(request, 'painel/tabela_pdi.html', {
        'pd_is_info': pd_is_info,
        'form': PDIForm(instance=pdi),
        'pessoas': pessoas,
        'page_obj': page_obj,
        'filtros': request.GET.dict(),
    })




from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from .models import PDI
from .forms import PDIForm
from django.contrib.auth import get_user_model
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from notification.models import Notificacao
from .forms import PDIForm

def editar_pdi(request, pdi_id):
    pdi = get_object_or_404(PDI, id=pdi_id)

    if request.method == 'POST':
        action_type = request.POST.get('action_type')

        if action_type == 'delete':
            pdi.delete()
            messages.success(request, 'PDI apagado com sucesso.')
            return redirect('tabela_pdi')

        form = PDIForm(request.POST, instance=pdi)

        if form.is_valid():
            resultado_anterior = PDI.objects.get(id=pdi_id).resultado
            print("📌 Resultado anterior:", resultado_anterior)

            pdi_atualizado = form.save()
            print("📌 Resultado novo (salvo):", pdi_atualizado.resultado)

            # Atualiza status da pessoa conforme o novo resultado
            if pdi_atualizado.resultado == 'sobrestado':
                pdi_atualizado.pessoa.status = 'foragido'
            elif pdi_atualizado.resultado in ['andamento', 'condenado']:
                pdi_atualizado.pessoa.status = 'ativo'

            pdi_atualizado.pessoa._status_definido = True
            pdi_atualizado.pessoa.save(update_fields=["status"])

            # ✅ Envia notificação se mudou para 'condenado'
            if resultado_anterior != 'condenado' and pdi_atualizado.resultado == 'condenado':
                print("✅ Condição para notificação satisfeita!")

                frente_ativa = pdi_atualizado.pessoa.frentes_de_trabalho.filter(status='ativo').first()

                if frente_ativa:
                    grau = 'importante'
                    mensagem = (
                        f"PDI ({pdi_atualizado.get_natureza_display()}) recebido. "
                        f"Frente de trabalho ativa ({frente_ativa.get_frente_trabalho_display()}) deve ser revogada."
                    )
                else:
                    grau = 'geral'
                    mensagem = f"PDI ({pdi_atualizado.get_natureza_display()}) recebido."

                # 🔔 Criar notificação única para todos os usuários
                User = get_user_model()
                notificacao = Notificacao.objects.create(
                    tipo='pdi',
                    titulo=pdi_atualizado.pessoa.nome_completo,
                    mensagem=mensagem,
                    pessoa=pdi_atualizado.pessoa,
                    criado_por=request.user,
                    grau=grau
                )
                notificacao.usuarios.set(User.objects.all())

                print("📨 Notificação criada e atribuída a todos os usuários")

                # 📡 Enviar via WebSocket
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    'notifications_group',
                    {
                        'type': 'send_notification',
                        'message': f'[PDI - {grau.upper()}] {notificacao.mensagem}'
                    }
                )
                print("📡 Notificação enviada via WebSocket")

            else:
                print("❌ Não enviou notificação — condição não satisfeita")

            messages.success(
                request,
                f'PDI atualizado com sucesso. {pdi_atualizado.pessoa.nome_completo} agora está {pdi_atualizado.pessoa.status}.'
            )
        else:
            messages.error(request, f'Erro ao atualizar o PDI: {form.errors.as_text()}')

        return redirect('tabela_pdi')

    else:
        messages.error(request, 'Método de requisição inválido.')
        return redirect('tabela_pdi')





def apagar_pdi(request, pdi_id):
    # Recupera o PDI com base no ID
    pdi = get_object_or_404(PDI, id=pdi_id)

    # Verifica se o método de requisição é POST (confirmação de exclusão)
    if request.method == 'POST':
        pdi.delete()  # Apaga o PDI do banco de dados
        messages.success(request, 'PDI apagado com sucesso.')
        return redirect('tabela_pdi')  # Redireciona para a tabela de PDIs

    # Se não for uma requisição POST, redireciona com uma mensagem de erro
    messages.error(request, 'Método de requisição inválido.')
    return redirect('tabela_pdi')




def psicossocial(request):
    
    return render(request, 'painel/psicossocial.html',)

@login_required
def lista_personalizada(request):
    pessoas = Pessoa.objects.exclude(status__in=['inativo', 'foragido']).distinct()
    pessoas_data = [{
        'id': pessoa.id,
        'nome_completo': pessoa.nome_completo,
        'bloco': pessoa.bloco or '-',
        'cela': pessoa.cela or '-'
    } for pessoa in pessoas]
    return render(request, 'painel/listapersonalizada.html', {'pessoas': pessoas_data})

import json
from django.template.loader import render_to_string
from django.http import HttpResponse
from weasyprint import HTML
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from pytz import timezone as pytz_timezone  # Importa pytz

@csrf_exempt 
@login_required
def gerar_pdf_lista(request):
    if request.method == "POST":
        dados_json = request.POST.get("dados_json", "[]")
        pessoas = json.loads(dados_json)

        # Converte para fuso horário local do Brasil (ex: Fortaleza)
        fuso_local = pytz_timezone('America/Fortaleza')
        data_hora = timezone.now().astimezone(fuso_local).strftime("%d/%m/%Y %H:%M")

        # Usuário logado
        usuario = request.user.get_full_name() or request.user.username

        context = {
            "pessoas": pessoas,
            "data_hora": data_hora,
            "usuario": usuario,
        }

        html_string = render_to_string("pdf/pdf_lista_personalizada.html", context)
        pdf_file = HTML(string=html_string).write_pdf()

        response = HttpResponse(pdf_file, content_type="application/pdf")
        response['Content-Disposition'] = 'inline; filename="Lista-personalizada-de-internos.pdf"'
        return response


    
from django.shortcuts import render
from .models import FrenteDeTrabalho


from django.db.models import Q

@login_required
def frentes_de_trabalho(request):
    frentes = FrenteDeTrabalho.objects.all()

    status_list = request.GET.getlist('status')
    frente = request.GET.get('frente')
    busca = request.GET.get('busca', '').strip()
    ordenacao = request.GET.get('ordenacao', '-pessoa__nome_completo')

    if status_list and ('' not in status_list):
        frentes = frentes.filter(status__in=status_list)

    if frente:
        frentes = frentes.filter(frente_trabalho=frente)

    if busca:
        frentes = frentes.filter(
            Q(pessoa__nome_completo__icontains=busca) | Q(pessoa__matricula__icontains=busca)
        )

    if ordenacao:
        frentes = frentes.order_by(ordenacao)

    # Paginação
    paginator = Paginator(frentes, 30)  # 30 por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    form = FrenteDeTrabalhoForm()

    contexto = {
        'page_obj': page_obj,
        'form': form,
        'status_selecionados': status_list,
        'fronteiras_trabalho': FrenteDeTrabalho.FRONTEIRAS_TRABALHO_CHOICES,
    }
    return render(request, 'painel/frentes_de_trabalho.html', contexto)

from django.http import JsonResponse
from collections import Counter
from .models import FrenteDeTrabalho

from collections import Counter
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

@login_required
def dados_graficos_frentes(request):
    frentes = FrenteDeTrabalho.objects.all()

    # Mapeamento legível
    nome_frentes = dict(FrenteDeTrabalho.FRONTEIRAS_TRABALHO_CHOICES)

    # Filtra ativos e revogados separadamente
    ativos = frentes.filter(status='ativo')
    revogados = frentes.filter(status='revogado')

    contagem_ativos = Counter(ativos.values_list('frente_trabalho', flat=True))
    contagem_revogados = Counter(revogados.values_list('frente_trabalho', flat=True))

    # Dados para gráfico de pizza — somente ATIVOS
    dados_pizza = []
    for frente_cod, count in contagem_ativos.items():
        nome = nome_frentes.get(frente_cod, frente_cod)
        dados_pizza.append({'name': nome, 'y': count})

    # Dados para gráfico de colunas — ATIVOS vs REVOGADOS
    categorias = []
    data_ativos = []
    data_revogados = []

    todos_codigos = set(contagem_ativos.keys()) | set(contagem_revogados.keys())
    for frente_cod in todos_codigos:
        nome = nome_frentes.get(frente_cod, frente_cod)
        categorias.append(nome)
        data_ativos.append(contagem_ativos.get(frente_cod, 0))
        data_revogados.append(contagem_revogados.get(frente_cod, 0))

    return JsonResponse({
        'pizza': dados_pizza,
        'barras': {
            'categorias': categorias,
            'ativos': data_ativos,
            'revogados': data_revogados,
        }
    })





from .models import FrenteDeTrabalho
from .forms import FrenteDeTrabalhoForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import FrenteDeTrabalho
from .forms import FrenteDeTrabalhoForm

@login_required
def cadastrar_frente_de_trabalho(request):
    if request.method == 'POST':
        print("🔄 Recebido POST para cadastrar frente de trabalho.")
        print("📦 Dados recebidos:", request.POST.dict())

        form = FrenteDeTrabalhoForm(request.POST)
        if form.is_valid():
            frente = form.save()
            print("✅ Frente de trabalho cadastrada:", frente)
            return JsonResponse({'message': 'Cadastro realizado com sucesso!'})
        else:
            print("❌ Erros no formulário:", form.errors)

            # Converte os erros para string legível
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(f"{field.capitalize()}: {error}")
            return JsonResponse({'message': ' | '.join(error_messages)}, status=400)

    else:
        print("📄 Página de cadastro acessada via GET")
        form = FrenteDeTrabalhoForm()

    return render(request, 'painel/frentes_de_trabalho.html', {'form': form})



from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import FrenteDeTrabalho

@require_POST
@login_required
def apagar_frente_de_trabalho(request, frente_id):
    frente = get_object_or_404(FrenteDeTrabalho, id=frente_id)

    try:
        frente.delete()
        return JsonResponse({'message': 'Frente de trabalho apagada com sucesso.'})
    except Exception as e:
        return JsonResponse({'message': f'Erro ao apagar: {str(e)}'}, status=400)
    
from datetime import datetime
import locale

import os
from django.conf import settings

from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from datetime import datetime
from .models import FrenteDeTrabalho

@login_required
def revogar_trabalho(request, frente_id):
    print(f"📥 Solicitação para revogar frente ID {frente_id}")
    frente = get_object_or_404(FrenteDeTrabalho, id=frente_id)
    print("🔍 Frente encontrada:", frente)

    frente.status = FrenteDeTrabalho.REVOGADO
    frente.data_revogacao = datetime.today()
    if not frente.data_retroacao:
        frente.data_retroacao = datetime.today()

    try:
        frente.save()
        print("✅ Frente atualizada como revogada.")

        # 🔔 Notificação de revogação
        from django.contrib.auth import get_user_model
        from notification.models import Notificacao
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync

        User = get_user_model()
        mensagem = (
            f"Portaria de Revogação Nº {frente.numero_portaria_revogacao}\n"
            f"Frente de trabalho \"{frente.get_frente_trabalho_display()}\" foi revogada."
        )

        notificacao = Notificacao.objects.create(
            tipo='revogacao',
            titulo=frente.pessoa.nome_completo,
            mensagem=mensagem,
            pessoa=frente.pessoa,
            criado_por=request.user,
            grau='geral'
        )
        notificacao.usuarios.set(User.objects.all())

        # Enviar via WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'notifications_group',
            {
                'type': 'send_notification',
                'message': f'[REVOGAÇÃO - GERAL] {notificacao.mensagem}'
            }
        )
        print("📡 Notificação de revogação enviada via WebSocket")

    except Exception as e:
        print("❌ Erro ao salvar frente:", e)
        return HttpResponse("Erro ao salvar dados", status=500)

    # Gerar PDF
    try:
        pdf_path = frente.gerar_pdf_revogacao()
        print("📄 PDF gerado em:", pdf_path)
    except Exception as e:
        print("❌ Erro ao gerar PDF:", e)
        return HttpResponse('Erro ao gerar o PDF', status=500)

    if not pdf_path:
        print("⚠️ Caminho do PDF está vazio ou inválido.")
        return HttpResponse('Erro ao gerar o PDF', status=500)

    with open(pdf_path, "rb") as pdf_file:
        response = HttpResponse(pdf_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(pdf_path)}"'

    print("📤 PDF pronto para download.")
    return response




