from otree.api import *

import itertools


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'Start'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 1

    #SENDER_ROLE = 'Sender'
    #RECEIVER_ROLE = 'Receiver'

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


def creating_session(subsession: Subsession):
    """
    AWe use itertools to assign treatment regularly to make sure there is a somewhat equal amount of each in the
    session but also that is it equally distributed in the sample. (So pp don't have to wait to long get matched
    in a pair. It simply cycles through the list of treatments (high & low) and that's saved in the participant vars.
    """
    treatments = itertools.cycle(['2nd', '9th', 'none'])
    for p in subsession.get_players():
        p.treatment = next(treatments)
        p.participant.treatment = p.treatment
        # print('treatment is', p.treatment)
        # print('vars treatment is', p.participant.treatment)

# def creating_session(subsession: Subsession):
#     for p in subsession.get_players():
#         p.participant.role = p.role
#         # print('roles', p.role, p.participant.role)
#         p.participant.is_dropout = False
#         # print(p.participant.is_dropout)


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    treatment = models.StringField(initial='')
    num_failed_attempts = models.IntegerField(initial=0)

    message_test = models.StringField(
        initial='',
        choices=['Option A', 'Option B'],
    )

    choice = models.StringField(
        initial='',
        choices=['Option A', 'Option B'],
        verbose_name='Your choice:',
        widget=widgets.RadioSelect
    )

    q1_failed_attempts = models.IntegerField(initial=0)
    q2_failed_attempts = models.IntegerField(initial=0)
    q3_failed_attempts = models.IntegerField(initial=0)
    q4_failed_attempts = models.IntegerField(initial=0)

    a1 = models.IntegerField(
        choices=[
            [1, '112'],
            [2, '911'],
            [3, '000'],
            [4, '999'],
        ],
        verbose_name='Which of these phone numbers connects you to emergency services?',
        widget=widgets.RadioSelect
    )

    a2 = models.IntegerField(
        choices=[
            [1, 'Eggs'],
            [2, 'Muesli'],
            [3, 'Bakes beans'],
            [4, 'Sausages']
        ],
        verbose_name='Which ingredient is not part of a typical full English breakfast?',
        widget=widgets.RadioSelect
    )

    a3 = models.IntegerField(
        choices=[
            [1, 'Lei-che-ster'],
            [2, 'Lei-ce-ster'],
            [3, 'Le-ster'],
            [4, 'Le-zter']
        ],
        verbose_name='What is the correct pronunciation of the City of Leicester?',
        widget=widgets.RadioSelect
    )

    q1 = models.IntegerField(
        choices=[
            [1, 'Yes, the set of Options are the same in every round.'],
            [2, 'No there are two possible sets of Options.'],
            #[3, 'No, there are different set of Options on each round.']
        ],
        verbose_name='Does the Receiver see the same set of Options in every round?',
        widget=widgets.RadioSelect
    )
    q2 = models.IntegerField(
        choices=[
            [1, 'One round is selected at random and that message is sent.'],
            [2, 'Each message from every round is sent.']
        ],
        verbose_name='Which message(s) is sent to the Receiver?',
        widget=widgets.RadioSelect
    )

    q3 = models.IntegerField(
        choices=[
            [1, 'Yes, the two have to match.'],
            [2, 'No, the Receiver is free to ignore the message.']
        ],
        verbose_name='Does the Receiver have to chose the same option as the Sender recommended?',
        widget=widgets.RadioSelect
    )

    q4 = models.IntegerField(
        choices=[
            [1, 'Only their own final bonus and not the one of the Sender.'],
            [2, "Both their own and the Sender's final bonus."],
            [3, "Both their own and the Sender's final bonus, as well as the bonus of the option not chosen."],
        ],
        verbose_name='What does the Receiver know about the bonuses in the end?',
        widget=widgets.RadioSelect
    )


# PAGES
class Consent(Page):

    def vars_for_template(player: Player):
        return {
            'participation_fee': player.session.config['participation_fee'],
        }


class AttentionChecks(Page):
    form_model = 'player'
    form_fields = ['a1', 'a2', 'a3']

    @staticmethod
    def error_message(player: Player, values):
        """
        function from oTree
        I removed the "return errors" so that participant do not know if they did it right or wrong
        I also record whether they got at least one Q wrong per page submission, not how many wrong.
        """
        # alternatively, you could make quiz1_error_message, quiz2_error_message, etc.
        # but if you have many similar fields, this is more efficient.
        solutions = dict(a1=4, a2=2, a3=3)

        # error_message can return a dict whose keys are field names and whose
        # values are error messages
        errors = {f: 'This answer is wrong' for f in solutions if values[f] != solutions[f]}
        # print('errors is', errors)
        if errors:
            player.num_failed_attempts += 1
            #return errors


class Instructions(Page):
    """
    General instructions of the deception task.
    For all roles
    """
    def vars_for_template(player: Player):
        """  """
        return dict(
            # role=player.role,
            sender_optionA=C.optionA_sender_high,
            receiver_optionA=C.optionA_receiver_high,
            sender_optionB=C.optionB_sender_high,
            receiver_optionB=C.optionB_receiver_high,
        )


class InstruReceiver(Page):
    """
    Instructions about what the Receiver sees and does.
    """
    form_model = 'player'
    form_fields = ['q3']

    @staticmethod
    def error_message(player: Player, values):
        """
        function from oTree
        I record for each questions how many times they got it wrong and tell the participants when they got it wrong.
        They can only continue when all are correct
        """
        if values['q3'] != 2:
            player.q3_failed_attempts += 1
            return 'Answer to question 3 is incorrect. Check the instructions again and give a new answer'


    # @staticmethod
    # def is_displayed(player: Player):
    #     if player.role == C.SENDER_ROLE:
    #         return True


class InstruSender(Page):
    """
    Instructions about what the Sender knows and does.
    """
    form_model = 'player'
    form_fields = ['q4']

    def vars_for_template(player: Player):
        """  """
        return dict(
            # role=player.role,
            sender_optionA_high=C.optionA_sender_high,
            receiver_optionA_high=C.optionA_receiver_high,
            sender_optionB_high=C.optionB_sender_high,
            receiver_optionB_high=C.optionB_receiver_high,

            sender_optionA_low=C.optionA_sender_low,
            receiver_optionA_low=C.optionA_receiver_low,
            sender_optionB_low=C.optionB_sender_low,
            receiver_optionB_low=C.optionB_receiver_low,
        )


    @staticmethod
    def error_message(player: Player, values):
        """
        function from oTree
        I record for each questions how many times they got it wrong and tell the participants when they got it wrong.
        They can only continue when all are correct
        """
        if values['q4'] != 1:
            player.q4_failed_attempts += 1
            return 'Answer to question 4 is incorrect. Check the instructions again and give a new answer'


    # @staticmethod
    # def is_displayed(player: Player):
    #     if player.role == C.SENDER_ROLE:
    #         return True


class InstruRepeated(Page):
    """
    Instructions about repeated rounds and random rounds selection.
    Bonus options displayed
    Sender only!
    """
    form_model = 'player'
    form_fields = ['q1', 'q2']

    def vars_for_template(player: Player):
        """  """
        return dict(
            # role=player.role,
            sender_optionA_high=C.optionA_sender_high,
            receiver_optionA_high=C.optionA_receiver_high,
            sender_optionB_high=C.optionB_sender_high,
            receiver_optionB_high=C.optionB_receiver_high,

            sender_optionA_low=C.optionA_sender_low,
            receiver_optionA_low=C.optionA_receiver_low,
            sender_optionB_low=C.optionB_sender_low,
            receiver_optionB_low=C.optionB_receiver_low,
        )

    @staticmethod
    def error_message(player: Player, values):
        """
        function from oTree
        I record for each questions how many times they got it wrong and tell the participants when they got it wrong.
        They can only continue when all are correct
        """
        if values['q1'] != 2:
            player.q1_failed_attempts += 1
            return 'Answer to question 1 is incorrect. Check the instructions again and give a new answer'

        if values['q2'] != 1:
            player.q2_failed_attempts += 1
            return 'Answer to question 2 is incorrect. Check the instructions again and give a new answer'


    # @staticmethod
    # def is_displayed(player: Player):
    #     if player.role == C.SENDER_ROLE:
    #         return True


class Role(Page):
    """
    Instructions for only Receiver??
    """
    form_model = 'player'
    form_fields = ['q1', 'q2', 'q3', 'q4']

    def vars_for_template(player: Player):
        """  """
        return dict(
            # role=player.role,
            sender_optionA=C.optionA_sender_high,
            receiver_optionA=C.optionA_receiver_high,
            sender_optionB=C.optionB_sender_high,
            receiver_optionB=C.optionB_receiver_high,
        )

    @staticmethod
    def error_message(player: Player, values):
        """
        function from oTree
        I record for each questions how many times they got it wrong and tell the participants when they got it wrong.
        They can only continue when all are correct
        """
        if values['q1'] != 2:
            player.q1_failed_attempts += 1
            return 'Answer to question 1 is incorrect. Check the instructions again and give a new answer'
        if values['q2'] != 1:
            player.q2_failed_attempts += 1
            return 'Answer to question 2 is incorrect. Check the instructions again and give a new answer'
        if values['q3'] != 2:
            player.q3_failed_attempts += 1
            return 'Answer to question 3 is incorrect. Check the instructions again and give a new answer'
        if values['q4'] != 1:
            player.q4_failed_attempts += 1
            return 'Answer to question 4 is incorrect. Check the instructions again and give a new answer'


    # @staticmethod
    # def is_displayed(player: Player):
    #     if player.role == C.RECEIVER_ROLE:
    #         return True


page_sequence = [Consent,
                 #AttentionChecks,
                 Instructions,
                 InstruReceiver,
                 InstruSender,
                 InstruRepeated,
                 #Role,
                 ]
