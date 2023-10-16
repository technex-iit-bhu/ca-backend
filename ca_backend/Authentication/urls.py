from django.urls import path
from .views import (
    RegisterView,
    LoginView
)

from rest_framework_simplejwt.views import (
    TokenObtainPairView,  # To obtain a token
    TokenRefreshView,     # To refresh an existing token
    TokenVerifyView,      # To verify a token's validity
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("login_dev/", LoginView.as_view(), name="login"),# will customize TokenObtainPairView
]