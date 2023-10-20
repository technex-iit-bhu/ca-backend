from django.shortcuts import render
from rest_framework import generics, mixins, status
from .models import Task
from .serializers import TaskSerializer
from . import permissions as CustomPerms
from Authentication.models import UserProfile
from .serializers import LeaderboardSerializer
from rest_framework.response import Response
from .permissions import IsAdminUser, IsStaffUser


# Create your views here.

class TaskListCreateAPIView(generics.ListCreateAPIView):
    """
    View for getting list of all Tasks and Creating New Tasks.
    Tasks can only be created by Admin User but viewed by all.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsStaffUser]

class TaskManipulateAPIView(generics.GenericAPIView, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, mixins.UpdateModelMixin):
    """
    Generic View for Deletion and Updation of the task. Can only be manipulated by Admin User. Can be seen by all.
    """
    queryset = Task.objects.all()
    lookup_field = 'pk'
    serializer_class = TaskSerializer
    permission_classes = [IsStaffUser]


    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
    
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
    

class TaskLeaderboardView(generics.GenericAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = LeaderboardSerializer
    def get(self,request):
        all_users_pf=UserProfile.objects.all()
        all_users_pf=all_users_pf.order_by('-points')
        serializer=LeaderboardSerializer(all_users_pf,many=True)
        serializer_data=serializer.data
        return Response(serializer_data,status=status.HTTP_200_OK)