# painel/admin.py
from django.contrib import admin
from .models import Pessoa, HistoricoAlteracao, Transferencia, Sancao, Eletronico, PDI, FrenteDeTrabalho

from .forms import PessoaForm  # Importando o formulário
from django.contrib.admin.models import LogEntry


# Criando uma classe de admin personalizada para o modelo Pessoa
class PessoaAdmin(admin.ModelAdmin):
    form = PessoaForm
    list_display = ('nome_completo', 'matricula', 'data_nascimento', 'data_entrada', 'bloco', 'cela', 'status', 'tem_transferencia_ativa', 'saiu_temporariamente', 'albergado')
    list_filter = ('bloco', 'cela', 'escolaridade', 'estudando', 'status', 'tem_transferencia_ativa', 'saiu_temporariamente', 'albergado')
    search_fields = ('nome_completo', 'matricula', 'data_nascimento', 'artigo_criminal', 'cidade', 'status')
    ordering = ('nome_completo',)
    readonly_fields = ('created_at',)
    actions = ['marcar_como_inativo', 'marcar_como_ativo']

    fieldsets = (
        (None, {
            'fields': ('nome_completo', 'matricula', 'data_nascimento', 'data_entrada', 'status')
        }),
        ('Localização', {
            'fields': ('bloco', 'cela', 'cidade')
        }),
        ('Atividades', {
            'fields': ('escolaridade', 'estudando')
        }),
        ('Situação Penal', {
            'fields': ('artigo_criminal', 'tem_transferencia_ativa', 'saiu_temporariamente', 'albergado')
        }),
        ('Outros', {
            'fields': ('created_at',)
        }),
    )

    def marcar_como_inativo(self, request, queryset):
        queryset.update(status='inativo')
    marcar_como_inativo.short_description = "Marcar como Inativo"

    def marcar_como_ativo(self, request, queryset):
        queryset.update(status='ativo')
    marcar_como_ativo.short_description = "Marcar como Ativo"

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

from django.contrib import admin
from django.utils.html import format_html
from .models import FrenteDeTrabalho

@admin.register(FrenteDeTrabalho)
class FrenteDeTrabalhoAdmin(admin.ModelAdmin):
    # Colunas exibidas na lista
    list_display = (
        'pessoa',
        'frente_trabalho_formatado',
        'data_inicio',
        'numero_portaria_admissao',
        'numero_portaria_revogacao',
        'data_retroacao',
        'data_revogacao',
        'status',
        'link_pdf_revogacao',
    )

    # Campos que serão links para abrir o detalhe
    list_display_links = ('pessoa', 'frente_trabalho_formatado')

    # Filtros avançados na lateral
    list_filter = (
        'frente_trabalho',
        'status',
        ('data_inicio', admin.DateFieldListFilter),
        ('data_revogacao', admin.DateFieldListFilter),
    )

    # Pesquisa por campos relacionais e texto
    search_fields = ('pessoa__nome_completo', 'numero_portaria_admissao', 'numero_portaria_revogacao')

    # Campos editáveis na edição do objeto
    fields = (
        'pessoa',
        'frente_trabalho',
        'data_inicio',
        'numero_portaria_admissao',
        'numero_portaria_revogacao',
        'data_retroacao',
        'data_revogacao',
        'status',
        'pdf_revogacao',
    )

    # Ordenação padrão da lista
    ordering = ('-data_inicio',)

    # Paginação na lista para melhorar performance e visual
    list_per_page = 30

    # Campos somente leitura (exemplo: numero_portaria_revogacao é gerado no save)
    readonly_fields = ('numero_portaria_revogacao', 'status', 'link_pdf_revogacao')

    # Campos em formato dinâmico para exibir artigos e links
    def frente_trabalho_formatado(self, obj):
        # Usa o método do modelo para mostrar a frente com artigo
        return obj.get_frente_trabalho_com_artigo()
    frente_trabalho_formatado.short_description = 'Frente de Trabalho'

    def link_pdf_revogacao(self, obj):
        if obj.pdf_revogacao:
            return format_html('<a href="{}" target="_blank">Ver PDF</a>', obj.pdf_revogacao.url)
        return "-"
    link_pdf_revogacao.short_description = 'PDF Revogação'

    # Para melhorar a visualização, pode usar cores no status
    def status_colored(self, obj):
        color = 'green' if obj.status == obj.ATIVO else 'red'
        return format_html(
            '<strong><span style="color: {};">{}</span></strong>',
            color,
            obj.get_status_display()
        )
    status_colored.short_description = 'Status'
    status_colored.admin_order_field = 'status'

    # Substituir o campo status na list_display pela versão colorida
    list_display = (
        'pessoa',
        'frente_trabalho_formatado',
        'data_inicio',
        'numero_portaria_admissao',
        'numero_portaria_revogacao',
        'data_retroacao',
        'data_revogacao',
        'status_colored',
        'link_pdf_revogacao',
    )

    # Permitindo edição rápida de alguns campos direto da lista (opcional)
    list_editable = ('data_revogacao',)

    # Campos com filtros por data mais detalhados
    date_hierarchy = 'data_inicio'
