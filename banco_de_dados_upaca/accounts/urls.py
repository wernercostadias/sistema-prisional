# accounts/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import users_online_view

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/accounts/login/'), name='logout'),
    path('create-user/', views.create_user, name='create-user'),  # Aqui está o nome 'create-user'
    path('configuracoes/', views.configuracoes_pessoais, name='configuracoes_pessoais'),
    path('users-online/', users_online_view, name='users-online'),
    path('logout_user/<int:user_id>/', views.logout_user, name='logout_user'),
    path('user_logged_out/', views.user_logged_out, name='user_logged_out'),  # Defina a URL para a página de logout
    
    
    
]

