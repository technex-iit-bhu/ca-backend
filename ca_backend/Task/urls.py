from django.urls import path
from .views import (TaskListCreateAPIView,
                     TaskManipulateAPIView,
                       TaskLeaderboardView,
                       SubmitTaskAPIView,
                       AdminVerifyTaskSubmissionAPIView,
                       SubmittedUserTasksListAPIView,
                       UserSubmittedTasksListAPIView)


urlpatterns = [
    path("", TaskListCreateAPIView.as_view(), name="tasks"),
    path("<int:pk>/", TaskManipulateAPIView.as_view(), name="task_update"),
    path("leaderboard/", TaskLeaderboardView.as_view(), name="leaderboard"),
    path("submit/<int:task_id>/", SubmitTaskAPIView.as_view(), name="submit_task"),
    path("verify/<int:task_submission_id>/", AdminVerifyTaskSubmissionAPIView.as_view(), name="verify_task_submission"),
    path("verify/", SubmittedUserTasksListAPIView.as_view(), name="verify_task_submission"),
    path("submitted/", UserSubmittedTasksListAPIView.as_view(), name="verify_task_submission"),
]
