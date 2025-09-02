from otree.api import *

import random
import itertools
import numpy as np

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'observers'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 10

    number_of_trials = 20 # from the actor task
    percent_accurate = 10
    bonus = cu(2)


class Subsession(BaseSubsession):
    pass

def creating_session(subsession):
    """
    create a fixed sequence of 10 elements for each player bu calling generate_k_sequence function.
    Stored in a participant.vars since player field cannot be lists (and I don't need it in the database).
    Because creating_session calls the function every round
    we force it not to do that by setting a value based on round number instead.
    """
    if subsession.round_number == 1:
        for p in subsession.get_players():
            sequence = generate_k_sequence()
            p.participant.vars['sequence'] = sequence
            # set first round value directly
            p.k_value = sequence[0]
    else:
        for p in subsession.get_players():
            # for rounds >1, just pick from participant.vars
            p.k_value = p.participant.vars['sequence'][p.round_number - 1]

class Group(BaseGroup):
    pass


class Player(BasePlayer):

    k_value = models.IntegerField(initial=99)
    ratings = models.IntegerField(
        initial=999,
        verbose_name='How cooperative is this person?',
        min=0, max=100,
    )

    random_selection = models.StringField(
        initial='',
        choices=['randomise', 'whatever'],
    )

    randomly_selected_round = models.IntegerField(initial=0)
    randomly_selected_k_value = models.IntegerField(initial=0)
    randomly_selected_ratings = models.IntegerField(initial=0)

    q1_failed_attempts = models.IntegerField(initial=0)
    q2_failed_attempts = models.IntegerField(initial=0)

    q1 = models.IntegerField(
        choices=[
            [1, f'Only one random choice they made.'],
            [2, f'Only how many times they chose the cooperative option, out of {C.number_of_trials}.'],
            [3, f'How many times they chose the cooperative option, out of {C.number_of_trials}, '
                f'as well as the payoff to themselves and the other player for each of these choices.'],
        ],
        verbose_name='What will you know about other participants when you rate them?',
        widget=widgets.RadioSelect
    )

    q2 = models.IntegerField(
        choices=[
            [1, f'You will receive a {C.bonus} bonus, '
                f'if your rating is the same as the average rating other participants in this study '
                f'who were given the same information gave to that person (±2 units), '
                f'for one randomly selected round of this task.'],
            [2, f'You will receive {C.bonus} bonus, no matter what you write'],
        ],
        verbose_name='How will your bonus for this part be determined?',
        widget=widgets.RadioSelect
    )

    comment_box = models.LongStringField(
        verbose_name=''
    )

    strategy_box = models.LongStringField(
        verbose_name=''
    )

######## FUNCTIONS ##########

def generate_k_sequence():
    """
    Generate a random sequence of 10 numbers.
    One different sequence is assigned to a player at creating_session
    4 values are always included, 6 are random.
    each sequence is shuffled before being returned as the values are assigned to each round in order.
    """
    optional_values = list(range(2, 19))  # 2 to 18
    necessary_values = [0, 1, 19, 20]
    sequence = necessary_values + random.sample(optional_values, 6)
    random.shuffle(sequence)
    return sequence

def random_payment(player: Player):
    """
    This function selects one round among all with equal probability.
    It records the value of each variable on this round as new random_variable fields
    """
    randomly_selected_round = random.randint(1, C.NUM_ROUNDS)
    me = player.in_round(randomly_selected_round)
    player.randomly_selected_round = randomly_selected_round
    #player.participant.randomly_selected_round = randomly_selected_round

    attributes = ['k_value', 'ratings']
    for attr in attributes:
        value = getattr(me, attr)
        setattr(player, f'randomly_selected_{attr}', value)
        #setattr(player.participant, f'randomly_selected_{attr}', value)


########## PAGES #########

class Instructions(Page):
    form_model = 'player'
    form_fields = ['q1', 'q2']

    @staticmethod
    def error_message(player: Player, values):
        """
        records the number of time the page was submitted with an error. which specific error is not recorded.
        """
        solutions = dict(q1=2, q2=1)

        # error_message can return a dict whose keys are field names and whose values are error messages
        errors = {}
        for question, correct_answer in solutions.items():
            if values[question] != correct_answer:
                errors[question] = 'This answer is wrong'
                # Increment the specific failed attempt counter for the incorrect question
                failed_attempt_field = f"{question}_failed_attempts"
                if hasattr(player, failed_attempt_field):  # Ensure the field exists
                    setattr(player, failed_attempt_field, getattr(player, failed_attempt_field) + 1)
        if errors:
            return errors
        return None

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


class RandomSelection(Page):
    form_model = 'player'
    form_fields = ['random_selection']

    @staticmethod
    def is_displayed(player: Player):
        if player.round_number == C.NUM_ROUNDS:
            return True
        return None

    def vars_for_template(player: Player):
        return dict(
            player_in_all_rounds=player.in_all_rounds(),
            round_number=player.round_number,
            k_value=player.k_value,
            ratings=player.ratings,

            call_payment=random_payment(player),
        )


class End(Page):

    @staticmethod
    def is_displayed(player: Player):
        if player.round_number == C.NUM_ROUNDS:
            return True
        return None

    def vars_for_template(player: Player):
        return dict(
            player_in_all_rounds=player.in_all_rounds(),
            round_number=player.round_number,
            k_value=player.k_value,
            ratings=player.ratings,

            random_round=player.randomly_selected_round,
            random_k_value=player.randomly_selected_k_value,
            random_ratings=player.randomly_selected_ratings,
        )


class CommentBox(Page):
    form_model = 'player'
    form_fields = ['comment_box', 'strategy_box']

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
                 RandomSelection,
                 End,
                 CommentBox,
                 Payment,
                 ProlificLink,
                 ]
