from rest_framework import serializers

from . import redis_utils
from .models import Agent


class AgentLocationSerializer(serializers.Serializer):
    lat = serializers.DecimalField(
        max_digits=11, decimal_places=8, min_value=-90, max_value=90
    )
    lng = serializers.DecimalField(
        max_digits=11, decimal_places=8, min_value=-180, max_value=180
    )


class AgentSerializer(serializers.ModelSerializer):
    live_location = serializers.SerializerMethodField()

    class Meta:
        model = Agent
        fields = [
            "id",
            "name",
            "current_node_fk",
            "status",
            "last_seen",
            "live_location",
        ]

    def get_live_location(self, agent):
        cached = self.context.get("live_locations")
        if cached is not None:
            return cached.get(agent.id)
        return redis_utils.read_agent_state(redis_utils.get_conn(), agent.id)
