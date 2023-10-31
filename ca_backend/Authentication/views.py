import datetime
import uuid
from django.shortcuts import render
from rest_framework import generics, serializers, status, authentication, permissions
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings
from django.contrib.auth import authenticate,login,logout
from drf_yasg.utils import swagger_auto_schema

from ca_backend.permissions import IsAdminUser
from .models import UserAccount, VerificationModel
from .serializers import (
    ProfileSerializer,
    RegisterSerializer,
    LoginSerializer,
    VerificationSerializer,
    check,
    UserSerializer,
    CombinedRegisterProfileSerializer,
    
)
from .send_email import send_verification_email
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
            send_verification_email(user.email, email_token)
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
   

class VerifyTokenView(generics.GenericAPIView):
    permission_classes = [IsAdminUser]
    def get(self,request):
        vm_obs = VerificationModel.objects.filter()
        
        # for vm in vm_obs:
        #     print(f"User ID: {vm.userid.username+vm.userid.email}, Email Token: {vm.email_token}")
        unverified_users_s = VerificationSerializer(data=vm_obs,many=True,raise_exception=True)
        try:

            unverified_users_s.is_valid()
        except Exception as e:
            print(e)
        print("hello")
        unverified_users = unverified_users_s.data
        print(unverified_users)
        return Response(
            {"unverified_users":"unverified_users"},
            status = status.HTTP_200_OK,
                )
    def post(self, request):
        try:
            verif_row = VerificationModel.objects.get(email_token=request.get("email_token"))
        except VerificationModel.DoesNotExist:
            return Response(
                {"error": "Invalid token!"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        userid = verif_row.userid
        user=UserAccount.objects.first(id=userid)
        user.status = "V"
        user.save()
        verif_row.delete()
        return Response(
            {"success": "User verified successfully!"},
            status=status.HTTP_200_OK,
        )