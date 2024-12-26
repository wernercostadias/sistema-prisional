from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('remover/<int:id>/', views.remover_pessoa, name='remover_pessoa'),
    
    path('adicionar/', views.adicionar_pessoa_view, name='adicionar_pessoa'),
    
    path('tabela/', views.ver_tabela_view, name='ver_tabela'),
    
    path('editar/<int:id>/', views.editar_pessoa, name='editar_pessoa'),
    
    path('tabela_transferidos/', views.tabela_transferidos_view, name='tabela_transferidos'),
    
    path('', views.index_view, name='index'),
    
    path('tabela_sancoes/', views.ver_tabela_sancoes_view, name='ver_tabela_sancoes'),
    
    path('sancao/apagar/<int:sancao_id>/', views.apagar_sancao_view, name='apagar_sancao'),
    
    path('atualizar-tempo-restante/<int:sancao_id>/', views.atualizar_tempo_restante_view, name='atualizar_tempo_restante'),
    
    path('eletronicos/', views.tabela_eletronico, name='tabela-eletronico'),
    
    path('pessoa/search/', views.pessoa_search, name='pessoa_search'),
    
    path('eletronico/excluir/<int:id>/', views.excluir_eletronico, name='excluir_eletronico'),
    
    path('eletronico/transferir/<int:id>/', views.transferir_eletronico, name='transferir_eletronico'),
    
    path('exportar_tabela_pdf/', views.exportar_tabela_pdf, name='exportar_tabela_pdf'),
    
    path('arquivos/', views.arquivos_view, name='arquivos'),
    
    path('informacao/', views.informacao_view, name='informacao'),
    
    path('pdi/', views.tabela_e_aplicar_pdi_view, name='tabela_pdi'),  # Para a tabela de PDIs
    
    path('editar_pdi/<int:pdi_id>/', views.editar_pdi, name='editar_pdi'),
    
    path('apagar_pdi/<int:pdi_id>/', views.apagar_pdi, name='apagar_pdi'),
    
    path('notificacoes/', views.notificacoes_view, name='notificacoes'),
    
    path('notificacoes/marcar-como-lida/<int:notification_id>/', views.marcar_como_lida, name='marcar_como_lida'),
    
    path('notificacoes/marcar-todas-como-lidas/', views.marcar_todas_como_lidas, name='marcar_todas_como_lidas'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)