# banco_de_dados_upaca/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),  # Adicionando as URLs do app accounts
    path('painel/', include('painel.urls')),  # Outras URLs do app painel
    path('', include('painel.urls')),  # Página inicial do painel
]
