import datetime
import random
import uuid
from django.shortcuts import render
from rest_framework import generics, serializers, status, authentication, permissions
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings
from django.contrib.auth import authenticate, login, logout
from drf_yasg.utils import swagger_auto_schema
from .models import UserAccount, UserPasswordForgotOTP
from .serializers import (
    ProfileSerializer,
    RegisterSerializer,
    LoginSerializer,
    check,
    UserSerializer,
    CombinedRegisterProfileSerializer,
    DummySerializer,
    ForgotPasswordSerializer,
    VerifyOTPSerializer,
    ResetPasswordSerializer,
)
import bcrypt
from rest_framework_simplejwt.views import TokenObtainPairView


# Create your views here.
class RegisterView(generics.GenericAPIView):
    queryset = UserAccount.objects.all()
    serializer_class = CombinedRegisterProfileSerializer
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        responses={
            200: """{"success": "Verification link has been sent by email!"}""",
            226: """ {"error": "User with same credentials already exists!"}""",
            409: """Conflict Errors""",
        }
    )
    def post(self, request):
        user = check(request.data)
        if user is not None:
            return Response(
                {"error": "User with same credentials already exists!"},
                status=status.HTTP_226_IM_USED,
            )
        request.data["referral_code"] = f"{uuid.uuid4()}_{datetime.datetime.now()}"
        raw_password = request.data.get("password")
        hashed_password = bcrypt.hashpw(raw_password.encode("utf-8"), bcrypt.gensalt())
        request.data["password"] = hashed_password.decode("utf-8")

        user_serializer = RegisterSerializer(data=request.data)
        if user_serializer.is_valid():
            user = user_serializer.save()
            request.data["user"] = user.id
            request.data["user_name"] = user.username
            profile_serializer = ProfileSerializer(data=request.data)
            if not profile_serializer.is_valid():
                user.delete()
                return Response(
                    profile_serializer.errors, status=status.HTTP_409_CONFLICT
                )

            profile_serializer.save(user=user)
            # todo: send verification link by email
            return Response(
                {"success": "Verification link has been sent by email!"},
                status=status.HTTP_200_OK,
            )

        else:
            error = {}
            for err in user_serializer.errors:
                error[err] = user_serializer.errors[err][0]
            return Response(error, status=status.HTTP_409_CONFLICT)


class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        try:
            user = UserAccount.objects.get(username=username)
        except UserAccount.DoesNotExist:
            return Response(
                {"error": "User does not exist."}, status=status.HTTP_400_BAD_REQUEST
            )

        if bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.validated_data, status=status.HTTP_200_OK)

        return Response(
            {"error": "Invalid password."}, status=status.HTTP_400_BAD_REQUEST
        )


class UserProfileView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StatusCheck(generics.GenericAPIView):
    serializer_class = DummySerializer

    def get(request, user):
        return Response(
            {"message": "Working"},
            status=status.HTTP_200_OK,
        )


class ForgotPasswordOTPCreationView(generics.GenericAPIView):
    serializer_class = ForgotPasswordSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data["email"]
        user = UserAccount.objects.filter(email=email).first()
        if user is not None:
            otp = "{:06}".format(random.randint(1, 999999))
            user_otp = UserPasswordForgotOTP.objects.filter(user=user).first()
            if user_otp is not None:
                user_otp.otp = otp
                user_otp.has_been_used = False
                user_otp.verified = False
                user_otp.save()
            else:
                UserPasswordForgotOTP.objects.create(user=user, otp=otp)
            # TODO: Send mail/text to user with OTP
            return Response(
                {"detail": "OTP generated successfully"}, status=status.HTTP_201_CREATED
            )
        return Response({"detail": "No such user"}, status=status.HTTP_404_NOT_FOUND)


class VerifyOTPView(generics.GenericAPIView):
    serializer_class = VerifyOTPSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data["email"]
        otp = request.data["otp"]

        user = UserAccount.objects.filter(email=email).first()
        if user is not None:
            user_otp = UserPasswordForgotOTP.objects.filter(user=user, otp=otp).first()
            if not user_otp.has_been_used:
                if user_otp is not None:
                    user_otp.verified = True
                    user_otp.save()
                    return Response(
                        {"detail": "OTP Verified"}, status=status.HTTP_202_ACCEPTED
                    )
                else:
                    return Response(
                        {"detail": "Incorrect OTP"}, status=status.HTTP_403_FORBIDDEN
                    )
            else:
                return Response(
                    {"detail": "OTP already used"}, status=status.HTTP_401_UNAUTHORIZED
                )
        return Response({"detail": "No such user"}, status=status.HTTP_404_NOT_FOUND)


class ResetPasswordAPIView(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        pass1 = request.data["password1"]
        pass2 = request.data["password2"]
        email = request.data["email"]
        user = UserAccount.objects.filter(email=email).first()
        user_otp = UserPasswordForgotOTP.objects.filter(user=user).first()
        if user_otp.verified:
            if pass1 == pass2:
                raw_password = pass1
                hashed_password = bcrypt.hashpw(
                    raw_password.encode("utf-8"), bcrypt.gensalt()
                )
                if user is not None:
                    user.password = hashed_password.decode("utf-8")
                    user.save()
                    user_otp.has_been_used = True
                    user_otp.save()
                    return Response(
                        {"detail": "Password Reset Successfully"},
                        status=status.HTTP_200_OK,
                    )
                return Response(
                    {"detail": "No such User"}, status=status.HTTP_404_NOT_FOUND
                )
            return Response(
                {"detail": "Passwords do not match."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {"detail": "OTP not verified"}, status=status.HTTP_401_UNAUTHORIZED
        )
