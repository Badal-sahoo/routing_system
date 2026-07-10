from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .redis_utils import get_conn, is_rate_limited, write_agent_state
from .serializers import AgentLocationSerializer


class AgentLocationView(APIView):
    """POST /api/agents/{id}/location/ -- ingest a GPS ping into Redis.

    High-frequency writes land in a Redis Hash (agent:{id}:state) with a short
    TTL; PostgreSQL is intentionally NOT touched here.

    Known gap: we do not verify the Agent exists in the DB -- doing so on every
    ping would defeat this layer. A rogue client can therefore pollute Redis
    with fake ids; to be closed with authentication later.
    """

    def post(self, request, agent_id):
        conn = get_conn()

        if is_rate_limited(conn, agent_id):
            return Response(
                {"detail": "Rate limit exceeded."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        serializer = AgentLocationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        payload = write_agent_state(conn, agent_id, data["lat"], data["lng"])
        return Response(payload, status=status.HTTP_200_OK)
