from otree.api import Currency as c, currency_range, expect, Bot
from . import *

import random


class PlayerBot(Bot):
    def play_round(self):
        if self.participant.role == "Sender":
            yield SenderMessage, dict(message=random.choice(['Option A', 'Option B']))
        else:
            yield ReceiverChoice, dict(choice=random.choice(['Option A', 'Option B']))
        yield Results
        yield Comprehension, dict(q1=random.choice(['1', '2']),
                                  q2=random.choice(['1', '2']),
                                  q3=random.choice(['1', '2']))
        # yield StrategyBox, {"strategy_box": 'n/a'}
        # yield CommentBox, {"comment_box": 'n/a'}
        yield Payment
        yield ProlificLink
