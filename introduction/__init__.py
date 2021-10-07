from otree.api import *

import itertools

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
    conversion = '10 tokens = £0.20'


class Subsession(BaseSubsession):
    pass


def creating_session(subsession: Subsession):
    roles = itertools.cycle(['dictator', 'receiver'])
    for p in subsession.get_players():
        p.title = next(roles)
        p.participant.vars['title'] = p.title

    # for p in subsession.get_players():
    #     if p.player.id_in_subsession % 2 == 0:
    #         return p.player.title == 'dictator'
    #     else:
    #         return p.player.title == 'receiver'
        # p.participant.vars['title'] = p.title


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    title = models.StringField()


# def set_title(player: Player):
#     if player.id_in_subsesion % 2 == 0:
#         return player.title == 'dictator'
#     else:
#         return player.title == 'receiver'


# PAGES
class Welcome(Page):
    pass


class Instructions(Page):

    def vars_for_template(player: Player):
        return {
            'my_title': player.participant.vars['title'],
        }


class Introduction(Page):
    pass


page_sequence = [Welcome,
                 Instructions]
