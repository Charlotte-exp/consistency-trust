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
    NUM_ROUNDS = 5

    endowment = cu(2)  # maximum range
    safe_option = endowment
    #conversion_rate = 1
    #proba_implementation = 0.1


class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass


class Player(BasePlayer):

    treatment = models.StringField(initial='')
    num_failed_attempts = models.IntegerField(initial=0)

    cost = models.CurrencyField(initial=0)
    benefit = models.CurrencyField(initial=0)
    proba_gamble = models.IntegerField(initial=0)
    proba_sure = models.IntegerField(initial=0)
    #proba_implementation = models.IntegerField(initial=0)
    #conversion_rate = models.FloatField(initial=0)

    randomly_selected_round = models.IntegerField(initial=0)
    randomly_selected_decision = models.IntegerField(initial=0)
    randomly_selected_decision_control = models.IntegerField(initial=0)
    randomly_selected_cost = models.CurrencyField(initial=0)
    randomly_selected_benefit = models.CurrencyField(initial=0)
    randomly_selected_proba_gamble = models.IntegerField(initial=0)
    #randomly_selected_proba_implementation = models.IntegerField(initial=0)
    #randomly_selected_conversion_rate = models.FloatField(initial=0)

    decision = models.IntegerField(
        initial=0,
        choices=[
            [0, f'Selfish option'],  # defect
            [1, f'Cooperative option'],  # cooperate
        ],
        verbose_name='Your choice:',
        widget=widgets.RadioSelect
    )

    decision_control = models.IntegerField(
        initial=0,
        choices=[
            [0, f'Risky option'],  # defect
            [1, f'Safe option'],  # cooperate
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
        verbose_name='How will your choice of the “Selfish” option affect both you and the previous participant?',
        widget=widgets.RadioSelect
    )

    q2 = models.IntegerField(
        choices=[
            [1, 'It will always be the same'],
            [2, 'The points will vary each round'],
            [3, 'The points are fixed at 50 points each'],
        ],
        verbose_name='If you choose the “Cooperate” option, '
                     'what will determine how many points you and the previous participant receive?',
        widget=widgets.RadioSelect
    )

    q3 = models.IntegerField(
        choices=[
            [1, f'Points are always worth 5 cents each'],
            [2, 'Points are converted to cents at a random rate at the end of the study'],
            [3, f'Points are converted to cents at a rate that changes each round, between 1 and 10 cents per point'],
        ],
        verbose_name=f'How will points be converted to cents?',
        widget=widgets.RadioSelect
    )

    q4 = models.IntegerField(
        choices=[
            [1, 'No, only one round will be randomly selected to count'],
            [2, f'Yes, all rounds will count'],
            [3, f'Only the last round will count']
        ],
        verbose_name=f'Will all rounds count toward the final bonus payment?',
        widget=widgets.RadioSelect
    )

    q5 = models.IntegerField(
        choices=[
            [1, 'If that round is selected, 100 cents will be added to your bonus.'],
            [2, f'If that round is selected, your bonus may go up by more than 100 cents. '
                f'How much more and with what probability will vary by round.'],
        ],
        verbose_name=f'How will your choice of “sure thing” affect your bonus?',
        widget=widgets.RadioSelect
    )

    q6 = models.IntegerField(
        choices=[
            [1, 'If that round is selected, 100 cents will be added to your bonus.'],
            [2, f'If that round is selected, your bonus may go up by more than 100 cents. '
                f'How much more and with what probability will vary by round.'],
        ],
        verbose_name=f'If you choose the “risky option,” '
                     f'what will determine how many points you and the previous participant receive?',
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
        numbers = [x / 10 for x in range(1, int(C.endowment * 10))]  # list from 0.1 to 1.9
        while True:
            # sample two numbers with replacement (for without use random.sample(numbers, 2)
            number_1, number_2 = random.choices(numbers, k=2)
            # check if sampled numbers satisfy the condition
            if number_1 + number_2 >= C.endowment and number_1 <= number_2:
                player.cost = number_1
                player.benefit = number_2
                # print('cost', player.cost, 'benefit', player.benefit)
                return player.cost, player.benefit

    def get_gambles(player):
        """
        """
        numbers = [x / 10 for x in range(1, int((C.endowment*2) * 10))]  # list from 0.1 to 3.9
        probabilities = list(range(10, 100, 10))  # list from 10 to 100 in increments of 10
        while True:
            number_1 = random.choice(numbers)
            proba_1 = random.choice(probabilities)
            proba_2 = 100 - proba_1  # Calculate the complement to sum to 1
            # Check if both numbers are within the range [0.01, 0.99]
            if number_1 * (proba_1/100) >= C.endowment: # gamble's EV must be higher than sure thing
                player.benefit = number_1
                player.proba_gamble = proba_1
                player.proba_sure = proba_2
                #print('EV', (player.proba_gamble*2)*player.benefit)
                return player.proba_gamble, player.proba_sure


    # def get_proba(player):
    #         """
    #         This function creates a list of possible probabilites of implementation from 1 t0 10 in increments of 1.
    #         it then selects on of those every time it is called
    #         """
    #         probabilities = list(range(1, 11, 1))
    #         proba = random.choice(probabilities)
    #         player.proba_implementation = proba
    #         #print('proba:', player.proba_implementation)
    #         return player.proba_implementation
    #
    # def get_conversion(player):
    #     """
    #     This function creates a list of possible conversion rates from 0.1 to 0.9 in increments of 0.1
    #     it then selects on of those every time it is called
    #     """
    #     conversion_rates = np.around(np.arange(0.1, 1.1, 0.1), 1).tolist()  # np for float and need to round up
    #     conversion = random.choice(conversion_rates)
    #     player.conversion_rate = conversion
    #     #print('conversion:', player.conversion_rate)
    #     return player.conversion_rate


######## FUNCTIONS ##########

def creating_session(subsession):
    """
    We use itertools to assign treatment regularly to make sure there is a somewhat equal amount of each in the
    session but also that is it equally distributed in the sample.
    It simply cycles through the list of treatments (high & low) and that's saved in the participant vars.
    """

    treatments = itertools.cycle(['treatment', 'control'])
    for p in subsession.get_players():
        p.treatment = next(treatments)
        p.participant.condition = p.treatment
        # print('condition is', p.condition)
        # print('vars condition is', p.participant.condition)


def random_payment(player: Player):
    """
    This function selects one round among all with equal probability.
    It records the value of each variable on this round as new random_variable fields
    """
    randomly_selected_round = random.randint(1, C.NUM_ROUNDS)
    me = player.in_round(randomly_selected_round)
    player.randomly_selected_round = randomly_selected_round
    player.participant.randomly_selected_round = randomly_selected_round

    attributes = ['decision', 'decision_control', 'cost', 'benefit', 'proba_gamble',
                  #'proba_implementation', 'conversion_rate'
                  ]
    for attr in attributes:
        value = getattr(me, attr)
        setattr(player, f'randomly_selected_{attr}', value)
        setattr(player.participant, f'randomly_selected_{attr}', value)
    # print('round is', randomly_selected_round)


def gamble(player: Player):
    if player.randomly_selected_decision_control == 0: # if chose the risky choice AKA the gamble
        if player.randomly_selected_proba_gamble/100 >= random.random():
            print('you won!')
            control_bonus = player.randomly_selected_benefit
            player.payoff = control_bonus
            return control_bonus
        else:
            print('you lost!')
            control_bonus = 0
            player.payoff = control_bonus
            return control_bonus
    else:
        print('you are safe!')
        control_bonus = C.safe_option
        player.payoff = control_bonus
        return control_bonus


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

    def get_form_fields(player:Player):
        if player.treatment == 'treatment':
            return ['q1', 'q2', 'q4']
        else:
            return ['q5', 'q6']

    @staticmethod
    def error_message(player: Player, values):
        """
        records the number of time the page was submitted with an error. which specific error is not recorded.
        """
        if player.treatment == 'treatment':
            solutions = dict(q1=1, q2=2, q4=1)
        else:
            solutions = dict(q5=1, q6=2)
        # error_message can return a dict whose keys are field names and whose values are error messages
        errors = {f: 'This answer is wrong' for f in solutions if values[f] != solutions[f]}
        # print('errors is', errors)
        if errors:
            player.num_failed_attempts += 1
            return errors

    @staticmethod
    def is_displayed(player: Player):
        if player.round_number == 1:
            return True
        else:
            return False

    def vars_for_template(player: Player):
        return dict(
            round_number=player.round_number,
            treatment=player.treatment,

            call_benefits=player.get_benefits(),
            # call_probability=player.get_proba(),
            # call_conversion=player.get_conversion(),
        )


class SetStakes(Page):

    timeout_seconds = 1  # instant timeout

    def vars_for_template(player: Player):
        if player.treatment == 'treatment':
            return dict(
                round_number=player.round_number,

                call_benefits=player.get_benefits(),
                # call_probability=player.get_proba(),
                # call_conversion=player.get_conversion(),
            )
        else:
            return dict(
                round_number=player.round_number,

                call_likelihood=player. get_gambles(),
                # call_probability=player.get_proba(),
                # call_conversion=player.get_conversion(),
            )


class Decision(Page):
    form_model = 'player'

    def get_form_fields(player:Player):
        if player.treatment == 'treatment':
            return ['decision']
        else:
            return ['decision_control']

    def vars_for_template(player: Player):
        if player.treatment == 'treatment':
            return dict(
                decision=player.decision,
                # proba=player.proba_implementation,
                # conversion=player.conversion_rate,
                cost=player.cost,
                benefit=player.benefit,
            )
        else:
            return dict(
                decision_control=player.decision_control,
                # proba=player.proba_implementation,
                # conversion=player.conversion_rate,
                cost=player.cost,
                benefit=player.benefit,
                proba_gamble=player.proba_gamble,
                proba_sure=player.proba_sure,
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
            call_gamble=gamble(player),
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
                payoff=player.payoff,  # for control

                random_round=player.randomly_selected_round,
                random_decision=player.randomly_selected_decision,
                random_decision_control=player.randomly_selected_decision_control,
                random_cost=player.randomly_selected_cost,
                random_benefit=player.randomly_selected_benefit,
                random_bonus=player.randomly_selected_benefit,
                #random_proba_implementation=player.randomly_selected_proba_implementation,
                #random_conversion_rate=player.randomly_selected_conversion_rate,
            )


class CommentBox(Page):
    form_model = 'player'
    form_fields = ['comment_box', 'strategy_box']

    @staticmethod
    def is_displayed(player: Player):
        if player.round_number == C.NUM_ROUNDS:
            return True


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
                 CommentBox,
                 Payment,
                 ProlificLink,
                 ]
