from otree.api import Currency as c, currency_range, expect, Bot
from . import *

import random


class PlayerBot(Bot):
    def play_round(self):
        if self.player.round_number == 1:
            # print('BOT DEBUG:', self.player.round_number, self.participant._current_page_name)
            yield Instructions, dict(q1=2, q2=1)
            if self.player.id_in_group % 2 == 1:
                yield FractionOfCooperators, dict(zero_20=1,
                                                  one_20=4,
                                                  two_20=5,
                                                  three_20=5,
                                                  four_20=5,
                                                  five_20=5,
                                                  six_20=5,
                                                  seven_20=5,
                                                  eight_20=5,
                                                  nine_20=5,
                                                  ten_20=5,
                                                  eleven_20=5,
                                                  twelve_20=5,
                                                  thirteen_20=5,
                                                  fourteen_20=5,
                                                  fifteen_20=5,
                                                  sixteen_20=5,
                                                  seventeen_20=5,
                                                  eighteen_20=5,
                                                  nineteen_20=5,
                                                  twenty_20=5,)

        if self.player.round_number < C.NUM_ROUNDS:
            # print('BOT DEBUG:', self.player.round_number, self.participant._current_page_name)
            yield Submission(
                CooperativenessRatings,
                dict(ratings=random.randint(1, 100)),
                check_html=False
            )

        if self.player.round_number == C.NUM_ROUNDS:
            # print('BOT DEBUG:', self.player.round_number, self.participant._current_page_name)
            if self.player.id_in_group % 2 == 0:
                yield FractionOfCooperators, dict(zero_20=1,
                                                  one_20=4,
                                                  two_20=5,
                                                  three_20=5,
                                                  four_20=5,
                                                  five_20=5,
                                                  six_20=5,
                                                  seven_20=5,
                                                  eight_20=5,
                                                  nine_20=5,
                                                  ten_20=5,
                                                  eleven_20=5,
                                                  twelve_20=5,
                                                  thirteen_20=5,
                                                  fourteen_20=5,
                                                  fifteen_20=5,
                                                  sixteen_20=5,
                                                  seventeen_20=5,
                                                  eighteen_20=5,
                                                  nineteen_20=5,
                                                  twenty_20=5,)
            yield RandomSelection, dict(random_selection='randomise')
            if self.player.randomly_selected_round == 11:
                raise AssertionError("randomly_selected_round should not be 11")
            yield End
            yield CommentBox, {"comment_box": 'n/a', 'strategy_box': 'n/a'}
            yield Payment
            yield ProlificLink



