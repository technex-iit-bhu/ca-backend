from django.urls import path
from .views import TaskListCreateAPIView, TaskManipulateAPIView, TaskLeaderboardView

urlpatterns = [
    path("", TaskListCreateAPIView.as_view(), name="tasks"),
    path("<int:pk>/", TaskManipulateAPIView.as_view(), name="task_update"),
    path("leaderboard/", TaskLeaderboardView.as_view(), name="leaderboard"),
]
