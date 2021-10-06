from otree.api import *


doc = """
Your app description
"""


class Constants(BaseConstants):
    name_in_url = 'introduction'
    players_per_group = None
    num_rounds = 1
    instructions_template = 'introduction/instructions.html'

    pot_money = cu(100)
    endowment_p2 = pot_money/2
    endowment_p1 = pot_money/2

    value = pot_money * 0.5


class Subsession(BaseSubsession):
    pass


def creating_session(subsession: Subsession):
    for p in subsession.get_players():
        p.participant.vars['title'] = p.title


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass


def set_title(player: Player):
    if player.id_in_subsesion % 2 == 0:
        return player.title == 'dictator'
    else:
        return player.title == 'receiver'


# PAGES
class Welcome(Page):
    pass


class Introduction(Page):
    pass


page_sequence = [Welcome,
                 Introduction]
