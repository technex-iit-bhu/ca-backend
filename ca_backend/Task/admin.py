from django.contrib import admin

# Register your models here.
from .models import Task, TaskSubmission

admin.site.register(Task)
admin.site.register(TaskSubmission)