from otree.api import *

import random

doc = """
Deception task over many rounds
not interactive - just the sender
"""


class C(BaseConstants):
    NAME_IN_URL = 'Task_01'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 10

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
    optionA_sender = models.CurrencyField(initial=cu(0))
    optionA_receiver = models.CurrencyField(initial=cu(0))
    optionB_sender = models.CurrencyField(initial=cu(0))
    optionB_receiver = models.CurrencyField(initial=cu(0))

    stake = models.StringField(initial='')
    num_failed_attempts = models.IntegerField(initial=0)

    randomly_selected_round = models.IntegerField(initial=0)
    randomly_selected_stake = models.StringField(initial='')
    randomly_selected_message = models.StringField(initial='')

    message = models.StringField(
        initial='',
        choices=['Option A', 'Option B'],
    )

    better4you = models.StringField(
        choices=['Option A', 'Option B'],
        verbose_name='Which Option is better for YOU?',
        widget=widgets.RadioSelect,
    )

    better4receiver = models.StringField(
        choices=['Option A', 'Option B'],
        verbose_name='Which Option is better for the RECEIVER?',
        widget=widgets.RadioSelect,
    )

    random_selection = models.StringField(
        initial='',
        choices=['randomise', 'whatever'],
    )

    def get_stake(player):
        if random.random() > 0.5:
            print("stake high")
            player.stake = "high"
            round_stake = player.stake
        else:
            print("stake low")
            player.stake = "low"
            round_stake = player.stake
        return round_stake

    def set_options(player):
        if player.get_stake() == 'high':
            player.optionA_sender = C.optionA_sender_high
            player.optionA_receiver = C.optionA_receiver_high
            player.optionB_sender = C.optionB_sender_high
            player.optionB_receiver = C.optionB_receiver_high
            print("options high")
        elif player.get_stake() == 'low':
            player.optionA_sender = C.optionA_sender_low
            player.optionA_receiver = C.optionA_receiver_low
            player.optionB_sender = C.optionB_sender_low
            player.optionB_receiver = C.optionB_receiver_low
            print("options low")

    def get_button_order(player):
        if random.random() > 0.5:
            return 1
        else:
            return 0


########  Functions #######

def set_payoff(player: Player):
    if player.message == 'Option A':
        player.payoff = player.optionA_sender
    elif player.message == 'Option B':
        player.payoff = player.optionB_sender
    print('payoff is', player.payoff)


def random_payment(player: Player):
    # random_payoff = random.choice([p.payoff for p in player.in_all_rounds()])
    #
    # player.random_payoff = random_payoff
    # print([p.payoff for p in player.in_all_rounds()])
    print("fuck")
    random_round_number = random.randint(1, C.NUM_ROUNDS)
    for round_ in range(1, C.NUM_ROUNDS):
        me = player.in_round(round_)
        if random_round_number == round_:
            randomly_selected_round = round_
            player.randomly_selected_round = randomly_selected_round
            player.participant.randomly_selected_round = randomly_selected_round
            randomly_selected_stake = me.stake
            player.randomly_selected_stake = randomly_selected_stake
            player.participant.randomly_selected_stake = randomly_selected_stake
            randomly_selected_message = me.message
            player.randomly_selected_message = randomly_selected_message
            player.participant.randomly_selected_message = randomly_selected_message
    print('round is', randomly_selected_round)
    print('stake is', randomly_selected_stake)
    print('message is', randomly_selected_message)


######  PAGES  #########

# class Consent(Page):
#
#     def is_displayed(player: Player):
#         if player.round_number == 1:
#             return True
#
#     def vars_for_template(player: Player):
#         return {
#             'participation_fee': player.session.config['participation_fee'],
#         }
#
#
# class Instructions(Page):
#
#     def is_displayed(player: Player):
#         if player.round_number == 1:
#             return True
#
#     def vars_for_template(player: Player):
#         """  """
#         return dict(
#             # role=player.role,
#             sender_optionA=C.optionA_sender_high,
#             receiver_optionA=C.optionA_receiver_high,
#             sender_optionB=C.optionB_sender_high,
#             receiver_optionB=C.optionB_receiver_high,
#         )


class StakesPage(Page):

    timeout_seconds = 2  # instant timeout

    @staticmethod
    def is_displayed(player):
        participant = player.participant
        if participant.is_dropout:
            return False
        elif player.participant.role == 'Sender':
            return True

    def vars_for_template(player: Player):
        participant = player.participant
        return dict(
            is_dropout=participant.is_dropout,
            round_number=player.round_number,

            # call_stake=player.set_options(),
        )


class SenderMessage(Page):
    form_model = 'player'
    form_fields = ['message', 'better4you', 'better4receiver']

    @staticmethod
    def is_displayed(player):
        participant = player.participant
        if participant.is_dropout:
            return False
        elif player.participant.role == 'Sender':
            return True

    def vars_for_template(player: Player):
        """  """
        return dict(
            call_stake=player.set_options(),

            sender_optionA=player.optionA_sender,
            receiver_optionA=player.optionA_receiver,
            sender_optionB=player.optionB_sender,
            receiver_optionB=player.optionB_receiver,
            round_number=player.round_number,
        )

    timer_text = 'If you stay inactive for too long you will be considered a dropout:'

    @staticmethod
    def error_message(player: Player, values):
        # alternatively, you could make quiz1_error_message, quiz2_error_message, etc.
        # but if you have many similar fields, this is more efficient.
        solutions = dict(better4you='Option B', better4receiver='Option A')

        # error_message can return a dict whose keys are field names and whose
        # values are error messages
        errors = {f: 'This answer is wrong' for f in solutions if values[f] != solutions[f]}
        # print('errors is', errors)
        if errors and player.round_number == 1:
            player.num_failed_attempts += 1
            return errors

    # @staticmethod
    # def get_timeout_seconds(player):
    #     participant = player.participant
    #     if participant.is_dropout:
    #         return 1  # instant timeout, 1 second
    #     else:
    #         return 12 * 60
    #
    # def before_next_page(player, timeout_happened):
    #     """
    #     Dropout check code! If the timer set above runs out, all the other players in the group become left_hanging = 1
    #     and are jumped to the leftHanging page with a link to Prolific. The dropout also goes to that page but gets
    #     a different text (left_hanging = 2).
    #     Decisions for the missed round are automatically filled to avoid an NONE type error.
    #     """
    #     me = player
    #     if timeout_happened:
    #         me.participant.is_dropout = True
    #         me.message = 'dropout'


class Results(Page):

    timeout_seconds = 1  # instant timeout

    @staticmethod
    def is_displayed(player):
        participant = player.participant
        if participant.is_dropout:
            return False
        elif player.participant.role == 'Sender':
            return True

    def vars_for_template(player: Player):
        participant = player.participant
        return dict(
            is_dropout=participant.is_dropout,
            round_number=player.round_number,

            call_payoff=set_payoff(player),
        )


class RandomSelection(Page):
    form_model = 'player'
    form_fields = ['random_selection']

    @staticmethod
    def is_displayed(player: Player):
        if player.participant.is_dropout:
            return False
        elif player.participant.role == 'Sender' and player.round_number == C.NUM_ROUNDS:
            return True

    def vars_for_template(player: Player):
        return dict(
            player_in_all_rounds=player.in_all_rounds(),
            total_payoff=sum([p.payoff for p in player.in_all_rounds()]),
            #
            # random_round=player.randomly_selected_round,
            # message=player.randomly_selected_message,

            call_payment=random_payment(player),
        )


# only need this if it is repeated rounds
class End(Page):

    @staticmethod
    def is_displayed(player: Player):
        if player.participant.is_dropout:
            return False
        elif player.participant.role == 'Sender' and player.round_number == C.NUM_ROUNDS:
            return True

    def vars_for_template(player: Player):
        return dict(
            player_in_all_rounds=player.in_all_rounds(),
            total_payoff=sum([p.payoff for p in player.in_all_rounds()]),

            random_round=player.randomly_selected_round,
            message=player.randomly_selected_message,
        )


page_sequence = [
    # Consent,
    # Instructions,
    StakesPage,
    SenderMessage,
    Results,
    RandomSelection,
    End,
    # Payment,
    # ProlificLink
]
