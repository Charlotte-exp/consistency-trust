from otree.api import *

import random
import itertools
import numpy as np

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
    proba_implementation = models.IntegerField(initial=0)
    conversion_rate = models.FloatField(initial=0)

    decision = models.CurrencyField(
        choices=[
            [0, f'Selfish option'],  # defect
            [1, f'Cooperative option'],  # cooperate
        ],
        verbose_name='Your decision:',
        widget=widgets.RadioSelect
    )

    q1 = models.IntegerField(
        choices=[
            [1, 'I get 100 points, the previous participant gets 0 points'],
            [2, 'I get fewer than 100 points, the previous participant gets more than 0 points'],
            [3, 'Both I and the previous participant get 100 points']
        ],
        verbose_name='How will your choice to “Defect” affect both you and the previous participant?',
        widget=widgets.RadioSelect
    )

    q2 = models.IntegerField(
        choices=[
            [1, 'It will always be the same'],
            [2, 'The points will vary each round'],
            [3, 'The points are fixed at 50 points each'],
        ],
        verbose_name='If you choose to “Cooperate,” '
                     'what will determine how many points you and the previous participant receive?',
        widget=widgets.RadioSelect
    )

    q3 = models.IntegerField(
        choices=[
            [1, f'Points are always worth 5 cents each'],
            [2, 'Points are converted to cents at a random rate at the end of the study'],
            [3, f'Points are converted to cents at a rate that changes each round, between 1 and 10 cents per point'],
        ],
        verbose_name=f'Will all rounds count toward the final bonus payment?',
        widget=widgets.RadioSelect
    )

    q4 = models.IntegerField(
        choices=[
            [1, 'No, only one round will be randomly selected to count'],
            [2, f'Yes, all rounds will count'],
            [3, f'Only the last round will count']
        ],
        verbose_name=f'How will points be converted to cents?',
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
                # print('cost', player.cost, 'benefit', player.benefit)
                return player.cost, player.benefit

    def get_proba(player):
        probabilities = list(range(10, 91, 10))
        proba = random.choice(probabilities)
        player.proba_implementation = proba
        print('proba:', player.proba_implementation)
        return player.proba_implementation

    def get_conversion(player):
        conversion_rates = np.around(np.arange(0.1, 1.1, 0.1), 1).tolist()  # np for float and need to round up
        conversion = random.choice(conversion_rates)
        player.conversion_rate = conversion
        print('conversion:', player.conversion_rate)
        return player.conversion_rate


######## PAGES ##########

class Introduction(Page):
    form_model = 'player'
    form_fields = ['q1', 'q2', 'q3', 'q4']


class Decision(Page):
    form_model = 'player'
    form_fields = ['decision']


    def vars_for_template(player: Player):
        return dict(
            call_benefits=player.get_benefits(), # has to be on another page or they can change on refresh...
            call_probability=player.get_proba(),
            call_conversion=player.get_conversion(),
            proba=player.proba_implementation,
            conversion=player.conversion_rate,
            cost=player.cost,
            benefit=player.benefit,
        )


page_sequence = [Introduction,
                 Decision,
                 # ResultsWaitPage,
                 # Results
                 ]
