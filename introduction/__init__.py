from otree.api import *

import itertools

doc = """
Your app description
"""


class Constants(BaseConstants):
    name_in_url = 'introduction'
    players_per_group = None
    num_rounds = 1
    num_interactions = 2

    high_pot_money = cu(6)
    high_half_pot = high_pot_money / 2

    low_pot_money = cu(2)
    low_half_pot = low_pot_money / 2

    likelihood = 0.5
    values = [1, 2]


class Subsession(BaseSubsession):
    pass


def creating_session(subsession: Subsession):

    treatments = itertools.cycle(['high-high', 'low-low'])
    for player in subsession.get_players():
        player.condition = next(treatments)
        player.participant.condition = player.condition
        print('treatment', player.condition, player.participant.condition)


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    condition = models.StringField()

    q1 = models.IntegerField(
            choices=[
                [1, '0 other participants'],
                [2, '1 other participant'],
                [3, 'Different participants']
            ],
            verbose_name='With how many participants will you be playing in this study?',
            widget=widgets.RadioSelect
        )

    q2 = models.IntegerField(
        choices=[
            [1, 'There is no bonus possible in this study.'],
            [2, 'My bonus payment depends on luck.'],
            [3, 'My bonus payment depends on a decision taken by one of the participants.']
        ],
        verbose_name='What will your bonus payment depend on?',
        widget=widgets.RadioSelect
    )

    q3 = models.IntegerField(
        choices=[
            [1, 'You, the decider.'],
            [2, f'The receiver.'],
            [3, f'Both the decider and the receiver.']
        ],
        verbose_name=f'Who makes the decision in each interaction?',
        widget=widgets.RadioSelect
    )

    q4h = models.IntegerField(
        choices=[
            [1, '£0.'],
            [2, f'{Constants.high_half_pot}.'],
            [3, f'{Constants.high_pot_money}.']
        ],
        verbose_name=f'What will be your total payoff in this round if you choose to take the {Constants.high_half_pot}?',
        widget=widgets.RadioSelect
    )

    q4l = models.IntegerField(
        choices=[
            [1, '£0.'],
            [2, f'{Constants.low_half_pot}.'],
            [3, f'{Constants.low_pot_money}.']
        ],
        verbose_name=f'What will be your total payoff in this round if you choose to take the {Constants.low_half_pot}?',
        widget=widgets.RadioSelect
    )

    q5 = models.IntegerField(
        choices=[
            [1, 'The decider.'],
            [2, f'You, the receiver.'],
            [3, f'Both the decider and the receiver.']
        ],
        verbose_name=f'Who makes the decision in each interaction?',
        widget=widgets.RadioSelect
    )


#######   PAGES   #######
class Welcome(Page):
    form_model = 'player'
    form_fields = ['q1', 'q2']

    def error_message(player, values):
        if values['q1'] != 3:
            return 'Answer to question 2 is incorrect. Check the instructions again and give a new answer'
        if values['q2'] != 3:
            return 'Answer to question 3 is incorrect. Check the instructions again and give a new answer'


class Introduction(Page):
    pass


class InstruDictator(Page):
    form_model = 'player'

    def get_form_fields(player: Player):
        """ make one q3 for each subgroup that displays only to each to avoid empty field errors"""
        if player.condition == 'high-high':
            return ['q3', 'q4h']
        else:
            return ['q3', 'q4l']

    @staticmethod
    def error_message(player, values):  # it works but the message is wrong... it says question 2 and 3 when it should be question 1 and 2
        if values['q3'] != 1:
            return 'Answer to question 2 is incorrect. Check the instructions again and give a new answer'
        if player.condition == 'high-high':
            if values['q4h'] != 3:
                return 'Answer to question 3 is incorrect. Check the instructions again and give a new answer'
        else:
            if values['q4l'] != 3:
                return 'Answer to question 3 is incorrect. Check the instructions again and give a new answer'

    def vars_for_template(player: Player):
        if player.condition == 'high-high':
            return dict(
                pot_money=Constants.high_pot_money,
                half_pot=Constants.high_half_pot,
            )
        else:
            return dict(
                pot_money=Constants.low_pot_money,
                half_pot=Constants.low_half_pot,
            )

page_sequence = [Welcome,
                 # Introduction,
                 InstruDictator,
]
