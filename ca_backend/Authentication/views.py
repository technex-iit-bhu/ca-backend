import datetime
import uuid
from django.shortcuts import render, get_object_or_404
from rest_framework import generics, serializers, status, authentication, permissions
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings
from django.contrib.auth import authenticate,login,logout
from drf_yasg.utils import swagger_auto_schema

from ca_backend.permissions import IsAdminUser
from .models import UserAccount, VerificationModel, UserProfile
from .serializers import (
    ProfileSerializer,
    RegisterSerializer,
    LoginSerializer,
    VerificationSerializer,
    check,
    UserSerializer,
    CombinedRegisterProfileSerializer,
    
)
from .send_email import send_approved_email, send_email_cnf_email, send_email_verif_email
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
        print(str(request.data))
        request.data["referral_code"]=f'{uuid.uuid4()}_{datetime.datetime.now()}'
        raw_password = request.data.get("password")
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
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        try:
            user = UserAccount.objects.get(username=username)
        except UserAccount.DoesNotExist:
            return Response(
                {"error": "User does not exist."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.validated_data, status=status.HTTP_200_OK)

        return Response(
            {"error": "Invalid password."},
            status=status.HTTP_400_BAD_REQUEST
        )

class UserProfileView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class=UserSerializer
    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class StatusCheck(generics.GenericAPIView):
    def get(request, user):
        return Response(
            {"message":"Working"},
            status = status.HTTP_200_OK,
                )
   

class VerifyAccountView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated,IsAdminUser]
    #todo: any authenticated user is able to access this endpoint
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
        


class VerifyEmailView(generics.GenericAPIView):
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
            return Response(
                {"error": "Email already verified!"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.email_verified = True
        user.save()
        # send_approved_email(user.email)
        # send email informing the user that email has been verified and account will shortly be activated after a review by our team
        send_email_cnf_email(user.email)
        print("returning success resp")
        return Response(
            {"success": "Email verified successfully!"},
            status=status.HTTP_200_OK,
        )
