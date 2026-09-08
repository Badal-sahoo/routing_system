from django.db import models


class Task(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ASSIGNED = "assigned", "Assigned"
        IN_PROGRESS = "in_progress", "In progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    id = models.BigAutoField(primary_key=True)
    origin_node_fk = models.ForeignKey(
        "graph.Node",
        on_delete=models.CASCADE,
        related_name="origin_tasks",
    )
    destination_node_fk = models.ForeignKey(
        "graph.Node",
        on_delete=models.CASCADE,
        related_name="destination_tasks",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    assigned_agent_fk = models.ForeignKey(
        "agents.Agent",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    pickup_eta_minutes = models.PositiveIntegerField(
        null=True, blank=True, help_text="Rider's current node -> pickup point."
    )
    delivery_eta_minutes = models.PositiveIntegerField(
        null=True, blank=True, help_text="Pickup point -> destination."
    )

    class Meta:
        indexes = [
            models.Index(fields=["status", "created_at"]),
        ]

    def __str__(self):
        return f"Task {self.id} ({self.status})"
