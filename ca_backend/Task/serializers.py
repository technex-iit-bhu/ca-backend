from rest_framework import serializers
from .models import Task
from Authentication.models import UserAccount

class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for the Task model's ListCreateView
    """
    class Meta:
        model = Task
        fields = "__all__"


class LeaderboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        fields = ['username','points']