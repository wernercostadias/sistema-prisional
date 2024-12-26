from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django import forms
from django.db.models.signals import post_save
from django.dispatch import receiver


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


    class FrenteDeTrabalho(models.TextChoices):
        NAO_TRABALHA = 'nao_trabalha', 'Não há'
        HORTA = 'horta', 'Horta'
        PISCICULTURA = 'piscicultura', 'Piscicultura'
        MINHOCARIO = 'minhocario', 'Minhocário'
        LIMPEZA = 'limpeza', 'Limpeza'
        MANUTENCAO = 'manutencao', 'Manutenção'
        FABRICA_DE_BLOCOS = 'fabrica_blocos', 'Fáb. de Blocos'
        CROCHE = 'croche', 'Crochê'
        DIGITALIZADOR = 'digitalizador', 'Digitalizador'
        BIBLIOTECARIO = 'bibliotecario', 'Bibliotecário'


    
    bloco = models.CharField(max_length=1, choices=[('A', 'Bloco A'), ('B', 'Bloco B'), ('C', 'Bloco C'), ('D', 'Bloco D'), ('E', 'Bloco E')], null=True)
    cela = models.CharField(max_length=2, choices=[('1', 'Cela 1'), ('2', 'Cela 2'), ('3', 'Cela 3'), ('4', 'Cela 4'), ('5', 'Cela 5'), ('6', 'Cela 6'), ('7', 'Cela 7')], null=True)
    tem_transferencia_ativa = models.BooleanField(default=False)
    nome_completo = models.CharField(max_length=255, null=True)
    idade = models.IntegerField(null=True)
    data_entrada = models.DateField(null=True)
    escolaridade = models.CharField(max_length=1, choices=Escolaridade.choices, null=True)
    estudando = models.CharField(max_length=255, choices=Estudando.choices, null=True)
    frente_trabalho = models.CharField(max_length=20, choices=FrenteDeTrabalho.choices)
    artigo_criminal = models.CharField(max_length=255, null=True)
    cidade = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    # Campo para indicar se o interno está fora
    saiu_temporariamente = models.BooleanField(default=False)  # Indica se o interno está fora da penitenciária

    
    def __str__(self):
        return self.nome_completo

    
    def limpar_opcoes_associadas(self):
        
        self.frente_trabalho = ''
        self.cela = None
        self.bloco = None
        self.estudando = None
        self.tipo_sancao = None
        self.artigo_criminal = None
        self.cidade = None
        self.tipo_eletronico = None
        self.eletronico = None
        self.escolaridade = None
        
        # Apaga os eletrônicos associados à pessoa
        self.eletronicos.all().delete()
        

    def save(self, *args, **kwargs):
        """Sobrescreve o método save para garantir que as opções sejam limpas quando necessário."""
        # Verifica se a transferência está ativa e se as opções ainda não foram limpas
        if self.tem_transferencia_ativa and not hasattr(self, '_opcoes_limpa'):
            self.limpar_opcoes_associadas()  # Chama o método para limpar as opções
            self._opcoes_limpa = True  # Marca que as opções foram limpas para evitar recursão
        super().save(*args, **kwargs)
        # Após salvar, remove a marcação '_opcoes_limpa' para permitir futuras execuções
        if hasattr(self, '_opcoes_limpa'):
            del self._opcoes_limpa

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
    


class Sancao(models.Model):
    TIPOS_SANCAO = [
        ('sem_castelo', 'Sem Castelo'),
        ('sem_visita_intima', 'Sem Visita Íntima'),
        ('sem_visita_social', 'Sem Visita Social'),
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

class Notification(models.Model):
    TIPOS_NOTIFICACAO = [
        ('warning', 'Aviso'),
        ('info', 'Informação'),
        ('success', 'Sucesso'),
        ('error', 'Erro'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificacoes')
    titulo = models.CharField(max_length=255)
    mensagem = models.TextField()
    tipo = models.CharField(max_length=50, choices=TIPOS_NOTIFICACAO, default='info')
    data_criacao = models.DateTimeField(default=now)
    lida = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.usuario.username} - {self.titulo}"

    class Meta:
        ordering = ['-data_criacao']
    
    
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




