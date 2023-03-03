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


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    optionA_sender = models.CurrencyField(initial=cu(0))
    optionA_receiver = models.CurrencyField(initial=cu(0))
    optionB_sender = models.CurrencyField(initial=cu(0))
    optionB_receiver = models.CurrencyField(initial=cu(0))
    stake = models.StringField(initial='')

    random_round = models.IntegerField()
    random_payment = models.CurrencyField()

    message = models.StringField(
        initial='',
        choices=['Option A', 'Option B'],
    )

    saliency = models.StringField(
        choices=['Option A', 'Option B'],
        verbose_name='Which Option is better for YOU?',
        widget=widgets.RadioSelect,
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
            random_payoff = me.payoff
            player.random_payment = random_payoff
            random_round = round_
            player.random_round = random_round

    print('payment is', player.random_payment)


######  PAGES  #########

class StakesPage(Page):

    timeout_seconds = 2  # instant timeout

    def vars_for_template(player: Player):
        participant = player.participant
        return dict(
            is_dropout=participant.is_dropout,
            round_number=player.round_number,

            # call_stake=player.set_options(),
        )


class SenderMessage(Page):
    form_model = 'player'
    form_fields = ['message', 'saliency']

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
    def get_timeout_seconds(player):
        participant = player.participant
        if participant.is_dropout:
            return 1  # instant timeout, 1 second
        else:
            return 12 * 60

    def before_next_page(player, timeout_happened):
        """
        Dropout check code! If the timer set above runs out, all the other players in the group become left_hanging = 1
        and are jumped to the leftHanging page with a link to Prolific. The dropout also goes to that page but gets
        a different text (left_hanging = 2).
        Decisions for the missed round are automatically filled to avoid an NONE type error.
        """
        me = player
        if timeout_happened:
            me.participant.is_dropout = True
            me.message = 'dropout'


class Results(Page):

    timeout_seconds = 2  # instant timeout

    def vars_for_template(player: Player):
        participant = player.participant
        return dict(
            is_dropout=participant.is_dropout,
            round_number=player.round_number,

            call_payoff=set_payoff(player),
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

            random_round=player.random_round,
            payment=player.random_payment,

            call_payment=random_payment(player),
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
            bonus=player.random_payment.to_real_world_currency(session),
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


page_sequence = [StakesPage,
                 SenderMessage,
                 Results,
                 End,
                 # Demographics,
                 Comprehension,
                 CommentBox,
                 Payment,
                 ProlificLink]
