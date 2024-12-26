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

# Models
from .models import Pessoa, Transferencia, Sancao, Eletronico, HistoricoAlteracao

# Forms
from .forms import PessoaForm, TransferenciaForm, EletronicoForm, SancaoForm

# ReportLab (PDF Generation)
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from django.contrib.staticfiles import finders

@login_required
def index_view(request):
    # Contagem total de pessoas cadastradas, excluindo as com transferência ativa e saiu_temporariamente ativo
    pessoas_list = Pessoa.objects.exclude(tem_transferencia_ativa=True).exclude(saiu_temporariamente=True)
    total_pessoas = pessoas_list.count()
    limite_maximo = 294  # Limite máximo para o gráfico
    porcentagem_cadastrados = (total_pessoas / limite_maximo) * 100  # Pode ultrapassar 100%
    total_saiu_temporariamente = Pessoa.objects.filter(saiu_temporariamente=True).count()  # Contagem das pessoas que saíram temporariamente

    # Contagem por programas de estudo, excluindo as pessoas que saíram temporariamente
    total_ibraema = Pessoa.objects.filter(estudando=Pessoa.Estudando.IBRAEMA).exclude(saiu_temporariamente=True).count()
    total_eja_i = Pessoa.objects.filter(estudando=Pessoa.Estudando.EJA_I).exclude(saiu_temporariamente=True).count()
    total_eja_ii = Pessoa.objects.filter(estudando=Pessoa.Estudando.EJA_II).exclude(saiu_temporariamente=True).count()
    total_eja_iii = Pessoa.objects.filter(estudando=Pessoa.Estudando.EJA_III).exclude(saiu_temporariamente=True).count()
    total_ensino_superior = Pessoa.objects.filter(estudando=Pessoa.Estudando.ENSINO_SUPERIOR).exclude(saiu_temporariamente=True).count()

    # Contagem por frentes de trabalho, excluindo as pessoas que saíram temporariamente
    total_nao_trabalha = Pessoa.objects.filter(frente_trabalho=Pessoa.FrenteDeTrabalho.NAO_TRABALHA).exclude(saiu_temporariamente=True).count()
    total_horta = Pessoa.objects.filter(frente_trabalho=Pessoa.FrenteDeTrabalho.HORTA).exclude(saiu_temporariamente=True).count()
    total_piscicultura = Pessoa.objects.filter(frente_trabalho=Pessoa.FrenteDeTrabalho.PISCICULTURA).exclude(saiu_temporariamente=True).count()
    total_minhocario = Pessoa.objects.filter(frente_trabalho=Pessoa.FrenteDeTrabalho.MINHOCARIO).exclude(saiu_temporariamente=True).count()
    total_limpeza = Pessoa.objects.filter(frente_trabalho=Pessoa.FrenteDeTrabalho.LIMPEZA).exclude(saiu_temporariamente=True).count()
    total_manutencao = Pessoa.objects.filter(frente_trabalho=Pessoa.FrenteDeTrabalho.MANUTENCAO).exclude(saiu_temporariamente=True).count()
    total_fabrica_blocos = Pessoa.objects.filter(frente_trabalho=Pessoa.FrenteDeTrabalho.FABRICA_DE_BLOCOS).exclude(saiu_temporariamente=True).count()
    total_croche = Pessoa.objects.filter(frente_trabalho=Pessoa.FrenteDeTrabalho.CROCHE).exclude(saiu_temporariamente=True).count()
    total_digitalizador = Pessoa.objects.filter(frente_trabalho=Pessoa.FrenteDeTrabalho.DIGITALIZADOR).exclude(saiu_temporariamente=True).count()
    total_bibliotecario = Pessoa.objects.filter(frente_trabalho=Pessoa.FrenteDeTrabalho.BIBLIOTECARIO).exclude(saiu_temporariamente=True).count()

    total_trabalhando = (
        total_horta +
        total_piscicultura +
        total_minhocario +
        total_limpeza +
        total_manutencao +
        total_fabrica_blocos +
        total_croche +
        total_digitalizador +
        total_bibliotecario
    )

    # Contagem de TVs e Rádios
    total_tv = Eletronico.objects.filter(tipo='tv').count()
    total_radio = Eletronico.objects.filter(tipo='radio').count()
    total_ventilador = Eletronico.objects.filter(tipo='ventilador').count()

    # Filtra as pessoas para mostrar por bloco, excluindo as pessoas que saíram temporariamente
    bloco_a = Pessoa.objects.filter(bloco='A').exclude(saiu_temporariamente=True)
    bloco_b = Pessoa.objects.filter(bloco='B').exclude(saiu_temporariamente=True)
    bloco_c = Pessoa.objects.filter(bloco='C').exclude(saiu_temporariamente=True)
    bloco_d = Pessoa.objects.filter(bloco='D').exclude(saiu_temporariamente=True)
    bloco_e = Pessoa.objects.filter(bloco='E').exclude(saiu_temporariamente=True)

    # Contagem por cela para cada bloco, excluindo as pessoas que saíram temporariamente
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
        'total_saiu_temporariamente': total_saiu_temporariamente,  # Passando a variável para o template
        'porcentagem_cadastrados': porcentagem_cadastrados,
        'limite_maximo': limite_maximo,
        'total_ibraema': total_ibraema,
        'total_eja_i': total_eja_i,
        'total_eja_ii': total_eja_ii,
        'total_eja_iii': total_eja_iii,
        'total_ensino_superior': total_ensino_superior,
        'total_tv': total_tv,
        'total_radio': total_radio,
        'total_ventilador': total_ventilador,
        'total_nao_trabalha': total_nao_trabalha,
        'total_horta': total_horta,
        'total_piscicultura': total_piscicultura,
        'total_minhocario': total_minhocario,
        'total_limpeza': total_limpeza,
        'total_manutencao': total_manutencao,
        'total_fabrica_blocos': total_fabrica_blocos,
        'total_croche': total_croche,
        'total_digitalizador': total_digitalizador,
        'total_bibliotecario': total_bibliotecario,
        'total_trabalhando': total_trabalhando,
        'cela_1_a': cela_1_a, 'cela_2_a': cela_2_a, 'cela_3_a': cela_3_a, 'cela_4_a': cela_4_a, 'cela_5_a': cela_5_a,
        'cela_b1': cela_b1, 'cela_b2': cela_b2, 'cela_b3': cela_b3, 'cela_b4': cela_b4, 'cela_b5': cela_b5,
        'cela_c1': cela_c1, 'cela_c2': cela_c2, 'cela_c3': cela_c3, 'cela_c4': cela_c4, 'cela_c5': cela_c5,
        'cela_c6': cela_c6, 'cela_c7': cela_c7,
        'cela_d1': cela_d1, 'cela_d2': cela_d2, 'cela_d3': cela_d3, 'cela_d4': cela_d4, 'cela_d5': cela_d5,
        'cela_e1': cela_e1, 'cela_e2': cela_e2, 'cela_e3': cela_e3, 'cela_e4': cela_e4, 'cela_e5': cela_e5,
        'cela_e6': cela_e6, 'cela_e7': cela_e7,
        'page_obj': page_obj,
    })

    



@login_required
def adicionar_pessoa_view(request):
    if request.method == 'POST':
        form = PessoaForm(request.POST)
        
        # Verifique se o formulário é válido
        if form.is_valid():
            form.save()
            messages.success(request, "Cadastrado com sucesso!")  # Mensagem de sucesso
            return redirect('adicionar_pessoa')  # Redireciona para a página de adicionar pessoa
        else:
            # Caso o formulário não seja válido, exiba os erros
            messages.error(request, "Por favor, corrija os erros abaixo.")
            print(form.errors)  # Exibe os erros no console (ou logs)
    
    else:
        form = PessoaForm()
    
    return render(request, 'painel/adicionar_pessoa.html', {'form': form})


@login_required
def remover_pessoa(request, id):
    pessoa = get_object_or_404(Pessoa, id=id)
    if request.method == 'POST':
        try:
            # Registrar a exclusão no histórico antes de excluir a pessoa
            HistoricoAlteracao.objects.create(
                pessoa=pessoa,
                usuario=request.user,
                campo_alterado='Exclusão',  # Indica que o campo alterado é a exclusão
                valor_antigo=str(pessoa),  # Valor antigo como a representação da pessoa
                valor_novo='Excluída',  # Valor novo indicando que foi excluída
                data_alteracao=timezone.now()  # Data e hora da exclusão
            )
            
            # Excluir a pessoa fisicamente após o histórico ser registrado
            pessoa.delete()
            
            messages.success(request, 'Alvará concedido com sucesso!')
        except Exception as e:
            messages.error(request, f'Ocorreu um erro ao tentar dar alvará ao interno! {e}')
    return redirect('ver_tabela')  # Redireciona para a tabela após a remoção



from django.db.models import Q
from django.db.models.functions import Lower



from django.utils.timezone import now
from django.db.models import Prefetch, Q


from datetime import timedelta
from django.utils.timezone import now

@login_required
def ver_tabela_view(request):
    # Filtros e base da queryset (já existente)
    bloco_filter = request.GET.get('bloco')
    cela_filter = request.GET.get('cela')
    escolaridade_filter = request.GET.get('escolaridade')
    estudando_filter = request.GET.get('estudando')
    frente_trabalho_filter = request.GET.get('frente_trabalho')
    ordenar_nome = request.GET.get('ordenar_nome')
    ordenar_bloco_cela = request.GET.get('ordenar_bloco_cela')
    nome_filter = request.GET.get('nome')
    saiu_temporariamente_filter = request.GET.get('saiu_temporariamente')

    pessoas_list = Pessoa.objects.exclude(
        transferencia__transferencia_ativa=True
    ).order_by('-created_at')

    # Aplicar filtros
    if bloco_filter:
        pessoas_list = pessoas_list.filter(bloco=bloco_filter)
    if cela_filter:
        pessoas_list = pessoas_list.filter(cela=cela_filter)
    if escolaridade_filter:
        pessoas_list = pessoas_list.filter(escolaridade=escolaridade_filter)
    if estudando_filter:
        pessoas_list = pessoas_list.filter(estudando=estudando_filter)
    if frente_trabalho_filter:
        pessoas_list = pessoas_list.filter(frente_trabalho=frente_trabalho_filter)
    if nome_filter:
        pessoas_list = pessoas_list.filter(nome_completo__icontains=nome_filter.strip())


    # Filtro para "Saiu Temporariamente"
    if saiu_temporariamente_filter == 'on':
        pessoas_list = pessoas_list.filter(saiu_temporariamente=True)

    # Ordenações
    if ordenar_nome:
        pessoas_list = pessoas_list.order_by('nome_completo')
    if ordenar_bloco_cela == 'on':
        pessoas_list = pessoas_list.order_by('bloco', 'cela')

    

    hoje = now().date()
    for pessoa in pessoas_list:
        # Verificar se há algum PDI ativo ou programado para começar em breve
        pdi_ativo = pessoa.pd_is.filter(data_inicio__lte=hoje, data_fim__gte=hoje) | pessoa.pd_is.filter(data_inicio__gte=hoje)
        pessoa.pdi_ativo = 'Sim' if pdi_ativo.exists() else 'Não'



    # Calcular limites de data
    hoje = now().date()
    ontem = hoje - timedelta(days=1)
    

    # Adicionar flag de status
    for pessoa in pessoas_list:
        # Adicionando o filtro de sanções ativas
        pessoa.sancoes_ativas = pessoa.sancoes.filter(data_fim__gte=now())

    # Adicionar flag de status
    for pessoa in pessoas_list:
        if pessoa.created_at.date() == hoje:
            pessoa.status_novo = 'Hoje'
        elif pessoa.created_at.date() == ontem:
            pessoa.status_novo = 'Ontem'
        else:
            pessoa.status_novo = ''


        # Adicionar status de "Saiu Temporariamente"
    for pessoa in pessoas_list:
        pessoa.saiu_temporariamente_ativo = pessoa.saiu_temporariamente  # Pode ser True ou False


    # Paginação
    paginator = Paginator(pessoas_list, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Calcular o número de pessoas que já foram exibidas
    start_index = (page_obj.number - 1) * 20  # Calcula o índice do primeiro item na página
    for i, pessoa in enumerate(page_obj.object_list):
        pessoa.counter = start_index + i + 1  # Ajusta o contador

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
        'start_index': start_index,  # Passar para o template
    })





def exportar_tabela_pdf(request):
    # Pegando os filtros da URL
    user_name = request.user.username  # Acessando o nome de usuário do usuário autenticado
    bloco_filter = request.GET.get('bloco')
    cela_filter = request.GET.get('cela')
    escolaridade_filter = request.GET.get('escolaridade')
    estudando_filter = request.GET.get('estudando')
    sancao_filter = request.GET.get('sancao')
    frente_trabalho_filter = request.GET.get('frente_trabalho')
    ordenar_nome = request.GET.get('ordenar_nome')
    ordenar_bloco_cela = request.GET.get('ordenar_bloco_cela')
    saiu_temporariamente_filter = request.GET.get('saiu_temporariamente')

    # Converter o valor "on" para True e lidar com a ausência do filtro
    if saiu_temporariamente_filter == 'on':
        saiu_temporariamente_filter = True
    else:
        saiu_temporariamente_filter = None

    # Base da queryset excluindo pessoas com transferência ativa
    pessoas_list = Pessoa.objects.exclude(
        transferencia__transferencia_ativa=True
    ).order_by('-data_entrada')

    # Filtro para 'saiu_temporariamente'
    if saiu_temporariamente_filter is not None:
        # Filtrar apenas quando o valor foi explicitamente passado
        pessoas_list = pessoas_list.filter(saiu_temporariamente=saiu_temporariamente_filter)
    else:
        # Excluir registros com 'saiu_temporariamente=True' se não houver filtro explícito
        pessoas_list = pessoas_list.exclude(saiu_temporariamente=True)

    
    # Aplicar filtros
    if bloco_filter:
        pessoas_list = pessoas_list.filter(bloco=bloco_filter)
    if cela_filter:
        pessoas_list = pessoas_list.filter(cela=cela_filter)
    if escolaridade_filter:
        pessoas_list = pessoas_list.filter(escolaridade=escolaridade_filter)
    if estudando_filter:
        pessoas_list = pessoas_list.filter(estudando=estudando_filter)
    if frente_trabalho_filter:
        pessoas_list = pessoas_list.filter(frente_trabalho=frente_trabalho_filter)
    if sancao_filter:
        pessoas_list = pessoas_list.filter(sancoes__tipo=sancao_filter, sancoes__data_fim__isnull=True)
    if ordenar_nome:
        pessoas_list = pessoas_list.order_by(Lower('nome_completo'))
    if ordenar_bloco_cela:
        pessoas_list = pessoas_list.order_by('bloco', 'cela')

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
        filtros.append(f"Bloco: {bloco_filter}")
    if cela_filter:
        filtros.append(f"Cela: {cela_filter}")
    if escolaridade_filter:
        filtros.append(f"Escolaridade: {escolaridade_filter}")
    if estudando_filter:
        filtros.append(f"Estudando: {estudando_filter}")
    if frente_trabalho_filter:
        filtros.append(f"Frente de Trabalho: {frente_trabalho_filter}")
    if sancao_filter:
        filtros.append(f"Sanção: {sancao_filter}")
    if ordenar_nome:
        filtros.append("Ordenação por Nome")
    if ordenar_bloco_cela:
        filtros.append("Ordenação por Bloco e Cela")

    col_widths = [20, 10, 20, 180, 58, 65, 70, 65, 65]  # Ajuste nas larguras das colunas
    col_titles = ["", "B", "C", "Nome Completo", "Eletrônicos", "Escolaridade", "Escola", "Trabalhando", "Sanções"]

    # Desenha o cabeçalho na primeira página
    y_position = desenhar_cabecalho(c, y_position, largura_pagina, altura_pagina, filtros, col_titles, col_widths)

    # Definindo o tamanho da fonte para as linhas de dados
    c.setFont("Helvetica", 9)

    # Verifica se há pessoas para exibir
    if pessoas_list.exists():
        # Escreve os dados das pessoas filtradas
        for pessoa in pessoas_list:
            # Dados a serem exibidos, removendo "Art.Crim" e colocando "Eletrônicos"
            row_data = [
                pessoa.bloco if pessoa.bloco else 'N/A',
                pessoa.cela if pessoa.cela else 'N/A',
                pessoa.nome_completo.title()[:40],  # Aplica a função title() ao nome completo
                '',  # Coluna "Eletrônicos" será preenchida abaixo
                dict(Pessoa.Escolaridade.choices).get(pessoa.escolaridade, 'N/A'),
                dict(Pessoa.Estudando.choices).get(pessoa.estudando, 'N/A'),
                dict(Pessoa.FrenteDeTrabalho.choices).get(pessoa.frente_trabalho, 'N/A'),
            ]

            # Desenha o quadrado (representando o índice)
            c.rect(x_position, y_position - 3, 10, 10)  # Desenha o quadrado
            c.drawString(x_position + 3, y_position, "")  # O número dentro do quadrado está vazio

            # Desenha os dados nas colunas seguintes
            for i, data in enumerate(row_data):
                # Verifica se é a coluna de "Bloco" ou "Cela" e aplica negrito
                if i == 0 or i == 1:  # Colunas Bloco e Cela
                    c.setFont("Helvetica-Bold", 8)  # Negrito
                else:
                    c.setFont("Helvetica", 8)  # Fonte normal
                c.drawString(x_position + sum(col_widths[:i+1]), y_position, data)
                
            
            
            
        # Processamento de Eletrônicos
            initial_y_position = y_position
            eletrônicos = Eletronico.objects.filter(pessoa=pessoa)

            if eletrônicos.exists():
                # Exibindo apenas os ícones dos eletrônicos, um ao lado do outro
                x_offset = x_position + sum(col_widths[:4])  # Posição inicial para os ícones
                for eletronico in eletrônicos:
                    # Definindo o ícone para cada tipo de eletrônico
                    if eletronico.tipo == 'tv':
                        img_path = finders.find('imagens/tv.png')  # Caminho da imagem TV
                    elif eletronico.tipo == 'radio':
                        img_path = finders.find('imagens/radio.png')  # Caminho da imagem Rádio
                    elif eletronico.tipo == 'ventilador':
                        img_path = finders.find('imagens/ventilador.png')  # Caminho da imagem Ventilador
                    else:
                        img_path = ''  # Caso não haja tipo válido (você pode adicionar mais tipos)
                    if img_path:
                        c.drawImage(img_path, x_offset, y_position - 3, width=12, height=12, mask='auto')  # Ícone com transparência
                        x_offset += 18  # Distância entre os ícones (ajuste conforme necessário)

                y_position -= 8  # Ajuste para o próximo item após a linha de ícones
            else:
                # Exibindo a mensagem "Não há" se não houver eletrônicos
                c.setFont("Helvetica", 8)
                c.drawString(x_position + sum(col_widths[:4]), y_position, "Não há")  # Mensagem
                y_position -= 8  # Ajuste após a mensagem


            # Restabelecendo y_position para a posição inicial antes de processar as sanções
            y_position = initial_y_position

            # Processamento das sanções
            sancao_atual = Sancao.objects.filter(pessoa=pessoa, data_fim__gt=datetime.now())

            if sancao_atual.exists():
                # Exibindo as sanções, um por um, manualmente
                c.setFont("Helvetica", 8)
                for sancao in sancao_atual:
                    c.drawString(
                        x_position + sum(col_widths[:-1]),  # Posição da última coluna
                        y_position,
                        f"{sancao.tipo.replace('_', ' ').capitalize()}"
                    )
                    y_position -= 8.5  # Ajuste para o próximo item
            else:
                c.setFont("Helvetica", 8)
                c.drawString(
                    x_position + sum(col_widths[:-1]),  # Posição horizontal correta (última coluna)
                    y_position,
                    "Não há"
                )
                y_position -= 8  # Ajuste quando não houver sanções

            # Linha de separação entre os dados
            c.setStrokeColorRGB(0.4, 0.4, 0.4)
            c.setLineWidth(0.3)
            c.line(x_position, y_position, x_position + 558, y_position)


            # separa o espaço entre uma linha e outra
            y_position -= 13

            # Verifique se a posição y é menor que o limite inferior e, se necessário, crie uma nova página
            if y_position < 40:
                c.showPage()
                y_position = altura_pagina - margem_superior
                y_position = desenhar_cabecalho(c, y_position, largura_pagina, altura_pagina, filtros, col_titles, col_widths)
                


        # Adiciona o rodapé com informações do usuário e a data de geração
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
    }



    
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
            elif transferencia_ativa and transferencia_form.is_valid():
                transferencia = transferencia_form.save(commit=False)
                transferencia.pessoa = pessoa
                transferencia.save()

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
            tipos_sancao = ['sem_castelo', 'sem_visita_intima', 'sem_visita_social']
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
})







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

def atualizar_tempo_restante_view(request, sancao_id):
    try:
        sancao = Sancao.objects.get(id=sancao_id)

        if sancao.data_fim:
            tempo_restante = sancao.data_fim - timezone.now()

            if tempo_restante.total_seconds() > 0:
                dias = tempo_restante.days
                horas, resto = divmod(tempo_restante.seconds, 3600)
                minutos, segundos = divmod(resto, 60)
                tempo_formatado = f"{dias} dias, {horas} horas, {minutos} minutos, {segundos} segundos restantes"
            else:
                tempo_formatado = "Sanção finalizada"

            return JsonResponse({'tempo_restante': tempo_formatado})

        return JsonResponse({'tempo_restante': 'Data inválida'})
    
    except Sancao.DoesNotExist:
        return JsonResponse({'tempo_restante': 'Sanção não encontrada'})
    
    
    
    
    
    
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



def pessoa_search(request):
    q = request.GET.get('q', '')
    # Filtrar pessoas que têm transferência ativa e não mostrá-las
    pessoas = Pessoa.objects.filter(
        nome_completo__icontains=q
    ).exclude(
        transferencia__transferencia_ativa=True
    ).distinct()[:10]  # Limitar a 10 resultados e garantir que não haja duplicação
    results = [{'id': pessoa.id, 'nome_completo': pessoa.nome_completo} for pessoa in pessoas]
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
    return render(request, 'painel/arquivos.html')


def informacao_view(request):
    return render(request, 'painel/informacao.html')
from django.http import HttpResponseNotFound
from django.shortcuts import render, redirect
from .models import PDI, Pessoa
from .forms import PDIForm
from django.utils import timezone
from django.contrib import messages
from .models import Notification
from django.contrib.auth.models import User
import logging
logger = logging.getLogger(__name__)
def tabela_e_aplicar_pdi_view(request, pdi_id=None):
    # Buscar todos os registros de PDI que ainda estão ativos (data_fim no futuro)
    pd_is = PDI.objects.all().order_by('-id')  # Ordena pelo ID em ordem decrescente (último primeiro)
    # Buscar todas as pessoas para o campo select
    pessoas = Pessoa.objects.all()

    # Aplicar os filtros com base nos parâmetros de consulta (GET)
    pessoa_filtro = request.GET.get('pessoa')
    natureza_filtro = request.GET.get('natureza')
    descricao_filtro = request.GET.get('descricao')
    data_inicio_filtro = request.GET.get('data_inicio')
    data_fim_filtro = request.GET.get('data_fim')
    resultado_filtro = request.GET.get('resultado')
    ordenar_por_letra = request.GET.get('ordenar_por_letra')

    if pessoa_filtro:
        pd_is = pd_is.filter(pessoa__nome_completo__icontains=pessoa_filtro)
    

    if natureza_filtro:
        pd_is = pd_is.filter(natureza=natureza_filtro)
    if descricao_filtro:
        pd_is = pd_is.filter(descricao__icontains=descricao_filtro)
    try:
        if data_inicio_filtro:
            data_inicio_filtro = timezone.datetime.strptime(data_inicio_filtro, "%Y-%m-%dT%H:%M")
        if data_fim_filtro:
            data_fim_filtro = timezone.datetime.strptime(data_fim_filtro, "%Y-%m-%dT%H:%M")
    except ValueError:
        messages.error(request, "Formato de data inválido.")
        return redirect('tabela_pdi')
    if resultado_filtro:
        pd_is = pd_is.filter(resultado=resultado_filtro)
    if ordenar_por_letra == "1":
        pd_is = pd_is.order_by(Lower('pessoa__nome_completo'))  # Ordena pela letra do nome da pessoa ignorando maiúsculas/minúsculas   
        
    # Paginação
    paginator = Paginator(pd_is, 20)  # Define 10 itens por página
    page_number = request.GET.get('page')  # Obtém o número da página da URL
    page_obj = paginator.get_page(page_number)  # Retorna os itens da página atual    
        
        
    # Se um ID de PDI for fornecido, buscamos o PDI para edição
    if pdi_id:
        try:
            pdi = PDI.objects.get(id=pdi_id)
        except PDI.DoesNotExist:
            return HttpResponseNotFound("PDI não encontrado")  # Retorna uma resposta de erro
    else:
        pdi = None


    # Calcular a diferença de meses e dias, e dias restantes
    def calcular_diferença(data_inicio, data_fim):
        # Diferença entre as duas datas
        diff = data_fim - data_inicio
        # Calculando meses e dias
        meses = diff.days // 30  # Aproximando para meses
        dias = diff.days % 30  # Resto de dias
        return meses, dias

    def calcular_dias_restantes(data_fim):
        # Verifica se data_fim é None
        if data_fim is None:
            return 'Data de término não definida'  # Ou qualquer outra mensagem adequada

        # Certifique-se de que data_fim tem um timezone
        if data_fim.tzinfo is None:
            data_fim = timezone.make_aware(data_fim)  # Torna data_fim ciente de timezone

        # Obter a data atual com timezone
        data_atual = timezone.now()

        # Calcular dias restantes
        dias_restantes = (data_fim - data_atual).days

        # Determinar a mensagem apropriada
        if dias_restantes > 0:
            return f"{dias_restantes} dias restantes"
        elif dias_restantes == 0:
            return "Expira Hoje"
        else:
            return f"Expirou há {abs(dias_restantes)} dias"

    # Se o formulário for enviado, processamos os dados
    if request.method == "POST":
        form = PDIForm(request.POST, instance=pdi)
        if form.is_valid():
            novo_pdi = form.save()
            if not pdi:
                messages.success(request, f"PDI para {novo_pdi.pessoa} foi criado com sucesso!")
            return redirect('tabela_pdi')  # Redireciona após salvar o PDI
        else:
            # Se o formulário não for válido, apenas renderize a página novamente com erros
            messages.error(request, "Houve um erro ao salvar o PDI.")

            return redirect('tabela_pdi')  # Redireciona de volta para a tabela
    else:
        form = PDIForm(instance=pdi)  # Carrega o formulário com os dados existentes (se houver)

    # Adicionando as novas colunas calculadas
    pd_is_info = []
    for pdi in pd_is:
        if pdi.data_fim:  # Verifica se há uma data_fim
            meses, dias = calcular_diferença(pdi.data_inicio, pdi.data_fim)
            dias_restantes = calcular_dias_restantes(pdi.data_fim)
        else:
            meses, dias = 0, 0  # Caso não tenha data_fim
            dias_restantes = 'Não definido'  # Indica que o tempo não foi aplicado

        pd_is_info.append({
            'pdi': pdi,
            'meses_aplicados': meses,
            'dias_aplicados': dias,
            'dias_restantes': calcular_dias_restantes(pdi.data_fim)  # Agora inclui "Expira Hoje"
        })

    # Renderiza a tabela de PDIs e o formulário no modal
    return render(request, 'painel/tabela_pdi.html', {
        'pd_is_info': pd_is_info,  # Passa as informações adicionais para o template
        'form': form,     # Passa o formulário para o template
        'pdi_id': pdi_id, # Passa o ID do PDI para edição, se necessário
        'pessoas': pessoas,  # Passa a lista de pessoas para o template
        'page_obj': page_obj,  # Página atual para controle de paginação no template
        'filtros': request.GET.dict(),  # Passa os filtros para persistência na paginação
    })



from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from .models import PDI
from .forms import PDIForm

def editar_pdi(request, pdi_id):
    print(f"Request recebido. Método: {request.method}, PDI ID: {pdi_id}")
    
    # Buscar o PDI no banco de dados
    pdi = get_object_or_404(PDI, id=pdi_id)
    print(f"PDI encontrado: {pdi.id} - {pdi}")

    if request.method == 'POST':
        action_type = request.POST.get('action_type')
        print(f"Ação recebida: {action_type}")

        if action_type == 'delete':
            # Apagar o PDI
            print(f"Deletando o PDI ID: {pdi_id}")
            pdi.delete()
            messages.success(request, 'PDI apagado com sucesso.')
            print("PDI deletado com sucesso.")
            return redirect('tabela_pdi')
        
        # Preencher o formulário com os dados do POST
        form = PDIForm(request.POST, instance=pdi)
        print("Dados do POST recebidos:", request.POST)
        print(f"Validação do formulário iniciada para PDI ID: {pdi_id}")
        
        if form.is_valid():
            # Salvar o formulário se os dados forem válidos
            pdi_atualizado = form.save()
            print(f"PDI atualizado com sucesso: {pdi_atualizado.id} - {pdi_atualizado}")
            messages.success(request, 'PDI atualizado com sucesso.')
        else:
            # Caso o formulário não seja válido
            print(f"Erro na validação do formulário: {form.errors}")
            messages.error(request, f'Erro ao atualizar o PDI: {form.errors.as_text()}')
        
        # Redirecionar de volta para a tabela
        print("Redirecionando para tabela_pdi")
        return redirect('tabela_pdi')
    
    else:
        # Caso o método da requisição não seja POST
        print("Método de requisição inválido.")
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


def notificacoes_view(request):
    notificacoes = Notification.objects.filter(usuario=request.user).order_by('-data_criacao')
    return render(request, 'notificacoes.html', {'notificacoes': notificacoes})

from django.http import JsonResponse
from .models import Notification


from django.http import JsonResponse
from .models import Notification

def marcar_como_lida(request, notification_id):
    if request.user.is_authenticated:
        try:
            notificacao = Notification.objects.get(id=notification_id, usuario=request.user)
            notificacao.lida = True
            notificacao.save()
            # Exclui a notificação após marcar como lida
            notificacao.delete()
            return JsonResponse({'success': True})
        except Notification.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Notificação não encontrada'}, status=404)
    return JsonResponse({'success': False}, status=400)



def marcar_todas_como_lidas(request):
    if request.user.is_authenticated:
        # Marca todas as notificações não lidas como lidas
        notificacoes = Notification.objects.filter(usuario=request.user, lida=False)
        
        # Marca como lida e exclui as notificações
        notificacoes.update(lida=True)
        notificacoes.delete()  # Exclui as notificações marcadas como lidas
        
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)


