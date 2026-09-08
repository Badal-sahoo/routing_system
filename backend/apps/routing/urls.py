from django.urls import path

from .views import DispatchTaskView

urlpatterns = [
    path(
        "tasks/<int:task_id>/dispatch/",
        DispatchTaskView.as_view(),
        name="task-dispatch",
    ),
]
