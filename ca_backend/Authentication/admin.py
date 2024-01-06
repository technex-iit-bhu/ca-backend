from django.contrib import admin

# Register your models here.
from .models import UserAccount, UserProfile, VerificationModel, ForgotPasswordOTPModel, ReferralCode
from .send_email import send_approved_email



class UserAccountAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'status')
    list_filter = ('role', 'status')
    search_fields = ('username', 'email')
    list_display_links = None
    list_per_page = 10

    @admin.action(description='Verify User')
    def make_verified(self, request, queryset):
        for user in queryset:
            if user.status == "P":
                send_approved_email(user.email)
        queryset.update(status="V")


    @admin.action(description='Unverify User')
    def make_unverified(self, request, queryset):
        queryset.update(status="P")
    
    actions = [make_verified, make_unverified]
    

    model = UserAccount

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'first_name', 'last_name', 'college', 'year', 'phone_no', 'whatsapp_no', 'postal_address', 'pin_code', 'why_choose', 'were_you_ca', 'points')
    list_filter = ('year', 'were_you_ca')
    search_fields = ('user_name', 'first_name', 'last_name', 'college', 'phone_no', 'whatsapp_no', 'postal_address', 'pin_code', 'why_choose', 'were_you_ca', 'points')
    list_editable = ('points',)
    list_display_links = None
    list_per_page = 10

    model = UserProfile

admin.site.register(UserAccount, UserAccountAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(VerificationModel)
admin.site.register(ForgotPasswordOTPModel)
admin.site.register(ReferralCode)