from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json
from connect4_game.models import Game
import uuid
from .models import Message

class ChatConsumer(WebsocketConsumer):
    # fetch messages from DB
    def fetch_messages(self, data):
        messages = Message.last_30_messages(self.game_id)
        content = {
            'command': 'messages',
            'messages': self.messages_to_json(messages)
        }
        self.send_message_to_websocket(content)

    def new_message(self, data):
        if ('message' not in data) or (len(data['message']) == 0):
            return

        curr_game = Game.objects.filter(game_id=self.game_id)[0]
        message = Message.objects.create(
            game=curr_game,
            author=self.scope["session"]["username"], 
            content=data['message']
        )
        content = {
            'command': 'new_message',
            'message': self.message_to_json(message)
        }
        return self.send_chat_message_to_group(content)
    
    commands = {
        'fetch_messages': fetch_messages,   # fetching previous messages
        'new_message': new_message          # creating a new message
    }

    def messages_to_json(self, messages):
        result = []
        for message in messages:
            result.append(self.message_to_json(message))
        return result

    def message_to_json(self, message):
        return {
            'game_id': str(message.game.game_id),
            'author': message.author,
            'content': message.content,
            'timestamp': str(message.timestamp)
        }

    def connect(self):
        try:
            self.room_group_name = 'chat_%s' % self.scope['url_route']['kwargs']['game_id']
            # Join room group
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name,
                self.channel_name
            )

            if "username" not in self.scope["session"]:
                self.close()

            self.game_id = uuid.UUID(self.scope['url_route']['kwargs']['game_id'])
            self.game = Game.objects.get(pk=self.game_id)

            self.accept()

            notif_msg = self.scope["session"]["username"] + " has entered the room"
            self.send_notification_to_group(notif_msg)
        except:
            self.close()

    def disconnect(self, close_code):
        # Leave room group
        notif_msg = self.scope["session"]["username"] + " has exited the room"
        self.send_notification_to_group(notif_msg)

        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        if ("command" not in text_data_json) or (text_data_json['command'] not in self.commands):
            pass
        else:
            self.commands[text_data_json['command']](self, text_data_json)

    # Send message to room group
    def send_chat_message_to_group(self, message):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Send notification to group
    def send_notification_to_group(self, message):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'notifcation',
                'message': message
            }
        )


    def send_message_to_websocket(self, message):
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))

    def send_notification_to_websocket(self, message):
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'notification': message
        }))

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']
        self.send_message_to_websocket(message)

    # Receive notification from room group
    def notifcation(self, event):
        message = event['message']
        self.send_notification_to_websocket(message)