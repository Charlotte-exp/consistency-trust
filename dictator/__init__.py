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

    high_pot_money = cu(6)
    high_half_pot = high_pot_money / 2

    low_pot_money = cu(2)
    low_half_pot = low_pot_money / 2

    likelihood = 0.5
    values = [0.10, 0.5, 1]


class Subsession(BaseSubsession):
    pass


# def creating_session(subsession: Subsession):
#
#     treatments = itertools.cycle(['high-high', 'low-low'])
#     for player in subsession.get_players():
#         player.condition = next(treatments)
#         print('treatment', player.condition)
#
#     # for p in subsession.get_players():
#     #     p.participant.conversion = random.choice(Constants.values)
#     #     print(p.participant.conversion)


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    title = models.StringField()
    # condition = models.StringField()
    # conversion = models.FloatField()
    receiver_payoff = models.CurrencyField()

    decision = models.CurrencyField(
        choices=[
            [0, f'Take'],  # defect
            [1, f'Leave'],  # cooperate
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
    def set_payoffs(player):
        """  """
        # receiver = player.receiver_payoff
        if player.participant.condition == 'high':
            if player.decision == 0:
                player.payoff = Constants.high_pot_money
                player.receiver_payoff = 0
            else:
                player.payoff = Constants.high_half_pot
                player.receiver_payoff = Constants.high_half_pot
            print('Dictator payoff:', player.payoff)
            print('Receiver payoff:', player.receiver_payoff)
        else:
            if player.decision == 0:
                player.payoff = Constants.low_pot_money
                player.receiver_payoff = 0
            else:
                player.payoff = Constants.low_half_pot
                player.receiver_payoff = Constants.low_half_pot
            print('Dictator payoff:', player.payoff)
            print('Receiver payoff:', player.receiver_payoff)


#######    PAGES   #########
class Introduction(Page):
    pass


class Offer(Page):
    form_model = 'player'
    form_fields = ['decision']

    # def vars_for_template(player: Player):
    #     return dict(
    #         condition_sa_mere=player.participant.condition,
    #         high_pot=Constants.high_pot_money,
    #         low_pot=Constants.low_pot_money,
    #         high_half_pot=Constants.high_pot_money/2,
    #         low_half_pot=Constants.low_pot_money/2,
    #     )

    def vars_for_template(player: Player):
        if player.participant.condition == 'high':
            return dict(
                pot_money=Constants.high_pot_money,
                half_pot=Constants.high_half_pot,
            )
        else:
            return dict(
                pot_money=Constants.low_pot_money,
                half_pot=Constants.low_half_pot,
            )


# class ResultsWaitPage(WaitPage):
#     player.set_payoffs()
## why is it so fucking hard to call a function?? al the examples online use self! why did they fucking change it!!

class Results(Page):
    """
    This is the only way I found to call this fucking function... ask Nik how these work and how it should be done
    """
    # def vars_for_template(player: Player):
    #     dictator = player.group.get_player_by_id(1)
    #     return dict(
    #         call=player.set_payoffs(),
    #         payoff=player.payoff,
    #         my_player_id=player.id_in_subsession,
    #     )

    def vars_for_template(player: Player):
        if player.participant.condition == 'high':
            return dict(
                call=player.set_payoffs(),
                payoff=player.payoff,
                pot_money=Constants.high_pot_money,
                half_pot=Constants.high_half_pot,
            )
        else:
            return dict(
                call=player.set_payoffs(),
                payoff=player.payoff,
                pot_money=Constants.low_pot_money,
                half_pot=Constants.low_half_pot,
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
