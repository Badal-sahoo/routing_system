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

    def __str__(self):
        return self.label


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

    def __str__(self):
        arrow = "<->" if self.is_bidirectional else "->"
        return f"{self.from_node_fk_id} {arrow} {self.to_node_fk_id} ({self.weight})"
