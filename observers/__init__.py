from otree.api import *

import random
import itertools
import numpy as np

from threshold_dictator import RandomSelection

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'observers'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 10


class Subsession(BaseSubsession):
    pass

def creating_session(subsession):
    """
    Pairs of original and reported dice from the prolific pilot.
    Must be called from a separate page or in the creating_session
    """
    for p in subsession.get_players():
        p.set_k_values()

class Group(BaseGroup):
    pass


class Player(BasePlayer):

    k_value = models.IntegerField(initial=99)
    ratings = models.FloatField(
        initial=999,
        verbose_name='How cooperative is this person?',
        min=0, max=100,
    )

    q1_failed_attempts = models.IntegerField()
    q2_failed_attempts = models.IntegerField()

    q1 = models.IntegerField(
        choices=[
            [1, f'bla'],
            [2, f'bla'],
            [3, f'bla']
        ],
        verbose_name='What would be the payment for you and the previous participant, if you selected the selfish option on that round?',
        widget=widgets.RadioSelect
    )

    q2 = models.IntegerField(
        choices=[
            [1, f'bla'],
            [2, f'bla'],
            [3, f'bla']
        ],
        verbose_name='What would be the payment for you and the previous participant, if you selected the cooperative option on that round?',
        widget=widgets.RadioSelect
    )

    # def set_k_sequences(player):
    #     """
    #     Return a pair (original_dice, reported_dice) such that
    #     distance = reported_dice - original_dice is *uniform* on {0,1,2,3,4,5}.
    #     Within each distance the specific pair is chosen uniformly.
    #     """
    #     sequence = list(range(0,21))
    #     k_value = random.choice(sequence)
    #     player.k_value = k_value
    #     # print(player.k_value)

    def set_k_values(player):
        """
        Return a pair (original_dice, reported_dice) such that
        distance = reported_dice - original_dice is *uniform* on {0,1,2,3,4,5}.
        Within each distance the specific pair is chosen uniformly.
        """
        sequence = list(range(0, 21))
        k_value = random.choice(sequence)
        player.k_value = k_value
        # print(player.k_value)

######## FUNCTIONS ##########


########## PAGES #########

class Instructions(Page):
    form_model = 'player'
    form_fields = ['q1', 'q2']

    # @staticmethod
    # def error_message(player: Player, values):
    #     """
    #     records the number of time the page was submitted with an error. which specific error is not recorded.
    #     """
    #     solutions = dict(q1=1, q2=2)
    #
    #     # error_message can return a dict whose keys are field names and whose values are error messages
    #     errors = {}
    #     for question, correct_answer in solutions.items():
    #         if values[question] != correct_answer:
    #             errors[question] = 'This answer is wrong'
    #             # Increment the specific failed attempt counter for the incorrect question
    #             failed_attempt_field = f"{question}_failed_attempts"
    #             if hasattr(player, failed_attempt_field):  # Ensure the field exists
    #                 setattr(player, failed_attempt_field, getattr(player, failed_attempt_field) + 1)
    #     if errors:
    #         return errors
    #     return None

    @staticmethod
    def is_displayed(player: Player):
        if player.round_number == 1:
            return True
        return False


class CooperativenessRatings(Page):
    form_model = 'player'
    form_fields = ['ratings']

    def vars_for_template(player: Player):
        return dict(
            k_value=player.k_value,
            ratings=player.ratings,
        )

class Results(Page):

    @staticmethod
    def is_displayed(player: Player):
        if player.round_number == C.NUM_ROUNDS:
            return True
        return None


class Payment(Page):

    @staticmethod
    def is_displayed(player: Player):
        if player.round_number == C.NUM_ROUNDS:
            return True
        return None

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
        return None


page_sequence = [Instructions,
                 CooperativenessRatings,
                 # Results,
                 # RandomSelection,
                 Payment,
                 ProlificLink,
                 ]
