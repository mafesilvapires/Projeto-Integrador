from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from authenticate_user.models import PerfilTOTP


class CadastroTermosTest(TestCase):
    dados_base = {
        'nome_completo': 'Maria Teste',
        'email': 'maria@teste.com',
        'senha': 'Xk9#vLm2qPz!77',
        'confirma_senha': 'Xk9#vLm2qPz!77',
    }

    def test_cadastro_sem_termos_e_recusado(self):
        resp = self.client.post(reverse('cadastro'), self.dados_base)
        self.assertEqual(resp.status_code, 302)           # volta para o cadastro
        self.assertEqual(User.objects.count(), 0)          # nenhuma conta criada

    def test_cadastro_com_termos_grava_versao_e_data(self):
        dados = {**self.dados_base, 'termos_uso': 'on'}
        self.client.post(reverse('cadastro'), dados)
        perfil = PerfilTOTP.objects.get(user__email='maria@teste.com')
        self.assertEqual(perfil.termos_versao, settings.TERMOS_VERSAO)
        self.assertIsNotNone(perfil.termos_aceitos_em)