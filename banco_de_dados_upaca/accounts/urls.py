# accounts/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import users_online_view
from .views import login_view  # Importando sua view personalizada
urlpatterns = [
    path('login/', login_view, name='login'),  # Agora usa sua view personalizada
    path('logout/', views.logout_view, name='logout'),
    path('create-user/', views.create_user, name='create-user'),  # Aqui está o nome 'create-user'
    path('configuracoes/', views.configuracoes_pessoais, name='configuracoes_pessoais'),
    path('users-online/', users_online_view, name='users-online'),
    path('logout_user/<int:user_id>/', views.logout_user, name='logout_user'),
   
    
]

