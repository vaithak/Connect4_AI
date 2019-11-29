from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json
import uuid
from .models import Game
from .helpers import ai_move, game_finished, verify_board_state_difference

class GameConsumer(WebsocketConsumer):
    # verify state send by user
    def verify_user_state(self, state):
        if len(state)!=42:
            return False

        for i in range(len(state)):
            if (state[i]!='0') and (state[i]!='r') and (state[i]!='y'):
                return False

        # extracting previous board state
        mark=0
        for i in range(5):
            if self.game.game_state[i]=='#':
                mark=i
                break

        length = int(self.game.game_state[1:mark])
        mark = mark + 1 + length
        prev_board_state = self.game.game_state[mark:mark+42]

        return verify_board_state_difference(self.game.game_state[0], prev_board_state, state)

    # compress frontend state into backend form
    def compress_state(self, user_state, sender):
        player = self.game.creator
        
        if sender == self.game.creator:
            player = self.game.opponent_name

        win_status = "f"
        if game_finished(user_state):
            win_status = "t"

        if self.game.game_state[0] == 'r':
            return "y" + str(len(player)) + "#" + player + user_state + win_status
        else:
            return "r" + str(len(player)) + "#" + player + user_state + win_status

    def verify_sender(self, sender):
        if (sender != self.game.creator) and (sender != self.game.opponent_name):
            return False

        supposed_player = self.get_new_player(self.game.game_state)
        if len(supposed_player)!=0 and sender != supposed_player:
            return False

        return True

    # get new player frpm compressed state
    def get_new_player(self, compressed_state):
        mark=0
        for i in range(5):
            if compressed_state[i]=='#':
                mark=i
                break

        length = int(compressed_state[1:mark])
        return compressed_state[mark+1:mark+1+length]

    # get prev player from compressed state
    def get_prev_player(self, compressed_state):
        new_player = self.get_new_player(compressed_state)
        if new_player == self.game.creator:
            return self.game.opponent_name
        else:
            return self.game.creator

    # fetch state from DB
    def fetch_state(self, data, sender):
        mark=0
        for i in range(5):
            if self.game.game_state[i]=='#':
                mark=i
                break

        length = int(self.game.game_state[1:mark])
        mark = mark + 1 + length
        board_state = self.game.game_state[mark:mark+42]

        content = {
            'command': 'curr_state',
            'state': self.state_to_json(self.game.game_state, board_state, 0, 0)
        }
        self.send_state_message_to_websocket(content)
        return True
    
    def reset_state(self, data, sender):
        self.game.game_state = "r" + str(len(self.scope["session"]["username"])) + "#" + self.scope["session"]["username"] + "000000000000000000000000000000000000000000f"
        self.game.save()

        content = {
            'command': 'reset_state',
            'state': self.state_to_json(self.game.game_state, "000000000000000000000000000000000000000000", 0, 0)
        }

        return self.send_state_message_to_group(content)

    # save and send new state
    def new_state(self, data, sender):
        if ('state' not in data) or (len(data['state']) == 0) or ('index' not in data) or ('index2' not in data):
            return False

        if not self.verify_user_state(data['state']):
            return False

        if not self.verify_sender(sender):
            return False

        compressed_state = self.compress_state(data['state'], sender)
        self.game.game_state = compressed_state
        self.game.save()

        content = {
            'command': 'new_state',
            'state': self.state_to_json(compressed_state, data['state'], data['index'], data['index2'])
        }
        self.send_state_message_to_group(content)
        return True
    
    commands = {
        'fetch_state': fetch_state,   
        'new_state': new_state,   
        'reset_state': reset_state,
    }

    def state_to_json(self, compressed_state, normal_state, index, index2):
        return {
            'index': index,
            'index2': index2,
            'active': compressed_state[0],
            'is_finished': (compressed_state[-1] == 't'),
            'state': normal_state,
            'prev_player': self.get_prev_player(compressed_state),
            'new_player': self.get_new_player(compressed_state),
        }

    def connect(self):
        try:
            self.room_group_name = 'game_%s' % self.scope['url_route']['kwargs']['game_id']
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

            if (len(self.game.opponent_name) == 0) and (self.game.creator != self.scope["session"]["username"]):
                self.game.opponent_name = self.scope["session"]["username"]
                if self.game.game_state[1] == "0":
                    self.game.game_state = self.game.game_state[0] + str(len(self.game.opponent_name)) + "#" + self.game.opponent_name + self.game.game_state[3:]
                    self.game.save()
                    self.fetch_state(None, self.scope["session"]["username"])
                else:
                    self.game.save()
        except:
            print("closing")
            self.close()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        if ("command" not in text_data_json) or (text_data_json['command'] not in self.commands):
            return 
        self.game = Game.objects.get(pk=self.game_id)
        if(self.commands[text_data_json['command']](self, text_data_json, self.scope["session"]["username"])):
            next_move_player = self.get_new_player(self.game.game_state)
            if (len(next_move_player)!=0) and (next_move_player == "ai") and ('state' in text_data_json):
                new_state_data = ai_move(self.game.game_state[0], text_data_json['state'])
                self.new_state(new_state_data, "ai")

    # Send message to room group
    def send_state_message_to_group(self, message):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'state_message',
                'message': message
            }
        )

    def send_state_message_to_websocket(self, message):
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))

    # Receive message from room group
    def state_message(self, event):
        message = event['message']
        self.send_state_message_to_websocket(message)
