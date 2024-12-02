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
    NUM_ROUNDS = 12

    endowment = 100  # maximum range
    conversion_rate = 1
    proba_implementation = 0.1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    receiver_payoff = models.CurrencyField(initial=cu(0))

    cost = models.IntegerField(initial=0)
    benefit = models.IntegerField(initial=0)
    proba_implementation = models.IntegerField(initial=0)
    conversion_rate = models.FloatField(initial=0)

    randomly_selected_round = models.IntegerField(initial=0)
    randomly_selected_decision = models.IntegerField(initial=0)
    randomly_selected_cost = models.IntegerField(initial=0)
    randomly_selected_benefit = models.IntegerField(initial=0)
    randomly_selected_proba_implementation = models.IntegerField(initial=0)
    randomly_selected_conversion_rate = models.FloatField(initial=0)

    decision = models.IntegerField(
        initial=0,
        choices=[
            [0, f'Selfish option'],  # defect
            [1, f'Cooperative option'],  # cooperate
        ],
        verbose_name='Your choice:',
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

    random_selection = models.StringField(
        initial='',
        choices=['randomise', 'whatever'],
    )

    comment_box = models.LongStringField(
        verbose_name=''
    )

    strategy_box = models.LongStringField(
        verbose_name=''
    )

    def get_benefits(player):
        """
        This function returns two numbers between 1 and 9 on each round to become the benefit and the cost.
        In addition, the sum of the two numbers is always smaller than 100
        and the first number (the cost) is smaller than the second (the benefit)
        """
        numbers = list(range(1, 99))
        while True:
            # sample two numbers with replacement (for without use random.sample(numbers, 2)
            number_1, number_2 = random.choices(numbers, k=2)
            # check if sampled numbers satisfy the condition
            if number_1 + number_2 >= C.endowment and number_1 <= number_2:
                player.cost = number_1
                player.benefit = number_2
                # print('cost', player.cost, 'benefit', player.benefit)
                return player.cost, player.benefit

    def get_proba(player):
        """
        This function creates a list of possible probabilites of implementation from 1 t0 10 in increments of 1.
        it then selects on of those every time it is called
        """
        probabilities = list(range(1, 11, 1))
        proba = random.choice(probabilities)
        player.proba_implementation = proba
        #print('proba:', player.proba_implementation)
        return player.proba_implementation

    def get_conversion(player):
        """
        This function creates a list of possible conversion rates from 0.1 to 0.9 in increments of 0.1
        it then selects on of those every time it is called
        """
        conversion_rates = np.around(np.arange(0.1, 1.1, 0.1), 1).tolist()  # np for float and need to round up
        conversion = random.choice(conversion_rates)
        player.conversion_rate = conversion
        #print('conversion:', player.conversion_rate)
        return player.conversion_rate


######## FUNCTIONS ##########

def random_payment(player: Player):
    """
    This function selects one round among all with equal probability.
    It records the value of each variable on this round as new random_variable fields
    """
    randomly_selected_round = random.randint(1, C.NUM_ROUNDS)
    me = player.in_round(randomly_selected_round)
    player.randomly_selected_round = randomly_selected_round
    player.participant.randomly_selected_round = randomly_selected_round

    attributes = ['decision', 'cost', 'benefit', 'proba_implementation', 'conversion_rate']
    for attr in attributes:
        value = getattr(me, attr)
        setattr(player, f'randomly_selected_{attr}', value)
        setattr(player.participant, f'randomly_selected_{attr}', value)
    # print('round is', randomly_selected_round)
    # print('stake is', randomly_selected_stake)
    # print('message is', randomly_selected_message)


######## PAGES ##########

class Consent(Page):

    @staticmethod
    def is_displayed(player: Player):
        if player.round_number == 1:
            return True
        else:
            return False

    def vars_for_template(player: Player):
        return {
            'participation_fee': player.session.config['participation_fee'],
        }


class Introduction(Page):
    form_model = 'player'
    form_fields = ['q1', 'q2', 'q3', 'q4']

    @staticmethod
    def is_displayed(player: Player):
        if player.round_number == 1:
            return True
        else:
            return False


class SetStakes(Page):

    timeout_seconds = 1  # instant timeout

    def vars_for_template(player: Player):
        participant = player.participant
        return dict(
            round_number=player.round_number,

            call_benefits=player.get_benefits(),
            call_probability=player.get_proba(),
            call_conversion=player.get_conversion(),
        )


class Decision(Page):
    form_model = 'player'
    form_fields = ['decision']


    def vars_for_template(player: Player):
        return dict(
            decision=player.decision,
            proba=player.proba_implementation,
            conversion=player.conversion_rate,
            cost=player.cost,
            benefit=player.benefit,
        )


class RandomSelection(Page):
    form_model = 'player'
    form_fields = ['random_selection']

    @staticmethod
    def is_displayed(player: Player):
        if player.round_number == C.NUM_ROUNDS:
            return True

    def vars_for_template(player: Player):
        return dict(
            player_in_all_rounds=player.in_all_rounds(),
            total_payoff=sum([p.payoff for p in player.in_all_rounds()]),

            call_payment=random_payment(player),
            #call_payoff=get_payoff(player),
        )


class End(Page):

    @staticmethod
    def is_displayed(player: Player):
        if player.round_number == C.NUM_ROUNDS:
            return True

    def vars_for_template(player: Player):
        return dict(
                player_in_all_rounds=player.in_all_rounds(),
                total_payoff=sum([p.payoff for p in player.in_all_rounds()]),

                random_round=player.randomly_selected_round,
                random_decision=player.randomly_selected_decision,
                random_cost=player.randomly_selected_cost,
                random_benefit=player.randomly_selected_benefit,
                random_proba_implementation=player.randomly_selected_proba_implementation,
                random_conversion_rate=player.randomly_selected_conversion_rate,
            )


class Payment(Page):

    @staticmethod
    def is_displayed(player: Player):
        if player.round_number == C.NUM_ROUNDS:
            return True

    def vars_for_template(player: Player):
        participant = player.participant
        session = player.session
        return dict(
            bonus=player.payoff.to_real_world_currency(session),
            participation_fee=session.config['participation_fee'],
            final_payment=player.payoff.to_real_world_currency(session) + session.config['participation_fee'],
        )


class ProlificLink(Page):
    """
    This page redirects pp to prolific automatically with a javascript (don't forget to put paste the correct link!).
    There is a short text and the link in case it is not automatic.
    """
    @staticmethod
    def is_displayed(player: Player):
        if player.round_number == C.NUM_ROUNDS:
            return True


page_sequence = [Consent,
                 Introduction,
                 SetStakes,
                 Decision,
                 # ResultsWaitPage,
                 # Results
                 RandomSelection,
                 End,
                 Payment,
                 ProlificLink,
                 ]
