from django.urls import path
from .views import (
    RegisterView,
    UserProfileView,
    VerifyAccountView,
    VerifyEmailView,
    ForgotPasswordOTPCreationView,
    VerifyOTPView,
    ResetPasswordAPIView,
    AvatarChangeView
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
    path("user/profile/",UserProfileView.as_view(),name="user_profile"),
    path("verifyaccount/", VerifyAccountView.as_view(), name="verify_account"),
    path("verifyemail/<str:token>/", VerifyEmailView.as_view(), name="verify_email"),
    path(
        "login/forgot_password/",
        ForgotPasswordOTPCreationView.as_view(),
        name="forgot_password",
    ),
    path("login/forgot_password/verify/", VerifyOTPView.as_view(), name="otp_verify"),
    path(
        "login/forgot_password/reset/",
        ResetPasswordAPIView.as_view(),
        name="reset_password",
    ),
    path("user/profile/change_avatar/<int:avatar_id>/",AvatarChangeView.as_view(),name="change_avatar")
]