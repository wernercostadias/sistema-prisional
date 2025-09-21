from django.contrib import admin
from .models import Notificacao, NotificacaoUsuario

class NotificacaoUsuarioInline(admin.TabularInline):
    model = NotificacaoUsuario
    extra = 1

@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
    list_display = (
        'titulo',
        'tipo',
        'grau',
        'data_criacao',
        'criado_por',
        'get_usuarios',
    )
    list_filter = ('tipo', 'grau', 'data_criacao')
    search_fields = ('titulo', 'mensagem', 'pessoa__nome_completo', 'criado_por__username', 'notificacaousuario__usuario__username')
    inlines = [NotificacaoUsuarioInline]

    def get_usuarios(self, obj):
        return ", ".join([nu.usuario.username for nu in obj.notificacaousuario_set.all()])
    get_usuarios.short_description = 'Usuários'

@admin.register(NotificacaoUsuario)
class NotificacaoUsuarioAdmin(admin.ModelAdmin):
    list_display = ('notificacao', 'usuario', 'lida')
    list_filter = ('lida', 'notificacao__tipo', 'notificacao__grau')
    search_fields = ('notificacao__titulo', 'usuario__username')
