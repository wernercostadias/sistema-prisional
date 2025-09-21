from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Notificacao(models.Model):
    TIPOS = [
        ('alvara', 'Alvará'),
        ('transferencia', 'Transferência'),
        ('revogacao', 'Revogação de Frente'),
        ('pdi', 'PDI'),
    ]

    GRAUS = [
        ('geral', 'Geral'),
        ('importante', 'Importante'),
    ]

    usuarios = models.ManyToManyField(
        User, 
        through='NotificacaoUsuario',  # Aqui o relacionamento intermediado
        related_name='notificacoes'
    )
    tipo = models.CharField(max_length=20, choices=TIPOS, default='pdi')
    titulo = models.CharField(max_length=255)
    mensagem = models.TextField()
    grau = models.CharField(max_length=15, choices=GRAUS, default='geral')
    data_criacao = models.DateTimeField(default=timezone.now)
    pessoa = models.ForeignKey('painel.Pessoa', null=True, blank=True, on_delete=models.SET_NULL)
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='notificacoes_criadas')

    def __str__(self):
        usuarios = ', '.join(user.username for user in self.usuarios.all())
        return f"[{self.get_tipo_display()}] {self.titulo} para {usuarios}"


class NotificacaoUsuario(models.Model):
    notificacao = models.ForeignKey(Notificacao, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    lida = models.BooleanField(default=False)

    class Meta:
        unique_together = ('notificacao', 'usuario')

    def marcar_como_lida(self):
        self.lida = True
        self.save()
