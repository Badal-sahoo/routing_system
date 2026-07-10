"""Development settings: everything in base plus a Redis cache backend."""

from .base import *  # noqa: F401,F403

DEBUG = True

# django-redis as the default cache. DB index 1 keeps this app's cache/live
# state separate from anything else that might use Redis DB 0.
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}
