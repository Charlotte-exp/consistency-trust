from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'Start'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 1

    SENDER_ROLE = 'Sender'
    RECEIVER_ROLE = 'Receiver'

    optionA_sender_high = cu(0.5)
    optionA_receiver_high = cu(1.5)
    optionB_sender_high = cu(1.5)
    optionB_receiver_high = cu(0.5)

    optionA_sender_low = cu(0.5)
    optionA_receiver_low = cu(0.6)
    optionB_sender_low = cu(0.6)
    optionB_receiver_low = cu(0.5)


class Subsession(BaseSubsession):
    pass


# def creating_session(subsession: Subsession):
#     for p in subsession.get_players():
#         p.participant.role = p.role
#         # print('roles', p.role, p.participant.role)
#         p.participant.is_dropout = False
#         # print(p.participant.is_dropout)


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


class InstruSender(Page):

    def vars_for_template(player: Player):
        """  """
        return dict(
            # role=player.role,
            sender_optionA=C.optionA_sender_high,
            receiver_optionA=C.optionA_receiver_high,
            sender_optionB=C.optionB_sender_high,
            receiver_optionB=C.optionB_receiver_high,
        )


class InstruReceiver(Page):

    def vars_for_template(player: Player):
        """  """
        return dict(
            # role=player.role,
            sender_optionA=C.optionA_sender_high,
            receiver_optionA=C.optionA_receiver_high,
            sender_optionB=C.optionB_sender_high,
            receiver_optionB=C.optionB_receiver_high,
        )


class Instructions(Page):

    def vars_for_template(player: Player):
        """  """
        if player.role == C.RECEIVER_ROLE:
            return dict(
                # role=player.role,
                sender_optionA=C.optionA_sender_high,
                receiver_optionA=C.optionA_receiver_high,
                sender_optionB=C.optionB_sender_high,
                receiver_optionB=C.optionB_receiver_high,
            )
        else:
            return dict(
                # role=player.role,
                sender_optionA=C.optionA_sender_high,
                receiver_optionA=C.optionA_receiver_high,
                sender_optionB=C.optionB_sender_high,
                receiver_optionB=C.optionB_receiver_high,
            )


page_sequence = [Consent,
                 Instructions]
