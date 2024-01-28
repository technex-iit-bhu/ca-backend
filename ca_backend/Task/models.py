from django.db import models
import datetime
from PIL import Image
from io import BytesIO
from django.core.files.images import ImageFile
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys
# Create your models here.


def upload_to(instance, filename):
    return "task_images/{filename}".format(filename=filename)

def sumbission_upload_to(instance, filename):
    user = instance.user
    task = instance.task
    return f"task_submissions/{user.user_name}_{task}_{filename}"

class Task(models.Model):
    """
    Model for Tasks.
    Stores Title, Description and the Points worth of the Task
    """


    title = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(blank=True, null=False)
    points = models.IntegerField(null=False, default=0)
    incentives = models.TextField(blank=True, default='no incentive🤡')

    deadline = models.DateTimeField(null=False, blank=False, default=datetime.datetime(2023, 12, 28, 22, 23, 18, 757893), help_text="Deadline for the Task", editable=True)
    image = models.ImageField(upload_to=upload_to, null=True, blank=True, help_text="Image for the Task")

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
    link = models.URLField(blank=True, null=True, help_text="Link to the Task Submission")
    image = models.ImageField(upload_to=sumbission_upload_to, null=True, blank=True, help_text="Image of the Task Submission")
    verified = models.BooleanField(default=False, help_text="Whether the Task Submission is Verified")
    admin_comment = models.TextField(blank=True, null=True, help_text="Admin Comment for the Task Submission")

    def __str__(self):
        return self.task.title + " - " + self.user.user_name

    def save(self, *args, **kwargs):
        if self.image:
            self.image = self.compressImage(self.image)
        super(TaskSubmission, self).save(*args, **kwargs)

    def compressImage(self, uploadedImage):
        imageTemporary = Image.open(uploadedImage)
        outputIoStream = BytesIO()
        if imageTemporary.mode in ("RGBA", "P"):
            imageTemporary = imageTemporary.convert("RGB")
        imageTemporary.save(outputIoStream, format='JPEG', quality=60)
        outputIoStream.seek(0)
        uploadedImage = InMemoryUploadedFile(outputIoStream, 'ImageField', f"{uploadedImage.name.split('.')[0]}.jpg", 'image/jpeg', sys.getsizeof(outputIoStream), None)
        return uploadedImage