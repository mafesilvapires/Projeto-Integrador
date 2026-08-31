from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User 
from django.contrib.auth import authenticate
from django.contrib.auth import login as login_django
from django.contrib.auth.decorators import login_required
import pyotp
import qrcode
import io
import base64
from .models import PerfilTOTP

# Create your views here.
def cadastro(request):
    if request.method == "GET":
        return render(request, 'cadastro.html')
    else:   
        username = request.POST.get('username')
        email =  request.POST.get('email')
        senha =  request.POST.get('senha')
        user = User.objects.filter(username=username).first()
        if user:
            return HttpResponse('Usuario ja cadastrado')
        user = User.objects.create_user(username=username, email=email, password=senha)

        secret = pyotp.random_base32()
        PerfilTOTP.objects.create(user=user, secret=secret)

        return redirect('qrcode', username=username)


def qrcode_2fa(request, username):
    user = User.objects.get(username=username)
    perfil = PerfilTOTP.objects.get(user=user)

    uri = pyotp.totp.TOTP(perfil.secret).provisioning_uri(name=user.username, issuer_name="MeuSite")

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
        senha =  request.POST.get('senha')
        user = authenticate(request, username=username, password=senha)
        if user:
            request.session['pre_2fa_user_id'] = user.id
            return redirect('verificar_2fa')
        else:
            return HttpResponse("email ou senha inválidos")


def verificar_2fa(request):
    if request.method == "GET":
        return render(request, 'verificar_2fa.html')
    else:
        codigo = request.POST.get('codigo')
        user_id = request.session.get('pre_2fa_user_id')

        if not user_id:
            return redirect('login')

        user = User.objects.get(id=user_id)
        perfil = PerfilTOTP.objects.get(user=user)
        totp = pyotp.TOTP(perfil.secret)

        if totp.verify(codigo):
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login_django(request, user)
            del request.session['pre_2fa_user_id']
            return HttpResponse("autenticação correta")
        else:
            return HttpResponse("código inválido")


@login_required(login_url="/auth/login")
def plataforma(request):
    return HttpResponse('você esta logado')