from django.db import models
import datetime
# Create your models here.


def upload_to(instance, filename):
    return "task_images/{filename}".format(filename=filename)

class Task(models.Model):
    """
    Model for Tasks.
    Stores Title, Description and the Points worth of the Task
    """

    title = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(blank=True, null=False)
    points = models.IntegerField(null=False, default=0)
    deadline = models.DateTimeField(null=False, blank=False, default=datetime.datetime(2023, 12, 28, 22, 23, 18, 757893), help_text="Deadline for the Task", editable=True)
    image = models.ImageField(upload_to=upload_to, null=True, blank=True)

    def __str__(self):
        return self.title


class TaskSubmission(models.Model):
    """
    Model for Task Submission.
    Stores the Task, the User who submitted it and the Timestamp of the Submission.
    """

    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    user = models.ForeignKey("Authentication.UserProfile", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    link = models.URLField(blank=True, null=True)
    verified = models.BooleanField(default=False)
    admin_comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.task.title + " - " + self.user.user_name