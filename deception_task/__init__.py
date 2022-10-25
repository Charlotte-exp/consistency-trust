from otree.api import *

import random
import itertools

doc = """
Deception task
multi round
multi treatment
"""


class C(BaseConstants):
    NAME_IN_URL = 'deception_task'
    PLAYERS_PER_GROUP = 6
    NUM_ROUNDS = 3

    optionA_sender_high = cu(0.5)
    optionA_receiver_high = cu(1.5)
    optionB_sender_high = cu(1.5)
    optionB_receiver_high = cu(0.5)

    optionA_sender_low = cu(0.5)
    optionA_receiver_low = cu(0.6)
    optionB_sender_low = cu(0.6)
    optionB_receiver_low = cu(0.5)


class Subsession(BaseSubsession):

    def get_treatments(self):
        items = [1, 2, 3, 4]
        random_item = random.choice(items)
        if random_item == 1:
            return 'high_high_high'
        elif random_item == 2:
            return 'high_high_low'
        elif random_item == 3:
            return 'high_low_high'
        elif random_item == 4:
            return 'high_low_low'


class Group(BaseGroup):
    # pass
    stake = models.StringField()

    # choice = models.StringField(
    #     initial='',
    #     choices=['Option A', 'Option B'],
    #     doc="""This player's decision""",
    #     verbose_name='Your choice:',
    #     widget=widgets.RadioSelect
    # )


class Player(BasePlayer):
    optionA_sender = models.CurrencyField()
    optionA_receiver = models.CurrencyField()
    optionB_sender = models.CurrencyField()
    optionB_receiver = models.CurrencyField()
    # stake = models.StringField()

    treatment = models.StringField()
    partner = models.IntegerField()
    left_hanging = models.IntegerField(initial=0)
    missing_bonus = models.CurrencyField(initial=0)

    message = models.StringField(
        initial='',
        choices=['Option A', 'Option B'],
    )

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
            [1, 'Yes'],
            [2, 'No']
        ],
        verbose_name='Did both player know that the Receiver would never learn the bonuses from the option not chosen?',
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
            [1, 'Yes'],
            [2, 'No']
        ],
        verbose_name='Did the bonuses from each option have to be the same for both participant?',
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

    def set_round_stakes(player):
        list_round_stakes = []
        if player.participant.treatment == 'high_high_high':
            list_round_stakes = ['high', 'high', 'high']
        elif player.participant.treatment == 'high_high_low':
            list_round_stakes = ['high', 'high', 'low']
        elif player.participant.treatment == 'high_low_high':
            list_round_stakes = ['high', 'low', 'high']
        elif player.participant.treatment == 'high_low_low':
            list_round_stakes = ['high', 'low', 'low']

        round_stake = list_round_stakes[player.round_number - 1]
        player.group.stake = round_stake
        # print(player.participant.treatment)
        # print(list_round_stakes)
        # print(round_stake)
        return round_stake

    def get_button_order(player):
        if random.random() > 0.5:
            return 1
        else:
            return 0

    def set_missing_bonus(player):
        if player.left_hanging == 1:
            if player.set_round_stakes() == 'high':
                player.missing_bonus = C.optionA_receiver_high
                player.payoff = player.missing_bonus
                print('missing bonus', player.missing_bonus)
                print('payoff', player.payoff)
            else:
                player.missing_bonus = C.optionA_receiver_low
                player.payoff = player.missing_bonus
                print('missing bonus', player.missing_bonus)
                print('payoff', player.payoff)


########  Functions #######


def group_by_arrival_time_method(subsession, waiting_players):
    senders = [p for p in waiting_players if p.participant.role == 'Sender']
    receivers = [p for p in waiting_players if p.participant.role == 'Receiver']
    if len(senders) >= 3 and len(receivers) >= 3:
        players = [senders[0], receivers[0], senders[1], receivers[1], senders[2], receivers[2]]
        treatment = subsession.get_treatments()
        for p in players:
            p.participant.treatment = treatment
            p.treatment = p.participant.treatment
        return players


def get_partner(player: Player):
    """
    We have group of 6 participants who switch partner on each round.
    We create a dictionary (matches) that matches the correct partner with each player.
    We create a list of all the possible partners in the group (so 3 players without oneself).
    Then for each player, we pick the matching partners from the dic and the 3 other players,
    and the id that match in both lists make the new partners list.
    """
    matches_round1 = {1: [2], 2: [1], 3: [4], 4: [3], 5: [6], 6: [5]}
    matches_round2 = {1: [4], 2: [5], 3: [6], 4: [1], 5: [2], 6: [3]}
    matches_round3 = {1: [6], 2: [3], 3: [2], 4: [5], 5: [4], 6: [1]}
    list_partners = player.get_others_in_group()
    # print(player.id_in_group)
    if player.round_number == 1:
        for partner_id in matches_round1[player.id_in_group]:  # picks the two partners from the matches dict
            for partner in list_partners:
                if partner.id_in_group == partner_id:
                    # print(partner.id_in_group)
                    player.partner = partner_id
                    return partner
    elif player.round_number == 2:
        for partner_id in matches_round2[player.id_in_group]:
            for partner in list_partners:
                if partner.id_in_group == partner_id:
                    # print(partner.id_in_group)
                    player.partner = partner_id
                    return partner
    elif player.round_number == 3:
        for partner_id in matches_round3[player.id_in_group]:
            for partner in list_partners:
                if partner.id_in_group == partner_id:
                    # print(partner.id_in_group)
                    player.partner = partner_id
                    return partner


def set_options(group: Group):
    for p in group.get_players():
        get_options(p)


def get_options(player: Player):
    if player.set_round_stakes() == 'high':
        player.optionA_sender = C.optionA_sender_high
        player.optionA_receiver = C.optionA_receiver_high
        player.optionB_sender = C.optionB_sender_high
        player.optionB_receiver = C.optionB_receiver_high
    else:
        player.optionA_sender = C.optionA_sender_low
        player.optionA_receiver = C.optionA_receiver_low
        player.optionB_sender = C.optionB_sender_low
        player.optionB_receiver = C.optionB_receiver_low


def set_payoffs(group: Group):
    for p in group.get_players():
        get_payoffs(p)


def get_payoffs(player: Player):
    me = player
    partner = get_partner(me)
    if me.left_hanging == 1:
        # partner.payoff = cu(0)
        me.payoff = me.missing_bonus
    elif me.left_hanging == 2:
        me.payoff = cu(0)
        # partner.payoff = partner.missing_bonus
    elif me.participant.role == 'Receiver':
        if me.choice == 'Option A':
            partner.payoff = partner.optionA_sender
            me.payoff = me.optionA_receiver
        elif me.choice == 'Option B':
            partner.payoff = partner.optionB_sender
            me.payoff = me.optionB_receiver
    elif me.participant.role == 'Sender':
        if partner.choice == 'Option A':
            me.payoff = me.optionA_sender
            partner.payoff = partner.optionA_receiver
        elif me.choice == 'Option B':
            me.payoff = partner.optionB_sender
            partner.payoff = me.optionB_receiver


######  PAGES  #########

class PairingWaitPage(WaitPage):
    group_by_arrival_time = True

    def is_displayed(player: Player):
        return player.round_number == 1

    template_name = 'deception_task/Waitroom.html'


class StakesWaitPage(WaitPage):
    after_all_players_arrive = set_options

    template_name = 'deception_task/StakesWaitPage.html'
    # body_text = "Please wait for the Receiver to make their choice."


class SenderMessage(Page):
    form_model = 'player'
    form_fields = ['message']

    @staticmethod
    def is_displayed(player):
        if player.left_hanging == 1 or player.left_hanging == 2:
            return False
        elif player.participant.role == 'Sender':
            return True

    def vars_for_template(player: Player):
        """  """
        me = player
        partner = get_partner(me)
        return dict(
            # role=player.role,
            sender_optionA=player.optionA_sender,
            receiver_optionA=player.optionA_receiver,
            sender_optionB=player.optionB_sender,
            receiver_optionB=player.optionB_receiver,

            player=player.id_in_group,
            partner=partner.id_in_group,

            call_stakes=player.set_round_stakes(),
        )

    timer_text = 'If you stay inactive for too long you will be considered a dropout:'

    @staticmethod
    def get_timeout_seconds(player):
        participant = player.participant

        if participant.is_dropout:
            return 1  # instant timeout, 1 second
        else:
            return 0.5 * 60

    def before_next_page(player, timeout_happened):
        """
        Dropout check code! If the timer set above runs out, all the other players in the group become left_hanging = 1
        and are jumped to the leftHanging page with a link to Prolific. The dropout also goes to that page but gets
        a different text (left_hanging = 2).
        Decisions for the missed round are automatically filled to avoid an NONE type error.
        """
        me = player
        partner = get_partner(me)
        if timeout_happened:
            me.participant.is_dropout = True
            print(me.participant.is_dropout)
            partner.left_hanging = 1
            me.left_hanging = 2
            me.message = 'None'


class MessageWaitPage(WaitPage):
    template_name = 'deception_task/MessageWaitPage.html'

    # body_text = "Please wait for the Sender to send his message."

    @staticmethod
    def is_displayed(player):
        if player.left_hanging == 1 or player.left_hanging == 2:
            return False
        elif player.participant.role == 'Receiver':
            return True


class ReceiverChoice(Page):
    form_model = 'player'
    form_fields = ['choice']

    @staticmethod
    def is_displayed(player):
        if player.left_hanging == 1 or player.left_hanging == 2:
            return False
        elif player.participant.role == 'Receiver':
            return True

    def vars_for_template(player: Player):
        """  """
        me = player
        partner = get_partner(me)
        if partner.message == 'Option A':
            return dict(
                other_player=partner.id_in_group,
                player=player.id_in_group,
                best_option='Option A',
                worst_option='Option B',

                button=player.get_button_order(),
            )
        else:
            return dict(
                other_player=partner.id_in_group,
                player=player.id_in_group,
                best_option='Option B',
                worst_option='Option A',

                button=player.get_button_order(),
            )

    timer_text = 'If you stay inactive for too long you will be considered a dropout:'

    @staticmethod
    def get_timeout_seconds(player):
        participant = player.participant

        if participant.is_dropout:
            return 1  # instant timeout, 1 second
        else:
            return 0.5 * 60

    def before_next_page(player, timeout_happened):
        """
        Dropout check code! If the timer set above runs out, all the other players in the group become left_hanging = 1
        and are jumped to the leftHanging page with a link to Prolific. The dropout also goes to that page but gets
        a different text (left_hanging = 2).
        Decisions for the missed round are automatically filled to avoid an NONE type error.
        """
        me = player
        partner = get_partner(me)
        if timeout_happened:
            me.participant.is_dropout = True
            print(me.participant.is_dropout)
            partner.left_hanging = 1
            me.left_hanging = 2
            me.choice = 'None'
            partner.choice = 'None'


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs

    template_name = 'deception_task/ResultsWaitPage.html'

    # body_text = "Please wait for the Receiver to make their choice."

    @staticmethod
    def is_displayed(player):
        if player.left_hanging == 1 or player.left_hanging == 2:
            return False
        elif player.participant.role == 'Sender' or player.participant.role == 'Receiver':
            return True


class Results(Page):

    @staticmethod
    def is_displayed(player):
        if player.left_hanging == 1 or player.left_hanging == 2:
            return False
        else:
            return True

    def vars_for_template(player: Player):
        """  """
        me = player
        partner = get_partner(me)
        if me.participant.role == 'Receiver':
            return dict(
                left_hanging=player.left_hanging,
                missing_bonus=player.missing_bonus,

                choice=me.choice,
                payoff=me.payoff,
                role=me.participant.role,

                player=player.id_in_group,
                partner=partner.id_in_group,
            )
        else:
            return dict(
                left_hanging=player.left_hanging,
                missing_bonus=player.missing_bonus,

                choice=partner.choice,
                payoff=me.payoff,
                role=me.participant.role,

                player=player.id_in_group,
                partner=partner.id_in_group,
            )

    # only need this if it is repeated rounds
    timer_text = 'If you stay inactive for too long you will be considered a dropout:'
    timeout_seconds = 12 * 60


class LeftHanging(Page):
    """
    This page is for dropouts. If a participant quits after the waitroom there is a timer on the results
    and decision page that redirect them to this page. Here depending on who left and who was left hanging,
    they get a different message (based on their left_hanging value).
    The left-hanging pp get a link to go back to Prolific (don't forget to paste the correct link!).
    """

    @staticmethod
    def is_displayed(player):
        """ This page is displayed only if the player is either left hanging (1) or a dropout (2)."""
        if player.left_hanging == 2:
            return True

    @staticmethod
    def get_timeout_seconds(player):
        participant = player.participant

        if participant.is_dropout:
            return 0.5 * 60  # quick timeout so doesn't hold the others too long
        else:
            return 2 * 60

    def vars_for_template(player: Player):
        """  """
        me = player
        partner = get_partner(me)
        if me.participant.role == 'Receiver':
            return dict(
                call_missing_bonus=player.set_missing_bonus(),

                payoff=me.payoff,
                role=me.participant.role,
                left_hanging=player.left_hanging,
                missing_bonus=player.missing_bonus,

                player=player.id_in_group,
                partner=partner.id_in_group,
            )
        else:
            return dict(
                call_missing_bonus=player.set_missing_bonus(),

                payoff=me.payoff,
                role=me.participant.role,
                left_hanging=player.left_hanging,
                missing_bonus=player.missing_bonus,

                player=player.id_in_group,
                partner=partner.id_in_group,
            )


# only need this if it is repeated rounds
class End(Page):

    @staticmethod
    def is_displayed(player: Player):
        if player.participant.is_dropout:
            return False
        elif player.round_number == C.NUM_ROUNDS:
            return True

    def vars_for_template(player: Player):
        return dict(
            player_in_all_rounds=player.in_all_rounds(),
            total_payoff=sum([p.payoff for p in player.in_all_rounds()]),
            left_hanging_score=sum([p.left_hanging for p in player.in_all_rounds()]),
            missing_bonus=player.missing_bonus,
        )


class Demographics(Page):
    """ This page displays survey box to record participants' demographics. it's just made of simple form fields. """
    form_model = 'player'
    form_fields = ['age', 'gender', 'income', 'education', 'ethnicity']

    @staticmethod
    def is_displayed(player: Player):
        if player.participant.is_dropout:
            return False
        elif player.round_number == C.NUM_ROUNDS:
            return True


class Comprehension(Page):
    form_model = 'player'
    form_fields = ['q1', 'q2', 'q3']

    @staticmethod
    def is_displayed(player: Player):
        if player.participant.is_dropout:
            return False
        elif player.round_number == C.NUM_ROUNDS:
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
        elif player.round_number == C.NUM_ROUNDS:
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
        if player.participant.is_dropout:
            return False
        elif player.round_number == C.NUM_ROUNDS:
            return True


page_sequence = [PairingWaitPage,
                 StakesWaitPage,
                 SenderMessage,
                 MessageWaitPage,
                 ReceiverChoice,
                 ResultsWaitPage,
                 Results,
                 LeftHanging,
                 End,
                 # Demographics,
                 # Comprehension,
                 # CommentBox,
                 Payment,
                 ProlificLink]
