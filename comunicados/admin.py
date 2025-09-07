from django.contrib import admin
from .models import Comunicado

@admin.register(Comunicado)
class ComunicadoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'data', 'criado_em')  # Colunas exibidas na lista do admin
    list_filter = ('data',)                         # Filtro lateral por data
    search_fields = ('titulo', 'conteudo')          # Barra de pesquisa
    ordering = ('-data',)                           # Ordena do mais recente para o mais antigo
