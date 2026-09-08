from django.db import models
from django.utils import timezone


class Agent(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "available", "Available"
        BUSY = "busy", "Busy"
        OFFLINE = "offline", "Offline"

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    current_node_fk = models.ForeignKey(
        "graph.Node",
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
    last_seen = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [
            models.Index(
                fields=["status"],
                name="active_idx",
                condition=models.Q(status="available"),
            ),
        ]

    def __str__(self):
        return self.name
