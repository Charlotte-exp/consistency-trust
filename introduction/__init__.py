from otree.api import *

import itertools

doc = """
Your app description
"""


class Constants(BaseConstants):
    name_in_url = 'introduction'
    players_per_group = None
    num_rounds = 1
    n_of_rounds = 3
    instructions_template = 'introduction/instructions.html'

    pot_money = cu(100)
    endowment_p2 = pot_money/2
    endowment_p1 = pot_money/2

    value = pot_money * 0.5
    conversion = '10 tokens = £0.20'


class Subsession(BaseSubsession):
    pass


def creating_session(subsession: Subsession):
    roles = itertools.cycle(['dictator', 'receiver'])
    for p in subsession.get_players():
        p.title = next(roles)
        p.participant.title = p.title

    # for p in subsession.get_players():
    #     if p.id_in_subsession % 2 == 0:
    #         return p.player.title == 'dictator'
    #     else:
    #         return p.player.title == 'receiver'


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    title = models.StringField()

    q1 = models.IntegerField(
            choices=[
                [1, '0 other participants'],
                [2, '1 other participant'],
                [3, 'multiple other participants']
            ],
            verbose_name='With how many participants will you be playing in this task?',
            widget=widgets.RadioSelect
        )

    q2 = models.IntegerField(
        choices=[
            [1, 'There is no bonus possible in this study.'],
            [2, 'My bonus payment depends on the conversion rates in each round.'],
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

    q4 = models.IntegerField(
        choices=[
            [1, '0 tokens.'],
            [2, f'{Constants.endowment_p1}.'],
            [3, f'{Constants.pot_money}.']
        ],
        verbose_name=f'What will be your total payoff in this round if you choose to take the {Constants.endowment_p1}?',
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


# def set_title(player: Player):
#     if player.id_in_subsesion % 2 == 0:
#         return player.title == 'dictator'
#     else:
#         return player.title == 'receiver'


# PAGES
class Welcome(Page):
    form_model = 'player'
    form_fields = ['q1', 'q2']

    def error_message(player, values):
        if values['q1'] != 3:
            return 'Answer to question 2 is incorrect. Check the instructions again and give a new answer'
        if values['q2'] != 2:
            return 'Answer to question 3 is incorrect. Check the instructions again and give a new answer'


class Introduction(Page):
    pass


class InstruDictator(Page):
    form_model = 'player'
    form_fields = ['q3', 'q4']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.title == 'dictator'

    @staticmethod
    def error_message(player, values):  # it works but the message is wrong...
        if values['q3'] != 1:
            return 'Answer to question 2 is incorrect. Check the instructions again and give a new answer'
        if values['q4'] != 3:
            return 'Answer to question 3 is incorrect. Check the instructions again and give a new answer'

    def vars_for_template(player: Player):
        return {
            'my_title': player.participant.title,
        }


class InstruReceiver(Page):
    form_model = 'player'
    form_fields = ['q5']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.title == 'receiver'

    @staticmethod
    def error_message(player, values):
        if values['q5'] != 1:
            return 'Answer to question 2 is incorrect. Check the instructions again and give a new answer'

    def vars_for_template(player: Player):
        return {
            'my_title': player.participant.title,
        }


page_sequence = [Welcome,
                 # Introduction,
                 InstruDictator,
                 InstruReceiver]
