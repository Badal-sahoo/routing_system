from rest_framework import serializers

from .models import Edge, Node


class NodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Node
        fields = ["id", "label", "lat", "lng"]


class EdgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Edge
        fields = ["id", "from_node_fk", "to_node_fk", "weight", "is_bidirectional"]
