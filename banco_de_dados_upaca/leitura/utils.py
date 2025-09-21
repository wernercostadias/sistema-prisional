# ============================================
# Imports
# ============================================
from .models import Leitura, Livro       # models do próprio app leitura
from painel.models import Pessoa   

# ============================================
# Função utilitária
# ============================================
def ja_leu_livro(pessoa_id, livro_id):
    """
    Verifica se a pessoa já leu o livro.
    Retorna True se já leu, False caso contrário.
    """
    pessoa = Pessoa.objects.get(id=pessoa_id)
    livro = Livro.objects.get(id=livro_id)
    return Leitura.objects.filter(pessoa=pessoa, livro=livro).exists()
