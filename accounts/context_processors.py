
# accounts/context_processors.py
from django.utils.timezone import now, timedelta
from django.contrib.auth.models import User
from django.core.cache import cache
from django.shortcuts import render

def get_user_ip(request):
    ip = cache.get(f'ip_{request.user.id}')
    if ip:
        return ip
    
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]  # Pega o primeiro IP da lista
    else:
        ip = request.META.get('REMOTE_ADDR')
    
    cache.set(f'ip_{request.user.id}', ip, timeout=3600)  # Armazenar por 1 hora
    return ip

def users_online(request):
    online_threshold = now() - timedelta(minutes=1)  # Define 1 minuto como limite para 'online'
    online_profiles = User.objects.filter(profile__last_activity__gte=online_threshold)
    
    users_status = [
        {
            'user': user,
            'is_online': True,  # Se o usuário estiver dentro do limite, está online
            'ip': get_user_ip(request),
        }
        for user in online_profiles
    ]
    
    # Você também pode adicionar usuários offline se necessário (por exemplo, para ter todos os usuários no sistema)
    
    return {'users_status': users_status}
