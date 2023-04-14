from otree.api import Currency as c, currency_range, expect, Bot
from . import *

import random


class PlayerBot(Bot):
    def play_round(self):
        if self.participant.role == "Sender":
            if self.round_number <= C.NUM_ROUNDS:
                yield StakesPage
                yield SenderMessage, dict(message=random.choice(['Option A', 'Option B']),
                                          better4you='Option B', better4receiver='Option A',
                                          what_receiver_knows='Nothing')
                # yield Results
            if self.round_number == C.NUM_ROUNDS:
                yield RandomSelection, dict(random_selection='randomise')
                yield End

