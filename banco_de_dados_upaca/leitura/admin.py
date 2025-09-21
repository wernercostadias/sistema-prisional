from django.contrib import admin
from .models import (
    Livro, Exemplar, CicloLeitura, Leitura,
    FilaDeEspera, FrenteDeLeitura, HistoricoLeitura
)

# ===========================
# Livro
# ===========================
@admin.register(Livro)
class LivroAdmin(admin.ModelAdmin):
    list_display = ("titulo", "autor")
    search_fields = ("titulo", "autor")


# ===========================
# Exemplar do Livro
# ===========================
@admin.register(Exemplar)
class ExemplarAdmin(admin.ModelAdmin):
    list_display = ("livro", "codigo", "disponivel")
    list_filter = ("disponivel", "livro")
    search_fields = ("codigo", "livro__titulo")


# ===========================
# Ciclo de Leitura
# ===========================
from django.contrib import admin
from .models import CicloLeitura

@admin.register(CicloLeitura)
class CicloLeituraAdmin(admin.ModelAdmin):
    list_display = ("numero", "ano", "inicio", "fim")
    list_filter = ("ano", "numero")
    ordering = ("-ano", "numero")
    search_fields = ("numero", "ano")
    readonly_fields = ("__str__",)  # opcional: mostrar a representação legível



# ===========================
# Leitura
# ===========================
@admin.register(Leitura)
class LeituraAdmin(admin.ModelAdmin):
    list_display = ("pessoa", "livro", "ciclo", "data_leitura")
    list_filter = ("ciclo", "livro")
    search_fields = ("pessoa__nome_completo", "livro__titulo")


# ===========================
# Fila de Espera
# ===========================
@admin.register(FilaDeEspera)
class FilaDeEsperaAdmin(admin.ModelAdmin):
    list_display = ("pessoa", "data_inclusao")
    search_fields = ("pessoa__nome_completo",)


# ===========================
# Frente de Leitura
# ===========================
@admin.register(FrenteDeLeitura)
class FrenteDeLeituraAdmin(admin.ModelAdmin):
    list_display = ("pessoa", "exemplar_livro", "exemplar_codigo", "ciclo", "data_inicio", "livros_lidos_no_ciclo")
    search_fields = ("pessoa__nome_completo", "exemplar__codigo", "exemplar__livro__titulo")

    # Campos customizados para exibir livro e código do exemplar
    def exemplar_livro(self, obj):
        return obj.exemplar.livro.titulo if obj.exemplar else "Sem livro"
    exemplar_livro.short_description = "Livro"

    def exemplar_codigo(self, obj):
        return obj.exemplar.codigo if obj.exemplar else "Sem código"
    exemplar_codigo.short_description = "Código do Exemplar"


# ===========================
# Histórico de Leitura
# ===========================
@admin.register(HistoricoLeitura)
class HistoricoLeituraAdmin(admin.ModelAdmin):
    list_display = ("pessoa", "ciclo", "data_saida", "livros_lidos", "motivo_saida")
    list_filter = ("motivo_saida", "ciclo")
    search_fields = ("pessoa__nome_completo", "ciclo")
