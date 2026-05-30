import json
from channels.generic.websocket import AsyncWebsocketConsumer


class CuotasConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.group_name = 'broadcast_cuotas'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def enviar_actualizacion_cuota(self, event):
        try:
            payload = event['payload']
            await self.send(text_data=json.dumps(payload))
        except Exception:
            pass
