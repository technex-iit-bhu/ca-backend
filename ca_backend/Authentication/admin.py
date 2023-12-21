from django.contrib import admin

# Register your models here.
from .models import UserAccount, UserProfile, VerificationModel, ForgotPasswordOTPModel

admin.site.register(UserAccount)
admin.site.register(UserProfile)
admin.site.register(VerificationModel)
admin.site.register(ForgotPasswordOTPModel)
