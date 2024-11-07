from otree.api import *

import random
import itertools

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'threshold_dictator'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 6

    endowment = cu(10)
    conversion_rate = 1
    proba_implementation = 0.1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    receiver_payoff = models.CurrencyField(initial=cu(0))

    cost = models.CurrencyField(initial=cu(0))
    benefit = models.CurrencyField(initial=cu(0))

    decision = models.CurrencyField(
        choices=[
            [0, f'Selfish option'],  # defect
            [1, f'Cooperative option'],  # cooperate
        ],
        verbose_name='Your decision:',
        widget=widgets.RadioSelect
    )

    def get_benefits(player):
        numbers = list(range(1, 9))
        while True:
            # sample two numbers with replacement (for without use random.sample(numbers, 2)
            number_1, number_2 = random.choices(numbers, k=2)
            # check if sampled numbers satisfy the condition
            if number_1 + number_2 >= 10 and number_1 <= number_2:
                player.cost = number_1
                player.benefit = number_2
                print('cost', player.cost, 'benefit', player.benefit)
                return player.cost, player.benefit



######## PAGES ##########

class Decision(Page):
    form_model = 'player'
    form_fields = ['decision']


    def vars_for_template(player: Player):
        return dict(
            call_benefits=player.get_benefits(), # has to be on another page or they can change on refresh...
            proba=int(C.proba_implementation * 100),  # remove decimal from display
            conversion=C.conversion_rate,
            cost=player.cost,
            benefit=player.benefit,
        )


page_sequence = [Decision,
                 # ResultsWaitPage,
                 # Results
                 ]
