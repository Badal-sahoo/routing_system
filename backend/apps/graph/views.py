from rest_framework import permissions, viewsets

from .models import Edge, Node
from .serializers import EdgeSerializer, NodeSerializer


class NodeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Node.objects.all()
    serializer_class = NodeSerializer
    permission_classes = [permissions.IsAuthenticated]


class EdgeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Edge.objects.select_related("from_node_fk", "to_node_fk")
    serializer_class = EdgeSerializer
    permission_classes = [permissions.IsAuthenticated]
