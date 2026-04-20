from django.urls import path
from .views import CreatorRegisterView

urlpatterns = [
    path('auth/register/', CreatorRegisterView.as_view(), name="CreatorRegister"),
]
