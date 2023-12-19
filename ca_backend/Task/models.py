from django.db import models

# Create your models here.


class Task(models.Model):
    """
    Model for Tasks.
    Stores Title, Description and the Points worth of the Task
    """

    title = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(blank=True, null=False)
    points = models.IntegerField(null=False, default=0)
    deadline = models.DateTimeField(null=False, blank=False, default="2024-01-01 00:00:00", editable=True)


class TaskSubmission(models.Model):
    """
    Model for Task Submission.
    Stores the Task, the User who submitted it and the Timestamp of the Submission.
    """

    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    user = models.ForeignKey("Authentication.UserProfile", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)