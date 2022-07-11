from otree.api import *

import itertools

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'deception_task'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    SENDER_ROLE = 'Sender'
    RECEIVER_ROLE = 'Receiver'

    boxA_sender = cu(1)
    boxA_receiver = cu(1)
    boxB_sender = cu(10)
    boxB_receiver = cu(10)


class Subsession(BaseSubsession):
    pass


def creating_session(subsession: Subsession):

    treatments = itertools.cycle(['high', 'low'])
    for p in subsession.get_players():
        p.condition = next(treatments)
        p.participant.condition = p.condition
        print('treatment', p.condition, p.participant.condition)


class Group(BaseGroup):

    choice = models.CurrencyField(
        choices=[
            [0, f'Box A'],
            [1, f'Box B'],
        ],
        doc="""This player's decision""",
        verbose_name='Your decision:',
        widget=widgets.RadioSelect
    )


class Player(BasePlayer):

    condition = models.StringField()
    message = models.StringField()

    choice = models.CurrencyField(
        choices=[
            [0, f'Box A'],
            [1, f'Box B'],
        ],
        doc="""This player's decision""",
        verbose_name='Your decision:',
        widget=widgets.RadioSelect
    )

    age = models.IntegerField(
        verbose_name='What is your age?',
        min=18, max=100)

    gender = models.StringField(
        choices=['Female', 'Male', 'Other'],
        verbose_name='What gender do you identify as?',
        widget=widgets.RadioSelect)

    income = models.StringField(
        choices=['£9.999 or below', '£10.000 - £29.999', '£30.000 - £49.999',
                 '£50.000 - £69.999', '£70.000 - £89.999', '£90.000 or over', 'Prefer not to say'],
        verbose_name='What is the total combined income of your household?',
        widget=widgets.RadioSelect)

    education = models.StringField(
        choices=['No formal education', 'GCSE or equivalent', 'A-Levels or equivalent', 'Vocational training',
                 'Undergraduate degree', 'Postgraduate degree', 'Prefer not to say'],
        verbose_name='What is the highest level of education you have completed?',
        widget=widgets.RadioSelect)

    ethnicity = models.StringField(
        choices=['Asian/Asian British', 'Black/African/Caribbean/Black British', 'Mixed/Multiple Ethnic groups',
                 'White', 'Other'],
        verbose_name='What is your ethnicity?',
        widget=widgets.RadioSelect)

    comment_box = models.LongStringField(
        verbose_name=''
    )


########  Functions #######

def set_payoffs(group: Group):
    receiver = group.get_player_by_role(C.RECEIVER_ROLE)
    sender = group.get_player_by_role(C.SENDER_ROLE)
    if group.choice == 'Box A':
        receiver.payoff = C.boxA_receiver
        sender.payoff = C.boxA_sender
    else:
        receiver.payoff = C.boxB_receiver
        sender.payoff = C.boxB_sender


    # def set_payoff(player):
    #     if player.recevier.choice == 'Box A':
    #         player.receiver.payoff = C.boxA_receiver
    #         player.sender.payoff = C.boxA_sender
    #     else:
    #         player.receiver.payoff = C.boxB_receiver
    #         player.sender.payoff = C.boxB_sender


#######  PAGES  #########
class SenderMessage(Page):
    form_model = 'player'
    form_fields = ['message']

    @staticmethod
    def is_displayed(player):
        return player.role == C.SENDER_ROLE

    def vars_for_template(player: Player):
        """  """
        if player.participant.condition == 'high':
            return dict(
                sender_message=player.message.field_maybe_none()
            )
        else:
            return dict(
                sender_message=player.message.field_maybe_none()
            )


class MessageWaitPage(WaitPage):

    @staticmethod
    def is_displayed(player):
        return player.role == C.RECEIVER_ROLE

    body_text = "Please wait for the Sender to send his message."


class ReceiverChoice(Page):
    form_model = 'player'
    form_fields = ['choice']

    @staticmethod
    def is_displayed(player):
        return player.role == C.RECEIVER_ROLE

    def vars_for_template(player: Player):
        """  """
        if player.participant.condition == 'high':
            return dict(
                sender_message=player.message
            )
        else:
            return dict(
                sender_message=player.message
            )


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs

    @staticmethod
    def is_displayed(player):
        return player.role == C.SENDER_ROLE

    body_text = "Please wait for the Receiver to make their choice."


class Results(Page):

    def vars_for_template(player: Player):
        """  """
        if player.receiver.choice == 'Box A':
            return dict(
                receiver_payoff=C.boxA_sender,
                sender_payoff=C.boxA_receiver,
            )
        else:
            return dict(
                receiver_payoff=C.boxB_sender,
                sender_payoff=C.boxB_receiver,
            )


class End(Page):

    @staticmethod
    def is_displayed(player: Player):
        if player.round_number == C.num_rounds:
            return True

    def vars_for_template(player: Player):
        return dict(
            player_in_all_rounds=player.in_all_rounds(),
            total_payoff=sum([p.payoff for p in player.in_all_rounds()]),
        )


class Demographics(Page):
    """ This page displays survey box to record pp's demographics. it's just made of simple form fields. """
    form_model = 'player'
    form_fields = ['age', 'gender', 'income', 'education', 'ethnicity']

    @staticmethod
    def is_displayed(player: Player):
        if player.round_number == C.num_rounds:
            return True


class CommentBox(Page):
    form_model = 'player'
    form_fields = ['comment_box']

    @staticmethod
    def is_displayed(player: Player):
        if player.round_number == C.num_rounds:
            return True


class Payment(Page):

    @staticmethod
    def is_displayed(player: Player):
        if player.round_number == C.num_rounds:
            return True

    def vars_for_template(player: Player):
        participant = player.participant
        session = player.session
        return dict(
            bonus=participant.payoff.to_real_world_currency(session),
            participation_fee=session.config['participation_fee'],
            final_payment=participant.payoff_plus_participation_fee(),
        )


class ProlificLink(Page):
    """
    This page redirects pp to prolific automatically with a javascript (don't forget to put paste the correct link!).
    There is a short text and the link in case it is not automatic.
    """

    @staticmethod
    def is_displayed(player: Player):
        """ This page only appears on the last round. It's after LeftHanging so no need to hide it from dropouts."""
        return player.round_number == C.num_rounds


page_sequence = [SenderMessage,
                 ReceiverChoice,
                 ResultsWaitPage,
                 Results,
                 End,
                 Demographics,
                 CommentBox,
                 Payment,
                 ProlificLink]

