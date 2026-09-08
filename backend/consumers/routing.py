from django.urls import path

from .location_consumer import LocationConsumer

websocket_urlpatterns = [
    path("ws/fleet/", LocationConsumer.as_asgi()),
]
