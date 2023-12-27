from django.contrib import admin

# Register your models here.
from .models import UserAccount, UserProfile, VerificationModel, ForgotPasswordOTPModel, ReferralCode



class UserAccountAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'status')
    list_filter = ('role', 'status')
    search_fields = ('username', 'email')
    list_editable = ('status',)
    

    model = UserAccount

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'first_name', 'last_name', 'college', 'year', 'phone_no', 'whatsapp_no', 'postal_address', 'pin_code', 'why_choose', 'were_you_ca', 'points')
    list_filter = ('year', 'were_you_ca', 'college')
    search_fields = ('user_name', 'first_name', 'last_name', 'college', 'phone_no', 'whatsapp_no', 'postal_address', 'pin_code', 'why_choose', 'were_you_ca', 'points')
    list_editable = ('points',)

    model = UserProfile

admin.site.register(UserAccount, UserAccountAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(VerificationModel)
admin.site.register(ForgotPasswordOTPModel)
admin.site.register(ReferralCode)