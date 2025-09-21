from django.db import models
from ckeditor.fields import RichTextField

class Comunicado(models.Model):
    titulo = models.CharField(max_length=255)
    conteudo = RichTextField()  # agora permite imagens dentro do texto
    data = models.DateField()
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-criado_em']

    def __str__(self):
        return f"{self.titulo} ({self.data})"
