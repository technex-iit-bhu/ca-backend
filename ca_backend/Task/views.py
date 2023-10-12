from django.shortcuts import render
from rest_framework import generics, authentication
from .models import Task
from .serializers import TaskSerializer
from . import permissions


# Create your views here.

class TaskListCreateAPIView(generics.ListCreateAPIView):
    """
    View for getting list of all Tasks and Creating New Tasks.
    Tasks can only be created by Admin User
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAdminUser]

