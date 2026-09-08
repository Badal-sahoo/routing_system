from consumers.broadcast import send_fleet_event

from . import redis_utils


def record_location(agent_id, lat, lng):
    conn = redis_utils.get_conn()
    payload = redis_utils.write_agent_state(conn, agent_id, lat, lng)
    broadcast_location(agent_id, payload)
    return payload


def broadcast_location(agent_id, payload):
    send_fleet_event("gps", {"agent_id": agent_id, **payload})


def broadcast_agent(agent):
    from .serializers import AgentSerializer

    send_fleet_event("agent", {"agent": AgentSerializer(agent).data})


def is_ping_allowed(agent_id):
    return not redis_utils.is_rate_limited(redis_utils.get_conn(), agent_id)
