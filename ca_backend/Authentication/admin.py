from django.contrib import admin

# Register your models here.
from .models import UserAccount, UserProfile, VerificationModel, ForgotPasswordOTPModel, ReferralCode
from .send_email import send_approved_email

from decouple import config
import smtplib

connection = smtplib.SMTP("smtp.gmail.com", 587)
connection.starttls()
connection.login(config("EMAIL_HOST_USER"), config("EMAIL_HOST_PASSWORD"))

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
                send_approved_email(user.email, user.username, connection)
        queryset.update(status="V")


    @admin.action(description='Unverify User')
    def make_unverified(self, request, queryset):
        queryset.update(status="P")
    
    @admin.action(description='Copy Email')
    def copy_email(self, request, queryset):
        import csv
        from django.http import HttpResponse
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=emails.csv'
        writer = csv.writer(response)
        writer.writerow(["Username", "Email"])
        for user in queryset:
            writer.writerow([user.username, user.email])
        return response
    
    @admin.action(description='Delete Admin Logs')
    def delete_logs(self, request, queryset):
        from django.contrib.admin.models import LogEntry
        LogEntry.objects.all().delete()
    
    actions = [make_verified, make_unverified, copy_email, delete_logs]
    

    model = UserAccount

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'first_name', 'last_name', 'college', 'year', 'phone_no', 'whatsapp_no', 'postal_address', 'pin_code', 'why_choose', 'were_you_ca', 'points')
    list_filter = ('year', 'were_you_ca')
    search_fields = ('user_name', 'first_name', 'last_name', 'college', 'phone_no', 'whatsapp_no', 'postal_address', 'pin_code', 'why_choose', 'were_you_ca', 'points')
    list_editable = ('points',)
    list_display_links = None
    list_per_page = 10

    @admin.action(description='Copy WhatsApp No.')
    def copy_whatsapp_no(self, request, queryset):
        import csv
        from django.http import HttpResponse
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=whatsapp_no.csv'
        writer = csv.writer(response)
        writer.writerow(["User", "First Name", "Last Name", "WhatsApp No."])
        for user in queryset:
            writer.writerow([user.user_name, user.first_name, user.last_name, user.whatsapp_no]) 
        return response
    
    actions = [copy_whatsapp_no]

    model = UserProfile

admin.site.register(UserAccount, UserAccountAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(VerificationModel)
admin.site.register(ForgotPasswordOTPModel)
admin.site.register(ReferralCode)