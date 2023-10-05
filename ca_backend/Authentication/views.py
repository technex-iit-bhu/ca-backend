from django.shortcuts import render
from rest_framework import generics, serializers, status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from .models import UserAccount
from .serializers import (
    RegisterSerializer,
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
    pass