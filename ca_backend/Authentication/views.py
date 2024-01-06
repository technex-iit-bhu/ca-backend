import datetime
import smtplib
from decouple import config
import random
import uuid
from django.shortcuts import render, get_object_or_404
from rest_framework import generics, serializers, status, authentication, permissions, views
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings
from django.contrib.auth import authenticate, login, logout
from drf_yasg.utils import swagger_auto_schema
from django.http import HttpResponseRedirect


from ca_backend.permissions import IsAdminUser
from .models import UserAccount, VerificationModel, UserProfile, ForgotPasswordOTPModel, ReferralCode
from .serializers import (
    ProfileSerializer,
    RegisterSerializer,
    LoginSerializer,
    VerificationSerializer,
    check,
    UserSerializer,
    CombinedRegisterProfileSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    VerifyOTPSerializer    
)
from .send_email import send_approved_email, send_email_cnf_email, send_email_verif_email, send_otp_email
import bcrypt  
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import password_validation
from django.db.models import Q


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
        request.data["referral_code"]=f'{uuid.uuid4()}_{datetime.datetime.now()}'
        raw_password = request.data.get("password")
        try:
            password_validation.validate_password(raw_password, user=UserAccount)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_409_CONFLICT,
            )
        hashed_password = bcrypt.hashpw(raw_password.encode("utf-8"), bcrypt.gensalt())
        request.data["password"] = hashed_password.decode("utf-8")

        user_serializer = RegisterSerializer(data=request.data)
        if user_serializer.is_valid():
            user = user_serializer.save()
            request.data["user"] = user.id
            request.data["user_name"]=user.username
            request.data["points"]=0
            request.data["status"]="P"
            profile_serializer = ProfileSerializer(data=request.data)
            if not profile_serializer.is_valid():
                user.delete()
                return Response(
                    profile_serializer.errors, status=status.HTTP_409_CONFLICT
                )

            profile_serializer.save(user=user)
            email_token=uuid.uuid4()
            verif_row=VerificationModel(userid=user,email_token=email_token)
            verif_row.save()
            referral_code = ReferralCode(user=user, referral_code=f"tnx24_{user.username}")
            referral_code.save()
            # send email to the user containing a link to verify their email
            send_email_verif_email(user.email, email_token)
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
    """
    Custom TokenObtainPairView to return access token
    """
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        try:
            user = UserAccount.objects.get(Q(username=username) | Q(email=username))
        except UserAccount.DoesNotExist:
            return Response(
                {"error": "User does not exist."}, status=status.HTTP_400_BAD_REQUEST
            )
        
        if user.status == "P":
            return Response(
                {"error": "User not verified by admin yet."}, status=status.HTTP_400_BAD_REQUEST
            )
        
        if not user.email_verified:
            return Response(
                {"error": "Email not verified! First verify email."}, status=status.HTTP_400_BAD_REQUEST
            )

        if bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
            data = {"username": user.username, "password": password}
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.validated_data, status=status.HTTP_200_OK)

        return Response(
            {"error": "Invalid password."}, status=status.HTTP_400_BAD_REQUEST
        )


class UserProfileView(generics.GenericAPIView):
    """
    Gives the detailed profile of the user
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    @swagger_auto_schema(
        responses={
            401: """ {"error": "Authorization header not found!"}""",
        },        
    )
    def get(self, request):
        """
        Retrieve the user profile.
        """
        user = request.user
        serializer = UserSerializer(user)
        referral_code = ReferralCode.objects.filter(user=user).first()
        data = serializer.data
        data['rank'] = UserProfile.objects.filter(points__gt=user.userprofile.points).count() + 1
        data["referral_code"] = referral_code.referral_code
        return Response(data, status=status.HTTP_200_OK)
    

class StatusCheck(views.APIView):
    def get(request, user):
        return Response(
            {"message":"Working"},
            status = status.HTTP_200_OK,
        )
   

class VerifyAccountView(views.APIView):
    """
    Verify the User Account by admin
    """
    permission_classes = [permissions.IsAuthenticated,IsAdminUser]
    #todo: any authenticated user is able to access this endpoint
    @swagger_auto_schema(
        responses={
            200: """{"success": "All verifiable users list"}""",
            400: """{"error": "Bad Request"}""",
        }
    )
    def get(self,request):
        try:
            vm_obs = VerificationModel.objects.all()
            profiles = UserProfile.objects.filter(user__in=[vm_ob.userid for vm_ob in vm_obs])
            serializer = ProfileSerializer(profiles, many=True)
            tokens=[vm_ob.email_token for vm_ob in vm_obs]
            for i,token in enumerate(tokens):
                serializer.data[i]["email_token"]=token
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )        
    
    @swagger_auto_schema(
        responses={
            200: """{"success": "User verified successfully!"}""",
            400: """{"error": "Bad Request"}""",
        }
    )
    def post(self, request):
        try:
            verif_row = VerificationModel.objects.filter(email_token=request.data["token"]).first()
            print(verif_row)
            if verif_row is None:
                return Response(
                    {"error": "Invalid token!"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user = verif_row.userid
            if user.email_verified == False:
                return Response(
                    {"error": "Email not verified! First verify email."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if user.status != "P":
                return Response(
                    {"error": "User already verified!"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            user.status = "V"
            verif_row.delete()
            user.save()
            send_approved_email(user.email)
            return Response(
                {"success": "User verified successfully!"},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        


class VerifyEmailView(views.APIView):
    """
    Verify the User Email by clicking on the link sent to the user's email
    """


    @swagger_auto_schema(
        responses={
            200: """{"success": "Email verified successfully!"}""",
            400: """{"error": "Bad Request"}""",
        }
    )
    def get(self,request,token):
        print(token)
        verif_row = VerificationModel.objects.filter(email_token=token).first()
        
        print(verif_row)
        if verif_row is None:
            return Response(
                {"error": "Invalid token!"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = verif_row.userid
        if user.email_verified:
            return HttpResponseRedirect(redirect_to=config("FRONTEND_URL")+"/login")
        user.email_verified = True
        user.save()
        # send_approved_email(user.email)
        # send email informing the user that email has been verified and account will shortly be activated after a review by our team
        send_email_cnf_email(user.email)
        print("returning success resp")
        return HttpResponseRedirect(redirect_to=config("FRONTEND_URL")+"/login")


class ForgotPasswordOTPCreationView(generics.GenericAPIView):
    """
    Creates an OTP for the user to reset their password
    """

    serializer_class = ForgotPasswordSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        responses={
            201: """{"detail": "OTP generated successfully"}""",
            404: """{"detail": "No such user"}""",
        }
    )
    def post(self, request):
        email = request.data["email"]
        user = UserAccount.objects.filter(email=email).first()
        if user is not None:
            otp = "{:06}".format(random.randint(1, 999999))
            user_otp = ForgotPasswordOTPModel.objects.filter(user=user).first()
            if user_otp is not None:
                user_otp.otp = otp
                user_otp.has_been_used = False
                user_otp.verified = False
                user_otp.save()
            else:
                ForgotPasswordOTPModel.objects.create(user=user, otp=otp)
            send_otp_email(user.email, otp)
            return Response(
                {"detail": "OTP generated successfully"}, status=status.HTTP_201_CREATED
            )
        return Response({"detail": "No such user"}, status=status.HTTP_404_NOT_FOUND)


class VerifyOTPView(generics.GenericAPIView):
    """
    Verifies the OTP sent to the user's email
    """
    serializer_class = VerifyOTPSerializer
    permission_classes = [permissions.AllowAny]
    @swagger_auto_schema(
        responses={
            202: """{"detail": "OTP Verified"}""",
            403: """{"detail": "Incorrect OTP"}""",
            408: """{"detail": "OTP Expired. Try again"}""",
            401: """{"detail": "OTP already used"}""",
            404: """{"detail": "No such user"}""",
        }
    )
    def post(self, request):
        email = request.data["email"]
        otp = request.data["otp"]

        user = UserAccount.objects.filter(email=email).first()
        if user is not None:
            user_otp = ForgotPasswordOTPModel.objects.filter(user=user, otp=otp).first()
            if not user_otp.has_been_used:
                if (
                    datetime.datetime.now(datetime.timezone.utc) - user_otp.last_created
                ).seconds > 600:
                    user_otp.delete()
                    return Response(
                        {"detail": "OTP Expired. Try again"},
                        status=status.HTTP_408_REQUEST_TIMEOUT,
                    )
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
    """
    Resets the password of the user
    """

    serializer_class = ResetPasswordSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        responses={
            200: """{"detail": "Password Reset Successfully"}""",
            400: """{"detail": "Passwords don't match"}""",
            401: """{"detail": "OTP not verified or has been already used."}""",
            404: """{"detail": "No such User"}""",
            409: """{"detail": "Password not strong enough"}""",
        }
    )
    def post(self, request):
        pass1 = request.data["password1"]
        pass2 = request.data["password2"]
        email = request.data["email"]
        user = UserAccount.objects.filter(email=email).first()
        user_otp = ForgotPasswordOTPModel.objects.filter(user=user).first()
        if user_otp.verified and not user_otp.has_been_used:
            if pass1 == pass2:
                raw_password = pass1
                try:
                    password_validation.validate_password(raw_password)
                except Exception as e:
                    return Response(
                        {"error": str(e)},
                        status=status.HTTP_409_CONFLICT,
                    )
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
                {"detail": "Passwords don't match"}, status=status.HTTP_400_BAD_REQUEST)
        return Response( {"detail": "OTP not verified or has been already used."}, status=status.HTTP_401_UNAUTHORIZED)
    

class AvatarChangeView(views.APIView):
    """
    Changes the avatar of the user
    """
    permission_classes = [permissions.IsAuthenticated]
    @swagger_auto_schema(
        responses={
            200: """{"detail": "Avatar changed successfully"}""",
        }
    )
    def patch(self, request, avatar_id):
        user = request.user
        profile = UserProfile.objects.filter(user=user).first()
        profile.avatar_id = avatar_id
        profile.save()
        return Response({"detail": "Avatar changed successfully"}, status=status.HTTP_200_OK)
    