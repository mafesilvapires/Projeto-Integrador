from django.urls import path
from . import views

urlpatterns = [
        path("", views.compliance_home, name='compliance_home'),
        path('data/', views.my_data, name='my_data'),
        path('data/export/', views.export_my_data, name='export_my_data'),
        path('delete-account/',  views.delete_account, name='delete_account'),
        ]
