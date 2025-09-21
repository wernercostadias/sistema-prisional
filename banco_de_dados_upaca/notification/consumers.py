# notification/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'notifications_group'

        # Entrar no grupo para receber mensagens
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()  # aceita a conexão WebSocket

    async def disconnect(self, close_code):
        # Sair do grupo ao desconectar
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Receber mensagem do grupo
    async def send_notification(self, event):
        message = event['message']

        # Enviar mensagem para o cliente WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
