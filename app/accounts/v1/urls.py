from django.urls import path

from .views import (
    LoginView,
    RegisterView,
    VerifyOTPView,
    ResendRegistrationOTPView,
)

urlpatterns = [
    path('login/', LoginView.as_view(), name="Login"),
    path('register/', RegisterView.as_view(), name="Register"),
    path('verify-otp/', VerifyOTPView.as_view(), name="VerifyOTP"),
    path('resend-otp/', ResendRegistrationOTPView.as_view(), name="ResendOTP"),
]
