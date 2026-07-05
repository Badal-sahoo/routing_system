from django.db import models


class Node(models.Model):
    id = models.BigAutoField(primary_key=True)
    label = models.CharField(max_length=255)
    lat = models.DecimalField(max_digits=11, decimal_places=8)
    lng = models.DecimalField(max_digits=11, decimal_places=8)

    class Meta:
        indexes = [
            models.Index(fields=["lat", "lng"]),
        ]


class Edge(models.Model):
    id = models.BigAutoField(primary_key=True)
    from_node_fk = models.ForeignKey(
        Node,
        on_delete=models.CASCADE,
        related_name="outgoing_edges",
    )
    to_node_fk = models.ForeignKey(
        Node,
        on_delete=models.CASCADE,
        related_name="incoming_edges",
    )
    weight = models.IntegerField()
    is_bidirectional = models.BooleanField(default=False)


class Agent(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "available", "Available"
        BUSY = "busy", "Busy"
        OFFLINE = "offline", "Offline"

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    current_node_fk = models.ForeignKey(
        Node,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="agents",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OFFLINE,
    )
    last_seen = models.DateTimeField()

    class Meta:
        indexes = [
            models.Index(
                fields=["status"],
                name="active_idx",
                condition=models.Q(status="available"),
            ),
        ]


class Task(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ASSIGNED = "assigned", "Assigned"
        IN_PROGRESS = "in_progress", "In progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    id = models.BigAutoField(primary_key=True)
    origin_node_fk = models.ForeignKey(
        Node,
        on_delete=models.CASCADE,
        related_name="origin_tasks",
    )
    destination_node_fk = models.ForeignKey(
        Node,
        on_delete=models.CASCADE,
        related_name="destination_tasks",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    assigned_agent_fk = models.ForeignKey(
        Agent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
    )
    created_at = models.DateTimeField(auto_now_add=True)
