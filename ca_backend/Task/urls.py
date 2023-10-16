from django.urls import path
from .views import TaskListCreateAPIView, TaskManipulateAPIView, TaskCompletionVerificationAPIView

urlpatterns = [
    path('', TaskListCreateAPIView.as_view(), name='tasks'),
    path('<int:pk>/', TaskManipulateAPIView.as_view(), name='task_update'),
    path('allot/<int:pk>', TaskCompletionVerificationAPIView.as_view(), name='allot-points')
]