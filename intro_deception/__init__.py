from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'intro_deception'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    SENDER_ROLE = 'Sender'
    RECEIVER_ROLE = 'Receiver'

    boxA_sender = cu(1)
    boxA_receiver = cu(2)
    boxB_sender = cu(10)
    boxB_receiver = cu(20)


class Subsession(BaseSubsession):
    pass


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
