import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, Group

# Create your models here.

ROLE_CHOICES = (
    (3, "Admin"),
    (2, "Staff"),
    (1, "User"),
)

STATUS_CHOICES = (("P", "Pending"), ("V", "Verified"), ("D", "Deleted"))


class UserAccount(AbstractBaseUser):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(verbose_name="email", max_length=60, unique=True)
    role=models.IntegerField(choices=ROLE_CHOICES, default=1)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')
    email_verified = models.BooleanField(default=False)
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    @property
    def is_staff(self):
        return self.role >= 2
    
    @property
    def is_admin(self):
        return self.role == 3
    
    @property
    def is_superuser(self):
        return self.role == 3
    
    def has_perm(self, perm, obj=None):
        return self.role == 3
    
    def has_module_perms(self, app_label):
        return self.role == 3
    
    def __str__(self):
        return f"{self.username} - {self.status}"


class UserProfile(models.Model):
    avatar_id = models.IntegerField(null=False, blank=False, default=1)
    user = models.OneToOneField(UserAccount, on_delete=models.CASCADE)
    user_name = models.CharField(max_length=100, unique=True)
    date_joined = models.DateTimeField(verbose_name="date joined", auto_now_add=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    college = models.CharField(max_length=200, blank=False, null=False)
    year = models.IntegerField(blank=False, null=False)
    phone_no = models.CharField(max_length=10, blank=False, null=False)
    whatsapp_no = models.CharField(max_length=10, blank=False, null=False)
    postal_address = models.TextField()
    pin_code = models.IntegerField()
    why_choose = models.TextField()
    were_you_ca = models.BooleanField(default=False)
    points = models.IntegerField(default=0)
    referrals = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user_name} - {self.first_name} - {self.last_name} - {self.college}"

class VerificationModel(models.Model):
    userid = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    email_token = models.CharField(max_length=100)

    def __str__(self):
        return f"Username:{self.userid.username} email_token:{self.email_token}"


class ForgotPasswordOTPModel(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6, unique=True, null=False)
    has_been_used = models.BooleanField(null=False, default=False)
    verified = models.BooleanField(null=False, default=False)
    last_created = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Username:{self.user.username} otp:{self.otp}"
    

class ReferralCode(models.Model):
    user = models.OneToOneField(UserAccount, on_delete=models.CASCADE)
    referral_code = models.CharField(max_length=50, null=True, unique=True)

    def __str__(self):
        return f"{self.user.username} - {self.referral_code}"