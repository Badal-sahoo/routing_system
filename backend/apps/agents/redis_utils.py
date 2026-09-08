from django.conf import settings
from django.utils import timezone
from django_redis import get_redis_connection

STATE_TTL_SECONDS = settings.GPS_STATE_TTL_SECONDS
RATE_LIMIT_MAX = settings.GPS_RATE_LIMIT_MAX
RATE_LIMIT_WINDOW = settings.GPS_RATE_LIMIT_WINDOW


def get_conn():
    return get_redis_connection("default")


def agent_state_key(agent_id):
    return f"agent:{agent_id}:state"


def ratelimit_key(agent_id):
    return f"ratelimit:agent:{agent_id}"


def decode_state(state):
    if not state:
        return None
    return {key.decode(): value.decode() for key, value in state.items()}


def write_agent_state(conn, agent_id, lat, lng):
    key = agent_state_key(agent_id)
    payload = {
        "lat": str(lat),
        "lng": str(lng),
        "timestamp": timezone.now().isoformat(),
    }
    pipe = conn.pipeline()
    pipe.hset(key, mapping=payload)
    pipe.expire(key, STATE_TTL_SECONDS)
    pipe.execute()
    return payload


def read_agent_state(conn, agent_id):
    state = conn.hgetall(agent_state_key(agent_id))
    return decode_state(state)


def read_many_agent_states(conn, agent_ids):
    agent_ids = list(agent_ids)
    if not agent_ids:
        return {}

    pipe = conn.pipeline()
    for agent_id in agent_ids:
        pipe.hgetall(agent_state_key(agent_id))
    results = pipe.execute()

    states = {}
    for agent_id, state in zip(agent_ids, results):
        states[agent_id] = decode_state(state)
    return states


def is_rate_limited(conn, agent_id):
    key = ratelimit_key(agent_id)
    current = conn.incr(key)
    if current == 1:
        conn.expire(key, RATE_LIMIT_WINDOW)
    return current > RATE_LIMIT_MAX
