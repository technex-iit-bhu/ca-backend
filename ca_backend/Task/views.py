from django.shortcuts import render
from rest_framework import generics, mixins, response, permissions, status
from .models import Task
from .serializers import TaskSerializer
from Authentication.models import CompletedTasks, UserTasksSent
from Authentication.serializers import CompletedTasksSerializer, UserTaskSentSerializer


# Create your views here.


class TaskListCreateAPIView(generics.ListCreateAPIView):
    """
    View for getting list of all Tasks and Creating New Tasks.
    Tasks can only be created by Admin User but viewed by all.
    """

    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class TaskManipulateAPIView(
    generics.GenericAPIView,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
):
    """
    Generic View for Deletion and Updation of the task. Can only be manipulated by Admin User. Can be seen by all.
    """

    queryset = Task.objects.all()
    lookup_field = "pk"
    serializer_class = TaskSerializer

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class TaskCompletionVerificationAPIView(generics.ListCreateAPIView):
    """
    View for Adding Tasks as completed for users.
    Will only add task as completed if not already done.
    """

    lookup_field = "pk"

    def get_queryset(self):
        return CompletedTasks.objects.filter(task=self.kwargs[self.lookup_field])

    serializer_class = CompletedTasksSerializer

    def post(self, request, *args, **kwargs):
        # user = UserAccount.objects.filter(id=request.data['user']).first()
        # if user.role != 3:
        #     return response.Response({"detail": "User not an Admin User"})
        if CompletedTasks.objects.filter(
            user=request.data["user"], task=request.data["task"]
        ).exists():
            return response.Response({"detail": "Task Already Completed"})
        return super().post(request, *args, **kwargs)


class TaskCompletionUserRequestAPIView(generics.CreateAPIView):
    """
    View for user to send request for a certain task. pk is the id of the task.
    """

    lookup_field = "pk"

    def post(self, request, *args, **kwargs):
        print(request.user)
        task = Task.objects.filter(id=self.kwargs[self.lookup_field]).first()
        if task is None:
            return response.Response({"detail": "No such task available"})
        if UserTasksSent.objects.filter(user=request.user, task=task).exists():
            return response.Response({"detail": "Task Already sent for review"})
        UserTasksSent.objects.create(user=request.user, task=task)
        return response.Response({"detail": "Request for review sent successfully."})


class TaskUserRequestSentAPIView(generics.ListAPIView):
    """
    View for the user to be able to see all the tasks sent for review by them.
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserTaskSentSerializer

    def get_queryset(self):
        return UserTasksSent.objects.filter(user=self.request.user.id)
    
class Status200ReturnView(generics.GenericAPIView):

    def get(self, request):
        return response.Response({"detail":"Status 200 "}, status=status.HTTP_200_OK)

