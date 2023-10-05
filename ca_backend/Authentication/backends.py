from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class AuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        user = UserModel.objects.filter(email=username).first()
        if user is not None and user.check_password(password):
            return user
        else:
            user = UserModel.objects.filter(username=username).first()
            if user is not None and user.check_password(password):
                return user
        return None
