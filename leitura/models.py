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
class CicloLeitura(models.Model):
    MES_CHOICES = [
        (1, "Janeiro"), (2, "Fevereiro"), (3, "Março"),
        (4, "Abril"), (5, "Maio"), (6, "Junho"),
        (7, "Julho"), (8, "Agosto"), (9, "Setembro"),
        (10, "Outubro"), (11, "Novembro"), (12, "Dezembro"),
    ]

    mes = models.PositiveSmallIntegerField(choices=MES_CHOICES)
    ano = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ("mes", "ano")
        ordering = ["ano", "mes"]

    def __str__(self):
        return f"{self.get_mes_display()}/{self.ano}"


# ============================================
# Registro de leitura (quem leu o quê em qual ciclo)
# ============================================
class Leitura(models.Model):
    pessoa = models.ForeignKey("painel.Pessoa", on_delete=models.CASCADE, related_name="leituras")
    livro = models.ForeignKey(Livro, on_delete=models.CASCADE)
    ciclo = models.ForeignKey(CicloLeitura, on_delete=models.CASCADE)
    exemplar = models.ForeignKey(Exemplar, on_delete=models.SET_NULL, null=True, blank=True)  # <- novo
    data_leitura = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ("pessoa", "livro", "ciclo")
        ordering = ["ciclo", "livro"]

    def __str__(self):
        return f"{self.pessoa.nome_completo} - {self.livro.titulo} ({self.ciclo})"


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
class FrenteDeLeitura(models.Model):
    pessoa = models.OneToOneField("painel.Pessoa", on_delete=models.CASCADE, related_name="frente_leitura")
    exemplar = models.ForeignKey(Exemplar, on_delete=models.CASCADE, null=True, blank=True)
    ciclo = models.ForeignKey(CicloLeitura, on_delete=models.CASCADE, null=True, blank=True)
    data_inicio = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def livros_lidos_no_ciclo(self):
        mes, ano = now().month, now().year
        ciclo_atual, _ = CicloLeitura.objects.get_or_create(mes=mes, ano=ano)
        return self.pessoa.leituras.filter(ciclo=ciclo_atual).count()

    def __str__(self):
        return f"Ativo: {self.pessoa.nome_completo} ({self.exemplar} - {self.ciclo})"



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
