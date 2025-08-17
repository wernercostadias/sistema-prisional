import os
import django
from unidecode import unidecode

# Configuração para Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "banco_de_dados_upaca.settings")
django.setup()

# Importação do modelo
from painel.models import Pessoa

# Atualizar os registros existentes removendo os acentos
for obj in Pessoa.objects.all():
    obj.nome_completo = unidecode(obj.nome_completo)
    obj.save()

print("Atualização concluída!")
