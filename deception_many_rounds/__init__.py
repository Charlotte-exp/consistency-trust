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

    comment_box = models.LongStringField(
        verbose_name=''
    )

    strategy_box = models.LongStringField(
        verbose_name=''
    )

    def get_stake(player):
        """
            This functions attributes the correct stake on the correct round.
            It is a deterministic system for set treatments.
            For each treatment I list exactly which stake I want on each round (list_round_stakes)
            The function selects the correct list based on participant treatment (attributed in the intro)
            The function is called every round ont he StakesPage.
            It returns the stake on the list that is a index round-1
        """
        list_round_stakes = []
        if player.participant.treatment == '2nd':
            list_round_stakes = ['low', 'high', 'low', 'low', 'low', 'low', 'low', 'low', 'low', 'low']
        elif player.participant.treatment == '9th':
            list_round_stakes = ['low', 'low', 'low', 'low', 'low', 'low', 'low', 'low', 'high', 'low']
        elif player.participant.treatment == 'none':
            list_round_stakes = ['low', 'low', 'low', 'low', 'low', 'low', 'low', 'low', 'low', 'low']

        round_stake = list_round_stakes[player.round_number - 1]
        player.stake = round_stake
        # print(player.participant.treatment)
        # print(list_round_stakes)
        # print(round_stake)
        return round_stake

    # def get_stake(player):
    #         """
    #             This functions randomly attributes stakes on each round.
    #             The system is binary and the probability can be changed under proba_low_stake
    #             The function compares the chosen probability to a randomly generated number
    #             Then it attributes either a high or low stake on that round
    #         """
    #     if random.random() >= C.proba_low_stake:
    #         player.stake = "high"
    #         round_stake = player.stake
    #     else:
    #         player.stake = "low"
    #         round_stake = player.stake
    #     # print("stake is", player.stake)
    #     return round_stake

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


def get_payoff(player: Player):
    if player.randomly_selected_stake == 'high':
        player.payoff = C.optionB_sender_high
    else:
        player.payoff = C.optionB_sender_low



######  PAGES  #########


class StakesPage(Page):

    timeout_seconds = 1  # instant timeout

    def vars_for_template(player: Player):
        participant = player.participant
        return dict(
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


class RandomSelection(Page):
    form_model = 'player'
    form_fields = ['random_selection']

    @staticmethod
    def is_displayed(player: Player):
        if player.round_number == C.NUM_ROUNDS:
            return True

    def vars_for_template(player: Player):
        return dict(
            player_in_all_rounds=player.in_all_rounds(),
            total_payoff=sum([p.payoff for p in player.in_all_rounds()]),

            call_payment=random_payment(player),
            call_payoff=get_payoff(player),
        )


# only need this if it is repeated rounds
class End(Page):

    @staticmethod
    def is_displayed(player: Player):
        if player.round_number == C.NUM_ROUNDS:
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


class CommentBox(Page):
    form_model = 'player'
    form_fields = ['comment_box', 'strategy_box']

    @staticmethod
    def is_displayed(player: Player):
        if player.round_number == C.NUM_ROUNDS:
            return True


class Payment(Page):

    @staticmethod
    def is_displayed(player: Player):
        if player.round_number == C.NUM_ROUNDS:
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
        if player.round_number == C.NUM_ROUNDS:
            return True


page_sequence = [
    # Consent,
    # Instructions,
    StakesPage,
    SenderMessage,
    # Results,
    RandomSelection,
    End,
    CommentBox,
    Payment,
    ProlificLink
]
