from django.db import models
from django.contrib.auth.models import User

class PerfilTOTP(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_totp')
    secret = models.CharField(max_length=255)
    
    # Consentimento LGPD
    aceita_comunicacoes = models.BooleanField(default=False)
    data_consentimento = models.DateTimeField(auto_now_add=True)
    data_atualizacao_consentimento = models.DateTimeField(auto_now=True)

    # Aceite dos Termos de Uso (obrigatório no cadastro)
    termos_versao = models.CharField(max_length=10, blank=True, default='')
    termos_aceitos_em = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"2FA & Perfil de {self.user.first_name or self.user.email}"


class IntegridadeLog(models.Model):
    timestamp = models.DateTimeField()
    event = models.CharField(max_length=100)
    data = models.TextField()
    previous_hash = models.CharField(max_length=64)
    actual_hash = models.CharField(max_length=64, unique=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.id} - {self.event}"
