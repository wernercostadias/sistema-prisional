from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import UserChangeForm
from django.contrib import messages
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site

# Função que verifica se o usuário é admin
def is_admin(user):
    return user.is_superuser

@user_passes_test(is_admin)
def create_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True  # Garante que o usuário está ativo para login no site
            user.save()
            messages.success(request, f'Conta de servidor "{user.username}" criada com sucesso! O usuário agora pode acessar o site.')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    if field == 'username':
                        messages.error(request, f'Erro no campo "Usuário": {error}.')
                    elif field == 'password1':
                        messages.error(request, f'Erro no campo "Senha": {error}.')
                    elif field == 'password2':
                        messages.error(request, f'Erro no campo "Confirmação de Senha": {error}.')
                    else:
                        messages.error(request, f'Erro no campo "{field}": {error}.')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/create_user.html', {'form': form})

@login_required
def configuracoes_pessoais(request):
    form_name = UserChangeForm(instance=request.user)  # Formulário para nome completo
    form_password = PasswordChangeForm(request.user)  # Formulário para senha
    
    if request.method == 'POST':
        if 'name_form' in request.POST:
            form_name = UserChangeForm(request.POST, instance=request.user)
            if form_name.is_valid():
                form_name.save()
                messages.success(request, 'Seu nome foi atualizado com sucesso.')
                return redirect('configuracoes_pessoais')
            else:
                messages.error(request, 'Erro ao atualizar o nome. Tente novamente.')
        elif 'password_form' in request.POST:
            form_password = PasswordChangeForm(request.user, request.POST)
            if form_password.is_valid():
                form_password.save()
                update_session_auth_hash(request, form_password.user)  # Manter o usuário autenticado após mudar a senha
                messages.success(request, 'Sua senha foi alterada com sucesso.')
                return redirect('configuracoes_pessoais')
            else:
                messages.error(request, 'Erro ao alterar a senha. Verifique as informações.')

    return render(request, 'accounts/configuracoes_pessoais.html', {
        'form_name': form_name,
        'form_password': form_password
    })

def logout_user(request, user_id):
    try:
        user_to_disconnect = User.objects.get(id=user_id)
        if user_to_disconnect != request.user:
            user_to_disconnect.is_active = False
            user_to_disconnect.save()
            messages.success(request, f'O usuário {user_to_disconnect.username} foi desconectado.')
            user_to_disconnect.is_active = True
            user_to_disconnect.save()
            return redirect('user_logged_out')
        else:
            messages.error(request, 'Você não pode desconectar a si mesmo dessa forma.')
            return redirect('some_error_page')
    except User.DoesNotExist:
        messages.error(request, 'Usuário não encontrado.')
        return redirect('some_error_page')
