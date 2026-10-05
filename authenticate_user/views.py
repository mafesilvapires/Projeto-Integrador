from django.shortcuts import render, redirect
from django.contrib.auth.models import User 
from django.contrib.auth.decorators import login_required
import pyotp
import qrcode
import io
import base64
import logging
from .models import PerfilTOTP
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from .crypto import criptografar_dado, descriptografar_dado
from .log_integrity import event_register

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
        logger.info(f"Redefinicao de senha concluida com sucesso - usuario: {form.user.username} - IP: {ip}")
        event_register(
                "REDEFINICAO_DE_SENHA_SUCEDIDA",
                {
                    "user": form.user.username,
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
        username = request.POST.get('username')
        email = request.POST.get('email', '').strip().lower()
        senha = request.POST.get('senha')
        confirma_senha = request.POST.get('confirma_senha')

        # Captura a escolha opcional do checkbox (True se marcado, False se desmarcado)
        aceita_comunicacoes = 'comunicacoes' in request.POST

        if senha != confirma_senha:
            messages.error(request, 'As senhas não coincidem.')
            return redirect('cadastro')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Este usuário já está cadastrado.')
            return redirect('cadastro')

        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, 'Este E-mail já foi cadastrado na plataforma.')
            return redirect('cadastro')

        user = User.objects.create_user(username=username, email=email, password=senha)

        secret = pyotp.random_base32()
        secret_cifrado = criptografar_dado(secret)

        # Salva o perfil TOTP junto com o consentimento de comunicação
        PerfilTOTP.objects.create(
            user=user, 
            secret=secret_cifrado,
            aceita_comunicacoes=aceita_comunicacoes
        )

        return redirect('qrcode', username=username)


def qrcode_2fa(request, username):
    try:
        user = User.objects.get(username=username)
        perfil = PerfilTOTP.objects.get(user=user)
    except (User.DoesNotExist, PerfilTOTP.DoesNotExist):
        messages.error(request, 'Usuário não encontrado.')
        return redirect('login')

    secret_puro = descriptografar_dado(perfil.secret)
    uri = pyotp.totp.TOTP(secret_puro).provisioning_uri(name=user.username, issuer_name="Teacher Hub")

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
                "LOGIN FALHA",
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
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            auth_login(request, user)
            del request.session['pre_2fa_user_id']
            ip = request.META.get("REMOTE_ADDR")
            logger.info(f"MFA Aprovado - usuario: {user.username} - IP: {ip}")
            event_register(
                    "MFA APROVADO",
                    {
                        "user": user.username,
                        "ip": ip
                        }
                    )
            return redirect("plataforma")
        else:
            messages.error(request, 'Código de verificação incorreto ou expirado.')
            ip = request.META.get('REMOTE_ADDR')
            logger.info(f"Falha de MFA: Código expirado ou incorreto - usuario: {user.username} - IP: {ip}")
            event_register(
                    "MFA FALHA",
                    {
                        "user": user.username,
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
        perfil = request.user.perfiltotp
        # Atualiza a preferência: True se a caixa estiver marcada, False se foi desmarcada
        perfil.aceita_comunicacoes = 'comunicacoes' in request.POST
        perfil.save()
        messages.success(request, 'Preferências de comunicação atualizadas com sucesso.')
    return redirect('plataforma')


def logout(request):
    username = request.user.username if request.user.is_authenticated else 'Anonimo'
    auth_logout(request)
    messages.info(request, "Você foi desconectado com sucesso.")
    ip = request.META.get('REMOTE_ADDR')
    logger.info(f"logout - usuario: {username} - IP: {ip}")
    event_register(
            "LOGOUT",
            {
                "user": username,
                "ip": ip
                }
            )
    return redirect('login')
