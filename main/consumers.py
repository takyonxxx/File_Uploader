import json
from datetime import datetime

from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from django.conf import settings
from jwt import decode as jwt_decode

from user.models import User


class BaseWebsocketConsumer(AsyncWebsocketConsumer):
    user = None

    async def get_token(self):
        query_string = self.scope['query_string'].decode()
        token = query_string.split('=')[1]
        return token

    async def get_user(self):
        token = await self.get_token()
        if token is not None:
            decoded_data = jwt_decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = decoded_data.get('user_id')
            if user_id is None:
                raise Exception('User not found!')
            user = User.objects.filter(id=user_id).first()
            return user
        else:
            raise Exception('Token not provided!')

    @property
    async def kwargs(self):
        return self.scope['url_route']['kwargs']


class NotificationConsumer(BaseWebsocketConsumer):
    room = 'notifications'

    async def connect(self):
        self.user = await self.get_user()

        await self.channel_layer.group_add(
            self.room,
            self.channel_name
        )

        await self.accept()

    # Function to disconnet the Socket
    async def disconnect(self, close_code):
        await self.close()
        # pass

    # Custom Notify Function which can be called from Views or api to send message to the frontend
    async def notify(self, event):
        await self.send(text_data=json.dumps(event))

    @staticmethod
    async def send_async_message(data):
        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            'notifications',
            {
                'type': 'notify',
                'time': str(datetime.now()),
                **data
            },
        )

    @staticmethod
    def send_message(data):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'notifications',
            {
                'type': 'notify',
                'time': str(datetime.now()),
                **data
            },
        )
