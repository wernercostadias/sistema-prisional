from django.contrib.auth.signals import user_logged_out
from django.dispatch import receiver
from django.utils.timezone import now
from datetime import timedelta
from .models import Profile  # Certifique-se de que o modelo Profile está importado corretamente

@receiver(user_logged_out)
def update_last_activity_on_logout(sender, request, user, **kwargs):
    try:
        # Verifica se o usuário tem um perfil
        if user.profile:
            # Atualiza o campo 'last_activity' para um valor distante no tempo
            user.profile.last_activity = now() - timedelta(days=365)  # Um ano atrás
            user.profile.save()
    except Profile.DoesNotExist:
        pass  # Caso o perfil do usuário não exista, nada é feito
    except AttributeError:
        pass  # Caso o usuário não tenha um atributo 'profile', nada é feito
