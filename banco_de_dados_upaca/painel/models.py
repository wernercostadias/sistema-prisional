from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django import forms
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import RegexValidator
from datetime import date
from unidecode import unidecode
from notification.models import Notificacao
from django.contrib.auth import get_user_model
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class Pessoa(models.Model):
    class Escolaridade(models.TextChoices):
        FUNDAMENTAL_INCOMPLETO = '1', 'E.F.I'
        FUNDAMENTAL_COMPLETO = '2', 'E.F.C'
        MEDIO_INCOMPLETO = '3', 'E.M.I'
        MEDIO_COMPLETO = '4', 'E.M.C'
        SUPERIOR_INCOMPLETO = '5', 'E.S.I'
        SUPERIOR_COMPLETO = '6', 'E.S.C'

    class Estudando(models.TextChoices):
        NAO_ESTUDA = 'nao_estuda', 'Não Estuda'
        IBRAEMA = 'ibraema', 'IBRAEMA'
        EJA_I = 'eja_i', 'EJA I'
        EJA_II = 'eja_ii', 'EJA II'
        EJA_III = 'eja_iii', 'EJA III'
        ENSINO_SUPERIOR = 'ensino_superior', 'Ensino Superior'


    STATUS_CHOICES = [
        ('ativo', 'Ativo'),
        ('inativo', 'Inativo'),
        ('foragido', 'Foragido'),
    ]

    bloco = models.CharField(max_length=1, choices=[('A', 'Bloco A'), ('B', 'Bloco B'), ('C', 'Bloco C'), ('D', 'Bloco D'), ('E', 'Bloco E')], null=True)
    cela = models.CharField(max_length=2, choices=[('1', 'Cela 1'), ('2', 'Cela 2'), ('3', 'Cela 3'), ('4', 'Cela 4'), ('5', 'Cela 5'), ('6', 'Cela 6'), ('7', 'Cela 7')], null=True)
    tem_transferencia_ativa = models.BooleanField(default=False)
    nome_completo = models.CharField(max_length=255, null=True)
    data_nascimento = models.DateField(null=True, blank=True)
    data_entrada = models.DateField(null=True)
    escolaridade = models.CharField(max_length=1, choices=Escolaridade.choices, null=True)
    estudando = models.CharField(max_length=255, choices=Estudando.choices, null=True)
    artigo_criminal = models.CharField(max_length=255, null=True)
    cidade = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    matricula = models.CharField(
        max_length=10,
        null=True,  # Permite valores nulos
        blank=True,  # Permite que o campo fique vazio
        validators=[RegexValidator(regex=r'^\d{1,30}$', message="A matrícula deve conter apenas números (até 10 dígitos).")]
    )



    # Campo para indicar se o interno está fora
    saiu_temporariamente = models.BooleanField(default=False)  # Indica se o interno está fora da penitenciária

    albergado = models.BooleanField(default=False)  # Indica se o interno está albergado (em liberdade condicional ou outra situação)

    # Novo campo de status
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='ativo',  # Define "Ativo" como padrão
    )

    def __str__(self):
        return self.nome_completo

    def limpar_opcoes_associadas(self):
        self.frente_trabalho = ''
        self.cela = None
        self.bloco = None
        self.estudando = None
        self.eletronicos.all().delete()
        self.status = 'inativo'
        self.saiu_temporariamente = False
        self.albergado = False

        frentes_ativas = self.frentes_de_trabalho.filter(status='ativo')
        for frente in frentes_ativas:
            frente.status = 'revogado'
            frente.data_revogacao = timezone.now()
            frente.save()
            frente.gerar_pdf_revogacao()
            self.notificar_revogacao(frente.get_frente_trabalho_display(), motivo='transferência')



    def limpar_opcoes_associadas_para_albergado(self):
        self.cela = "0"
        self.bloco = "0"
        self.frente_trabalho = ''
        self.estudando = None

    def limpar_opcoes_associadas_para_status(self):
        if self.pd_is.filter(resultado="sobrestado").exists():
            self.status = "foragido"
            self.cela = None
            self.bloco = None
            self.estudando = None
            self.eletronicos.all().delete()
            self.saiu_temporariamente = False
            self.albergado = False

        elif self.pd_is.filter(resultado__in=["andamento", "condenado"]).exists():
            self.status = "ativo"

    # Definição correta do método dentro da classe
    def limpar_opcoes_associadas_para_alvara(self):
        self.cela = None
        self.bloco = None
        self.estudando = None
        if self.status not in ['foragido', 'ativo']:
            self.status = 'inativo'
        self.saiu_temporariamente = False
        self.albergado = False
        self.eletronicos.all().delete()

        frentes_ativas = self.frentes_de_trabalho.filter(status='ativo')
        for frente in frentes_ativas:
            frente.status = 'revogado'
            frente.data_revogacao = timezone.now()
            frente.save()
            frente.gerar_pdf_revogacao()
            self.notificar_revogacao(frente, motivo='alvará')



    def get_idade(self):
        if self.data_nascimento:
            hoje = date.today()
            return hoje.year - self.data_nascimento.year - (
                (hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day)
            )
        return None  # Retorna None se não houver data de nascimento

    def notificar_revogacao(self, frente, motivo):
        from django.contrib.auth import get_user_model
        from notification.models import Notificacao
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync

        User = get_user_model()

        mensagem = (
            f"Revogação automática\n"
            f"Portaria de Revogação Nº {frente.numero_portaria_revogacao}\n"
            f"A frente de trabalho \"{frente.get_frente_trabalho_display()}\" foi revogada "
            f"devido a {motivo.lower()} do interno."
        )

        notificacao = Notificacao.objects.create(
            tipo='revogacao',
            titulo=self.nome_completo,
            mensagem=mensagem,
            pessoa=self,
            criado_por=None,
            grau='importante'
        )
        notificacao.usuarios.set(User.objects.all())

        # Enviar via WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'notifications_group',
            {
                'type': 'send_notification',
                'message': f'[REVOGAÇÃO] {mensagem}'
            }
        )


    def save(self, *args, **kwargs):
        if self.nome_completo:
            self.nome_completo = unidecode(self.nome_completo)

        ignorar_status_auto = kwargs.pop('ignorar_status_auto', False)

        if self.pk is None:
            super().save(*args, **kwargs)

        if not ignorar_status_auto:
            if self.tem_transferencia_ativa:
                self.limpar_opcoes_associadas()
            elif self.albergado:
                self.limpar_opcoes_associadas_para_albergado()
            self.limpar_opcoes_associadas_para_status()
            if self.status == 'inativo':
                self.limpar_opcoes_associadas_para_alvara()

        super().save(*args, **kwargs)


class HistoricoAlteracao(models.Model):
    pessoa = models.ForeignKey(Pessoa, on_delete=models.CASCADE, related_name='historico_alteracoes')
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    campo_alterado = models.CharField(max_length=50)
    valor_antigo = models.CharField(max_length=100)
    valor_novo = models.CharField(max_length=100)
    data_alteracao = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Alteração de {self.campo_alterado} para {self.valor_novo}"

class PessoaForm(forms.ModelForm):
    class Meta:
        model = Pessoa
        fields = ['nome_completo']

class Transferencia(models.Model):
    pessoa = models.ForeignKey('Pessoa', on_delete=models.CASCADE)
    penitenciaria_destino = models.CharField(max_length=255, default='Não Definido')  # Definindo valor padrão
    data_transferencia = models.DateTimeField(null=True, blank=True)
    justificativa = models.TextField(default='Sem justificativa')  # Definindo valor padrão
    transferencia_ativa = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transferência para {self.pessoa} - {self.penitenciaria_destino}"


from django.db import models
from datetime import datetime

class FrenteDeTrabalho(models.Model):
    # Opções de trabalho
    NAO_TRABALHA = 'nao_trabalha'
    HORTA = 'horta'
    PISCICULTURA = 'piscicultura'
    MINHOCARIO = 'minhocario'
    LIMPEZA = 'limpeza'
    MANUTENCAO = 'manutencao'
    FABRICA_DE_BLOCOS = 'fabrica_blocos'
    CROCHE = 'croche'
    DIGITALIZADOR = 'digitalizador'
    BIBLIOTECARIO = 'bibliotecario'
    FACILITADOR = 'facilitador'
    SERVICOS_GERAIS = 'servicos_gerais'

    FRONTEIRAS_TRABALHO_CHOICES = [
        (NAO_TRABALHA, 'Não há'),
        (HORTA, 'Horta'),
        (PISCICULTURA, 'Piscicultura'),
        (MINHOCARIO, 'Minhocário'),
        (LIMPEZA, 'Limpeza'),
        (MANUTENCAO, 'Manutenção'),
        (FABRICA_DE_BLOCOS, 'Fáb. de Blocos'),
        (CROCHE, 'Crochê'),
        (DIGITALIZADOR, 'Digitalizador'),
        (BIBLIOTECARIO, 'Bibliotecário'),
        (FACILITADOR, 'Facilitador'),
        (SERVICOS_GERAIS, 'Serviços Gerais'),
    ]

    ATIVO = 'ativo'
    REVOGADO = 'revogado'

    STATUS_CHOICES = [
        (ATIVO, 'Ativo'),
        (REVOGADO, 'Revogado'),
    ]

    pessoa = models.ForeignKey(Pessoa, on_delete=models.CASCADE, related_name='frentes_de_trabalho')
    frente_trabalho = models.CharField(max_length=50, choices=FRONTEIRAS_TRABALHO_CHOICES, default=NAO_TRABALHA)
    data_inicio = models.DateField()
    numero_portaria_admissao = models.CharField(max_length=50)
    numero_portaria_revogacao = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
    )
    data_retroacao = models.DateField(null=True, blank=True)
    data_revogacao = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=ATIVO)
    pdf_revogacao = models.FileField(upload_to='revogacoes/', null=True, blank=True)

    def get_frente_trabalho_com_artigo(self):
        """Retorna a frente de trabalho com o artigo adequado (ou preposição 'como') para uso em textos formais."""

        mapa_formatado = {
            self.CROCHE: 'Artesanato',
            self.MANUTENCAO: 'Manutenção e Conservação Predial',
            self.FABRICA_DE_BLOCOS: 'Fábrica de Blocos',
        }

        nome = mapa_formatado.get(self.frente_trabalho, self.get_frente_trabalho_display())

        # Frentes com artigo definido (locais)
        frentes_com_artigo_feminino = {
            'Horta', 'Piscicultura', 'Limpeza', 'Fábrica de Blocos', 'Manutenção e Conservação Predial'
        }

        frentes_com_artigo_masculino = {
            'Minhocário'
        }

        if nome in frentes_com_artigo_feminino:
            return f"na {nome}"
        elif nome in frentes_com_artigo_masculino:
            return f"no {nome}"
        else:
            # Considera como função/cargo
            return f"como {nome}"


    def gerar_pdf_revogacao(self):
        """ Gera e salva o PDF de revogação da frente de trabalho """

        # 1. Tratamento robusto das imagens para evitar erro NoneType
        img_seap_base64 = ""
        img_logo_base64 = ""

        img_seap_path = finders.find('imagens/seap.png')
        img_logo_path = finders.find('imagens/logo_maranhao_seap.png')

        try:
            if img_seap_path:
                with open(img_seap_path, 'rb') as img_file:
                    img_seap_base64 = base64.b64encode(img_file.read()).decode('utf-8')

            if img_logo_path:
                with open(img_logo_path, 'rb') as img_file:
                    img_logo_base64 = base64.b64encode(img_file.read()).decode('utf-8')
        except Exception as e:
            print(f"⚠️ Aviso: Erro ao carregar imagens para o PDF: {e}")
            # Prossegue mesmo sem imagem para não travar o sistema

        locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')

        data_retroacao_formatada = self.data_retroacao.strftime('%d de %B de %Y') if self.data_retroacao else "N/A"
        data_hoje_formatada = timezone.now().strftime('%d de %B de %Y')

        context = {
            'img_seap_base64': img_seap_base64,
            'img_logo_base64': img_logo_base64,
            'tempo_geracao': timezone.now().strftime('%d/%m/%Y %H:%M:%S'),
            'pessoa': self.pessoa,
            'frente_trabalho': self.get_frente_trabalho_com_artigo(),
            'data_inicio': self.data_inicio.strftime('%d/%m/%Y') if self.data_inicio else "N/A",
            'numero_portaria_revogacao': self.numero_portaria_revogacao,
            'data_revogacao': self.data_revogacao.strftime('%d/%m/%Y') if self.data_revogacao else "N/A",
            'data_retroacao': data_retroacao_formatada,
            'numero_portaria_admissao': self.numero_portaria_admissao,
            'data_hoje': data_hoje_formatada,
        }

        template_path = 'pdf/revogar_trabalho.html'
        template = get_template(template_path)
        html = template.render(context)

        # 2. Pasta baseada no ano da revogação (coerência com a portaria)
        ano_doc = self.data_revogacao.year if self.data_revogacao else timezone.now().year
        pdf_dir = os.path.join(settings.MEDIA_ROOT, f'Revogações no Ano de {ano_doc}')
        os.makedirs(pdf_dir, exist_ok=True)

        # Nome do arquivo limpo
        pdf_filename = f"Revogação_{self.pessoa.nome_completo}_{self.numero_portaria_revogacao}".replace("/", "-").replace(" ", "_") + ".pdf"
        pdf_path = os.path.join(pdf_dir, pdf_filename)

        # Gerar o PDF
        with open(pdf_path, "wb") as pdf_file:
            HTML(string=html).write_pdf(pdf_file)

        # 3. Atualizar apenas o campo do PDF sem disparar o save() completo novamente
        # Isso evita que a lógica de numeração seja executada duas vezes
        relative_path = f"Revogações no Ano de {ano_doc}/{pdf_filename}"
        FrenteDeTrabalho.objects.filter(id=self.id).update(pdf_revogacao=relative_path)

        return pdf_path

    def save(self, *args, **kwargs):
        # Agora não temos mais um número inicial fixo global.
        # O sistema sempre buscará o maior do ano vigente ou começará do 0.

        if self.data_revogacao and not self.numero_portaria_revogacao:
            # Pega o ano da data de revogação definida na View (ex: 2026)
            ano_atual = self.data_revogacao.year
            print(f"🔍 [SAVE] Verificando numeração para o ciclo de {ano_atual}")

            # Filtra apenas registros que REALMENTE pertencem ao ano atual
            # e que já possuem um número de portaria gerado
            registros_do_ano = FrenteDeTrabalho.objects.filter(
                data_revogacao__year=ano_atual,
                numero_portaria_revogacao__isnull=False
            ).exclude(numero_portaria_revogacao="")

            if registros_do_ano.exists():
                maiores_numeros = []
                for reg in registros_do_ano:
                    try:
                        # Extrai o número antes da barra (ex: de "005/2026" pega "005")
                        num_str = reg.numero_portaria_revogacao.split('/')[0]
                        maiores_numeros.append(int(num_str))
                    except (ValueError, IndexError, AttributeError):
                        continue

                ultimo_numero = max(maiores_numeros) if maiores_numeros else 0
                print(f"📈 [SAVE] Já existem registros em {ano_atual}. Maior atual: {ultimo_numero}")
            else:
                # Se cair aqui, é porque é o primeiro registro de 2026, ou 2027, etc.
                print(f"✨ [SAVE] Nenhum registro encontrado para {ano_atual}. Reiniciando contagem para 001.")
                ultimo_numero = 0

            # Gera o novo número: ex 0 + 1 = "001/2026"
            self.numero_portaria_revogacao = f"{ultimo_numero + 1:03}/{ano_atual}"
            print(f"🆔 [SAVE] Resultado final: {self.numero_portaria_revogacao}")

        if self.data_revogacao:
            self.status = self.REVOGADO

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.pessoa} - {self.get_frente_trabalho_display()} ({self.get_status_display()})"

class Sancao(models.Model):
    TIPOS_SANCAO = [
        ('sem_castelo', 'Sem Castelo'),
        ('sem_visita_intima', 'Sem Visita Íntima'),
        ('sem_visita_social', 'Sem Visita Social'),
        ('isolamento_preventivo', 'Isolamento Preventivo'),
        ('isolamento_reflexao', 'Isolamento Reflexivo'),
    ]

    pessoa = models.ForeignKey(Pessoa, on_delete=models.CASCADE, related_name='sancoes')
    tipo = models.CharField(max_length=50, choices=TIPOS_SANCAO, blank=True)
    descricao = models.TextField(blank=True, null=True)
    data_inicio = models.DateTimeField(blank=True, null=True)
    data_fim = models.DateTimeField(blank=True, null=True)
    def __str__(self):
        return f"{self.pessoa.nome_completo} - {self.tipo}"

from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now



from django.template.loader import get_template
import os
from django.conf import settings
from weasyprint import HTML
import locale
import base64
from django.contrib.staticfiles import finders
from django.utils import timezone
from django.db import models

class PDI(models.Model):
    NATUREZA_PDI = [
        ('leve', 'Leve'),
        ('media', 'Média'),
        ('grave', 'Grave'),
    ]

    RESULTADOS_CHOICES = [
        ('andamento', 'Andamento'),
        ('condenado', 'Condenado'),
        ('sobrestado', 'Sobrestado',)
    ]

    pessoa = models.ForeignKey(Pessoa, on_delete=models.CASCADE, related_name='pd_is')
    numero_pdi = models.CharField(max_length=20, verbose_name="Nº PDI", default="PDI-0000")
    numero_ocorrencia = models.CharField(max_length=20, verbose_name="Nº Ocorrência", default="OCC-0000")
    natureza = models.CharField(max_length=50, choices=NATUREZA_PDI, blank=True)
    descricao = models.TextField(blank=True, null=True)
    data_inicio = models.DateTimeField(blank=True, null=True)
    data_fim = models.DateTimeField(blank=True, null=True)
    resultado = models.CharField(max_length=20, choices=RESULTADOS_CHOICES, blank=True, verbose_name="Resultado")


    def save(self, *args, **kwargs):
        # Converte as datas para "aware" (com fuso horário)
        if self.data_inicio and timezone.is_naive(self.data_inicio):
            self.data_inicio = timezone.make_aware(self.data_inicio)

        if self.data_fim and timezone.is_naive(self.data_fim):
            self.data_fim = timezone.make_aware(self.data_fim)

        # Atualiza o status da pessoa baseado no resultado do PDI
        if self.resultado == 'sobrestado':
            self.pessoa.status = 'foragido'  # Sobrestado = Foragido
        elif self.resultado in ['andamento', 'condenado']:
            self.pessoa.status = 'ativo'  # Andamento e Condenado = Ativo

        self.pessoa.save()  # Salva a pessoa com o novo status

        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.pessoa.nome_completo} - {self.get_natureza_display()}"




class Eletronico(models.Model):
    TIPOS_ELETRONICO = [
        ('tv', 'Tv'),
        ('radio', 'Rádio'),
        ('ventilador', 'Ventilador'),  # Novo tipo
    ]

    pessoa = models.ForeignKey(Pessoa, on_delete=models.CASCADE, related_name='eletronicos')
    tipo = models.CharField(max_length=50, choices=TIPOS_ELETRONICO, blank=True)
    data_entrada = models.DateField(null=True, blank=True)
    nova_fiscal = models.FileField(upload_to='eletronicos/fiscais/', blank=True, null=True)  # Receberá arquivos do computador

    def __str__(self):
        return f"{self.tipo.capitalize()} - {self.pessoa.nome_completo}"




