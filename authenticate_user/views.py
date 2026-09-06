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


logger = logging.getLogger('authenticat_user')


def cadastro(request):
    if request.method == "GET":
        return render(request, 'cadastro.html')
    else:   
        username = request.POST.get('username')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        confirma_senha = request.POST.get('confirma_senha')

        if senha != confirma_senha:
            messages.error(request, 'As senhas não coincidem.')
            return redirect('cadastro')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Este usuário já está cadastrado.')
            return redirect('cadastro')

        user = User.objects.create_user(username=username, email=email, password=senha)

        secret = pyotp.random_base32()
        PerfilTOTP.objects.create(user=user, secret=secret)

        return redirect('qrcode', username=username)


def qrcode_2fa(request, username):
    try:
        user = User.objects.get(username=username)
        perfil = PerfilTOTP.objects.get(user=user)
    except (User.DoesNotExist, PerfilTOTP.DoesNotExist):
        messages.error(request, 'Usuário não encontrado.')
        return redirect('login')

    uri = pyotp.totp.TOTP(perfil.secret).provisioning_uri(name=user.username, issuer_name="Teacher Hub")

    img = qrcode.make(uri)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    return render(request, 'qrcode.html', {'qr_base64': qr_base64})


def login(request):
    if request.method == "GET":
        return render(request, 'login.html')
    else:
        username = request.POST.get('username')
        senha = request.POST.get('senha')
        user = authenticate(request, username=username, password=senha)

        if user:
            logger.info(f"login - usuario: {username} - IP: {request.META.get('REMOTE_ADDR')}")
            request.session['pre_2fa_user_id'] = user.id
            return redirect('verificar_2fa')
        else:
<<<<<<< Updated upstream
            messages.error(request, 'E-mail ou senha inválidos. Tente novamente.')
            return redirect('login')
=======
            logger.warning(f"tentativa falaha de acesso - usuario: {username} - IP: {request.META.get('REMOTE_ADDR')}")
            return HttpResponse("email ou senha inválidos")
>>>>>>> Stashed changes


def verificar_2fa(request):
    if request.method == "GET":
        return render(request, 'verificar_2fa.html')
    else:
        # Lê o campo 'codigo' do form simples ou 'token_2fa' do form de 6 pinos
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

        totp = pyotp.TOTP(perfil.secret)

        if codigo and totp.verify(codigo):
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            auth_login(request, user)
            del request.session['pre_2fa_user_id']
            return redirect("plataforma")
        else:
            messages.error(request, 'Código de verificação incorreto ou expirado.')
            return redirect('verificar_2fa')


@login_required(login_url="/auth/login")
def plataforma(request):
    return render(request, 'home.html', {
        'user': request.user
    })


def logout(request):
    auth_logout(request)
    messages.info(request, "Você foi desconectado com sucesso.")
    return redirect('login')