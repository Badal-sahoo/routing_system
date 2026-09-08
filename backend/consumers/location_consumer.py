import json

from channels.generic.websocket import AsyncWebsocketConsumer

FLEET_GROUP = "fleet_updates"


class LocationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add(FLEET_GROUP, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(FLEET_GROUP, self.channel_name)

    async def fleet_update(self, event):
        await self.send(text_data=json.dumps(event["data"]))
