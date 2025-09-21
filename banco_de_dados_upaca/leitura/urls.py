from django.urls import path
from .views import (
    pedagogia_view, livro_exemplares, dados_grafico_leitura,
    excluir_interno_view, buscar_interno, listar_livros_interno,
    cadastrar_livro, buscar_livro, adicionar_exemplar_interno,
    remover_exemplar_interno, listar_ciclos, definir_ciclo,
    detalhar_ciclo, avancar_ciclos_ativos_ajax, checar_livro_lido, sortear_livros_frente
)

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ----- Views principais de pedagogia -----
    path("livro/", pedagogia_view, name="pedagogia_view"),
    path('livro-exemplares/<int:livro_id>/', livro_exemplares, name='livro_exemplares'),
    path('grafico-leitura/', dados_grafico_leitura, name='dados_grafico_leitura'),

    # ----- Operações sobre internos -----
    path('leitura/excluir/', excluir_interno_view, name='excluir_interno'),
    path('leitura/buscar/', buscar_interno, name='buscar_interno'),
    path('livros-interno/', listar_livros_interno, name='listar_livros_interno'),

    # ----- Livros e exemplares -----
    path("livro/cadastrar/", cadastrar_livro, name="cadastrar_livro"),
    path('livro/buscar-livro/', buscar_livro, name='buscar_livro'),
    path("leitura/adicionar-exemplar/", adicionar_exemplar_interno, name="adicionar_exemplar_interno"),
    path("leitura/remover-exemplar/", remover_exemplar_interno, name="remover_exemplar_interno"),
    path('leitura/checar-livro-lido/', checar_livro_lido, name='checar_livro_lido'),

    # ----- Ciclos -----
    path("listar-ciclos/", listar_ciclos, name="listar_ciclos"),
    path("leitura/definir-ciclo/", definir_ciclo, name="definir_ciclo"),
    path('detalhar-ciclo/<int:ciclo_id>/', detalhar_ciclo, name='detalhar_ciclo'),
    path('leitura/avancar-ciclos-ajax/', avancar_ciclos_ativos_ajax, name='avancar_ciclos_ativos_ajax'),
    # ----- Sortear livros -----
    path('leitura/sortear-livros/', sortear_livros_frente, name='sortear_livros_frente'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
