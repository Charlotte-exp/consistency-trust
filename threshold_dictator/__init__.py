from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'threshold_dictator'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 3

    endowment = cu(10)
    conversion_rate = 1
    proba_implementation = 0.1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    receiver_payoff = models.CurrencyField()

    decision = models.CurrencyField(
        choices=[
            [0, f'Selfish option'],  # defect
            [1, f'Cooperative option'],  # cooperate
        ],
        verbose_name='Your decision:',
        widget=widgets.RadioSelect
    )


######## PAGES ##########

class Decision(Page):
    form_model = 'player'
    form_fields = ['decision']


    def vars_for_template(player: Player):
        return dict(
            proba=C.proba_implementation * 10,
            conversion=C.conversion_rate,
        )


page_sequence = [Decision,
                 # ResultsWaitPage,
                 # Results
                 ]
