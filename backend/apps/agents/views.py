from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from . import redis_utils, services
from .models import Agent
from .serializers import AgentLocationSerializer, AgentSerializer


class AgentLocationView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, agent_id):
        serializer = AgentLocationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if not services.is_ping_allowed(agent_id):
            return Response(
                {"detail": "Rate limit exceeded."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        payload = services.record_location(agent_id, data["lat"], data["lng"])
        return Response(payload, status=status.HTTP_200_OK)


class AgentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.action == "list":
            queryset = self.filter_queryset(self.get_queryset())
            agent_ids = list(queryset.values_list("id", flat=True))
            conn = redis_utils.get_conn()
            context["live_locations"] = redis_utils.read_many_agent_states(
                conn, agent_ids
            )
        return context
