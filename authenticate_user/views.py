from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import pyotp
import qrcode
import io
import base64
import logging
import uuid
from .models import PerfilTOTP
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from .crypto import criptografar_dado, descriptografar_dado
from .log_integrity import event_register
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger('authenticate_user')

class PasswordResetViewLog(PasswordResetView):
    def form_valid(self, form):
        email = form.cleaned_data.get('email')
        ip = self.request.META.get('REMOTE_ADDR')
        logger.info(f"Solicitacao de recuperacao de senha - email: {email} - IP: {ip}")
        event_register(
                "SOLICITACAO_RECUPERACAO_SENHA",
                {
                    "user": email,
                    "ip": ip
                }
            )
        return super().form_valid(form)


class PasswordResetConfirmViewLog(PasswordResetConfirmView):
    def form_valid(self, form):

        ip = self.request.META.get('REMOTE_ADDR')
        logger.info(f"Redefinicao de senha concluida com sucesso - usuario: {form.user.email} - IP: {ip}")
        event_register(
                "REDEFINICAO_DE_SENHA_SUCEDIDA",
                {
                    "user": form.user.email,
                    "ip": ip
                    }
                )
        return super().form_valid(form)

    def form_invalid(self, form):
        ip = self.request.META.get('REMOTE_ADDR')
        logger.warning(f"Tentativa de redefinicao de senha invalida - IP: {ip}")
        event_register(
                "REDEFINICAO_SENHA_FALHA",
                {
                    "ip": ip
                    }
                )
        return super().form_invalid(form)


def cadastro(request):
    if request.method == "GET":
        return render(request, 'cadastro.html')
    else:
        nome_completo = request.POST.get('nome_completo')
        email = request.POST.get('email', '').strip().lower()
        senha = request.POST.get('senha')
        confirma_senha = request.POST.get('confirma_senha')

        # Captura a escolha opcional do checkbox (True se marcado, False se desmarcado)
        aceita_comunicacoes = 'comunicacoes' in request.POST

        # Termos de Uso: obrigatório. O 'required' do HTML só barra o navegador;
        # aqui garantimos no servidor, que é onde a regra realmente vale.
        aceitou_termos = 'termos_uso' in request.POST

        if not aceitou_termos:
            messages.error(request, 'É necessário aceitar os Termos de Uso e a Política de Privacidade.')
            return redirect('cadastro')

        if senha != confirma_senha:
            messages.error(request, 'As senhas não coincidem.')
            return redirect('cadastro')

        # Valida a senha com as regras definidas em AUTH_PASSWORD_VALIDATORS (settings.py):
        # tamanho mínimo, senha comum, apenas números e similaridade com nome/e-mail.
        try:
            validate_password(
                senha or '',
                user=User(email=email, first_name=nome_completo or ''),
            )
        except ValidationError as erros:
            for erro in erros.messages:
                messages.error(request, erro)
            return redirect('cadastro')

        # Validação de unicidade apenas pelo e-mail
        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, 'Este E-mail já foi cadastrado na plataforma.')
            return redirect('cadastro')

        # Gera o identificador único para o username e armazena o nome completo em first_name
        uuid_tecnico = uuid.uuid4().hex[:30]
        user = User.objects.create_user(
            username=uuid_tecnico,
            email=email,
            password=senha,
            first_name=nome_completo
        )

        secret = pyotp.random_base32()
        secret_cifrado = criptografar_dado(secret)

        # Salva o perfil TOTP junto com o consentimento de comunicação
        # e o registro do aceite dos termos (versão + data/hora)
        PerfilTOTP.objects.create(
            user=user,
            secret=secret_cifrado,
            aceita_comunicacoes=aceita_comunicacoes,
            termos_versao=settings.TERMOS_VERSAO,
            termos_aceitos_em=timezone.now(),
        )

        ip = request.META.get('REMOTE_ADDR')
        logger.info(f"Aceite de termos - usuario_id: {user.id} - versao: {settings.TERMOS_VERSAO} - IP: {ip}")
        event_register(
            "ACEITE_TERMOS",
            {
                "user": email,
                "ip": ip,
                "versao": settings.TERMOS_VERSAO,
            }
        )

        return redirect('qrcode', username=user.username)


def qrcode_2fa(request, username):
    try:
        user = User.objects.get(username=username)
        perfil = PerfilTOTP.objects.get(user=user)
    except (User.DoesNotExist, PerfilTOTP.DoesNotExist):
        messages.error(request, 'Usuário não encontrado.')
        return redirect('login')

    secret_puro = descriptografar_dado(perfil.secret)
    uri = pyotp.totp.TOTP(secret_puro).provisioning_uri(name=user.email, issuer_name="Teacher Hub")

    img = qrcode.make(uri)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    return render(request, 'qrcode.html', {'qr_base64': qr_base64})


def login(request):
    if request.method == "GET":
        return render(request, 'login.html')

    email = request.POST.get('email', '').strip().lower()
    senha = request.POST.get('senha')

    try:
        user = User.objects.get(email__iexact=email)
    except User.DoesNotExist:
        user = None

    if user:
        user = authenticate(request, username=user.username, password=senha)

    if user:
        ip = request.META.get('REMOTE_ADDR')
        logger.info(f"login - usuario: {email} - IP: {ip}")
        event_register(
                'LOGIN',
                {
                    "user": email,
                    "ip": ip
                    }
                )
        request.session['pre_2fa_user_id'] = user.id
        return redirect('verificar_2fa')
    else:
        ip = request.META.get('REMOTE_ADDR')
        logger.warning(f"tentativa falha de acesso - usuario: {email} - IP: {ip}")
        event_register(
                "LOGIN_FALHA",
                {
                    "user": email,
                    "ip": ip
                    }
                )
        messages.error(request, 'E-mail ou senha inválidos.')
        return redirect('login')


def verificar_2fa(request):
    if request.method == "GET":
        return render(request, 'verificar_2fa.html')
    else:
        codigo = request.POST.get('codigo') or request.POST.get('token_2fa')
        user_id = request.session.get('pre_2fa_user_id')

        if not user_id:
            messages.error(request, 'Sessão expirada. Faça login novamente.')
            return redirect('login')

        try:
            user = User.objects.get(id=user_id)
            perfil = PerfilTOTP.objects.get(user=user)
        except (User.DoesNotExist, PerfilTOTP.DoesNotExist):
            messages.error(request, 'Usuário ou perfil não encontrado.')
            return redirect('login')

        secret_puro = descriptografar_dado(perfil.secret)
        totp = pyotp.TOTP(secret_puro)

        if codigo and totp.verify(codigo):
            request.session.pop('pre_2fa_user_id', None)
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            auth_login(request, user)
            ip = request.META.get("REMOTE_ADDR")
            logger.info(f"MFA Aprovado - usuario_id: {user.id} - IP: {ip}")
            event_register(
                    "MFA_APROVADO",
                    {
                        "user": user.email,
                        "ip": ip
                        }
                    )
            return redirect("plataforma")
        else:
            messages.error(request, 'Código de verificação incorreto ou expirado.')
            ip = request.META.get('REMOTE_ADDR')
            logger.info(f"Falha de MFA: Código expirado ou incorreto - usuario_id: {user.id} - IP: {ip}")
            event_register(
                    "MFA_FALHA",
                    {
                        "user": user.email,
                        "ip": ip
                        }
                    )
            return redirect('verificar_2fa')


@login_required(login_url="/auth/login")
def plataforma(request):
    return render(request, 'home.html', {
        'user': request.user
    })

@login_required(login_url="/auth/login")
def atualizar_comunicacoes(request):
    if request.method == 'POST':
        perfil = request.user.perfil_totp          # com underscore (era perfiltotp)
        # Atualiza a preferência: True se a caixa estiver marcada, False se foi desmarcada
        perfil.aceita_comunicacoes = 'comunicacoes' in request.POST
        perfil.save()

        event_register("CONSENTIMENTO_ALTERADO", {
            "user_id": request.user.id,
            "aceita_comunicacoes": perfil.aceita_comunicacoes,
            "ip": request.META.get('REMOTE_ADDR'),
        })

        messages.success(request, 'Preferências de comunicação atualizadas com sucesso.')
    return redirect('plataforma')


def logout(request):
    email = request.user.email if request.user.is_authenticated else 'Anonimo'
    ip = request.META.get('REMOTE_ADDR')
    logger.info(f"logout - usuario: {email} - IP: {ip}")
    event_register(
            "LOGOUT",
            {
                "user": email,
                "ip": ip
                }
            )
    auth_logout(request)
    messages.info(request, "Você foi desconectado com sucesso.")
    return redirect('login')