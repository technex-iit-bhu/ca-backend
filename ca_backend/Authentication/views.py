from django.shortcuts import render
from rest_framework import generics, serializers, status
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings
from django.contrib.auth import authenticate,login,logout
from drf_yasg.utils import swagger_auto_schema
from .models import UserAccount
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    check
)

# Create your views here.
class RegisterView(generics.GenericAPIView):
    queryset = UserAccount.objects.all()
    serializer_class = RegisterSerializer
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = check(request.data)
            if user is None:
                user = serializer.save()
                return Response(
                    {"success": "Verification link has been sent by email!"},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"error": "User with same credentials already exists!"},
                    status=status.HTTP_226_IM_USED,
                )
        else:
            error = {}
            for err in serializer.errors:
                error[err] = serializer.errors[err][0]
            return Response(error, status=status.HTTP_409_CONFLICT)


class LoginView(generics.GenericAPIView):
    """
    Implement login functionality, taking email and password
    as input, and returning the Token.
    """

    serializer_class = LoginSerializer

    @swagger_auto_schema(
        responses={
            200: """{ "token" : "......" }""",
            400: """{"error": "Please provide both username and password"}""",
            401: """{"error": "Please check your credentials...cannot login!"} 
                    {"error": "Please verify your email first and then login."}""",
            403: """{"error": "Your account has been deleted. For queries contact Registrations and Enquiry numbers mentioned in Contact Us section!"}""",
        }
    )
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        if username is None or password is None:
            return Response(
                {"error": "Please provide both username and password"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = authenticate(username=username, password=password)
        if not user:
            return Response(
                {"error": "Please check your credentials...cannot login!"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
       #TODO: check what to do if user is deleted or not verified
        # elif user.is_active is False:
        #     return Response(
        #         {"error": "Please verify your email first and then login."},
        #         status=status.HTTP_401_UNAUTHORIZED,
        #     )

        login(request, user)
        # payload = api_settings.JWT_PAYLOAD_HANDLER(user)
        # token = api_settings.JWT_ENCODE_HANDLER(payload)
        role = user.role
        return Response({"token": "rndm-token", "role": role})