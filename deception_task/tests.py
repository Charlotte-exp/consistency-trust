from otree.api import Currency as c, currency_range, expect, Bot
from . import *

import random


class PlayerBot(Bot):
    def play_round(self):
        yield SenderMessage, dict(message=random.choice(['Box A', 'Box B']))
        yield ReceiverChoice, dict(choice=random.choice(['Box A', 'Box B']))
        yield Results
        yield Comprehension
        # yield StrategyBox, {"strategy_box": 'n/a'}
        # yield CommentBox, {"comment_box": 'n/a'}
        yield Payment
        yield ProlificLink
