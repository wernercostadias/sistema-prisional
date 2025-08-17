# accounts/models.py
from django.db import models

class Pessoa(models.Model):
    nome = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    cpf = models.CharField(max_length=11, unique=True)
    data_nascimento = models.DateField()

    def __str__(self):
        return self.nome



from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    last_activity = models.DateTimeField(default=now, null=True, blank=True)  # Usa 'now' como padrão

    def __str__(self):
        return self.user.username
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        Profile.objects.create(user=instance)
