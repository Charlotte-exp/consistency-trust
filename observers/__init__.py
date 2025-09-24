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
    NUM_ROUNDS = 11

    NUMBER_WORDS = [
        "zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
        "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen",
        "eighteen", "nineteen", "twenty"
    ]

    number_of_trials = 20 # from the actor task
    percent_accurate = 90
    bonus_ratings = cu(2)
    bonus_fraction = cu(0.1)


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
            # for rounds >1, just pick from participant.vars BUT not last round because fantom page
            last_index = len(p.participant.vars['sequence']) - 1
            idx = min(p.round_number - 1, last_index)
            p.k_value = p.participant.vars['sequence'][idx]

class Group(BaseGroup):
    pass


class Player(BasePlayer):

    k_value = models.IntegerField(initial=99)
    ratings = models.IntegerField(
        initial=999,
        verbose_name='How cooperative is this person?',
        min=0, max=100,
    )

    zero_20 = models.IntegerField(
        label='',
        min=0, max=100,
    )

    one_20 = models.IntegerField(
        label='',
        min=0, max=100,
    )

    two_20 = models.IntegerField(
        label='',
        min=0, max=100,
    )

    three_20 = models.IntegerField(
        label='',
        min=0, max=100,
    )

    four_20 = models.IntegerField(
        label='',
        min=0, max=100,
    )

    five_20 = models.IntegerField(
        label='',
        min=0, max=100,
    )

    six_20 = models.IntegerField(
        label='',
        min=0, max=100,
    )

    seven_20 = models.IntegerField(
        label='',
        min=0, max=100,
    )

    eight_20 = models.IntegerField(
        label='',
        min=0, max=100,
    )

    nine_20 = models.IntegerField(
        label='',
        min=0, max=100,
    )

    ten_20 = models.IntegerField(
        label='',
        min=0, max=100,
    )

    eleven_20 = models.IntegerField(
        label='',
        min=0, max=100,
    )

    twelve_20 = models.IntegerField(
        label='',
        min=0, max=100,
    )

    thirteen_20 = models.IntegerField(
        label='',
        min=0, max=100,
    )

    fourteen_20 = models.IntegerField(
        label='',
        min=0, max=100,
    )

    fifteen_20 = models.IntegerField(
        label='',
        min=0, max=100,
    )

    sixteen_20 = models.IntegerField(
        label='',
        min=0, max=100,
    )

    seventeen_20 = models.IntegerField(
        label='',
        min=0, max=100,
    )

    eighteen_20 = models.IntegerField(
        label='',
        min=0, max=100,
    )

    nineteen_20 = models.IntegerField(
        label='',
        min=0, max=100,
    )

    twenty_20 = models.IntegerField(
        label='',
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
            [1, f'You will receive a {C.bonus_ratings} bonus, '
                f'if you are closer than {C.percent_accurate}% of all the other participants '
                f'for one randomly selected round of this task.'],
            [2, f'You will receive a {C.bonus_ratings} bonus, '
                f'if you are closer than 80% of all the other participants '
                f'for one randomly selected round of this task.'],
            [3, f'You will receive {C.bonus_ratings} bonus, no matter what you write'],
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
    randomly_selected_round = random.randint(1, (C.NUM_ROUNDS-1)) ## only round 1-10 since I added one
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
    def is_displayed(player: Player):
        if player.round_number == 1:
            return True
        return False

    @staticmethod
    def vars_for_template(player: Player):
        if player.id_in_group % 2 == 1:
            player_is = 'odd'
        else:
            player_is = 'even'
        return dict(
            player_id=player_is,
            played_rounds=C.NUM_ROUNDS-1,
        )

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


class FractionOfCooperators(Page):
    form_model = 'player'

    @staticmethod
    def get_form_fields(player: Player):
        return [f"{w}_20" for w in C.NUMBER_WORDS]

    @staticmethod
    def is_displayed(player: Player):
        if player.round_number == 1:
            return player.id_in_group % 2 == 1
        if player.round_number == C.NUM_ROUNDS:
            return player.id_in_group % 2 == 0
        return False

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
        )

    @staticmethod
    def error_message(player, values):
        # list of all field names you want to sum
        field_names = [
            'zero_20', 'one_20', 'two_20', 'three_20', 'four_20', 'five_20',
            'six_20', 'seven_20', 'eight_20', 'nine_20', 'ten_20',
            'eleven_20', 'twelve_20', 'thirteen_20', 'fourteen_20', 'fifteen_20',
            'sixteen_20', 'seventeen_20', 'eighteen_20', 'nineteen_20', 'twenty_20'
        ]
        total = sum(values[name] for name in field_names)
        if total != 100:
            return 'The numbers must add up to 100'
        return None


class CooperativenessRatings(Page):
    form_model = 'player'
    form_fields = ['ratings']

    @staticmethod
    def is_displayed(player: Player):
        if player.round_number < C.NUM_ROUNDS:
            return True
        return False

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
        return False

    def vars_for_template(player: Player):
        almost_all_rounds = player.in_rounds(1, C.NUM_ROUNDS-1)
        return dict(
            player_in_all_rounds= almost_all_rounds,
            round_number=player.round_number,
            played_rounds=C.NUM_ROUNDS-1,
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
        almost_all_rounds = player.in_rounds(1, C.NUM_ROUNDS - 1)
        return dict(
            player_in_all_rounds=almost_all_rounds,
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
            final_bonus=player.payoff.to_real_world_currency(session),
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
                 FractionOfCooperators,
                 CooperativenessRatings,
                 RandomSelection,
                 End,
                 CommentBox,
                 Payment,
                 ProlificLink,
                 ]
