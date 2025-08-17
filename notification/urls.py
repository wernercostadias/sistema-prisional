from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from notification.views import marcar_notificacao_como_lida, carregar_notificacoes


urlpatterns = [
    path('notificacao/mark-as-read/<int:notif_id>/', marcar_notificacao_como_lida, name='marcar_notificacao_como_lida'),
    path('carregar-notificacoes/', carregar_notificacoes, name='carregar_notificacoes'),
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # Adicione esta linha