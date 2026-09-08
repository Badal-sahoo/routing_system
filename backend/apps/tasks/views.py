from rest_framework import permissions, viewsets

from .models import Task
from .serializers import TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.select_related(
        "origin_node_fk", "destination_node_fk", "assigned_agent_fk"
    )
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
