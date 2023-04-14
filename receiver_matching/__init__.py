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

    left_hanging = models.BooleanField(initial=False)

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
            [1, 'A randomly selected one'],
            [2, 'all of them']
        ],
        verbose_name='Which message(s) was sent to the Receiver?',
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


def get_payoffs(player: Player):
    me = player
    partner = other_player(me)
    if me.participant.role == 'Sender':
        if me.participant.randomly_selected_stake == 'high':
            if partner.choice == 'Option A':
                me.payoff = C.optionA_sender_high
            else:
                me.payoff = C.optionB_sender_high
        else:
            if partner.choice == 'Option A':
                me.payoff = C.optionA_sender_low
            else:
                me.payoff = C.optionB_sender_low
        print('sender bonus is', me.payoff)
    elif me.participant.role == 'Receiver':
        if partner.participant.randomly_selected_stake == 'high':
            if me.choice == 'Option A':
                me.payoff = C.optionA_receiver_high
            else:
                me.payoff = C.optionB_receiver_high
        else:
            if me.choice == 'Option A':
                me.payoff = C.optionA_receiver_low
            else:
                me.payoff = C.optionB_receiver_low
        print('receiver bonus is', me.payoff)
    # print('my payoff', me.payoff)


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
            print('is dropout?', player.participant.is_dropout)
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
            partner.participant.is_dropout = False
            partner.left_hanging = True
            print("me is dropout?", me.participant.is_dropout)
            print(" partner is dropout?", partner.participant.is_dropout)
            me.choice = random.choice(['Option A', 'Option B'])


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs

    template_name = 'receiver_matching/ResultsWaitPage.html'

    # body_text = "Please wait for the Receiver to make their choice."

    # @staticmethod
    # def is_displayed(player):
    #     participant = player.participant
    #     if participant.is_dropout or player.left_hanging:
    #         return False

    def vars_for_template(player: Player):
            """  """
            participant = player.participant
            return dict(
                role=player.participant.role,
                is_dropout=participant.is_dropout,
                round_number=player.round_number,
            )


class Results(Page):

    # @staticmethod
    # def is_displayed(player: Player):
    #     if player.participant.is_dropout:
    #         return False
    #     # elif player.participant.role == 'Sender':
    #     #     return True
    #     # elif player.left_hanging:
    #     #     return True

    def vars_for_template(player: Player):
        """  """
        participant = player.participant
        return dict(
            role=player.participant.role,
            is_dropout=player.participant.is_dropout,
            left_hanging=player.left_hanging,
            round_number=player.round_number,
            payoff=player.payoff,
        )


class Demographics(Page):
    """ This page displays survey box to record participants' demographics. it's just made of simple form fields. """
    form_model = 'player'
    form_fields = ['age', 'gender', 'income', 'education', 'ethnicity']

    @staticmethod
    def is_displayed(player: Player):
        if player.left_hanging:
            return True
        elif not player.participant.is_dropout:
            return True
        else:
            return False


class Comprehension(Page):
    form_model = 'player'
    form_fields = ['q1', 'q2', 'q3']

    @staticmethod
    def is_displayed(player: Player):
        if player.left_hanging:
            return True
        elif not player.participant.is_dropout:
            return True
        else:
            return False


class CommentBox(Page):
    form_model = 'player'
    form_fields = ['comment_box']

    @staticmethod
    def is_displayed(player: Player):
        if player.left_hanging:
            return True
        elif not player.participant.is_dropout:
            return True
        else:
            return False


class Payment(Page):

    @staticmethod
    def is_displayed(player: Player):
        if player.left_hanging:
            return True
        elif not player.participant.is_dropout:
            return True
        else:
            return False

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
        if player.left_hanging:
            return True
        elif not player.participant.is_dropout:
            return True
        else:
            return False


page_sequence = [PairingWaitPage,
                 ReceiverChoice,
                 ResultsWaitPage,
                 Results,
                 # Demographics,
                 Comprehension,
                 CommentBox,
                 Payment,
                 ProlificLink]
