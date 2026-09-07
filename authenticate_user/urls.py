from django.contrib.auth import views as auth_views
from django.urls import path, include, reverse_lazy
from . import views

urlpatterns = [
    # Paths de autenticação e MFA
    path('cadastro/', views.cadastro, name='cadastro'),
    path('qrcode/<str:username>/', views.qrcode_2fa, name='qrcode'),
    path('login/', views.login, name='login'),
    path('verificar-2fa/', views.verificar_2fa, name='verificar_2fa'),
    path('plataforma', views.plataforma, name='plataforma'),
    path('logout/', views.logout, name='logout'),

    # Paths de recuperação de senha (com log - Req 2.6 e 2.7)
    path('password_reset/', views.PasswordResetViewLog.as_view(
        template_name='registration/password_reset_form.html',
        email_template_name='registration/password_reset_email.txt',
        html_email_template_name='registration/password_reset_email.html',
        subject_template_name='registration/password_reset_subject.txt',
        success_url=reverse_lazy('password_reset_done')
    ), name='password_reset'),

    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ), name="password_reset_done"),

    path('reset/<uidb64>/<token>/', views.PasswordResetConfirmViewLog.as_view(
        template_name='registration/password_reset_confirm.html',
        success_url=reverse_lazy('password_reset_complete')
    ), name='password_reset_confirm'),

    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),

    # Include por último — só preenche o que não foi sobrescrito acima
    # (password_change, password_change/done, etc.)
    path('', include('django.contrib.auth.urls')),
]