import json
from channels.generic.websocket import AsyncWebsocketConsumer

class CuotasConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'broadcast_cuotas'

        # Unión al grupo de Redis de forma asíncrona nativa
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
        print("[WebSocket] Túnel asíncrono establecido y escuchando de forma permanente.")

    async def disconnect(self, close_code):
        # Abandono del grupo al cerrar la pestaña
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        print(f"[WebSocket] Conexión liberada limpiamente por el cliente. Código: {close_code}")

    async def enviar_actualizacion_cuota(self, event):
        """
        Recibe el pulso de Redis enviado por el Signal y lo inyecta
        al navegador instantáneamente sin cerrar el socket.
        """
        try:
            payload = event['payload']
            await self.send(text_data=json.dumps(payload))
        except Exception as e:
            print(f"[WebSocket Error] Fallo al transmitir JSON: {e}")