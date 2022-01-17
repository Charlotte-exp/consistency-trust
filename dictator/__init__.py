from otree.api import *

import itertools
import random


doc = """
Dictator game for the consistency project. 
perfect random matching
random token value
asymmetric token value
"""


class Constants(BaseConstants):
    name_in_url = 'dictator'
    players_per_group = None
    num_rounds = 2
    instructions_template = 'dictator/instructions.html'

    pot_money = cu(10)
    endowment_dictator = pot_money/2
    endowment_receiver = pot_money/2

    likelihood = 0.5
    values = [0.1, 0.5]


class Subsession(BaseSubsession):
    pass


def creating_session(subsession: Subsession):

    treatments = itertools.cycle(['high-high', 'low-low'])
    for player in subsession.get_players():
        player.condition = next(treatments)
        print('treatment', player.condition)

    # for p in subsession.get_players():
    #     p.participant.conversion = random.choice(Constants.values)
    #     print(p.participant.conversion)


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    title = models.StringField()
    condition = models.StringField()
    # conversion = models.FloatField()
    receiver_payoff = models.CurrencyField()

    decision = models.CurrencyField(
        choices=[
            [0, f'Take the {Constants.endowment_receiver} from the receiver.'],  # cooperate
            [1, f'Leave the {Constants.endowment_receiver} of the receiver'],  # defect
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

    being_receiver = models.StringField(
        choices=['Yes', 'No'],
        verbose_name='Would you like to be the receiver for another dictator?',
        widget=widgets.RadioSelect)


#######   FUNCTIONS   #######
def set_payoffs(player: Player):
    """  """
    if player.participant.condition == 'high-high':
        receiver = player.receiver_payoff
        if player.decision == 0:
            player.payoff = Constants.pot_money * Constants.values[1]
            receiver.payoff = 0 * Constants.values[1]
        else:
            player.payoff = Constants.endowment_dictator * Constants.values[1]
            receiver.payoff = Constants.endowment_receiver * Constants.values[1]
        print('Dictator payoff:', player.payoff)
        print('Receiver payoff:', receiver.payoff)
    if player.participant.condition == 'high-high':
        if player.participant.condition == 'high-high':
            receiver = player.receiver_payoff
            if player.decision == 0:
                player.payoff = Constants.pot_money * Constants.values[0]
                receiver.payoff = 0 * Constants.values[0]
            else:
                player.payoff = Constants.endowment_dictator * Constants.values[0]
                receiver.payoff = Constants.endowment_receiver * Constants.values[0]
            print('Dictator payoff:', player.payoff)
            print('Receiver payoff:', receiver.payoff)


#######    PAGES   #########
class Introduction(Page):
    pass


class Offer(Page):
    form_model = 'player'
    form_fields = ['decision']

    def vars_for_template(player: Player):
        return dict(
            my_player_id=player.id_in_subsession,
            currency_total=f'{Constants.values[0] * Constants.endowment_receiver:.0f}',
        )


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs


class Results(Page):

    def vars_for_template(player: Player):
        dictator = player.group.get_player_by_id(1)
        return dict(
            left=Constants.endowment_receiver - Constants.endowment_receiver,
            payoff=player.payoff,
            my_player_id=player.id_in_subsession,
        )


class End(Page):

    @staticmethod
    def is_displayed(player: Player):
        if player.round_number == Constants.num_rounds:
            return True

    def vars_for_template(player: Player):
        return dict(
            player_in_all_rounds=player.in_all_rounds(),
            total_payoff=sum([p.payoff for p in player.in_all_rounds()]),
        )

    # def vars_for_template(player: Player):
    #     opponent = player.get_others_in_group()[0]
    #     print(sum([p.payoff for p in player.in_all_rounds()]))
    #     print(sum([p.payoff for p in opponent.in_all_rounds()]))
    #     p1 = player.group.get_player_by_id(1)
    #     p2 = player.group.get_player_by_id(2)
    #     return dict(
    #         player_in_all_rounds=player.in_all_rounds(),
    #         p1_total_payoff=sum([p.payoff for p in player.in_all_rounds()]),
    #         p2_total_payoff=sum([p.payoff for p in player.in_all_rounds()]),
    #         my_total_payoff=sum([p.payoff for p in p1.in_all_rounds()]),
    #         opponent_total_payoff=sum([p.payoff for p in p2.in_all_rounds()]),
    #         partner=opponent,
    #         my_player_id=player.id_in_subsession,
    #         opponent_id=opponent.id_in_subsession,
    #     )


# class BeingReceiver(Page):
#     form_model = 'player'
#     form_fields = ['being_receiver']
#
#     @staticmethod
#     def is_displayed(player: Player):
#         if player.round_number == Constants.num_rounds:
#             return True


class Demographics(Page):
    """ This page displays survey box to record pp's demographics. it's just made of simple form fields. """
    form_model = 'player'
    form_fields = ['age', 'gender', 'income', 'education', 'ethnicity']

    @staticmethod
    def is_displayed(player: Player):
        if player.round_number == Constants.num_rounds:
            return True


class CommentBox(Page):
    form_model = 'player'
    form_fields = ['comment_box', 'being_receiver']

    @staticmethod
    def is_displayed(player: Player):
        if player.round_number == Constants.num_rounds:
            return True


class Payment(Page):

    @staticmethod
    def is_displayed(player: Player):
        if player.round_number == Constants.num_rounds:
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
        return player.round_number == Constants.num_rounds


page_sequence = [Offer,
                 # ResultsWaitPage,
                 Results,
                 End,
                 Demographics,
                 CommentBox,
                 Payment,
                 ProlificLink]
