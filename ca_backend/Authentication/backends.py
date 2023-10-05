from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class AuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        print("i am called",UserModel)
        user = UserModel.objects.filter(username=username).first()
        if user is not None and password==user.password:
            return user
        else:
            return None
