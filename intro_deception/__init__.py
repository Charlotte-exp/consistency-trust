from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'intro_deception'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 1

    SENDER_ROLE = 'Sender'
    RECEIVER_ROLE = 'Receiver'

    boxA_sender = cu(1)
    boxA_receiver = cu(2)
    boxB_sender = cu(3)
    boxB_receiver = cu(4)


class Subsession(BaseSubsession):
    pass


def creating_session(subsession: Subsession):
    for p in subsession.get_players():
        p.participant.role = p.role
        # print('roles', p.role, p.participant.role)


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass


# PAGES
class Consent(Page):

    def vars_for_template(player: Player):
        return {
            'participation_fee': player.session.config['participation_fee'],
        }


class Instructions(Page):

    def vars_for_template(player: Player):
        """  """
        if player.role == C.RECEIVER_ROLE:
            return dict(
                # role=player.role,
                receiver_payoff=C.boxB_sender,
                sender_payoff=C.boxB_receiver,
            )
        else:
            return dict(
                # role=player.role,
                receiver_payoff=C.boxB_sender,
                sender_payoff=C.boxB_receiver,
            )


page_sequence = [Consent,
                 Instructions]
