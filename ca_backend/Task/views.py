from django.shortcuts import render
from rest_framework import generics, mixins
from .models import Task
from .serializers import TaskSerializer
from . import permissions as CustomPerms


# Create your views here.

class TaskListCreateAPIView(generics.ListCreateAPIView):
    """
    View for getting list of all Tasks and Creating New Tasks.
    Tasks can only be created by Admin User but viewed by all.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

class TaskManipulateAPIView(generics.GenericAPIView, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, mixins.UpdateModelMixin):
    """
    Generic View for Deletion and Updation of the task. Can only be manipulated by Admin User. Can be seen by all.
    """
    queryset = Task.objects.all()
    lookup_field = 'pk'
    serializer_class = TaskSerializer

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
    
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)