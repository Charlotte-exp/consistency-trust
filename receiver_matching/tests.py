from otree.api import Currency as c, currency_range, expect, Bot
from . import *

import random


class PlayerBot(Bot):
    def play_round(self):
        yield PairingWaitPage
        yield ReceiverChoice, dict(choice=random.choice(['Option A', 'Option B']))
        yield ResultsWaitPage
        # yield Results
        # yield Demographics, {"age": '22', "gender": 'Female', "income": '£10.000 - £29.999',
        #                      "education": 'Postgraduate degree', "ethnicity": 'White'}
        yield Comprehension, dict(q1=random.choice(['1', '2']),
                                  q2=random.choice(['1', '2']),
                                  q3=random.choice(['1', '2']))
        yield CommentBox, {"comment_box": 'n/a'}
        yield Payment
        yield ProlificLink

