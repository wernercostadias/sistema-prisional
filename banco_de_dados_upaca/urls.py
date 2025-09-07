# banco_de_dados_upaca/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('painel/', include('painel.urls')),
    path('leitura/', include('leitura.urls')),
    path('notificacao/', include('notification.urls')),
    path('', include('painel.urls')),
    path('comunicados/', include('comunicados.urls')),
]

# Só serve para desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
