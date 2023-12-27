from django.contrib import admin

# Register your models here.
from .models import Task, TaskSubmission


class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'points', 'deadline')
    list_filter = ('deadline',)
    search_fields = ('title', 'description', 'points', 'deadline')
    list_editable = ('title', 'description', 'points', 'deadline')
    list_display_links = None
    
    model = Task


class TaskSubmissionAdmin(admin.ModelAdmin):
    list_display = ('task', 'user', 'timestamp', 'link', 'verified', 'admin_comment')
    list_filter = ('verified',)
    search_fields = ('task', 'user', 'timestamp', 'link', 'verified', 'admin_comment')
    list_editable = ('verified', 'admin_comment')


    model = TaskSubmission

admin.site.register(Task, TaskAdmin)
admin.site.register(TaskSubmission, TaskSubmissionAdmin)

