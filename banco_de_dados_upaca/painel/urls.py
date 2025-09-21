from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('remover/<int:id>/', views.remover_pessoa, name='remover_pessoa'),
    
    path('adicionar/', views.adicionar_pessoa_view, name='adicionar_pessoa'),

    path('autocomplete-nome/', views.autocomplete_nome_view, name='autocomplete_nome'),
    
    path('tabela/', views.ver_tabela_view, name='ver_tabela'),
    
    path('editar/<int:id>/', views.editar_pessoa, name='editar_pessoa'),

    path('editar_pessoa_index/', views.editar_pessoa_index, name='editar_pessoa_index'),
    
    path('tabela_transferidos/', views.tabela_transferidos_view, name='tabela_transferidos'),
    
    path('', views.index_view, name='index'),
    
    path('tabela_sancoes/', views.ver_tabela_sancoes_view, name='ver_tabela_sancoes'),
    
    path('psicossocial/', views.psicossocial, name='psicossocial'),
    
    path('frentes/', views.frentes_de_trabalho, name='frentes_de_trabalho'),

    path('revogar-trabalho/<int:frente_id>/', views.revogar_trabalho, name='revogar_trabalho'),

    path('cadastrar-frente/', views.cadastrar_frente_de_trabalho, name='cadastrar_frente_de_trabalho'),
    path('apagar-frente/<int:frente_id>/', views.apagar_frente_de_trabalho, name='apagar_frente_de_trabalho'),

    path('sancao/apagar/<int:sancao_id>/', views.apagar_sancao_view, name='apagar_sancao'),
    
    path('atualizar-tempos-restantes/', views.atualizar_tempos_restantes_view, name='atualizar_tempos_restantes'),

    path('conceder_alvara/<int:id>/', views.conceder_alvara, name='conceder_alvara'),
    
    path('eletronicos/', views.tabela_eletronico, name='tabela-eletronico'),
    
    path('pessoa/search/', views.pessoa_search, name='pessoa_search'),
    
    path('eletronico/excluir/<int:id>/', views.excluir_eletronico, name='excluir_eletronico'),

    path('lista_personalizada/', views.lista_personalizada, name='lista_personalizada'),
    
    path('eletronico/transferir/<int:id>/', views.transferir_eletronico, name='transferir_eletronico'),
    
    path('exportar_tabela_pdf/', views.exportar_tabela_pdf, name='exportar_tabela_pdf'),

    path('gerar-pdf/', views.gerar_pdf, name='gerar_pdf'),
    path('gerar-pdf-lista/', views.gerar_pdf_lista, name='gerar_pdf_lista'),
    path('arquivos/', views.arquivos_view, name='arquivos'),
    
    path('informacao/', views.informacao_view, name='informacao'),
    
    path('pdi/', views.tabela_e_aplicar_pdi_view, name='tabela_pdi'),  # Para a tabela de PDIs
    
    path('editar_pdi/<int:pdi_id>/', views.editar_pdi, name='editar_pdi'),

    path('apagar_pdi/<int:pdi_id>/', views.apagar_pdi, name='apagar_pdi'),
    path('frentes/graficos/', views.dados_graficos_frentes, name='dados_graficos_frentes'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # Adicione esta linha