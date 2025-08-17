from django.utils.timezone import now

class UpdateLastActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Atualiza o 'last_activity' do perfil do usuário
            request.user.profile.last_activity = now()
            request.user.profile.save()
        return self.get_response(request)
