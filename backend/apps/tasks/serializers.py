from rest_framework import serializers

from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    total_eta_minutes = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            "id",
            "origin_node_fk",
            "destination_node_fk",
            "status",
            "assigned_agent_fk",
            "created_at",
            "pickup_eta_minutes",
            "delivery_eta_minutes",
            "total_eta_minutes",
        ]
        read_only_fields = [
            "status",
            "assigned_agent_fk",
            "created_at",
            "pickup_eta_minutes",
            "delivery_eta_minutes",
        ]

    def get_total_eta_minutes(self, task):
        if task.pickup_eta_minutes is None or task.delivery_eta_minutes is None:
            return None
        return task.pickup_eta_minutes + task.delivery_eta_minutes
