# banco_de_dados_upaca/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),  # Adicionando as URLs do app accounts
    path('painel/', include('painel.urls')),  # Outras URLs do app painel
    path('leitura/', include('leitura.urls')),
    path('notificacao/', include('notification.urls')),
    path('comunicados/', include('comunicados.urls')),
    path('', include('painel.urls')),  # Página inicial do painel
]



if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)