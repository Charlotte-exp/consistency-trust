from otree.api import *



doc = """
One player decides how to divide a certain amount between himself and the other
player.
See: Kahneman, Daniel, Jack L. Knetsch, and Richard H. Thaler. "Fairness
and the assumptions of economics." Journal of business (1986):
S285-S300.
"""


class Constants(BaseConstants):
    name_in_url = 'dictator'
    players_per_group = 2
    num_rounds = 3
    instructions_template = 'dictator/instructions.html'

    pot_money = cu(100)
    endowment_p2 = pot_money/2
    endowment_p1 = pot_money/2

    value = pot_money * 0.5


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    # kept = models.CurrencyField(
    #     doc="""Amount dictator decided to keep for himself""",
    #     min=0,
    #     max=Constants.endowment,
    #     label="I will keep",
    # )

    decision = models.CurrencyField(
        choices=[
            [0, f'Take the {Constants.endowment_p2} token from Participant 2.'],  # cooperate
            [1, f'Leave the {Constants.endowment_p2} token of Participant 2'],  # defect
        ],
        doc="""This player's decision""",
        widget=widgets.RadioSelect
    )


class Player(BasePlayer):
    pass


# FUNCTIONS
def set_payoffs(group: Group):
    p1 = group.get_player_by_id(1)
    p2 = group.get_player_by_id(2)
    if group.decision == 0:
        p1.payoff = Constants.pot_money
        p2.payoff = 0
    else:
        p1.payoff = Constants.endowment_p1
        p2.payoff = Constants.endowment_p2


# PAGES
class Introduction(Page):
    pass


class Offer(Page):
    form_model = 'group'
    form_fields = ['decision']

    @staticmethod
    def is_displayed(player: Player):
        return player.id_in_group == 1

    def vars_for_template(player: Player):
        return dict(partner=player.get_others_in_group()[0])


class Receiver(Page):

    def is_displayed(player: Player):
        return player.id_in_group == 2


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        p1 = player.group.get_player_by_id(1)
        p2 = player.group.get_player_by_id(2)
        return dict(
            left=Constants.endowment_p2 - Constants.endowment_p2,
            p1_payoff=p1.payoff,
            p2_payoff=p2.payoff,

        )


class End(Page):
    def is_displayed(player: Player):
        if player.round_number == 3:
            return True

    def vars_for_template(player: Player):
        return {
            'player_in_all_rounds': player.in_all_rounds(),
            'p1_total_payoff': sum([p.payoff for p in player.in_all_rounds()]),
            'p2_total_payoff': sum([p.payoff for p in player.in_all_rounds()])
        }


page_sequence = [Introduction,
                 Offer,
                 Receiver,
                 ResultsWaitPage,
                 Results,
                 End]
