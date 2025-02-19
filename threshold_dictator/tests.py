from otree.api import Currency as c, currency_range, expect, Bot
from . import *

import random


class PlayerBot(Bot):
    def play_round(self):
        if self.participant.balanced_order == 'treatment-control':
            if self.round_number == 1:
                yield Consent
                yield Introduction
                yield Instructions, dict(q1=1, q2=2)
            if self.round_number <= C.half_rounds:
                yield SetStakes
                yield Decision, dict(decision=random.choice([0, 1]))
            if self.round_number == C.half_rounds:
                yield Results
            if self.round_number == C.half_rounds + 1:
                yield Instructions, dict(q5=1, q6=2)
            if C.half_rounds < self.round_number <= C.NUM_ROUNDS:
                yield SetStakes
                yield Decision, dict(decision_control=random.choice([0, 1]))
            if self.round_number == C.NUM_ROUNDS:
                yield Results
                yield RandomSelection, dict(random_selection='randomise')
                yield End
                yield CommentBox, dict(comment_box='blablabla', survey_box='bliblibli')
                yield Payment
        elif self.participant.balanced_order == 'control-treatment':
            if self.round_number == 1:
                yield Consent
                yield Introduction
                yield Instructions, dict(q5=1, q6=2)
            if self.round_number <= C.half_rounds:
                yield SetStakes
                yield Decision, dict(decision_control=random.choice([0, 1]))
            if self.round_number == C.half_rounds:
                yield Results
            if self.round_number == C.half_rounds+1:
                yield Instructions, dict(q1=1, q2=2)
            if C.half_rounds < self.round_number <= C.NUM_ROUNDS:
                yield SetStakes
                yield Decision, dict(decision=random.choice([0, 1]))
            if self.round_number == C.NUM_ROUNDS:
                yield Results
                yield RandomSelection, dict(random_selection='randomise')
                yield End
                yield CommentBox, dict(comment_box='blablabla', survey_box='bliblibli')
                yield Payment


