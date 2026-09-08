from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .location_consumer import FLEET_GROUP


def send_fleet_event(kind, payload):
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return

    async_to_sync(channel_layer.group_send)(
        FLEET_GROUP,
        {"type": "fleet.update", "data": {"kind": kind, **payload}},
    )
