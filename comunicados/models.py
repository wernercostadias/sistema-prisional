from django.db import models

class Comunicado(models.Model):
    titulo = models.CharField(max_length=255)
    conteudo = models.TextField()
    data = models.DateField()
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-criado_em']  # agora ordena pelo último publicado

    def __str__(self):
        return f"{self.titulo} ({self.data})"
