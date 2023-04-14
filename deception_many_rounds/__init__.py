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

    proba_low_stake = 0.75

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

    what_receiver_knows = models.StringField(
        choices=['Nothing', 'That one is worse for the Receiver', 'What the amounts are but not in which option'],
        verbose_name='What does the Receiver know about the Options?',
        widget=widgets.RadioSelect,
    )

    random_selection = models.StringField(
        initial='',
        choices=['randomise', 'whatever'],
    )

    def get_stake(player):
        if random.random() >= C.proba_low_stake:
            player.stake = "high"
            round_stake = player.stake
        else:
            player.stake = "low"
            round_stake = player.stake
        # print("stake is", player.stake)
        return round_stake

    def set_options(player):
        stake = player.get_stake()
        if stake == 'high':
            player.optionA_sender = C.optionA_sender_high
            player.optionA_receiver = C.optionA_receiver_high
            player.optionB_sender = C.optionB_sender_high
            player.optionB_receiver = C.optionB_receiver_high
            # print("options high")
        elif stake == 'low':
            player.optionA_sender = C.optionA_sender_low
            player.optionA_receiver = C.optionA_receiver_low
            player.optionB_sender = C.optionB_sender_low
            player.optionB_receiver = C.optionB_receiver_low
            # print("options low")

    def get_button_order(player):
        if random.random() > 0.5:
            return 1
        else:
            return 0


########  Functions #######

def random_payment(player: Player):
    randomly_selected_round = random.randint(1, C.NUM_ROUNDS)
    # print("chosen round", randomly_selected_round)
    me = player.in_round(randomly_selected_round)
    player.randomly_selected_round = randomly_selected_round
    player.participant.randomly_selected_round = randomly_selected_round
    randomly_selected_stake = me.stake
    player.randomly_selected_stake = randomly_selected_stake
    player.participant.randomly_selected_stake = randomly_selected_stake
    randomly_selected_message = me.message
    player.randomly_selected_message = randomly_selected_message
    player.participant.randomly_selected_message = randomly_selected_message
    # print('round is', randomly_selected_round)
    # print('stake is', randomly_selected_stake)
    # print('message is', randomly_selected_message)


######  PAGES  #########


class StakesPage(Page):

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

            call_stake=player.set_options(),
        )

    # def before_next_page(player, timeout_happened):
    #     me = player
    #     if timeout_happened:
    #         player.set_options()


class SenderMessage(Page):
    form_model = 'player'
    form_fields = ['message', 'better4you', 'better4receiver', 'what_receiver_knows']

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
        solutions = dict(better4you='Option B', better4receiver='Option A', what_receiver_knows='Nothing')

        # error_message can return a dict whose keys are field names and whose
        # values are error messages
        errors = {f: 'This answer is wrong' for f in solutions if values[f] != solutions[f]}
        # print('errors is', errors)
        if errors:
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


# class Results(Page):
#
#     timeout_seconds = 1  # instant timeout
#
#     @staticmethod
#     def is_displayed(player):
#         participant = player.participant
#         if participant.is_dropout:
#             return False
#         elif player.participant.role == 'Sender':
#             return True
#
#     def vars_for_template(player: Player):
#         participant = player.participant
#         return dict(
#             is_dropout=participant.is_dropout,
#             round_number=player.round_number,
#
#             # call_payoff=set_payoff(player),
#         )


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
        if player.participant.randomly_selected_message == 'Option A':
            return dict(
                player_in_all_rounds=player.in_all_rounds(),
                total_payoff=sum([p.payoff for p in player.in_all_rounds()]),
                best_option='Option A',
                worst_option='Option B',

                random_round=player.randomly_selected_round,
                message=player.randomly_selected_message,
            )
        else:
            return dict(
                player_in_all_rounds=player.in_all_rounds(),
                total_payoff=sum([p.payoff for p in player.in_all_rounds()]),
                best_option='Option B',
                worst_option='Option A',

                random_round=player.randomly_selected_round,
                message=player.randomly_selected_message,
            )


page_sequence = [
    # Consent,
    # Instructions,
    StakesPage,
    SenderMessage,
    # Results,
    RandomSelection,
    End,
    # Payment,
    # ProlificLink
]
