from django.contrib.auth.backends import ModelBackend
from .models import UserAccount, UserProfile
import bcrypt


class AuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None):
        try:
            user = UserAccount.objects.get(username=username)
            if user.status == 'V' and bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
                return user
            else:
                return None

        except UserAccount.DoesNotExist:
            return None
