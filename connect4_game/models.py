from django.db import models
import uuid

class Game(models.Model):
    game_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    creator = models.CharField(max_length=20)
    game_state = models.CharField(max_length=100)
    against_ai = models.BooleanField()
    opponent_name = models.CharField(max_length=20, default="")

    def __str__(self):
        return "Creator: {}, Game Id: {}, State: {}, Opponent: {}".format(self.creator, self.game_id, self.game_state, self.opponent_name)