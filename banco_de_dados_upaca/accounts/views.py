# accounts/views.py
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
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.shortcuts import redirect

from comunicados.models import Comunicado  # Importa o modelo de comunicados

from django.utils import timezone
from datetime import timedelta
def login_view(request):
    comunicados_qs = Comunicado.objects.order_by('-criado_em')[:5]  # últimos 5
    comunicados = list(comunicados_qs)  # transforma em lista para poder adicionar atributos

    now = timezone.now()
    two_days_ago = now - timedelta(days=2)

    for comunicado in comunicados:
        comunicado.is_new = comunicado.criado_em >= two_days_ago

    if request.method == "POST":
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        
        user_exists = User.objects.filter(username=username).exists()

        if user_exists:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Login realizado com sucesso!")
                return redirect('index')
            else:
                messages.error(request, "Senha incorreta. Tente novamente.")
        else:
            messages.error(request, "Nome de usuário não encontrado. Tente novamente.")

    return render(request, 'accounts/login1.html', {'comunicados': comunicados})



def logout_view(request):
    logout(request)
    messages.success(request, "Você foi desconectado, o sistema UPACA estará aqui sempre para ajudar você!")
    return redirect('login')

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
            
            
            # return redirect('success_page') 

        else:
            # Adicionando mensagens de erro mais específicas para cada campo
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





# Modifique o UserAdmin se necessário
class CustomUserAdmin(UserAdmin):
    # Exemplo de personalização (ajuste conforme necessário)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')

# Use o admin.site.unregister antes de registrar o modelo personalizado
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)



from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

@login_required
def configuracoes_pessoais(request):
    

    form_name = UserChangeForm(instance=request.user)  # Formulário para nome completo
    form_password = PasswordChangeForm(request.user)  # Formulário para senha

    if request.method == 'POST':
        # Verificar qual formulário foi enviado
        if 'name_form' in request.POST:
            
            form_name = UserChangeForm(request.POST, instance=request.user)
            
            if form_name.is_valid():
                print("Formulário de nome é válido.")
                form_name.save()
                messages.success(request, 'Seu nome foi atualizado com sucesso.')
                return redirect('configuracoes_pessoais')
            else:
                print("Erro ao validar o formulário de nome:", form_name.errors)
                messages.error(request, 'Erro ao atualizar o nome. Tente novamente.')

        elif 'password_form' in request.POST:
            
              # Mostrar os dados enviados para senha
            form_password = PasswordChangeForm(request.user, request.POST)
            if form_password.is_valid():
                print("Formulário de senha é válido.")
                form_password.save()
                update_session_auth_hash(request, form_password.user)  # Manter o usuário autenticado após mudar a senha
                messages.success(request, 'Sua senha foi alterada com sucesso.')
                return redirect('configuracoes_pessoais')
            else:
                print("Erro ao validar o formulário de senha:", form_password.errors)
                messages.error(request, 'Erro ao alterar a senha. Verifique as informações.')

    # Renderizar o template
    
    
    
    return render(request, 'accounts/configuracoes_pessoais.html', {
        'form_name': form_name,
        'form_password': form_password
    })






from django.contrib.sessions.models import Session
from django.utils.timezone import now
from django.contrib.auth.models import User
from django.shortcuts import render
from django.core.cache import cache

# Função para pegar o IP real do cliente
def get_user_ip(request):
    # Tenta pegar o IP diretamente do cache se já tiver sido registrado
    ip = cache.get(f'ip_{request.user.id}')
    if ip:
        return ip
    
    # Se não houver no cache, pega o IP real
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]  # Pega o primeiro IP da lista
    else:
        ip = request.META.get('REMOTE_ADDR')
    
    # Armazena o IP no cache para reutilização
    cache.set(f'ip_{request.user.id}', ip, timeout=3600)  # Armazenar por 1 hora
    return ip

from django.shortcuts import render

def users_online_view(request):
    return render(request, 'accounts/users_online.html')





from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.contrib.sessions.models import Session

def logout_user(request, user_id):
    try:
        # Obtenha o usuário que será desconectado
        user_to_disconnect = get_object_or_404(User, id=user_id)

        # Certifique-se de que o administrador não está tentando desconectar a si mesmo
        if user_to_disconnect != request.user:
            # Desconecte o usuário encerrando suas sessões
            for session in Session.objects.filter(expire_date__gte=timezone.now()):
                session_data = session.get_decoded()
                if user_to_disconnect.id == int(session_data.get('_auth_user_id', 0)):
                    session.delete()

            # Adicione uma mensagem de sucesso
            messages.success(request, f'O usuário {user_to_disconnect.username} foi desconectado com sucesso.')

        else:
            # Mensagem de erro caso tente se desconectar
            messages.error(request, 'Você não pode desconectar a si mesmo.')

    except User.DoesNotExist:
        # Mensagem de erro caso o usuário não exista
        messages.error(request, 'Usuário não encontrado.')

    # Redirecione para a página anterior
    return redirect(request.META.get('HTTP_REFERER', '/'))


