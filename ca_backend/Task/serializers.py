from rest_framework import serializers
from .models import Task
from Authentication.models import UserProfile


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
        fields = ["user_name", "points"]
