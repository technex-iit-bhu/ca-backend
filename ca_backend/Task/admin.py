from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from rest_framework.response import Response
from rest_framework import status
from .send_email import send_task_submission_email, send_task_admin_comment_email, send_task_submission_verification_email

# Register your models here.
from .models import Task, TaskSubmission

admin.site.site_header = "Technex '24 Campus Ambassador Admin"
admin.site.site_title = "Technex '24 Campus Ambassador Admin"
admin.site.index_title = "Welcome to Technex '24 Campus Ambassador Admin"

class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'points', 'deadline', 'image')
    list_filter = ('deadline',)
    search_fields = ('title', 'description', 'points', 'deadline')
    list_editable = ('title', 'description', 'points', 'deadline', 'image')
    list_display_links = None
    list_per_page = 10
    
    model = Task


class TaskSubmissionAdmin(admin.ModelAdmin):
    list_display = ('task', 'user', 'timestamp', 'link', 'verified', 'admin_comment', 'image')
    list_filter = ('verified','user')
    search_fields = ('task', 'user', 'timestamp', 'link', 'verified', 'admin_comment')
    list_editable = ['admin_comment']
    list_display_links = None
    list_per_page = 10

    # Send mail on admin comment
    def save_model(self, request, obj, form, change):
        if 'admin_comment' in form.changed_data:
            send_task_admin_comment_email(obj.user.user.email, obj.user.user_name, obj.admin_comment)
        super().save_model(request, obj, form, change)

    @admin.action(description='Verify Task Submission')
    def make_verified(self, request, queryset):            
        for task_submission in queryset:
            if not task_submission.verified:
                task_submission.verified = True
                task_submission.user.points += task_submission.task.points
                task_submission.user.save()
                send_task_submission_verification_email(task_submission.user.user.email, task_submission.user.user_name, task_submission.task.title)
        queryset.update(verified=True)

    @admin.action(description='Unverify Task Submission')
    def make_unverified(self, request, queryset):
        # add all the functionality from the actual endpoint here
        for task_submission in queryset:
            if task_submission.verified:
                task_submission.verified = False
                task_submission.user.points -= task_submission.task.points
                task_submission.user.save()
        queryset.update(verified=False)

    def delete_queryset(self, request: HttpRequest, queryset: QuerySet[Any]) -> None:
        for task_submission in queryset:
            if task_submission.image:
                task_submission.image.delete(save=True)
        return super().delete_queryset(request, queryset)
    
    actions = [make_verified, make_unverified]


    model = TaskSubmission

admin.site.register(Task, TaskAdmin)
admin.site.register(TaskSubmission, TaskSubmissionAdmin)

