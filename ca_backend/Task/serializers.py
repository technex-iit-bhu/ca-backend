from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for the Task model's ListCreateView
    """
    class Meta:
        model = Task
        fields = "__all__"