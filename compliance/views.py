import csv
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils import timezone

# Importa o modelo de Perfil e o registrador da trilha de auditoria
from authenticate_user.models import PerfilTOTP
from authenticate_user.log_integrity import event_register


def _ip(request):
    return request.META.get('REMOTE_ADDR')


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

        # Registra a decisão do titular: o valor NOVO fica na trilha
        event_register("CONSENTIMENTO_ALTERADO", {
            "user_id": request.user.id,
            "aceita_comunicacoes": perfil.aceita_comunicacoes,
            "ip": _ip(request),
        })

        messages.success(request, 'Suas preferências de comunicação foram atualizadas com sucesso.')
        return redirect('compliance:my_data')

    # GET = o titular está consultando os próprios dados (direito de acesso)
    event_register("CONSULTA_DADOS", {
        "user_id": request.user.id,
        "ip": _ip(request),
    })

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

    writer.writerow(["Nome de Usuário", "Email", "Aceita Comunicações", "Versão dos Termos", "Termos Aceitos Em"])
    writer.writerow([
        request.user.first_name,
        request.user.email,
        aceita_comunicacoes,
        perfil.termos_versao if perfil else "",
        timezone.localtime(perfil.termos_aceitos_em).strftime("%d/%m/%Y %H:%M") if perfil and perfil.termos_aceitos_em else "",
    ])

    event_register("EXPORTACAO_DADOS", {
        "user_id": request.user.id,
        "ip": _ip(request),
    })

    return response


@login_required
def delete_account(request):
    if request.method == "POST":
        user = request.user

        # O evento vem ANTES de apagar. Depois do logout, request.user é anônimo
        # e perderíamos o id. Se algo falhasse depois, ainda haveria o rastro.
        event_register("EXCLUSAO_CONTA", {
            "user_id": user.id,
            "ip": _ip(request),
        })

        logout(request)
        user.delete()

        messages.success(request, "Sua conta foi excluída de nossa base.")

        return redirect("login")
    return render(request, "compliance/delete_account.html")