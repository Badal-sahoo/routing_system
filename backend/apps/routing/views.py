from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.tasks.models import Task

from .tasks import dispatch_task


class DispatchTaskView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, task_id):
        get_object_or_404(Task, pk=task_id)
        result = dispatch_task.delay(task_id)
        return Response(
            {"task_id": task_id, "celery_task_id": result.id, "status": "queued"},
            status=status.HTTP_202_ACCEPTED,
        )
