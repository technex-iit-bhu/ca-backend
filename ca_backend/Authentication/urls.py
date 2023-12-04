from django.urls import path
from .views import (
    RegisterView,
    UserProfileView,
    VerifyAccountView,
    VerifyEmailView,
)

from rest_framework_simplejwt.views import (
    TokenObtainPairView,  # To obtain a token
    TokenRefreshView,  # To refresh an existing token
    TokenVerifyView,  # To verify a token's validity
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("user/profile",UserProfileView.as_view(),name="user_profile"),
    path("verifyaccount/", VerifyAccountView.as_view(), name="verify_account"),
    path("verifyemail/<str:token>", VerifyEmailView.as_view(), name="verify_email"),
]
