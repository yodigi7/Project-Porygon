"""This module contains several functions that emulate the logic 
for a Pokemon battle. In particular, it requires a strict adherence 
to a predefined JSON format. See the examples folder for details.

At the moment, Project Porygon only supports 2-player single battles.
"""
import json
import random
import pokebase as pb
import pokeutils as pk


"""Updates the battle JSON file.

Parameters:
battle_JSON -- the filepath to a Pokemon battle JSON
updated_dict -- the updated python dictionary representing the battle
"""
def update_battle(battle_JSON, updated_dict):
    with open(battle_JSON, 'w') as f:
        f.write(json.dumps(updated_dict))


"""Performs the given actions as they would be performed in a battle.
Returns the modified battle dictionary. Does not yet take fainting into account.

Parameters:
battle_dict -- a dictionary containing a Pokemon battle
player_choices -- a list containing the actions each player has chosen
in the form of {'action': 'attack 2', 'player': 'bugcatchercindy'}
teams -- a list containing the team data for each player
"""
def performTurn(battle_dict, player_choices, teams):

    # initialize toxic variable if not already done (work around)
    if not performTurn.toxic_multiplier:
        for team in teams:
            performTurn.toxic_multiplier[team['account_name']] = 1

    #  unpack player choices into attacks and switches
    attacks = []
    switches = []

    #  edge case for pursuit
    pursuit = False

    for choice in player_choices:
        action = choice['action']
        if action[0:6] == 'attack':
            attacks.append(choice)
        elif action[0:6] == 'switch':
            switches.append(choice)
        else:
            battle_dict['loser'] = choice['player']
            battle_dict['loss_reason'] = 'invalid command!'
            return battle_dict

    #  gather relevant data for attacks and store it
    for attack in attacks:
        attack['performed'] = False
        for player in battle_dict['players']:
            if player['account_name'] == attack['player']:
                attack['battle_data'] = player['active_pokemon']
                break
        for team in teams:
            if team['account_name'] == attack['player']:
                for pokemon in team['pokemon']:
                    if pokemon['poke_id'] == attack['battle_data']['poke_id']:
                        attack['team_data'] = pokemon
                        index = int(attack['action'][-1])
                        attack['attack_data'] = pb.move(pokemon['moves'][index])

                        #  edge case for pursuit
                        if attack['attack_data'].id == 228 and len(switches) > 0:
                            attack['attack_data'].power *= 2
                            pursuit = True
                        break
                break

        #  calculate the speed with which the attack is performed
        attack['speed'] = pk.calcStats(attack['team_data'])['speed']
        attack['speed'] *= attack['battle_data']['stat_modifiers']['speed']

        #  paralysis modifier
        if attack['battle_data']['status_condition'] == 'paralysis':
            attack['speed'] *= 0.5

    #  sort attacks by speed, then by priority
    sorted_attacks = sorted(attacks, key=lambda attack: attack['speed'])
    sorted_attacks = sorted(sorted_attacks, key=lambda attack: attack['attack_data'].priority)

    #  first, attempt to switch
    for switch in switches:
        if not pursuit:
            battle_dict = switch(battle_dict, switch['player'], int(switch['action'][-1]))
        else:

            #  find the pursuit user and use the move before the switch occurs
            for attack in attacks:
                if attack['attack_data'].id == 288:
                    battle_dict = perform_attack(battle_dict, teams, attack)

                    #  after a Pokemon takes damage, check if anyone fainted
                    for player in battle_dict['players']:
                        if player['active_pokemon']['hp_percent'] <= 0:

                            #  check if all backup Pokemon are also fainted
                            for backup in player['backup_pokemon']:
                                if backup['hp_percent'] > 0:
                                    break
                            else:
                                battle_dict['loser'] = player['account_name']
                                battle_dict['loss_reason'] = 'all Pokemon fainted'
                                return battle_dict

                            battle_dict['must_switch'].append(player)

                    #  'must switch' is a special case that demands a switch from a certain user
                    #  this does not count as an action for a turn
                    if len(battle_dict['must_switch']) > 0:
                        return battle_dict

                    attack['performed'] = True
                    battle_dict = switch(battle_dict, switch['player'], int(switch['action'][-1]))

    #  next, perform the attacks in order
    for attack in sorted_attacks:
        if attack['performed'] != True:
            battle_dict = perform_attack(battle_dict, teams, attack)

            #  after a Pokemon takes damage, check if anyone fainted
            for player in battle_dict['players']:
                if player['active_pokemon']['hp_percent'] <= 0:

                    #  check if all backup Pokemon are also fainted
                    for backup in player['backup_pokemon']:
                        if backup['hp_percent'] > 0:
                            break
                    else:
                        battle_dict['loser'] = player['account_name']
                        battle_dict['loss_reason'] = 'all Pokemon fainted'
                        return battle_dict

                    battle_dict['must_switch'].append(player)

            #  'must switch' is a special case that demands a switch from a certain user
            #  this does not count as an action for a turn
            if len(battle_dict['must_switch']) > 0:
                return battle_dict

            attack['performed'] = True

    #  perform end-of-turn effects (poison, burn, etc)
    for player in battle_dict['players']:

        #  burns deal 1/16th of a Pokemon's max HP each turn
        if player['active_pokemon']['status_condition'] == 'burn':
            for team in teams:
                if team['account_name'] == player['account_name']:
                    for pokemon in team['pokemon']:
                        if pokemon['poke_id'] == player['active_pokemon']['poke_id']:
                            max_hp = pk.calcStats(pokemon)['hp']
                            lost_hp = int(max_hp/16)
                            lost_hp_pct = int(lost_hp/max_hp)*100
            player['active_pokemon']['hp_percent'] -= lost_hp_pct

        #  regular poison deals 1/8th of a Pokemon's max HP each turn
        if player['active_pokemon']['status_condition'] == 'poison':
            for team in teams:
                if team['account_name'] == player['account_name']:
                    for pokemon in team['pokemon']:
                        if pokemon['poke_id'] == player['active_pokemon']['poke_id']:
                            max_hp = pk.calcStats(pokemon)['hp']
                            lost_hp = int(max_hp/8)
                            lost_hp_pct = int(lost_hp/max_hp)*100
            player['active_pokemon']['hp_percent'] -= lost_hp_pct

        # Toxic deals increasing damage per turns and leech seed
        if player['active_pokemon']['status_condition'] == 'poison':
            for team in teams:
                if team['account_name'] == player['account_name']:
                    for pokemon in team['pokemon']:
                        if pokemon['poke_id'] == player['active_pokemon']['poke_id']:
                            currtoxic_multiplier = performTurn.toxic_multiplier[team['account_name']]
                            max_hp = pk.calcStats(pokemon)['hp']
                            lost_hp = max(1, int(currtoxic_multiplier*(max_hp/16)))
                            lost_hp_pct = int(lost_hp/max_hp)*100
                            # Increment multiplier for next turn
                            performTurn.toxic_multiplier[team['account_name']] += 1

        #  check if the active Pokemon fainted after end-of-turn effects
        if player['active_pokemon']['hp_percent'] <= 0:

            #  check if all backup Pokemon are also fainted
            for backup in player['backup_pokemon']:
                if backup['hp_percent'] > 0:
                    break
            else:
                battle_dict['loser'] = player['account_name']
                battle_dict['loss_reason'] = 'all Pokemon fainted'
                return battle_dict
            battle_dict['must_switch'].append(player)

    return battle_dict


"""Performs an attack and returns the modified battle_dict.

Parameters:
battle_dict -- a dictionary containing a Pokemon battle
teams -- a list containing the team data for each player
attack -- the attack dict as defined in performTurn()
"""
def perform_attack(battle_dict, teams, attack):

    #  paralysis chance
    if attack['battle_data']['status_condition'] == 'paralysis':
        if random.randrange(0,100) < 25:
            return battle_dict

    #  get pokemon indices
    if battle_dict['players'][0]['account_name'] == attack['player']:
        atk_in = 0
        def_in = 1
    else:
        atk_in = 1
        def_in = 0

    combatants = {}
    combatants['atk_poke_public'] = attack['battle_data']

    #  get the defending Pokemon
    def_poke = battle_dict['players'][def_in]['active_pokemon']
    combatants['def_poke_public'] = def_poke

    #  load stat modifiers and HP percentages
    atk_stat_mods = attack['battle_data']['stat_modifiers']
    atk_hp_pct = attack['battle_data']['hp_percent']
    def_stat_mods = def_poke['stat_modifiers']
    def_hp_pct = def_poke['hp_percent']

    raw_stats = {}
    modded_stats = {}

    #  calculate raw stats for each Pokemon
    raw_stats['atk_stats'] = pk.calcStats(attack['team_data'])
    for team in teams:
        if team['account_name'] != attack['player']:
            for pokemon in team['pokemon']:
                if pokemon['poke_id'] == def_poke['poke_id']:
                    raw_stats['def_stats'] = pk.calcStats(pokemon)
                    combatants['def_poke_private'] = pokemon
    combatants['atk_poke_private'] = attack['team_data']

    #  apply stat modifiers to each Pokemon
    modded_stats['atk_stats'] = raw_stats['atk_stats']
    modded_stats['def_stats'] = raw_stats['def_stats']
    for key, value in raw_stats['atk_stats'].items():
        if key != 'hp':
            modded_stats['atk_stats'][key] = value*attack['battle_data']['stat_modifiers'][key]
    for key, value in raw_stats['def_stats'].items():
        if key != 'hp':
            modded_stats['def_stats'][key] = value*def_poke['stat_modifiers'][key]

    #  apply paralysis speed reduction to the defending Pokemon
    #  this shouldn't really come up outside of Electro Ball, Gyro Ball, etc.
    if def_poke['status_condition'] == 'paralysis':
        modded_stats['def_stats']['speed'] *= 0.5


    """ Perform the attack and write the results to the battle_dict """
    atk_category = attack['attack_data'].meta.category.name
    atk_accuracy = attack['attack_data'].accuracy
    #  Get the weather condition. This has an impact on accuracy of certain moves.
    weather_condition = battle_dict['weather']
    
    # Conversion table for accuracy stages to modifiers
    acc_stage_to_mod = {-6: 1/3, -5: 3/8, -4: 3/7, -3: 1/2, -2: 3/5, -1: 3/4, 0: 1, 1: 4/3, 2: 5/3, 3: 2, 4: 7/3, 5: 8/3, 6: 3}

    #  Check to see if the attack is a no-miss move, which has an accuracy listed as null in the API
    #  but is treated as None in python code. Skip the accuracy check if the move is a no-miss move.
    if atk_accuracy is None:
        pass
    # The attacks Thunder (id = 87) and Hurricane (id = 542) has different accuracy based on the weather
    elif (attack.id == 87 or attack.id == 542) and weather_condition == 'rain':
        # Thunder and Hurricane do not miss in the rain, so bypass the accuracy calculation
        pass
    elif (attack.id == 87 or attack.id == 542) and weather_condition == 'sun':
        # Thunder and Hurricane have 50% accuracy in the sun, so use a different accuracy calculation
        # Get the combined accuracy and evasion stage
        acc_mod_stage = atk_stat_mods['accuracy'] - def_stat_mods['evasion']
        # The total stage is capped at -6 and +6, so make sure that the combined stage reflects this
        if acc_mod_stage < -6:
            acc_mod_stage = -6
        elif acc_mod_stage > 6:
            acc_mod_stage
        # Convert the combined stage to an actual modifier
        acc_mod = acc_stage_to_mod[acc_mod_stage]
        # Generate a chance to miss
        miss_chance = random.randrange(0, 100)
        if miss_chance > 50 * acc_mod:
            return battle_dict # If it misses, return the battle_dict unmodified
    # The attack Blizzard (id = 59) does not miss during hail
    elif attack.id == 59 and weather_condition == 'hail':
        pass
    else: #  The move may have a chance to miss. Check to see if it lands.
        # Get the combined accuracy and evasion stage
        acc_mod_stage = atk_stat_mods['accuracy'] - def_stat_mods['evasion']
        # The total stage is capped at -6 and +6, so make sure that the combined stage reflects this
        if acc_mod_stage < -6:
            acc_mod_stage = -6
        elif acc_mod_stage > 6:
            acc_mod_stage
        # Convert the combined stage to an actual modifier
        acc_mod = acc_stage_to_mod[acc_mod_stage]
        # Generate a chance to miss
        miss_chance = random.randrange(0, 100)
        if miss_chance > atk_accuracy * acc_mod:
            return battle_dict # If it misses, return the battle_dict unmodified

    #  This gets executed if the attack lands
    if 'damage' in atk_category:
        raw_damage = pk.calcDamage(combatants, raw_stats, modded_stats, attack['attack_data'], battle_dict)

        #  Convert from an HP percentage to an HP amount and back again
        def_hp = int((def_hp_pct/100)*raw_stats['def_stats']['hp'])
        def_hp -= raw_damage
        def_hp_pct = int(def_hp/raw_stats['def_stats']['hp']*100)

        #  Write the new HP percentage to the dictionary
        battle_dict['players'][def_in]['active_pokemon']['hp_percent'] = def_hp_pct

    #  if the attack inflicts an ailment, try to inflict the ailment
    def_poke_status = def_poke['status_condition']
    def_poke_confused = def_poke['confused']
    if 'ailment' in atk_category:
        status = pk.applyStatus(combatants, attack['attack_data'])

        #  confusion is separate from status conditions
        #  we'll have to make an exception for 'curse' too
        #  and leech seed, oh god there's so many
        if status == 'confusion' and def_poke_confused == 0:
            battle_dict['players'][def_in]['active_pokemon']['confused'] = random.randrange(1, 5)
        elif status == 'curse':
            battle_dict['players'][def_in]['active_pokemon']['curse'] = 1
        elif status == 'leech-seed':
            battle_dict['players'][def_in]['active_pokemon']['leech-seed'] = 1
        elif status == 'infatuation':
            battle_dict['players'][def_in]['active_pokemon']['infatuation'] = 1
        elif status == 'perish-song':
            if battle_dict['players'][def_in]['active_pokemon']['perish_song_turn_count'] == 0:
                battle_dict['players'][def_in]['active_pokemon']['perish_song_turn_count'] = 4
            if battle_dict['players'][atk_in]['active_pokemon']['perish_song_turn_count'] == 0:
                battle_dict['players'][atk_in]['active_pokemon']['perish_song_turn_count'] = 4
        elif status == 'trap':
            if battle_dict['players'][def_in]['active_pokemon']['trap_turns'] == 0:
                battle_dict['players'][def_in]['active_pokemon']['trapped'] == 'partial'
                battle_dict['players'][def_in]['active_pokemon']['trap_turns'] = random.randrange(4, 6)
        elif status == 'trapped':
            battle_dict['players'][def_in]['active_pokemon']['trapped'] == 'by-opponent'
        elif def_poke_status == 'none':
            battle_dict['players'][def_in]['active_pokemon']['status_condition'] = status

    #  if the attack tries to change stats, try to change stats
    if atk_category == 'damage+raise' or atk_category == 'damage+lower' or atk_category == 'net-good-stats':
        atk_stat_mods, def_stat_mods = pk.changeStats(combatants, attack['attack_data'])
        battle_dict['players'][atk_in]['active_pokemon']['stat_modifiers'] = atk_stat_mods
        battle_dict['players'][def_in]['active_pokemon']['stat_modifiers'] = def_stat_mods

    return battle_dict


# Initialize static variables for perform turn functions (work around)
performTurn.toxic_multiplier = 0

"""Switches a Pokemon into the active slot for a team.

Parameters:
battle_dict -- a dictionary representing a Pokemon battle
player_name -- the player who is switching out
switch_index -- the index in backup_pokemon that player is switching to
"""
def switch(battle_dict, player_name, switch_index):

    #  get index for switching player
    if battle_dict['players'][0]['account_name'] == player_name:
        team_num = 0
    else:
        team_num = 1

    active_pokemon = battle_dict['players'][team_num]['active_pokemon']
    try:
        switch = battle_dict['players'][team_num]['backup_pokemon'][switch_index]
    except ValueError:
        battle_dict['loser'] = player_name
        battle_dict['loss_reason'] = 'invalid switch index!'
        return battle_dict

    #  swap applicable values
    active_pokemon['name'], switch['name'] = switch['name'], active_pokemon['name']
    active_pokemon['species'], switch['species'] = switch['species'], active_pokemon['species']
    active_pokemon['poke_id'], switch['poke_id'] = switch['poke_id'], active_pokemon['poke_id']
    active_pokemon['gender'], switch['gender'] = switch['gender'], active_pokemon['gender']
    active_pokemon['hp_percent'], switch['hp_percent'] = switch['hp_percent'], active_pokemon['hp_percent']
    active_pokemon['used_moves'], switch['used_moves'] = switch['used_moves'], active_pokemon['used_moves']
    active_pokemon['status_condition'], switch['status_condition'] = switch['status_condition'], active_pokemon['status_condition']

    #  reset values upon switching out
    active_pokemon['confused'] = 0
    active_pokemon['perish_song_turn_count'] = 0
    active_pokemon['cursed'] = 0
    active_pokemon['seeded'] = 0
    active_pokemon['infatuated'] = 0
    active_pokemon['trapped'] = 0
    performTurn.toxic_multiplier[player_name] = 1
    for key, value in active_pokemon['stat_modifiers'].items():
        value = 1

    battle_dict['players'][team_num]['active_pokemon'] = active_pokemon
    battle_dict['players'][team_num]['backup_pokemon'][switch_index] = switch

    return battle_dict
