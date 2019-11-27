from django.db import models
from connect4_game.models import Game

class Message(models.Model):
    game = models.ForeignKey('connect4_game.Game', related_name='game_messages', on_delete=models.CASCADE)
    author = models.CharField(max_length=20)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Author: {}, Content: {}, Game_id: {}".format(self.author, self.content, self.game_id)

    def last_30_messages(game_id):
        curr_game = Game.objects.get(pk=game_id)
        return Message.objects.filter(game = curr_game).order_by('timestamp').all()[:30]