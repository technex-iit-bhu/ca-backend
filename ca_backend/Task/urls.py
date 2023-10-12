from django.urls import path
from .views import TaskListCreateAPIView

urlpatterns = [
    path('', TaskListCreateAPIView.as_view(), name='tasks'),
]