from django.urls import path
from . import views

urlpatterns = [
    path('cadastro/', views.cadastro, name='cadastro'),
    path('qrcode/<str:username>/', views.qrcode_2fa, name='qrcode'),
    path('login/', views.login, name='login'),
    path('verificar-2fa/', views.verificar_2fa, name='verificar_2fa'),
    path('plataforma', views.plataforma, name='plataforma'),
    path('logout/', views.logout, name='logout'),
]
