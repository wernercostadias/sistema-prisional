from django.db import models
from django.utils.timezone import now

# ============================================
# Livro (catálogo)
# ============================================
class Livro(models.Model):
    titulo = models.CharField(max_length=255)
    autor = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.titulo


# ============================================
# Exemplar do Livro (cada cópia na biblioteca)
# ============================================
class Exemplar(models.Model):
    livro = models.ForeignKey(Livro, on_delete=models.CASCADE, related_name="exemplares")
    codigo = models.CharField(max_length=50, unique=True)  # código único do exemplar
    disponivel = models.BooleanField(default=True)  # se está disponível para leitura

    def __str__(self):
        return f"{self.livro.titulo} - Código: {self.codigo} ({'Disponível' if self.disponivel else 'Indisponível'})"


# ============================================
# Ciclo de Leitura (mês/ano)
# ============================================
from django.db import models
from django.utils.timezone import now

from django.db import models
from django.utils.timezone import now

class CicloLeitura(models.Model):
    numero = models.IntegerField(default=1)  # Ciclo nominal: 1 a 12
    ano = models.IntegerField(default=2025)  # Ano nominal do ciclo
    inicio = models.DateField(null=True, blank=True)  # Pode começar no ano anterior
    fim = models.DateField(null=True, blank=True)     # Pode terminar no ano seguinte

    class Meta:
        ordering = ["ano", "numero"]
        unique_together = ("numero", "ano")

    def __str__(self):
        if self.inicio and self.fim:
            return f"Ciclo {self.numero}/{self.ano} - {self.inicio.strftime('%d/%m/%Y')} a {self.fim.strftime('%d/%m/%Y')}"
        return f"Ciclo {self.numero}/{self.ano} - Datas não definidas"

    @classmethod
    def ciclo_atual(cls, data=None):
        """
        Retorna o ciclo em andamento ou None.
        Mesmo que o ciclo atravesse anos, considera o intervalo real.
        """
        data = data or now().date()
        return cls.objects.filter(inicio__lte=data, fim__gte=data).first()

    @classmethod
    def proximo_ciclo_numerico(cls):
        """
        Retorna o próximo ciclo baseado no último ciclo concluído.
        Considera que os ciclos podem atravessar anos.
        """
        ultimo_ciclo = cls.objects.filter(fim__lt=now().date()).order_by('-ano', '-numero').first()
        if ultimo_ciclo:
            # Primeiro tenta pegar o próximo ciclo nominal no mesmo ano
            proximo = cls.objects.filter(numero=ultimo_ciclo.numero + 1, ano=ultimo_ciclo.ano).first()
            if proximo:
                return proximo
            # Se não existir, pega o próximo ciclo do próximo ano
            return cls.objects.filter(ano__gt=ultimo_ciclo.ano).order_by('ano', 'numero').first()
        else:
            # Se não houver ciclo concluído, retorna o ciclo atual ou o primeiro que vai iniciar
            return cls.ciclo_atual() or cls.objects.filter(inicio__gt=now().date()).order_by("inicio").first()





# ============================================
# Registro de leitura (quem leu o quê em qual ciclo)
# ============================================
class Leitura(models.Model):
    pessoa = models.ForeignKey("painel.Pessoa", on_delete=models.CASCADE, related_name="leituras")
    livro = models.ForeignKey(Livro, on_delete=models.CASCADE)
    ciclo = models.ForeignKey(CicloLeitura, on_delete=models.CASCADE, null=True, blank=True)
    exemplar = models.ForeignKey(Exemplar, on_delete=models.SET_NULL, null=True, blank=True)
    data_leitura = models.DateField(auto_now_add=True)

    # Novo campo
    ciclo_indefinido = models.BooleanField(default=False)

    class Meta:
        unique_together = ("pessoa", "livro", "ciclo")
        ordering = ["ciclo", "livro"]

    def __str__(self):
        if self.ciclo_indefinido:
            return f"{self.pessoa.nome_completo} - {self.livro.titulo} (Ciclo Indefinido)"
        elif self.ciclo:
            return f"{self.pessoa.nome_completo} - {self.livro.titulo} (Ciclo {self.ciclo.numero}/{self.ciclo.ano})"
        return f"{self.pessoa.nome_completo} - {self.livro.titulo} (Sem ciclo registrado)"



# ============================================
# Fila de Espera
# ============================================
class FilaDeEspera(models.Model):
    pessoa = models.OneToOneField("painel.Pessoa", on_delete=models.CASCADE, related_name="fila_espera")
    data_inclusao = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Fila: {self.pessoa.nome_completo}"



# ============================================
# Frente de Leitura (internos ativos lendo)
# ============================================
from django.utils.timezone import now

class FrenteDeLeitura(models.Model):
    pessoa = models.OneToOneField("painel.Pessoa", on_delete=models.CASCADE, related_name="frente_leitura")
    exemplar = models.ForeignKey(Exemplar, on_delete=models.CASCADE, null=True, blank=True)
    ciclo = models.ForeignKey(CicloLeitura, on_delete=models.CASCADE, null=True, blank=True)
    data_inicio = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def livros_lidos_no_ciclo(self):
        ciclo_atual = CicloLeitura.ciclo_atual()  # pega o ciclo atual baseado nas datas
        if not ciclo_atual:
            return 0
        return self.pessoa.leituras.filter(ciclo=ciclo_atual).count()

    def __str__(self):
        return f"Ativo: {self.pessoa.nome_completo} ({self.exemplar} - {self.ciclo})"

    # =============================
    # Função para avançar o ciclo
    # =============================
    def avancar_ciclo(self):
        if not self.ciclo:
            return None  # Nenhum ciclo atual definido

        # Só avança se a data de fim do ciclo já passou
        if not self.ciclo.fim or self.ciclo.fim >= now().date():
            return None  # Ainda não terminou, não avança

        ciclo_atual_num = self.ciclo.numero
        ano_atual = self.ciclo.ano

        # Tenta buscar o próximo ciclo no mesmo ano
        proximo_num = ciclo_atual_num + 1
        proximo_ciclo = CicloLeitura.objects.filter(numero=proximo_num, ano=ano_atual).first()

        # Se não existir, vai para o ciclo 1 do próximo ano
        if not proximo_ciclo:
            proximo_ciclo = CicloLeitura.objects.filter(numero=1, ano=ano_atual + 1).first()

        # Atualiza o ciclo do interno
        if proximo_ciclo:
            self.ciclo = proximo_ciclo
            self.save()
            return self.ciclo

        return None





# ============================================
# Histórico de Leitura (quem já saiu da frente)
# ============================================
class HistoricoLeitura(models.Model):
    MOTIVO_SAIDA_CHOICES = [
        ("concluido", "Concluiu o ciclo"),
        ("transferencia", "Transferência"),
        ("outro", "Outro motivo"),
    ]

    pessoa = models.ForeignKey("painel.Pessoa", on_delete=models.CASCADE, related_name="historico_leitura")
    ciclo = models.CharField(max_length=100, default="Ciclo 1") 
    data_saida = models.DateField(auto_now_add=True)
    livros_lidos = models.PositiveIntegerField(default=0)
    motivo_saida = models.CharField(max_length=20, 
    choices=MOTIVO_SAIDA_CHOICES)

    def __str__(self):
        return f"Histórico: {self.pessoa.nome_completo} - {self.ciclo}"
