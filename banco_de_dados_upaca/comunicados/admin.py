from django.contrib import admin
from django.db import models
from ckeditor.widgets import CKEditorWidget
from .models import Comunicado

@admin.register(Comunicado)
class ComunicadoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'data', 'criado_em')
    list_filter = ('data',)
    search_fields = ('titulo', 'conteudo')
    ordering = ('-data',)

    # Isso faz o campo 'conteudo' aparecer com o editor CKEditor
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget},
    }
