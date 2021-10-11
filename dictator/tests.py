from otree.api import Currency as c, currency_range, expect, Bot
from . import *


class PlayerBot(Bot):
    def play_round(self):
        if self.participant.title == 'dictator':
            yield Offer, dict(decision=1)
        else:
            if self.participant.title == 'receiver':
                yield Receiver

        yield Results

        if self.round_number == 3:
            yield End
