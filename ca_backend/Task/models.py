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
