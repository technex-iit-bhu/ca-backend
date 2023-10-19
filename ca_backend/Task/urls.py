from django.urls import path
from .views import (
    TaskListCreateAPIView,
    TaskManipulateAPIView,
    TaskCompletionVerificationAPIView,
    TaskCompletionUserRequestAPIView,
    TaskUserRequestSentAPIView,
)

urlpatterns = [
    path("", TaskListCreateAPIView.as_view(), name="tasks"),
    path("<int:pk>/", TaskManipulateAPIView.as_view(), name="task_update"),
    path(
        "allot/<int:pk>/",
        TaskCompletionVerificationAPIView.as_view(),
        name="allot-points",
    ),
    path(
        "review/<int:pk>/",
        TaskCompletionUserRequestAPIView.as_view(),
        name="user-request",
    ),
    path("review/all/", TaskUserRequestSentAPIView.as_view(), name="task-in-review"),
]
