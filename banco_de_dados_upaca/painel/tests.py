from django.urls import reverse
from django.test import TestCase
from django.contrib.auth.models import User

class TestExibicaoSancoesAtivas(TestCase):

    def setUp(self):
        # Criação de um usuário para autenticação no teste
        self.user = User.objects.create_user(username='teste', password='teste123')
    
    def test_renderizacao_sancoes_ativas(self):
        # Autentica o usuário
        self.client.login(username='teste', password='teste123')

        # Realiza a requisição à página
        response = self.client.get(reverse('ver_tabela'))
        
        # Verifica se a resposta tem o conteúdo esperado
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sem Castelo')  # Verifica se o texto 'Sem Castelo' está presente na página
