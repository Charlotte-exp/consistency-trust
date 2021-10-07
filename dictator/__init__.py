from otree.api import *

import itertools

doc = """
Dictator game for the consistency project. 
perfect random matching
random token value
assymetric token value
"""


class Constants(BaseConstants):
    name_in_url = 'dictator'
    players_per_group = None
    num_rounds = 3
    instructions_template = 'dictator/instructions.html'

    pot_money = cu(100)
    endowment_p2 = pot_money/2
    endowment_p1 = pot_money/2

    value = pot_money * 0.5


class Subsession(BaseSubsession):
    pass


def creating_session(subsession: Subsession):
    """
    past_groups must be initialised in the settings.py.
    """
    session = subsession.session
    session.past_groups = []
    # for p in subsession.get_players():
    #     p.participant.vars['title'] = p.set_title()


def group_by_arrival_time_method(subsession: Subsession, waiting_players):
    """
    First, the gbat_new_partners code for random matching. this block perfect randomisation
    (one player never plays the same opponent twice).
    Then must make sure that there is always one dictator and one receiver per pair.
    I just used Nik's code from Multichannel.
    """
    session = subsession.session
    dictators = [p for p in waiting_players if p.participant.vars['title'] == 'dictator']
    receivers = [p for p in waiting_players if p.participant.vars['title'] == 'receiver']
    for possible_group in itertools.combinations(waiting_players, 2):
        # use a set, so that we can easily compare even if order is different
        # e.g. {1, 2} == {2, 1}
        pair_ids = set(p.id_in_subsession for p in possible_group)
        print(pair_ids)
        if pair_ids not in session.past_groups and len(dictators) >= 1 and len(receivers) >= 1:
            # mark this group as used, so we don't repeat it in the next round.
            session.past_groups.append(pair_ids)
            players = [dictators[0], receivers[0]]
            return possible_group and players


    # dictators = [p for p in waiting_players if p.title == 'dictator']
    # receivers = [p for p in waiting_players if p.title == 'receiver']
    # print(subsession.participant.vars['title'])



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

    title = models.StringField()


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


def set_title(player: Player):
    if player.id_in_subsesion % 2 == 0:
        return player.title == 'dictator'
    else:
        return player.title == 'receiver'


# PAGES
class Introduction(Page):
    pass


class Offer(Page):
    form_model = 'group'
    form_fields = ['decision']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.vars['title'] == 'dictator'

    def vars_for_template(player: Player):
        return dict(partner=player.get_others_in_group()[0])


class Receiver(Page):

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.vars['title'] == 'receiver'


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


class PairingWaitPage(WaitPage):
    group_by_arrival_time = True
    body_text = "Waiting to pair you with someone you haven't already played with"


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


page_sequence = [PairingWaitPage,
                 Offer,
                 Receiver,
                 ResultsWaitPage,
                 Results,
                 End]
