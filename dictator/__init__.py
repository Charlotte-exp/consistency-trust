from otree.api import *

import itertools
import random

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

    likelihood = 0.5
    values = [1, 3]


class Subsession(BaseSubsession):
    pass


def creating_session(subsession: Subsession):
    """
    past_groups must be initialised in the settings.py.
    """
    session = subsession.session
    session.past_groups = []

    # ok this assigns one of the values from the seq in constant for each player for each round.
    # issue is it's per player, not group. one cannot do groups as they are not created yet.
    # also, it is not printing to the data... why? The field is there but empty
    for p in subsession.get_players():
        p.participant.conversion = random.choice(Constants.values)
        print(p.participant.conversion)


def group_by_arrival_time_method(subsession: Subsession, waiting_players):
    """
    First, the gbat_new_partners code for random matching. this block perfect randomisation
    (one player never plays the same opponent twice). First check all the possible combinations.
    The function uses a set so we can check for the order (e.g. {1, 2} == {2, 1}).
    Then if the pair is not part of the past_group list and there is one receiver and one dictator, the new group is formed.
    Finally make sure to add this new group to the past_group list.
    """
    session = subsession.session
    for possible_group in itertools.combinations(waiting_players, 2):
        pair_ids = set(p.id_in_subsession for p in possible_group)
        if pair_ids not in session.past_groups and possible_group[0].participant.title != possible_group[1].participant.title:
            session.past_groups.append(pair_ids)
            new_conversion = new_conversion_value()
            for p in possible_group:
                p.conversion = new_conversion
                print(p.conversion)
                # p.new_value = p.participant.new_conversion
            return possible_group


class Group(BaseGroup):
    # kept = models.CurrencyField(
    #     doc="""Amount dictator decided to keep for himself""",
    #     min=0,
    #     max=Constants.endowment,
    #     label="I will keep",
    # )

    decision = models.CurrencyField(
        choices=[
            [0, f'Take the {Constants.endowment_p2} from the receiver.'],  # cooperate
            [1, f'Leave the {Constants.endowment_p2} of the receiver'],  # defect
        ],
        doc="""This player's decision""",
        verbose_name='Your decision:',
        widget=widgets.RadioSelect
    )


class Player(BasePlayer):

    title = models.StringField()
    conversion = models.IntegerField()


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
    print('Dictator', p1.payoff)
    print('Receiver', p2.payoff)


def new_conversion_value():
    """
    random assignment of the two conversion values from the constant list.
    """
    new_value = random.choice(Constants.values)
    return new_value


# def set_title(player: Player):
#     if player.id_in_subsesion % 2 == 0:
#         return player.title == 'dictator'
#     else:
#         return player.title == 'receiver'


# PAGES
class Introduction(Page):
    pass


class PairingWaitPage(WaitPage):
    group_by_arrival_time = True

    body_text = "Waiting to pair you with someone you haven't already played with"


class Offer(Page):
    form_model = 'group'
    form_fields = ['decision']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.title == 'dictator'

    def vars_for_template(player: Player):
        opponent = player.get_others_in_group()[0]
        return dict(
            partner=opponent,
            my_player_id=player.id_in_subsession,
            opponent_id=opponent.id_in_subsession,
        )


class Receiver(Page):

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.title == 'receiver'

    def vars_for_template(player: Player):
        opponent = player.get_others_in_group()[0]
        return dict(
            partner=opponent,
            my_player_id=player.id_in_subsession,
            opponent_id=opponent.id_in_subsession,
        )


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs
    # after_all_players_arrive = set_payoffs and new_conversion_value


class Results(Page):

    def vars_for_template(player: Player):
        opponent = player.get_others_in_group()[0]
        p1 = player.group.get_player_by_id(1)
        p2 = player.group.get_player_by_id(2)
        return dict(
            left=Constants.endowment_p2 - Constants.endowment_p2,
            p1_payoff=p1.payoff,
            p2_payoff=p2.payoff,
            partner=opponent,
            my_player_id=player.id_in_subsession,
            opponent_id=opponent.id_in_subsession,
        )


class End(Page):

    @staticmethod
    def is_displayed(player: Player):
        if player.round_number == 3:
            return True

    def vars_for_template(player: Player):
        opponent = player.get_others_in_group()[0]
        print(sum([p.payoff for p in player.in_all_rounds()]))
        print(sum([p.payoff for p in opponent.in_all_rounds()]))
        p1 = player.group.get_player_by_id(1)
        p2 = player.group.get_player_by_id(2)
        return dict(
            player_in_all_rounds=player.in_all_rounds(),
            p1_total_payoff=sum([p.payoff for p in player.in_all_rounds()]),
            p2_total_payoff=sum([p.payoff for p in player.in_all_rounds()]),
            my_total_payoff=sum([p.payoff for p in p1.in_all_rounds()]),
            opponent_total_payoff=sum([p.payoff for p in p2.in_all_rounds()]),
            partner=opponent,
            my_player_id=player.id_in_subsession,
            opponent_id=opponent.id_in_subsession,
        )


page_sequence = [PairingWaitPage,
                 Offer,
                 Receiver,
                 ResultsWaitPage,
                 Results,
                 End]
