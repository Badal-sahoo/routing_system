"""Redis helpers for high-frequency agent GPS state.

We drop below the Django cache API to the raw redis client (via
``get_redis_connection``) because we need Hash operations (HSET) and per-key
TTLs, which the cache API does not expose.
"""

from django.utils import timezone
from django_redis import get_redis_connection

STATE_TTL_SECONDS = 30
RATE_LIMIT_MAX = 10          # pings allowed per window
RATE_LIMIT_WINDOW = 10       # window length in seconds


def get_conn():
    """Raw redis-py client backing the 'default' django-redis cache."""
    return get_redis_connection("default")


def agent_state_key(agent_id):
    return f"agent:{agent_id}:state"


def ratelimit_key(agent_id):
    return f"ratelimit:agent:{agent_id}"


def write_agent_state(conn, agent_id, lat, lng):
    """Write {lat, lng, timestamp} to the agent's Hash and (re)set its TTL."""
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


def is_rate_limited(conn, agent_id):
    """Simple fixed-window limiter: INCR the counter, set its TTL on the first
    hit of the window. Returns True once the agent exceeds its ping budget."""
    key = ratelimit_key(agent_id)
    current = conn.incr(key)
    if current == 1:
        conn.expire(key, RATE_LIMIT_WINDOW)
    return current > RATE_LIMIT_MAX
