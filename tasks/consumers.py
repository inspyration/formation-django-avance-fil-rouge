import json

from channels.generic.websocket import AsyncWebsocketConsumer


class BoardConsumer(AsyncWebsocketConsumer):
    """Diffuse les changements du tableau d'un projet aux clients connectés."""

    async def connect(self):
        self.project_id = self.scope["url_route"]["kwargs"]["project_id"]
        self.group = f"board_{self.project_id}"
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group, self.channel_name)

    async def board_update(self, event):
        await self.send(text_data=json.dumps(
            {"task_id": event["task_id"], "status_id": event["status_id"]}
        ))
