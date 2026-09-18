import csv
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.models import User 
from django.contrib.auth.decorators import login_required

@login_required
def compliance_home(request):
    return render(request, "compliance/home.html", {"user": request.user,})

@login_required
def my_data(request):
    return render(request, "compliance/my_data.html", {"user": request.user,})

@login_required
def export_my_data(request):
    response = HttpResponse(content_type = "text/csv; charset = utf-8")

    response["Content-Disposition"] = ('attachment; filename="meus_dados.csv"')

    response.write("\ufeff")
    writer = csv.writer(response)

    writer.writerow(["Nome de Usuário", "Email"])
    writer.writerow([request.user.username, request.user.email,])

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
