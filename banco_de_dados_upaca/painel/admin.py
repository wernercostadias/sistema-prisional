# painel/admin.py
from django.contrib import admin
from .models import Pessoa, HistoricoAlteracao, Transferencia, Sancao, Eletronico, PDI, Notification  # Importando Notification

from .forms import PessoaForm  # Importando o formulário
from django.contrib.admin.models import LogEntry
# Administrador de Notificação
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'titulo', 'tipo', 'data_criacao', 'lida')
    list_filter = ('tipo', 'lida', 'data_criacao')
    search_fields = ('usuario__username', 'titulo', 'mensagem')
    ordering = ('-data_criacao',)
    actions = ['marcar_como_lida']

    def marcar_como_lida(self, request, queryset):
        queryset.update(lida=True)
    marcar_como_lida.short_description = "Marcar como lida"

admin.site.register(Notification, NotificationAdmin)

# Criando uma classe de admin personalizada para o modelo Pessoa
class PessoaAdmin(admin.ModelAdmin):
    form = PessoaForm
    list_display = ('nome_completo', 'idade', 'data_entrada', 'bloco', 'cela',)
    list_filter = ('bloco', 'cela', 'escolaridade', 'estudando',)
    search_fields = ('nome_completo', 'idade', 'artigo_criminal', 'cidade')
    ordering = ('nome_completo',)
    fieldsets = (
        (None, {
            'fields': ('nome_completo', 'idade', 'data_entrada', 'bloco', 'cela')
        }),
        ('Detalhes adicionais', {
            'fields': (
                'escolaridade', 'estudando',
                'artigo_criminal', 'cidade'
            ),
        }),
    )

    def is_sancao_ativa(self, obj):
        return obj.is_sancao_ativa()
    is_sancao_ativa.boolean = True
    is_sancao_ativa.short_description = 'Sanção Ativa'

admin.site.register(Pessoa, PessoaAdmin)

# Administrador do HistoricoAlteracao
class HistoricoAlteracaoAdmin(admin.ModelAdmin):
    list_display = ('pessoa', 'usuario', 'campo_alterado', 'valor_antigo', 'valor_novo', 'data_alteracao')
    list_filter = ('campo_alterado', 'data_alteracao', 'usuario')
    search_fields = ('pessoa__nome_completo', 'campo_alterado', 'valor_antigo', 'valor_novo')
    date_hierarchy = 'data_alteracao'
    ordering = ('-data_alteracao',)

admin.site.register(HistoricoAlteracao, HistoricoAlteracaoAdmin)

# Administrador da Transferencia
class TransferenciaAdmin(admin.ModelAdmin):
    list_display = ('pessoa', 'penitenciaria_destino', 'data_transferencia', 'transferencia_ativa')
    list_filter = ('transferencia_ativa', 'data_transferencia', 'penitenciaria_destino')
    search_fields = ('pessoa__nome_completo', 'penitenciaria_destino')
    ordering = ('-data_transferencia',)
    fieldsets = (
        (None, {
            'fields': ('pessoa', 'penitenciaria_destino', 'data_transferencia', 'justificativa', 'transferencia_ativa')
        }),
    )

admin.site.register(Transferencia, TransferenciaAdmin)

# Administrador da Sancao
class SancaoAdmin(admin.ModelAdmin):
    list_display = ('pessoa', 'tipo', 'descricao', 'data_inicio', 'data_fim')
    list_filter = ('tipo', 'data_inicio', 'data_fim')
    search_fields = ('pessoa__nome_completo', 'tipo', 'descricao')
    ordering = ('-data_inicio',)

admin.site.register(Sancao, SancaoAdmin)

# Administrador do Eletronico
class EletronicoAdmin(admin.ModelAdmin):
    list_display = ('pessoa', 'tipo', 'data_entrada', 'nova_fiscal')
    list_filter = ('tipo', 'data_entrada')
    search_fields = ('pessoa__nome_completo', 'tipo')
    ordering = ('-data_entrada',)

admin.site.register(Eletronico, EletronicoAdmin)

# Administrador do PDI
class PDIAdmin(admin.ModelAdmin):
    list_display = ('pessoa', 'natureza', 'descricao', 'data_inicio', 'data_fim')
    list_filter = ('natureza', 'data_inicio', 'data_fim')
    search_fields = ('pessoa__nome_completo', 'descricao')
    ordering = ('-data_inicio',)
    fieldsets = (
        (None, {
            'fields': ('pessoa', 'natureza', 'descricao')
        }),
        ('Datas', {
            'fields': ('data_inicio', 'data_fim'),
        }),
    )

admin.site.register(PDI, PDIAdmin)


# Exibindo Logs de Administração
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'content_type', 'object_id', 'change_message', 'action_time')
    list_filter = ('action_flag', 'user', 'content_type')
    search_fields = ('content_type__model', 'change_message')
    ordering = ('-action_time',)

admin.site.register(LogEntry, LogEntryAdmin)

