from otree.api import *

import itertools

doc = """
Your app description
"""


class Constants(BaseConstants):
    name_in_url = 'introduction'
    players_per_group = None
    num_rounds = 1
    num_interactions = 1
    session_time = 10
    participation_fee = cu(1)

    high_half_pot = cu(1)
    high_pot_money = high_half_pot * 2

    low_half_pot = cu(0.10)
    low_pot_money = low_half_pot * 2

    likelihood = 0.5
    endowments = [cu(0.10), cu(0.5), cu(1)]


class Subsession(BaseSubsession):
    pass


# def creating_session(subsession: Subsession):
#
#     treatments = itertools.cycle(['high', 'low'])
#     for p in subsession.get_players():
#         p.condition = next(treatments)
#         p.participant.condition = p.condition
#         print('treatment', p.condition, p.participant.condition)


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    condition = models.StringField()

    q1 = models.IntegerField(
            choices=[
                [1, '0 other participants'],
                [2, '1 other participant'],
                [3, f'2 other participants']
            ],
            verbose_name='With how many participants will you be paired with in each interaction?',
            widget=widgets.RadioSelect
        )

    q2 = models.IntegerField(
            choices=[
                [1, '0 other participants'],
                [2, '1 other participant'],
                [3, f'2 other participants']
            ],
            verbose_name='If you play two interactions, how many different participants will you face in total?',
            widget=widgets.RadioSelect
        )

    q3 = models.IntegerField(
            choices=[
                [1, 'The active player'],
                [2, 'The passive player'],
                [3, f"It's random"]
            ],
            verbose_name='If you play two interactions, and you are selected to be the active player in the first interaction, what will your role be in the second interaction?',
            widget=widgets.RadioSelect
        )

    q4 = models.IntegerField(
        choices=[
            [1, 'There is no bonus possible in this study.'],
            [2, 'My bonus payment depends on luck.'],
            [3, 'My bonus payment depends on the decision taken by '
                'the active player.']
        ],
        verbose_name='What will your bonus payment in each interaction depend on?',
        widget=widgets.RadioSelect
    )

    q5 = models.IntegerField(
        choices=[
            [1, f"Either both players get {Constants.high_half_pot} or both players get {Constants.low_half_pot}."],
            [2, f'Either the active player gets {Constants.high_half_pot} while the passive player gets {Constants.low_half_pot} '
                f'or the other way around.'],
            [3, f'Either both players get {Constants.low_half_pot*2} or both players get {Constants.high_half_pot*2}.']
        ],
        verbose_name=f"What are the possible endowment sizes in a given interaction?",
        widget=widgets.RadioSelect
    )

    q6 = models.IntegerField(
        choices=[
            [1, f'The active player does not make any decisions.'],
            [2, "Take or leave the other player's endowment."],
            [3, f'Keep or give your endowment to the other player.']
        ],
        verbose_name=f" What are the active player's options in a given interaction?",
        widget=widgets.RadioSelect
    )

    q7 = models.IntegerField(
        choices=[
            [1, '£0.'],
            [2, f'{Constants.low_half_pot}.'],
            [3, f'{Constants.low_pot_money}.']
        ],
        verbose_name=f"What will be the active player's payoff, "
                     f"if the endowments are {Constants.low_half_pot} and he/she chooses to take?",
        widget=widgets.RadioSelect
    )

    q8 = models.IntegerField(
        choices=[
            [1, '£0.'],
            [2, f'{Constants.low_half_pot}.'],
            [3, f'{Constants.low_pot_money}.']
        ],
        verbose_name=f"What will be the passive player's payoff, "
                     f"if the endowments are {Constants.low_half_pot} and the active player chooses to take?",
        widget=widgets.RadioSelect
    )

    q9 = models.IntegerField(
        choices=[
            [1, 'The decider.'],
            [2, f'You, the recipient.'],
            [3, f'Both the decider and the recipient.']
        ],
        verbose_name=f'Who makes the decision in each interaction?',
        widget=widgets.RadioSelect
    )


#######   PAGES   #######
class Consent(Page):
    pass


class Welcome(Page):
    form_model = 'player'
    form_fields = ['q1', 'q2', 'q3', 'q4']

    def error_message(player, values):
        if values['q1'] != 2:
            return 'Answer to question 1 is incorrect. Check the instructions again and give a new answer'
        if values['q2'] != 3:
            return 'Answer to question 2 is incorrect. Check the instructions again and give a new answer'
        if values['q3'] != 3:
            return 'Answer to question 3 is incorrect. Check the instructions again and give a new answer'
        if values['q4'] != 3:
            return 'Answer to question 4 is incorrect. Check the instructions again and give a new answer'


class Introduction(Page):
    pass


class InstruDictator(Page):
    form_model = 'player'

    def get_form_fields(player: Player):
        """ make one q3 for each subgroup that displays only to each to avoid empty field errors"""
        return ['q5', 'q6', 'q7', 'q8']

    def error_message(player, values):  # it works but the message is wrong... it says question 2 and 3 when it should be question 1 and 2
        if values['q5'] != 1:
            return 'Answer to question 1 is incorrect. Check the instructions again and give a new answer'
        if values['q6'] != 2:
            return 'Answer to question 2 is incorrect. Check the instructions again and give a new answer'
        if values['q7'] != 3:
            return 'Answer to question 3 is incorrect. Check the instructions again and give a new answer'
        if values['q8'] != 1:
            return 'Answer to question 4 is incorrect. Check the instructions again and give a new answer'

    def vars_for_template(player: Player):
        return dict(
            pot_money=Constants.high_pot_money,
            half_pot=Constants.high_half_pot,
        )


page_sequence = [Consent,
                 Welcome,
                 # Introduction,
                 InstruDictator,
]
