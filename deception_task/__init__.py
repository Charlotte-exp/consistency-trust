from otree.api import *

import itertools

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'deception_task'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 1

    SENDER_ROLE = 'Sender'
    RECEIVER_ROLE = 'Receiver'

    boxA_sender = cu(5)
    boxA_receiver = cu(6)
    boxB_sender = cu(6)
    boxB_receiver = cu(5)


class Subsession(BaseSubsession):
    pass


def creating_session(subsession: Subsession):

    treatments = itertools.cycle(['high', 'low'])
    for p in subsession.get_players():
        p.condition = next(treatments)
        p.participant.condition = p.condition
        print('treatment', p.condition, p.participant.condition)
        # p.role = p.participant.role


class Group(BaseGroup):
    pass
    # choice = models.StringField(
    #     initial='',
    #     choices=['Box A', 'Box B'],
    #     doc="""This player's decision""",
    #     verbose_name='Your choice:',
    #     widget=widgets.RadioSelect
    # )


class Player(BasePlayer):

    condition = models.StringField()
    left_hanging = models.IntegerField(initial=0)
    message = models.StringField(
        initial='',
        choices=['Box A', 'Box B'],
    )

    choice = models.StringField(
        initial='',
        choices=['Box A', 'Box B'],
        doc="""This player's decision""",
        verbose_name='Your choice:',
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

    q1 = models.IntegerField(
        choices=[
            [1, 'Yes'],
            [2, 'No']
        ],
        verbose_name='Do you think you played with a real other participant?',
        widget=widgets.RadioSelect
    )

    q2 = models.IntegerField(
        choices=[
            [1, 'Yes, the two had to match'],
            [2, 'No, the Receiver was free to ignore the message']
        ],
        verbose_name='Did the Receiver have to chose the same box as the Sender recommended?',
        widget=widgets.RadioSelect
    )

    q3 = models.IntegerField(
        choices=[
            [1, 'Yes'],
            [2, 'No']
        ],
        verbose_name='Did the bonuses in each box have to be the same for both participant?',
        widget=widgets.RadioSelect
    )

    q4 = models.IntegerField(
        choices=[
            [1, 'There is no bonus possible in this study.'],
            [2, 'My bonus payment depends on luck.'],
            [3, 'My bonus payment depends on the decision taken by '
                'the active player.']
        ],
        verbose_name='...?',
        widget=widgets.RadioSelect
    )


########  Functions #######

def other_player(player: Player):
    return player.get_others_in_group()[0]


def set_payoffs(group: Group):
    receiver = group.get_player_by_role(C.RECEIVER_ROLE)
    sender = group.get_player_by_role(C.SENDER_ROLE)
    if receiver.choice == 'Box A':
        receiver.payoff = C.boxA_receiver
        sender.payoff = C.boxA_sender
    else:
        receiver.payoff = C.boxB_receiver
        sender.payoff = C.boxB_sender


# def set_message(player: Player):
#     if player.message == 'Box A':
#         return print("whatever")

    # def set_payoff(player):
    #     if player.recevier.choice == 'Box A':
    #         player.receiver.payoff = C.boxA_receiver
    #         player.sender.payoff = C.boxA_sender
    #     else:
    #         player.receiver.payoff = C.boxB_receiver
    #         player.sender.payoff = C.boxB_sender


######  PAGES  #########

class PairingWaitPage(WaitPage):
    group_by_arrival_time = True

    def is_displayed(player: Player):
        return player.round_number == 1

    template_name = 'deception_task/Waitroom.html'


class SenderMessage(Page):
    form_model = 'player'
    form_fields = ['message']

    @staticmethod
    def is_displayed(player):
        if player.participant.role == 'Sender':
            return True

    timer_text = 'If you stay inactive for too long you will be considered a dropout:'
    timeout_seconds = 2 * 60

    def before_next_page(player, timeout_happened):
        """
        Dropout check code! If the timer set above runs out, all the other players in the group become left_hanging = 1
        and are jumped to the leftHanging page with a link to Prolific. The dropout also goes to that page but gets
        a different text (left_hanging = 2).
        Decisions for the missed round are automatically filled to avoid an NONE type error.
        """
        me = player
        partner = other_player(me)
        if timeout_happened:
            partner.left_hanging = 1
            me.left_hanging = 2
            me.message = 'left_hanging'


class MessageWaitPage(WaitPage):

    @staticmethod
    def is_displayed(player):
        return player.participant.role == 'Receiver'

    body_text = "Please wait for the Sender to send his message."


class ReceiverChoice(Page):
    form_model = 'player'
    form_fields = ['choice']

    @staticmethod
    def is_displayed(player):
        return player.participant.role == 'Receiver'

    def vars_for_template(player: Player):
        """  """
        me = player
        partner = other_player(me)
        return dict(sender_message=partner.message)
        # if player.participant.condition == 'high':
        #     return dict(
        #         sender_message=player.message
        #     )
        # else:
        #     return dict(
        #         sender_message=player.message
        #     )

    timer_text = 'If you stay inactive for too long you will be considered a dropout:'
    timeout_seconds = 2 * 60

    def before_next_page(player, timeout_happened):
        """
        Dropout check code! If the timer set above runs out, all the other players in the group become left_hanging = 1
        and are jumped to the leftHanging page with a link to Prolific. The dropout also goes to that page but gets
        a different text (left_hanging = 2).
        Decisions for the missed round are automatically filled to avoid an NONE type error.
        """
        me = player
        partner = other_player(me)
        if timeout_happened:
            partner.left_hanging = 1
            me.left_hanging = 2
            me.choice = 'left_hanging'


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs

    @staticmethod
    def is_displayed(player):
        return player.participant.role == 'Sender'

    body_text = "Please wait for the Receiver to make their choice."


class Results(Page):

    def vars_for_template(player: Player):
        """  """
        if player.participant.role == 'Receiver':
            if player.choice == 'Box A':
                return dict(
                    # role=player.role,
                    choice=player.choice,
                    receiver_payoff=C.boxA_sender,
                    sender_payoff=C.boxA_receiver,
                )
            else:
                return dict(
                    # role=player.role,
                    choice=player.choice,
                    receiver_payoff=C.boxB_sender,
                    sender_payoff=C.boxB_receiver,
                )
        else:
            me = player
            partner = other_player(me)
            if partner.choice == 'Box A':
                return dict(
                    # role=player.role,
                    choice=partner.choice,
                    receiver_payoff=C.boxA_sender,
                    sender_payoff=C.boxA_receiver,
                )
            else:
                return dict(
                    # role=player.role,
                    choice=partner.choice,
                    receiver_payoff=C.boxB_sender,
                    sender_payoff=C.boxB_receiver,
                )

    # only need this if it is repeated rounds
    # timer_text = 'If you stay inactive for too long you will be considered a dropout:'
    # timeout_seconds = 2 * 60


class End(Page):

    # only need this if it is repeated rounds
    # @staticmethod
    # def is_displayed(player: Player):
    #     if player.round_number == C.num_rounds:
    #         return True

    def vars_for_template(player: Player):
        return dict(
            player_in_all_rounds=player.in_all_rounds(),
            total_payoff=sum([p.payoff for p in player.in_all_rounds()]),
        )


class Demographics(Page):
    """ This page displays survey box to record pp's demographics. it's just made of simple form fields. """
    form_model = 'player'
    form_fields = ['age', 'gender', 'income', 'education', 'ethnicity']

    # @staticmethod
    # def is_displayed(player: Player):
    #     if player.round_number == C.num_rounds:
    #         return True


class Comprehension(Page):
    form_model = 'player'
    form_fields = ['q1', 'q2', 'q3', 'q4']

    # @staticmethod
    # def error_message(player: Player, values):
    #     # alternatively, you could make quiz1_error_message, quiz2_error_message, etc.
    #     # but if you have many similar fields, this is more efficient.
    #     solutions = dict(q1=2, q2=3, q3=1, q4=3)
    #
    #     # error_message can return a dict whose keys are field names and whose
    #     # values are error messages
    #     errors = {f: 'This answer is wrong' for f in solutions if values[f] != solutions[f]}
    #     # print('errors is', errors)
    #     if errors:
    #         player.num_failed_attempts += 1
    #         return errors

    # @staticmethod
    # def error_message(player: Player, values):
    #     if values['q1'] != 2:
    #         player.q1_failed_attempts += 1
    #         return 'Answer to question 1 is incorrect. Check the instructions again and give a new answer'
    #     if values['q2'] != 3:
    #         player.q2_failed_attempts += 1
    #         return 'Answer to question 2 is incorrect. Check the instructions again and give a new answer'
    #     if values['q3'] != 1:
    #         player.q3_failed_attempts += 1
    #         return 'Answer to question 3 is incorrect. Check the instructions again and give a new answer'
    #     if values['q4'] != 3:
    #         player.q4_failed_attempts += 1
    #         return 'Answer to question 4 is incorrect. Check the instructions again and give a new answer'


class CommentBox(Page):
    form_model = 'player'
    form_fields = ['comment_box']

    # @staticmethod
    # def is_displayed(player: Player):
    #     if player.round_number == C.num_rounds:
    #         return True


class Payment(Page):

    # @staticmethod
    # def is_displayed(player: Player):
    #     if player.round_number == C.num_rounds:
    #         return True

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

    # @staticmethod
    # def is_displayed(player: Player):
    #     """ This page only appears on the last round. It's after LeftHanging so no need to hide it from dropouts."""
    #     return player.round_number == C.num_rounds


page_sequence = [SenderMessage,
                 MessageWaitPage,
                 ReceiverChoice,
                 ResultsWaitPage,
                 Results,
                 # End,
                 # Demographics,
                 Comprehension,
                 # CommentBox,
                 Payment,
                 ProlificLink]

