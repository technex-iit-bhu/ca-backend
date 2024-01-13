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
from rest_framework import parsers
from Authentication.serializers import ProfileSerializer
from .send_email import send_task_admin_comment_email, send_task_submission_email, send_task_submission_verification_email

# import Url validator
from django.core.validators import URLValidator

import smtplib
from decouple import config

connection = smtplib.SMTP("smtp.gmail.com", port=587)
connection.starttls()
connection.login(config("EMAIL_HOST_USER"), config("EMAIL_HOST_PASSWORD"))

# Create your views here.


class TaskListCreateAPIView(generics.ListCreateAPIView):
    """
    View for getting list of all Tasks and Creating New Tasks.
    Tasks can only be created by Admin User but viewed by all.
    """

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsStaffUser]
    parser_classes = [parsers.MultiPartParser]



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
    parser_classes = [parsers.MultiPartParser]

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
    parser_classes = [parsers.MultiPartParser]

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('link', openapi.IN_FORM, type=openapi.TYPE_STRING, description='Link to the Task Submission'),
        openapi.Parameter('image', openapi.IN_FORM, type=openapi.TYPE_FILE, description='Image of the Task Submission')
    ])
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
            if link == "":
                link = None
                pass
            else:
                validate(link)
        except KeyError:
            link = None
        except Exception as e:
            print(e)
            return Response({"status": "Invalid Link"}, status=status.HTTP_400_BAD_REQUEST)

        image = request.data.get("image", None)    
        task_submission = TaskSubmission(task=task, user=user, link=link, image=image)
        
        task_submission.save()
        send_task_submission_email(user.user.email, user.user_name, task.title, connection)
        return Response({"status": "Task Submitted"}, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('link', openapi.IN_FORM, type=openapi.TYPE_STRING, description='Link to the Task Submission'),
        openapi.Parameter('image', openapi.IN_FORM, type=openapi.TYPE_FILE, description='Image of the Task Submission')
    ])
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
            link = request.data["link"]
        except KeyError:
            link = None
        except Exception as e:
            print(e)
            return Response({"status": "Invalid Link"}, status=status.HTTP_400_BAD_REQUEST)
        user_id = request.user
        task = Task.objects.filter(id=task_id).first()
        user = UserProfile.objects.filter(user=user_id).first()
        task_submission = TaskSubmission.objects.filter(task=task, user=user).first()
        if link is not None:
            task_submission.link = link
            
        image = request.data.get("image", None)
        if image is not None:
            task_submission.image = image

        task_submission.save()
        return Response({"status": "Task Submission Updated"}, status=status.HTTP_200_OK)
    

class AdminVerifyTaskSubmissionAPIView(views.APIView):
    permission_classes = [IsStaffUser]

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'admin_comment': openapi.Schema(type=openapi.TYPE_STRING, description='Admin Comment')
        }
    ))
    def post(self, request, task_submission_id, *args, **kwargs):
        """
        View for Admin to verify the Task Submission. Can only be accessed by Admin/Staff User. This will verify the task submission and add the points to the user's profile.
        """
        
        if not TaskSubmission.objects.filter(id=task_submission_id).exists():
            return Response({"status": "Task Submission Does Not Exist"}, status=status.HTTP_404_NOT_FOUND)
        task_submission = TaskSubmission.objects.select_related('user', 'task').get(id=task_submission_id)
        if task_submission.verified:
            return Response({"status": "Task Submission Already Verified"}, status=status.HTTP_400_BAD_REQUEST)
        
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
        # send email to the user
        send_task_submission_verification_email(user.user.email, user.user_name, task.title, connection)
        
        return Response({"status": "Task Submission Verified"}, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'admin_comment': openapi.Schema(type=openapi.TYPE_STRING, description='Admin Comment')
        }
    ))
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
        # send email to the user
        send_task_admin_comment_email(task_submission.user.user.email, task_submission.user.user_name, task_submission.admin_comment, connection)
        return Response({"status": "Task Submission Commented"}, status=status.HTTP_200_OK)
    

class SubmittedUserTasksListAPIView(generics.ListAPIView):
    """
    View for getting list of all Tasks submitted by all users. Can only be accessed by Admin/Staff User.
    """

    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    serializer_class = TaskSubmissionSerializer
    
    def get(self, request, *args, **kwargs):
        # add list of all users to the response
        users = UserProfile.objects.all().select_related('user').prefetch_related('tasksubmission_set', 'tasksubmission_set__task')
        response = []
        for user in users:
            user_submissions_serializer = TaskSubmissionSerializer(user.tasksubmission_set.all(), many=True)
            # Fix: Check if the link is a relative URL and prepend the base URL if necessary
            for submission in user_submissions_serializer.data:
                if submission['image'] and not submission['image'].startswith('http'):
                    submission['image'] = request.build_absolute_uri(submission['image'])
                if submission['task']['image'] and not submission['task']['image'].startswith('http'):
                    submission['task']['image'] = request.build_absolute_uri(submission['task']['image'])
            response.append({"user": user.user_name,
                             "email": user.user.email,
                              "submissions": user_submissions_serializer.data})
       
        return Response(response, status=status.HTTP_200_OK)

    
    

class UserSubmittedTasksListAPIView(generics.ListAPIView):
    """
    View for getting list of all Tasks submitted by a particular user.
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TaskSubmissionSerializer
    
    def get_queryset(self):
        user = self.request.user
        profile = UserProfile.objects.get(user=user)
        return TaskSubmission.objects.filter(user=profile)