from otree.api import *

import random

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'matching'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 1

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


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    choice = models.StringField(
        initial='',
        choices=['Option A', 'Option B'],
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
            [1, '1 partner, the same in each task'],
            [2, '3 partners, one per task']
        ],
        verbose_name='With how many different partner did each participant interact '
                     '(regardless of whether some partner dropped out)?',
        widget=widgets.RadioSelect
    )

    q2 = models.IntegerField(
        choices=[
            [1, 'Yes, the two had to match'],
            [2, 'No, the Receiver was free to ignore the message']
        ],
        verbose_name='Did the Receiver have to chose the same option as the Sender recommended?',
        widget=widgets.RadioSelect
    )

    q3 = models.IntegerField(
        choices=[
            [1, 'Only their own final bonus and not the one of the Sender'],
            [2, "Both their own and the Sender's final bonus"],
            [3, "Both their own and the Sender's final bonus, as well as the bonus of the option not chosen"],
        ],
        verbose_name='What did the Receiver know about the bonuses in the end?',
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

    def get_button_order(player):
        if random.random() > 0.5:
            return 1
        else:
            return 0


##### FUNCTIONS #####

def group_by_arrival_time_method(subsession, waiting_players):
    senders = [p for p in waiting_players if p.participant.role == 'Sender']
    receivers = [p for p in waiting_players if p.participant.role == 'Receiver']
    if len(senders) >= 1 and len(receivers) >= 1:
        players = [senders[0], receivers[0]]
        # treatment = subsession.get_treatments()
        # for p in players:
        #     p.participant.treatment = treatment
        #     p.treatment = p.participant.treatment
        return players


def other_player(player: Player):
    return player.get_others_in_group()[0]


def get_sender_bonus(player: Player):
    me = player
    partner = other_player(me)
    if me.participant.role == 'Sender':
        if me.participant.randomly_selected_stake == 'high':
            if partner.choice == 'Option A':
                sender_bonus = C.optionA_sender_high
            else:
                sender_bonus = C.optionB_sender_high
        else:
            if partner.choice == 'Option A':
                sender_bonus = C.optionA_sender_low
            else:
                sender_bonus = C.optionB_sender_low
        return sender_bonus


def get_receiver_bonus(player: Player):
    me = player
    partner = other_player(me)
    if me.participant.role == 'Receiver':
        if partner.participant.randomly_selected_stake == 'high':
            if me.choice == 'Option A':
                receiver_bonus = C.optionA_sender_high
            else:
                receiver_bonus = C.optionB_sender_high
        else:
            if me.choice == 'Option A':
                receiver_bonus = C.optionA_sender_low
            else:
                receiver_bonus = C.optionB_sender_low
        return receiver_bonus


def get_payoffs(player: Player):
    me = player
    partner = other_player(me)
    if me.participant.role == 'Receiver':
        me.payoff = get_receiver_bonus(me)
        partner.payoff = get_sender_bonus(me)
    elif me.participant.role == 'Sender':
        me.payoff = get_sender_bonus(me)
        partner.payoff = get_receiver_bonus(me)


# def get_payoffs(player: Player):
#     me = player
#     partner = other_player(me)
#     if me.participant.role == 'Receiver':
#         if me.left_hanging == 1:
#             me.payoff = me.optionA_receiver
#         elif me.left_hanging == 2:
#             me.payoff = cu(0)
#         elif me.choice == 'Option A':
#             partner.payoff = partner.optionA_sender
#             me.payoff = me.optionA_receiver
#         elif me.choice == 'Option B':
#             partner.payoff = partner.optionB_sender
#             me.payoff = me.optionB_receiver
#     elif me.participant.role == 'Sender':
#         if me.left_hanging == 1:
#             me.payoff = me.optionB_sender
#         elif me.left_hanging == 2:
#             me.payoff = cu(0)
#         elif partner.choice == 'Option A':
#             me.payoff = me.optionA_sender
#             partner.payoff = partner.optionA_receiver
#         elif me.choice == 'Option B':
#             me.payoff = partner.optionB_sender
#             partner.payoff = me.optionB_receiver


def set_payoffs(group: Group):
    for p in group.get_players():
        get_payoffs(p)
        print_fuck(p)


def print_fuck(player: Player):
    """
    Just to test how to call multiple functions through set_payoffs and after_all_players_arrive. It does!
    """
    print("Fuck")


###### PAGES #######

class PairingWaitPage(WaitPage):
    group_by_arrival_time = True

    def is_displayed(player: Player):
        return player.round_number == 1

    def vars_for_template(player: Player):
            """  """
            participant = player.participant
            return dict(
                role=player.participant.role,
                is_dropout=participant.is_dropout,
                round_number=player.round_number,
            )

    template_name = 'receiver_matching/Waitroom.html'


class ReceiverChoice(Page):
    form_model = 'player'
    form_fields = ['choice']

    @staticmethod
    def is_displayed(player):
        if player.participant.role == 'Receiver':
            return True

    def vars_for_template(player: Player):
        """  """
        me = player
        partner = other_player(me)
        if partner.participant.randomly_selected_message == 'Option A':
            return dict(
                other_player=partner.id_in_group,
                player=player.id_in_group,
                best_option='Option A',
                worst_option='Option B',

                round_number=player.round_number,

                button=player.get_button_order(),
            )
        else:
            return dict(
                other_player=partner.id_in_group,
                player=player.id_in_group,
                best_option='Option B',
                worst_option='Option A',

                round_number=player.round_number,

                button=player.get_button_order(),
            )

    timer_text = 'If you stay inactive for too long you will be considered a dropout:'

    @staticmethod
    def get_timeout_seconds(player):
        participant = player.participant

        if participant.is_dropout:
            return 1  # instant timeout, 1 second
        else:
            return 2 * 60

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
            me.participant.is_dropout = True
            # print(me.participant.is_dropout)
            partner.left_hanging = 1
            me.left_hanging = 2
            me.choice = 'None'


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs

    template_name = 'receiver_matching/ResultsWaitPage.html'

    # body_text = "Please wait for the Receiver to make their choice."

    # @staticmethod
    # def is_displayed(player):
    #     participant = player.participant
    #     if participant.is_dropout:
    #         return False
    #     elif player.participant.role == 'Sender' or player.participant.role == 'Receiver':
    #         return True

    def vars_for_template(player: Player):
            """  """
            participant = player.participant
            return dict(
                role=player.participant.role,
                is_dropout=participant.is_dropout,
                round_number=player.round_number,
            )


class Results(Page):

    @staticmethod
    def is_displayed(player: Player):
        if player.participant.is_dropout:
            return False
        elif player.round_number == C.NUM_ROUNDS:
            return True

    def vars_for_template(player: Player):
        """  """
        participant = player.participant
        return dict(
            role=player.participant.role,
            is_dropout=participant.is_dropout,
            round_number=player.round_number,
            payoff=player.payoff,
        )


class Demographics(Page):
    """ This page displays survey box to record participants' demographics. it's just made of simple form fields. """
    form_model = 'player'
    form_fields = ['age', 'gender', 'income', 'education', 'ethnicity']

    @staticmethod
    def is_displayed(player: Player):
        if player.participant.is_dropout:
            return False
        elif player.participant.role == 'Sender':
            return True


class Comprehension(Page):
    form_model = 'player'
    form_fields = ['q1', 'q2', 'q3']

    @staticmethod
    def is_displayed(player: Player):
        if player.participant.is_dropout:
            return False
        elif player.participant.role == 'Sender':
            return True

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

    @staticmethod
    def is_displayed(player: Player):
        if player.participant.is_dropout:
            return False
        elif player.participant.role == 'Sender':
            return True


class Payment(Page):

    @staticmethod
    def is_displayed(player: Player):
        if player.participant.is_dropout:
            return False
        elif player.round_number == C.NUM_ROUNDS:
            return True

    def vars_for_template(player: Player):
        participant = player.participant
        session = player.session
        return dict(
            bonus=player.payoff.to_real_world_currency(session),
            participation_fee=session.config['participation_fee'],
            final_payment=player.payoff.to_real_world_currency(session) + session.config['participation_fee'],
        )


class ProlificLink(Page):
    """
    This page redirects pp to prolific automatically with a javascript (don't forget to put paste the correct link!).
    There is a short text and the link in case it is not automatic.
    """
    @staticmethod
    def is_displayed(player: Player):
        if player.participant.is_dropout:
            return False
        elif player.round_number == C.NUM_ROUNDS:
            return True


page_sequence = [PairingWaitPage,
                 ReceiverChoice,
                 ResultsWaitPage,
                 Results,
                 # Demographics,
                 Comprehension,
                 CommentBox,
                 Payment,
                 ProlificLink]
