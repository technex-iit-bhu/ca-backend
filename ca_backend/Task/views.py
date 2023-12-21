from django.shortcuts import render
from rest_framework import generics, mixins, status, views, permissions
from .models import Task ,TaskSubmission
from .serializers import TaskSerializer
from Authentication.models import UserProfile
from .serializers import LeaderboardSerializer , TaskSubmissionSerializer
from rest_framework.response import Response
from ca_backend.permissions import IsAdminUser, IsStaffUser
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# import Url validator
from django.core.validators import URLValidator

# Create your views here.


class TaskListCreateAPIView(generics.ListCreateAPIView):
    """
    View for getting list of all Tasks and Creating New Tasks.
    Tasks can only be created by Admin User but viewed by all.
    """

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsStaffUser]


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

    def get(self, request):
        all_users_pf = UserProfile.objects.all()
        all_users_pf = all_users_pf.order_by("-points")
        serializer = LeaderboardSerializer(all_users_pf, many=True)
        serializer_data = serializer.data
        return Response(serializer_data, status=status.HTTP_200_OK)


class SubmitTaskAPIView(views.APIView):
    """
    View for Submitting the Task. Can only be submitted by Verified Users.
    """

    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(manual_parameters=[openapi.Parameter('link', openapi.IN_QUERY, description="Link to the Task Submission", type=openapi.TYPE_STRING)])
    def post(self, request, task_id, *args, **kwargs):
        user_id = request.user
        task = Task.objects.filter(id=task_id).first()
        if task is None:
            return Response({"status": "Task Does Not Exist"}, status=status.HTTP_404_NOT_FOUND)
        if task.deadline < timezone.now():
            return Response({"status": "Task Deadline Expired"}, status=status.HTTP_400_BAD_REQUEST)
        user = UserProfile.objects.filter(user=user_id).first()
        if TaskSubmission.objects.filter(task=task, user=user).exists():
            return Response({"status: Task Already Submitted"},status=status.HTTP_400_BAD_REQUEST)
        
        validate = URLValidator()
        try:
            link = request.data["link"]
            validate(link)
        except KeyError:
            link = None
        except Exception as e:
            return Response({"status": "Invalid Link"}, status=status.HTTP_400_BAD_REQUEST)

        task_submission = TaskSubmission(task=task, user=user, link=link)
        
        task_submission.save()
        return Response({"status": "Task Submitted"}, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(manual_parameters=[openapi.Parameter('link', openapi.IN_QUERY, description="Link to the Task Submission", type=openapi.TYPE_STRING)])
    def patch(self, request, task_id, *args, **kwargs):
        """
        View for Updating the Task Submission. Can only be accessed by the User who submitted the Task.
        """
        if not TaskSubmission.objects.filter(task=task_id).exists():
            return Response({"status": "Task Submission Does Not Exist"}, status=status.HTTP_404_NOT_FOUND)
        # validate if the link is valid
        validate = URLValidator()
        try:
            validate(request.data["link"])
        except Exception as e:
            return Response({"status": "Invalid Link"}, status=status.HTTP_400_BAD_REQUEST)
        user_id = request.user
        task = Task.objects.filter(id=task_id).first()
        user = UserProfile.objects.filter(user=user_id).first()
        task_submission = TaskSubmission.objects.filter(task=task, user=user).first()
        task_submission.link = request.data["link"]
        task_submission.save()
        return Response({"status": "Task Submission Updated"}, status=status.HTTP_200_OK)
    

class AdminVerifyTaskSubmissionAPIView(views.APIView):
    permission_classes = [IsStaffUser]

    @swagger_auto_schema(manual_parameters=[openapi.Parameter('admin_comment', openapi.IN_QUERY, description="Admin Comment", type=openapi.TYPE_STRING)])
    def post(self, request, task_submission_id, *args, **kwargs):
        """
        View for Admin to verify the Task Submission. Can only be accessed by Admin/Staff User. This will verify the task submission and add the points to the user's profile.
        """
        
        if not TaskSubmission.objects.filter(id=task_submission_id).exists():
            return Response({"status": "Task Submission Does Not Exist"}, status=status.HTTP_404_NOT_FOUND)
        if TaskSubmission.objects.get(id=task_submission_id).verified:
            return Response({"status": "Task Submission Already Verified"}, status=status.HTTP_400_BAD_REQUEST)
        task_submission = TaskSubmission.objects.get(id=task_submission_id)
        user = task_submission.user
        task = task_submission.task
        user.points += task.points
        user.save()
        task_submission.verified = True
        try:
            task_submission.admin_comment = request.data["admin_comment"]
        except KeyError:
            pass
        task_submission.save()
        return Response({"status": "Task Submission Verified"}, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(manual_parameters=[openapi.Parameter('admin_comment', openapi.IN_QUERY, description="Admin Comment", type=openapi.TYPE_STRING)])
    def patch(self, request, task_submission_id, *args, **kwargs):
        """
        View for Admin to comment on the Task Submission. Can only be accessed by Admin/Staff User. Use this if not verifying the task submission.
        """
        if request.user.role < 2:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        if not TaskSubmission.objects.filter(id=task_submission_id).exists():
            return Response({"status": "Task Submission Does Not Exist"}, status=status.HTTP_404_NOT_FOUND)
        task_submission = TaskSubmission.objects.get(id=task_submission_id)
        task_submission.admin_comment = request.data["admin_comment"]
        task_submission.save()
        return Response({"status": "Task Submission Commented"}, status=status.HTTP_200_OK)
    

class SubmittedUserTasksListAPIView(generics.GenericAPIView):
    """
    View for getting list of all unverified Tasks submitted by all users. Can only be accessed by Admin/Staff User.
    """

    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    serializer_class = TaskSubmissionSerializer
    queryset = TaskSubmission.objects.all()

    def get(self, request):
        if request.user.role < 2:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        task_submissions = TaskSubmission.objects.filter(verified=False)
        serializer = TaskSubmissionSerializer(task_submissions, many=True)
        try:
            serializer_data = serializer.data
        except Exception as e:
            return Response({"status": "No Task Submission Found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer_data, status=status.HTTP_200_OK)
    

class UserSubmittedTasksListAPIView(generics.GenericAPIView):
    """
    View for getting list of all Tasks submitted by a particular user.
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TaskSubmissionSerializer
    queryset = TaskSubmission.objects.all()

    def get(self, request):
        user_id = request.user
        user_id = UserProfile.objects.filter(user=user_id).first()
        task_submissions = TaskSubmission.objects.filter(user=user_id)
        serializer = TaskSubmissionSerializer(task_submissions, many=True)
        try:
            serializer_data = serializer.data
        except Exception as e:
            return Response({"status": "No Task Submission Found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer_data, status=status.HTTP_200_OK)