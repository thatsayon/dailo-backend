from django.contrib import admin
from app.accounts.models import UserAccount, OTPVerification


admin.site.register(UserAccount)
admin.site.register(OTPVerification)
