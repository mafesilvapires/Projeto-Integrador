import csv
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.models import User 
from django.contrib.auth.decorators import login_required
from django.utils import timezone

# Importa o modelo de Perfil
from authenticate_user.models import PerfilTOTP 

@login_required
def compliance_home(request):
    return render(request, "compliance/home.html", {"user": request.user})


@login_required
def my_data(request):
    # Busca o perfil ou cria caso ainda não exista para este usuário
    perfil, _ = PerfilTOTP.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        perfil.aceita_comunicacoes = 'comunicacoes' in request.POST
        if hasattr(perfil, 'data_consentimento'):
            perfil.data_consentimento = timezone.now()
        perfil.save()
        messages.success(request, 'Suas preferências de comunicação foram atualizadas com sucesso.')
        return redirect('compliance:my_data')

    return render(request, "compliance/my_data.html", {
        "user": request.user,
        "perfil": perfil
    })


@login_required
def export_my_data(request):
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="meus_dados.csv"'

    response.write("\ufeff")
    writer = csv.writer(response)

    perfil = PerfilTOTP.objects.filter(user=request.user).first()
    aceita_comunicacoes = "Sim" if perfil and perfil.aceita_comunicacoes else "Não"

    writer.writerow(["Nome de Usuário", "Email", "Aceita Comunicações"])
    writer.writerow([request.user.username, request.user.email, aceita_comunicacoes])

    return response


@login_required
def delete_account(request):
    if request.method == "POST":
        user = request.user

        logout(request)
        user.delete()
        
        messages.success(request, "Sua conta foi excluída de nossa base.")

        return redirect("login")
    return render(request, "compliance/delete_account.html")