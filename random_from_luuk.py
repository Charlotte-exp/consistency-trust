
def creating_session(subsession: Subsession):
    session = subsession.session
    session.group_randomly(fixed_id_in_group=True)
    print(session.get_group_matrix())


def do_my_shuffle(subsession: Subsession):
    # get all players in session
    session = subsession.session
    player = subsession.session.group.player
    print("self player?", player)
    players = subsession.get_players()

    # get total numbers of participants
    num_players = session.num_participants

    # couple participants to their variables
    for x in range(num_players):
        players[int(x)] = "p" + str(x + 1)
        print(players)
        print("p" + str(x + 1) + ".coupled_HH")
        print("p" + str(x + 1) + ".coupled_HL")
        print("p" + str(x + 1) + ".coupled_LH")
        print("p" + str(x + 1) + ".coupled_LL")
        print("p" + str(x + 1) + ".multiplier")
        print("p" + str(x + 1) + ".endowment")

    # create variables to count iterations inside the loop
    x = 0
    d = {}

    # randomize players
    from random import shuffle
    shuffle(players)

    if subsession.round_number > 1:
        for p_self in subsession.get_players():
            p_self.coupled_pother1 = p_self.in_round(subsession.round_number - 1).coupled_pother1
            p_self.coupled_pother2 = p_self.in_round(subsession.round_number - 1).coupled_pother2
            p_self.coupled_pother3 = p_self.in_round(subsession.round_number - 1).coupled_pother3
            p_self.coupled_pother4 = p_self.in_round(subsession.round_number - 1).coupled_pother4
            p_self.coupled_pother5 = p_self.in_round(subsession.round_number - 1).coupled_pother5
            p_self.coupled_pother6 = p_self.in_round(subsession.round_number - 1).coupled_pother6

    for p_self in subsession.get_players():
        print("Paired Previously before shuffle")
        print("p1 other1:", p_self.coupled_pother1)
        print("p1 other2:", p_self.coupled_pother2)
        print("p1 other3:", p_self.coupled_pother3)
        print("p1 other4:", p_self.coupled_pother4)
        print("p1 other5:", p_self.coupled_pother5)
        print("p1 other6:", p_self.coupled_pother6)
        print("p.id", p_self.random_id)

    if subsession.round_number == 1:
        number_list = [1, 2, 3]
        print("Original list:", number_list)
        random.shuffle(number_list)
        print("List after first shuffle:", number_list)
        session.ran_number_list = number_list

    #        print("List after first shuffle:", number_list)
    print(session.ran_number_list)
    print(session.ran_number_list[0])
    print(session.ran_number_list[1])
    print(session.ran_number_list[2])

    if subsession.round_number == session.ran_number_list[0]:
        matrix = subsession.get_group_matrix()
        new_structure = [[1, 2], [3, 4], [5, 6]]
        subsession.set_group_matrix(new_structure)

    if subsession.round_number == session.ran_number_list[1]:
        matrix = subsession.get_group_matrix()
        new_structure = [[1, 4], [3, 6], [5, 2]]
        subsession.set_group_matrix(new_structure)

    if subsession.round_number == session.ran_number_list[2]:
        matrix = subsession.get_group_matrix()
        new_structure = [[1, 6], [3, 4], [5, 2]]
        subsession.set_group_matrix(new_structure)


    print(subsession.get_group_matrix())




#### PAST_GORUPS METHOD

    def group_by_arrival_time_method(subsession, waiting_players):
    senders = [p for p in waiting_players if p.participant.role == 'Sender']
    receivers = [p for p in waiting_players if p.participant.role == 'Receiver']
    if len(senders) >= 1 and len(receivers) >= 1:
        players = [senders[0], receivers[0]]
        treatment = subsession.get_treatments()
        for p in players:
            p.participant.treatment = treatment
            p.treatment = p.participant.treatment
        return players
    session = subsession.session
    for possible_group in itertools.combinations(waiting_players, 2):
        pair_ids = set(p.id_in_subsession for p in possible_group)
        if pair_ids not in session.past_groups:
            session.past_groups.append(pair_ids)
            return possible_group



##### GROUP OF 6 WITH PARTNER ALLOCATION METHOD


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
    print(player.get_others_in_group())
    print(player.id_in_group)
    partner = []
    if player.round_number == 1:
        for partner_id in matches_round1[player.id_in_group]:  # picks the two partners from the matches dict
            for other_player in list_partners:  #
                if other_player.id_in_group == partner_id:
                    partner.append(other_player)
        return partner
    elif player.round_number == 2:
        for partner_id in matches_round2[player.id_in_group]:  # picks the two partners from the matches dict
            for other_player in list_partners:  #
                if other_player.id_in_group == partner_id:
                    partner.append(other_player)
        return partner
    elif player.round_number == 3:
        for partner_id in matches_round3[player.id_in_group]:  # picks the two partners from the matches dict
            for other_player in list_partners:  #
                if other_player.id_in_group == partner_id:
                    partner.append(other_player)
        return partner

