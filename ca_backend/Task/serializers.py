from rest_framework import serializers
from .models import Task ,TaskSubmission
from Authentication.models import UserProfile
from Authentication.serializers import ProfileSerializer


class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for the Task model's ListCreateView
    """

    class Meta:
        model = Task
        fields = "__all__"


class LeaderboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["user_name","first_name","last_name", "points"]


class TaskSubmissionSerializer(serializers.ModelSerializer):
    """
    Serializer for the Task Submission model's CreateView
    """

    task = TaskSerializer(read_only=True)
    
    class Meta:
        model = TaskSubmission
        fields = "__all__"