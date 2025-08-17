from django.urls import path
from .views import pedagogia_view, dados_grafico_leitura, excluir_interno_view, buscar_interno, listar_livros_interno, cadastrar_livro, buscar_livro
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("livro/", pedagogia_view, name="pedagogia_view"),
    path('grafico-leitura/', dados_grafico_leitura, name='dados_grafico_leitura'),
    path('leitura/excluir/', excluir_interno_view, name='excluir_interno'),
    path('leitura/buscar/', buscar_interno, name='buscar_interno'),
    path('livros-interno/', listar_livros_interno, name='listar_livros_interno'),
    path("livro/cadastrar/", cadastrar_livro, name="cadastrar_livro"),
    path('livro/buscar-livro/', buscar_livro, name='buscar_livro'),  # ✅ nova URL para busca

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # 