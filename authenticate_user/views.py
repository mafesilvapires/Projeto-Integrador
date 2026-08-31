from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login

# Create your views here.
def cadastro(request):
    if request.method == "GET":
        return render(request, 'cadastro.html')

    username = request.POST.get('username')
    email =  request.POST.get('email')
    senha =  request.POST.get('senha')

    if User.objects.filter(username=username).exists():
        return HttpResponse("Usuário já cadastrado")

    user = User(
            username=username,
            email=email,
        )

    user.set_password(senha)
    user.save()

    return HttpResponse("Usuário cadastrado com sucesso")

def login(request):
    if request.method == "GET":
        return render(request, 'login.html')

    username = request.POST.get("username")
    senha = request.POST.get("senha")

    user = authenticate(
            request,
            username=username,
            password=senha,
        )

    if user is not None:
        auth_login(request, user)
        return redirect("plataforma")

    return HttpResponse("Usuário ou senha inválidos")

@login_required
def plataforma(request):
    return render(request, "home.html")
