from otree.api import Currency as c, currency_range, expect, Bot
from . import *


class PlayerBot(Bot):
    def play_round(self):
        yield Welcome
        if self.participant.title == 'dictator':
            yield InstruDictator, dict(decision_high=1)
        else:
            if self.participant.title == 'receiver':
                yield InstruReceiver
